from textual import work, on
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Horizontal, Vertical, VerticalScroll, Center
from textual.widgets import Header, Static, Button, Input
from textual.message import Message
from textual.widget import Widget
from textual._box_drawing import BOX_CHARACTERS 
from textual.geometry import Offset

from textual_hires_canvas import Canvas, HiResMode
from textual_plot.plot_widget import PlotWidget, LegendLocation
from rich.text import Text

from levycas import Expression, Variable, sym_eval, parse, get_symbols, trig_simplify

from dataclasses import dataclass

# Graph config
MAX_PLOTS        = 4
DEFAULT_X_BOUNDS = (-13.0, 13.0)
DEFAULT_Y_BOUNDS = (-10.0, 10.0)
PLOT_COLORS      = ("blue", "green", "purple", "red")
DEFAULT_RES_MODE = HiResMode.BRAILLE
EPS              = 1e-6  # max difference to consider two floats equal
SIMPLIFY_EXPRESSIONS = True # Simplify expressions fully; may hide removable discontinuities
# Gridlines
DRAW_GRIDLINES       = True
GRID_HORIZONTAL_CHAR = BOX_CHARACTERS[(0, 1, 0, 1)]
GRID_VERTICAL_CHAR   = BOX_CHARACTERS[(1, 0, 1, 0)]
GRID_CROSS_CHAR      = BOX_CHARACTERS[(1, 2, 1, 2)]

class ExpressionInput(Widget):
    """Single-line expression input field widget.
    
    As input is entered, validation is performed.
    When a valid expression is detected, a PlotExpression
    message is propagated. 
    """
    SAMPLES = [
        "sin(x)^2",
        "x^2",
        "ln(2x)",
        "x^(1/2)",
    ]
    DEFAULT_TOOLTIP = \
        'Start typing an expression, e.g. "{sample}"'
    
    @dataclass
    class Plot(Message):
        """Request to render a parsed expression."""
        idx:  int        # index of the expression to graph
        expr: Expression # expression to graph
    
    @dataclass
    class Clear(Message):
        """Request to clear a plot."""
        idx: int # index of expression to clear
    
    def __init__(self, idx: int) -> None:
        self.idx = idx
        sample = self.SAMPLES[idx]
        self.default_tooltip = self.DEFAULT_TOOLTIP.format(sample=sample)
        
        self.container = Horizontal(
            classes="expression-input-container",
            id=f"expression-input-container-{idx}",
        )
        self.input = Input(
            placeholder=self.SAMPLES[idx],
            classes="expression-input",
            id=f"expression-input-{idx}",
        )
        self.input.styles.border = ("tall", PLOT_COLORS[idx])
        self.delete_button = Button(
            label="x",
            classes="expression-delete",
            id=f"expression-delete-{idx}",
        )
        self.input.tooltip = self.default_tooltip

        super().__init__()

    def compose(self) -> ComposeResult:
        with self.container:
            yield self.input
            yield self.delete_button

    def on_input_changed(self, event: Input.Changed) -> None:
        """Parse the expression, send plot request if valid."""
        try:
            if not event.value:
                self.input.tooltip = self.default_tooltip
                self.post_message(
                    self.Clear(idx=self.idx)
                )
                return
            expr = parse(event.value)
            symbols = get_symbols(expr)

            if len(symbols) > 1:
                self.input.tooltip = f"Too many variables! How do I plot this?"
                return
            if symbols and Variable('x') not in symbols:
                self.input.tooltip = f"Expected an expression in terms of 'x'."
                return
            
            self.input.tooltip = f"Plotting: {expr}"
            self.post_message(
                self.Plot(
                    idx=self.idx,
                    expr=expr,
                )
            )
            
        except (SyntaxError, AssertionError) as e:
            self.input.tooltip = f"Failed to parse: {e}"

class CasPlot(PlotWidget):
    """Extension of `textual-plot`'s PlotWidget.
    
    Extended to allow for grid lines and some optimizations.
    Not a general-use widget; hardcoded for the LevyCAS Graphing screen.
    """
    def __init__(self) -> None:
        super().__init__(invert_mouse_wheel=True)
        # Keep track of each expression requesting a plot.
        self.expressions: list[Expression|None] = [None] * MAX_PLOTS

    def on_mount(self) -> None:
        super().on_mount()
        self.show_legend(LegendLocation.BOTTOMLEFT)
        self._update_legend()

    def _render_plot(self) -> None:
        """Renders axis lines before drawing plots, then canvas box & ticks."""
        # Return if widget isn't composed yet.
        canvas = self.query_one_optional("#plot", Canvas)
        if canvas is None or canvas._canvas_size is None: return
        canvas.reset()

        if DRAW_GRIDLINES: self.draw_grid_lines(canvas)
        self.render_expressions(canvas)
        # Render axis, ticks, and labels
        canvas.draw_rectangle_box(
            0, 0,
            self._scale_rectangle.width + 1, self._scale_rectangle.height + 1,
            thickness=2,
            style=str(self.get_component_rich_style("plot--axis")),
        )
        # render tick marks and labels
        self._render_x_ticks(); self._render_x_label()
        self._render_y_ticks(); self._render_y_label()
        # update legend
        self._update_legend()

    def draw_grid_lines(self, canvas: Canvas) -> None:
        """Render grid lines at tick labels"""
        x_ticks = self._x_formatter.get_ticks(self._x_min, self._x_max)
        y_ticks = self._y_formatter.get_ticks(self._y_min, self._y_max)
        rect_right_bound  = self._scale_rectangle.right - 1
        rect_bottom_bound = self._scale_rectangle.bottom - 1
        coords = []
        for x_tick in x_ticks:
            for y_tick in y_ticks:
                x, y = self.get_pixel_from_coordinate(x_tick, y_tick)
                coords.append((x, y))
                canvas.draw_line( # horizontal line (─)
                    1, y,
                    rect_right_bound, y,
                    style="white",
                    char=GRID_HORIZONTAL_CHAR,
                )
                canvas.draw_line( # vertical line (│)
                    x, 1,
                    x, rect_bottom_bound,
                    style="white",
                    char=GRID_VERTICAL_CHAR,
                )
        for x, y in coords: # intersections (┿)
            canvas.set_pixel(
                x, y,
                char=GRID_CROSS_CHAR,
                style="white",
            )

    def render_expressions(self, canvas: Canvas) -> None:
        """Compute & plot the current expressions.

        Approximates a graph by computing one point per canvas width coord,
        then drawing straight lines between them.
        """
        density = self._scale_rectangle.width
        for idx, expr in enumerate(self.expressions):
            if expr is None: continue
            color = PLOT_COLORS[idx]
            data  = self.compute_data(
                expr, self._x_min, self._x_max, density,
            )
            hires_pixels = [self.get_hires_pixel_from_coordinate(xi, yi) for xi, yi in data]
            segments = [(*hires_pixels[i-1], *hires_pixels[i]) for i in range(1, len(hires_pixels))]
            canvas.draw_hires_lines(segments, style=color, hires_mode=DEFAULT_RES_MODE)
            # canvas.set_hires_pixels(hires_pixels, style=color, hires_mode=DEFAULT_RES_MODE)

    def update_expression(self, idx: int, expr: Expression) -> None:
        """Plot a new expression."""
        if expr and SIMPLIFY_EXPRESSIONS:
            expr = trig_simplify(expr)
        self.expressions[idx] = expr
        self._rerender()

    def _update_legend(self) -> None:
        """Update the content and position of the plot legend.
        
        Updated to map plot colors to expression names without relying
        on the `PlotWidget.Dataset` class.
        """
        legend = self.query_one_optional("#legend", Static)
        if not legend: return
        
        legend_lines = []
        for idx, expr in enumerate(self.expressions):
            if expr is None: continue  
            style = PLOT_COLORS[idx]
            text = Text("▀▄▀▄") # "\u2580\u2584"*2
            text.stylize(style)
            text.append(f" {expr}")
            legend_lines.append(text.markup)
        if not legend_lines:
            legend.display = False; return
            
        legend.display = True
        legend.update(Text.from_markup("\n\n".join(legend_lines)))
        self._legend_relative_offset = Offset(1,-(len(legend_lines)+5))
        self._position_legend()

    @staticmethod
    def compute_data(
        expr: Expression, 
        x_min: float,
        x_max: float,
        density: int,
    ) -> list[tuple[float, float]]:
        """Compute (x, y) points across the canvas for a given expression."""
        data = []
        if (x_max - x_min) < EPS:
            x_max += EPS; x_min -= EPS
        dx = (x_max - x_min) / (density - 1)
        for i in range(density):
            x = x_min + i * dx
            try:
                y = float(sym_eval(expr, approximate=True, x=x))
            except ValueError as e:
                continue
            data.append((x, y))
        return data

class GraphingScreen(Screen):
    TITLE = "LevyCAS - Graphing"
    CSS_PATH = "styles/graphing.tcss"

    def __init__(self) -> None:
        super().__init__()

        # Initialize child widgets
        self.expression_inputs_container = VerticalScroll(id="expression-input-menu")
        self.expression_inputs_container.border_title = "expression input"
        self.expression_inputs_container.border_subtitle = "input"

        # self.plot_data = [[] for i in range(MAX_PLOTS)]
        self.inputs    = [ExpressionInput(i) for i in range(MAX_PLOTS)]
        for input in self.inputs:
            input.display = False

        self.add_expr_container = \
            Center(
                Button(
                    label="++",
                    id="add-expression",
                ),
                id="add-expression-container",
            )

        # self.plot = PlotWidget(invert_mouse_wheel=True)
        self.plot = CasPlot()

    @property
    def num_inputs_displayed(self) -> int:
        """Number of input fields currently visible."""
        return sum(input_field.display for input_field in self.inputs)

    def on_mount(self) -> None:
        # Display the first input box
        first_input = self.inputs[0]
        first_input.display = True

        # Initialize plot.
        self.plot.set_xlimits(*DEFAULT_X_BOUNDS)
        self.plot.set_ylimits(*DEFAULT_Y_BOUNDS)

    def compose(self) -> ComposeResult:
        """Screen layout and widgets"""

        yield Header()
        with Horizontal(id="main-container"):
            with Vertical(id="menu-desc-container"):
                # Screen Title
                yield Static(
                    "LevyCAS - Graphing",
                    id='screen-title',
                )

                # Expression input area
                with self.expression_inputs_container:
                    yield from self.inputs
                    yield self.add_expr_container

                # Graphing description
                yield Static(
                    "Welcome to LevyCAS Graphing! "
                    "Enter an expression in a box above, and view its graph "
                    "in the plot on the right. Hover over an input for help.",
                    id="screen-description"
                )

            # Graph Widget
            with Vertical(id="plot-and-menu-container"):
                yield self.plot
                with Horizontal(id="welcome-container"):
                    yield Button("Return Home", name='switch-screen', id='welcome')
                    yield Button("Reset Plot", id="reset-plot")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        """Dispatch button handlers"""
        button = event.button
        if button.id.startswith("expression-delete"):
            input_container = button.query_ancestor("ExpressionInput")
            self.remove_input(input_container)
        elif button.id == "add-expression":
            self.add_input()
        elif button.id == "reset-plot":
            self.reset_plot_limits()

    def remove_input(self, input_container: ExpressionInput) -> None:
        """Remove an expression input field from the display."""
        input_container.input.clear()
        
        # Don't remove the final input.
        if self.num_inputs_displayed == 1:
            return

        # When an input is deleted, the add button should be visible.
        input_container.display = False
        if not self.add_expr_container.display:
            self.add_expr_container.display = True

    def add_input(self) -> None:
        """Add an expression input field to the display."""
        # Display new input field after the visible ones.
        for input in self.inputs:
            if not input.display:
                self.expression_inputs_container.move_child(
                    child=input, 
                    before=self.add_expr_container,
                )
                input.display = True
                break

        # Remove add button if max fields are already visible
        if self.num_inputs_displayed == MAX_PLOTS:
            self.add_expr_container.display = False

    def reset_plot_limits(self) -> None:
        """Reset the axes limits of a plot back to default."""
        self.plot.action_reset_scales()

    def on_expression_input_plot(self, message: ExpressionInput.Plot) -> None:
        """Plot the sent expression."""
        idx, expr = message.idx, message.expr
        self.plot.update_expression(idx, expr)

    def on_expression_input_clear(self, message: ExpressionInput.Clear) -> None:
        """Clear the indicated expression."""
        idx = message.idx
        self.plot.update_expression(idx, None)

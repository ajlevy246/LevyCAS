from typing import Optional, Callable

from dataclasses import dataclass
from math import dist

from textual import on
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Horizontal, Vertical, VerticalScroll, Center
from textual.widgets import Header, Static, Button, Input
from textual.message import Message
from textual.renderables.gradient import LinearGradient
from textual.widget import Widget
from textual._box_drawing import BOX_CHARACTERS 
from textual.reactive import reactive
from rich.text import Text

from textual_hires_canvas import Canvas, HiResMode
from textual_plot.plot_widget import PlotWidget, LegendLocation

from ...expressions import Expression, Variable
from ...operations import sym_eval, compile_approximation, get_symbols, trig_simplify, derivative
from ...parser import parse

# Graph config
MAX_PLOTS        = 4
DEFAULT_X_BOUNDS = (-13.0, 13.0)
DEFAULT_Y_BOUNDS = (-10.0, 10.0)
INPUT_COLORS     = ("black", "darkgreen", "purple", "red", "green",)
PLOT_COLORS      = ("black", "dark_green", "purple", "red", "green",)
DEFAULT_RES_MODE = HiResMode.BRAILLE
EPS              = 1e-6  # max difference to consider two floats equal
SIMPLIFY_EXPRESSIONS = True # Simplify expressions fully; may hide removable discontinuities
COLOR_GRADIENT = LinearGradient(
    angle=25.0,
    stops=(
        (0.0, "#FF0000"),
        (0.2, "#FFEE00"),
        (0.3, "#09FF00"),
        (0.5, "#00FFFF"),
        (0.7, "#1100FF"),
        (0.8, "#AE00FF"),
        (1.0, "#FF00DD"),
    )
)
# Sampling config
MAX_DEPTH     = 10
MAX_INTERVALS = 25


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
    DEFAULT_TOOLTIP = 'Start typing an expression, e.g. "{sample}"'
    
    @dataclass
    class Plot(Message):
        """Request to render a parsed expression."""
        idx:  int        # index of the expression to graph
        expr: Expression # expression to graph
        color_idx: str   # parseable color string for the plot
    
    @dataclass
    class Clear(Message):
        """Request to clear a plot."""
        idx: int # index of expression to clear

    @dataclass
    class Add(Message):
        """Request to add a new input expression."""
        pass

    def __init__(self, idx: int) -> None:
        self.idx = idx
        self.color_idx = idx
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
        self.input.styles.border = ("tall", INPUT_COLORS[self.color_idx])
        self.input.tooltip = self.default_tooltip

        self.delete_button = Button(
            label="x",
            classes="expression-delete",
            id=f"expression-delete-{idx}",
        )
        self.delete_button.tooltip = "clear/delete the plot"

        self.color_button = Button(
            label="✓", # \u2713
            classes="expression-color",
            id=f"expression-color-{idx}",
        )
        self.color_button.render = lambda: COLOR_GRADIENT
        self.color_button.tooltip = "change the plot's color"

        super().__init__()

    def compose(self) -> ComposeResult:
        with self.container:
            yield self.input
            with Vertical():
                yield self.delete_button
                yield self.color_button

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
                    color_idx=self.color_idx,
                )
            )
    
        except (SyntaxError, AssertionError) as e:
            self.input.tooltip = f"Failed to parse: {e}"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button = event.button
        if button.id.startswith("expression-color"):
            self.color_idx = (self.color_idx + 1) % len(INPUT_COLORS)
            self.input.styles.border = ("tall", INPUT_COLORS[self.color_idx])
            self.post_message(
                self.Plot(
                    idx=self.idx,
                    expr=None, # don't update expression
                    color_idx=self.color_idx,
                )
            )

    def key_enter(self) -> None:
        """Request a new input field when enter is pressed."""
        self.post_message(self.Add())

class CasPlot(PlotWidget):
    """Extension of `textual-plot`'s PlotWidget.
    
    Extended to allow for grid lines and some optimizations.
    Not a general-use widget; hardcoded for the LevyCAS Graphing screen.
    """
    BINDINGS = [
        ("l", 'toggle_legend', "show/hide legend"),
        ("g", 'toggle_gridlines', "show/hide gridlines"),
    ]

    # graph config
    visible_legend = reactive(True, layout=True)
    hide_gridlines = reactive(False, layout=True)
    
    def __init__(self) -> None:
        super().__init__(invert_mouse_wheel=True)
        # Keep track of each expression requesting a plot, as well as its color.
        self.expressions: list[tuple[Optional[Expression],int]] = [(None, -1)] * MAX_PLOTS

    def on_mount(self) -> None:
        super().on_mount()
        self.show_legend(LegendLocation.TOPLEFT, is_visible=self.visible_legend)

    def _render_plot(self) -> None:
        """Renders axis lines before drawing plots, then canvas box & ticks."""
        # Return if widget isn't composed yet.
        canvas = self.query_one_optional("#plot", Canvas)
        if canvas is None or canvas._canvas_size is None: return
        canvas.reset()

        self.draw_grid_lines(canvas)
        self.render_expressions(canvas)
        # Render axis, ticks, and labels
        canvas.draw_rectangle_box(
            0, 0,
            self._scale_rectangle.width + 1, self._scale_rectangle.height + 1,
            thickness=2,
            style=str(self.get_component_rich_style("plot--axis")),
        )
        
        self._render_x_ticks(); self._render_x_label()
        self._render_y_ticks(); self._render_y_label()

        self._update_legend()

    def draw_grid_lines(self, canvas: Canvas) -> None:
        """Render grid lines at tick labels"""
        if self.hide_gridlines:
            return
        
        rect_right_bound = self._scale_rectangle.right - 1
        rect_bottom_bound = self._scale_rectangle.bottom - 1

        x_ticks = self._x_formatter.get_ticks(self._x_min, self._x_max)
        y_ticks = self._y_formatter.get_ticks(self._y_min, self._y_max)
        x_coords, y_coords = [], [] # avoids recomputing pixel coordinates for intersections

        # vertical lines │
        for x_tick in x_ticks:
            x, _ = self.get_pixel_from_coordinate(x_tick, 0)
            canvas.draw_line(
                x, 1,
                x, rect_bottom_bound,
                style="white",
                char=BOX_CHARACTERS[(1, 0, 1, 0)],
            )
            x_coords.append(x)
        # horizontal lines ─
        for y_tick in y_ticks: 
            _, y = self.get_pixel_from_coordinate(0, y_tick)
            canvas.draw_line(
                1, y,
                rect_right_bound, y,
                style="white",
                char=BOX_CHARACTERS[(0, 1, 0, 1)],
            )
            y_coords.append(y)
        # intersections ┿
        for x in x_coords:
            for y in y_coords:
                canvas.set_pixel(
                    x, y,
                    style="white",
                    char=BOX_CHARACTERS[(1, 2, 1, 2)],
                )

    def render_expressions(self, canvas: Canvas) -> None:
        """Compute & plot the current expressions.

        Approximates a graph by computing one point per canvas width coord,
        then drawing straight lines between them.
        """
        # parameters for plot resolution
        #  raising either will increase computed points, while decreasing performance. 
        #  max_depth = 10 and initial_intervals = 25 works reasonably well for `tan(x)` & `1/x`.
        # initial_intervals = max(MAX_INTERVALS, self._scale_rectangle.width // 15)
        initial_intervals = min(MAX_INTERVALS, self._scale_rectangle.width // 5)
        edges = [
            self._x_min + i * (self._x_max - self._x_min) / initial_intervals
            for i in range(initial_intervals + 1)
        ]

        canvas = self.query_one("#plot", Canvas)
        with canvas.batch_refresh():
            for expr, color_idx in self.expressions:
                if expr is None: 
                    continue
                f = compile_approximation(expr)

                pixels, segments = [], []
                for i in range(initial_intervals):
                    new_pixels, new_segments = self._adaptive_sample(
                        f,
                        edges[i], edges[i+1],
                        MAX_DEPTH,
                    )
                    pixels.extend(new_pixels)
                    segments.extend(new_segments)

                if pixels:
                    canvas.set_hires_pixels(pixels, DEFAULT_RES_MODE, PLOT_COLORS[color_idx])
                if segments:
                    canvas.draw_hires_lines(segments, DEFAULT_RES_MODE, PLOT_COLORS[color_idx])

    def _adaptive_sample(
        self, 
        f: Callable[[float], Optional[float]],
        a: float, c: float,
        depth: int,
        fa: float = None, fb: float = None, fc: float = None,
    ) -> list[tuple[float], tuple[float]]:
        """Sample the function recursively until the requested resolution is 
        reached or max depth is hit.

        Args:
            f (Callable[[float], Optional[float]]): The function to evaluate.
            a (float): left-hand side of the interval (x-min)
            c (float): right-hand side of the interval (x-max)
            depth (int): recursive depth
            fa (float, optional): Optional value for f(x) at the left-hand side. Defaults to None.
            fb (float, optional): Optional value for f(x) at the midpoint. Defaults to None.
            fc (float, optional): Optional value for f(x) at the right-hand side. Defaults to None.

        Returns:
            list[tuple[float], tuple[float]]: The list [Pixels, Segments] where Pixels is a list of coordinates to plot and Segments is a list of lines to draw.
        """
        b  = (a + c) / 2
        a1 = (a + b) / 2
        b1 = (b + c) / 2
  
        fa = f(a) if fa is None else fa
        fb = f(b) if fb is None else fb
        fc = f(c) if fc is None else fc
        fa1, fb1 = f(a1), f(b1)

        xs = (  a,  a1,  b,  b1,  c )
        ys = ( fa, fa1, fb, fb1, fc )

        if depth <= 0:
            samples = [self.get_hires_pixel_from_coordinate(x, y) for x, y in zip(xs, ys) if y is not None]
            return [samples, []]

        # Check oscillation/discontinuity criteria
        if all(y == None for y in ys): # e.g ln(x) for x < 0
            return [[], []]
        discontinuity_present = None in ys or float('-inf') in ys or float('inf') in ys

        if not discontinuity_present:
            oscillating_segments = 0
            for p1, p2, p3 in zip(ys, ys[1:], ys[2:]):
                if (
                    (p2 > p1 and p2 > p3)
                    or (p2 < p1 and p2 < p3)
                ):
                    oscillating_segments += 1

        needs_subdivision = discontinuity_present or oscillating_segments
        if not needs_subdivision:
            if self._screen_linear(xs, ys):
                pa = self.get_hires_pixel_from_coordinate(a, fa)
                pc = self.get_hires_pixel_from_coordinate(c, fc)
                return [[], [pa+pc]]

        # resolution isn't quite there;
        #  subdivide again
        lhs = self._adaptive_sample(
                f, a, b,
                depth-1,
                fa=fa, fb=fa1, fc=fb,
            )
        rhs = self._adaptive_sample(
                f, b, c,
                depth-1,
                fa=fb, fb=fb1, fc=fc,
            )
        return [lhs[0]+rhs[0], lhs[1]+rhs[1]]

    def _screen_linear(
        self,
        xs: tuple[float, ...],
        ys: tuple[float, ...],
        *,
        tolerance: float = 0.75,
    ) -> bool:
        """Test whether sampled points are visually linear in screen coordinates.

        If all interior samples lie within the same segment of pixels joining
            the first and last samples, then we can approximate the segment with a line
            from one endpoint to the other.

        A perpendicular-distance test is used rather than comparing y-values
            because it behaves correctly for steep lines.
        """
        pixels = [
            self.get_hires_pixel_from_coordinate(x, y)
            for x, y in zip(xs, ys)
        ]

        x0, y0 = pixels[0]
        x1, y1 = pixels[-1]

        dx = x1 - x0
        dy = y1 - y0

        length_sq = dx * dx + dy * dy

        # All samples project to the same screen point.
        if length_sq <= 1e-12:
            tolerance_sq = tolerance * tolerance

            return all(
                (px - x0) ** 2 + (py - y0) ** 2 <= tolerance_sq
                for px, py in pixels[1:-1]
            )

        tolerance_sq = tolerance * tolerance

        # Distance from point p to the infinite endpoint line:
        #  |cross(endpoint, point)| / |endpoint|
        for px, py in pixels[1:-1]:
            cross = (
                dx * (py - y0)
                - dy * (px - x0)
            )

            if cross * cross > tolerance_sq * length_sq:
                return False

        return True

    def update_expression(self, idx: int, expr: Expression, color_idx: int) -> None:
        """Plot a new expression."""
        if expr is None:
            if color_idx != -1:
                expr = self.expressions[idx][0]
        else:
            simp = trig_simplify(expr)
            # TODO: fix this silly heuristic for guessing which 
            #  will be cheaper to compute.
            expr = expr if len(str(expr)) < len(str(simp)) else simp

        self.expressions[idx] = (expr, color_idx)
        self._rerender()

    def _update_legend(self) -> None:
        """Update the content and position of the plot legend.
        
        Updated to map plot colors to expression names without relying
        on the `PlotWidget.Dataset` class.
        """
        legend = self.query_one_optional("#legend", Static)
        if not legend: return

        legend.display = self.visible_legend
        if not legend.display:
            return
        
        legend_lines = []
        for expr, color_idx in self.expressions:
            if expr is None: continue  
            style = PLOT_COLORS[color_idx]
            text = Text("▀▄▀▄") # "\u2580\u2584"*2
            text.stylize(style)
            key = str(expr)
            key = key if len(key) < 20 else key[:17] + "..."
            text.append(f" {key}")
            legend_lines.append(text.markup)
        if not legend_lines:
            legend.display = False
            return

        legend.update(Text.from_markup("\n\n".join(legend_lines)))

    def action_toggle_gridlines(self) -> None:
        self.hide_gridlines = not self.hide_gridlines

    def action_toggle_legend(self) -> None:
        self.visible_legend = not self.visible_legend

class GraphingScreen(Screen):
    TITLE = "LevyCAS - Graphing"
    CSS_PATH = "styles/graphing.tcss"

    def __init__(self, exprs: list[str] = None) -> None:
        super().__init__()
        self.initial_exprs = exprs if exprs is not None else []

        # Initialize child widgets
        self.expression_inputs_container = VerticalScroll(id="expression-input-menu")
        self.expression_inputs_container.border_title = "expression input"
        self.expression_inputs_container.border_subtitle = "input"

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

        # Add initial expressions
        for idx, expr in enumerate(self.initial_exprs):
            self.inputs[idx].input.value = expr
            self.add_input()

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
            self.plot.hide_gridlines = False
            self.plot.visible_legend = True
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

    @on(ExpressionInput.Add)
    def add_input(self) -> None:
        """Add an expression input field to the display.
        
        Focuses new widget.
        """
        # Display new input field after the visible ones.
        for input in self.inputs:
            if not input.display:
                self.expression_inputs_container.move_child(
                    child=input, 
                    before=self.add_expr_container,
                )
                input.display = True
                input.query_one("Input").focus(scroll_visible=True)
                break

        # Remove add button if max fields are already visible
        if self.num_inputs_displayed == MAX_PLOTS:
            self.add_expr_container.display = False

    def reset_plot_limits(self) -> None:
        """Reset the axes limits of a plot back to default."""
        self.plot.action_reset_scales()

    def on_expression_input_plot(self, message: ExpressionInput.Plot) -> None:
        """Plot the sent expression."""
        idx, expr, color_idx = message.idx, message.expr, message.color_idx
        self.plot.update_expression(idx, expr, color_idx)

    def on_expression_input_clear(self, message: ExpressionInput.Clear) -> None:
        """Clear the indicated expression."""
        idx = message.idx
        self.plot.update_expression(idx, None, -1)
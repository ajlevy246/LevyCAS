from textual import on
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Horizontal, Vertical, VerticalScroll, Center
from textual.widgets import Header, Static, Button
from textual_hires_canvas import HiResMode

from .cas_plot         import CasPlot
from .expression_input import ExpressionInput

class GraphingScreen(Screen):
    """A Desmos-esque graphing interface."""
    TITLE = "LevyCAS - Graphing"
    CSS_PATH = "./graphing.tcss"

    #  config
    MAX_PLOTS = 4
    """Maximum number of plots allowed at once."""
    DEFAULT_X_BOUNDS = (-13.0, 13.0)
    """Default plot x-bounds."""
    DEFAULT_Y_BOUNDS = (-10.0, 10.0)
    """Default plot y-bounds."""

    def __init__(self, exprs: list[str] = None) -> None:
        super().__init__()
        self.initial_exprs = exprs if exprs is not None else []

        # Initialize child widgets
        self.expression_inputs_container = VerticalScroll(id="expression-input-menu")
        self.expression_inputs_container.border_title = "expression input"
        self.expression_inputs_container.border_subtitle = "input"

        self.inputs = [ExpressionInput(i) for i in range(self.MAX_PLOTS)]
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

        self.plot = CasPlot(self.MAX_PLOTS)

    @property
    def num_inputs_displayed(self) -> int:
        """Number of input fields currently visible."""
        return sum(input_field.display for input_field in self.inputs)

    def on_mount(self) -> None:
        # Display the first input box
        first_input = self.inputs[0]
        first_input.display = True

        # Set default plot bounds
        self.plot.set_xlimits(*self.DEFAULT_X_BOUNDS)
        self.plot.set_ylimits(*self.DEFAULT_Y_BOUNDS)

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
        if self.num_inputs_displayed == self.MAX_PLOTS:
            self.add_expr_container.display = False

    def reset_plot_limits(self) -> None:
        """Reset the axes limits of a plot back to default."""
        self.plot.action_reset_scales()

    def on_expression_input_plot(self, message: ExpressionInput.Plot) -> None:
        """Plot the sent expression."""
        idx, expr, color = message.idx, message.expr, message.color
        self.plot.update_expression(idx, expr, color)

    def on_expression_input_clear(self, message: ExpressionInput.Clear) -> None:
        """Clear the indicated expression."""
        idx = message.idx
        self.plot.update_expression(idx, None, None) # clear
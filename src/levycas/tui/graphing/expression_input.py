from dataclasses import dataclass
from itertools import cycle

from textual.app import ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import Button, Input
from textual.message import Message
from textual.widget import Widget
from textual.renderables.gradient import LinearGradient

from ...expressions import Expression, Variable
from ...operations import get_symbols
from ...parser import parse

class ExpressionInput(Widget):
    """Single-line expression input field widget.
    
    As input is entered, validation is performed.
    When a valid expression is detected, a PlotExpression
    message is propagated. 
    """

    PLOT_COLORS = (  #     ANSI   -      Web Color (TCSS)
        "#000000", # black      -  black
        "#006400", # dark_green -  darkgreen
        "#920492", # purple     -  purple
        "#FF0000", # red        -  red
        "#008000", # green      -  green
    )
    """Possible plot colors.

    Widgets in Textual sometimes intermingle incompatible Rich/Textual named colors.
        - Textual's `Color` class uses Web standard named colors for native styles (TCSS).
        - Rich's `Color` class uses named ANSI colors. All Textual widgets that directly use the Render API can't use TCSS colors.

    Both `Color` classes can parse hex colors. 
    """

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
    """Simple angled rainbow gradient.

    Creates a nice pixelated effect when used at small sizes."""

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
        color: str       # parseable hex color string for the plot
    
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

        sample = self.SAMPLES[idx]
        self.default_tooltip = self.DEFAULT_TOOLTIP.format(sample=sample)

        # initialize styles
        self.plot_colors = cycle(self.PLOT_COLORS)
        for _ in range(idx+1):
            self.plot_color = next(self.plot_colors)

        # initialize widgets
        self.container = Horizontal(
            classes="expression-input-container",
            id=f"expression-input-container-{idx}",
        )
        self.input = Input(
            placeholder=sample,
            classes="expression-input",
            id=f"expression-input-{idx}",
        )
        self.input.styles.border = ("tall", self.plot_color)
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
        self.color_button.render = lambda: self.COLOR_GRADIENT
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
                    color=self.plot_color, # don't update color
                )
            )
    
        except (SyntaxError, AssertionError) as e:
            self.input.tooltip = f"Failed to parse: {e}"

    def on_button_pressed(self, event: Button.Pressed) -> None:
        button = event.button
        if button.id.startswith("expression-color"):
            self.plot_color = next(self.plot_colors)

            self.input.styles.border = ("tall", self.plot_color)
            self.post_message(
                self.Plot(
                    idx=self.idx,
                    expr=None, # don't update expression
                    color=self.plot_color,
                )
            )

    def key_enter(self) -> None:
        """Request a new input field when enter is pressed."""
        self.post_message(self.Add())
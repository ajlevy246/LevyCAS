"""Contains the CASPlot widget.

An extension of textual-plot's PlotWidget with:
    - Arbitrary expression plotting with adaptive sampling.
    - scientific-notation labels.
    - Optional gridlines, updated styles. """
from typing import Optional, Callable
from itertools import cycle

from textual.widgets import Static
from textual._box_drawing import BOX_CHARACTERS 
from textual.reactive import reactive

from textual_hires_canvas import Canvas, HiResMode
from textual_plot.plot_widget import PlotWidget, LegendLocation
from textual_plot.axis_formatter import NumericAxisFormatter

from rich.text import Text

from ...expressions import Expression
from ...operations import compile_approximation, trig_simplify

class CasPlot(PlotWidget):
    """Extension of `textual-plot`'s PlotWidget.
    
    Extended to allow for grid lines and some optimizations.
    Not a general-use widget; hardcoded for the LevyCAS Graphing screen.
    """
    BINDINGS = [
        ("l", 'toggle_legend',    'show/hide legend'),
        ("g", 'toggle_gridlines', 'show/hide gridlines'),
        ("m", 'switch_res_mode',  'change line type')
    ]

    # Graph config
    RES_MODE = cycle(HiResMode)

    # Adaptive sampling defaults.
    MAX_DEPTH     = 10
    MIN_INTERVALS = 25
    MAX_INTERVALS = 150

    # reactive attributes (configurable graph options)
    visible_legend  = reactive(True, layout=True)  # default: legend is visible
    hide_gridlines  = reactive(False, layout=True) # default: gridlines are visible
    active_res_mode = reactive(HiResMode.BRAILLE, layout=True) # default: plots are rendered using unicode braille characters
    
    def __init__(self, max_plots: int) -> None:
        super().__init__(invert_mouse_wheel=True)
        # Keep track of each expression requesting a plot, as well as its color.
        self.expressions: list[tuple[Optional[Expression], str]] = [(None, None)] * max_plots
        self._x_formatter = self._y_formatter = ScientificAxisFormatter()

    def on_mount(self) -> None:
        """Initialize margins and legend on mount."""
        self._update_margin_sizes()
        self.show_legend(LegendLocation.TOPLEFT, is_visible=self.visible_legend)

    def _render_plot(self) -> None:
        """Renders axis lines before drawing plots, then canvas box & ticks."""
        # Return if widget isn't composed yet.
        canvas = self.query_one_optional("#plot", Canvas)
        if canvas is None or canvas._canvas_size is None: return
        canvas.reset()

        self.draw_grid_lines(canvas)
        self._render_expressions(canvas)
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

        for x_tick in x_ticks: # vertical lines │
            x, _ = self.get_pixel_from_coordinate(x_tick, 0)
            canvas.draw_line(
                x, 1,
                x, rect_bottom_bound,
                style="white",
                char=BOX_CHARACTERS[(1, 0, 1, 0)],
            )
            x_coords.append(x)
        for y_tick in y_ticks: # horizontal lines ─
            _, y = self.get_pixel_from_coordinate(0, y_tick)
            canvas.draw_line(
                1, y,
                rect_right_bound, y,
                style="white",
                char=BOX_CHARACTERS[(0, 1, 0, 1)],
            )
            y_coords.append(y)
        for x in x_coords: # intersections ┿
            for y in y_coords:
                canvas.set_pixel(
                    x, y,
                    style="white",
                    char=BOX_CHARACTERS[(1, 2, 1, 2)],
                )

    def _render_expressions(self, canvas: Canvas) -> None:
        """Compute & plot the current expressions.

        Approximates a graph by computing one point per canvas width coord,
        then drawing straight lines between them.
        """
        initial_intervals = max(self.MIN_INTERVALS, min(self.MAX_INTERVALS, self._scale_rectangle.width // 2))
        self.log(f"\n\n{initial_intervals=}\n\n")
        edges = [
            self._x_min + i * (self._x_max - self._x_min) / initial_intervals
            for i in range(initial_intervals + 1)
        ]

        canvas = self.query_one("#plot", Canvas)
        with canvas.batch_refresh():
            for expr, color in self.expressions:
                if expr is None: 
                    continue
                f = compile_approximation(expr)

                pixels, segments = [], []
                for i in range(initial_intervals):
                    new_pixels, new_segments = self._adaptive_sample(
                        f,
                        edges[i], edges[i+1],
                        self.MAX_DEPTH,
                    )
                    pixels.extend(new_pixels)
                    segments.extend(new_segments)

                if pixels:
                    canvas.set_hires_pixels(pixels, self.active_res_mode, color)
                if segments:
                    canvas.draw_hires_lines(segments, self.active_res_mode, color)

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
            # can't subdivide again; just draw the computed points.
            samples = [
                self.get_hires_pixel_from_coordinate(x, y) for x, y in zip(xs, ys)
                if y is not None and self._y_min < y < self._y_max # bounds check avoids the coordinate mapping failing for extremely large inputs.
            ]
            return [samples, []]

        # Check oscillation/discontinuity criteria
        if all(y == None for y in ys):
            # this check has ramifications for zoomed out plots, e.g. 
            #  intervals of `y = tan(x)` will not be rendered if all f(x)'s land on asymptotes.
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
            if (pixels := self._screen_linear(xs, ys)) is not None:
                pa, *_, pc = pixels
                # pa = self.get_hires_pixel_from_coordinate(a, fa)
                # pc = self.get_hires_pixel_from_coordinate(c, fc)
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
    ) -> Optional[list[tuple[float,float]]]:
        """Test whether sampled points are visually linear in screen coordinates.

        If all interior samples lie within the same segment of pixels joining
            the first and last samples, then we can approximate the segment with a line
            from one endpoint to the other.

        A perpendicular-distance test is used rather than comparing y-values
            because it behaves correctly for steep lines.

        Args:
            xs (tuple[float, ...]): x coords.
            ys (tuple[float, ...]): computed y = f(x) values.
            tolerance (float, optional): minimum distance from projected points to be accepted. Defaults to 0.75.

        Returns:
            Optional[tuple[float,float]]: Returns None if an approximation should not be used, or the screen coordinates of the points to draw.
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

            if all(
                (px - x0) ** 2 + (py - y0) ** 2 <= tolerance_sq
                for px, py in pixels[1:-1]
            ):
                return pixels

            return None

        tolerance_sq = tolerance * tolerance

        # Distance from point p to the infinite endpoint line:
        #  |cross(endpoint, point)| / |endpoint|
        for px, py in pixels[1:-1]:
            cross = (
                dx * (py - y0)
                - dy * (px - x0)
            )

            if cross * cross > tolerance_sq * length_sq:
                return None

        return pixels

    def update_expression(self, idx: int, expr: Expression, color: str) -> None:
        """Plot a new expression."""
        if expr is None and color is None: # clear the plot
            self.expressions[idx] = (None, None)
            self._rerender()
            return
         
        old_expr, old_color = self.expressions[idx]
        if expr is None: # a new color was requested, but the expression to plot hasn't changed
            expr = old_expr
        elif color is None: # vice versa
            color = old_color
            # TODO: fix this silly heuristic for guessing which 
            #  will be cheaper to compute.
            simp = trig_simplify(expr)
            expr = expr if len(str(expr)) < len(str(simp)) else simp

        self.expressions[idx] = (expr, color)
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
        for expr, color in self.expressions:
            if expr is None: continue  
            text = Text("▀▄▀▄") # "\u2580\u2584"*2
            text.stylize(color)
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

    def action_switch_res_mode(self) -> None:
        self.active_res_mode = next(self.RES_MODE)

class ScientificAxisFormatter(NumericAxisFormatter):
    def __init__(self, digit_threshold=10, decimals=5):
        """NumericAxisFormatter, but with tick labels rendered in scientific notation.

        Args:
            digit_threshold (int, optional): number of decimal places at which to start using scientific notation. Defaults to 10.
            decimals (int, optional): number of significant figures to display. Defaults to 3.
        """
        self.threshold = digit_threshold
        self.decimals = decimals

    def get_labels_for_ticks(self, ticks):
        labels = super().get_labels_for_ticks(ticks)

        formatted_labels = []
        for tick, label in zip(ticks, labels):
            digit_count = sum(ch.isdigit() for ch in label)
            if digit_count >= self.threshold:
                formatted_labels.append(f"{tick:.{self.decimals}e}")
            else:
                formatted_labels.append(label)
        return formatted_labels
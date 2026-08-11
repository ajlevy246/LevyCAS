import pytest

from textual.pilot import Pilot
from textual.events import MouseScrollUp, MouseScrollDown
from textual.containers import Center
from pytest_textual_snapshot import snap_compare

from levycas.tui.__main__ import LevyCasApp

class TestGraphing:
    async def test_screen_load(self):
        cas = LevyCasApp() 
        async with cas.run_test() as pilot:
            await pilot.click("#graphing")

    def test_plots_simple_uses(self, snap_compare):
        cas = LevyCasApp()
        async def graph_exprs(pilot: Pilot):
            await pilot.click("#graphing")
            await pilot.press("tab")
            await pilot._post_mouse_events([MouseScrollUp], times=5, widget="#plot")

            exprs = ["x^3", "sin(sin(sin(sin(x))))", "ln(x)x^(1/2)", "cos(x)^2+sin(x)^2-0.5"]
            for expr in exprs:
                await pilot.press(*expr, "enter")

            await pilot.pause()


        assert snap_compare(
            cas,
            terminal_size=(125, 40),
            run_before=graph_exprs,
        )

    def test_plots_colors_and_delete(self, snap_compare):
        cas = LevyCasApp()
        async def graph_color_and_delete(pilot: Pilot):
            await pilot.click("#graphing")
            await pilot.press("tab")

            exprs = ["tan(x-5)-2", "exp(cos(x))", "ln(x^2)", "(x+1)/(x-1)"]
            for expr in exprs:
                await pilot.press(*expr, "enter")

            for i in range(len(exprs)-1):
                await pilot.click(f"#expression-delete-{i}")

            await pilot.click("#expression-color-3")

            await pilot.click("#add-expression")
            await pilot.press(*"cos(x)^(1/2)-2")
            await pilot.click("#expression-color-0")
            await pilot.click("#expression-color-0")
            await pilot.click("#expression-color-0")

            await pilot.pause(0.5)

        assert snap_compare(
            cas, 
            terminal_size=(125, 40),
            run_before=graph_color_and_delete,
        )

    def test_plot_actions(self, snap_compare):
        cas = LevyCasApp()
        async def graph_actions(pilot: Pilot):
            await pilot.click("#graphing")
            await pilot.press("tab")

            exprs = ["x", "x^2+2", "x^3 - 3", "x^4 + 4"]
            for expr in exprs:
                await pilot.press(*expr, "enter")

            await pilot.click("#plot")

            # try disabling gridlines
            await pilot.press("g")

            # and disabling legend
            await pilot.press("l")

            # move plot around
            for _ in range(15):
                await pilot.press("right", "up")
            await pilot._post_mouse_events([MouseScrollUp], times=5, widget="#plot")

            await pilot.pause()

        assert snap_compare(
            cas,
            terminal_size=(125, 40),
            run_before=graph_actions
        )

    def test_plot_reset_action(self, snap_compare):
        cas = LevyCasApp()
        async def graph_actions(pilot: Pilot):
            await pilot.click("#graphing")
            await pilot.press("tab")

            exprs = ["x", "x^2+2", "x^3 - 3", "x^4 + 4"]
            for expr in exprs:
                await pilot.press(*expr, "enter")

            await pilot.click("#plot")

            # try disabling gridlines
            await pilot.press("g")

            # and disabling legend
            await pilot.press("l")

            # move plot around
            for _ in range(15):
                await pilot.press("right", "up")
            await pilot._post_mouse_events([MouseScrollUp], times=5, widget="#plot")

            # reset plot; should see gridlines and legend back at default axes.
            await pilot.press("r")

            await pilot.pause()

        assert snap_compare(
            cas,
            terminal_size=(125, 40),
            run_before=graph_actions
        )
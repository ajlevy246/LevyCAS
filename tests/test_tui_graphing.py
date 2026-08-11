import pytest

from textual.pilot import Pilot
from textual.events import MouseScrollUp
from textual.containers import Center
from pytest_textual_snapshot import snap_compare

from levycas.tui.__main__ import LevyCasApp

class TestGraphing:
    async def test_screen_load(self):
        cas = LevyCasApp() 
        async with cas.run_test() as pilot:
            await pilot.click("#graphing")

    def test_plots_simple_Uses(self, snap_compare):
        cas = LevyCasApp()
        async def graph_exprs(pilot: Pilot):
            await pilot.resize_terminal(125, 40)
            await pilot.click("#graphing")
            await pilot.press("tab")
            await pilot._post_mouse_events([MouseScrollUp], times=5, widget="#plot")

            exprs = ["x^3", "sin(x)", "ln(x)x^(1/2)", "cos(x)^2+sin(x)^2-0.5"]
            for expr in exprs:
                await pilot.press(*expr)
                await pilot.press("enter")

        assert snap_compare(cas, run_before=graph_exprs)

    def test_plots_colors_and_delete(self, snap_compare):
        cas = LevyCasApp()
        async def graph_color_and_delete(pilot: Pilot):
            await pilot.resize_terminal(125, 40)
            await pilot.click("#graphing")
            await pilot.press("tab")

            exprs = ["tan(x-5)-2", "exp(cos(x))", "ln(x^2)", "(x+1)/(x-1)"]
            for expr in exprs:
                await pilot.press(*expr)
                await pilot.press("enter")

            for i in range(len(exprs)-1):
                await pilot.click(f"#expression-delete-{i}")

            await pilot.click("#expression-color-3")

            await pilot.click("#add-expression")
            await pilot.press(*"cos(x)^(1/2)-2")
            await pilot.click("#expression-color-0")
            await pilot.click("#expression-color-0")
            await pilot.click("#expression-color-0")

        assert snap_compare(cas, run_before=graph_color_and_delete)

    def test_plots_actions_and_reset(self, snap_compare):
        cas = LevyCasApp()
        async def graph_actions(pilot: Pilot):
            ...

        assert snap_compare(cas, run_before=graph_actions)
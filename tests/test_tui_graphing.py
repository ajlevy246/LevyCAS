import pytest

from textual.pilot import Pilot
from textual.events import MouseScrollUp
from pytest_textual_snapshot import snap_compare

from levycas.cli.__main__ import LevyCasApp

class TestGraphing:
    async def test_screen_load(self):
        cas = LevyCasApp() 
        async with cas.run_test() as pilot:
            await pilot.click("#graphing")

    def test_plots_snapshot(self, snap_compare):
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
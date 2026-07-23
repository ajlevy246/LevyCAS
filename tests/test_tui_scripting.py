import pytest
from pytest_textual_snapshot import snap_compare
from textual.widgets import TextArea
from textual.pilot import Pilot

from levycas.cli.__main__ import LevyCasApp

class TestScriptingScreen:
    async def test_screen_load(self):
        cas = LevyCasApp() 
        async with cas.run_test() as pilot:
            await pilot.click("#scripting")

    async def run_example(self, pilot):
        await pilot.resize_terminal(125, 40)
        await pilot.click("#scripting")
        await pilot.click("#load-example")
        await pilot.click("#run-script")

    async def test_script_example(self):
        cas = LevyCasApp()
        async with cas.run_test() as pilot:
            await self.run_example(pilot)
            output_log = cas.screen.script_output
            assert output_log.lines == [
                "-yCos(y) + yCos(x) + Sin(y)",
                "-Sin(x)",
                "Cos(1)",
                "Cos(2)",
                "Cos(3)",
            ]

    def test_script_snapshot(self, snap_compare):
        cas = LevyCasApp()
        assert snap_compare(cas, run_before=self.run_example)
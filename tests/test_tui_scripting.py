import pytest

from levycas.cli.__main__ import LevyCasApp

class TestScriptingScreen:
    async def test_screen_load(self):
        cas = LevyCasApp() 
        async with cas.run_test() as pilot:
            await pilot.click("#scripting")

    async def test_script_example(self):
        cas = LevyCasApp()
        async with cas.run_test() as pilot:
            await pilot.click("#scripting")
            await pilot.click("#load-example")
            await pilot.click("#run-script")
            output_log = cas.screen.script_output
            assert output_log.lines == [
                "-yCos(y) + yCos(x) + Sin(y)",
                "-Sin(x)",
                "Cos(1)",
                "Cos(2)",
                "Cos(3)",
            ]

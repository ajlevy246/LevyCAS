import pytest
from levycas.cli.main import LevyCasApp

class TestGraphing:
    async def test_screen_load(self):
        cas = LevyCasApp() 
        async with cas.run_test() as pilot:
            await pilot.click("#graphing")
import pytest
from levycas.cli.main import LevyCasApp

class TestScripting:
    async def test_screen_load(self):
        cas = LevyCasApp() 
        async with cas.run_test() as pilot:
            await pilot.click()
            assert True
from textual.screen import Screen
from textual.app import ComposeResult
from textual.widgets import Button, Static, Header, Footer
from textual.containers import Horizontal

class WelcomeScreen(Screen):
    """Home screen for the LevyCAS TUI"""

    CSS_PATH = "styles/welcome.tcss"

    def compose(self) -> ComposeResult:
        yield Header()
        yield Static("Welcome to LevyCAS!", id="welcome-title")
        with Horizontal():
            yield Button(label="Scripting", name="switch-screen", id="scripting")
            yield Button(label="Demo", name="switch-screen", id="demo")
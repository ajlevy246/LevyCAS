"""A Textual interface for the LevyCAS package"""

#TODO:
# Two Interfaces:
# REPL: One-line input and outputs. Choose operation type (parse, derivate, integrate, et cetera). Input is parsed directly to output.
# Scripting: Full scripting support using ";" to deliminate instructions. 
# Buttons to switch screens have event handler in main App. Format: name = 'switch-screen', id = 'demo', e.g. (name of screen) 

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, HorizontalScroll, VerticalScroll
from textual.widgets import Header, Footer, Input, Static, Button, TextArea
from textual.theme import Theme

from .screens import WelcomeScreen, DemoScreen, ScriptingScreen

levycas_theme = Theme(
    name="levycas",
    primary="#001858",
    secondary="#172c66",
    accent="#f582ae",
    foreground="#172c66",
    background="#fef6e4",
    surface="#8bd3dd",
    panel="#f3d2c1",
    success="#10b981",
    warning="#f59e0b",
    error="#ef4444",
)

class LevyCasApp(App):
    """Root textual app"""

    TITLE = "LevyCAS - Computer Algebra System"
    SCREENS = {
        'welcome': WelcomeScreen,
        'demo': DemoScreen,
        'scripting': ScriptingScreen,
    }

    def on_mount(self) -> None:
        self.register_theme(levycas_theme)
        self.theme = 'levycas'
        self.push_screen("welcome")

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.name == "switch-screen":
            self.switch_screen(event.button.id)

def main():
    app = LevyCasApp()
    app.run()
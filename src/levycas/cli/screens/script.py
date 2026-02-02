from textual import work
from textual.app import ComposeResult
from textual.screen import Screen
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Header, Footer, Static, Button, TextArea, Log

from .. import run_script, lex_script

from time import sleep

class ScriptingScreen(Screen):
    """Root textual app"""
    TITLE = "LevyCAS - Scripting"
    CSS_PATH = "styles/scripting.tcss"

    def __init__(self) -> None:
        super().__init__()

        self.script_input = TextArea()
        self.script_input.border_title = "script input"
        self.script_input.border_subtitle = "scripting"

        self.script_output = Log()
        self.script_output.border_title = "script output"
        self.script_output.border_subtitle = "logging"

        self.run_button = Button("Run", id="run-script")
        self.save_button = Button("Save", id="save-script")
        self.load_button = Button("Load", id="load-script")
        self.clear_button = Button("Clear", id="clear-script")

        self.example_button = Button("Load Example", id="load-example")

    def compose(self) -> ComposeResult:
        """Screen layout and widgets"""
        menu = VerticalScroll(id="cas-menu")
        menu.border_title = "operations menu"
        menu.border_subtitle = "menu"

        yield Header()
        with Horizontal(id="main-container"):
            with Vertical(id="menu-desc-container"):
                # Title
                yield Static(
                    content = "LevyCAS - Scripting",
                    id = 'screen-title',
                )

                # Operations Menu
                with menu:
                    yield self.run_button
                    yield self.save_button
                    yield self.load_button
                    yield self.clear_button
                    

                # Scripting Description
                yield Static(
                    content = """\
Welcome to LevyCAS Scripting! Write scripts \
in the text area to the right and press the green \
Run button to see output. Save or Load a script with the \
orange and yellow buttons. Clear the input text area with the red Clear button.""",
                    id='desc'    
                )

            # User Input
            with Horizontal(id="script-inout-container"):
                yield self.script_input
                yield self.script_output

        # Home Button
        with Horizontal(id="welcome-container"):
            yield Button("Return Home", name='switch-screen', id='welcome')
            yield self.example_button
            

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "run-script":
            self.run_button.disabled = True
            self.run(self.script_input.text)

        elif event.button.id == "clear-script":
            self.script_input.clear()
            self.script_output.clear()

        elif event.button.id == "load-example":
            self.script_input.clear()
            self.script_input.text = """\
f(x, y) = cos(x) + ysin(y);\n
print \integrate(f(x, y),y);
print \derivate(f(x, y),x);\n
for (i : 3) {
    print f(i, 0);
}            
"""

    @work(thread=True)
    def run(self, script: str) -> None:
        """Parse and run an input string."""
        # TODO: Reference below
        self.app.call_from_thread(self.script_output.clear)
        
        tokens = lex_script(script)
        #NOTE: Uncomment below lines for lexing debugging.
        # for token in tokens:
        #     self.app.call_from_thread(self.script_output.write_line, str(token))
        run_script(script, self.script_output)
        

        self.app.call_from_thread(self.toggle_run_button)

    def toggle_run_button(self) -> None:
        self.app.notify("Script run complete", timeout=1.5)
        self.run_button.disabled = False
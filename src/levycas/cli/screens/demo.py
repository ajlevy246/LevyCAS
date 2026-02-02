from textual.screen import Screen
from textual.app import ComposeResult
from textual.widget import Widget
from textual.widgets import Button, Label, Static, Header, Tabs, Tab, ContentSwitcher, Input, Log
from textual.containers import Horizontal, Vertical, VerticalScroll

class DemoContent(Widget):
    """A widget for displaying a demo app hardcoded for a specific LevyCAS function.
    
    Args:
       id (str) - The ID of the widget
       inputs (list[str]) - A list of labels for the inputs, in order.
       func: The function to pass the inputs in on run
    """
    def __init__(
            self, 
            id: str, 
            inputs: list[str],
            func,
        ) -> None:
        super().__init__()
        self.id = id
        self.inputs = inputs
        self.func = func

    def compose(self) -> ComposeResult:
        demo_input = VerticalScroll(classes="demo-menu")
        with demo_input:
            for input in self.inputs:
                yield Label(input)
                input_widget = Input(placeholder="enter input here", compact=True)
                yield input_widget

class DemoApp(Widget):
    """A widget for displaying a demo app with tabs for various operations.
    
    Args:
        tab_labels (list[str]) - A list of tab labels
        inputs (list[str]) - A list of DemoContent widgets corresponding to each tab header.        
        log (Log) - A reference to a Log object to post output
    """
    def __init__(self, tab_labels: list[str], tabs: list[DemoContent], output_log: Log):
        super().__init__()
        self.tab_labels = [Tab(label=tab, id=f"{tab.lower()}-tab") for tab in tab_labels]
        self.tabs = tabs
        self.content = ContentSwitcher()
        self.output_log = output_log

    def compose(self) -> ComposeResult:
        yield Tabs(*self.tab_labels)
        with Horizontal(id="demo-app-container"):
            with self.content:
                for tab_content in self.tabs:
                    yield tab_content
            yield self.output_log

    def on_tabs_tab_activated(self, event: Tabs.TabActivated):
        """Event handler to swap tabs"""
        tab_id = event.tab.id
        content_id = tab_id[:tab_id.index("-tab")] + "-content"
        self.content.current = content_id

class DemoScreen(Screen):
    """Demo application screen for the LevyCAS TUI"""

    TITLE = "LevyCAS - Demo"
    CSS_PATH = "styles/demo.tcss"    

    def __init__(self) -> None:
        """Tabbed content initialization"""
        super().__init__()
        self.output_log = Log()
        self.output_log.border_title = "demo output"
        self.output_log.border_subtitle = "output"

        # Initialize Applications
        self.calculus_app = DemoApp(
            tab_labels=["Derivate", "Integrate"],
            tabs=[
                DemoContent(
                    id="derivate-content",
                    inputs=["expression", "var. of differentiation"],
                    func=None,
                ),
                DemoContent(
                    id="integrate-content",
                    inputs=["integrand", "var. of integration"],
                    func=None
                )
            ],
            output_log=self.output_log
        )
        self.numerical_app = DemoApp(
            tab_labels=["Factor", "IsPrime"],
            tabs=[
                DemoContent(
                    id="factor-content",
                    inputs=["integral expression"],
                    func=None
                ),
                DemoContent(
                    id="isprime-content",
                    inputs=["integral expression"],
                    func=None
                )
            ],
            output_log=self.output_log
        )
        self.simplification_app = DemoApp(
            tab_labels=["Parse", "TrigSimplify", "Expand"],
            tabs=[
                DemoContent(
                    id="parse-content",
                    inputs=["expression"],
                    func=None
                ),
                DemoContent(
                    id="trigsimplify-content",
                    inputs=["expression"],
                    func=None
                ),
                DemoContent(
                    id="expand-content",
                    inputs=["expression"],
                    func=None
                )
            ],
            output_log=self.output_log
        )
    
    def compose(self) -> ComposeResult:
        """Screen layout and widgets"""
        
        menu = VerticalScroll(id="cas-demo-menu")
        menu.border_title = "operations menu"
        menu.border_subtitle = "menu"

        yield Header()
        with Horizontal(id="main-container"):
            with Vertical(id="menu-desc-container"):
                # Title
                yield Static(
                    content = "LevyCAS - Demo",
                    id = 'screen-title',
                )

                # Operations Menu
                with menu:
                    yield Button("Calculus")
                    yield Button("Numerical")
                    yield Button("Polynomial")
                    yield Button("Simplification")
                    
                # Scripting Description 
                yield Static(
                    content = """\
Welcome to LevyCAS Demo! Select an operation type \
from the tabs below, and then a specific function \
from the menu pane to the right.
                    """,
                    id='desc'    
                )

            yield self.calculus_app

        # Home Button
        with Horizontal(id="welcome-container"):
            yield Button("Return Home", name='switch-screen', id='welcome')
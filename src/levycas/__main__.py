from argparse import ArgumentParser

from levycas.parser import parse
from levycas.operations import derivative, integrate, get_symbols

def integrate_action(args) -> None:
    expr, wrt = parse(args.expr), parse(args.wrt)
    print(f"{integrate(expr, wrt)}")

def derivate_action(args) -> None:
    expr, wrt = parse(args.expr), parse(args.wrt)
    print(f"{derivative(expr, wrt)}")

def graph_action(args) -> None:
    try:
        import textual, textual_plot
    except ImportError as e:
        raise ImportError(
            f"The LevyCAS TUI requires the '{e.name}' package. "
            f"Please see installation instructions in the README."
        )

    assert len(args.exprs) <= 4, f"Support for more than four graphs at once is not yet available."
    from levycas.cli.__main__ import LevyCasApp
    app = LevyCasApp(graphing=True, exprs=args.exprs)
    app.run()

def launch_tui_action() -> None:
    try:
        import textual, textual_plot
    except ImportError as e:
        raise ImportError(
            f"The LevyCAS TUI requires the '{e.name}' package. "
            f"Please see installation instructions in the README."
        )

    from levycas.cli.__main__ import main as launch_tui
    launch_tui()

def build_parser() -> ArgumentParser:
    parser = ArgumentParser(
        prog="levycas",
        description=(
            "A set of symbolic computation tools, with a powerful text-based UI built with Textual. "
            "Do calculus, simplification, graphing, scripting, and more.\n"
            "Run with no arguments to launch the TUI."
        ),
        epilog="See github.com/ajlevy246/LevyCAS/ for examples and source."
    )
    subparsers = parser.add_subparsers(
        dest="command",
        description="The specific command to run. Run with no command to launch the TUI.")

    # Differentiate with `levycas derivate ...`
    diff_parser = subparsers.add_parser(
        "derivate",
        help="Compute the derivative of an expression.",
    )
    diff_parser.add_argument(
        "expr",
        help="The expression to compute the derivative of."
    )
    diff_parser.add_argument(
        "wrt",
        nargs="?", default="x",
        help="The variable of differentiation; 'x' by default."
    )
    # Integrate with `levycas integrate ...`
    int_parser = subparsers.add_parser(
        "integrate",
        help="Compute the integral of an expression.",
    )
    int_parser.add_argument(
        "expr",
        help="The expression to compute the integral of."
    )
    int_parser.add_argument(
        "wrt",
        nargs="?", default="x",
        help="The variable of integration; 'x' by default."
    )
    # Graph with `levycas graph ...`
    graph_parser = subparsers.add_parser(
        "graph",
        help="Graph up to four expressions.",
    )
    graph_parser.add_argument(
        "exprs",
        nargs="*",
        help="Enter up to four expressions to plot."
    )
    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    
    command = args.command
    if command is None:
        launch_tui_action()
    elif command == "integrate":
        integrate_action(args)
    elif command == "derivate":
        derivate_action(args)
    elif command == "graph": 
        graph_action(args)

if __name__ == "__main__":
    main()
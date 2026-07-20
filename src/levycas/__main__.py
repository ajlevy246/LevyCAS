from argparse import ArgumentParser

from levycas.parser import parse
from levycas.operations import derivative, integrate, get_symbols, factor, simplify
from levycas.expressions import Product

def print_version():
    try:
        from importlib.metadata import version
        print(f"LevyCAS: version=={version('levycas')}")
    except ImportError:
        print("importlib not found in standard library... LevyCAS may not support this Python version.")

def launch_terminal_session():
    raise NotImplementedError("Terminal session not yet implemented...  ")

def integrate_action(args) -> None:
    expr, wrt = parse(args.expr), parse(args.wrt)
    print(f"{integrate(expr, wrt)}")

def diff_action(args) -> None:
    expr, wrt = parse(args.expr), parse(args.wrt)
    print(f"{derivative(expr, wrt)}")

def factor_action(args) -> None:
    poly, var = parse(args.poly), parse(args.var)
    factors = factor(poly, var)
    print(simplify(Product(*factors)))

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
    # Help opens with `levycas -h or --help`
    parser = ArgumentParser(
        prog="levycas",
        description=(
            "A set of symbolic computation tools, with a powerful text-based UI built with Textual. "
            "Do calculus, simplification, graphing, scripting, and more. "
        ),
        epilog=(
            "See github.com/ajlevy246/LevyCAS/ for examples and source. "
            "Run with no arguments to launch the TUI."
        )
    )
    parser.add_argument("-v", "--version", help="print the levycas version and exit.", action='store_true')
    parser.add_argument("-i", "--interactive", help="launch an interactive python session with common commands already run.", action='store_true')

    subparsers = parser.add_subparsers(
        dest="command",
        description="The specific command to run. Run with no command to launch the TUI.")
    
    # Differentiate with `levycas diff ...`
    diff_parser = subparsers.add_parser(
        "diff",
        help="compute the derivative of an expression.",
    )
    diff_parser.add_argument(
        "expr", metavar="EXPR",
        help="the expression to compute the derivative of, e.g. 'x^2ln(x)'",
    )
    diff_parser.add_argument(
        "wrt", metavar="VAR",
        nargs="?", default="x",
        help="the variable of differentiation; 'x' by default.",
    )

    # Integrate with `levycas integrate ...`
    int_parser = subparsers.add_parser(
        "integrate",
        help="compute the integral of an expression.",
    )
    int_parser.add_argument(
        "expr", metavar="EXPR",
        help="the expression to compute the integral of, e.g. 'xsin(x^2)",
    )
    int_parser.add_argument(
        "wrt", metavar="VAR",
        nargs="?", default="x",
        help="the variable of integration; 'x' by default.",
    )

    # Factor with `levycas factor ...`
    fact_parser = subparsers.add_parser(
        "factor",
        help="factor a univariate polynomial with rational coefficients.",
    )
    fact_parser.add_argument(
        "poly", metavar="POLY",
        help="the polynomial to factor, e.g. 'x^2 + 3x + 2'",
    )
    fact_parser.add_argument(
        "var", metavar="VAR",
        nargs="?", default="x",
        help="the polynomial variable; 'x' by default.",
    )

    # Graph with `levycas graph ...`
    graph_parser = subparsers.add_parser(
        "graph",
        help="graph up to four expressions.",
    )
    graph_parser.add_argument(
        "exprs", metavar="EXPRS",
        nargs="*",
        help="enter up to four expressions to plot, e.g. 'sin(x)'",
    )
    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    
    # -v or -i launch actions and exit
    if args.version:
        print_version()
        return

    if args.interactive:
        launch_terminal_session()
        return

    # otherwise, expect a command + optional arguments
    command = args.command
    if command is None:
        launch_tui_action()
    elif command == "integrate":
        integrate_action(args)
    elif command == "diff":
        diff_action(args)
    elif command == "factor":
        factor_action(args)
    elif command == "graph": 
        graph_action(args)

if __name__ == "__main__":
    main()
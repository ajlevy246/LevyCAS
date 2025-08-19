import gradio as gr
from levycas import *

with gr.Blocks() as api:
    def deriv(expr: str, wrt: str) -> str:
        """Take the derivative of an expression.

        Args:
            expr (str): expression
            wrt (str): variable of differentiation

        Returns:
            str: derivative
        """
        expr, wrt = parse(expr), parse(wrt)
        return str(derivative(expr, wrt))

    def integ(expr: str, wrt: str) -> str:
        """Take the integral of an expression.

        Args:
            expr (str): expression
            wrt (str): variable of integration

        Returns:
            str: integral
        """
        expr, wrt = parse(expr), parse(wrt)
        return str(integrate(expr, wrt))


    def poly_gcd(poly_1: str, poly_2: str) -> str:
        """Calculate the greatest common divisor of two polynomials

        Args:
            poly_1 (str): first polynomial
            poly_2 (str): second polynomial

        Returns:
            str: gcd(poly_1, poly_2)
        """
        poly_1, poly_2 = parse(poly_1), parse(poly_2)
        syms = get_symbols(poly_1).union(get_symbols(poly_2))
        return str(polynomial_gcd(poly_1, poly_2, list(syms)))

    def poly_rationalize(poly: str) -> str:
        """Rationalize a polynomial

        Args:
            poly (str): polynomial

        Returns:
            str: rationalized polynomial
        """
        poly = parse(poly)
        return str(rationalize(poly))

    gr.api(deriv, api_name="calculus/derivative")
    gr.api(integ, api_name="calculus/integrate")
    gr.api(poly_rationalize, api_name="polynomials/rationalize")

api.launch(show_error=True)
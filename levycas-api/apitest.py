import gradio as gr
import levycas as cas

with gr.Blocks() as api:

    # Calculus Operations
    def derivative(expr: str, wrt: str) -> str:
        """Take the derivative of an expression.

        Args:
            expr (str): expression
            wrt (str): variable of differentiation

        Returns:
            str: derivative
        """
        expr, wrt = cas.parse(expr), cas.parse(wrt)
        return str(cas.derivative(expr, wrt))

    def integrate(expr: str, wrt: str) -> str:
        """Take the integral of an expression.

        Args:
            expr (str): expression
            wrt (str): variable of integration

        Returns:
            str: integral
        """
        expr, wrt = cas.parse(expr), cas.parse(wrt)
        return str(cas.integrate(expr, wrt))

    # Numerical Operations
    def is_prime(expr: str) -> str:
        """Check if an integer is prime
        
        Args:
            expr (str): number

        Returns:
            str: primality of the number
        """
        expr = cas.parse(expr)
        return str(cas.is_prime(expr))
    
    def factor(expr: str) -> str:
        """Compute the prime factors of a number

        Args:
            expr (str): integer

        Returns:
            str: prime factorization
        """
        expr = cas.parse(expr)
        factors_dict = cas.factor_integer(expr)
        factors = [str(cas.Power(factor, factors_dict[factor])) for factor in factors_dict]
        return " * ".join(factors)
        
    # Simplification Operations
    def auto(expr: str) -> str:
        """Parse an expression. Allows the user to 
        see how the CAS is interpreting their input.

        Args:
            expr (str): expression

        Returns:
            str: parsed expression
        """
        return str(cas.parse(expr))
    
    def trig(expr: str) -> str:
        """Run an expression through the
        trig_simplify routine. 

        Args:
            expr (str): expression

        Returns:
            str: trig-simplified expression
        """
        expr = cas.parse(expr)
        return str(cas.trig_simplify(expr))
    
    def rationalize(expr: str) -> str:
        """Rationalize an expression.

        Args:
            expr (str): expression

        Returns:
            str: rationalized form
        """
        expr = cas.parse(expr)
        return str(cas.rationalize(expr))

    # Polynomial operations - API endpoints not yet implemented

    gr.api(derivative, api_name="calculus/derivative")
    gr.api(integrate, api_name="calculus/integrate")

    gr.api(is_prime, api_name="num/prime")
    gr.api(factor, api_name="num/factor")

    gr.api(auto, api_name="simp/auto")
    gr.api(trig, api_name="simp/trig")
    gr.api(rationalize, api_name="simp/rationalize")

    # gr.api(gcd, api_name="poly/gcd")
    # gr.api(sqf, api_name="poly/sqf")


api.launch(show_error=True)
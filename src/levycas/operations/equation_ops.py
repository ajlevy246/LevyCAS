"""Routines acting on implicit equations or systems of equations."""
from levycas.expressions import *
from levycas.operations.algebraic_ops import linear_form, quadratic_form

def solve_implicit(expr: Expression, var: Variable) -> list[Expression] | None:
    """Find the zeroes of an equation of a given variable.
    
    Treats all other symbols as constants.
    Returns: A list of real roots; None if solve failed or empty list if no real solutions were found.
    """
    roots = solve_polynomial(expr, var)
    
    if roots is None:
        #TODO: Implement more advanced solver? 
        ...
    return roots

def solve_linear(expr: Expression, var: Variable) -> list[Expression] | None:
    """Solve Ax + B = 0 for x"""
    form = linear_form(expr, var)
    if form is None: return None

    a, b = form
    if a == 0:
        if b == 0: return None
        return []
    return [-b / a]

def solve_quadratic(expr: Expression, var: Variable) -> list[Expression] | None:
    form = quadratic_form(expr, var)
    if form is None: return None

    a, b, c = form
    disc = b**2 - 4*a*c
    if isinstance(disc, Constant) and disc < 0:
        return []
    root = disc**Rational(1, 2)
    return [(-b+root) / (2*a), (-b-root) / (2*a)]

def solve_polynomial(expr: Expression, var: Variable) -> list[Expression] | None:
    ...
"""Methods acting on an expression's AST. These operations are mathematical in nature.
"""

from ..expressions import *
from .expression_ops import copy
from .simplification_ops import simplify

def algebraic_expand(expr: Expression) -> Expression:
    """Given an expression, returns an equivalent expression in expanded form.
    For now, will only return a completely result for integer exponents. 

    Args:
        expr (Expression): The expression to expand

    Returns:
        Expression: The expanded expression
    """
    if not isinstance(expr, Expression):
        return expr

    expr = simplify(expr) #Inefficient top-down simplification. Better way? Require a simplified input?
    operation = type(expr)
    operands = expr.operands()

    if isinstance(expr, Constant) or isinstance(expr, Variable):
        return expr
    
    elif operation == Sum:
        expanded_operands = [algebraic_expand(operand) for operand in operands]
        return simplify(sum(expanded_operands))
    
    elif operation == Product:
        if len(operands) == 1:
            return operands[0].algebraic_expand()
        
        v = algebraic_expand(operands[0])
        u_div_v = algebraic_expand(Product(*operands[1::]))
        return simplify(_expand_product(v, u_div_v))
    
    elif operation == Power:
        exponent = algebraic_expand(expr.exponent())
        base = algebraic_expand(expr.base())

        if not isinstance(exponent, Integer): #Expansion for non-integer exponents not yet supported
            return base ** exponent

        if exponent == 0:
            return Integer(1)
        elif exponent == 1:
            return base
        else:
            return _expand_power(base, exponent)

    expanded_args = [algebraic_expand(operand) for operand in operands]
    return operation(*expanded_args)

def rationalize(expr: Expression) -> Expression:
    """Rationalizes an expression over a common denominator.

    Args:
        expr (Expression): The expression to rationalize

    Returns:
        Expression: The rationalized expression
    """
    return simplify(_rationalize_expression(simplify(expr)))

def _expand_product(r: Expression, s: Expression) -> Sum | Product:
    """Given a product (r * s), expanded the product recursively.
    If neither r nor s is a sum, then the product r * s is returned unchanged.

    Args:
        r (Expression): First factor
        s (Expression): Second factor

    Returns:
        Sum | Product: Expanded product
    """
    r_op = type(r)
    s_op = type(s)

    if r_op == Sum:
        r_operands = r.operands()
        f = r_operands[0]

        if len(r_operands) == 1:
            return algebraic_expand(f * s)
        else:
            r_minus_f = Sum(*r_operands[1::])
            return _expand_product(f, s) + _expand_product(r_minus_f, s)
        
    elif s_op == Sum:
        return _expand_product(s, r)
    
    return r * s

def _expand_power(u: Expression, n: Integer) -> Sum | Power:
    """Expanded a power of the form u ^ n, where n is an integer >= 2, using 
    the binomial theorem. 
    If the base is not a sum, then the product u ^ n is returned unchanged.

    Args:
        u (Expression): Base of the power
        n (Integer): Integer exponent

    Returns:
        Sum | Power: Expanded power
    """
    from math import comb

    u_op = type(u)
    if u_op == Sum:
        u_operands = u.operands()
        f = u_operands[0]
        n = int(n)
        if n == 1:
            return algebraic_expand(f)
        if len(u_operands) == 1:
            return algebraic_expand(f ** Integer(n))
        r = Sum(*u_operands[1::])
        s = 0
        for k in range(n + 1):
            c = comb(n, k)
            s += _expand_product((c * f ** (n - k)), _expand_power(r, Integer(k)))
        return algebraic_expand(s)

    return u ** n

def _rationalize_expression(expr: Expression) -> Expression:
    """Rationalizes an expression over a common denominator recursively.

    Args:
        expr (Expression): The expression to rationalize

    Returns:
        Expression: The rationalized expression
    """
    operation = type(expr)
    operands = expr.operands()

    if operation == Power:
        return _rationalize_expression(operands[0]) ** operands[1]
    elif operation == Product:
        first_factor = _rationalize_expression(operands[0])
        if len(operands) == 1:
            return first_factor
        else:
            remaining_factor = _rationalize_expression(Product(*operands[1::]))
            return first_factor * remaining_factor
    elif operation == Sum:
        first_term = _rationalize_expression(operands[0])
        if len(operands) == 1:
            return first_term
        else:
            remaining_term = _rationalize_expression(Sum(*operands[1::]))
            return _rationalize_sum(first_term, remaining_term)
    else:
        return expr

def _rationalize_sum(first_term: Expression, second_term: Expression) -> Expression:
    """Given two terms m/r + n/s, returns the simplified form of
    (ms + nr)/sr

    Args:
        first_term (Expression): _description_
        second_term (Expression): _description_

    Returns:
        Expression: _description_
    """
    m = first_term.num()
    r = first_term.denom()
    n = second_term.num()
    s = second_term.denom()
    if r == 1 and s == 1:
        return first_term + second_term
    else:
        return _rationalize_sum(m * s, n * r) / (r * s)
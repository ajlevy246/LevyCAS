"""Methods acting on an expression's AST. These operations are mathematical in nature.
"""

from ..expressions import *
from .expression_ops import copy

def trig_substitute(expr: Expression) -> Expression:
    """Given an expression, replaces all instances of trig functions with their equivalent
    expressions in sin and cos. Returns a new expression.

    Args:
        expr (Expression): The expression to trig-sub.

    Returns:
        Expression: An expression containing no trig functions other than sin/cos
    """
    #Terminals of the AST do not have operands to substitute
    if isinstance(expr, Constant) or isinstance(expr, Variable):
        return copy(expr)

    operation = type(expr)

    #First, recursively apply to operands
    new_operands = [trig_substitute(operand) for operand in expr.operands()]
    new_expr = operation(*new_operands)

    if operation == Tan:
        return Sin(*new_operands) / Cos(*new_operands)
    elif operation == Csc:
        return 1 / Sin(*new_operands)
    elif operation == Sec:
        return 1 / Cos(*new_operands)
    elif operation == Cot:
        return Cos(*new_operands) / Sin(*new_operands)
    else:
        return operation(*new_operands)
    
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
    
    expr = expr.simplify() #Inefficient top-down simplification. Better way? Require a simplified input?
    operation = type(expr)
    operands = expr.operands()

    if isinstance(expr, Constant) or isinstance(expr, Variable):
        return expr
    
    elif operation == Sum:
        expanded_operands = [algebraic_expand(operand) for operand in operands]
        return sum(expanded_operands).simplify()
    
    elif operation == Product:
        if len(operands) == 1:
            return operands[0].algebraic_expand()
        
        v = algebraic_expand(operands[0])
        u_div_v = algebraic_expand(Product(*operands[1::]))
        return expand_product(v, u_div_v).simplify()
    
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
            return expand_power(base, exponent)

    expanded_args = [algebraic_expand(operand) for operand in operands]
    return operation(*expanded_args)

def expand_product(r: Expression, s: Expression) -> Sum | Product:
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
            return expand_product(f, s) + expand_product(r_minus_f, s)
        
    elif s_op == Sum:
        return expand_product(s, r)
    
    return r * s

def expand_power(u: Expression, n: Integer) -> Sum | Power:
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
            s += expand_product((c * f ** (n - k)), expand_power(r, Integer(k)))
        return algebraic_expand(s)

    return u ** n

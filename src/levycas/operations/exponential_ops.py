"""Operations acting on an expresion's AST. These operations affect those AST's that have
exponential functions (Ln, Exp, ...).
"""
from ..expressions import *
from .algebraic_ops import algebraic_expand, algebraic_expand_main, rationalize
from .expression_ops import construct
from .simplification_ops import simplify

def exp_expand(u: Expression) -> Expression:
    """Given an algebraic expression, returns the expression in exponential-expanded form.
    
    The result is an expression in which no argument of an exponential function is a sum
    nor a product with integer coefficient.

    Args:
        u (Expression): An algebraic expression. 

    Returns:
        Expression: An algebraic expression in exponential-expanded form.
    """
    if isinstance(u, (Constant, Variable)):
        return u
    
    expanded = simplify(
        construct(
            operands=list(exp_expand(algebraic_expand(arg)) for arg in u.operands()),
            op=type(u),
        )
    )
    if isinstance(expanded, Exp):
        return _exponential_expand(*expanded.operands())
    else:
        return expanded
    
def _exponential_expand(u: Expression) -> Expression:
    """Recursive helper for exponential_expand(), acting on the argument
    of an exponential.
    """
    if isinstance(u, Sum):
        return Product(*map(_exponential_expand, u.operands()))
    elif isinstance(u, Product):
        c = u.coefficient()
        if isinstance(c, Integer) and c != 1:
            return exp_expand(Exp(u / c))**c
    return Exp(u)

def exp_contract(u: Expression) -> Expression:
    """Given an algebraic expression, returns the expression in exponential-contracted form.
    
    The result is an expression in which no power has an exponential as a base,
    and no product has more than one exponential function as a factor.

    Args:
        u (Expression): An algebraic expression.

    Returns:
        Expression: u in exponential contracted form.
    """
    if isinstance(u, (Constant, Variable)):
        return u
    expanded = simplify(
        construct(
            operands=list(exp_contract(arg) for arg in u.operands()),
            op=type(u),
        )
    )
    if isinstance(expanded, (Product, Power)):
        return _exp_contract(expanded)
    else:
        return expanded

def _exp_contract(u: Expression) -> Expression:
    """Recursive helper for exp_contract."""
    v = algebraic_expand_main(u)
    if isinstance(v, Power):
        b, s = v.base(), v.exponent()
        if isinstance(b, Exp):
            p = b.operands()[0] * s
            if isinstance(p, (Product, Power)):
                p = _exp_contract(p)
            return Exp(p)
    elif isinstance(v, Product):
        p = Integer(1)
        s = Integer(0)
        for y in v.operands():
            if isinstance(y, Exp):
                s += y.operands()[0]
            else:
                p *= y
        return Exp(s) * p
    elif isinstance(v, Sum):
        s = Integer(0)
        for y in v.operands():
            if isinstance(y, (Product, Power)):
                s += _exp_contract(y)
            else:
                s += y
        return s
    return v

def exp_simplify(expr: Expression) -> Expression:
    """Given an expression, returns an expression in contracted-exponential form
    that is simplified.

    Args:
        expr (Expression): The expression to simplify

    Returns:
        Expression: The simplified expression
    """
    if expr is UNDEFINED: return UNDEFINED
    if isinstance(expr, Constant):
        return expr
    
    expr = rationalize(expr)
    numerator = exp_contract(exp_expand(expr.num()))
    denominator = exp_contract(exp_expand(expr.denom()))
    if denominator == 0:
        return UNDEFINED
    else:
        return numerator / denominator

def log_expand(u: Expression) -> Expression:
    """Given an algebraic expression, returns the expression in log-expand form.
    
    The result is an expression in which no argument of a logarithm
    is a product or power.
    
    Args:
        u (Expression): An algebraic expression.

    Returns:
        Expression: u in log-expanded form.
    """
    if isinstance(u, (Constant, Variable)):
        return u

    expanded = simplify(
        construct(
            operands=list(log_expand(algebraic_expand(arg)) for arg in u.operands()),
            op=type(u),
        )
    )
    if isinstance(expanded, Ln):
        return _log_expand(*expanded.operands())
    else:
        return expanded
    
def _log_expand(u: Expression) -> Expression:
    """Recursive helper for log_expand(), acting on the 
    argument of a logarithm."""
    if isinstance(u, Product):
        return Sum(*map(_log_expand, u.operands()))
    elif isinstance(u, Power):
        return log_expand(u.exponent() * Ln(u.base()))
    return Ln(u)
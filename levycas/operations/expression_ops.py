"""Methods acting on an expression's AST. These operations are not mathematical in nature.
"""

from ..expressions import Expression, Constant

def contains(expr: Expression, sub: Expression) -> bool:
    """Checks whether the given expression contains the given
    sub-expression as a *complete* argument.

    Note that the 'complete' condition means that:
    >>> contains(x + y + z, y + z)
    True
    >>> contains((x + y) + z, y + z)
    False

    Args:
        expr (Expression): Expression to check in.
        sub (Expression): Sub-expression to check for.

    Returns:
        bool: True if expr contains sub as a *complete* sub-expression.
    """
    if expr == sub:
        return True
    else:
        for operand in expr.operands():
            #The following case covers terminal expressions
            #i.e, the operand of Variable('x') is the string 'x'
            if not isinstance(operand, Expression):
                return False
            if contains(operand, sub):
                return True
        return False

def copy(expr: Expression) -> Expression:
    """Creates a copy of the given expression.

    Args:
        expr (Expression): Expression to copy.

    Returns:
        Expression: Copied expression.
    """
    copied_operands = [copy(operand) for operand in expr.operands()]
    return type(expr)(*copied_operands)

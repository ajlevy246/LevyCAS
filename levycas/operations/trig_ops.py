"""Operations acting on an expresion's AST. These operations affect those AST's that have
trigonometric functions
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
    if isinstance(expr, Constant) or isinstance(expr, Variable):
        return copy(expr)

    operation = type(expr)

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

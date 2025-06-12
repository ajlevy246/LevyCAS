"""Operations acting on an expresion's AST. These operations affect those AST's that have
trigonometric functions
"""

from ..expressions import *
from .expression_ops import copy

from math import comb

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

def trig_expand(expr: Expression) -> Expression:
    """Given an expression, returns an equivalent expression in trigonometric-expanded form.

    Args:
        expr (Expression): The expression to expand

    Returns:
        Expression: An expression in trigonometric-expanded form.
    """
    operation = type(expr)
    if operation in [Integer, Rational, Variable]:
        return operation
    
    expanded_operands = [trig_expand(operand) for operand in expr.operands()]
    if operation == Sin:
        arg = expanded_operands[0]
        return trig_expand_recursive(arg)[0]
    elif operation == Cos:
        arg = expanded_operands[0]
        return trig_expand_recursive(arg)[1]
    else:
        return operation(*expanded_operands)

def trig_expand_recursive(expr: Expression) -> list[Expression]:
    """Given the argument x of a sin or cosine, returns a list [s, c]:
    s -> trigonometric-expanded form of sin(x)
    c -> trigonometric-expanded form of cos(x)

    Args:
        expr (Expression): x

    Returns:
        list[Expression]: s, c
    """
    operation = type(expr)
    operands = expr.operands()
    if operation == Sum:
        first_term = operands[0]
        remaining = expr - first_term
        sin_first_term, cos_first_term = trig_expand_recursive(first_term)
        sin_remaining, cos_remaining = trig_expand_recursive(remaining)
        sin_expanded = sin_first_term * cos_remaining + cos_first_term * sin_remaining
        cos_expanded = cos_first_term * cos_remaining - sin_first_term * sin_remaining
        return [sin_expanded, cos_expanded]
    elif operation == Product:
        first_factor = operands[0]
        if isinstance(first_factor, Integer):
            remaining = expr / first_factor
            return [multiple_angle_sin(first_factor, remaining), multiple_angle_cos(first_factor, remaining)]
        return [Sin(expr), Cos(expr)]
    
def multiple_angle_sin(n: Integer, theta: Expression) -> Expression:
    """Given an expression Sin(n * theta), with argument that has an integer
    multiple (n) of angle (theta), returns the expanded form.

    Args:
        n (Integer): Integer multiple
        theta (Expression): Angle

    Returns:
        Expression: Expanded form
    """
    pass

def multiple_angle_cos(n: Integer, theta: Expression) -> Expression:
    """Given an expression Cos(n * theta), with argument that has an integer
    multiple (n) of angle (theta), returns the expanded form.

    Args:
        n (Integer): Integer multiple
        theta (Expression): Angle

    Returns:
        Expression: Expanded form
    """
    pass
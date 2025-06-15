"""Methods acting on an expression's AST. These operations are not mathematical in nature.
"""

from ..expressions import *
from numbers import Number

from typing import Callable 

def contains(expr: Expression, sub: Expression) -> bool:
    """Checks whether the given expression contains the given
    sub-expression as a *complete* argument.

    Args:
        expr (Expression): Expression to check in.
        sub (Expression): Sub-expression to check for.

    Returns:
        bool: True if expr contains sub as a *complete* sub-expression.

    Examples:
    >>> contains(x + y + z, y + z)
    True
    >>> contains((x + y) + z, y + z)
    False
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

    Examples:
    >>> x = Variable('x')
    >>> x == copy(x)
    True
    >>> x is copy(x)
    False
    """
    copied_operands = []
    for operand in expr.operands():
        if isinstance(operand, Expression):
            copied_operands.append(copy(operand))
        else:
            copied_operands.append(operand)
    return type(expr)(*copied_operands)

def map_op(expr: Expression, op: Callable) -> Expression:
    """Maps the operator "op" acting on AST's to the arguments of an expression.

    Args:
        expr (Expression): The expression to map to
        op (function): The operation to map

    Returns:
        Expression: The mapped expression
    """
    if type(expr) in [Integer, Rational, Variable]:
        return op(expr)
    
    mapped_operators = [map_op(operator, op) for operator in expr.operands()]
    operation = type(expr)
    
    #Special case to force simplification
    if operation == Sum:
        return op(sum(mapped_operators))
    
    elif operation == Product:
        prod = 1
        for mapped_operator in mapped_operators:
            prod *= mapped_operator
        return op(prod)
    
    elif operation == Power:
        return op(mapped_operators[0] ** mapped_operators[1])
    
    else:
        return op(operation(*mapped_operators))
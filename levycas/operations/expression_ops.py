"""Methods acting on an expression's AST. These operations are not mathematical in nature.
"""

from ..expressions import *

from numbers import Number
from typing import Callable 

def contains(expr: Expression, subs: Expression | set[Expression]) -> bool:
    """Checks whether the given expression contains any of the given
    sub-expressions as a *complete* argument.

    Args:
        expr (Expression): Expression to check in.
        sub (Expression | set[Expression]): Sub-expression to check for.

    Returns:
        bool: True if expr contains sub as a *complete* sub-expression.

    Examples:
    >>> contains(x + y + z, y + z)
    True
    >>> contains((x + y) + z, y + z)
    False
    """
    subs = {subs} if isinstance(subs, Expression) else subs
    if expr in subs:
        return True
    else:
        if not isinstance(expr, Expression):
            return False

        for operand in expr.operands():
            #The following case covers terminal expressions
            #i.e, the operand of Variable('x') is the string 'x'
            if not isinstance(operand, Expression):
                return False
            if contains(operand, subs):
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

def construct(operands: list[Expression], op: type[Expression]) -> Expression:
    """Given a list of operands and an operation, 
    returns the constructed operation.

    The point of this method is to force simplification procedures for anonymous
    constructions. See levycas.operations.trig_ops for an example.

    Example:
        >>> sum = 1 + 1
        >>> operation = type(sum)
        >>> operands = sum.operands()
        >>> construct_op(operands, operation)
        (1 + 1)

    Args:
        operands (list[Expression]): List of operands
        op (type[Expression]): Type of operation to construct

    Returns:
        Expression: The resulting expression
    """
    if op == Sum:
        return sum(operands)

    elif op == Product:
        prod = Integer(1)
        for operand in operands:
            prod *= operand
        return prod

    elif op == Power:
        assert len(operands) == 2, f"Cannot construct a power from more/less than two arguments"
        return operands[0] ** operands[1]
    
    else:
        return op(*operands)

def substitute(expr: Expression, sub_expr: Expression, replacement: Expression) -> Expression:
    """Given an expression, replaces all instances of a complete sub-expression with 
    a replacement.

    Example:
        >>> substitute(x * (2 + y), (2 + y), x)
        (x ** 2)

        >>> substitute(2 + 2*x + 2*x**2, 2, 3)
        (3 + 3*x + 3*x**3)

    Args:
        expr (Expression): The expression to substitute in.
        sub_expr (Expression): The sub-expression to replace.
        replacement (Expression): The replacement

    Returns:
        Expression: The substituted expression
    """
    if not isinstance(expr, Expression):
        return expr

    if expr == sub_expr:
        return replacement
    
    operation = type(expr)

    if operation in [Variable, Integer, Rational]:
        return expr
    
    replaced_operands = [substitute(operand, sub_expr, replacement) for operand in expr.operands()]
    return construct(replaced_operands, operation)

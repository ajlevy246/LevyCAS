"""Methods acting on an expression's AST. These are calculus operations."""

from ..expressions import *
from .expression_ops import contains, copy
from .trig_ops import trig_substitute

def derivative(expr: Expression, wrt: Variable) -> Expression:
    """Take the derivative of an expression with respect to a variable.

    Args:
        expr (Expression): The expression to derivate
        wrt (Variable): The variable to take the derivative with respect to

    Returns:
        Expression: The computed derivative.
    """
    return _derivative_recursive(trig_substitute(expr), wrt)

def _derivative_recursive(expr: Expression, wrt: Variable) -> Expression:
    """Recursively computed derivative.

    Args:
        expr (Expression): The expression to derivate
        wrt (Variable): The variable to take the derivative with respect to

    Returns:
        Expression: The computed derivative
    """
    
    operation = type(expr)
    operands = expr.operands()

    if expr == wrt:
        return Integer(1)
    
    elif operation == Power:
        v = expr.base()
        w = expr.exponent()
        lhs = w * v ** (w - 1) * _derivative_recursive(v, wrt)
        rhs = _derivative_recursive(w, wrt) * v ** w * Ln(v)
        return (lhs + rhs)
    
    elif operation == Exp:
        arg = operands[0]
        return (_derivative_recursive(arg) * expr, wrt)

    elif operation == Sum:
        derived_operands = [_derivative_recursive(operand, wrt) for operand in operands]
        return sum(derived_operands)
    
    elif operation == Product:
        if len(operands) == 1:
            return _derivative_recursive(operands[0], wrt)
        
        v = operands[0]
        w = expr / v
        return (_derivative_recursive(v, wrt) * w + v * _derivative_recursive(w, wrt))
    
    elif operation == Sin:
        arg = operands[0]
        return (Cos(arg) * _derivative_recursive(arg, wrt))
    
    elif operation == Cos:
        arg = operands[0]
        return (-1 * Sin(arg) * _derivative_recursive(arg, wrt))
    
    else:
        if not contains(expr, wrt):
            return Integer(0)
        
        if isinstance(expr, Ln):
            arg = operands[0]
            return (_derivative_recursive(arg, wrt) / arg)

        return Derivative(expr)
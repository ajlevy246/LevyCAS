from ..expressions import *
from .expression_ops import contains, copy

def derivative(expr: Expression, wrt: Variable) -> Expression:
    """Take the derivative of an expression with respect to a variable.

    Args:
        expr (Expression): The expression to derivate
        wrt (Variable): The variable to take the derivative with respect to

    Returns:
        Expression: The computed derivative.
    """
    operation = type(expr)
    operands = expr.operands()

    if expr == wrt:
        return Integer(1)
    
    elif operation == Power:
        v = expr.base()
        w = expr.exponent()
        lhs = w * v ** (w - 1) * derivative(v, wrt)
        rhs = derivative(w, wrt) * v ** w * Ln(v)
        return (lhs + rhs).simplify()
    
    elif operation == Exp:
        arg = operands[0]
        return (derivative(arg) * expr).simplify()

    elif operation == Sum:
        derived_operands = [derivative(operand, wrt) for operand in operands]
        return sum(derived_operands).simplify()
    
    elif operation == Product:
        if len(operands) == 1:
            return derivative(operands[0], wrt)
        
        v = operands[0]
        w = Product(*operands[1::])
        return (derivative(v, wrt) * w + v * derivative(w, wrt)).simplify()
    
    elif operation == Sin:
        arg = operands[0]
        return (Cos(arg) * derivative(arg, wrt)).simplify()
    
    elif operation == Cos:
        arg = operands[0]
        return (-1 * Sin(arg) * derivative(arg, wrt)).simplify()
    
    else:
        if not contains(expr, wrt):
            return Integer(0)
        
        if isinstance(expr, Ln):
            arg = operands[0]
            return (derivative(arg, wrt) / arg).simplify()

        simplified = copy(expr).simplify()
        if expr == simplified:
            return Derivative(expr)
        return simplified.derivative(expr)
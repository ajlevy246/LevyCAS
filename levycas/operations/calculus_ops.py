"""Methods acting on an expression's AST. These are calculus operations."""

from ..expressions import *
from .expression_ops import contains, copy\

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

def integrate(expr: Expression, wrt: Variable) -> Expression | None:
    """Attempts to symbolically integrate the given expression with respect 
    to the given variable. If the operation fails, returns None. 

    Args:
        expr (Expression): The expression to integrate.
        wrt (Variable): The variable to integrate with respect to.

    Returns:
        Expression | None: The integrated expression, or None if the integration failed.
    """
    assert isinstance(wrt, Variable), f"Cannot integrate with respect to {wrt}"
    integrated = integral_match(expr, wrt)

    if integrated is None:
        integrated = linear_properties(expr, wrt)

    if integrated is None:
        integrated = substitution_method(expr, wrt)

    if integrated is None:
        expanded = algebraic_expand(expr)
        if integrated != expanded:
            integrated = integrate(expanded, wrt)

    return integrated

def integral_match(expr: Expression, wrt: Variable) -> Expression | None:
    """Integrates epxressions free of the inegration variable by matching the given expression to
    the integral table.

    Args:
        expr (Expression): The expression to integrate
        wrt (Variable): The variable to integrate with respect to

    Returns:
        Expression | None: The integrated expression, or None if the integration fails.
    """
    from .simplification_ops import sym_eval

    """Table of known integrals. Uses anonymous variable 'x'"""
    INTEGRAL_TABLE = {
    Variable('x')  : (1 / 2) * Variable('x') ** 2,  #x -> (1/2)x^2
    1 / Variable('x')      : Ln(Variable('x')),         #1 / x -> Ln(x)
    Cos(Variable('x'))     : Sin(Variable('x')),        #Cos(x) -> Sin(x)
    Sin(Variable('x'))     : -Cos(Variable('x')),       #Sin(x) -> -Cos(x)
    Exp(Variable('x'))     : Exp(Variable('x')),        #Exp(x) -> Exp(x)
    Sec(Variable('x'))**2  : Tan(Variable('x')),        #Sec(x)^2 -> Tan(x)
    -Csc(Variable('x'))**2 : Cot(Variable('x')),        #-Csc(x)^2 -> Cot(x)
    -Csc(Variable('x')) * Cot(Variable('x')) : Csc(Variable('x')),
    }

    if expr == 0:
        return Integer(0)
    
    elif not contains(expr, wrt):
        return expr * wrt
    

    elif isinstance(expr, Power):
        base = expr.base()
        exponent = expr.exponent()
        if not contains(exponent, wrt):
            return exponent * wrt ** (exponent - 1)
        
        elif exponent == wrt and not contains(base, wrt):
            return base ** wrt / Ln(base)

    substitution = {str(wrt) : Variable('x')}
    test_expr = sym_eval(expr, **substitution)
    return INTEGRAL_TABLE.get(test_expr, None)
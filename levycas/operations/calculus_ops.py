"""Methods acting on an expression's AST. These are calculus operations."""

from ..expressions import *
from .expression_ops import contains, copy, substitute
from .algebraic_ops import algebraic_expand
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
    integrated = _integrate_match(expr, wrt)

    if integrated is None:
        integrated = _integrate_linear(expr, wrt)

    if integrated is None:
        integrated = _integrate_substitute(expr, wrt)

    if integrated is None:
        expanded = algebraic_expand(expr)
        if expr != expanded:
            integrated = integrate(expanded, wrt)

    return integrated

def _integrate_match(expr: Expression, wrt: Variable) -> Expression | None:
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
        Variable('x')  : (1 / 2) * Variable('x') ** 2,                 #x -> (1/2)x^2
        1 / Variable('x') : Ln(Variable('x')),                         #1 / x -> Ln(x)
        Cos(Variable('x')) : Sin(Variable('x')),                       #Cos(x) -> Sin(x)
        Sin(Variable('x')) : -Cos(Variable('x')),                      #Sin(x) -> -Cos(x)
        Exp(Variable('x')) : Exp(Variable('x')),                       #Exp(x) -> Exp(x)
        Sec(Variable('x'))**2 : Tan(Variable('x')),                    #Sec(x)^2 -> Tan(x)
        -Csc(Variable('x'))**2 : Cot(Variable('x')),                   #-Csc(x)^2 -> Cot(x)
        -Csc(Variable('x')) * Cot(Variable('x')) : Csc(Variable('x')), #-Csc(x)*Cot(x) -> Csc(x)
        Sec(Variable('x')) * Tan(Variable('x')) : Sec(Variable('x')),  #Sec(x)Tan(x) -> Sec(x)
    }

    if expr == 0:
        return Integer(0)

    elif not contains(expr, wrt):
        return expr * wrt

    elif isinstance(expr, Power):
        base = expr.base()
        exponent = expr.exponent()
        if base == wrt and not contains(exponent, wrt) and exponent != -1:
            return (1 / (exponent + 1)) * wrt ** (exponent + 1)

        elif not contains(base, wrt) and exponent == wrt:
            return base ** wrt / Ln(base)

    substitution = {str(wrt) : Variable('x')}
    test_expr = sym_eval(expr, **substitution) 
    return INTEGRAL_TABLE.get(test_expr, None)

def _integrate_linear(expr: Expression, wrt: Variable) -> Expression | None:
    """Given an expression, integrates linearly with respect to the given variable.
    That is, uses the sum and scalar multiplication rules to split the integral, and 
    returns the result.

    Args:
        expr (Expression): The expression to integrate
        wrt (Variable): The variable to integrate with respect to

    Returns:
        Expression | None: The integrated expression, or None if the integration fails.
    """

    if isinstance(expr, Product):
        independent, dependent = _separate_factors(expr, wrt)
        if expr == dependent:
            return None
        integral = integrate(dependent, wrt)
        return independent * integral if integral is not None else None
    
    elif isinstance(expr, Sum):
        integral = 0
        for term in expr.operands():
            term_integral = integrate(term, wrt)
            if term_integral is None:
                return None
            print(f"{term_integral=}")
            integral += term_integral
        return integral

    return None

def _integrate_substitute(expr: Expression, wrt: Variable) -> Expression | None:
    """Given an expression, attempts to integrate with u-substitution with 
    respect to the given variable.

    Args:
        expr (Expression): The expression to integrate
        wrt (Variable): The variable to integrate with respect to

    Returns:
        Expression | None: The integrated expression, or None if the integration fails.
    """
    possible_substitutions = _trial_substitutions(expr)
    print(f"Possible substitutions: {possible_substitutions}")
    for substitution in possible_substitutions:
        if substitution != wrt and contains(substitution, wrt):
            test_expr = substitute(expr / derivative(substitution, wrt), substitution, Variable('v'))
            if not contains(test_expr, wrt):
                return substitute(integrate(test_expr, Variable('v')), Variable('v'), substitution)

    return None

def _trial_substitutions(expr: Expression) -> set[Expression]:
    """Given an expression, returns a set of complete sub-expressions
    that are candidates for u-substitution. These candidates are all 
    functions, arguments of functions, or bases/exponents of powers.

    Args:
        expr (Expression): The expression to search through.

    Returns:
        set[Expression]: Set of complete sub-expression to be used as substitution candidates.
    """
    candidates = set()
    
    operation = type(expr)
    if operation in [Integer, Rational, Variable]:
        return candidates
    
    #TODO: Have all functions (trigonometric, exponential) inherit from the Function class.
    if isinstance(expr, Function):
        candidates.add(expr)
        candidates = candidates.union(set(expr.operands()))
    elif operation == Power:
        candidates.add(expr.base())
        candidates.add(expr.exponent())

    operands = expr.operands()
    for operand in operands:
        candidates = candidates.union(_trial_substitutions(operand))
    return candidates

def _separate_factors(expr: Product, wrt: Variable) -> list[Product | Integer]:
    """Given a product of factors, separates the factors into those independent of the given variable
    and those dependent on it.

    Args:
        expr (Product): Product to separate
        wrt (Variable): Variable to separate with respect to

    Returns:
        list[Product]: The list [independent, dependent]
    """
    independent = Integer(1)
    dependent = Integer(1)

    for factor in expr.operands():
        if contains(factor, wrt):
            dependent *= factor
        else:
            independent *= factor

    return [independent, dependent]
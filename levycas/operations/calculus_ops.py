"""Methods acting on an expression's AST. These are calculus operations."""

from ..expressions import *
from .expression_ops import contains, copy, substitute
from .algebraic_ops import algebraic_expand, linear_form, quadratic_form
from .polynomial_ops import is_polynomial, polynomial_divide, degree

class Deriv(Elementary):
    """Anonymous derivative class"""
    pass

def derivative(expr: Expression, wrt: Variable) -> Expression:
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
        lhs = w * v ** (w - 1) * derivative(v, wrt)
        rhs = derivative(w, wrt) * v ** w * Ln(v)
        return (lhs + rhs)

    elif operation == Sum:
        derived_operands = [derivative(operand, wrt) for operand in operands]
        return sum(derived_operands)

    elif operation == Product:
        if len(operands) == 1:
            return derivative(operands[0], wrt)
        
        v = operands[0]
        w = expr / v
        return (derivative(v, wrt) * w + v * derivative(w, wrt))

    elif isinstance(expr, Elementary):
        arg = operands[0]
        arg_deriv = derivative(arg, wrt)

        if operation == Deriv:
            return Deriv(expr, wrt) * arg_deriv

        elif operation == Exp:
            return (arg_deriv * expr)

        elif operation == Ln:
            return (arg_deriv / arg)

        elif operation == Sin:
            return (Cos(arg) * arg_deriv)

        elif operation == Cos:
            return (-1 * Sin(arg) * arg_deriv)

        elif operation == Tan:
            return (Sec(arg)**2 * arg_deriv)

        elif operation == Sec:
            return Sec(arg) * Tan(arg) * arg_deriv
        
        elif operation == Csc:
            return -Cot(arg) * Csc(arg) * arg_deriv
        
        elif operation == Cot:
            return -Csc(arg)**2 * arg_deriv

        elif operation == Arccos:
            return -arg_deriv / (1 - arg**2)**(1 / 2)

        elif operation == Arcsin:
            return arg_deriv / (1 - arg**2)**(1 / 2)

        elif operation == Arctan:
            return arg_deriv / (1 + arg**2)

    else:
        if not contains(expr, wrt):
            return Integer(0)

        return Deriv(expr, wrt)

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
        integrated = _integrate_rational(expr, wrt)

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

    """Table of known integrals, especially containing elementary functions. Uses anonymous variable x"""
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

    substitution = {str(wrt) : Variable('x')}
    test_expr = sym_eval(expr, **substitution)
    integrated = INTEGRAL_TABLE.get(test_expr, None)
    if integrated is None:
        return None
    return substitute(integrated, Variable('x'), wrt)

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
    for substitution in possible_substitutions:
        if substitution != wrt and contains(substitution, wrt):
            test_expr = substitute(expr / derivative(substitution, wrt), substitution, Variable('v'))
            if not contains(test_expr, wrt):
                test_integral = integrate(test_expr, Variable('v'))
                if test_integral is None:
                    continue
                return substitute(test_integral, Variable('v'), substitution)

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
    if isinstance(expr, Elementary):
        candidates.add(expr)
        candidates = candidates.union(set(expr.operands()))
    elif operation == Power:
        candidates.add(expr.base())
        candidates.add(expr.exponent())

    operands = expr.operands()
    for operand in operands:
        candidates = candidates.union(_trial_substitutions(operand))
    return sorted(candidates)

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

def _integrate_rational(expr: Expression, wrt: Variable) -> Expression | None:
    """Given an expression in rational form, attemps to integrate with respect to the given variable.
    Expressions integrated with this method are of the form (rx + s) / (ax^2 + bx + c)

    Args:
        expr (Expression): The expression to integrate
        wrt (Variable): The variable to integrate with respect to

    Returns:
        Expression | None: The integrated expression, or None if the integration fails.
    """
    numerator = linear_form(expr.num(), wrt)
    if numerator is None:
        return None
    r, s = numerator

    denominator = quadratic_form(expr.denom(), wrt)
    if denominator is None or denominator[0] == 0:
        return None
    a, b, c = denominator

    if r == 0:
        discriminant = b**2 - 4 * a * c
        if isinstance(discriminant, Constant):
            if discriminant == 0:
                return (-2) / (2 * a * wrt + b)
            
            elif discriminant.is_positive():
                #TODO: hyperbolic trigonometric functions not yet implemented
                # return -2 * Arctanh((2*a*wrt + b) / (discriminant)**(1 / 2)) / (discriminant)
                return None

        return 2 * Arctan((2*a*wrt + b) / (-discriminant)**(1 / 2)) / (-discriminant)**(1 / 2)

    quadratic = a*wrt**2 + b*wrt + c
    return (r / 2*a) * Ln(quadratic) + (s - r*b / (2*a)) * integrate(quadratic, wrt)

def _integrate_rational(expr: Expression, wrt: Variable) -> Expression:
    """Given an expression in rational form, attemps to integrate with respect to the given variable.
    Expressions integrated with this method are of the form (rx + s) / (ax^2 + bx + c)

    Args:
        expr (Expression): The expression to integrate
        wrt (Variable): The variable to integrate with respect to

    Returns:
        Expression | None: The integrated expression, or None if the integration fails.
    """
    denominator = expr.denom()
    if not is_polynomial(denominator, wrt):
        return None
    denom_degree = degree(denominator, wrt)
    if not int(denom_degree) <= 2:
        return None

    numerator = expr.num()
    if not is_polynomial(numerator, wrt):
        return None
    num_degree = degree(numerator, wrt)
    if num_degree > denom_degree:
        quotient, remainder = polynomial_divide(numerator, denominator, [wrt])
        return integrate(quotient + remainder / denominator, wrt)
    
    a, b, c = quadratic_form(denominator, wrt)
    discriminant = b**2 - 4*a*c 
    if numerator == 1:
        if isinstance(discriminant, Integer):
            if discriminant == 0:
                return -2 / (2*a*wrt + b)
            elif discriminant.is_positive():
                #Hyperbolic arctanh not yet implemented
                return None
        
        return 2 * Arctan((2*a*wrt + b)/(-discriminant)**(1/2)) / (-discriminant)**(1/2)

    else:
        if num_degree == 1:
            r, s = linear_form(numerator, wrt)
            alpha = r / (2*a)
            beta = s - r*b/(2*a)
            #Correction from Elementary Algorithms, beta -> 1/beta
            return alpha*Ln(denominator) + (1/beta) * integrate(1 / denominator, wrt)


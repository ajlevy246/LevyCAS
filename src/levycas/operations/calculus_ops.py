"""Methods acting on an expression's AST. These are calculus operations."""

from ..expressions import *
from .expression_ops import contains, substitute
from .algebraic_ops import algebraic_expand, linear_form, quadratic_form
from .polynomial_ops import (
    is_polynomial, 
    polynomial_divide, 
    degree, 
    partial_fractions, 
    polynomial_gcd, 
    coefficient,
    _solve_linear_system,
)
from .trig_ops import trig_simplify

from typing import Literal
from numbers import Number

"""Max recursive depth for relevant routines (e.g. limit)"""
_MAX_DEPTH = 10

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
        integrated = _integrate_known_byparts(expr, wrt)

    if integrated is None:
        expanded = algebraic_expand(expr)
        if expr != expanded:
            integrated = integrate(expanded, wrt)

    if integrated is None:
        simp = trig_simplify(expr)
        if expr != simp:
            integrated = integrate(simp, wrt)
    
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
    X = Variable("x")
    INTEGRAL_TABLE = {
        X              : (1/2)*X**2,   
        1/X            : Ln(X),        
        Exp(X)         : Exp(X),       
        Ln(X)          : X * Ln(X) - X,
        Cos(X)         : Sin(X),       
        Sin(X)         : -Cos(X),      
        Sec(X)**2      : Tan(X),       
        Sec(X)*Tan(X)  : Sec(X),       
        -Csc(X)**2     : Cot(X),       
        -Csc(X)*Cot(X) : Csc(X),       
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
        wrt (Variable): Variable of integration

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
    """Given an expression in rational form (P/Q with P, Q polynomials), 
    attemps to integrate with respect to the given variable via Hermite reduction,
    partial fractions or closed forms.

    Args:
        expr (Expression): The expression to integrate
        wrt (Variable): The variable of integration 

    Returns:
        Expression | None: The integrated expression, or None if the integration fails.
    """
    from .factorization_ops import factor
    num, denom = algebraic_expand(expr.num()), algebraic_expand(expr.denom())
    if not (is_polynomial(denom, wrt) and is_polynomial(num, wrt)):
        # Expression is not rational, try integrating somewhere else
        return None
    
    num_degree, denom_degree = degree(num, wrt), degree(denom, wrt)
    if num_degree >= denom_degree:
        Q, R = polynomial_divide(num, denom, [wrt])
        R_int = integrate(R/denom, wrt)
        if R_int is not None:
            return integrate(Q, wrt) + R_int
        return None

    reduction = _hermite_reduce(num, denom, wrt)
    if reduction not in (None, 0):
        return reduction
    
    if denom_degree <= 2:
        # try first with partial fractions, which 
        # returns a nice result if successful.
        partial_int = _integrate_partial(num, denom, wrt)
        if partial_int is not None: 
            return partial_int

        # Failed with partial fractions, return 
        #  closed form (which might be uglier).
        a, b, c = quadratic_form(denom, wrt)
        discriminant = b**2 - 4*a*c
        if num == 1:
            if not isinstance(discriminant, Integer) or discriminant < 0:
                sqrt_nd = (-discriminant)**(1/2)
                return 2 * Arctan((2*a*wrt + b)/sqrt_nd) / sqrt_nd
            if discriminant == 0:
                return -2 / (2*a*wrt + b)
            elif discriminant.is_positive():
                # Arctanh form uses Ln expansion.
                #  assumes complex logarithm until Abs() implemented.
                sqrt_d = discriminant ** (1/2)
                return -1 / sqrt_d * Ln((1 + (2*a*wrt + b) / sqrt_d)/(1 - (2*a*wrt + b) / sqrt_d))

        elif num_degree == 1:
            r, s = linear_form(num, wrt)
            alpha = r / (2*a)
            beta = s - r*b/(2*a)
            #Correction from Elementary Algorithms, beta -> 1/beta
            factor = integrate(1 / denom, wrt)
            return None if factor is None else alpha*Ln(denom) + beta * factor
                
        return None
    
    # no closed form for denominator of degree > 2;
    #  try partial fractions
    return _integrate_partial(num, denom, wrt)

def _hermite_reduce(P: Expression, Q: Expression, x: Expression) -> Expression | None:
    """Uses Hermite's method to reduce the integral p/q in x.

    Algorithm 11.1 from Algorithms for Computer Algebra (Geddes, Czapor, Labahn)

    Args:
        P (Expression): Numerator
        Q (Expression): Denominator
        x (Expression): Polynomial generalized variable

    Returns:
        Expression: The sum rational_part + \int(poly_part) + \int(integral_part)
    """
    from .factorization_ops import factor_sqfree

    # Check that denominator is square-free
    g = polynomial_gcd(Q, derivative(Q, x), [x])
    if g == 1:
        return None

    poly_part, r_rem = polynomial_divide(P, Q, x)

    factors = factor_sqfree(Q, x)
    q = [factor.base() for factor in factors]
    mult = [factor.exponent() for factor in factors]

    # Construct numerators dict r := {(factor_base, multiplicity) -> numerator}
    pf_decomp = partial_fractions(r_rem, factors, x)
    r = {}
    terms = pf_decomp.operands() if isinstance(pf_decomp, Sum) else [pf_decomp]
    for term in terms:
        
        # the following mess is due to constants automatically distributed across
        #  sum. e.g. (1/9) / (x+1) has _denom() -> 9x+9.
        #  thus we manually move the coefficient in the denominator back to the numerator.
        c = term.coefficient()
        term /= c
        num, denom = term.num(), term.denom()
        num *= c

        if isinstance(denom, Power):
            f, m = denom.base(), denom.exponent()
        else:
            f, m = denom, Integer(1)

        r[(f, m)] = num

    rational_part, integral_part = Integer(0), Integer(0)

    for idx in range(len(q)):
        qi = q[idx]
        m_i = mult[idx]
        qi_prime = derivative(qi, x)

        # reduce numerators from multiplicity m_i down to multiplicity 2
        for j in range(m_i, 1, -1):
            num_ij = r.get((qi, j), Integer(0))
            if num_ij == 0:
                continue

            reduction = _hermite_solve_reduction(qi, qi_prime, num_ij, x)
            if reduction is None:
                return None
            s, t = reduction

            rational_part -= t / ((j - 1) * qi ** (j - 1))
            r[(qi, j - 1)] = r.get((qi, j - 1), Integer(0)) + s + derivative(t, x) / (j - 1)

        # what's left has multiplicity 1 and goes into the "hard" integral part
        integral_part += r.get((qi, 1), Integer(0)) / qi

    poly_integral = integrate(poly_part, x)
    if poly_integral is None:
        return None
    integral_part_integral = integrate(integral_part, x)
    if integral_part_integral is None:
        return None

    return rational_part + poly_integral + integral_part_integral

def _hermite_solve_reduction(f, f_prime, num, x) -> tuple[Expression, Expression] | None:
    """Solves s*f + t*f' = num for polynomials s, t with deg(s), deg(t) < deg(f).

    f and f' are coprime (f is square-free), so a solution always exists.
    """
    n = degree(f, x)
    if n == 0:
        return Integer(0), Integer(0)

    s_coeffs = [Variable(f'<s_{k}>') for k in range(n)]
    t_coeffs = [Variable(f'<t_{k}>') for k in range(n)]
    s = sum((c * x**k for k, c in enumerate(s_coeffs)), Integer(0))
    t = sum((c * x**k for k, c in enumerate(t_coeffs)), Integer(0))

    eq = algebraic_expand(s * f + t * f_prime - num)
    deg_eq = degree(eq, x)
    if deg_eq is None:
        deg_eq = 0

    system = [coefficient(eq, x, d) for d in range(deg_eq + 1)]
    soln = _solve_linear_system(system)
    if soln is None:
        return None

    s_val = sum((soln.get(c, Integer(0)) * x**k for k, c in enumerate(s_coeffs)), Integer(0))
    t_val = sum((soln.get(c, Integer(0)) * x**k for k, c in enumerate(t_coeffs)), Integer(0))
    return s_val, t_val

def _integrate_partial(num: Expression, denom: Expression, wrt: Expression) -> Expression | None:
    """Given an expression in rational form (P/Q with P, Q polynomials), 
    attemps to integrate with respect to the given variable by decomposing via partial fractions.

    Args:
        num (Expression): Numerator (P)
        denom (Expression): Denominator (Q)
        wrt (Expression): Generalised variable of integration

    Returns:
        Expression | None: The integrated expression, or None if the partial fractions decomposition fails.
    """
    from .factorization_ops import factor

    constant, *factors = factor(denom, wrt)
    decomposed_expr = partial_fractions(num, factors, wrt)
    if decomposed_expr is None or decomposed_expr == num/(constant*Product(*factors)):
        # Partial fractions failed to yield new information.
        return None
    decomposed_integral = integrate(decomposed_expr, wrt)
    if decomposed_integral is None:
        return None
    return (1 / constant) * decomposed_integral

def _integrate_known_byparts(expr: Expression, wrt: Variable) -> Expression | None:
    """Given an expression of a known form that can be integrated wrt to the given 
    variable using a integration by parts recurrence, returns the integrated formula. 
    Otherwise, returns None

    Args:
        expr (Expression): The expression to integrate
        wrt (Variable): The variable of integration

    Returns:
        Expression | None: The integrated expression, or None if the integration fails
    """
    if type(expr) is not Product:
        return None

    factors = expr.operands()
    if len(factors) != 2:
        return None
    
    op, var = factors
    if not (isinstance(var, Power) or var == wrt):
        return None
    base, exp = var.base(), var.exponent()
    if base != wrt or not isinstance(exp, Integer) or exp.is_negative():
        return None
    linear_op = linear_form(op.operands()[0], wrt)
    if linear_op is None:
        return None
    a, b = linear_op

    #Integrand is of the form (x^n) * op(ax + b)
    if isinstance(op, Exp):
        by_parts = integrate(wrt ** (exp - 1) * op, wrt)
        if by_parts is None:
            return None
        return var / a * op - exp / a * by_parts
    
    elif isinstance(op, Sin):
        by_parts = integrate(wrt ** (exp - 1) * Cos(a*wrt + b), wrt)
        if by_parts is None:
            return None
        return -var / a * Cos(a*wrt + b) + exp / a * by_parts
    
    elif isinstance(op, Cos):
        by_parts = integrate(wrt ** (exp - 1) * Sin(a*wrt + b), wrt)
        if by_parts is None:
            return None
        return var / a * Sin(a*wrt + b) - exp / a * by_parts

    elif isinstance(op, Ln):
        by_parts = integrate((wrt**(exp+1))/(a*wrt+b), wrt)
        if by_parts is None:
            return None
        return (wrt**(exp+1)) / (exp+1) * Ln(a*wrt+b) - a/(exp+1) * by_parts
 
def limit(expr: Expression, x: Variable, point: Constant | Number) -> Expression | Literal['UNDEFINED']:
    """Compute the limit of an expression at a point."""
    point = convert_primitive(point)

    lim = trig_simplify(substitute(expr, x, point))
    if lim is not UNDEFINED: return lim

    num, denom = expr.num(), expr.denom()
    num_val   = trig_simplify(substitute(expr.num(), x, point))
    denom_val = trig_simplify(substitute(expr.denom(), x, point))
    if denom_val == 0 and num_val == 0:
        return _lhopital(num, denom, x, point)
    return UNDEFINED # TODO: Update when signed inifinites are implemented.
    
def _lhopital(num: Expression, denom: Expression, x: Variable, point: Constant, depth: int = 0) -> Expression | Literal['UNDEFINED']:
    if depth > _MAX_DEPTH:
        return UNDEFINED
    
    num_val = trig_simplify(substitute(num, x, point))
    denom_val = trig_simplify(substitute(denom, x, point))
    if num_val == 0 and denom_val == 0:
        return _lhopital(
            derivative(num, x), derivative(denom, x),
            x, point, depth+1,   
        )
    if denom_val != 0:
        return num_val / denom_val
    return UNDEFINED
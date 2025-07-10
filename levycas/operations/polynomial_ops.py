"""Operations on generalized polynomial expressions, both single and multivariate cases"""
from numbers import Number

from ..expressions import *
from .expression_ops import contains
from .algebraic_ops import algebraic_expand
from .numerical_ops import gcd

def is_monomial(expr: Expression, vars: Expression | set[Expression]) -> bool:
    """Checks whether the given expression is a monomial in the given variables.

    Args:
        expr (Expression): The expression to check
        vars (Variable | set[Variable]): The parameters of the monomial expression.

    Returns:
        bool: True if the expression is a generalized monomial expression in the given variables, False otherwise.
    """
    vars = vars if isinstance(vars, set) else {vars}

    if expr in vars:
        return True
    
    operation = type(expr)
    if operation == Power:
            base = expr.base()
            exponent = expr.exponent()
            if base in vars and isinstance(exponent, Integer) and Integer(1) < exponent:
                return True
            
    elif operation == Product:
            for factor in expr.operands():
                if not is_monomial(factor, vars):
                    return False
            return True
        
    return not contains(expr, vars)

def is_polynomial(expr: Expression, vars: Expression | set[Expression]) -> bool:
    """Checks whether the given expression is a polynomial in the given variables.

    Args:
        expr (Expression): The expression to check
        vars (Expression | set[Expression]): The set of parameters of the polynomial

    Returns:
        bool: True if the expression is a generalized polynomial expression in the given variables, False otherwise.
    """
    vars = vars if isinstance(vars, set) else {vars}

    if isinstance(expr, Sum):
        if expr in vars:
              return True
        for term in expr.operands():
            if not is_monomial(term, vars):
                return False
        return True
    
    return is_monomial(expr, vars)

def variables(expr: Expression) -> set[Expression]:
    """For a generalized polynomial expression, returns the set of parameters.

    Examples:
        >>> variables(x**3 + 3*x**2*y+3*x*y**2 + y**3)
        {x, y}

        >>> variables(a*sin(x)**2 + 2*b*Sin(x) + 3c)
        {a, b, c, Sin(x)}

        >>> variables(1)
        {}

    Args:
        expr (Expression): A generalized polynomial expression.

    Returns:
        set[Expression]: The set of parameters, or the empty set
    """
    if isinstance(expr, Constant) or not isinstance(expr, Expression):
        return set()

    operation = type(expr)
    if operation == Power:
        exponent = expr.exponent()
        if isinstance(exponent, Integer) and Integer(1) < exponent:
            return {expr.base()}
        return {expr}

    elif operation == Sum:
        vars = set()
        for term in expr.operands():
            vars |= variables(term)
        return vars

    elif operation == Product:
        vars = set()
        for factor in expr.operands():
            vars |= variables(factor)
        return vars

    return {expr}

def _fill_variables(expr: Expression, vars: Expression | list[Expression]) -> list[Expression]:
    """For many of the following algorithm, it is necessary to get a list of parameters for a given
    multivariate polynomial. Given an expression and a partially filled list of generalized variables,
    returns the filled list. 

    Examples:
        >>> _fill_variables(x*y*z, x | [x])
        [x, y, z]

    Args:
        expr (Expression): _description_
        vars (Expression | list[Expression]): _description_

    Returns:
        list[Expression]: _description_
    """
    vars = vars if isinstance(vars, list) else [vars]
    all_vars = variables(expr)
    for var in all_vars:
        if isinstance(var, Variable) and var not in vars:
            vars.append(var)
    return vars

def coefficient(expr: Expression, var: Expression, degree: Integer) -> Expression | None:
    """Given a generalized polynomial expression, 

    Examples:
        >>> coefficient(ax^2 + bx + c, x, 2)
        a

        >>> coefficient(3xy^2 + 5x^2y + 7x + 9, x, 1)
        3y^2 + 7

        >>> coefficient(3xy^2 + 5x^2y + 7x + 9, x, 3) 
        0

        >>> coefficient(3sin(x)x^2 + 2ln(x)x + 4, x, 2) 
        None

    Args:
        expr (Expression): A generalized polynomial expression.
        var (Expression): The generalized variable to extract the coefficient from.
        degree (Integer): The exponent of the variable to extract the coefficient from.

    Returns:
        Expression | None: The coefficient of the generalized variable, or None if it does not exist.
    """
    degree = convert_primitive(degree)
    if isinstance(expr, Sum):
        if expr == var:
            return degree if degree == Integer(1) else Integer(0)
        sum_coeff = 0
        for term in expr.operands():
            f = _coefficient_monomial(term, var)
            if f is None:
                return None
            term_coeff, term_degree = f
            if term_degree == degree:
                sum_coeff += term_coeff
        return sum_coeff

    else:
        f = _coefficient_monomial(expr, var)
        if f is None:
            return None

        factor_coeff, factor_degree = f
        if factor_degree == degree:
            return factor_coeff
        return Integer(0) 

def _coefficient_monomial(expr: Expression, var: Expression) -> list[Expression] | None:
    """Given a monomial expression u and a variable x, returns the list [a, n]
    where n is the degree of x and a is its coefficient in u.

    Args:
        expr (Expression): u
        var (Expression): x

    Returns:
        list[Expression] | None: The list [a, n], or None if the operation fails.
    """
    if expr == var:
        return [Integer(1), Integer(1)]

    operation = type(expr)
    if operation == Power:
        base = expr.base()
        exponent = expr.exponent()
        if base == var and isinstance(exponent, Integer) and Integer(1) < exponent:
            return [Integer(1), exponent]
        
    elif operation == Product:
        m = Integer(0)
        c = expr
        for factor in expr.operands():
            factor_coeff = _coefficient_monomial(factor, var)
            if factor_coeff is None:
                return None
            coeff, degree = factor_coeff
            if degree != 0:
                m = degree
                c = expr / (var ** m)
        return [c, m]

    if not contains(expr, var):
            return [expr, Integer(0)]

    return None

def degree(expr: Expression, vars: Expression | set[Expression]) -> Integer | None:
    """Given a generalized polynomial expression u and a set of parameters x,
    returns the highest degree of x in u.

    Args:
        expr (Expression): The polynomial expression u
        vars (Expression | set[Expression]): The parameter set x

    Returns:
        Integer: The degree of x in u, or None if the operation fails
    """
    #By convention, the degree of the zero-polynomial is -oo. Here, 
    #I'll default to -1 until -oo is implemented.
    if expr == 0:
        return -1
    vars = {vars} if not isinstance(vars, set) else vars
    if isinstance(expr, Sum):
        deg = Integer(0)
        for term in expr.operands():
            deg_sum = Integer(0)
            for var in vars:
                monomial = _coefficient_monomial(term, var)
                if monomial is None:
                    return None
                deg_sum += monomial[1]
            deg = deg_sum if deg < deg_sum else deg
        return deg

    else:
        deg_sum = Integer(0)
        for var in vars:
            monomial = _coefficient_monomial(expr, var)
            if monomial is None:
                return None
            deg_sum += monomial[1]
        return deg_sum

def leading_coefficient(expr: Expression, var: Expression) -> Expression | None:
    """Given a generalized polynomial expression u with parameter x, returns 
    the coefficient of the highest power of x in u.

    Args:
        expr (Expression): The expression u
        var (Expression): The parameter x

    Returns:
        Expression | None: Coefficient of the highest power of x
    """
    if isinstance(expr, Sum):
        deg = Integer(0)
        coeff = Integer(0)
        for term in expr.operands():
            deg_sum = Integer(0)
            coeff_sum = Integer(0)
            monomial = _coefficient_monomial(term, var)
            if monomial is None:
                return None
            deg_sum += monomial[1]
            coeff_sum += monomial[0]
            if deg == deg_sum:
                coeff += coeff_sum
            elif deg < deg_sum:
                deg = deg_sum
                coeff = coeff_sum
        return coeff
    else:
        return _coefficient_monomial(expr, var)[0]

def lex_lt(first: Expression, second: Expression, ordering: list[Expression]) -> bool:
    """Returns the monomial ordering of two expressions. True if first < second, 
    or false otherwise. Default behavior is lexicographic ordering. 

    If both monomials have the same variable part, then
    both first < second and second < first are false.

    Args:
        first (Expression): The first monomial to compare
        second (Expression): The second monomial to compare
        ordering (list[Expression]): The ordering of the generalized variables

    Returns:
        bool: True if first < second; False otherwise
    """
    for var in ordering:
        first_deg = degree(first, var)
        second_deg = degree(second, var)
        if first_deg == second_deg:
            continue

        return True if first_deg < second_deg else False

    return False

def leading_monomial(expr: Expression, ordering: list[Expression]) -> Expression:
    """Returns the leading monomial of a rational polynomial expression. The order of monomials
    is ordered based on the given lexicographical ordering.

    Examples:
        >>> expr = 3*x**2*y + 4*x*y**2 + y**3 + x + 1
        >>> leading_monomial(expr, [x, y])
        3 * x**2 * y

        >>> leading_monomial(expr, [y, x]])
        y**3

    Args:
        expr (Expression): A rational polynomial expression
        ordering (list[Expression]): An ordering of generalized variables

    Returns:
        Expression: The leading monomial of the polynomial
    """
    ordering = ordering if isinstance(ordering, list) else [ordering]

    if len(ordering) == 0:
        return expr

    var = ordering[0]
    remaining = ordering[1::]
    exponent = degree(expr, var)
    coeff = coefficient(expr, var, exponent)
    return var**exponent * leading_monomial(coeff, remaining)

def polynomial_divide_recursive(u: Expression, v: Expression, L: list[Expression]) -> tuple[Expression]:
    """Recursively computes the polynomial quotient of u and v.

    Args:
        u (Expression): _description_
        v (Expression): _description_
        L (list[Expression]): _description_
    """
    #If the list of generalized variables is empty, this is 
    #just rational number division
    if len(L) == 0:
        if v == 0:
            raise ZeroDivisionError
        return [u / v, Integer(0)]
    
    x = L[0]
    r = u
    m, n = degree(r, x), degree(v, x)
    q = 0
    lcv = leading_coefficient(v, x)
    while not m < n: #Iterate until degree of the that of the divisor.
        lcr = leading_coefficient(r, x)
        c, rem = polynomial_divide_recursive(lcr, lcv, L[1::])
        if rem != 0 or c == 0:
            break

        q += c * x ** (m - n)
        r = algebraic_expand(r - c * v * x **(m -n))
        m = degree(r, x)
    return (algebraic_expand(q), r)

def monomial_divide(dividend: Expression, divisor: Expression) -> Expression:
    """Computes the division u / v, where u is a polynomial and v is a monomial,
    both with rational coefficients.

    Args:
        dividend (Expression): A polynomial with rational coefficients
        divisor (Expression): A monomial with rational coefficient.

    Returns:
        Expression: The list [Q, R] where Q is the quotient and R the remainder of the division.
    """
    terms = dividend.operands() if isinstance(dividend, Sum) else [dividend]
    quotient = Integer(0)
    remainder = Integer(0)
    for term in terms:
        term_quot = term / divisor
        if isinstance(term_quot.denom(), (Constant, Number)):
            quotient += term_quot
        else:
            remainder += term
    return [quotient, remainder]

def polynomial_divide(dividend: Expression, divisor: Expression, ordering: list[Expression]) -> tuple[Expression]:
    """Given two general polynomial expressions with rational coefficients, performs monomial-based
    division and returns the result [Quotient, Remainder]

    This is the polynomial long division algorithm from Mathematical Methods. Polynomial division
    ensures that deg(R) < deg(Divisor). Division is performed with respect to the monomial ordering given.

    Args:
        dividend (Expression): A rational polynomial
        denominator (Expression): A rational polynomial
        ordering (list[Expression]): Ordered list of generalized variables

    Returns:
        list[Expression]: The list [Q, R] where Q is the quotient and R the remainder of the division.
    """
    quotient = Integer(0)
    remainder = dividend
    lm = leading_monomial(divisor, ordering)
    f = monomial_divide(remainder, lm)[0]
    while f != 0:
        quotient += f
        remainder = algebraic_expand(remainder - f * divisor)
        f = monomial_divide(remainder, lm)[0]
    return (quotient, remainder)

def polynomial_pseudo_divide(u, v, x):
    p, s = 0, u
    m, n = degree(s, x), degree(v, x)
    delta = m - n + 1
    if delta.is_negative():
        delta = 0
    lcv = coefficient(v, x, n)
    sigma = 0
    while not m < n:
        lcs = coefficient(s, x, m)
        p = lcv * p + lcs * x**(m - n)
        s = algebraic_expand(lcv * s - lcs * v * x ** (m - n))
        sigma += 1
        m = degree(s, x)
    return algebraic_expand(lcv ** (delta - sigma) * p), algebraic_expand(lcv ** (delta - sigma) * s)

def _is_univariate(expr: Expression, var: Expression) -> bool:
    """Determines if an expression is univariate with respect 
    to the given variable.

    Args:
        expr (Expression): The polynomial to check
        var (Expression): The generalized variable to check respect to

    Returns:
        bool: True if the polynomial expression is univariate wrt var
    """
    return variables(expr) == variables(var)

def _univariate_gcd(u: Expression, v: Expression,  x: Expression) -> Expression:
    """Computes the gcd of a univariate polynomial in x.

    Args:
        u (Expression): u(x)
        v (Expression): v(x)
        var (Expression): x

    Returns:
        Constant: gcd(u, v)
    """
    return _univariate_extended_euclidean(u, v, x)[0]

def _univariate_extended_euclidean(u: Expression, v: Expression, x: Expression) -> tuple[Expression]:
    """Extended euclidean algorithm for univariate polynomials.

    Args:
        u (Expression): u(x)
        v (Expression): v(x)
        x (tuple[Expression]): Parameter x

    Returns:
        Expression: The list [g, r, s] where gcd(u, v) = g = u*r + v*s
    """
    if u == 0 and v == 0:
        return [0, 0, 0]

    U, V = u, v
    app, ap = 1, 0
    bpp, bp = 0, 1
    while V != 0:
        q, r = polynomial_divide(U, V, x)
        a, b = app - q * ap, bpp - q * bp
        app, bpp = ap, bp
        ap, bp = a, b
        U, V = V, r
    c = leading_coefficient(U, x)
    app, bpp = algebraic_expand(app / c), algebraic_expand(bpp / c)
    U = algebraic_expand(U / c)
    return (U, app, bpp)

def univariate_partial_fractions(u: Expression, v1: Expression, v2: Expression, x: Expression) -> tuple[Expression]:
    """Given a rational expression u / (v1v2) where u, v1, v2 are univariate in
    x and v1 and v2 are coprime wrt x, returns the expanded u1/v1 + u2/v2, where 
    both terms are proper rational expressions.

    Args:
        u (Expression): Numerator
        v1 (Expression): LHS of denominator
        v2 (Expression): RHS of denominator
        x (Expression): Generalized variable

    Returns:
        tuple[Expressio] The list [u1, u2] in the decomposition u/(v1v2) = u1/v1 + u2/v2
    """
    d, a, b = _univariate_extended_euclidean(v1, v2, x)
    assert d == 1, f"partial fraction factors must be coprime"
    u1 = polynomial_divide(algebraic_expand(b*u), v1, x)[1]
    u2 = polynomial_divide(algebraic_expand(a*u), v2, x)[1]
    return u1, u2

def polynomial_gcd(u: Expression, v: Expression, L: list[Expression]) -> Expression:
    """Given u, v that are two multivariate polynomials with variables in L and rational coefficients,
    computes the greatest common divisor gcd(u, v) and returns it (normalized).

    Args:
        u (Expression): u(*L), a multivariate polynomial with rational coefficients.
        v (Expression): v(*L), a multivariate polynomial with rational coefficients.
        L (list[Expression]): The ordered list of variables

    Returns:
        Expression: gcd(u, v)
    """
    u, v = algebraic_expand(u), algebraic_expand(v)
    if u == 0:
        return _normalize(v, L)
    if v == 0:
        return _normalize(u, L)
    return _normalize(_polynomial_gcd_rec(u, v, L), L)

def _polynomial_gcd_rec(u, v, L):
    """Given u, v that are two multivariate polynomials with variables in L and rational coefficients,
    computes the greatest common divisor gcd(u, v), and returns it (non-normalized).

    This is the sub-resultant algorithm given in Mathematical Methods.

    Args:
        u (Expression): u(*L), a multivariate polynomial with rational coefficients.
        v (Expression): v(*L), a multivariate polynomial with rational coefficients.
        L (list[Expression]): The ordered list of variables

    Returns:
        Expression: gcd(u, v)
    """
    if len(L) == 0:
        return gcd(u, v)
    
    x, R = L[0], L[1::]
    U, V = (v, u) if degree(u, x) < degree(v, x) else (u, v)
    cont_U, cont_V = polynomial_content(U, x, R), polynomial_content(V, x, R)
    d = _polynomial_gcd_rec(cont_U, cont_V, R)
    U, V = polynomial_divide_recursive(U, cont_U, L)[0], polynomial_divide_recursive(V, cont_V, L)[0]
    g = _polynomial_gcd_rec(leading_coefficient(U, x), leading_coefficient(V, x), R)

    i = 1
    while V != 0:
        r = polynomial_pseudo_divide(U, V, x)[1]
        if r != 0:
            if i == 1:
                delta = degree(U, x) - degree(V, x) + 1
                psi = -1
                beta = (-1)**delta
            else:
                delta_p = delta
                delta = degree(U, x) - degree(V, x) + 1
                f = leading_coefficient(U, x)
                psi = polynomial_divide_recursive(algebraic_expand(-f)**(delta_p - 1), algebraic_expand(psi**(delta_p - 2)), R)[0]
                beta = algebraic_expand(-f * psi**(delta - 1))
            U = V
            V = polynomial_divide_recursive(r, beta, L)[0]
            i += 1
        elif r == 0:
            U, V = V, r
    s = polynomial_divide_recursive(leading_coefficient(U, x), g, R)[0]
    W = polynomial_divide_recursive(U, s, L)[0]
    cont_W = polynomial_content(W, x, R)
    pp_W = polynomial_divide_recursive(W, cont_W, L)[0]
    return algebraic_expand(d * pp_W)

def _normalize(u, L):
    if len(L) == 0:
        return abs(u)

    if u == 0:
        return u
    
    c = polynomial_content(u, L[0], L[1::]).coefficient()
    return u / c

def polynomial_content(expr: Expression, main_var: Expression, vars: list[Expression] | Expression) -> Expression:
    """Determines the polynomial content of a polynomial u in x. This is 
    a generalization of the greatest common denominator of coefficients.

    See: https://en.wikipedia.org/wiki/Primitive_part_and_content

    Args:
        expr (Expression): The polynomial u(x)
        vars (Expression | list[Expression]): The generalized variable x

    Returns:
        Expression: The content part of the polynomial
    """
    content = Integer(0)
    if expr == 0:
        return content

    terms = expr.operands() if isinstance(expr, Sum) else [expr]
    for term in terms:
        content = polynomial_gcd(content, leading_coefficient(term, main_var), vars)
    return content

def factor_sqfree(u: Expression, x: Variable) -> list[Expression]:
    from .calculus_ops import derivative
    if u == 0:
        return u
    
    c = leading_coefficient(u, x)
    U = algebraic_expand(u / c)
    factors = []
    P = 1
    R = polynomial_gcd(U, derivative(U, x), [x])
    F = polynomial_divide(U, R, x)[0]
    j = 1
    while R != 1:
        G = polynomial_gcd(R, F, [x])
        s = polynomial_divide(F, G, x)[0]
        factors.append(s**j)
        P *= s**j
        R = polynomial_divide(R, G, x)[0]
        F = G
        j += 1
    factors.append(F ** j)
    P *= F**j
    return [c] + factors
    # return Product(c, P)
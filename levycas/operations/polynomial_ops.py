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

def polynomial_pseudo_divide(dividend: Expression, divisor: Expression, var: Expression) -> tuple[Expression]:
    """Given two general polynomial expressions with rational coefficients, performs monomial-based
    pseudo-division and returns the result [Quotient, Remainder]

    Psuedo-division is required as a variant of the euclidean division algorithm for which all remainders
    are polynomials with integer coefficients. 

    Psuedo-division and polynomial long-division are equivalent when the leading coefficient
    of the divisor is a unit. This means that they are equivalent for all univariate polynomials
    with rational coefficients.

    Args:
        dividend (Expression): A rational polynomial
        denominator (Expression): A rational polynomial
        var (Expression): A generalized variable

    Returns:
        list[Expression]: The list [Q, R] where Q is the quotient and R the remainder of the division.
    """
    p = 0
    s = dividend
    m = degree(s, var)
    n = degree(divisor, var)
    delta = max(m - n + 1, 0)
    lcv = coefficient(divisor, var, n)
    sigma = 0
    while n < m: 
        lcs = coefficient(s, var, m)
        p = lcv * p + lcs * var ** (m - n)
        s = algebraic_expand(lcv * s - lcs * divisor * var ** (m - n))
        sigma += 1
        m = degree(s, var)
    return (algebraic_expand(lcv ** (delta - sigma) * p), algebraic_expand(lcv**(delta -sigma) * s))

#TODO: Interpret the content() operator for univariate and multivariate polynomials.
#Requires first the implementation for univariate, which is relied on by the multivariate
#case. Algorithm should be recursive. 

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
    return _extended_euclidean(u, v, x)[0]

def _extended_euclidean(u: Expression, v: Expression, x: Expression) -> tuple[Expression]:
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

def polynomial_gcd(u: Expression, v: Expression, x: Expression | list[Expression]) -> Expression:
    """Computes the greatest common divisor of a multivariate polynomial. Recurses by treating the 
    given polynomials as univariate with respect to the first variable in the given ordering.

    Args:
        u (Expression): u(*x)
        v (Expression): v(*x)
        x (Expression | list[Expression]): The ordering of generalized variables 

    Returns:
        Expression: gcd(u(*x), v(*x))
    """
    x = x if isinstance(list) else [x]
    if len(x) == 1:
        assert _is_univariate(u, x) and _is_univariate(v, x), f"Polynomial gcd algorithm failed? Make sure all variables were passed in correctly."
        return _univariate_gcd(u, v, x)

def polynomial_content(expr: Expression, vars: list[Expression] | Expression) -> Expression:
    """Determines the polynomial content of a polynomial u in x. This is 
    a generalization of the greatest common denominator of coefficients.

    See: https://en.wikipedia.org/wiki/Primitive_part_and_content

    Args:
        expr (Expression): The polynomial u(x)
        vars (Expression | list[Expression]): The generalized variable x

    Returns:
        Expression: The content part of the polynomial
    """
    #All univariate non-zero polynomials in Q[x] have content 1
    if expr == 0:
        return Integer(0)

    vars = vars if isinstance(vars, list) else [vars]
    main_var = vars[0]
    num_vars = len(vars)
    terms = expr.operands() if isinstance(expr, Sum) else [expr]
    common_degrees = [None for var in vars]
    content = Integer(0)

    #Extract the common (minimum) degree for all variables except main_var,
    #and the common coefficient shared by all terms.
    for term in terms:
        content = gcd(content, term.coefficient())
        for i in range(num_vars):
            if vars[i] == main_var:
                common_degrees[i] = 0
            else:
                curr_degree = degree(term, vars[i])
                curr_common = common_degrees[i]
                if common_degrees[i] is None:
                    common_degrees[i] = curr_degree
                else:
                    common_degrees[i] = curr_common if curr_common < curr_degree else curr_degree

    for i in range(len(vars)):
        content *= vars[i] ** common_degrees[i]
    return content


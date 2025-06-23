"""Operations on generalized polynomial expressions, both single and multivariate cases"""
from ..expressions import *
from .expression_ops import contains

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
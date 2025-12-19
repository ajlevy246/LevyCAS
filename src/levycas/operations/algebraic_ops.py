"""Methods acting on an expression's AST. These operations are mathematical in nature.
"""

from ..expressions import *
from .expression_ops import construct, contains

def algebraic_expand(expr: Expression) -> Expression:
    """Given an expression, returns an equivalent expression in expanded form.
    For now, will only return a completely result for integer exponents. 

    Args:
        expr (Expression): The expression to expand

    Returns:
        Expression: The expanded expression
    """
    if not isinstance(expr, Expression):
        return expr

    elif isinstance(expr, Constant) or isinstance(expr, Variable):
        return expr

    operation = type(expr)
    operands = expr.operands()
    if operation == Sum:
        expanded_operands = [algebraic_expand(operand) for operand in operands]
        return sum(expanded_operands)

    elif operation == Product:
        first_factor = operands[0]
        remaining = expr / first_factor
        new_num = _expand_product(algebraic_expand(first_factor).num(), algebraic_expand(remaining).num())
        new_denom = _expand_product(algebraic_expand(first_factor).denom(), algebraic_expand(remaining).denom())

        return new_num / new_denom

    elif operation == Power:
        return _expand_power(algebraic_expand(operands[0]), algebraic_expand(operands[1]))
    
    expanded_operands = [algebraic_expand(operand) for operand in operands]
    return construct(expanded_operands, operation)

def algebraic_expand_main(expr: Expression) -> Expression:
    """Given an expression, returns an expanded expression that is expanded only with respect
    to the root operation of the AST.

    Args:
        expr (Expression): The expression to expand

    Returns:
        Expression: The expanded expression
    """
    if not isinstance(expr, Expression):
        return expr

    elif isinstance(expr, Constant) or isinstance(expr, Variable):
        return expr
    
    operation = type(expr)
    operands = expr.operands()
    if operation == Sum:
        return expr
    
    elif operation == Product:
        first_factor = operands[0]
        remaining = expr / first_factor
        return _expand_product(first_factor, remaining)
        new_num = _expand_product(first_factor.num(), remaining.num())
        new_denom = _expand_product(first_factor.denom(), remaining.denom()) 
        return new_num / new_denom
    
    elif operation == Power:
        return _expand_power(operands[0], operands[1])
    
    return expr

def _expand_product(r: Expression, s: Expression) -> Sum | Product:
    """Given a product (r * s), expanded the product recursively.
    If neither r nor s is a sum, then the product r * s is returned unchanged.

    Args:
        r (Expression): First factor
        s (Expression): Second factor

    Returns:
        Sum | Product: Expanded product
    """
    r_op = type(r)
    s_op = type(s)
    if r_op == Sum:
        f = r.operands()[0]
        return _expand_product(f, s) + _expand_product(r - f, s)
        
    elif s_op == Sum:
        return _expand_product(s, r)

    return r * s

def _expand_power(u: Expression, int_exp: Integer) -> Sum | Power:
    """Expanded a power of the form u ^ n, where n is an integer >= 2, using 
    the binomial theorem. 
    If the base is not a sum, then the product u ^ n is returned unchanged.

    Args:
        u (Expression): Base of the power
        int_exp (Integer): Integer exponent (n)

    Returns:
        Sum | Power: Expanded power
    """
    from math import comb
    if isinstance(int_exp, Integer):
        if int_exp.is_negative():
            return u ** int_exp
        elif int_exp == 0:
            return 1
        elif int_exp == 1:
            return u
        elif type(u) == Sum:
            n = int_exp.eval()
            f = u.operands()[0]
            r = u - f
            s = 0
            for k in range(0, n + 1):
                c = comb(n, k)
                s += _expand_product(c * f ** (n - k), _expand_power(r, Integer(k)))
            return s
    
    return u ** int_exp

def rationalize(expr: Expression) -> Expression:
    """Rationalizes an expression over a common denominator recursively.

    Args:
        expr (Expression): The expression to rationalize

    Returns:
        Expression: The rationalized expression
    """
    operation = type(expr)
    operands = expr.operands()

    if operation == Power:
        return rationalize(operands[0]) ** operands[1]
    elif operation == Product:
        first_factor = rationalize(operands[0])
        if len(operands) == 1:
            return first_factor
        else:
            remaining_factor = rationalize(Product(*operands[1::]))
            return first_factor * remaining_factor
    elif operation == Sum:
        first_term = rationalize(operands[0])
        if len(operands) == 1:
            return first_term
        else:
            remaining_term = rationalize(Sum(*operands[1::]))
            return _rationalize_sum(first_term, remaining_term)
    else:
        return expr

def _rationalize_sum(first_term: Expression, second_term: Expression) -> Expression:
    """Given two terms m/r + n/s, returns the simplified form of
    (ms + nr)/sr

    Args:
        first_term (Expression): _description_
        second_term (Expression): _description_

    Returns:
        Expression: _description_
    """
    m = first_term.num()
    r = first_term.denom()
    n = second_term.num()
    s = second_term.denom()
    if r == 1 and s == 1:
        return first_term + second_term
    else:
        return _rationalize_sum(m * s, n * r) / (r * s)

def linear_form(expr: Expression, wrt: Variable) -> list[Expression] | None:
    """Checks if the given expression is of the form
    a*x + b, where x is the given variable.

    Args:
        expr (Expression): The expression to check
        wrt (Variable): The variable x

    Returns:
        list[Expression] | None: The list [a, b], where a is the coefficient of x and b is the constant term,
        or None if the expression is not linear.
    """
    if expr == wrt:
        return [Integer(1), Integer(0)]

    operation = type(expr)
    if operation in [Integer, Rational, Variable]:
        return [Integer(0), expr]

    elif operation == Product:
        if not contains(expr, wrt):
            return [Integer(0), expr]
        
        elif not contains(expr / wrt, wrt):
            return [expr / wrt, Integer(0)]

        return None

    elif operation == Sum:
        linear = [Integer(0), Integer(0)]
        for term in expr.operands():
            term_form = linear_form(term, wrt)
            if term_form is None:
                return None
            
            linear[0] += term_form[0]
            linear[1] += term_form[1]
        return linear

    elif not contains(expr, wrt):
        return [Integer(0), expr]

    return None

def quadratic_form(expr: Expression, wrt: Variable) -> list[Expression] | None:
    """Checks if the given expression is of the form
    ax^2 + bx + c, where x is the given variable.

    Args:
        expr (Expression): The expression to check
        wrt (Variable): The variable x

    Returns:
        list[Expression] | None: The list [a, b, c] or None if the expression is not quadratic.
    """
    if expr == wrt:
        return [Integer(1), Integer(0), Integer(0)]

    operation = type(expr)
    if operation in [Integer, Rational, Variable]:
        return [Integer(0), Integer(0), expr]

    elif operation == Product:
        if not contains(expr, wrt):
            return [Integer(0), Integer(0), expr]

        elif lin_form := linear_form(expr / wrt, wrt):
            return [lin_form[0], lin_form[1], Integer(0)]

        return None
    
    elif operation == Sum:
        quadratic = [Integer(0), Integer(0), Integer(0)]
        for term in expr.operands():
            term_form = quadratic_form(term, wrt)
            if term_form is None:
                return None
            
            quadratic[0] += term_form[0]
            quadratic[1] += term_form[1]
            quadratic[2] += term_form[2]
        return quadratic

    elif operation == Power:
        exponent = expr.exponent()
        if contains(exponent, wrt):
            return None

        base = expr.base()
        if base == wrt:
            if exponent == 2:
                return [Integer(1), Integer(0), Integer(0)]
            elif exponent == 1:
                return [Integer(0), Integer(1), Integer(0)]
            
            return None
        
        if contains(base, wrt):
            return None
        
        return [Integer(0), Integer(0), expr]

    elif not contains(expr, wrt):
        return [Integer(0), Integer(0), expr]
    
    return None

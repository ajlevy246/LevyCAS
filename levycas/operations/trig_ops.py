"""Operations acting on an expresion's AST. These operations affect those AST's that have
trigonometric functions
"""

from ..expressions import *
from .expression_ops import construct
from .algebraic_ops import algebraic_expand_main, rationalize
from .simplification_ops import simplify

from math import comb

def trig_simplify(expr: Expression) -> Expression:
    """Given an expression, returns an expression in contracted-trigonometric form
    that is simplified.

    Args:
        expr (Expression): The expression to simplify

    Returns:
        Expression: The simplified expression
    """
    expr = rationalize(trig_substitute(expr))
    numerator = trig_expand(trig_contract(expr.num()))
    denominator = trig_contract(trig_expand(expr.denom()))
    if denominator == 0:
        return UNDEFINED
    else:
        return numerator / denominator

def trig_substitute(expr: Expression) -> Expression:
    """Given an expression, replaces all instances of trig functions with their equivalent
    expressions in sin and cos. Returns a new expression.

    Args:
        expr (Expression): The expression to trig-sub.

    Returns:
        Expression: An expression containing no trig functions other than sin/cos
    """
    if isinstance(expr, Constant) or isinstance(expr, Variable):
        return expr

    operation = type(expr)

    new_operands = [trig_substitute(operand) for operand in expr.operands()]
    new_expr = construct(new_operands, operation)
    # new_expr = operation(*new_operands)

    if operation == Tan:
        return Sin(*new_operands) / Cos(*new_operands)
    elif operation == Csc:
        return 1 / Sin(*new_operands)
    elif operation == Sec:
        return 1 / Cos(*new_operands)
    elif operation == Cot:
        return Cos(*new_operands) / Sin(*new_operands)
    else:
        return construct(new_operands, operation)
        # return operation(*new_operands)

def trig_expand(expr: Expression) -> Expression:
    """Given an expression, returns an equivalent expression in trigonometric-expanded form.

    Args:
        expr (Expression): The expression to expand

    Returns:
        Expression: An expression in trigonometric-expanded form.
    """
    operation = type(expr)
    if operation in [Integer, Rational, Variable]:
        return expr
    
    expanded_operands = [trig_expand(operand) for operand in expr.operands()]
    if operation == Sin:
        arg = expanded_operands[0]
        return _trig_expand_recursive(arg)[0]
    elif operation == Cos:
        arg = expanded_operands[0]
        return _trig_expand_recursive(arg)[1]
    else:
        return construct(expanded_operands, operation)
        # return operation(*expanded_operands)

def _trig_expand_recursive(expr: Expression) -> list[Expression]:
    """Given the argument x of a sin or cosine, returns a list [s, c]:
    s -> trigonometric-expanded form of sin(x)
    c -> trigonometric-expanded form of cos(x)

    Args:
        expr (Expression): x

    Returns:
        list[Expression]: s, c
    """
    operation = type(expr)
    operands = expr.operands()
    if operation == Sum:
        first_term = operands[0]
        remaining = expr - first_term
        sin_first_term, cos_first_term = _trig_expand_recursive(first_term)
        sin_remaining, cos_remaining = _trig_expand_recursive(remaining)
        sin_expanded = sin_first_term * cos_remaining + cos_first_term * sin_remaining
        cos_expanded = cos_first_term * cos_remaining - sin_first_term * sin_remaining
        return [sin_expanded, cos_expanded]
    elif operation == Product:
        first_factor = operands[0]
        if isinstance(first_factor, Integer):
            remaining = expr / first_factor
            return [_multiple_angle_sin(first_factor, remaining), _multiple_angle_cos(first_factor, remaining)]
        
    return [Sin(expr), Cos(expr)]
    
def _multiple_angle_sin(n: Integer, theta: Expression) -> Expression:
    """Given an expression Sin(n * theta), with argument that has an integer
    multiple (n) of angle (theta), returns the expanded form using the 
    multiple angle Sin identity.

    Args:
        n (Integer): Integer multiple
        theta (Expression): Angle

    Returns:
        Expression: Expanded form
    """
    expanded = 0
    if isinstance(theta, Sum):
        sin_theta, cos_theta = _trig_expand_recursive(theta)
    else:
        sin_theta, cos_theta = Sin(theta), Cos(theta)

    for j in range(0, n + 1, 2):
        expanded += (-1)**(j // 2) * comb(n, j) * cos_theta**(n - j) * sin_theta ** j
    return expanded

def _multiple_angle_cos(n: Integer, theta: Expression) -> Expression:
    """Given an expression Cos(n * theta), with argument that has an integer
    multiple (n) of angle (theta), returns the expanded form using the 
    multiple angle Cos identity.

    Args:
        n (Integer): Integer multiple
        theta (Expression): Angle

    Returns:
        Expression: Expanded form
    """
    expanded = 0
    if isinstance(theta, Sum):
        sin_theta, cos_theta = _trig_expand_recursive(theta)
    else:
        sin_theta, cos_theta = Sin(theta), Cos(theta)
    
    for j in range(1, n + 1, 2):
        expanded += (-1)**((j - 1) // 2) * comb(n, j) * Cos(theta) ** (n - j) * Sin(theta) ** j
    return expanded

def trig_contract(expr: Expression) -> Expression:
    """Given an expression, returns an equivalent expression in trigonometric-contracted form.

    Args:
        expr (Expression): The expression to contract

    Returns:
        Expression: The contracted expression
    """
    operation = type(expr)
    if operation in [Integer, Rational, Variable]:
        return expr

    contracted_operands = [trig_contract(operand) for operand in expr.operands()]
    # contracted_operation = operation(*contracted_operands)

    # if operation in [Product, Power]:
    #     return _trig_contract_recursive(contracted_operation)
    # else:
    #     return contracted_operation

    if operation == Product:
        prod = 1
        for operand in contracted_operands:
            prod *= operand
        return _trig_contract_recursive(prod)
    
    elif operation == Power:
        power = contracted_operands[0] ** contracted_operands[1]
        return _trig_contract_recursive(power)
    
    elif operation == Sum:
        return sum(contracted_operands)
    
    else:
        return construct(contracted_operands, operation)
        # return operation(*contracted_operands)
    
def _trig_contract_recursive(expr: Expression) -> Expression:
    """Given an algebraic expression, returns the algebraic expression in
    trigonometric contracted form.

    Args:
        expr (Expression): The expression to contract

    Returns:
        Expression: The contracted expression
    """
    expr = algebraic_expand_main(expr)
    operation = type(expr)

    if operation == Power:
        return _contract_trig_power(expr)
    
    elif operation == Product:
        trig_factors, non_trig_factors = _trig_separate(expr)
        trig_operation = type(trig_factors)
        if trig_factors == 1 or isinstance(trig_factors, Trig):
            return expr
        elif trig_operation == Power:
            return algebraic_expand_main(non_trig_factors * _contract_trig_power(trig_factors))
        else:
            return algebraic_expand_main(non_trig_factors * _contract_trig_product(trig_factors))

    elif operation == Sum:
        s = 0
        for operand in expr.operands():
            if type(operand) in [Product, Power]:
                s += _trig_contract_recursive(operand)
            else:
                s += operand
        return s
    
    else:
        return expr

def _contract_trig_power(expr: Power) -> Expression:
    """Given an expression u ^ v, where the base is a Trigonometric function and
    the exponent is a positive integer, then returns the trigonometric-contracted
    form using the power-reduction identities for Sin and Cos.

    See equations 
    
    Args:
        expr (Power): u ^ v

    Returns:
        Expression: the trigonometric-contracted expression
    """
    exponent = expr.exponent()
    base = expr.base()

    n = exponent.eval()
    theta = base.operands()[0]

    total = expr
    if n % 2 == 0:
        if type(base) == Cos:
            total = (1 / 2**exponent) * comb(n, n // 2)
            subtotal = 0
            for k in range(n // 2 - 1):
                subtotal += comb(n, k) * Cos((n - 2 * k) * theta)
            total += (2 / 2**exponent) * subtotal
            return total

        elif type(base) == Sin:
            total = (1 / 2**exponent) * comb(n, n // 2)
            subtotal = 0
            for k in range(n // 2 - 1):
                subtotal += (-1)**(n // 2 - k) * comb(n, k) * Cos((n - 2 * k) * theta)
            total += (2 / 2**exponent) * subtotal
            return total

    else:
        if type(base) == Cos:
            subtotal = 0
            for k in range((n - 1) // 2):
                subtotal += comb(n, k) * Cos((n - 2 * k) * theta)
            return (2 / 2 ** exponent) * subtotal

        elif type(base) == Sin:
            subtotal = 0
            for k in range((n - 1) // 2):
                subtotal += (-1) ** ((n - 1) // 2 - k) * comb(n, k) * Sin((n - 2 * k) * theta)
            return (2 / 2 ** exponent) * subtotal

    return expr

def _contract_trig_product(expr: Product) -> Expression:
    """Given a product of trigonometric functions, returns the trigonometric contracted form.

    Args:
        expr (Product): The product to contract.

    Returns:
        Expression: The contracted expression.
    """
    factors = expr.operands()
    num_factors = len(factors)
    
    if num_factors < 2:
        return expr
    
    elif num_factors > 2:
        first_factor = factors[0]
        remaining = _contract_trig_product(expr / first_factor)
        return _trig_contract_recursive(first_factor * remaining)
    
    theta = factors[0]
    phi = factors[1]
    
    first_op = type(theta)
    second_op = type(phi)

    if first_op == Power:
        return _trig_contract_recursive(_contract_trig_power(theta) * phi)
    elif second_op == Power:
        return _trig_contract_recursive(theta * _contract_trig_power(phi))
    
    elif first_op == Sin and second_op == Sin:
        return (Cos(theta - phi) / 2 - Cos(theta + phi) / 2)
    elif first_op == Cos and second_op == Cos:
        return (Cos(theta + phi) / 2 + Cos(theta - phi) / 2)
    elif first_op == Sin and second_op == Cos:
        return (Sin(theta + phi) / 2 + Sin(theta - phi) / 2)
    elif first_op == Cos and second_op == Sin:
        return (Sin(theta + phi) / 2 + Sin(phi - theta) / 2)
    else:
        return expr

def _trig_separate(expr: Expression) -> list[Expression]:
    """Given a simplified expression u, returns a list [v, w] where 
    v is the product of all factors of u that are trigonometric functions,
    and w is the product of the remaining factors of u.

    Args:
        expr (Expression): The expression u

    Returns:
        list[Expression]: The list [v, w]
    """
    if isinstance(expr.base(), Trig) and isinstance(expr.exponent(), Integer):
        return [expr, Integer(1)]
    
    elif type(expr) == Product:
        trig_factors = 1
        non_trig_factors = 1
        for factor in expr.operands():
            trig_factor, non_trig_factor = _trig_separate(factor)
            trig_factors *= trig_factor
            non_trig_factors *= non_trig_factor
        return [trig_factors, non_trig_factors]
    
    else:
        return [Integer(1), expr]

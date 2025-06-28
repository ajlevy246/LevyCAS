"""Methods acting on an expression's AST. 
These operations perform simplification procedures, as defined in Chapter 3 of Mathematical Methods.
"""

from ..expressions import *
from ..operations import construct

def simplify(expr: Expression) -> Expression:
    """Given an algebraic expression expr, performs simplification procedures as
    defined in Chapter 3 of Mathematical Methods, returning a new ASAE (Automatically
    Simplified Algebraic Expression) or the symbol UNDEFINED

    Args:
        expr (Expression): The expression to simplify

    Returns:
        Expression: The simplified expression
    """
    operation = type(expr)

    if isinstance(expr, (Constant, Variable)):
        return expr

    simplified_operands = [simplify(operand) for operand in expr.operands()]
    if UNDEFINED in simplified_operands:
        return UNDEFINED
    
    expr = construct(simplified_operands, operation)
    if operation == Power:
        return simplify_power(expr)
    elif operation == Product:
        return simplify_product(expr)
    elif operation == Sum:
        return simplify_sum(expr)
    elif operation == Div:
        return simplify_div(expr)
    elif operation == Factorial:
        return simplify_factorial(expr)
    else:
        return expr

def simplify_power(expr: Power) -> Expression:
    """Given a power v ^ w, returns a simplified expression or the 
    symbol UNDEFINED.

    Args:
        expr (Power): The power to simplify

    Returns:
        Expression: The simplified expression or UNDEFINED
    """
    v = expr.base()
    w = expr.exponent()

    if v == 0:
        if isinstance(w, Constant) and w.is_positive():
            return Integer(0)
        else:
            return UNDEFINED
        
    elif v == 1:
        return Integer(1)
    
    if isinstance(w, Constant):
        if isinstance(v, Constant):
            return expr
        elif w == 0:
            return Integer(1)
        elif w == 1:
            return v
        elif isinstance(v, Power):
            r = v.base()
            s = v.exponent()
            new_exponent = simplify_product(Product(s, w))
            new_power = Power(r, new_exponent)
            if isinstance(new_exponent, Integer):
                return simplify_power(new_power)
            return new_power
        elif isinstance(v, Product):
            new_factors = [simplify_power(factor ** w) for factor in v.operands()]
            new_product = Product(*new_factors)
            return simplify_product(new_product)

    return expr

def simplify_product(expr: Product) -> Expression:
    """Given a product, returns an equivalent simplified expression or the 
    symbol UNDEFINED

    Args:
        expr (Product): The product to simplify

    Returns:
        Expression: The simplified expression or UNDEFINED
    """
    factors = expr.operands()
    if 0 in factors:
        return Integer(0)

    elif len(factors) == 1:
        return factors[0]

    elif len(factors) == 2:
        if isinstance(factors[0], Constant):
            if isinstance(factors[1], Sum):
                return sum([factors[0] * term for term in factors[1].operands()])

        elif isinstance(factors[1], Constant):
            return simplify_product(Product(factors[1], factors[0]))

    flattened = flatten_factors(factors)
    num_flattened = len(flattened)
    if num_flattened == 0:
        return Integer(1)
    elif num_flattened == 1:
        return flattened[0]
    else:
        return Product(*flattened)

def simplify_sum(expr: Sum) -> Expression:
    """Given a sum, returns an equivalent simplified expression or the
    symbol UNDEFINED

    Args:
        expr (Sum): The sum to simplify

    Returns:
        Expression: The simplified sum
    """
    terms = expr.operands()
    if UNDEFINED in terms:
        return UNDEFINED
    
    if len(terms) == 1:
        return terms[0]
    
    flattened_terms = flatten_terms(terms)
    num_flattened = len(flattened_terms)
    if num_flattened == 0:
        return Integer(0)
    elif num_flattened == 1:
        return flattened_terms[0]
    else:
        return Sum(*flattened_terms)

def simplify_div(expr: Div) -> Expression:
    """Given a quotient u / v, returns the rational number u / v if both are constants, 
    or the simplified expression of u * v ^ (-1) otherwise.

    Args:
        expr (Div): The quotient to simplify

    Returns:
        Expression: The simplified expression.
    """
    numerator = expr.num()
    denominator = expr.denom()
    if isinstance(numerator, Constant) and isinstance(denominator, Constant):
        return numerator / denominator
    else:
        return simplify(numerator * denominator ** Integer(-1))

def simplify_factorial(expr: Factorial) -> Expression:
    operand = expr.operands()[0]
    if isinstance(operand, Integer):
        from math import factorial
        return Integer(factorial(int(operand)))
    return expr

def simplify_cos(expr: Cos) -> Expression:
    """Given an expression Cos(v), does basic 
    simplification based on the argument.
    
    Args:
        expr (Cos): The expression to simplify

    Returns:
        Expression: The simplified expression
    """
    pass

def simplify_sin(expr: Sin) -> Expression:
    """Given an expression Sin(v), does  basic
    simplification based on the argument.

    Args:
        expr (Sin): The expression to simplify

    Returns:
        Expression: The simplified expression
    """
    pass

def flatten_factors(factors: list[Expression]) -> list[Expression]:
    """Given a list of factors, combines those with like bases (e.g. [x, x] -> [x^2])
    and flattens nested products (e.g. [x, Product(x, y)] -> [x, x, y] -> [x^2, y]) recursively.
    Orders factors based on total ordering ("<" relation)

    Args:
        factors (list[Expression]): The list of factors to simplify

    Returns:
        list[Expression]: The simplified factors.
    """
    num_factors = len(factors)
    if num_factors < 2:
        return factors
    
    u_1 = factors[0]
    u_2 = factors[1]
    u_1_prod = isinstance(u_1, Product)
    u_2_prod = isinstance(u_2, Product)
    
    if num_factors == 2:
        if u_1_prod:
            if u_2_prod:
                return merge_factors(u_1.operands(), u_2.operands())
            else:
                return merge_factors(u_1.operands(), [u_2])
        else:
            if u_2_prod:
                return merge_factors([u_1], u_2.operands())

        if isinstance(u_1, Constant) and isinstance(u_2, Constant):
            coefficient = u_1 * u_2
            if coefficient == 1:
                return []
            else:
                return [coefficient]
            
        elif u_1 == 1:
            return [u_2]
        
        elif u_2 == 1:
            return [u_1]

        elif u_1.base() == u_2.base():
            new_exponent = simplify_sum(u_1.exponent() + u_2.exponent())
            new_power = simplify_power(u_1.base() ** new_exponent)
            if new_power == 1:
                return []
            else:
                return [new_power]
            
        else:
            if u_2 < u_1:
                return [u_2, u_1]
            else:
                return [u_1, u_2]
            
    elif num_factors > 2:
        remaining = flatten_factors(factors[1::])
        if u_1_prod:
            return merge_factors(u_1.operands(), remaining)
        else:
            return merge_factors([u_1], remaining)

def merge_factors(first_factors: list[Expression], second_factors: list[Expression]) -> list[Expression]:
    """Given two lists of factors, merges them into a single list of factors in sorted order. This applies
    for nested products.

    Args:
        first_factors (list[Expression]): The first set of factors
        second_factors (list[Expression]): The second set of factors

    Returns:
        list[Expression]: The merged list of factors
    """
    if len(second_factors) == 0:
        return first_factors
    
    elif len(first_factors) == 0:
        return second_factors
    
    else:
        p = first_factors[0]
        q = second_factors[0]
        rest_p = first_factors[1::]
        rest_q = second_factors[1::]

        h = flatten_factors([p, q])
        num_flattened = len(h)
        if num_flattened == 0:
            return merge_factors(rest_p, rest_q)
        elif num_flattened == 1:
            return h + merge_factors(rest_p, rest_q)
        else:
            if h == [p, q]:
                return [p] + merge_factors(rest_p, second_factors)
            else:
                assert h == [q, p]
                return [q] + merge_factors(first_factors, rest_q)

def flatten_terms(terms: list[Expression]) -> list[Expression]:
    """Given a list of terms, combines those with like factors (e.g. 2x + 3x = 5x)
    and flattens nested sums (e.g. [x, Sum(x, y)] -> [x, x, y] -> [2x, y]) recursively.
    Orders terms based on total ordering ("<" relation)

    Args:
        factors (list[Expression]): The list of terms to simplify

    Returns:
        list[Expression]: The simplified terms.
    """
    num_terms = len(terms)
    if num_terms < 2:
        return terms
    
    u_1 = terms[0]
    u_2 = terms[1]
    u_1_sum = isinstance(u_1, Sum)
    u_2_sum = isinstance(u_2, Sum)

    if num_terms == 2:
        if u_1_sum:
            if u_2_sum:
                return merge_terms(u_1.operands(), u_2.operands())
            else:
                return merge_terms(u_1.operands(), [u_2])
        else:
            if u_2_sum:
                return merge_terms([u_1], u_2.operands())
            
        if isinstance(u_1, Constant) and isinstance(u_2, Constant):
            coefficient = u_1 + u_2
            if coefficient == 0:
                return []
            else:
                return [coefficient]
            
        if u_1 == 0:
            return [u_2]
        
        if u_2 == 0:
            return [u_1]
        
        if u_1.term() == u_2.term():  
            new_coefficient = u_1.coefficient() + u_2.coefficient()
            new_product = new_coefficient * u_1.term()
            if new_product == 0:
                return []
            else:
                return [new_product]
            
        if u_2 < u_1:
            return [u_2, u_1]
        else:
            return [u_1, u_2]
        
    elif num_terms > 2:
        remaining = flatten_terms(terms[1::])
        if u_1_sum:
            return merge_terms(u_1.operands(), remaining)
        else:
            return merge_terms([u_1], remaining)

def merge_terms(first_terms: list[Expression], second_terms: list[Expression]) -> list[Expression]:
    """Given two lists of terms, merges them into a single list of terms in sorted order. This applies
    for nested sums.

    Args:
        first_terms (list[Expression]): The first set of terms
        second_terms (list[Expression]): The second set of terms

    Returns:
        list[Expression]: The merged list of terms
    """
    if len(second_terms) == 0:
        return first_terms
    
    elif len(first_terms) == 0:
        return second_terms
    
    else:
        p = first_terms[0]
        q = second_terms[0]
        rest_p = first_terms[1::]
        rest_q = second_terms[1::]

        h = flatten_terms([p, q])
        num_flattened = len(h)
        if num_flattened == 0:
            return merge_terms(rest_p, rest_q)
        elif num_flattened == 1:
            return h + merge_terms(rest_p, rest_q)
        else:
            if h == [p, q]:
                return [p] + merge_terms(rest_p, second_terms)
            else:
                assert h == [q, p], f"{h=}\n {p=}\n {q=}"
                return [q] + merge_terms(first_terms, rest_q)

def sym_eval(expr: Expression, **symbols: dict[Expression, Expression]) -> Expression:
    """Given a symbol table "symbols" and an expression "expr", evaluates the expression by replacing all symbols
    with their definitions in the table, and then simplifying. If the expression contains only constants or if
    all symbols have definitions in the table, sym_eval will return a constant.

    Args:
        expr (Expression): The expression to evaluate.
        symbols (dict[Expression, Expression]): The symbol table containing variable definitions.

    Returns:
        Expression: The original expression evaluated with respect to the symbol table.
    """
    if not isinstance(expr, Expression) or isinstance(expr, Constant):
        return expr

    if isinstance(expr, Variable):
        definition = symbols.get(expr, expr)
        if definition is expr:
            return expr
        else:
            return sym_eval(definition, **symbols)

    operation = type(expr)
    evaluated_operands = [sym_eval(operand, **symbols) for operand in expr.operands()]

    if operation == Sum:
        return simplify(sum(evaluated_operands))

    elif operation == Product:
        evaluated = 1
        for operand in evaluated_operands:
            evaluated *= operand
        return simplify(evaluated)

    elif operation == Div:
        return simplify(evaluated_operands[0] / evaluated_operands[1])

    elif operation == Power:
        return simplify(evaluated_operands[0] ** evaluated_operands[1])
    
    elif operation == Factorial:
        operand = evaluated_operands[0]
        if isinstance(operand, Integer):
            from math import factorial
            return Integer(factorial(int(operand)))
        return Factorial(operand)

    else:
        return simplify(construct(evaluated_operands, operation))

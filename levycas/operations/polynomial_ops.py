"""Operations on generalized polynomial expressions, both single and multivariate cases"""
from ..expressions import *
from .expression_ops import contains

def is_monomial(expr: Expression, vars: Variable | set[Variable]) -> bool:
    """_summary_

    Args:
        expr (Expression): The expression to check
        vars (Variable | set[Variable]): The parameters of the monomial expression.

    Returns:
        bool: True if the expression is a generalized polynomial expression in the given variables, False otherwise.
    """
    vars = {vars} if isinstance(vars, Variable) else vars

    if expr in vars:
        return True
    
    operation = type(expr)
    if operation == Power():
            base = expr.base()
            exponent = expr.exponent()
            if base in vars and isinstance(exponent, Integer) and Integer(1) < exponent:
                return True
            
    elif operation == Product():
            for factor in expr.operands():
                if not is_monomial(factor, vars):
                    return False
            return True
        
    return not contains(expr, vars)
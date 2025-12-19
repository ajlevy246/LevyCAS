"""LevyCAS is an implementation of a Computer Algebra System written
in pure Python. It requires only the built-in regex (re) and math modules.

Check out https://alexlevy.me for a LevyCAS demo!

- Alex Levy (2025)
"""

from .parser import (
    Token, tokenize,
    TOKEN_SPEC, TOKEN_CLASS, TOKEN_BP, parse, expand, pratt
)

from .expressions import (
    Constant, Integer, Rational, convert_primitive,
    UNDEFINED, CAS_ENV, Expression, Sum, Product, Div, Power, Factorial, Special,
    Trig, Sin, Cos, Tan, Csc, Sec, Cot, Arctan, Arccos, Arcsin,
    Variable, Function, Elementary,
    Exp, Ln
)

from .operations import (
    contains, copy, construct, map_op, substitute, symbols, get_symbols,
    algebraic_expand, algebraic_expand_main, rationalize, linear_form, quadratic_form,
    Deriv, derivative, integrate,
    simplify, sym_eval, simplify_factorial, simplify_div, simplify_power, simplify_product, simplify_sum,
    trig_simplify, trig_substitute, trig_contract, trig_expand,
    is_monomial, is_polynomial, variables, coefficient, degree, leading_coefficient, lex_lt, leading_monomial, monomial_divide, polynomial_divide, polynomial_pseudo_divide, polynomial_content, univariate_partial_fractions,
    polynomial_gcd, polynomial_divide_recursive,
    gcd, factor_integer, is_prime, radical, rational_simplify
)

__all__ = [
    # Lexing Module
    'Token', 'tokenize',
    'TOKEN_SPEC', 'TOKEN_CLASS', 'TOKEN_BP', 'parse', 'expand', 'pratt',

    # Core Expressions Module
    'Constant', 'Integer', 'Rational', 'convert_primitive',
    'UNDEFINED', 'CAS_ENV', 'Expression', 'Sum', 'Product', 'Div', 'Power', 'Factorial', 'Special',
    'trig_substitute', 'Trig', 'Sin', 'Cos', 'Tan', 'Csc', 'Sec', 'Cot', 'Arctan', 'Arccos', 'Arcsin',
    'Variable', 'Function', 'Elementary',
    'Exp', 'Ln',

    # Algebraic Manipulation Module
    'contains', 'copy', 'construct', 'map_op', 'substitute', 'symbols', 'get_symbols',
    'trig_simplify', 'trig_substitute', 'trig_expand', 'trig_contract',
    'is_monomial', 'is_polynomial', 'variables', 'coefficient', 'degree', 'leading_coefficient', 'lex_lt', 'leading_monomial',
    'monomial_divide', 'polynomial_divide', 'polynomial_pseudo_divide', 'polynomial_content', 'polynomial_gcd', 'polynomial_divide_recursive',
    'univariate_partial_fractions',
    'algebraic_expand', 'algebraic_expand_main', 'rationalize', 'linear_form', 'quadratic_form',

    # Symbolic Calculus Module
    'Deriv', 'derivative', 'integrate', 

    # Simplification (Core) Module
    'simplify', 'sym_eval', 'simplify_power', 'simplify_product', 'simplify_sum', 'simplify_div', 'simplify_factorial',

    # Numerical Methods
    'gcd', 'factor_integer', 'is_prime', 'radical', 'rational_simplify'
]
"""LevyCAS is an implementation of a Computer Algebra System written
in pure Python. It requires only the built-in regex (re) and math modules.

Install with the `tui` extra and run `levycas` for the interactive Textual user interface.
Or, check out https://alexlevy.me for an online LevyCAS demo, hosted with Gradio on Huggingface.

- Alex Levy (2025)
"""

from .parser import (
    Token, tokenize,
    TOKEN_SPEC, TOKEN_CLASS, TOKEN_BP, parse, expand, pratt
)

from .expressions import (
    Constant, Integer, Rational, convert_primitive,
    UNDEFINED, Expression, Sum, Product, Div, Power, Factorial,
    Trig, Sin, Cos, Tan, Csc, Sec, Cot, Arctan, Arccos, Arcsin,
    Variable, Elementary,
    Exp, Ln
)

from .operations import (
    contains, copy, construct, map_op, substitute, symbols, get_symbols,
    algebraic_expand, algebraic_expand_main, rationalize, linear_form, quadratic_form,
    Deriv, derivative, integrate, limit,
    simplify, sym_eval, simplify_factorial, simplify_div, simplify_power, simplify_product, simplify_sum,
    trig_simplify, trig_substitute, trig_contract, trig_expand,
    is_monomial, is_polynomial, variables, coefficient, degree, leading_coefficient, lex_lt, leading_monomial, 
    monomial_divide, polynomial_divide, polynomial_pseudo_divide, polynomial_content, partial_fractions,
    reduce_mod_p, polynomial_divide_mod_p, polynomial_gcd_mod_p,
    polynomial_gcd, polynomial_divide_recursive, rational_simplify, factor_sqfree, distinct_degree_factorization,
    gcd, factor_integer, is_prime, radical, mod_inverse, factor_mod_p, factor, collect_terms,
    exp_expand, log_expand, exp_contract, exp_simplify
)

__all__ = [
    # Lexing Module
    'Token', 'tokenize',
    'TOKEN_SPEC', 'TOKEN_CLASS', 'TOKEN_BP', 'parse', 'expand', 'pratt',

    # Core Expressions Module
    'Constant', 'Integer', 'Rational', 'convert_primitive',
    'UNDEFINED', 'Expression', 'Sum', 'Product', 'Div', 'Power', 'Factorial',
    'trig_substitute', 'Trig', 'Sin', 'Cos', 'Tan', 'Csc', 'Sec', 'Cot', 'Arctan', 'Arccos', 'Arcsin',
    'Variable', 'Elementary',
    'Exp', 'Ln',

    # Algebraic Manipulation Module
    'contains', 'copy', 'construct', 'map_op', 'substitute', 'symbols', 'get_symbols',
    'trig_simplify', 'trig_substitute', 'trig_expand', 'trig_contract',
    'is_monomial', 'is_polynomial', 'variables', 'coefficient', 'degree', 'leading_coefficient', 'lex_lt', 'leading_monomial',
    'monomial_divide', 'polynomial_divide', 'polynomial_pseudo_divide', 'polynomial_content', 'polynomial_gcd', 'polynomial_divide_recursive', 'polynomial_divide_mod_p', 'polynomial_gcd_mod_p',
    'partial_fractions', 'reduce_mod_p', 'distinct_degree_factorization', 'factor_mod_p', 'factor',
    'algebraic_expand', 'algebraic_expand_main', 'rationalize', 'linear_form', 'quadratic_form', 'collect_terms',
    'exp_expand', 'log_expand', "exp_contract", "exp_simplify",

    # Symbolic Calculus Module
    'Deriv', 'derivative', 'integrate', 'limit',

    # Simplification (Core) Module
    'simplify', 'sym_eval', 'simplify_power', 'simplify_product', 'simplify_sum', 'simplify_div', 'simplify_factorial',

    # Numerical Methods
    'gcd', 'factor_integer', 'is_prime', 'radical', 'rational_simplify', 'factor_sqfree', 'mod_inverse',
]
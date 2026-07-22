"""Routines acting on LevyCAS expression trees, including simplification and calculus routines."""

from .expression_ops import (
    symbols, get_symbols,
    contains, copy, map_op,
    construct, substitute
)

from .simplification_ops import (
    simplify, sym_eval,
    simplify_power, simplify_sum, 
    simplify_product, simplify_factorial,
    simplify_div,
)

from .algebraic_ops import (
    algebraic_expand, algebraic_expand_main,
    rationalize, linear_form, quadratic_form
)

from .calculus_ops import (
    Deriv,
    derivative, integrate, limit
)

from .exponential_ops import (
    exp_expand, exp_contract, exp_simplify,
    log_expand
)

from .factorization_ops import (
    factor_sqfree, factor_mod_p, factor,
)

from .numerical_ops import (
    gcd, mod_inverse, 
    small_primes, is_prime, 
    factor_integer, radical,
)

from .polynomial_ops import (
    is_monomial, is_polynomial, variables,
    coefficient, leading_coefficient, leading_monomial,
    polynomial_divide, polynomial_gcd, polynomial_content,
    rational_simplify, collect_terms,
    reduce_mod_p, polynomial_divide_mod_p, polynomial_gcd_mod_p,
    partial_fractions, degree, lex_lt
)

from .trig_ops import (
    trig_contract, trig_expand, trig_simplify,
    trig_substitute, 
)

__all__ = [
    # Expression operations
    "symbols", "get_symbols",
    "contains", "copy", "map_op",
    "construct", "substitute",

    # Simplification routines
    "simplify", "sym_eval",
    "simplify_power", "simplify_sum", 
    "simplify_product", "simplify_factorial",
    "simplify_div",

    # Algebraic operations
    "algebraic_expand", "algebraic_expand_main",
    "rationalize", "linear_form", "quadratic_form",

    # Calculus operations
    "Deriv",
    "derivative", "integrate", "limit",

    # Exponential operations
    "exp_expand", "exp_contract", "exp_simplify",
    "log_expand",

    # Factorization operations
    "factor_sqfree", "factor_mod_p", "factor",

    # Numerical operations
    "gcd", "mod_inverse", 
    "small_primes", "is_prime", 
    "factor_integer", "radical",

    # Polynomial operations
    "is_monomial", "is_polynomial", "variables",
    "coefficient", "leading_coefficient", "leading_monomial",
    "polynomial_divide", "polynomial_gcd", "polynomial_content",
    "rational_simplify", "collect_terms",
    "reduce_mod_p", "polynomial_divide_mod_p", "polynomial_gcd_mod_p",
    "partial_fractions", "degree", "lex_lt",

    # Trigonometric routines
    "trig_contract", "trig_expand", "trig_simplify",
    "trig_substitute",

    # Equation solving routines

]
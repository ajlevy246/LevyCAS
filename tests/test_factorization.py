"""Tests for polynomial factorization routines."""
import pytest

from levycas.expressions import *
from levycas.operations.factorization_ops import *

def test_distinct_degree_factorization():
    x = Variable("x")

    # Case 1: all factors same degree
    result = distinct_degree_factorization(x**4 + 1, x, 5)
    assert result == [(x**4 + 1, 2)]

    # Case 2: multiple linear factors, none higher degree
    result = distinct_degree_factorization(x**3 - x, x, 7)
    g, deg_found = result[0]
    assert deg_found == 1
    assert len(result) == 1  # everything grouped into one degree-1 bucket

    # Case 3: mixed degree roots
    f = reduce_mod_p(x * (x**2 + 1), x, 3)
    result = distinct_degree_factorization(f, x, 3)
    assert result == [(x, 1), (x**2 + 1, 2)]

def test_factor_mod_p():
    def check_factor_mod_p(f, x, p, expected_count=None, expected_degrees=None):
        """Verifies factor_mod_p(f) reconstructs f mod p, and optionally checks 
        the count and degree multiset of factors found."""
        factors = factor_mod_p(f, x, p)
        lc = int(leading_coefficient(reduce_mod_p(f, x, p), x))

        product = Integer(lc)
        for fac in factors:
            product = reduce_mod_p(algebraic_expand(product * fac), x, p)
        assert product == reduce_mod_p(f, x, p), f"Reconstruction failed: {product} != {f}"

        if expected_count is not None:
            assert len(factors) == expected_count, f"Expected {expected_count} factors, got {len(factors)}"
        if expected_degrees is not None:
            degrees = sorted(int(degree(fac, x)) for fac in factors)
            assert degrees == sorted(expected_degrees), f"Degree mismatch: {degrees} != {expected_degrees}"
        return factors

    x = Variable("x")

    # 1. Single-attempt split test, isolated
    for _ in range(30):
        check_factor_mod_p(x**4 + 1, x, 5, expected_count=2, expected_degrees=[2, 2])

    # 2. Three distinct linear factors w/ same degree
    for _ in range(30):
        check_factor_mod_p(x**3 - x, x, 7, expected_count=3, expected_degrees=[1, 1, 1])

    # 3. Mixed-degree case
    check_factor_mod_p(reduce_mod_p(x * (x**2 + 1), x, 3), x, 3, expected_count=2, expected_degrees=[1, 2])

    # 4. A case with four same-degree linear factors
    f = algebraic_expand(x * (x - 1) * (x - 2) * (x - 3))
    for _ in range(20):
        check_factor_mod_p(f, x, 5, expected_count=4, expected_degrees=[1, 1, 1, 1])

    # 5. Already-irreducible input
    check_factor_mod_p(x**2 + 1, x, 3, expected_count=1, expected_degrees=[2])

    # 6. Non-monic leading coefficient, to check factor_mod_p's normalization step
    check_factor_mod_p(2*(x**2 + 1), x, 3, expected_count=1, expected_degrees=[2])

def test_complete_factor():
    x = Variable('x')

    assert factor(7, x) == [7]
    assert factor(0, x) == [0]
    assert factor(-12*(x-3), x) == [-12, x-3]

    expr = x + 2
    factors = factor(expr, x)
    assert set(factors) == {1, expr}

    expr = x**2 + 1
    factors = factor(expr, x)
    assert set(factors) == {1, expr}

    expr = (x-2) * (x+3)
    factors = factor(expr, x)
    assert set(factors) == {1, x - 2, x + 3}

    expr = (x-3)**2
    factors = factor(expr, x)
    assert set(factors) == {1, (x-3)**2}

    expr = (x-1)**3 * (x+2)**2
    factors = factor(expr, x)
    assert set(factors) == {1, (x-1)**3, (x+2)**2}

    expr = (x**2+1) * (x-4)
    factors = factor(expr, x)
    assert set(factors) == {1, x**2+1, x-4}

    expr = (x**2+1) * (x**2+x+1)
    factors = factor(expr, x)
    assert set(factors) == {1, x**2 + 1, x**2 + x + 1} 

    expr = 6 * (x-1) * (x+2)
    factors = factor(expr, x)
    assert set(factors) == {6, x-1, x+2}

    expr = (
        (x-1) * (x+2) * (x-3) 
        * (x+4) * (x-5) * (x+6)
    )
    factors = factor(expr, x)
    assert set(factors) == {
        1, (x-1), (x+2), (x-3),
        (x+4), (x-5), (x+6)
    }
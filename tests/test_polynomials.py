"""Tests for the polynomial operators is_monomial, is_polynomial, coefficient, et cetera"""
import pytest

from levycas import *

def test_monomial():
    x, y = Variable('x'), Variable('y')
    a = Variable('a')

    assert is_monomial(a*x**2*y**2, {x, y})
    assert is_monomial(2 + a + 4 + 2*y**2, x)

    assert not is_monomial(x**2 + y**2, {x, y})
    assert not is_monomial(a**2 + x, {a})

def test_polynomial():
    x, y = Variable('x'), Variable('y')
    a = Variable('a')

    assert is_polynomial(x**2 + y**2, {x, y})
    assert is_polynomial(Sin(x)**2 + 2*Sin(x) + 3, Sin(x))
    
    assert not is_polynomial((x / y) + 2*y, {x, y})
    assert not is_polynomial((x + 1) * (x + 3), x)

def test_variables():
    x, y = Variable('x'), Variable('y')
    a, b, c = Variable('a'), Variable('b'), Variable('c')

    assert variables(x**3 + 3*x**2*y+3*x*y**2 + y**3) == {x, y}
    assert variables(a*Sin(x)**2 + 2*b*Sin(x) + 3*c) == {a, b, c, Sin(x)}
    assert variables(1) == set()

def test_coefficient():
    x, y = Variable('x'), Variable('y')
    a, b, c = Variable('a'), Variable('b'), Variable('c')

    assert (
        coefficient(a*x**2 + b*x + c, x, 2)
        == a
    )

    assert (
        coefficient(3*x*y**2 + 5*x**2*y + 7*x + 9, x, 1)
        == 3*y**2 + 7
    )

    assert (
        coefficient(3*x*y**2 + 5*x**2*y + 7*x + 9, x, 3)
        == 0
    ) 

    assert (
        coefficient(3*Sin(x)*x**2 + 2*Ln(x)*x + 4, x, 2)
        is None
    )

def test_leading_coefficient():
    x, y = Variable('x'), Variable('y')
    a, b, c = Variable('a'), Variable('b'), Variable('c')

    assert (
        leading_coefficient(a*x + b*x + y, x)
        == (a + b)
    )

    assert (
        leading_coefficient(3*Sin(x) + a*Sin(x)**2*b + 2*y*x, Sin(x))
        == a*b
    )

    assert (
        leading_coefficient(3*x*Cos(y)**3 + Cos(y)**2 + y*Cos(y) + 4*a*b*Cos(y)**3, Cos(y))
        == 3*x + 4*a*b
    )

def test_degree():
    x, y = Variable('x'), Variable('y')
    a, b, c = Variable('a'), Variable('b'), Variable('c')

    assert (
        degree(3*x**2 + 4*x + 4, x)
        == 2
    )

    assert (
        degree(3*x**3*y + x**3 + y, {x, y})
        == 4
    )

    assert (
        degree(3*a*x**2*y**3*b**4, {x, b})
        == 6
    )

    assert (
        degree(a*Sin(x)**2 +  b*Sin(x) + c, Sin(x))
        == 2
    )

    assert (
        degree(2*x**2*y*a**3 + y*x*a**6, {a, x, y})
        == 8
    )

def test_lex_ordering():
    x, y, z = Variable('x'), Variable('y'), Variable('z')
    a, b, c = Variable('a'), Variable('b'), Variable('c')

    alphabetical = [a, b, c, x, y, z]
    reverse_alphabetical = alphabetical[::-1]

    assert lex_lt(x**2 * y**3 * z**4, x**2 * y**4 * z**3, alphabetical)
    assert not lex_lt(x**2 * y**3 * z**4, x**2 * y**4 * z**3, reverse_alphabetical)

    assert not lex_lt(x**2 * y**4 * z**3, x**2 * y**3 * z**4, alphabetical)
    assert lex_lt(x**2 * y**4 * z**3, x**2 * y**3 * z**4, reverse_alphabetical)
    
    assert lex_lt(x * y**2 * z, x**2 * y, alphabetical)
    assert not lex_lt(x * y**2 * z, x**2 * y, reverse_alphabetical)

    assert not lex_lt(x**2 * y, x * y**2 * z, alphabetical)
    assert lex_lt(x**2 * y, x * y**2 * z, reverse_alphabetical)

    assert lex_lt(y*z**5, x, alphabetical)
    assert not lex_lt(y*z**5, x, reverse_alphabetical)

    assert not lex_lt(x, y*z**5, alphabetical)
    assert lex_lt(x, y*z**5, reverse_alphabetical)

    assert not lex_lt(2*x*y, 3*x*y, alphabetical)
    assert not lex_lt(2*x*y, 3*x*y, reverse_alphabetical)

    assert not lex_lt(3*x*y, 2*x*y, alphabetical)
    assert not lex_lt(3*x*y, 2*x*y, reverse_alphabetical)

def test_leading_monomial():
    x, y = Variable('x'), Variable('y')
    lm = lambda y: leading_monomial(y, [x, y])
    less = lambda x, y: lex_lt(x, y, [x, y])

    expr = 3*x**2*y + 4*x*y**2 + y**3 + x + 1
    assert leading_monomial(expr, [x, y]) == 3*x**2*y
    assert leading_monomial(expr, [y, x]) == y**3

    u = 3*x**2*y**3 + 5*x*y**2 + 2*x*y + 4*x + 2*y + 1
    v = 2*x**3*y**2 + 3*x**2*y + x*y + 3*x + 4*y + 1
    uv = algebraic_expand(u*v)

    w = 4*x*y+ 2*x + 3*y + 4
    uw = algebraic_expand(u*w)
    vw = algebraic_expand(v*w)

    assert (
        lm(uv)
        == algebraic_expand(lm(u) * lm(v))
    )

    #lm(u) < lm(v) => lm(uw) < lm(vw), where w \neq 0
    assert (
        not less(lm(uw), lm(vw)) or less(lm(u), lm(v))
    )

def test_polynomial_division():
    x, y = Variable('x'), Variable('y')
    ordering = [x, y]

    dividend = 2*x**2*y + 3*x**2 + 4*x*y + 5*x + 6*y + 7
    divisor = x*y

    divide = lambda x, y: polynomial_divide(x, y, ordering)

    quot, rem = divide(dividend, divisor)
    assert (
        [quot, rem]
        == [(2*x + 4), (3*x**2 + 5*x + 6*y + 7)]
        and dividend == algebraic_expand(quot * divisor + rem)
    )
    assert (
        divide(x**3 + 2*x**2 + x, x + 1)
        == (x**2 + x, 0)
    ) 
    assert (
        divide(x**2 + 2, x + 1)
        == (x - 1, 3)
    )
    assert (
        divide(x*y + y**2, y)
        == (x+y, 0)
        and
        divide(x*y + y**2, x)
        == (y, y**2)
    )
    assert (
        divide(x**2 + x*y + 1, x + y)
        == (x, 1)
        and
        divide(x**2 + x*y + 1, y)
        == (x, x**2 + 1)
    )
    assert (
        divide(x**2*y + x*y**2 + y**3, x*y + y**2)
        == (x, y**3)
    )

def test_polynomial_gcd():
    x, y, z = Variable('x'), Variable('y'), Variable('z')
    pass
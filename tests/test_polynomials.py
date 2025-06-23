"""Tests for the polynomial operators monomial, polynomial, et cetera"""
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
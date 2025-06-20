"""Tests for the total ordering of expressions"""

import pytest
from levycas.expressions import *

def test_constant_ordering():
    assert Integer(2) < Rational(5, 2)
    assert not Rational(5, 2) < Integer(2)

    assert Integer(-1) < Integer(1)
    assert not Integer(1) < Integer(-1)

def test_symbol_ordering():
    assert (
        Variable('0')
        < Variable('1')
        < Variable('9')
        < Variable('A')
        < Variable('Z')
        < Variable('a')
        < Variable('z')
    )

    assert not Variable('z') < Variable('a')
    assert not Variable('a') < Variable('Z')
    assert not Variable('A') < Variable('9')

def test_sum_and_product_ordering():
    a, b, c, d = Variable('a'), Variable('b'), Variable('c'), Variable('d')

    assert Sum(a, b) < Sum(a, c)
    assert not Sum(a, c) < Sum(a, b)

    assert Sum(a, c, d) < Sum(b, c, d)
    assert not Sum(b, c, d) < Sum(a, c, d)

def test_elementary_orderings():
    x, y, z = Variable("x"), Variable("y"), Variable("z")

    assert Cos(x) < Sin(x)
    assert not Sin(x) < Cos(x)

    assert Cos(x) < Tan(x)
    assert not Tan(x) < Cos(x)

    assert Exp(x) < Tan(x)
    assert not Tan(x) < Exp(x)

    assert Exp(x) < Ln(x)
    assert not Ln(x) < Exp(x)

    assert Ln(x) < Factorial(x)
    assert not Factorial(x) < Ln(x)

    assert Sin(x) < Sin(y)
    assert not Sin(y) < Sin(x)

    assert Cos(x) < Cos(y)
    assert not Cos(y) < Cos(x)

    assert Exp(x) < Exp(y)
    assert not Exp(y) < Exp(x)

    assert Sin(x + y) < Sin(x + z)
    assert not Sin(x + z) < Sin(x + y)

    assert Exp(x * y) < Exp(x * z)
    assert not Exp(x * z) < Exp(x * y)

    assert Power(Cos(x), Integer(2)) < Power(Sin(x), Integer(2))
    assert not Power(Sin(x), Integer(2)) < Power(Cos(x), Integer(2))

    assert Power(Exp(x), Integer(2)) < Power(Exp(x), Integer(3))
    assert not Power(Exp(x), Integer(3)) < Power(Exp(x), Integer(2))

    assert Factorial(x) < Factorial(y)
    assert not Factorial(y) < Factorial(x)

    assert Sum(Sin(x), Integer(1)) < Sin(x)
    assert not Sin(x) < Sum(Sin(x), Integer(1))
import pytest
from levycas.expressions import *

class TestOrdering:
    """Tests for the total ordering of expressions"""
    def test_constant_ordering(self):
        assert Integer(2) < Rational(5, 2)
        assert not Rational(5, 2) < Integer(2)

        assert Integer(-1) < Integer(1)
        assert not Integer(1) < Integer(-1)

    def test_symbol_ordering(self):
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

    def test_sum_and_product_ordering(self):
        a, b, c, d = Variable('a'), Variable('b'), Variable('c'), Variable('d')

        assert Sum(a, b) < Sum(a, c)
        assert not Sum(a, c) < Sum(a, b)

        assert Sum(a, c, d) < Sum(b, c, d)
        assert not Sum(b, c, d) < Sum(a, c, d)

        assert Sum(c, d) < Sum(b, c, d)
        assert not Sum(b, c, d) < Sum(c, d)

        assert Product(a, b) < Product(a, c)
        assert not Product(a, c) < Product(a, b)

        assert Product(a, c, d) < Product(b, c, d)
        assert not Product(b, c, d) < Product(a, c, d)

        assert Product(c, d) < Product(b, c, d)
        assert not Product(b, c, d) < Product(c, d)
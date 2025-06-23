import pytest
from levycas import *

#TODO: Add the distribution of constants over sums in the simplification procedure?

class TestSimplification:
    """Tests for automatic simplification of expressions"""
    def test_sum(self):
        x, y, z = Variable('x'), Variable('y'), Variable('z')

        assert (
            1 + x + y + z
            == x + 1 + z + y
            == z + y + 1 + x
            == x + 2 + y - 1 + z
        )

        assert (
            2*(x + 1) + 3*(x + 1)
            == 5*(x + 1)
            == 5*x + 5
        )

        assert (
            (1 + x) + (y + z)
            == z + (y + x) + 1
            == (1 + x + y + z)
        )

        assert (
            5*x**2 + 4*x + 1 - 4*x - 5*x**2 - 1
            == 5*x**2 + 4*x + 1 - (4*x + 5*x**2 + 1)
            == 0
        )

    def test_product(self):
        x, y, z = Variable('x'), Variable('y'), Variable('z')

        assert (
            x * y * z * x * y * z
            == (x*y*z)**2
            == x**2 * y**2 * z**2
        )

        assert (
            2*x*y*z * 3*x*y*z
            == 6*(x*y*z)**2
            == 6*x**2 * y**2 * z**2
        )

        assert (
            2*x - (2*x + 1) 
            == -1
        )

        assert (
            (x + y + z) - (x + y + z)
            == (z + y + x) - (y + x + z)
            == (x + y + z) - (x + y + z)
            == 0
        )

    def test_basics(self):
        x, y, z = Variable('x'), Variable('y'), Variable('z')
        a, b, c = Variable('a'), Variable('b'), Variable('c')
        
        assert x / x == 1
        assert (x / y)*(y / x) == 1
        assert 0 / x == 0
        assert x / 1 == x
        assert x - 0 == x
        assert 0 - x == -x

        assert (
            Sin(x) + 2*Sin(x) == 3*Sin(x)
        )

        assert (
            x + (x + y)  == 2*x + y
        )

        assert (
            2*(x*y*z) + 3*x*(y*z) + 4*(x*y)*z == 9*x*y*z
        )

        assert (
            x*y**3 / y == x*y**2
        )

        assert (
            ((x**(1 / 2)) ** (1 / 2)) ** 8 == x**2
        )

        assert (
            ((x*y)**(1 / 2)*z**2)**2 == x*y*z**4
        )

        assert (
            (2*a*b*c) * (3*c*b*a) == 6 * a**2 * b**2 * c**2
        )

        assert (
            (2*a*b*c) + (3*c*b*a) == 5*a*b*c
        )

        assert (
            (x*y*z) * (x*y**-1*z*a) == a * x**2 * z**2
        )
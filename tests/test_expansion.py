import pytest
from levycas import Variable, algebraic_expand, algebraic_expand_main, rationalize

class TestExpansion:
    """Tests for the algebraic_expand() and algebraic_expand_main() operators."""

    def test_expansion_binomial(self):
        """Binomial expansion tests"""
        x,y  = Variable('x'), Variable('y')

        assert (
            algebraic_expand((x + 2) ** 2)
            == (x**2) + (4*x) + (4)
        )

        assert (
            algebraic_expand((x - y) ** 3)
            == (x**3) - (y**3) - 3*(x**2 * y) + 3*(x * y**2)
        )

        assert (
            algebraic_expand((1 - x) * (1 + x))
            == 1 - (x**2)
        )

        assert (
            algebraic_expand(((2*x) + (3*y))**2)
            == 4*(x)**2 + (12*x*y) + 9*(y)**2
        )

    def test_expansion_polynomial(self):
        """Univariate polynomial expansion tests"""
        x = Variable('x')

        assert (
            algebraic_expand((x + 1) * ((x**2) + (2*x) + (2))) 
            == (x**3) + 3*(x)**2 + (4*x) + (2)
        )

        assert (
            algebraic_expand((x + 1) * (x + 2) * (x + 3))
            == algebraic_expand(x * (x + 2) * (x + 3) + (x + 2) * (x + 3))
            == (x**3) + 6*(x)**2 + (11*x) + 6
        )

        assert (
            algebraic_expand((2*x**3 -2*x**2 + 4*x -10) * (4*x**5 + 3*x**4 -2*x**3 + 3*x**2 - 27*x + 45)) 
            == 8*x**8 - 2*x**7 + 6*x**6 - 18*x**5 - 98*x**4 + 176*x**3 - 228*x**2 + 450*x - 450
        )

    def test_expansion_rational(self):
        """Rational expansion tests for the algebraic_expand operator"""
        x, y = Variable('x'), Variable('y')
        
        assert (
            algebraic_expand((1 - x**2) / ((1 - x)*(1 + x)))
            == 1
        )

    def test_expansion_main(self):
        """Tests for algebraic expansion with respect to the main operation of an AST"""
        x = Variable('x')

        assert (
            algebraic_expand_main(x * (2 + (1 + x)**2)) 
            == (2*x) + x*(1 + x)**2
        )

        assert (
            algebraic_expand_main((x + (1 + x)**2)**2)
            == (x**2) + 2*x*(1 + x)**2 + (1 + x)**4
        )

class TestRationalization:
    """Tests for the rationalize() method"""
    pass

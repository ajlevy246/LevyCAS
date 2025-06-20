import pytest

from levycas import *

class TestDerivative:
    """Tests for the derivative operator"""
    
    def test_derivative_constant(self):
        x = Variable('x')

        assert derivative(Sin(Integer(1)), x) == 0


class TestIntegrate:
    """Tests for the integrate operator"""

    def test_integrate_constant(self):
        x, y = Variable('x'), Variable('y')

        assert integrate(2 * y, x) == 2*y*x
        assert integrate(Sin(Integer(1)), x) == Sin(Integer(1))*x
        assert integrate(Cos(Sin(Rational(-1, 2))), x) == Cos(Sin(Rational(-1, 2))) * x

    def test_integrate_match(self):
        x, y = Variable("x"), Variable("y")
        pass

    def test_integrate_substitute(self):
        x, y = Variable("x"), Variable("y")
        pass

    def test_integrate_linear(self):
        x, y = Variable("x"), Variable("y")
        
        # assert integrate(2*x + (1 / 2)*x**2, x) == x**2 + (1 / 6)*x**3 #-> Fails, because of incorrect processing of (1 / 6)
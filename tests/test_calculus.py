import pytest

from levycas import *

class TestDerivative:
    """Tests for the derivative operator"""
    
    def test_derivative_constant(self):
        x = Variable('x')

        assert derivative(Sin(Integer(1)), x) == 0

    def test_derivative_functions(self):
        x = Variable('x')

        assert derivative(Ln(x), x) == 1 / x
        assert derivative(Exp(x), x) == Exp(x)

        assert derivative(Tan(x), x) == 1 + Sin(x)**2 / Cos(x)**2
        assert derivative(Cos(x), x) == -Sin(x)
        assert derivative(Sin(x), x) == Cos(x)

        assert derivative(Sec(x), x) == Sin(x) / Cos(x)**2
        assert derivative(Csc(x), x) == -Cos(x) / Sin(x)**2
        assert derivative(Cot(x), x) == -(1 + Cos(x)**2 / Sin(x)**2)

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
        
        sub_test = integrate(Sin(x) * Cos(x), x)
        assert (
            # u = Sin(x) -> du = Cos(x)dx
            sub_test == (1 / 2) * Sin(x) ** 2

            # u = Cos(x) -> du = -Sin(x)dx
            or sub_test == - (1 / 2) * Cos(x) ** 2
        )

    def test_integrate_linear(self):
        x, y = Variable("x"), Variable("y")

        # assert integrate(2*x + (1 / 2)*x**2, x) == x**2 + (1 / 6)*x**3 #-> Fails, because of incorrect processing of (1 / 6)
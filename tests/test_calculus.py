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

        assert derivative(Tan(x), x) == Sec(x)**2
        assert derivative(Cos(x), x) == -Sin(x)
        assert derivative(Sin(x), x) == Cos(x)

        assert derivative(Sec(x), x) == Sec(x) * Tan(x)
        assert derivative(Csc(x), x) == -Cot(x) * Csc(x)
        assert derivative(Cot(x), x) == -Csc(x)**2

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
        
        #Elementary function substitution
        assert (
            integrate(Sin(x) * Cos(x), x)
            == - (1 / 2) * Cos(x) ** 2
        )
        assert (
            integrate(Cos(3*x), x)
            == Rational(1, 3) * Sin(3*x)
        )
        assert (
            integrate(Sin(x**2) * 2*x, x)
            == -Cos(x**2)
        )
        assert (
            integrate(Exp(2*x), x) 
            == (1 / 2) * Exp(2*x)
        )
        assert (
            integrate(Ln(x)**3 * (1 / x), x)
            == (1 / 4) * Ln(x)**4
        )

        #Algebraic substitution
        assert (
            integrate((3*x + 1)**4, x)
            == Rational(1, 15) * (3*x + 1)**5
        )
        assert (
            integrate((5*x + 2)**(1 / 2), x)
            == Rational(2, 15) * (5*x + 2) ** (3 / 2)
        )
        assert (
            integrate(1 / (x*Ln(x)), x)
            == Ln(Ln(x))
        )

        #Rational expressions
        assert (
            integrate((2*x) / (x**2 + 1), x)
            == Ln(x**2 + 1)
        )

        assert (
            integrate(x / (x**2 + 1)**2, x)
            == -(1 / 2) / (1 + x**2)
        )

        #Trig substitution
        assert (
            integrate(Cos(x)**2 * Sin(x), x)
            == -Rational(1, 3) * Cos(x)**3
        )

        assert (
            integrate(Sec(x)**2 * Tan(x), x)
            == Sec(x)**2 / 2
        )

    def test_integrate_linear(self):
        x, y = Variable("x"), Variable("y")

        assert integrate(2*x + (1 / 2)*x**2, x) == x**2 + Rational(1, 6)*x**3

    def test_integration_byparts(self):
        x, y = Variable('x'), Variable('y')

        #Exponential tests
        assert (
            integrate(x*Exp(x), x)
            == x*Exp(x) - Exp(x)
        )
        assert (
            integrate(x**2 * Exp(x), x)
            == x**2 * Exp(x) - 2*x*Exp(x) + 2*Exp(x)
        )
        assert (
            integrate(x * Exp(2*x), x)
            == Rational(1, 2) * x * Exp(2*x) - Rational(1, 4) * Exp(2*x)
        )
        assert (
            integrate(x * Exp(x + 1), x)
            == x * Exp(x + 1) - Exp(x + 1)
        )
        assert (
            integrate(x**2 * Exp(2*x + 1), x)
            == (1/2)*x**2*Exp(2*x+1) - (1/2)*x*Exp(2*x+1) + (1/4)*Exp(2*x+1)
        )

        #Sin tests
        assert (
            integrate(x*Sin(x), x)
            == Sin(x) - x*Cos(x)
        )
        assert (
            integrate(x**2 * Sin(x), x)
            == 2*Cos(x) + 2*x*Sin(x) - x**2*Cos(x)
        )
        assert (
            integrate(x * Sin(2*x), x)
            == (1/4)*Sin(2*x) - (1/2)*x*Cos(2*x)
        )
        assert (
            integrate(x * Sin(x + 1), x)
            == Sin(x+1) - x*Cos(x + 1)
        )
        assert (
            integrate(x**2 * Sin(2*x + 1), x)
            == (1/4)*Cos(2*x+1) + (1/2)*x*Sin(2*x+1) - (1/2)*x**2*Cos(2*x+1)
        )

        #Cos tests
        assert (
            integrate(x*Cos(x), x)
            == x*Sin(x) + Cos(x)
        )
        assert (
            integrate(x**2 * Cos(x), x)
            == x**2*Sin(x) + 2*x*Cos(x) - 2*Sin(x)
        )
        assert (
            integrate(x * Cos(2*x), x)
            == (1/2)*x*Sin(2*x) + (1/4)*Cos(2*x)
        )
        assert (
            integrate(x * Cos(x + 1), x)
            == x*Sin(x+1) + Cos(x + 1)
        )
        assert (
            integrate(x**2 * Cos(2*x + 1), x)
            == (1/2)*x**2*Sin(2*x+1) + (1/2)*x*Cos(2*x+1) - (1/4)*Sin(2*x+1)
        )

    def test_integrate_miscellaneous(self):
        x, y = Variable('x'), Variable('y')

        assert (
            integrate(Cos(x) / (Sin(x)**2 + 3*Sin(x) + 4), x)
            == 2 * (Arctan((3 + 2 * Sin(x)) / 7 ** Rational(1, 2)) / 7**Rational(1, 2))
        )
        assert (
            integrate(Sin(2*x)**3 * Cos(2*x)**4, x)
            == trig_simplify(Cos(2*x)**5 * (5*Cos(4*x) - 9) / 140)
        )
        assert (
            integrate(x*Exp(x), x)
            == x * Exp(x) - Exp(x)
        )

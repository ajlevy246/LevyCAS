"""Tests for the algebraic operations rationalize() and linear_form() and quadratic_form()"""
import pytest

from levycas import *

class TestLinearForm:
    """Tests for the linear_form() operator"""

    def test_linear_fail(self):
        x, y = Variable('x'), Variable('y')
        
        assert (
            None
            is linear_form(Sin(x), x)
            is linear_form(x * x, x)
            is linear_form(y + y*x + y*x**2, x)
            is linear_form(x * Cos(x) + x * Sin(y), x)
        )

    def test_linear_simple(self):
        x, y = Variable('x'), Variable('y')

        assert (
            linear_form(1 - Sin(y) + Cos(y) * x, x)
            == [Cos(y), 1 - Sin(y)]
        )

        assert (
            linear_form(5 * x / 4 + y - 5, x)
            == [(5 / 4), (y - 5)]
        )

class TestQuadraticForm:
    """Tests for the quadratic_form() operator"""

    def test_quadratic_fail(self):
        x, y = Variable('x'), Variable('y')

        assert (
            None
            is quadratic_form(Sin(x), x)
            is quadratic_form(x * x * x, x)
            is quadratic_form(y + y*x + y*x**3, x)
            is quadratic_form(x * Cos(x) + x * Sin(y), x)
            is quadratic_form(x ** 3, x)
            is quadratic_form(x * x * x * y + x**2 * y, x)
        )

    def test_quadratic_simnple(self):
        x, y = Variable('x'), Variable('y')

        assert (
            quadratic_form(x**2 + 2*x + 3, x)
            == [1, 2, 3]
        )

        assert (
            quadratic_form(y**3*x**2 + 2*y**2 + y*x + 2*x**2 + 2*x + 3, x)
            == [2 + y**3, y + 2, 2*y**2 + 3]
        )
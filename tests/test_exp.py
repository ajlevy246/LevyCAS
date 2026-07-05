"""Tests for the exponential family of functions (Exp, Ln)"""
import pytest

from levycas.expressions.exp import Ln, Exp
from levycas.expressions.expression import UNDEFINED
from levycas.operations.expression_ops import symbols

def test_exp_asimplify():
    """Tests for the automatic simplification when instantiating."""
    x, y = symbols("x y")
    with pytest.raises(ValueError):
        Ln(0)
    assert Ln(1) == 0
    assert Ln(1/x) == -Ln(x)
    assert Ln(x**2 * y**3) == 2*Ln(x) + 3*Ln(y)
    assert Ln(1/x**2) == -2*Ln(x)
    assert Ln(x*y) == Ln(x) + Ln(y)
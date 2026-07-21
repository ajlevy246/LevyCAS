"""Tests for the exponential family of functions (Exp, Ln)"""
import pytest

from levycas.expressions.exp import Ln, Exp
from levycas.expressions.expression import UNDEFINED
from levycas.operations.expression_ops import symbols
from levycas.operations.exponential_ops import (
    exp_contract, exp_expand, exp_simplify,
    log_expand,
)

x, y, w, z = symbols("x y w z")

def test_ln_asimplify():
    """Tests for the automatic simplification of Ln when instantiating."""
    with pytest.raises(ValueError):
        Ln(0)
    assert Ln(1) == 0
    assert Ln(1/x) == -Ln(x)
    assert Ln(x**2 * y**3) == 2*Ln(x) + 3*Ln(y)
    assert Ln(1/x**2) == -2*Ln(x)
    assert Ln(x*y) == Ln(x) + Ln(y)

def test_exp_asimplify():
    """Tests for the automatic simplification of Exp when instantiating."""
    assert Exp(0) == 1

def test_exp_expand():
    """Tests for the exp_expand() operator."""
    assert (
        exp_expand(Exp(2*w*x + 3*y*z))
        == exp_expand(Exp(2*w*x)*Exp(3*y*z))
        == Exp(w*x)**2 * Exp(y*z)**3
    )
    assert (
        exp_expand(Exp(2*(x+y)))
        == exp_expand(Exp(x+y)**2)
        == Exp(x)**2 * Exp(y)**2
    )
    assert (
        exp_expand(Exp((x+y)*(x-y)))
        == Exp(x**2) / Exp(y**2)
    )
    assert (
        exp_expand(1 / (Exp(2*x)-Exp(x)**2))
        is UNDEFINED
    )

def test_exp_contract():
    """Tests for the exp_contract() operator."""
    assert (
        exp_contract(Exp(x)*Exp(y))
        == Exp(x+y)
    )
    assert (
        exp_contract(Exp(x)**y)
        == Exp(x*y)
    )
    assert (
        exp_contract(Exp(x)*(Exp(x)+Exp(y)))
        == exp_contract(Exp(x)**2 + Exp(x)*Exp(y))
        == Exp(2*x) + Exp(x+y)
    )
    assert (
        exp_contract(Exp(Exp(x))**Exp(y))
        == exp_contract(Exp(Exp(x)*Exp(y)))
        == Exp(Exp(x+y))
    )

def test_exp_simplify():
    """Tests for the exp_simplify() operator."""
    assert (
        exp_simplify(1/(Exp(x)*(Exp(y)+Exp(-x))) - (Exp(x+y)-1)/(Exp(x+y)**2 - 1))
        == 0
    )

def test_log_expand():
    """Tests for the log_expand operator."""
    assert (
        log_expand(Ln(x*y))
        == Ln(x) + Ln(y)
    )
    assert (
        log_expand(Ln(x**y))
        == y*Ln(x)
    )
    a, b = symbols("a b")
    assert (
        log_expand(Ln((w*x)**a)) + Ln(y**b*z)
        == a*(Ln(w) + Ln(x)) + b*Ln(y) + Ln(z)
    )
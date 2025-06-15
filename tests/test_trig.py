import pytest

from levycas.expressions import *
from levycas import trig_simplify

def test_trig_simplify():
    """Early tests for the trig_simplify operator"""
    x = Variable('x')

    assert (
        trig_simplify(Sin(x) ** 2 + Cos(x) ** 2)
        == 1
    )

    assert (
        trig_simplify(Cos(4*x)*(Sin(x) + Sin(3*x) + Sin(5*x) + Sin(7*x))) 
        == trig_simplify(Sin(4*x)*(Cos(x)+Cos(3*x)+Cos(5*x)+Cos(7*x)))
    )
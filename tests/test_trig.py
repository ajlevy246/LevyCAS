import pytest

from levycas.expressions import *
from levycas import trig_simplify, trig_contract, trig_expand

def test_trig_expand():
    """Tests for the trig_expand() operator"""
    x, y = Variable('x'), Variable('y')

    assert (
        trig_expand(Sin(x + y)) 
        == Sin(x) * Cos(y) + Cos(x) * Sin(y)
    )

    assert (
        trig_expand(Cos(x + y))
        == Cos(x) * Cos(y) - Sin(x) * Sin(y)
    )

    assert (
        trig_expand(Sin(2*(x+y)))
        == trig_expand(2*Sin(x+y)*Cos(x+y))
        == 2*(Sin(x)*Cos(y) + Cos(x)*Sin(y)) * (Cos(x)*Cos(y) - Sin(x)*Sin(y))
    )

    assert (
        trig_expand(Sin(2*x + 3*y)) 
        == trig_expand(Sin(2*x)*Cos(3*y) + Cos(2*x)*Sin(3*y))
        == 2*Sin(x)*Cos(x)*(Cos(y)**3 - 3*Cos(y)*Sin(y)**2) + \
              (Cos(x)**2 - Sin(x)**2) * (3*Cos(y)**2*Sin(y) - Sin(y)**3)
    )



# def test_trig_simplify():
#     """Early tests for the trig_simplify operator"""
#     x = Variable('x')

#     assert (
#         trig_simplify(Sin(x) ** 2 + Cos(x) ** 2)
#         == 1
#     )

#     assert (
#         trig_simplify(Cos(4*x)*(Sin(x) + Sin(3*x) + Sin(5*x) + Sin(7*x))) 
#         == trig_simplify(Sin(4*x)*(Cos(x)+Cos(3*x)+Cos(5*x)+Cos(7*x)))
#     )


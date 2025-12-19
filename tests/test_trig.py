import pytest

from levycas.expressions import *
from levycas import trig_simplify, trig_contract, trig_expand, symbols

def test_trig_asimplify():
    """Tests for substitution and automatic simplification of trig operations"""
    x, y = symbols('x y')

    assert 1 - Cos(0) == 0
    assert Cos(-x) == Cos(x)

    assert 1 - Sin(0) == 1
    assert Sin(-x) == -Sin(x)

def test_trig_expand():
    """Tests for the trig_expand() operator"""
    x, y = symbols('x y')

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
        == trig_expand(2*(Sin(x)*Cos(y) + Cos(x)*Sin(y)) * (Cos(x)*Cos(y) - Sin(x)*Sin(y)))
    )

    assert (
        trig_expand(Sin(2*x + 3*y)) 
        == trig_expand(Sin(2*x)*Cos(3*y) + Cos(2*x)*Sin(3*y))
        == trig_expand(2*Sin(x)*Cos(x)*(Cos(y)**3 - 3*Cos(y)*Sin(y)**2) + \
              (Cos(x)**2 - Sin(x)**2) * (3*Cos(y)**2*Sin(y) - Sin(y)**3))
    )

def test_trig_identities():
    """Tests that trigonometric simplification applies identities correctly"""
    theta, phi = Variable('\u03b8'), Variable('\u03d5')

    #Reciprocal identities
    assert (
        trig_simplify(1 / Csc(theta))
        == Sin(theta)
    )

    assert (
        trig_simplify(1 / Sec(theta))
        == Cos(theta)
    )

    assert (
        trig_simplify(1 / Cot(theta))
        == trig_simplify(Tan(theta))
    )

    #Pythagorean identities
    assert (
        trig_simplify(Sin(theta) ** 2 + Cos(theta) ** 2)
        == trig_simplify(Sec(theta) ** 2 - Tan(theta) ** 2)
        == trig_simplify(Csc(theta) ** 2 - Cot(theta) ** 2)
        == 1
    )

    #Even-Odd identities
    assert (
        trig_simplify(Sin(-theta))
        == -Sin(theta)
    )

    assert (
        trig_simplify(Tan(-theta))
        == trig_simplify(-Tan(theta))
    )

    assert (
        trig_simplify(Sec(-theta))
        == trig_simplify(Sec(theta))
    )

    #Sum identities
    assert (
        trig_simplify(Sin(theta + phi))
        == trig_simplify(Sin(theta) * Cos(phi) + Cos(theta) * Sin(phi))
    )

    assert (
        trig_simplify(Cos(theta + phi))
        == trig_simplify(Cos(theta) * Cos(phi) - Sin(theta) * Sin(phi))
    )

    assert (
        trig_simplify(Tan(theta + phi))
        == trig_simplify((Tan(theta) + Tan(phi)) / (1 - Tan(theta) * Tan(phi)))
    )

    #Difference identities
    assert (
        trig_simplify(Sin(theta - phi))
        == trig_simplify(Sin(theta) * Cos(phi) - Cos(theta) * Sin(phi))
    )

    assert (
        trig_simplify(Cos(theta - phi))
        == trig_simplify(Cos(theta) * Cos(phi) + Sin(theta) * Sin(phi))
    )

    assert (
        trig_simplify(Tan(theta - phi))
        == trig_simplify((Tan(theta) - Tan(phi)) / (1 + Tan(theta) * Tan(phi)))
    )

    #Double-angle identities
    assert (
        trig_simplify(Sin(2 * theta))
        == trig_simplify(2 * Sin(theta) * Cos(theta))
    )

    assert (
        trig_simplify(Cos(2 * theta))
        == trig_simplify(Cos(theta) ** 2 - Sin(theta) ** 2)
        == trig_simplify(2 * Cos(theta) ** 2 - 1)
        == trig_simplify(1 - 2 * Sin(theta) ** 2)
    )

    assert (
        trig_simplify(Tan(2 * theta))
        == trig_simplify(2 * Tan(theta) / (1 - Tan(theta) ** 2))
    )

    #Multiple-angle identities:
    assert (
        trig_simplify(Sin(4*theta))
        == trig_simplify(4 * Cos(theta)**3 * Sin(theta) - 4 * Cos(theta) * Sin(theta)**3)
    )


    #Cofunction identities, half-angle, triple-angle, supplement angle -> Not yet implemented (requires Pi implementation)

def test_trig_contract():
    """Tests for the trig_contract() operator"""
    x, y = symbols("x y")

    assert (
        trig_contract((Sin(x) + Cos(y)) * Cos(y))
        == trig_contract(Sin(x) * Cos(y) + Cos(y)**2)
        == (1 / 2) * (Sin(x + y) + Sin(x - y) + Cos(2*y) + 1)
    )
    
    assert (
        trig_contract(Sin(x)**2 * Cos(x)**2)
        == trig_contract( (1 / 2) * (1 - Cos(2*x)) * (1 / 2) * (1 + Cos(2*x)))
        == trig_contract( (1 / 4) * (1 - (1 / 2) * (1 + Cos(4*x))))
        == (1 / 8) * (1 - Cos(4*x))
    )

    assert (
        trig_contract(Cos(x)**4)
        ==  (1 / 8) * Cos(4*x) + (1 / 2) * Cos(2*x) + (3 / 8)
    )

    assert (
        trig_contract(Cos(x)**3)
        == (1 / 4) * (3*Cos(x) + Cos(3*x))
    )

    assert (
        trig_contract(Sin(x)**3)
        == (1 / 4) * (3*Sin(x) - Sin(3*x))
    )

    assert (
        trig_contract(Sin(x)**4)
        == (1 / 8) * (3 - 4*Cos(2*x) + Cos(4*x))
    )

def test_trig_simplify():
    """Tests from the Elementary Algorithms for the trig_simplify() operator"""
    x = Variable('x')

    assert (
        trig_simplify(Cos(2*x) * (Sin(x) + Sin(3*x)))
        == trig_simplify(Sin(2*x) * (Cos(x) + Cos(3*x)))
    )

    assert (
        trig_simplify(Cos(4*x) * (Sin(x) + Sin(3*x) + Sin(5*x) + Sin(7*x)))
        == trig_simplify(Sin(4*x) * (Cos(x) + Cos(3*x) + Cos(5*x) + Cos(7*x)))
    )
import pytest

from levycas import Exp, Sin, Cos, Variable
from levycas.operations.expression_ops import (
    symbols, get_symbols,
    contains, map_op, construct,
    substitute, copy_expr
)

x, y, z = symbols("x y z")

def test_symbols():
    vars = symbols("x y z")
    assert vars == (Variable('x'), Variable('y'), Variable('z'))
    x = symbols("  x  ")
    assert isinstance(x, Variable) and x == Variable('x')

def test_get_symbols():
    expr = Exp(x)**Sin(y) + 4*Cos(3+z)
    assert get_symbols(expr) == { x, y, z }
    
    expr = Exp(4)**Sin(3) + 4*Cos(3)
    assert get_symbols(expr) == set()

    assert get_symbols(x) == {x,}
    assert get_symbols(y) == {y,}
    assert get_symbols(z) == {z,}

def test_contains():
    expr = Exp(x) ** Sin(y) + 3*Cos(x*y) - 4*Sin(4*x**2+3*y+2)
    subs = [
        expr,
        x, y, x*y, x*y,
        4*x**2 + 3*y + 2,
        Exp(x),Sin(y),Cos(x*y),
        Exp(x)**Sin(y),
        3*Cos(x*y),
        Sin(4*x**2+3*y+2),
        -4*Sin(4*x**2+3*y+2),
    ]
    for sub in subs:
        assert contains(expr, sub)
    assert not contains(1, x)
    assert not contains(Sin(x) + 3*Cos(x), y)

def test_map_op():
    ...

def test_copy_expr():
    expr = 4*(Exp(4*Sin(x**2 + 3*x + Cos(x))))
    copy = copy_expr(expr)
    assert expr is not copy and str(expr) == str(copy) and expr == copy

def test_substitute():
    expr = Exp(x**2) * Sin(2*x**2 + 3) + Cos(x**2) ** Sin(2*x)

    assert (
        substitute(expr, x, y) == 
        Exp(y**2) * Sin(2*y**2 + 3) + Cos(y**2) ** Sin(2*y)
    )
    assert (
        substitute(expr, x**2, y) ==
        Exp(y) * Sin(2*y + 3) + Cos(y) ** Sin(2*x)
    )
    assert (
        substitute(expr, Cos(x**2), x*y) ==
        Exp(x**2) * Sin(2*x**2 + 3) + (x*y) ** Sin(2*x)
    )
import pytest
from levycas import *

def test_parse():
    x, y, z = symbols('x y z')

    #Basic order of operations tests
    assert (
        parse("1 + 2 * 3")
        == 7
    )
    assert (
        parse("x + y * z")
        == x + y * z
    )
    assert (
        parse("4 - 2 - 1")
        == 1
    )
    assert (
        parse("x - y - z")
        == x - y - z
    )
    assert (
        parse("2 * 3 + 4 * 5")
        == 26
    )
    assert (
        parse("3 + 4 * 2 / (1 - 5) ^ 2 ^ 3")
        == Rational(24577, 8192)
    )

def test_tests():
    """Reruns some tests, but with parsing"""
    x, y, z = parse('x'), parse('y'), parse('z')

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
        integrate(parse('xcos(x)'), x)
        == parse("xsin(x) + cos(x)")
    )
    assert (
        integrate(parse('(x^2)cos(x)'), x)
        == parse("(x^2)sin(x) + 2xcos(x) - 2sin(x)")
    )
    assert (
        integrate(parse('xcos(2x)'), x)
        == parse("(1/2)xsin(2x) + (1/4)cos(2x)")
    )
import pytest
from levycas import *

def test_parse():
    x, y, z = Variable('x'), Variable('y'), Variable('z')

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

    #Case sensitivity tests
    assert (
        parse("Cos(x)")
        == parse("COS(x)")
        == parse("cOs(x)")
        == parse("cosx")
        == parse("cOSx")
        == Cos(x)
    )
"""Tests for the numerical operations module."""
import pytest

from levycas.operations.numerical_ops import *

def test_gcd():
    assert gcd(12, 8) == 4
    assert gcd(100, 10) == 10
    assert gcd(17, 13) == 1
    assert gcd(7, 0) == 7
    assert gcd(0, 0) == 0
    assert gcd(-12, 8) == 4
    assert gcd(123456, 7890) == 6
    assert gcd(9, 9) == 9
    assert gcd(Integer(0), Integer(5)) == 5
    assert gcd(12, Integer(-8)) == 4
    assert gcd(Integer(-12), Integer(-8)) == 4

def test_factor_integer():
    assert (
        factor_integer(2198374)
        == {2: 1, 29: 2, 1307: 1}
    )
    assert (
        factor_integer(Integer(23847932475))
        == {
            3: 2,
            5: 2,
            103: 1,
            1029037: 1
        }
    )
    assert (
        factor_integer(2)
        == {2: 1}
    )
    assert (
        factor_integer(6)
        == {
            2: 1,
            3: 1
        }
    )
    assert (
        factor_integer(Integer(2**6 * 3**5 * 5**3 * 7**3))
        == {
            2: 6,
            3: 5,
            5: 3,
            7: 3
        }
    )
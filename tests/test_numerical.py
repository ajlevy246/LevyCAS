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

    #Over the field of rational numbers, we have that gcd(a, b) = 1 whenever a or b is non-zero
    assert gcd(Rational(2384729374, 123), 0) == 1
    assert gcd(0, Rational(234857, 2394)) == 1
    assert gcd(Rational(123354, 2), Rational(2345, 2)) == 1

def test_is_prime():
    ip = lambda x: is_prime(Integer(x))
    
    assert not ip(1)
    assert not ip(23452)
    assert not ip(4385379)
    assert not ip(32453453)

    assert ip(2)
    assert ip(3)
    assert ip(5)
    assert ip(7)
    assert ip(11)

    assert ip(5431)
    assert ip(89071)
    assert ip(10853)
    assert ip(79987)

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

def test_radical():
    assert (
        radical(16)
        == 2
    )
    assert (
        radical(17)
        == 17
    )
    assert (
        radical(18)
        == 6
    )
    assert (
        radical(1000000)
        == 10
    )
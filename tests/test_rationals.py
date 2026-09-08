"""Tests for LevyCAS Constants."""

import math

import pytest

from levycas.expressions import UNDEFINED, Integer, Rational
from levycas.operations.numerical_ops import gcd


class TestConstruction:
 
    def test_integer_basic(self):
        assert Integer(5).value == 5
 
    def test_integer_from_float_truncates_or_rejects(self):
        assert (
            Integer(4.0).value
            == Integer(4)
            == 4
        )
 
    def test_rational_reduces_to_lowest_terms(self):
        r = Rational(4, 8)
        assert isinstance(r, Rational)
        assert r.num() == 1 and r.denom() == 2
 
    def test_rational_demotes_to_integer(self):
        r = Rational(6, 3)
        assert isinstance(r, Integer)
        assert r.value == 2
 
    def test_rational_negative_denominator_normalizes_sign(self):
        r = Rational(3, -4)
        assert r.num() == -3 and r.denom() == 4
 
    def test_rational_both_negative_normalizes_to_positive(self):
        r = Rational(-3, -4)
        assert r.num() == 3 and r.denom() == 4
 
    def test_rational_div_by_zero_is_undefined(self):
        assert Rational(1, 0) is UNDEFINED
 
    def test_rational_single_arg_is_integer_valued(self):
        r = Rational(7)
        assert isinstance(r, Integer)
        assert r.value == 7
 
    def test_rational_with_boxed_integer_args(self):
        r = Rational(Integer(4), Integer(8))
        assert isinstance(r, Rational)
        assert r.num() == 1 and r.denom() == 2
 
    def test_rational_with_mixed_boxed_and_native_args(self):
        r = Rational(Integer(9), 3)
        assert isinstance(r, Integer)
        assert r.value == 3
 
    def test_integer_rejects_two_args(self):
        with pytest.raises(TypeError):
            Integer(3, 2)
 
    def test_rational_subclass_without_own_new_raises(self):
        with pytest.raises(TypeError):
            class Fake(Rational):
                pass
            Fake(1, 2)
 
class TestEqualityAndHash:
 
    @pytest.mark.parametrize("a,b", [
        (Integer(4), 4),
        (4, Integer(4)),
        (Integer(4), Integer(4)),
        (Integer(4), Rational(4, 1)),
        (Rational(1, 2), 0.5),
        (Rational(4, 8), Rational(1, 2)),
        (Integer(0), 0),
        (Integer(-3), -3),
    ])
    def test_equal_pairs(self, a, b):
        assert a == b
        assert b == a
 
    @pytest.mark.parametrize("a,b", [
        (Integer(4), 5),
        (Rational(1, 2), Rational(1, 3)),
        (Integer(4), Rational(1, 2)),
    ])
    def test_unequal_pairs(self, a, b):
        assert a != b
        assert b != a
 
    def test_hash_consistent_with_equality(self):
        assert hash(Integer(4)) == hash(4)
        assert hash(Rational(1, 2)) == hash(Rational(2, 4))
 
    def test_integer_hashable_in_set(self):
        s = {Integer(1), Integer(2), 2, Rational(1, 1)}
        assert len(s) <= 3
 
class TestAddSubMul:
    @pytest.mark.parametrize("a,b,expected", [
        (Integer(2), Integer(3), 5),
        (Integer(2), 3, 5),
        (3, Integer(2), 5),
        (Rational(1, 2), Rational(1, 3), Rational(5, 6)),
        (Rational(1, 2), 1, Rational(3, 2)),
        (1, Rational(1, 2), Rational(3, 2)),
        (Integer(2), Rational(1, 2), Rational(5, 2)),
    ])
    def test_add(self, a, b, expected):
        assert a + b == expected
 
    @pytest.mark.parametrize("a,b,expected", [
        (Integer(5), Integer(3), 2),
        (Rational(1, 2), Rational(1, 3), Rational(1, 6)),
        (Integer(1), Rational(1, 2), Rational(1, 2)),
        (Rational(1, 2), 1, Rational(-1, 2)),
    ])
    def test_sub(self, a, b, expected):
        assert a - b == expected
 
    @pytest.mark.parametrize("a,b,expected", [
        (Integer(4), Integer(5), 20),
        (Integer(4), 5, 20),
        (Rational(2, 3), Rational(3, 4), Rational(1, 2)),
        (Rational(2, 3), 3, Integer(2)),
        (Integer(0), Rational(5, 7), Integer(0)),
    ])
    def test_mul(self, a, b, expected):
        assert a * b == expected
 
    def test_add_result_type_demotes_to_integer(self):
        result = Rational(1, 2) + Rational(1, 2)
        assert isinstance(result, Integer)
        assert result.value == 1
 
class TestFloorDivMod:
 
    @pytest.mark.parametrize("a,b,expected", [
        (Integer(7), Integer(2), 3),
        (Integer(7), 2, 3),
        (7, Integer(2), 3),
        (Rational(7, 2), 1, 3),
        (Integer(-7), Integer(2), -4),
    ])
    def test_floordiv(self, a, b, expected):
        assert a // b == expected
 
    @pytest.mark.parametrize("a,b,expected", [
        (Integer(7), Integer(2), 1),
        (Integer(-7), Integer(2), 1),
        (Rational(7, 2), Integer(1), Rational(1, 2)),
    ])
    def test_mod(self, a, b, expected):
        assert a % b == expected
 
class TestCoercion:
 
    def test_abs_integer(self):
        assert abs(Integer(-5)) == Integer(5)
        assert abs(Integer(5)) == Integer(5)
 
    def test_abs_rational(self):
        assert abs(Rational(-3, 4)) == Rational(3, 4)
 
    def test_int_conversion(self):
        assert int(Integer(7)) == 7
 
    def test_float_conversion(self):
        assert float(Rational(1, 4)) == 0.25
        assert float(Integer(3)) == 3.0
 
    def test_eval_integer_stays_exact_where_expected(self):
        result = Integer(4).eval()
        assert result == 4
 
class TestPow:
 
    def test_integer_pow_positive_integer(self):
        assert Integer(2) ** Integer(10) == 1024
 
    def test_integer_pow_native_int_exponent(self):
        assert Integer(2) ** 10 == 1024
 
    def test_integer_pow_zero_exponent(self):
        assert Integer(5) ** Integer(0) == 1
        assert Integer(0) ** Integer(0) == 1 
 
    def test_zero_pow_positive(self):
        assert Integer(0) ** Integer(3) == 0
 
    def test_zero_pow_negative_is_undefined(self):
        assert Integer(0) ** Integer(-1) is UNDEFINED
 
    def test_integer_pow_negative_exponent_is_exact_fraction(self):
        result = Integer(4) ** Integer(-1)
        assert result == Rational(1, 4)
        assert isinstance(result, Rational)
        assert not isinstance(result, float)
 
    def test_integer_pow_negative_exponent_native(self):
        result = Integer(4) ** -1
        assert result == Rational(1, 4)
 
    def test_negative_base_pow_negative_integer_exponent(self):
        result = Integer(-2) ** Integer(-2)
        assert result == Rational(1, 4)
 
    def test_negative_base_pow_odd_negative_integer_exponent(self):
        result = Integer(-2) ** Integer(-3)
        assert result == Rational(-1, 8)
 
    def test_one_pow_anything(self):
        assert Integer(1) ** Integer(-100) == 1
        assert Integer(1) ** Integer(100) == 1
 
    def test_pow_with_mod(self):
        assert pow(Integer(3), Integer(4), Integer(5)) == pow(3, 4, 5)
 
    def test_pow_with_mod_rejects_non_integer_exponent(self):
        with pytest.raises(ValueError):
            pow(Integer(3), Rational(1, 2), Integer(5))
 
    def test_pow_with_mod_rejects_non_integer_modulus(self):
        with pytest.raises(ValueError):
            pow(Integer(3), Integer(4), Rational(1, 2))
 
    def test_rational_pow_positive_integer(self):
        assert Rational(2, 3) ** Integer(2) == Rational(4, 9)
 
    def test_rational_pow_negative_integer_is_reciprocal_power(self):
        assert Rational(2, 3) ** Integer(-2) == Rational(9, 4)
 
    def test_negative_rational_pow_negative_integer(self):
        assert Rational(-2, 3) ** Integer(-1) == Rational(-3, 2)
 
    def test_perfect_square_root_exponent(self):
        assert Integer(4) ** Rational(1, 2) == Integer(2)
 
    def test_perfect_cube_root_exponent(self):
        assert Integer(8) ** Rational(1, 3) == Integer(2)
 
    def test_perfect_root_with_numerator_other_than_one(self):
        # 4 ** (3/2) == (4**(1/2))**3 == 2**3 == 8
        assert Integer(4) ** Rational(3, 2) == Integer(8)
 
    def test_non_perfect_root_returns_simplified_radical_or_power_expr(self):
        result = Integer(2) ** Rational(1, 2)
        assert not isinstance(result, float)
 
    def test_partial_root_extraction(self):
        result = Integer(8) ** Rational(1, 2)
        assert not isinstance(result, float)
        assert math.isclose(float(result), math.sqrt(8), rel_tol=1e-9)
 
    def test_negative_base_non_integer_exponent_raises_or_handles_imaginary(self):
        with pytest.raises(ValueError):
            Integer(-4) ** Rational(1, 2)
 
    def test_rational_exponent_reduces_zero_to_one(self):
        assert Integer(5) ** Rational(0, 3) == 1  # Rational(0,3) reduces to Integer(0)
 
    def test_integer_pow_float_exponent_behaves_reasonably(self):
        result = Integer(4) ** 0.5
        assert math.isclose(float(result), 2.0)
 
    def test_native_int_pow_boxed_integer_uses_rpow(self):
        result = 2 ** Integer(10)
        assert result == 1024
 
class TestGcdRegressions:
 
    def test_gcd_does_not_hang_on_equal_values(self):
        assert gcd(4, 4) == 4
 
    def test_gcd_native_ints(self):
        assert gcd(12, 18) == 6
 
    def test_gcd_boxed_integers(self):
        assert gcd(Integer(12), Integer(18)) == Integer(6)
 
    def test_gcd_mixed_native_and_boxed(self):
        assert gcd(Integer(12), 18) == 6
 
    def test_gcd_with_zero(self):
        assert gcd(0, 5) == 5
        assert gcd(5, 0) == 5
 
    def test_gcd_rational_returns_one(self):
        assert gcd(Rational(1, 2), Integer(4)) == 1
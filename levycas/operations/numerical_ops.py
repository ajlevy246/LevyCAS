"""Operations acting on Constants (rationals)."""
from levycas.expressions import Constant, Rational, Integer

def gcd(a: Integer, b: Integer) -> Integer:
    """Computes the greated common divisor of two integers using binary gcd algorithm.

    Args:
        a (Integer): First integer
        b (Integer): Second integer

    Returns:
        Integer: gcd(a, b)
    """
    a, a_d = _reduce(a)
    b, b_d = _reduce(b)
    d = a_d if a_d < b_d else b_d

    while a != b:
        if b < a:
            a = _reduce(a - b)[0]
        else:
            b = _reduce(b - a)[0]

    return Integer(2 ** d) * abs(a)


def _reduce(a: Integer) -> tuple[Integer]:
    """Helper method to reduce an even number to an odd one,
    keeping track of the number of divisions by 2.

    Args:
        a (Integer): Integer to reduce

    Returns:
        tuple[Integer]: (a', d) where a' and d are such that a = a'/2**d
    """
    d = 0
    while a % 2 == 0:
        d += 1
        a //= 2
    return a, d
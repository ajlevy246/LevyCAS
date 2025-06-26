"""Operations acting on Constants (rationals)."""
from levycas.expressions import Integer, convert_primitive

def gcd(a: Integer, b: Integer) -> Integer:
    """Computes the greated common divisor of two integers using binary gcd algorithm.

    Args:
        a (Integer): First integer
        b (Integer): Second integer

    Returns:
        Integer: gcd(a, b)
    """
    if a == 1 or b == 1:
        return Integer(1)
    if a == 0:
        return b
    if b == 0:
        return a

    a, a_d = _reduce(abs(a))
    b, b_d = _reduce(abs(b))
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

def factor_integer(a: Integer | int) -> dict[int, int]:
    """Given an integer, returns a dictionary with key, value pairs (p, m),
    with p the prime factor and m it's multiplicity. 

    Utilize the Pollard Rho factorization algorithm below.

    Args:
        a (Integer): The Integer to factor.

    Returns:
        dict[Integer, Integer]: The dictionary with keys p and values m
    """
    if isinstance(a, int):
        a = Integer(a)
    if not isinstance(a, Integer):
        raise TypeError(f"factor_integer does not support {type(a)}")
    
    factors = dict()
    while a != 1:
        new_factor = _pollard_rho(a)
        a //= new_factor
        factors[new_factor] = factors.get(new_factor, 0) + 1
    return factors

def is_prime(a: Integer) -> bool:
    """Primality test for the given integer, implemented only for small
    integers right now < 2 ^ 64

    Args:
        a (Integer): The integer to test

    Returns:
        bool: True if a is prime, False otherwise
    """
    #TODO: Implement a working primality test
    from sympy import isprime
    return isprime(a)

def _pollard_rho(n: Integer) -> Integer | None:
    """An implementation of Pollard Rho algorithm for integer factorization.
    Given an integer a, returns d, a non-trivial divisor of a. 
    
    Based on the starting value, the algorithm may fail to find a divisor.
    In this case, it tries again with a different starting value. If all starting values
    are somehow exhausted, raises an error.

    see: https://en.wikipedia.org/wiki/Pollard%27s_rho_algorithm

    Args:
        n (Integer): The Integer to factor, n > 3

    Returns:
        Integer | None: A non-trivial factor of a.
    """
    if isinstance(n, int):
        n = Integer(n)

    if not isinstance(n, Integer):
        raise TypeError(f"Cannot factor type {type(n)}")

    #Bounds check
    if n < 4:
        return n
    if is_prime(n):
        return n
    
    b = d = Integer(1)
    x = y = Integer(0)
    g = lambda val: (val ** 2 + b) % n

    for x in range(n):
        for b in range(1, n - 2):
            while d == 1:
                x = g(x)
                y = g(g(y))
                d = gcd(abs(x - y), n)
            if d == n:
                continue
            return d
    raise ValueError(f"Could not factor {n} with Pollard's Rho Algorithm")


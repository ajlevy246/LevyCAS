"""Operations acting on Constants (rationals)."""
from functools import cache

from levycas.expressions import Constant, Integer, Rational

def gcd(a: Constant, b: Constant) -> Integer:
    """Computes the greated common divisor of two integers using binary gcd algorithm.

    Args:
        a (Integer): First integer
        b (Integer): Second integer

    Returns:
        Integer: gcd(a, b)
    """
    if isinstance(a, Rational) or isinstance(b, Rational):
        return Integer(1)
    
    a, b = int(a), int(b)
    if a == 1 or b == 1:
        return Integer(1)
    if a == 0:
        return abs(Integer(b))
    if b == 0:
        return abs(Integer(a))

    a, a_d = _reduce(abs(a))
    b, b_d = _reduce(abs(b))
    d = a_d if a_d < b_d else b_d

    while a != b:
        if b < a:
            a = _reduce(a - b)[0]
        else:
            b = _reduce(b - a)[0]

    return Integer(2 ** d * abs(a))

def _reduce(a: Integer) -> tuple[Integer]:
    """Helper method to reduce an even number to an odd one,
    keeping track of the number of divisions by 2.

    Args:
        a (Integer): Integer to reduce

    Returns:
        tuple[Integer]: (a', d) where a' and d are such that a' = a/2**d
    """
    a = int(a)
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
    a = int(a)
    
    factors = dict()
    while a != 1:
        #Base case
        if is_prime(a):
            factors[a] = factors.get(a, 0) + 1
            return factors

        new_factor = _pollard_rho(a)
        a //= new_factor

        #New factor may not be prime, in which case recursion is used.
        new_factors = factor_integer(new_factor)
        new_factors = {key: val + factors.get(key, 0) for key, val in new_factors.items()}
        factors.update(new_factors)

    return factors

@cache
def is_prime(n: Integer) -> bool:
    """Primality test for the given integer, implemented only for small
    integers right now. Implements the Miller-Rabin test for the first 12 prime bases.

    Utilizies functools cache for faster lookups.

    This test is deterministic for integers up to 2**64, and for larger integers it is
    probabilistic, but almost always accurate.

    See: https://en.wikipedia.org/wiki/Miller%E2%80%93Rabin_primality_test#Testing_against_small_sets_of_bases

    Args:
        n (Integer): The integer to test

    Returns:
        bool: True if n is prime, False otherwise
    """
    n = int(n)
    if n < 2:
        return False
    
    #Check manually against first few small primes:
    SMALL_PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37)
    if n in SMALL_PRIMES:
        return True

    d, s = _reduce(n - 1)
    for a in SMALL_PRIMES: #Small bases sufficient for ints up to 2^64
        x = pow(a, d, n)
        for i in range(s):
            y = pow(x, 2, n)
            if y == 1 and x != 1 and x != n - 1:
                return False
            x = y
        if x != 1:
            return False
    return True

def _pollard_rho(n: Integer, check_prime = False) -> Integer | None:
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
    n = int(n)

    #Bounds check
    if n < 4:
        return n
    if check_prime and is_prime(n):
        return n
    
    #Cheap check for even
    if n % 2 == 0:
        return 2

    b = d = 1
    x = y = 0
    g = lambda val: (val ** 2 + b) % n

    for x in range(n):
        for b in range(1, n - 1):
            while d == 1:
                x = g(x)
                y = g(g(y))
                d = gcd(abs(x - y), n)
            if d == n:
                #Failure, repeat with new parameters
                d = 1
                continue
            return d
    raise ValueError(f"Could not factor {n} with Pollard's Rho Algorithm")

def radical(n: Integer) -> Integer:
    """Computes the radical of an integer, defined
    as the product of its unique prime factors.

    Args:
        n (Integer): The integer whose radical is computed

    Returns:
        Integer: rad(n); the product of its unique prime factors
    """
    n = int(n)
    factors = factor_integer(n)
    rad = Integer(1)
    for factor in factors.keys():
        rad *= factor
    return rad
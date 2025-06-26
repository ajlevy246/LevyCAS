"""Operations acting on Constants (rationals)."""
from levycas.expressions import Integer

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

def factor_integer(a: Integer) -> dict[int, int]:
    """Given an integer, returns a dictionary with key, value pairs (p, m),
    with p the prime factor and m it's multiplicity. 

    Utilize the Pollard Rho factorization algorithm below.

    Args:
        a (Integer): The Integer to factor.

    Returns:
        dict[Integer, Integer]: The dictionary with keys p and values m
    """
    factors = dict()
    while a != 1:
        new_factor = _pollard_rho(a)
        a //= new_factor
        factors[new_factor] = factors.get(new_factor, 0) + 1
        print(f"new factor: {new_factor}, new check {a}")
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

def _pollard_rho(n: Integer, x: Integer = Integer(0), b: Integer = Integer(1)) -> Integer | None:
    """An implementation of Pollard Rho algorithm for integer factorization.
    Given an integer a, returns d, a non-trivial divisor of a. 
    
    Based on the starting value, the algorithm may fail to find a divisor.
    In this case, it tries again with a different starting value. If all starting values
    are somehow exhausted, raises an error.

    see: https://en.wikipedia.org/wiki/Pollard%27s_rho_algorithm

    Args:
        n (Integer): The Integer to factor
        x (int, optional): Preset starting search value. Defaults to 0.
        b (int, optional) Preset offset for the searching polynomial. Defaults to 1.

    Returns:
        Integer | None: A non-trivial factor of a.
    """
    #Bounds check
    if x < Integer(0) or not x < n:
        raise ValueError(f"Could not find any divisors of {n}; check starting x")
    if b < Integer(1) or not b < (n - 2):
        raise ValueError(f"Could not find any divisors of {n}; check starting b")

    g = lambda val: (val ** 2 + b) % n

    y, d = x, Integer(1)
    while d == 1:
        x = g(x)
        y = g(g(y))
        print(f"Calculating gcd({abs(x - y)}, {n})")
        d = gcd(abs(x - y), n)

    if d == n:
        print(f"Checking primality of {n}")
        #Check primality on first iteration only
        if x == 0 and b == 1 and is_prime(n): 
            return n
        
        #Algorithm failed, iterate starting values:
        if x == n - 1:
            if b == n - 3:
                raise ValueError(f"Could not find any divisors of {n}??")
            return _pollard_rho(n, 0, b + 1)
        return _pollard_rho(n, x + 1)

    return d

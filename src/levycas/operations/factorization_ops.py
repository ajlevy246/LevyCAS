"""Polynomial factorization routines (Yun's Algorithm, Hensel Lifting, et cetera"""
from levycas.expressions import *
from .polynomial_ops import (
    random_polynomial_mod_p,
    algebraic_expand,
    degree,
    reduce_mod_p,
    polynomial_pow_mod,
    polynomial_gcd_mod_p,
    leading_coefficient,
    mod_inverse,
    polynomial_divide_mod_p,
    polynomial_gcd,
    polynomial_divide,
)


def _edf_split_attempt(g: Expression, d: int, x: Variable, p: int) -> Expression | None:
    """Attempts one random split of g, assumed to be a product of irreducible
    factors all of degree d. Returns a proper nontrivial factor of g, or None
    if this attempt failed to split.

    Requires p odd.

    Args:
        g (Expression): Monic polynomial, product of same-degree irreducibles
        d (int): The common degree of g's irreducible factors
        x (Variable): Polynomial variable
        p (int): An odd prime modulus

    Returns:
        Expression | None: A proper monic factor of g, or None
    """
    assert p != 2, "Cantor-Zassenhaus odd-degree split requires p odd"
    n = int(degree(g, x))
    a = random_polynomial_mod_p(x, n, p)

    gcd1 = polynomial_gcd_mod_p(a, g, x, p)
    if gcd1 != 1:
        return gcd1

    exponent = (p**d - 1) // 2
    b = polynomial_pow_mod(a, exponent, g, x, p)
    b_minus_1 = reduce_mod_p(b - 1, x, p)
    gcd2 = polynomial_gcd_mod_p(b_minus_1, g, x, p)

    if gcd2 != 1 and gcd2 != g:
        return gcd2
    return None

def factor_mod_p(f: Expression, x: Variable, p: int) -> list[Expression]:
    """Given a squarefree polynomial f, returns the complete list of monic 
    irreducible factors of f mod p.

    Args:
        f (Expression): A squarefree polynomial mod p
        x (Variable): Polynomial variable
        p (int): An odd prime modulus

    Returns:
        list[Expression]: All monic irreducible factors, with multiplicity 
            (though f being squarefree means no repeats)
    """
    lc_inv = mod_inverse(int(leading_coefficient(f, x)), p)
    f_monic = reduce_mod_p(Integer(lc_inv) * f, x, p)

    factors = []
    for g, d in distinct_degree_factorization(f_monic, x, p):
        factors.extend(equal_degree_factorization(g, d, x, p))
    return factors

def distinct_degree_factorization(f: Expression, x: Variable, p: int) -> list[tuple[Expression, int]]:
    """Given a squarefree polynomial f mod p, groups its irreducible factors 
    by degree without splitting same-degree factors apart from each other.

    Args:
        f (Expression): A squarefree polynomial, monic or not, mod p
        x (Variable): Polynomial variable
        p (int): Prime modulus

    Returns:
        list[tuple[Expression, int]]: List of (g_i, i) pairs, where g_i is the 
            product of all irreducible factors of f of degree i.
    """
    lc_inv = mod_inverse(int(leading_coefficient(f, x)), p)
    f = reduce_mod_p(Integer(lc_inv) * f, x, p)

    result = []
    f_bar = f
    h = x
    i = 0

    while True:
        d = degree(f_bar, x)
        if d is UNDEFINED or d == 0:
            break

        i += 1
        if 2 * i > int(d):
            # Remaining f_bar has no factors of degree <= d/2 left to find,
            # so it must itself be irreducible.
            result.append((f_bar, int(d)))
            break

        h = polynomial_pow_mod(h, p, f, x, p)  # h = x^(p^i) mod f
        g = polynomial_gcd_mod_p(reduce_mod_p(h - x, x, p), f_bar, x, p)

        if g != 1:
            result.append((g, i))
            f_bar = polynomial_divide_mod_p(f_bar, g, x, p)[0]
            h = polynomial_divide_mod_p(h, f_bar, x, p)[1] if f_bar != 1 else h

    return result

def equal_degree_factorization(g: Expression, d: int, x: Variable, p: int) -> list[Expression]:
    """Given g, a monic product of irreducible factors all of degree d mod p,
    returns the complete list of those irreducible factors.

    Args:
        g (Expression): Monic polynomial, product of same-degree irreducibles
        d (int): The common degree of g's irreducible factors
        x (Variable): Polynomial variable
        p (int): An odd prime modulus

    Returns:
        list[Expression]: The individual monic irreducible factors of g
    """
    n = degree(g, x)
    if n is UNDEFINED or n == 0:
        return []
    n = int(n)

    if n == d:
        return [g]

    factor = None
    while factor is None:
        factor = _edf_split_attempt(g, d, x, p)

    cofactor = polynomial_divide_mod_p(g, factor, x, p)[0]
    return equal_degree_factorization(factor, d, x, p) + equal_degree_factorization(cofactor, d, x, p)

def factor_sqfree(u: Expression, x: Variable) -> list[Expression]:
    from .calculus_ops import derivative

    if u == 0:
        return [Integer(0)]
    u = algebraic_expand(u)

    c = leading_coefficient(u, x)
    U = algebraic_expand(u / c)

    R = polynomial_gcd(U, derivative(U, x), [x])
    F = polynomial_divide(U, R, [x])[0]

    factors = []
    j = 1
    while R != 1:
        G = polynomial_gcd(R, F, [x])
        s = polynomial_divide(F, G, [x])[0]
        if s != 1:
            factors.append(s**j)
        R = polynomial_divide(R, G, [x])[0]
        F = G
        j += 1

    if F != 1:
        factors.append(F**j)

    return [c] + factors
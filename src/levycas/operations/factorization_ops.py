"""Polynomial factorization routines (Yun's Algorithm, Hensel Lifting, et cetera"""
from itertools import combinations

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
    polynomial_content,
)
from .calculus_ops import derivative
from .numerical_ops import small_primes

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
    """Square-free factor for monic integer polynomials."""
    from .calculus_ops import derivative

    if u == 0:
        return [Integer(0)]
    u = algebraic_expand(u)

    c = polynomial_content(u, x, [])
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

def _choose_prime(f: Expression, x: Variable) -> int:
    """Select a small prime suitable for hensel lifting"""
    for p in small_primes():
        if p == 2: continue
        if leading_coefficient(f, x) % p == 0:
            continue
        fp = reduce_mod_p(f, x, p)

        if polynomial_gcd_mod_p(
            fp,
            reduce_mod_p(derivative(fp, x), x, p),
            x,
            p,
        ) == 1:
            return p

#####################################################################

def _product(exprs: list[Expression]) -> Expression:
    """Multiplies a list of expressions together."""
    result = Integer(1)
    for e in exprs:
        result = result * e
    return result

def _coefficient_list(f: Expression, x: Variable) -> list[Expression]:
    """Returns [a_n, a_{n-1}, ..., a_0], the coefficients of f as a
    polynomial in x, extracted via repeated leading-term stripping.
    """
    f = algebraic_expand(f)
    d = degree(f, x)
    if d is UNDEFINED or d is None:
        return [f]
    d = int(d)

    coeffs = []
    cur = f
    for i in range(d, -1, -1):
        cur_deg = degree(cur, x)
        if cur_deg is UNDEFINED or cur_deg is None or int(cur_deg) < i:
            coeffs.append(Integer(0))
            continue
        c = leading_coefficient(cur, x)
        coeffs.append(c)
        cur = algebraic_expand(cur - c * x**i)
    return coeffs

def _poly_2norm(f: Expression, x: Variable) -> int:
    """A safe (rounded up) integer upper bound on the Euclidean norm of f's
    coefficient vector.
    """
    from math import isqrt
    total = 0
    for c in _coefficient_list(f, x):
        ci = int(c)
        total += ci * ci
    return isqrt(total) + 1

def _hensel_precision(f: Expression, x: Variable, p: int) -> int:
    """Chooses k such that p^k comfortably exceeds twice a Landau-Mignotte
    bound on the coefficients of any integer factor of f, guaranteeing that
    every true factor is uniquely recoverable from its symmetric-range
    representative mod p^k.
    """
    n = int(degree(f, x))
    lc = abs(int(leading_coefficient(f, x)))
    norm = _poly_2norm(f, x)
    bound = 2 * (2**n) * max(lc, 1) * norm

    k, pk = 1, p
    while pk <= 2 * bound:
        pk *= p
        k += 1
    return k

def _symmetric_reduce(f: Expression, x: Variable, modulus: int) -> Expression:
    """Reduces every coefficient of f into the symmetric range
    (-modulus/2, modulus/2], for any (not necessarily prime) modulus.
    """
    coeffs = _coefficient_list(f, x)
    n = len(coeffs) - 1
    half = modulus // 2

    result = Integer(0)
    for i, c in enumerate(coeffs):
        deg_i = n - i
        ci = int(c) % modulus
        if ci > half:
            ci -= modulus
        if ci != 0:
            result = result + Integer(ci) * x**deg_i
    return algebraic_expand(result)

def _extended_gcd_mod_p(
    a: Expression, b: Expression, x: Variable, p: int
) -> tuple[Expression, Expression, Expression]:
    """Extended Euclidean algorithm mod p. Returns (gcd, s, t) with
    s*a + t*b = gcd (mod p). Does NOT normalize gcd to 1.
    """
    r0, r1 = reduce_mod_p(a, x, p), reduce_mod_p(b, x, p)
    s0, s1 = Integer(1), Integer(0)
    t0, t1 = Integer(0), Integer(1)

    while r1 != 0:
        q, r = polynomial_divide_mod_p(r0, r1, x, p)
        r0, r1 = r1, reduce_mod_p(r, x, p)
        s0, s1 = s1, reduce_mod_p(algebraic_expand(s0 - q * s1), x, p)
        t0, t1 = t1, reduce_mod_p(algebraic_expand(t0 - q * t1), x, p)

    return r0, s0, t0

def _bezout_mod_p(
    g0: Expression, h0: Expression, x: Variable, p: int
) -> tuple[Expression, Expression]:
    """Returns (s, t) with s*g0 + t*h0 = 1 (mod p), assuming g0, h0 coprime."""
    gcd_val, s, t = _extended_gcd_mod_p(g0, h0, x, p)
    inv = mod_inverse(int(gcd_val), p)
    s = reduce_mod_p(algebraic_expand(Integer(inv) * s), x, p)
    t = reduce_mod_p(algebraic_expand(Integer(inv) * t), x, p)
    return s, t

def hensel_step(
    f: Expression,
    g: Expression,
    h: Expression,
    g0: Expression,
    h0: Expression,
    s: Expression,
    t: Expression,
    x: Variable,
    p: int,
    p_power: int,
) -> tuple[Expression, Expression]:
    """Performs one Hensel lifting step, lifting a factorization f = g*h
    (mod p_power) to a factorization mod p_power*p.

    Uses fixed Bezout coefficients s, t (satisfying s*g0 + t*h0 = 1 mod p,
    where g0, h0 are the mod-p reductions of g, h) which remain valid at
    every precision level, so they only need to be computed once per split.

    Args:
        f (Expression): Exact target polynomial being factored
        g (Expression): Current approximation of one factor, correct mod p_power
        h (Expression): Current approximation of the other factor, correct mod p_power
        g0 (Expression): Mod-p reduction of g (fixed across all lifting steps)
        h0 (Expression): Mod-p reduction of h (fixed across all lifting steps)
        s (Expression): Bezout coefficient, s*g0 + t*h0 = 1 (mod p)
        t (Expression): Bezout coefficient, s*g0 + t*h0 = 1 (mod p)
        x (Variable): Polynomial variable
        p (int): Prime modulus
        p_power (int): Current precision (a power of p); f = g*h (mod p_power)

    Returns:
        tuple[Expression, Expression]: (g_new, h_new), correct mod p_power*p
    """
    e = algebraic_expand(f - g * h)
    e = algebraic_expand(e / Integer(p_power))
    e_bar = reduce_mod_p(e, x, p)

    te = reduce_mod_p(algebraic_expand(t * e_bar), x, p)
    q, delta_g = polynomial_divide_mod_p(te, g0, x, p)
    delta_h = reduce_mod_p(algebraic_expand(s * e_bar + q * h0), x, p)

    g_new = algebraic_expand(g + Integer(p_power) * delta_g)
    h_new = algebraic_expand(h + Integer(p_power) * delta_h)
    return g_new, h_new

def hensel_lift(
    f: Expression, factors: list[Expression], x: Variable, p: int
) -> list[Expression]:
    """Lifts a mod-p factorization of f into a p^k-adic factorization, with k
    chosen (via a Landau-Mignotte coefficient bound) large enough that every
    true integer factor of f can be recovered from its symmetric-range
    representative mod p^k by recombine_factors.

    Uses the classical leading-coefficient trick for non-monic f: f is
    scaled to f* = lc(f)^(r-1) * f, and each mod-p factor A_i is scaled to
    lc(f) * A_i, so that the (now consistent) product still matches f* mod p.
    The scaled factors are lifted together via a binary factor tree, using
    hensel_step at each split.

    Args:
        f (Expression): A primitive, squarefree polynomial over Z
        factors (list[Expression]): Its monic irreducible factors mod p, as
            returned by factor_mod_p (f = lc(f) * prod(factors) mod p)
        x (Variable): Polynomial variable
        p (int): The prime used for the mod-p factorization

    Returns:
        list[Expression]: Symmetric-range mod-p^k lifts of lc(f) * factors[i]
            (or, if factors has 0 or 1 elements, [f] itself)
    """
    r = len(factors)
    if r <= 1:
        return [f]

    lc = int(leading_coefficient(f, x))
    k = _hensel_precision(f, x, p)
    p_final = p**k

    scaled = [reduce_mod_p(algebraic_expand(Integer(lc) * fac), x, p) for fac in factors]

    def lift_subtree(target: Expression, leaves: list[Expression]) -> list[Expression]:
        if len(leaves) == 1:
            return [_symmetric_reduce(target, x, p_final)]

        mid = len(leaves) // 2
        left_leaves, right_leaves = leaves[:mid], leaves[mid:]

        g0 = reduce_mod_p(algebraic_expand(_product(left_leaves)), x, p)
        h0 = reduce_mod_p(algebraic_expand(_product(right_leaves)), x, p)
        s, t = _bezout_mod_p(g0, h0, x, p)

        g, h, p_power = g0, h0, p
        for _ in range(k - 1):
            g, h = hensel_step(target, g, h, g0, h0, s, t, x, p, p_power)
            p_power *= p

        return lift_subtree(g, left_leaves) + lift_subtree(h, right_leaves)

    f_star = algebraic_expand(Integer(lc) ** (r - 1) * f)
    return lift_subtree(f_star, scaled)

def recombine_factors(
    f: Expression,
    lifted_factors: list[Expression],
    x: Variable,
    p: int,
) -> list[Expression]:
    """Recovers the irreducible factors of f over Q from a p^k-adic lift of
    its mod-p factorization, via Zassenhaus's trial combination method:
    every subset of the lifted factors is multiplied together (scaled by the
    current cofactor's leading coefficient), reduced to symmetric range,
    stripped to a primitive part, and tested for exact division of the
    (shrinking) cofactor of f.

    Args:
        f (Expression): The original primitive, squarefree polynomial over Z
        lifted_factors (list[Expression]): Symmetric-range mod-p^k lifts of
            lc(f) times the true irreducible factors' mod-p images, as
            returned by hensel_lift
        x (Variable): Polynomial variable
        p (int): The prime used for lifting (the precision p^k is
            recomputed internally via the same bound hensel_lift used)

    Returns:
        list[Expression]: The irreducible integer factors of f (their
            product equals f exactly)
    """
    if len(lifted_factors) <= 1:
        return [f]

    k = _hensel_precision(f, x, p)
    p_power = p**k

    remaining_indices = list(range(len(lifted_factors)))
    current = f
    true_factors = []
    subset_size = 1

    while 2 * subset_size <= len(remaining_indices):
        found = False
        for subset in combinations(remaining_indices, subset_size):
            lc_current = leading_coefficient(current, x)
            candidate = Integer(int(lc_current))
            for i in subset:
                candidate = algebraic_expand(candidate * lifted_factors[i])
            candidate = _symmetric_reduce(candidate, x, p_power)

            content = polynomial_content(candidate, x, [])
            if content == 0:
                continue
            primitive_candidate = algebraic_expand(candidate / content)

            quotient, remainder = polynomial_divide(current, primitive_candidate, [x])
            if remainder == 0:
                true_factors.append(primitive_candidate)
                current = quotient
                remaining_indices = [i for i in remaining_indices if i not in subset]
                found = True
                break
        if not found:
            subset_size += 1

    if current != 1:
        true_factors.append(current)

    return true_factors

#####################################################################

def _factor_squarefree(
    f: Expression,
    x: Variable,
    multiplicity: int = 1,
) -> list[Expression]:
    """Factors a primitive squarefree polynomial over Q."""

    # Primitive/content decomposition
    content = polynomial_content(f, x, [])
    primitive = algebraic_expand(f / content)

    # Select a suitable lifting prime
    p = _choose_prime(primitive, x)

    # Factor over GF(p)
    mod_p_factors = factor_mod_p(primitive, x, p)

    # Lift factors modulo p^k
    lifted = hensel_lift(primitive, mod_p_factors, x, p)

    # Recover the rational factors
    rational = recombine_factors(
        primitive,
        lifted,
        x,
        p,
    )

    result = []

    if content != 1:
        result.append(content)

    for factor in rational:
        if multiplicity == 1:
            result.append(factor)
        else:
            result.append(factor**multiplicity)

    return result

def factor(f: Expression, x: Variable) -> list[Expression]:
    """Factors a univariate polynomial over the rationals.

    Returns:
        list[Expression]: A list of irreducible factors whose product is f.
            Constant factors are returned as the first element.
    """
    f = algebraic_expand(f)

    if f == 0:
        return [Integer(0)]

    if degree(f, x) <= 0 or degree(f, x) is None:
        return [f]

    content = polynomial_content(f, x, [])
    f = algebraic_expand(f / content)
    squarefree_parts = factor_sqfree(f, x)
    constant = squarefree_parts[0]
    result = [constant * content]

    for part in squarefree_parts[1:]:
        if isinstance(part, Power):
            base = part.base()
            multiplicity = int(part.exponent())
        else:
            base = part
            multiplicity = 1

        result.extend(_factor_squarefree(base, x, multiplicity))

    return result
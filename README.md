LevyCAS!!

This project is using the Setuptools backend.

I'm using a venv environment to help me develop this project.

# Examples:

### Integer Radical
``` python
>>> from levycas import factor_integer

>>> def rad(n: Integer) -> Integer:
>>>     rad, factors = 1, factor_integer(n).keys()
>>>     for factor in factors:
>>>         rad *= factor
>>>     return rad

>>> rad(18)
6
```

### Integer Operations
``` python
>>> from levycas import is_prime, factor_integer, gcd

>>> gcd(2**4 * 3**5 * 5**3, 7**4 * 11**4 * 13**5)
1

>>> factor_integer(2**4 * 3**5 * 5**3 * 7**9)
{2: 4, 3: 5, 5: 3, 7: 9}
```


### Symbolic Integration
``` python
>>> from levycas import Variable, integrate, Sin, Cos, Ln
>>> x = Variable("x")

>>> integrate(Sin(x) * Cos(x), x)
(-1 / 2) · (Cos(x) ^ 2)

>>> integrate(4*x**3 + 3*x**2 + 2*x + 1, x)
(x ^ 4) + (x ^ 3) + (x ^ 2) + x

>>> integrate(Ln(x), x)
(Ln(x) · x) - x
```

### Symbolic Derivatives
``` python
>>> from levycas import Variable, derivative, Cos, Ln
>>> x = Variable('x')

>>> derivative(-(1 / 2) * (Cos(x)**2), x)
Cos(x) · Sin(x)

>>> derivative(x**4 + x**3 + x**2 + x, x)
(4 · (x ^ 3)) + (3 · (x ^ 2)) + 2 · x + 1

>>> derivative(x * Ln(x) - x, x)
Ln(x)
```

### Partial Fractions and Rationalization
```python
>>> from levycas import Variable, rationalize
>>> from levycas import univariate_partial_fractions as partial
>>> x = Variable('x')

# (8x+7) / (x+2)(x-1) -> 3/(x+2) + 5/(x-1)
>>> partial(8*x + 7, x + 2, x - 1, x)
3, 5

# 3 / (x+2) + 5 / (x-1) -> (8x+7) / (x+2)(x-1)
>>> rationalize(3 / (x + 2) + 5 / (x - 1))
((x + -1) ^ -1) · ((x + 2) ^ -1) · (8x + 7)
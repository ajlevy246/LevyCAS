# Welcome to LevyCAS!

[![CI](https://github.com/ajlevy246/LevyCAS/actions/workflows/python-package.yml/badge.svg)](https://github.com/ajlevy246/LevyCAS/actions/workflows/python-package.yml)
[![codecov](https://codecov.io/gh/ajlevy246/LevyCAS/graph/badge.svg?token=MlatPlQxJ6)](https://codecov.io/gh/ajlevy246/LevyCAS)

**LevyCAS** is a lightweight symbolic computer algebra system (CAS) written in Python. It focuses on parsing natural mathematical expressions into symbolic objects and performing symbolic manipulation, calculus, simplification, and number-theoretic computations.

<img src="https://github.com/ajlevy246/LevyCAS/blob/main/assets/graph.png?raw=true" width=1000 alt="A screenshot of the LevyCAS graphing textual user interface. Expressions are entered on the left hand side, and an interactive graph is plotted on the right.">

<br/> 

LevyCAS began as an educational project, exploring symbolic computation, expression trees, Pratt parsing, grammars, and terminal UIs. It's designed to combine the best of existing computational tools that I regularly use: Desmos, sympy, and Matlab. 

## Features
- Parse natural mathematical expressions
- Symbolic differentiation
- Symbolic integration
- Expression simplification
- Integer factorization and number-theoretic operations
- Rationalization and partial fractions
- Interactive Textual-based graphing & scripting interface
- Python core w/ no required dependencies 

<br/>

# Installation & Quick Start:

While the base package has no dependencies, it is designed for Python3.10+

## Core package & CLI
LevyCAS is uploaded as a Python package on the TestPyPi index [here](https://test.pypi.org/project/levycas/). Install with pip:

```bash
python3 -m pip install levycas --index-url https://test.pypi.org/simple/ 
```

Then, get started by launching python and running:
```python
from levycas import symbols, parse, derivative, integrate

x, y = symbols("x y")
expr = parse("sin(x)cos(y)")
print(expr)

print(derivative(expr, x))
print(integrate(expr, x))
```

Or through the command-line interface:
```bash
$ levycas integrate "xsin(x^2)"
```

## Terminal-Based TUI
To use the textual user interface, install with the `tui` extra. This extra depends on the [`Textual`](https://textual.textualize.io/) library, as well as the `textual-plot` package.

```bash
python3 -m pip install levycas[tui] --extra-index-url https://test.pypi.org/simple/ 
```

Launch the TUI directly in your terminal:

```bash
$ levycas
```

Or jump straight to the graphing interface:

```bash
$ levycas graph "sin(x)" "x^2" "lnx" "exp(x)"
```

<br/>

# Textual User Interface

By default, installing the `tui` extra adds the `levycas` script to PATH. Launch the powerful interface to write scripts or plot expressions:

<img src="https://github.com/ajlevy246/LevyCAS/blob/main/assets/script.png?raw=true" width=1000 alt="A screenshot of the LevyCAS scripting textual user interface. A script is entered on the left hand side, while output is printed on the right.">

<br/>

# Project Structure

The base package consists of a set of core expression objects, along with a set of routines acting on them.

In addition, LevyCAS includes a native Pratt parser capable of interpreting natural mathematical syntax such as `sin(x)cosx`, `1/2x`, and `3ln(x^2)` into symbolic expression trees.

### [`src/levycas/`](./src/levycas/__init__.py)
- [`expressions/`](./src/levycas/expressions/__init__.py): Defines the symbolic expression tree classes used through LevyCAS. These classes make extensive use of Python's operator overloading and inheritance to provide a simple interface.

- [`operations/`](./src/levycas/operations/__init__.py): The routines consist of both the fundamental simplification operations (`simplify`, `sym_eval`), as well as useful symbolic computations like `derivative` and `integrate`. 

- [`parser/`](./src/levycas/parser/__init__.py): All of the Pratt parsing logic is contained here. Lexing converts and input string into tokens, and the parsing logic converts it to native objects.

- [`cli/`](./src/levycas/cli/__init__.py): All of the logic for the textual user interface is contained here. This submodule does not expose any external routines, but the scripts here may be interesting to those building simple Textual apps themselves.

<br/>

# Examples:

### Parse
```python
>>> from levycas import parse

# implicit multiplication & function args
>>> parse("1/2sin(x)cosx")
(1/2)Sin(x)Cos(x)

# symbol generation
>>> parse("ax^2 + bx + c")
ax² + bx + c

# automatic simplification/normalization
>>> parse("2(x+3) - x - 6y/y")
x
```

### Polynomial Factoring
```python
>>> from levycas import Variable, factor
>>> x = Variable("x")

# repeated irreducible factors
>>> factor(x**8 + 2*x**6 - 6*x**5 - 12*x**3 + 9*x**2 + 18, x)
[1, x² + 2, (x³ - 3)^2]

# generalized polynomial variables
>>> factor(4*Ln(x)**2 + 10*Ln(x) + 6, Ln(x))
[2, Ln(x) + 1, 2Ln(x) + 3]
```

### Symbolic Integration
```python
>>> from levycas.expressions import Variable, Sin, Cos, Ln,
>>> from levycas.operations  import integrate, collect_terms
>>> x = Variable("x")

# u-substitution
>>> integrate(x*Sin(x**2), x)
-(1/2)(Cos(x)^2)

# partial fractions via Hermite reduction
>>> integrate(1 / ((x**2+1)*(x-2)), x)
-(1/10)Ln(x² + 1) + (1/5)Ln(x - 2) - (2/5)Arctan(x)

# integration by parts
>>> integrate(x**3 * Exp(x), x)
>>> collect_terms(_, Exp(x))
(x³ - 3x² + 6x - 6)Exp(x)
```

### Symbolic Derivatives
```python
>>> from levycas.expression import Variable, Cos, Ln
>>> from levycas.operations import derivative, trig_simplify
>>> x = Variable('x')

>>> derivative(x**4 + x**3 + x**2 + x, x)
1 + 2x + 3x² + 4x³

>>> derivative((Cos(x)+Sin(x))**2,  x)
>>> trig_simplify(_)
2Cos(2x)

>>> derivative(x*Ln(x) - x, x)
Ln(x)
```

### Algebraic Operations
```python
>>> from levycas.expressions import Variable
>>> from levycas.operations import rationalize, partial_fractions as partial
>>> x = Variable('x')

# partial fractions
>>> partial(8*x+7, [x+2, x-1], x)
3/(x+2) + 5/(x-1)

# rationalization
>>> rationalize(3/(x+2) + 5/(x-1))
(8x+7)/((x+2)*(x-1))
```

### Integer Operations
```python
>>> from levycas import is_prime, factor_integer, gcd

>>> gcd(2**4 * 3**5 * 5**3, 7**4 * 11**4 * 13**5)
1

>>> factor_integer(2**4 * 3**5 * 5**3 * 7**9)
{2: 4, 3: 5, 5: 3, 7: 9}

# integer radical
>>> def rad(n: Integer) -> Integer:
>>>     rad, factors = 1, factor_integer(n).keys()
>>>     for factor in factors:
>>>         rad *= factor
>>>     return rad

>>> rad(18)
6
```


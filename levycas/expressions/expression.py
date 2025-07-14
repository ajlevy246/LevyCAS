"""Classes for internal representations of mathematical expressions"""
from math import lcm, comb, factorial
from numbers import Number

#TODO: Change the simplify operation to return a new expression, instead of altering in place??
#perhaps make it a static function under Expression

#TODO: Rethink function implementation! Not too late!!
#Do this before implementing derivative operator on page 182 of Elementary Algorithms
#also, implement natural logarithm first! TEST DERIVATIVE IMPLEMENTATION 
#Example: (x ** 2).derivative(y) -> fails
#Implement derivative operator to simplify automatically?

#TODO: Deal with **symbols dictionary. It should ideally be global
#to avoid conflicts with the simplify function

#TODO: Deal with redefinition of functions.
# Recursion works (correctly raises error), but now we should store functions
# in the symbol table differently, or copy them over differently
# no need to copy the definition over, if the sym_eval will just 
# get the global definition first 

#TODO: Make note of the following behavior:
#1: f(x) = x
#2: x = 2
#3: f(x) -> 2, but intended would be: f(x) -> x
#No way to avoid overwriting parameters? Except manually when parsing.
#Causes the following error:
#1: f(x, y) = x + y
#2: f(0, x) -> 0 (incorrect), the names of the param args shouldn't matter.
#Possible solution, change the internal representations of the parameters
#in a function definition so that they don't matter?
#NOTE: More complicated, consider:
#1: f(x) = x
#2: g(x) = f(x)
#3: g(1) -> Should return 1

#TODO: Deal with errors in the following:
#1: f(x) = x
#2: g(y) = y
#3: simplify f(x) + g(y) -> Error??

#TODO: Parse error? 
#1: g(x, y) = g(0, 0) + g(0, 1)
#"None is not a valid function definition"

"""Undefined flyweight; default value for expressions that can not be evaluated
"""
UNDEFINED = "UNDEFINED" 

"""Minimumn threshold used to determine if a float is an integer"""
MIN_ERROR = 10 ** -30

#============ OPERATIONS ===============

class CAS_ENV:
    """An environment class that specifies a symbol and function table"""
    def __init__(self):

        #A dictionary of symbols and their definitions.
        self.symbols = dict()

class Expression:
    """An Expression is a general mathematical object.
    In this case, it is used to represent binary operations
    """
    def __init__(self, *args):
        assert len(args) == 2
        self.left = args[0]
        self.right = args[1]

    """The following four methods allow us to treat arbitrary expressions as powers/products/rationals. 
    This is useful for automatic simplification and total ordering of expressions.
    """
    def base(self):
        return self

    def exponent(self):
        return Integer(1)

    def coefficient(self):
        return Integer(1)

    def term(self):
        return Product(self)

    def num(self):
        return self

    def denom(self):
        return Integer(1)

    """The following dunder methods allow us to treat python statements as AST's"""
    def __eq__(self, other):
        """Check if two expressions are syntactically equal. For this to make sense, 
        both expressions should be ASAE (Automatically-Simplified Arithmetic Expressions)."""

        return str(self) == str(other)

    def __hash__(self):
        return hash(str(self))

    def __gt__(self, other):
        return not (self < other)

    def __add__(self, other):
        from ..operations import simplify_sum
        other = convert_primitive(other)
        return simplify_sum(Sum(self, other)) if isinstance(other, Expression) else NotImplemented

    def __sub__(self, other):
        from ..operations import simplify_sum
        other = convert_primitive(other)
        return self + -1 * other if isinstance(other, Expression) else NotImplemented

    def __neg__(self):
        return -1 * self

    def __mul__(self, other):
        from ..operations import simplify_product
        other = convert_primitive(other)
        return simplify_product(Product(self, other)) if isinstance(other, Expression) else NotImplemented

    def __truediv__(self, other):
        other = convert_primitive(other)
        if other == 0:
            raise ZeroDivisionError
        return (self * other ** -1) if isinstance(other, Expression) else NotImplemented

    def __pow__(self, other):
        from ..operations import simplify_power
        other = convert_primitive(other)
        return simplify_power(Power(self, other)) if isinstance(other, Expression) else NotImplemented

    """Right hand dunder methods for treating ints as Integers"""
    def __radd__(self, other):
        other = convert_primitive(other)
        return (other + self) if isinstance(other, Expression) else NotImplemented

    def __rsub__(self, other):
        other = convert_primitive(other)
        return (other - self) if isinstance(other, Expression) else NotImplemented

    def __rmul__(self, other):
        other = convert_primitive(other)
        return (other * self) if isinstance(other, Expression) else NotImplemented

    def __rtruediv__(self, other):
        if self == 0:
            raise ZeroDivisionError
        other = convert_primitive(other)
        return (other * self ** -1) if isinstance(other, Expression) else NotImplemented

    def __rpow__(self, other):
        other = convert_primitive(other)
        return (other ** self) if isinstance(other, Expression) else NotImplemented
    
    def __rmod__(self, other):
        other = convert_primitive(other)
        return (other % self) if isinstance(other, Expression) else NotImplemented

class Sum(Expression):
    """A Sum is the sum of two terms"""
    def __init__(self, *terms):
        self.terms = list(terms)
        
    def __repr__(self):
        term_repr = [str(term) for term in self.terms[::-1]]
        return "(" + " + ".join(term_repr) + ")"
    
    def __lt__(self, other):
        """Total ordering for Sums: O-3"""
        if isinstance(other, Sum):
            #O-3 (1 & 2) Compare terms from most significant (last term) to least.
            num_left = len(self.terms)
            num_right = len(other.terms)
            min_length = min(num_left, num_right)
            for i in range(-1, -min_length - 1, -1):
                if self.terms[i] == other.terms[i]:
                    continue
                return self.terms[i] < other.terms[i]
            
            #O-3 (2) If all terms are equal, compare number of terms
            return num_left < num_right
        
        if isinstance(other, Expression) and not isinstance(other, Constant) and not isinstance(other, Power):
            #O-10 (Unary Sum)
            return self < Sum(other)
        
        return NotImplemented
    
    def __add__(self, other):
        #Overrides parent method to denest the addition of two sums
        #example: x + y + z should be Sum(x, y, z), not Sum(Sum(x, y), z)
        if isinstance(other, Sum):
            from ..operations import simplify_sum
            new_terms = self.terms + other.operands()
            return simplify_sum(Sum(*new_terms))

        return super().__add__(other)
        
    def operands(self):
        return self.terms

class Product(Expression):
    """A Product is the product of two factors"""
    def __init__(self, *factors):
        self.factors = list(factors)

    def __repr__(self):
        if len(self.factors) == 2 and isinstance(self.factors[0], Integer) and isinstance(self.factors[1], Variable):
            if self.factors[0] == -1:
                return "-" + str(self.factors[1])
            return f"{self.factors[0]}{self.factors[1]}" #Implicit multiplication is easier on the eyes
        
        factor_repr = [str(factor) for factor in self.factors]
        return "(" + " \u00B7 ".join(factor_repr) + ")" #\u00b7 -> \cdot
    
    def __lt__(self, other):
        """Total ordering for Products: O-3"""
        if isinstance(other, Product):
            #O-3 (1 & 2) Compare factors from most significant (last factor) to least.
            num_left = len(self.factors)
            num_right = len(other.factors)
            min_length = min(num_left, num_right)
            for i in range(-1, -min_length -1, -1):
                if self.factors[i] == other.factors[i]:
                    continue
                return self.factors[i] < other.factors[i]
            
            #O-3 (2) If all terms are equal, compare number of terms
            return num_left < num_right
        
        if isinstance(other, Expression) and not isinstance(other, Constant):
            #Rule O-8; test against unary product
            return self < Product(other)

        return NotImplemented

    def operands(self):
        return self.factors
    
    def coefficient(self):
        return self.factors[0] if isinstance(self.factors[0], Constant) else Integer(1)
    
    def term(self):
        return Product(*self.factors[1::]) if isinstance(self.factors[0], Constant) else self
    
    def num(self):
        first_factor = self.factors[0]
        return first_factor.num() * (self / first_factor).num()
    
    def denom(self):
        first_factor = self.factors[0]
        return first_factor.denom() * (self / first_factor).denom()

    def __mul__(self, other):
        if isinstance(other, Product):
            from ..operations import simplify_product
            new_factors = self.factors + other.operands()
            return simplify_product(Product(*new_factors))
        return super().__mul__(other)

class Div(Expression):
    """A Div represents the quotient of two terms. 
    If both terms are integers, it is simplified to a rational number."""
    def __repr__(self):
        return f"({self.left} / {self.right})"

    def operands(self):
        return [self.left, self.right]
    
    def num(self):
        return self.left
    
    def denom(self):
        return self.right

class Power(Expression):
    """A Power represents exponentiation"""
    def __repr__(self):
        return f"({self.left} ^ {self.right})"
    
    def __lt__(self, other):       
        if isinstance(other, Expression) and not isinstance(other, Product):
            if self.base() == other.base():
                return self.exponent() < other.exponent()
            return self.base() < other.base()
        return NotImplemented

    def base(self):
        return self.left
    
    def exponent(self):
        return self.right 
    
    def operands(self):
        return [self.left, self.right]
    
    def num(self):
        if isinstance(self.right, Constant) and self.right.eval() < 0:
            return Integer(1)
        else:
            return self
        
    def denom(self):
        if isinstance(self.right, Constant) and self.right.eval() < 0:
            return self.left ** (-1 * self.right)
        else:
            return Integer(1)

class Factorial(Expression):
    """A Factorial represents the factorial of a number"""
    def __init__(self, value: Expression):
        """Create a new Factorial object"""
        self.value = value

    def __repr__(self):
        return f"({self.value}!)"
    
    def __lt__(self, other):
        if isinstance(other, Factorial):
            return self.value < other.value

        if isinstance(other, Variable):
            if self.value == other:
                return False
            return self < Factorial(other)

        if isinstance(other, Elementary):
            if self.value == other:
                return False
            return self < Factorial(other)

        return NotImplemented

    def operands(self):
        return [self.value]

class Special(Expression):
    """Special represents special cases"""

    def __init__(self):
        raise NotImplementedError("Special cases not yet implemented")
    
    def __repr__(self):
        raise NotImplementedError("Special cases not yet implemented") 

#=============== SYMBOLS ===============

class Variable(Expression):
    """A Variable represents a variable"""

    def __init__(self, name: str):
        """Create a new Variable object"""
        self.name = name

    def __repr__(self) -> str:
        """Return the name of the variable"""
        return self.name
    
    def __lt__(self, other):
        """Total ordering for Variables: O-2"""
        if isinstance(other, Variable):
            return self.name < other.name
        return NotImplemented
    
    def operands(self):
        return [self.name]

class Elementary(Expression):
    """Core elementary functions include the exponential functions, logarithm and exponential, trigonometric and 
    inverse trigonometric functions, and hyperbolic/inverse hyperbolic functions."""

    def __init__(self, *args):
        self.args = args

    def operands(self):
        return self.args

    def __lt__(self, other):
        self_kind = type(self).__name__
        other_kind = type(other).__name__
        if isinstance(other, Elementary):

            if self_kind == other_kind:
                self_args = self.args
                other_args = other.args
                for i in range(len(self_args)):
                    if self_args[i] == other_args[i]:
                        continue
                    return self_args[i] < other_args[i]
            return self_kind < other_kind
        
        elif isinstance(other, Variable):
            if self_kind == other:
                return False
            return self_kind < other.name

        return NotImplemented

    def __repr__(self):
        args_repr = "(" + ", ".join([str(arg) for arg in self.args]) + ")"
        return type(self).__name__ + args_repr

class Function(Expression):
    def __init__(self, name):
        self.name = name
        self.args = None
        self.parameters = None
        self.definition = None

    def add_args(self, *arguments, **symbols):
        self.args = list(arguments)
        assert len(self.args) == len(self.parameters), f"Number of arguments does not match number of parameters for {self}"

    def set_parameters(self, *parameters: list[Variable]):
        assert Variable(self.name) not in parameters, f"Function {self.name} cannot depend on itself"
        self.parameters = parameters

    def set_definition(self, definition: Expression):
        self.definition = definition

    def sym_eval(self, **symbols):
        if not self.args:
            return self
        
        for i in range(len(self.parameters)):
            param = str(self.parameters[i])
            param_def = self.args[i].sym_eval(**symbols)
            symbols[param] = param_def
        
        definition = symbols.get(self.name, None).definition
        assert definition is not None, f"Function {self.name} was cleared?"
        return definition.sym_eval(**symbols)

    def __repr__(self):
        if self.args:
            args_repr = [str(arg) for arg in self.args]
            return f"{self.name}({', '.join(args_repr)})"
        if self.definition:
            return f"{self.definition}"
        if self.definition:
            return f"{self.name}({', '.join(self.parameters)})"
        return f"Function({self.name})"

    def __lt__(self, other):
        if isinstance(other, Function):
            if self.name < other.name:
                return True
            
            num_left = len(self.args)
            num_right = len(other.args)
            min_num = min(num_left, num_right)
            for i in range(min_num):
                if self.factors[i] == other.factors[i]:
                    continue
                return self.factors[i] < other.factors[i]
            
            #O-3 (2) If all terms are equal, compare number of terms
            return num_left < num_right
        
        return NotImplemented
    
    def copy(self):
        copied = Function(self.name)
        copied.set_definition(self.definition.copy())
        copied.set_parameters(self.parameters) #Parameters not copied.
        if self.args:
            copied.add_args(*self.args)
        return copied
    
    def operands(self):
        if self.definition:
            return [self.definition]
        return 

#=============== CONSTANTS ===============

class Constant(Expression):
    """A Constant represents a constant value"""

    def coefficient(self):
        return self
    
    def term(self):
        return Integer(1)

    def __lt__(self, other):
        """Total ordering for Constants: O-1"""
        if isinstance(other, Constant):
            return self.eval() < other.eval()
        
        if isinstance(other, Expression):
            return True
        
        return self.eval() < other

    def __add__(self, other):
        other = convert_primitive(other)
        if not isinstance(other, Constant):
            return super().__add__(other)
        
        denom_lcm = lcm(self.denom(), other.denom())
        left_num = self.num() * denom_lcm // self.denom()
        right_num = other.num() * denom_lcm // other.denom()
        new_num = left_num + right_num
        return Rational(new_num, denom_lcm)

    def __sub__(self, other):
        other = convert_primitive(other)
        if not isinstance(other, Constant):
            return super().__sub__(other)

        denom_lcm = lcm(self.denom(), other.denom())
        left_num = self.num() * denom_lcm // self.denom()
        right_num = other.num() * denom_lcm // other.denom()
        new_num = left_num - right_num
        return Rational(new_num, denom_lcm)

    def __mul__(self, other):
        other = convert_primitive(other)
        if not isinstance(other, Constant):
            return super().__mul__(other)

        new_num = self.num() * other.num()
        new_denom = self.denom() * other.denom()
        return Rational(new_num, new_denom)
    
    def __abs__(self):
        if self == 0 or self.is_positive():
            return self
        return -self

    def __floordiv__(self, other):
        other = convert_primitive(other)
        if not isinstance(other, Constant):
            return NotImplemented
        
        div = self / other
        return Integer(div.num() // div.denom())

    def __rfloordiv__(self, other):
        other = convert_primitive(other)
        if not isinstance(other, Constant):
            return NotImplemented
        return other // self

    def __mod__(self, other):
        other = convert_primitive(other)
        if not isinstance(other, Constant):
            return NotImplemented
        return (self - other * (self // other))

class Rational(Constant):
    """A rational expression is a constant; a fraction of two integers"""

    def __new__(cls, *args):
        """To faciliatate automatic simplification of Rational expression,
        the __new__ method is overwritten.
        
        First, a new Rational instance is created. Then, the _factory method is called,
        which returns a simplified Rational object.
        """
        if len(args) == 1:
            args = [args[0], 1]

        new_instance = super().__new__(cls)
        n = int(args[0])
        d = int(args[1])

        #Simplify to lowest terms
        if d == 0:
            return UNDEFINED

        if n % d == 0:
            return Integer(n // d)

        from ..operations import gcd
        g = int(gcd(n, d))
        if  d > 0:
            new_instance.left = n // g
            new_instance.right = d // g

        else:
            new_instance.left = -n // g
            new_instance.right = -d // g

        return new_instance

    def __init__(self, *args):
        """The __new__ function is responsible for automatic simplification
        no mutation is done here.
        """
        pass

    def __repr__(self):
        return f"({self.left} / {self.right})"

    def __eq__(self, other):
        if isinstance(other, Number):
            return super().__eq__(convert_primitive(other))
        return super().__eq__(other)

    def __hash__(self):
        return super().__hash__()

    def __pow__(self, other):
        other = convert_primitive(other)
        if not isinstance(other, Expression):
            return NotImplemented
        if not isinstance(other, Constant):
            return super().__pow__(other)
        
        if isinstance(other, Integer):
            if other == 0:
                return Integer(1)
            elif other.is_negative():
                nexpt = -other
                if nexpt == 1:
                    return Rational(self.denom(), self.num())
                if self.is_negative():
                    return (-1)**other * (-Rational())**nexpt
                else:
                    return Rational(self.denom(), self.num())**nexpt
            else:
                return Rational(self.num() ** other.eval(), self.denom() ** other.eval())

        assert isinstance(other, Rational), f"{other} is not Rational exponent?"
        #Algorithm adapted from sympy, see: https://github.com/sympy/sympy/blob/master/sympy/core/numbers.py#L1570

        bp, bq = self.num(), self.denom()
        ep, eq = other.num(), other.denom()

        intpart = ep // eq
        if intpart:
            intpart += 1
            remfracpart = intpart * eq - ep
            ratfracpart = Rational(remfracpart, eq)
            if bp != 1:
                return Integer(bp)**other * Integer(bq) ** ratfracpart * Rational(1, bp**intpart)
            return Integer(bq)**ratfracpart * Rational(1, bq**intpart)
        else:
            remfracpart = eq - ep
            ratfracpart = Rational(remfracpart, eq)
            if bp != 1:
                return Integer(bp)**other * Integer(bq) ** ratfracpart * Rational(1, bq)
            return Integer(bq)**ratfracpart * Rational(1, bq)

    def eval(self):
        return self.left / self.right

    def is_positive(self):
        return (self.left < 0) if (self.right < 0) else (self.left > 0)

    def is_negative(self):
        return (self.left < 0) if (self.right > 0) else (self.left > 0)

    def operands(self):
        return [self.left, self.right]

    def num(self):
        return self.left

    def denom(self):
        return self.right

class Integer(Constant):
    """An Integer represents a decimal integer"""

    def __init__(self, value: int):
        """Creates a new Integer object"""
        self.value = value

    def __repr__(self):
        """Returns the value of the integer"""
        return str(self.value)

    def __hash__(self):
        return hash(self.eval())

    def __pow__(self, other, mod=None):
        other = convert_primitive(other)
        if not isinstance(other, Expression):
            return NotImplemented

        if not isinstance(other, Constant):
            return super().__pow__(other)
        
        if mod is not None:
            mod = convert_primitive(mod)
            if not isinstance(other, Integer) or not isinstance(mod, Integer):
                raise ValueError(f"{mod=} is not a supported modulus for {self} ^ {other}")
            return pow(int(self), int(other), int(mod))

        if self == 1 or other == 0:
            return Integer(1)

        if other.is_negative():
            nexpt = -other
            if self.is_negative():
                return (-1)**int(other) * Rational(1, -self.value) ** nexpt
            return Rational(1, self.value) ** nexpt
        
        if isinstance(other, Integer):
            return Integer(self.value ** int(other))

        assert isinstance(other, Rational), f"{other} is not Rational exponent?"
        ep, eq = other.num(), other.denom()
        nthroot = abs(self.value) ** (1 / eq)
        if abs(nthroot - int(nthroot)) < MIN_ERROR:
            result = Integer(int(nthroot) ** abs(ep))
            if self.is_negative():
                #result *= (-1) ** other 
                raise ValueError(f"Could not compute {self} ** {other}, imaginary numbers not yet supported")
            return result
        
        #The following simplification algorithm is adapted from sympy
        #It converts rational powers b^(p / q) -> a * sqrt(b) * c^(r / s)
        #See: https://github.com/sympy/sympy/blob/master/sympy/core/numbers.py#L2078
        from ..operations import factor_integer, gcd
        factors = factor_integer(abs(self))
        out_int, out_rad = 1, 1
        sqr_dict = dict()

        #Remove multiples of q
        for prime, exponent in factors.items():
            exponent *= ep
            quot, rem = divmod(exponent, eq)
            if quot > 0:
                out_int *= prime ** quot
            if rem > 0:
                g = gcd(rem, eq)
                if g != 1:
                    out_rad *= prime ** Rational(rem // g, eq // g)
                else:
                    sqr_dict[prime] = rem
        
        sqr_int, sqr_gcd = 1, 0
        #Calculate gcd of remaining powers
        for prime, exponent in sqr_dict.items():
            sqr_gcd = gcd(sqr_gcd, exponent)
            if sqr_gcd == 1:
                break
            sqr_gcd = int(sqr_gcd)

        #Calculate remainder
        for prime, exponent in sqr_dict.items():
            sqr_int *= prime ** (exponent // sqr_gcd)
        if sqr_int == abs(self) and out_int == 1 and out_rad == 1:
            #No simplification could be performed
            return Power(self, other)

        result = out_int * out_rad * (sqr_int ** Rational(sqr_gcd, eq))
        if self.is_negative():
            result *= (-1) ** other
        return result

    def eval(self):
        return self.value

    def is_positive(self):
        return self.value > 0
    
    def is_negative(self):
        return self.value < 0

    def is_even(self):
        return not self.value % 2

    def operands(self):
        return [self.value]

    def __int__(self):
        return self.value

    def num(self):
        return self.value

    def denom(self):
        return 1

    def __index__(self):
        return self.value
    
    def __mod__(self, other):
        other = convert_primitive(other)
        if not isinstance(other, Integer):
            return super().__mod__(other)
        return Integer(self.eval() % other.eval())

#============== METHODS =================

def convert_primitive(num: Number) -> Constant:
    """Converts a python number to a levycas Constant in lowest terms.

    Args:
        num (Number): A primitive number

    Returns:
        Constant: The boxed number
    """
    if num is UNDEFINED:
        return UNDEFINED

    if isinstance(num, Expression):
        return num

    if isinstance(num, int):
        return Integer(num)
    
    if isinstance(num, float):
        num = str(num)

    try:
        number = num.split(".")
        if len(number) == 1:
            return Integer(int(num))
        else:
            assert len(number) == 2, f"Failed to parse number {num}"
            whole, partial = number
            denominator = 10 ** len(partial)
            numerator = int(whole + partial)
            if denominator == 1:
                return Integer(numerator)
            else:
                return Rational(numerator, denominator)
    except:
        raise ValueError(f"Could not convert {num} to Rational.")
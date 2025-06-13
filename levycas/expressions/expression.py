"""Classes for internal representations of mathematical expressions"""
from math import gcd, lcm, comb, factorial
from numbers import Number

#TODO: Infinite recursion issue:
#1: Integer(1) / 1

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

#TODO: Fix algebraic expand: Elementary Algorithms page 253
#Use example: (x + 1)(x + 2) -> (x^2) + (3*x) + 2


"""Undefined flyweight; default value for expressions that can not be evaluated
"""
UNDEFINED = "UNDEFINED" 

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
        #This method is called as the "inverse" of the lt method
        #i.e: if (a < b) returns NotImplemented, this ensures that
        # (not b < a) is returned
        if isinstance(other, Expression):
            return not (self < other)
        else:
            return NotImplemented
    
    def __add__(self, other):
        from ..operations import simplify
        other = convert_primitive(other)
        return simplify(Sum(self, other)) if isinstance(other, Expression) else NotImplemented

    def __sub__(self, other):
        from ..operations import simplify
        other = convert_primitive(other)
        return simplify(Sum(self, Product(Integer(-1), other))) if isinstance(other, Expression) else NotImplemented

    def __neg__(self):
        from ..operations import simplify
        return simplify(Product(Integer(-1), self))

    def __mul__(self, other):
        from ..operations import simplify
        other = convert_primitive(other)
        return simplify(Product(self, other)) if isinstance(other, Expression) else NotImplemented

    def __truediv__(self, other):
        from ..operations import simplify
        other = convert_primitive(other)
        if other == 0:
            raise ZeroDivisionError
        return (self * other ** -1) if isinstance(other, Expression) else NotImplemented

    def __pow__(self, other):
        from ..operations import simplify
        other = convert_primitive(other)
        return simplify(Power(self, other)) if isinstance(other, Expression) else NotImplemented
    
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

class Sum(Expression):
    """A Sum is the sum of two terms"""
    def __init__(self, *terms):
        self.terms = list(terms)
        
    def __repr__(self):
        term_repr = [str(term) for term in self.terms]
        return "(" + " + ".join(term_repr) + ")"
    
    def __lt__(self, other):
        """Total ordering for Sums: O-3"""
        if isinstance(other, Sum):
            #O-3 (1 & 2) Compare terms from most significant (last term) to least.
            num_left = len(self.terms)
            num_right = len(other.terms)
            min_length = min(num_left, num_right)
            for i in range(min_length - 1, -1, -1):
                if self.terms[i] == other.terms[i]:
                    continue
                return self.terms[i] < other.terms[i]
            
            #O-3 (2) If all terms are equal, compare number of terms
            return num_left < num_right
        
        if isinstance(other, Expression) and not isinstance(other, Constant) and not isinstance(other, Power):
            #O-10 (Unary Sum)
            test_other = Sum(other)
            return self < test_other
        
        return NotImplemented
    
    def __add__(self, other):
        #Overrides parent method to denest the addition of two sums
        #example: x + y + z should be Sum(x, y, z), not Sum(Sum(x, y), z)
        if isinstance(other, Sum):
            from ..operations import simplify
            self.terms += other.operands()
            return simplify(self)

        return super().__add__(other)
        
    def operands(self):
        return self.terms

class Product(Expression):
    """A Product is the product of two factors"""
    def __init__(self, *factors):
        self.factors = list(factors)

    def __repr__(self):
        # if len(self.factors) == 2 and isinstance(self.factors[0], Integer) and isinstance(self.factors[1], Variable):
        #     return f"{self.factors[0]}{self.factors[1]}" #Implicit multiplication is easier on the eyes
        
        factor_repr = [str(factor) for factor in self.factors]
        return "(" + " \u00B7 ".join(factor_repr) + ")" #\u00b7 -> \cdot
    
    def __lt__(self, other):
        """Total ordering for Products: O-3"""
        if isinstance(other, Product):
            #O-3 (1 & 2) Compare factors from most significant (last factor) to least.
            num_left = len(self.factors)
            num_right = len(other.factors)
            min_length = min(num_left, num_right)
            for i in range(min_length - 1, -1, -1):
                if self.factors[i] == other.factors[i]:
                    continue
                return self.factors[i] < other.factors[i]
            
            #O-3 (2) If all terms are equal, compare number of terms
            return num_left < num_right
        
        if isinstance(other, Expression) and not isinstance(other, Constant):
            #Rule O-8; test against unary product
            test_other = Product(other)
            return self < test_other

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

    # def num(self):
    #     first_factor = self.factors[0]
    #     remaining = self.factors[1::]
    #     if len(remaining) == 0:
    #         return first_factor.num()
    #     else:
    #         return first_factor.num() * Product(*remaining).num()

    def __mul__(self, other):
        if isinstance(other, Product):
            from ..operations import simplify
            self.factors += other.operands()
            return simplify(self)
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
        if isinstance(other, Expression):
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
            return self.value < other
        return NotImplemented

    def operands(self):
        return [self.value]

class Derivative(Expression):
    """The anonymous derivative operator will be used when other derivative rules fail
    See DERIV-7, page 183 Elementary Algorithms
    """
    def __init__(self, *args):
        self.operands = args

    def __repr__(self):
        return f"Derivative({self.name})"

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

class Function(Expression):
    def __init__(self, name):
        print(f"Creating function?? {name}")
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

    def __lt__(self, other):
        """Total ordering for Constants: O-1"""
        if isinstance(other, Constant):
            return self.eval() < other.eval()
        
        if isinstance(other, Expression):
            return True
        
        return NotImplemented
    
    def __add__(self, other):
        other = convert_primitive(other)
        if not isinstance(other, Constant):
            return super().__add__(other)
        
        denom_lcm = lcm(self.denom(), other.denom())
        left_num = other.denom() * self.num()
        right_num = self.denom() * other.num()
        new_num = left_num + right_num
        return Rational(new_num, denom_lcm).lowest_terms()

    def __sub__(self, other):
        other = convert_primitive(other)
        if not isinstance(other, Constant):
            return super().__sub__(other)
        
        if isinstance(self, Integer):
            self = Rational(self.eval(), 1)
        if isinstance(other, Integer):
            other = Rational(other.eval(), 1)

        denom_lcm = lcm(self.denom(), other.denom())
        left_num = denom_lcm * self.num()
        right_num = denom_lcm * other.num()
        new_num = left_num - right_num
        return Rational(new_num, denom_lcm).lowest_terms()
           
    def __mul__(self, other):
        other = convert_primitive(other)
        if not isinstance(other, Constant):
            return super().__mul__(other)
        
        if isinstance(self, Integer):
            self = Rational(self.eval(), 1)
        if isinstance(other, Integer):
            other = Rational(other.eval(), 1)

        new_num = self.num() * other.num()
        new_denom = self.denom() * other.denom()
        return Rational(new_num, new_denom).lowest_terms()

    def __pow__(self, other):
        other = convert_primitive(other)
        if not isinstance(other, Integer):
            return super().__pow__(other)
        
        if other.is_negative():
            new_num = self.denom() ** -other.eval()
            new_denom = self.num() ** -other.eval()
        else:
            new_num = self.num() ** other.eval()
            new_denom = self.denom() ** other.eval()
        return Rational(new_num, new_denom).lowest_terms()

class Rational(Constant):
    """A rational expression is a constant; a fraction of two integers"""
    def __init__(self, *args):
        for arg in args:
            assert isinstance(arg, int), f"arg {arg} is {type(arg)}"

        if len(args) == 1:
            self.left = args[0]
            self.right = 1
        else:
            super().__init__(*args)

    def __repr__(self):
        return f"({self.left} / {self.right})"

    def eval(self):
        return self.left / self.right

    def is_positive(self):
        return (self.left < 0) if (self.right < 0) else (self.left > 0)
    
    def is_negative(self):
        return (self.left < 0) if (self.right < 0) else (self.left > 0)
    
    def lowest_terms(self):
        """Simplifies a fraction into lowest terms"""
        n = self.left
        d = self.right
        if d == 0:
            return UNDEFINED
        
        if n % d == 0:
            return Integer(n // d)
        
        g = gcd(n, d)
        if  d > 0:
            return Rational(n // g, d // g)
        
        else:
            return Rational(-n // g, -d // g)
        
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

    def eval(self):
        return self.value

    def is_positive(self):
        return self.value > 0
    
    def is_negative(self):
        return self.value < 0

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
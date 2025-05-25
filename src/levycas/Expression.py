"""Classes for internal representations of mathematical expressions"""
from math import gcd

UNDEFINED = "UNDEFINED"

class Expression:
    """An Expression is a general mathematical object.
    In this case, it is used to represent binary operations
    """
    def __init__(self, left, right):
        self.left = left
        self.right = right
        self.simplify()

    def simplify(self):
        """Set of simplification rules for producing Automatic-Simplified
        Arithmetic Expressions (ASAE) per Joel S. Cohen
        """
        # raise NotImplementedError(f"Could not simplify {self}")
        print("Simplification not yet implemented")
        return self

    def __add__(self, other):
        return Sum(self, other) if issubclass(other, Expression) else NotImplemented
    
    def __sub__(self, other):
        return Minus(self, other) if issubclass(other, Expression) else NotImplemented
    
    def __mul__(self, other):
        return Product(self, other) if issubclass(other, Expression) else NotImplemented
    
    def __truediv__(self, other):
        return Div(self, other) if issubclass(other, Expression) else NotImplemented
    
    def __pow__(self, other):
        return Power(self, other) if issubclass(other, Expression) else NotImplemented

class Sum(Expression):
    """A Sum is the sum of two terms"""
    def __init__(self, left, right):
        self.terms = list()

        #Automatic simplification of associativity of addition
        self.terms += left.terms if isinstance(left, Sum) else [left]
        self.terms += right.terms if isinstance(right, Sum) else [right]  
        
    def __repr__(self):
        term_repr = [str(term) for term in self.terms]
        return "(" + " + ".join(term_repr) + ")"
    
    def eval(self, **vars):
        return sum([term.eval(**vars) for term in self.terms])
    
class Minus(Expression):
    """A Minus is the difference of two terms"""
    def __repr__(self):
        return f"({self.left} - {self.right})"
    
    def eval(self, **vars):
        return self.left.eval(**vars) - self.right.eval(**vars)

class Product(Expression):
    """A Product is the product of two factors"""
    def __repr__(self):
        return f"({self.left} * {self.right})"
    
    def eval(self, **vars):
        return self.left.eval(**vars) * self.right.eval(**vars)

class Div(Expression):
    """A Div represents the quotient of two terms. 
    If both terms are integers, it is a rational expression."""
    def __init__(self, left, right):
        if isinstance(left, Integer) and isinstance(right, Integer):
            self.rational = True 
        else:
            self.rational = False
        super().__init__(left, right)

    def __repr__(self):
        return f"({self.left} / {self.right})"
    
    def eval(self, **vars):
        return self.left.eval(**vars) / self.right.eval(**vars)
    
    def simplify(self):
        return self.simplify_rational() if self.rational else self.simplify_non_rational()

    def simplify_rational(self):
        assert isinstance(self.left, Integer)
        assert isinstance(self.right, Integer)

        if self.right.value == 0:
            return UNDEFINED

        quotient = self.left.value // self.right.value
        remainder = self.left.value % self.right.value

        if remainder == 0:
            return Integer(quotient)
        
        divisor = gcd(self.left.value, self.right.value)
        if self.right.value > 0:
            return Div(Integer(self.left.value // divisor), Integer(self.right.value // divisor))
        
        if self.right.value < 0:
            return Div(Integer((-1 * self.left.value) // divisor), Integer((-1 * self.right.value) // divisor))

    def simplify_non_rational(self):
        #u / v -> u * v ^ (-1)
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        if self.left == UNDEFINED or self.right == UNDEFINED:
            return UNDEFINED
        return Product(self.left.simplify(), Power(self.right.simplify(), Integer(-1)))

class Power(Expression):
    """A Power represents exponentiation"""
    def __repr__(self):
        return f"({self.left} ^ {self.right})"
    
    def eval(self, **vars):
        return self.left.eval(**vars) ** self.right.eval(**vars)
    
    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        if self.left == UNDEFINED or self.right == UNDEFINED:
            return UNDEFINED
        
        if isinstance(self.left, Integer):
            if self.left.value == 0:
                if isinstance(self.right, Integer) and self.right.value > 0:
                    return Integer(0)
                if isinstance(self.right, Div) and self.right.rational and self.right.positive:
                    return Integer(0)
                return UNDEFINED
            if self.left.value == 1:
                return Integer(1)
            
        if isinstance(self.right, Integer):
            return self.simplify_integer_power()
        
        return self
    
    def simplify_integer_power(self):
        exp = self.right.value
        #TODO: Implement from page 115ex


class Variable:
    """A Variable represents a variable"""

    def __init__(self, name: str):
        """Create a new Variable object"""
        self.name = name

    def __repr__(self) -> str:
        """Return the name of the variable"""
        return self.name
    
    def eval(self, **vars):
        val = vars.get(self.name, None)
        if val is None:
            raise ValueError(f"Variable {self.name} was not given a value")
        return val
    
    def simplify(self):
        return self

class Integer:
    """An Integer represents a decimal integer"""

    def __init__(self, value: int):
        """Creates a new Integer object"""
        self.value = value

    def __repr__(self):
        """Returns the value of the integer"""
        return str(self.value)
    
    def eval(self, **vars):
        return self.value
    
    def simplify(self):
        return self

class Special:
    """Special represents special cases"""

    def __init__(self):
        raise NotImplementedError("Special cases not yet implemented")
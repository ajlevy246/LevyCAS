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

    """The following two methods allow us to treat arbitrary expressions as powers. 
    This is useful for automatic simplification and total ordering of expressions.
    """
    def base(self):
        return self
    
    def exponent(self):
        return Integer(1)

    def __eq__(self, other):
        """Check if two expressions are syntactically equal. For this to make sense, 
        both expressions should be ASAE (Automatically-Simplified Arithmetic Expressions)."""
        if isinstance(self, Constant) and isinstance(other, Constant):
            return self.eval() == other.eval()
        
        if isinstance(other, Expression):
            return str(self) == str(other)
        
        return NotImplemented
    
    def __gt__(self, other):
        return not (self < other)
    
    def __add__(self, other):
        return Sum(self, other) if isinstance(other, Expression) else NotImplemented
    
    def __sub__(self, other):
        return Minus(self, other) if isinstance(other, Expression) else NotImplemented
    
    def __mul__(self, other):
        return Product(self, other) if isinstance(other, Expression) else NotImplemented
    
    def __truediv__(self, other):
        return Div(self, other) if isinstance(other, Expression) else NotImplemented
    
    def __pow__(self, other):
        return Power(self, other) if isinstance(other, Expression) else NotImplemented

class Sum(Expression):
    """A Sum is the sum of two terms"""
    def __init__(self, *terms):
        self.terms = terms
        
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
    def __init__(self, *factors):
        self.factors = factors

    def __repr__(self):
        factor_repr = [str(factor) for factor in self.factors]
        return "(" + " * ".join(factor_repr) + ")"
    
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

    def eval(self, **vars):
        prod = 1
        for factor in self.factors:
            prod *= factor.eval(**vars)
        return prod

class Div(Expression):
    """A Div represents the quotient of two terms. 
    If both terms are integers, it is a rational expression."""
    def __repr__(self):
        return f"({self.left} / {self.right})"
    
    def eval(self, **vars):
        return self.left.eval(**vars) / self.right.eval(**vars)

class Power(Expression):
    """A Power represents exponentiation"""
    def __repr__(self):
        return f"({self.left} ^ {self.right})"
    
    def eval(self, **vars):
        return self.left.eval(**vars) ** self.right.eval(**vars)
    
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
        return NotImplemented
    
    def eval(self, **vars):
        return 1

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
            print(f"{self} vs {other}")
            return self.name < other.name
        return NotImplemented

    def eval(self, **vars):
        val = vars.get(self.name, None)
        if val is None:
            raise ValueError(f"Variable {self.name} was not given a value")
        return val

class Constant(Expression):
    """A Constant represents a constant value"""

    def __lt__(self, other):
        """Total ordering for Constants: O-1"""
        if isinstance(other, Constant):
            return self.value < other.eval()
        
        if isinstance(other, Expression):
            return True
        
        return NotImplemented
    
class Rational(Constant):
    """A rational expression is a constant; a fraction of two integers"""

    #TODO: Ensure that the numbers given are not boxed.

    def __repr__(self):
        return f"({self.left} / {self.right})"
    
    def eval(self, **vars):
        return self.left / self.right

class Integer(Constant):
    """An Integer represents a decimal integer"""

    def __init__(self, value: int):
        """Creates a new Integer object"""
        self.value = value

    def __repr__(self):
        """Returns the value of the integer"""
        return str(self.value)

    def eval(self, **vars):
        return self.value

class Special(Expression):
    """Special represents special cases"""

    def __init__(self):
        raise NotImplementedError("Special cases not yet implemented")
    
    def __repr__(self):
        raise NotImplementedError("Special cases not yet implemented")
from . import Expression

class Constant(Expression):
    """A Constant represents a constant value"""

    def __lt__(self, other):
        """Total ordering for Constants: O-1"""
        if isinstance(other, Constant):
            return self.eval() < other.eval()
        
        if isinstance(other, Expression):
            return True
        
        return NotImplemented
    
    def sym_eval(self, **symbols):
        return self.simplify()

    def __add__(self, other):
        if not isinstance(other, Constant):
            return super().__add__(other)
        
        denom_lcm = lcm(self.denom(), other.denom())
        left_num = other.denom() * self.num()
        right_num = self.denom() * other.num()
        new_num = left_num + right_num
        return Rational(new_num, denom_lcm).simplify()

    def __sub__(self, other):
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
        return Rational(new_num, denom_lcm).simplify()
           
    def __mul__(self, other):
        if not isinstance(other, Constant):
            return super().__mul__(other)
        
        if isinstance(self, Integer):
            self = Rational(self.eval(), 1)
        if isinstance(other, Integer):
            other = Rational(other.eval(), 1)

        new_num = self.num() * other.num()
        new_denom = self.denom() * other.denom()
        return Rational(new_num, new_denom).simplify()

    def __pow__(self, other):
        if not isinstance(other, Integer):
            return super().__pow__(other)
        
        if other.is_negative():
            new_num = self.denom() ** -other.eval()
            new_denom = self.num() ** -other.eval()
        else:
            new_num = self.num() ** other.eval()
            new_denom = self.denom() ** other.eval()
        return Rational(new_num, new_denom).simplify()
    
    def derivative(self, wrt):
        return Integer(0)
    
    def trig_substitute(self):
        return self
    
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
    
    def copy(self):
        return Rational(self.left, self.right)

    def eval(self, **vars):
        return self.left / self.right

    def is_positive(self):
        return (self.left < 0) if (self.right < 0) else (self.left > 0)
    
    def is_negative(self):
        return (self.left < 0) if (self.right < 0) else (self.left > 0)
    
    def num(self):
        return self.left
    
    def denom(self):
        return self.right

    def simplify(self):
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
    
    @staticmethod 
    def convert_float(num):
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
            raise ValueError(f"Could not convert {num} to rational.")

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
    
    def copy(self):
        return Integer(self.value)

    def is_positive(self):
        return self.value > 0
    
    def is_negative(self):
        return self.value < 0

    def simplify(self):
        return self
    
    def operands(self):
        return [self.value]
    
    def num(self):
        return self.value
    
    def denom(self):
        return 1
    
    def __int__(self):
        return self.value
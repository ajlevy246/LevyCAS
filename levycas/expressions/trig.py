from .expression import Expression, Power, Integer

class Trig(Expression):
    """Trig functions represent the trigonometric functions"""
    orderings = ['Sin', 'Cos', 'Tan', 'Csc', 'Sec', 'Cot']

    def __init__(self, *args):
        assert len(args) == 1, "Trig functions expect one argument"
        self.arg = args[0]
        
    def __lt__(self, other):

        #If they are the same type, compare values
        if isinstance(other, type(self)): 
            return self.arg < other.arg
        
        #If they are both trig functions, compare via precedence rules
        if isinstance(other, Trig):
            self_precedence = Trig.orderings.index(type(self).__name__)
            other_precedence = Trig.orderings.index(type(other).__name__)
            return self_precedence < other_precedence
        
        #If the other is a power, compare via power rules
        if isinstance(other, Power):
            return NotImplemented

        #Otherwise, return false
        if isinstance(other, Expression):
            return False

        return NotImplemented

    def operands(self):
        return [self.arg]

    def sym_eval(self, **symbols):
        return type(self)(self.arg.sym_eval(**symbols)).simplify()

    def __repr__(self):
        return f"{type(self).__name__}({self.arg})"

    def copy(self):
        return type(self)(self.arg.copy())

    def contains(self, other):
        if self == other:
            return True
        return self.arg.contains(other)

class Sin(Trig):
    def __new__(cls, *args):
        """Automatic simplification for trigonometric functions
        requires the __new__ constructor to be overridden
        """
        assert len(args) == 1, f"Sin expects one argument"
        arg = args[0]
        coefficient = arg.coefficient()
        if coefficient.is_negative():
            return -Sin(-arg)
        elif coefficient == 0:
            return Integer(0)
        
        return super().__new__(Sin)

class Cos(Trig):
    def __new__(cls, *args):
        assert len(args) == 1, f"Cos expects one argument"
        arg = args[0]
        coefficient = arg.coefficient()
        if coefficient.is_negative():
            return Cos(-arg)
        elif coefficient == 0:
            return Integer(1)
        
        return super().__new__(Cos)

class Tan(Trig):
    pass

class Csc(Trig):
    pass

class Sec(Trig):
    pass

class Cot(Trig):
    pass
from .expression import Expression

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
    #DERIV-5
    def derivative(self, wrt):
        return (Cos(self.arg) * self.arg.derivative(wrt)).simplify()

class Cos(Trig):
    #DERIV-5
    def derivative(self, wrt):
        (-1 * Sin(self.arg) * self.arg.derivative(wrt)).simplify()

class Tan(Trig):
    pass

class Csc(Trig):
    pass

class Sec(Trig):
    pass

class Cot(Trig):
    pass
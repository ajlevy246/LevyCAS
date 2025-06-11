from .expression import Expression
from .trig import Trig

class Exp(Expression):
    def __init__(self, *args):
        assert len(args) == 1, "Exp takes only one argument"
        self.arg = args[0]

    def __repr__(self):
        return f"exp({self.arg})"

    def operands(self):
        return [self.arg]
    
    def __lt__(self, other):
        if not isinstance(other, Expression):
            return NotImplemented
        
        elif isinstance(other, Exp):
            return self.arg < other.arg

        elif isinstance(other, Ln):
            return True

class Ln(Expression):
    def __init__(self, *args):
        assert len(args) == 1, "Ln takes only one argument"
        self.arg = args[0]

    def __repr__(self):
        return f"ln({self.arg})"

    def operands(self):
        return [self.arg]
    
    def __lt__(self, other):
        if not isinstance(other, Expression):
            return NotImplemented
        
        elif isinstance(other, Ln):
            return self.arg < other.arg

        return False
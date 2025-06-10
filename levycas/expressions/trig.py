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

    #For other trig derivatives, transform into sin/cos form, then simplify the resulting derivative
    def derivative(self, wrt):
        substituted = trig_substitute(self).simplify() #Derivative operator requires simplified expression
        deriv = substituted.derivative(wrt)
        simplified = deriv.simplify()
        return simplified

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

def trig_substitute(expr: Expression):
    """Given an expression, replaces all instances of trig functions with their equivalent
    expressions in sin and cos. Returns a new expression.

    Args:
        expr (Expression): The expression to trig-sub.

    Returns:
        Expression: An expression containing no trig functions other than sin/cos
    """
    #Terminals of the AST do not have operands to substitute
    from .expression import Constant, Variable
    if isinstance(expr, Constant) or isinstance(expr, Variable):
        return expr.copy()

    operation = type(expr)

    #First, recursively apply to operands
    new_operands = [Trig.substitute(operand) for operand in expr.operands()]
    new_expr = operation(*new_operands)

    if operation == Tan:
        return Sin(*new_operands) / Cos(*new_operands)
    elif operation == Csc:
        return 1 / Sin(*new_operands)
    elif operation == Sec:
        return 1 / Cos(*new_operands)
    elif operation == Cot:
        return Cos(*new_operands) / Sin(*new_operands)
    else:
        return operation(*new_operands)
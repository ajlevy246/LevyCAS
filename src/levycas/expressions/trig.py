import math

from .expression import *


class _Pi(Constant):
    """Pi constant.
    
    Exposed as a singleton."""
    def __init__(self):
        pass

    def _get_str(self):
        return "\u03C0"

    def eval(self):
        return math.pi

PI = _Pi()
"""Pi - flyweight."""

class Trig(Elementary):
    """Trig functions represent the trigonometric functions"""
    def eval(self):
        raise NotImplementedError(f"Eval for {type(self)} not yet implemented.")

class Sin(Trig):
    def __new__(cls, *args):
        """To facilitate automatic simplifcation of trigonometric expressions,
        the __new__ method is overwritten.
        """
        assert len(args) == 1, "Sin expects a single argument"
        arg = convert_primitive(args[0])

        coefficient = arg.coefficient()
        if coefficient in (0, PI):
            return Integer(0)
        elif coefficient.is_negative():
            return -Sin(-arg)

        new_instance = super().__new__(cls)
        new_instance.args = [arg]
        return new_instance

class Cos(Trig):
    def __new__(cls, *args):
        """To facilitate automatic simplifcation of trigonometric expressions,
        the __new__ method is overwritten.
        """
        assert len(args) == 1, "Cos expects a single argument"
        arg = convert_primitive(args[0])
        coefficient = arg.coefficient()
        if coefficient == 0:
            return Integer(1)
        elif coefficient is PI:
            return Integer(-1)
        
        new_instance = super().__new__(cls)
        new_instance.args = [arg]
        if coefficient.is_negative():
            new_instance.args = [-arg]
        
        return new_instance
    
    def __init__(self, *args): 
        pass

class Tan(Trig):
    pass

class Csc(Trig):
    pass

class Sec(Trig):
    pass

class Cot(Trig):
    pass

class AntiTrig(Elementary):
    """AntiTrig functions represent the inverse trigonometric functions"""
    pass

class Arctan(AntiTrig):
    pass

class Arccos(AntiTrig):
    pass

class Arcsin(AntiTrig):
    pass
from .expression import *

class Trig(Elementary):
    """Trig functions represent the trigonometric functions"""
    pass

class Sin(Trig):
    def __new__(cls, *args):
        """To facilitate automatic simplifcation of trigonometric expressions,
        the __new__ method is overwritten.
        """

        assert len(args) == 1, f"Sin expects a single argument"
        arg = convert_primitive(args[0])

        coefficient = arg.coefficient()
        if coefficient == 0:
            return Integer(0)
        elif coefficient.is_negative():
            return -Sin(-arg)

        return super().__new__(cls)

class Cos(Trig):
    def __new__(cls, *args):
        """To facilitate automatic simplifcation of trigonometric expressions,
        the __new__ method is overwritten.
        """

        assert len(args) == 1, f"Cos expects a single argument"
        arg = convert_primitive(args[0])
        coefficient = arg.coefficient()
        if coefficient == 0:
            return Integer(1)
        
        new_instance = super().__new__(cls)
        if coefficient.is_negative():
            new_instance._arg = -arg
            return new_instance
        
        new_instance._arg = None
        return new_instance

    def __init__(self, *args):
        if self._arg is not None:
            super().__init__(self._arg)
        else:
            super().__init__(*args)

class Tan(Trig):
    pass

class Csc(Trig):
    pass

class Sec(Trig):
    pass

class Cot(Trig):
    pass
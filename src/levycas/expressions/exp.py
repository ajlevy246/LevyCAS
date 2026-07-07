from .expression import *
from .trig import Trig

class Exp(Elementary):
    """Exp represents the exponential e^(...)"""

    def __new__(cls, *args):
        """To facilitate automatic simplification of the exponential,
        the __new__ method is overwritten.
        
        Performs the simplification Exp(0) -> 1.
        """
        assert len(args) == 1, f"Exp expects a single argument"
        arg = convert_primitive(args[0])

        if arg == 0:
            return Integer(1)
        
        new_instance = super().__new__(cls)
        new_instance.args = [arg]

        return new_instance

class Ln(Elementary):
    """Ln represents the natural logarithm"""
    
    def __new__(cls, *args):
        """To facilitate automatic simplification of logarithmic expressions,
        the __new__ method is overwritten.

        Performs the simplification Ln(x^n * y^m) -> nLn(x) + mLn(y) and
        Ln(1) -> 0 and Ln(0) -> UNDEFINED
        """
        assert len(args) == 1, f"Ln expects a single argument"
        arg = convert_primitive(args[0])

        if arg == 1:
            return Integer(0)

        if isinstance(arg, Constant):
            coefficient = arg.coefficient()
            if coefficient <= 0:
                raise ValueError("Argument of the natural log must be positive")
        
        if type(arg) == Product:
            sum = 0
            for factor in arg.operands():
                term = Ln(factor)
                if term is UNDEFINED:
                    return term
                sum += term
            return sum
        
        if type(arg) == Power:
            return arg.exponent() * Ln(arg.base())

        new_instance = super().__new__(cls)
        new_instance.args = [arg]
        return new_instance

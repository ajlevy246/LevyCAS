from .expression import Expression

class Exp(Expression):
    def __init__(self, *args):
        assert len(args) == 1, "Exp takes only one argument"
        self.arg = args[0]

    def __repr__(self):
        return f"exp({self.arg})"

    def operands(self):
        return [self.arg]

class Ln(Expression):
    def __init__(self, *args):
        assert len(args) == 1, "Ln takes only one argument"
        self.arg = args[0]

    def __repr__(self):
        return f"ln({self.arg})"

    def operands(self):
        return [self.arg]
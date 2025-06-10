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
            return self.name < other.name
        return NotImplemented

    def copy(self):
        return Variable(self.name)
    
    def sym_eval(self, **symbols):
        definition = symbols.get(self.name, None)
        if definition is None:
            return self
        if definition == self:
            return self
        return definition.sym_eval(**symbols).simplify()
    
    def simplify(self):
        return self
    
    def operands(self):
        return [self.name]
    
    def derivative(self, wrt):
        #DERIV-1
        assert isinstance(wrt, Variable), f"Can only take derivative with respect to a variable"
        if self == wrt:
            return Integer(1)
        return Integer(0)
    
    def trig_substitute(self):
        return self

class Function(Expression):
    def __init__(self, name):
        print(f"Creating function?? {name}")
        self.name = name
        self.args = None
        self.parameters = None
        self.definition = None

    def add_args(self, *arguments, **symbols):
        self.args = list(arguments)
        assert len(self.args) == len(self.parameters), f"Number of arguments does not match number of parameters for {self}"

    def set_parameters(self, *parameters: list[Variable]):
        assert Variable(self.name) not in parameters, f"Function {self.name} cannot depend on itself"
        self.parameters = parameters

    def set_definition(self, definition: Expression):
        self.definition = definition

    def sym_eval(self, **symbols):
        if not self.args:
            return self
        
        for i in range(len(self.parameters)):
            param = str(self.parameters[i])
            param_def = self.args[i].sym_eval(**symbols)
            symbols[param] = param_def
        
        definition = symbols.get(self.name, None).definition
        assert definition is not None, f"Function {self.name} was cleared?"
        return definition.sym_eval(**symbols)

    def simplify(self):
        if self.args and UNDEFINED in self.args:
            return UNDEFINED
        return self

    def __repr__(self):
        if self.args:
            args_repr = [str(arg) for arg in self.args]
            return f"{self.name}({', '.join(args_repr)})"
        if self.definition:
            return f"{self.definition}"
        if self.definition:
            return f"{self.name}({', '.join(self.parameters)})"
        return f"Function({self.name})"

    def __lt__(self, other):
        if isinstance(other, Function):
            if self.name < other.name:
                return True
            
            num_left = len(self.args)
            num_right = len(other.args)
            min_num = min(num_left, num_right)
            for i in range(min_num):
                if self.factors[i] == other.factors[i]:
                    continue
                return self.factors[i] < other.factors[i]
            
            #O-3 (2) If all terms are equal, compare number of terms
            return num_left < num_right
        
        return NotImplemented
    
    def copy(self):
        copied = Function(self.name)
        copied.set_definition(self.definition.copy())
        copied.set_parameters(self.parameters) #Parameters not copied.
        if self.args:
            copied.add_args(*self.args)
        return copied
    
    def operands(self):
        if self.definition:
            return [self.definition]
        return self
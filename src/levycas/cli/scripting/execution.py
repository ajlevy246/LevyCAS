from levycas.parser import parse
from levycas.expressions import Variable, Integer
from levycas.operations import sym_eval, derivative, integrate

from enum import Enum

"""Global state is a stored as a dictionary 'env'.

Mappings are from levycas.Variable -> a tuple of (type, args [optional], definition).
Note that since levycas.Variables are hashed by their names:
    - env['x'] == env[Variable('x')]
"""
class ReferenceError(KeyError):
    pass

class ExecutionError(SystemError):
    pass

class Environment:
    """Captures state information for an active script"""
    VARIABLE = 0
    FUNCTION = 1

    #TODO: Function definitions should carry with them their own scope.
    # - e.g., Defining a function `f(x) = x` should not raise a ReferenceError.

    def __init__(self):
        """Initialize environment dictionary.
        
        Environment Schema: 
            - (self.VARIABLE, definition) OR
            - (self.FUNCTION, parameters, definition)
        """
        self.env = dict()

    def add_or_update(self, name, parameters, definition):
        """Add or update a stored variable/function reference.
        
        arguments is an optional list of symbols that defines 
        the new reference as a function. 
        Only one definition can exist for a given symbol at a time.
            - Example: 'f(x) = 2;' will create a reference to a function
            - 'f' that takes in an argument 'x' and is defined as levycas.Integer(2)
        """
        if parameters is None: #Variable reference
            self.env[name] = (self.VARIABLE, definition)
        else:
            self.env[name] = (self.FUNCTION, parameters, definition)

    def evaluate_at(self, name, arguments=None):
        """Evaluate a stored expression with given arguments.
        
        Arguments should be previously evaluated LevyCAS Expressions.
        Raises ReferenceError if reference does not exist or is the 
        wrong type.
        """
        reference = self.env.get(name, None)
        if reference is None:
            # raise ReferenceError(f"No reference to symbol {name} was found")
            return Variable(name)

        ref_type = reference[0]
        if ref_type == self.VARIABLE:
            if arguments is not None:
                raise ReferenceError(f"Could not evaluate variable {name} with arguments {arguments}")
            return reference[1]
        
        elif ref_type == self.FUNCTION:
            parameters = reference[1]
            if (arguments is None) or (len(parameters) != len(arguments)):
                raise ReferenceError(f"Function {name} expected {len(parameters)} argument(s) but got {len(arguments) if arguments is not None else 0}")
            func_definition = reference[2]
            #TODO: Ensure that overwriting the result (while evaluating)
            #doesn't affect the stored definition of the symbol.
            #TODO: Test with recursive definitions.
            #   - failing: `f(x) = x; print f(xy);`... why? 
            #   - after testing, this is a problem with sym_eval
            #   - example: x = Variable('x'); sym_eval(x, x=parse('xy'))
            local_args_mapping = dict(zip(parameters, arguments))
            return sym_eval(func_definition, **local_args_mapping)
            
            
def execute(script, output_log):
    """Executes a parsed script AST by intiializing global state and log reference."""
    global log
    global env

    log = output_log
    env = Environment()

    script.run()

class Script:
    """Basic Scripts contain one or more statements/conditionals to be executed."""
    def __init__(self):
        self.statements = list()

    def add_executable(self, statement):
        self.statements.append(statement)

    def run(self):
        for statement in self.statements:
            if statement is not None:
                statement.run()
            else:
                log.write_line("Empty statement...")

class ForLoop:
    """For-loop implementation."""
    def __init__(self, iterator: str, count: int, body: Script):
        self.iterator = iterator
        self.count = count
        self.body = body

    def run(self):
        """Runs a for loop, count starts from 1.
        
        Iterator is cleared after loop completes.
        """
        for i in range(1, self.count + 1):
            env.add_or_update(self.iterator, None, Integer(i))
            self.body.run()
        env.add_or_update(self.iterator, None, None)

class WhileLoop:
    """While-loop implementation."""
    def __init__(self):
        ...
        
    def run(self):
        ...

class ExpressionStatement:
    """Expression implementation.

    Expressions consist of tokens and commands that can be     
    turned into LevyCAS Expression objects directly.
    """
    def __init__(self):
        self.children = list()

    def run(self):
        """Children may be a single character, a ReferenceStatement, or a CommandStatement.
        
        If a child is an executable rather than a literal, the child's result is computed, an arbitrary
        Variable is substitued in its place, and then after the entire expression is parsed it is
        substituted back in.

        The logic here substitutes with uppercase letters A-Z, restricting variables in the scripting
        language to lowercase a-z.
        """
        expr_str = ""
        substitutions = dict()
        num_subs = 0
        for child in self.children:
            if isinstance(child, (ReferenceStatement, CommandStatement)):
                if num_subs >= 26:
                    raise ExecutionError("Cannot support > 26 statements needing evaluation in a single expression. Try adding some abstraction!")
                evaluated_child = child.run()
                substitution = chr(num_subs + 65)
                substitutions[substitution] = evaluated_child
                num_subs += 1
                expr_str += substitution
            else:
                expr_str += child

        try:
            expr = parse(expr_str)
        except Exception as parse_except:
            raise SyntaxError(f"Could not parse expression... {parse_except}")
        
        return sym_eval(expr, **substitutions)
    
    def add_child(self, new_child):
        """Add a new token to this expression.
        
        ExpressionStatements are flattened, so an Expression object will
        never appear as a child of another ExpressionStatement.
        """
        if isinstance(new_child, ExpressionStatement):
            self.children += new_child.children
        else:
            self.children.append(new_child)

class CommandStatement:
    """Commands implementation."""
    def __init__(self, cmd_type: str, arguments):
        self.cmd_type = cmd_type
        self.arguments = arguments

    def run(self):
        if self.cmd_type == "\\derivate":
            if len(self.arguments) != 2:
                raise ExecutionError(f"Derivate command expected expression and variable of differentiation.")
            expr = self.arguments[0].run()
            wrt = self.arguments[1].run()
            if not isinstance(wrt, Variable):
                raise ExecutionError(f"Could not differentiate {expr} wrt non-symbol {wrt}")
            try:
                result = derivative(expr, wrt)
            except Exception as e:
                raise ExecutionError(f"Could not differentiate {expr} w.r.t. {wrt}")
            return result
        elif self.cmd_type == "\\integrate":
            if len(self.arguments) != 2:
                raise ExecutionError(f"Integrate command expected integrand and variable of integration.")
            expr = self.arguments[0].run()
            wrt = self.arguments[1].run()
            if not isinstance(wrt, Variable):
                raise ExecutionError(f"Could not integrate {expr} wrt non-symbol {wrt}")
            try:
                result = integrate(expr, wrt)
            except Exception as e:
                raise ExecutionError(f"Could not inetgrate {expr} w.r.t. {wrt}")
            return result 
        else:
            raise SyntaxError(f"Command: {self.cmd_type} not yet implemented.")

class AssignmentStatement:
    """Variable or function assignment.
    
    Includes both declarations and updates.
    """
    def __init__(self, name: str, parameters: list[str], definition):
        self.name = name
        self.parameters = parameters
        self.definition = definition

    def run(self):
        env.add_or_update(self.name, self.parameters, self.definition.run())

class ReferenceStatement:
    """Variable or function reference."""
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

    def run(self):
        if self.arguments is None: #Variable reference
            reference = env.evaluate_at(self.name, None)
            if reference is None:
                raise ReferenceError(f"Undefined reference to variable {self.name}")
            return reference
        
        else: #Function reference
            arguments = [arg.run() for arg in self.arguments]
            return env.evaluate_at(self.name, arguments)

class PrintStatement:
    """Print statement implementation."""
    def __init__(self, expression):
        self.expr = expression
        
    def run(self):
        result = self.expr.run()
        log.write_line(str(result))
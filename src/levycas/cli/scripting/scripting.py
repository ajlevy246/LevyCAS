"""How does it work? 

Expressions within a script are parsed using the LevyCAS built-in Pratt parser. This parser is built around that, essentially
a wrapper that extends the functionality of the basic expression parser into a fully fledged computer algebra system. Because of this
much of the code here (especially the lexical analysis phase) looks very similar to that found in the Pratt parser. 

Each command in a script falls under three categories:

1. Control Logic:
The for loops and while loops that allow for more complex scripts.
    - Example: for (i : 3) {...}

2. Declarations:
Initializations of variables and functions.
    - Example: func f(x, y) = x + y;

3. Expressions: 
Simple statements of computation.
    - Example: f(3, 4) + 5;

4. Assignments (Not Yet Implemented):
Updates of a declared variables/function's value.
    - Example: x = x * x + 5;

Parsing uses a hardcoded one-token lookahead to ensure the correct path is taken, avoiding backtracking.
Statement are interpreted as they are read, using the global variables below:

- 'log': a reference to the output log where the output of each statement is written
- 'cas_environment': an object that represents the current state of the CAS as statements are interpreted.

The parser constructs an AST as it iterates over each token. The AST consists of encapsulated objects (located in `execution.py`)
that each contain a 'run' method.
"""

from enum import Enum
from .execution import (
    Script,
    ForLoop,
    WhileLoop,
    ExpressionStatement,
    CommandStatement,
    AssignmentStatement,
    ReferenceStatement,
    PrintStatement,
    execute,
)
import re

"""Token Types (Enum'd for readability)"""
class TokenType(Enum):
    COMMAND = "COMMAND"
    FLOAT = "FLOAT"
    INTEGER = "INTEGER"
    FOR = "FOR"
    WHILE = "WHILE"
    PRINT = "PRINT"
    COMMA = "COMMA"
    SYMBOL = "SYMBOL"
    EQUALS = "EQUALS"
    SEMICOLON = "SEMICOLON"
    COLON = "COLON"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    LBRACKET = "LBRACKET"
    RBRACKET = "RBRACKET"
    OPERATION = "OPERATION"
    SPACE = "SPACE"
    OTHER = "OTHER"

"""Token specification. Matches TokenTypes to regex strings.

Note that order matters here. Since SYMBOL captures all single letters, 
commands, operations, and keywords must precede it in the final regex.
"""
TOKEN_SPEC: list[tuple[TokenType, str]] = [
    (TokenType.COMMAND, r"\\derivate|\\integrate|\\eval"),
    (TokenType.INTEGER, r"\d+(?!\.)"), #Negative lookahead avoids matching floats yet
    (TokenType.FLOAT, r"(\d+\.?\d*|\d*\.\d+)"),
    (TokenType.FOR, r"for"),
    (TokenType.WHILE, r"while"),
    (TokenType.PRINT, r"print"),
    (TokenType.COMMA, r"\,"),
    (TokenType.EQUALS, r"="),
    (TokenType.SEMICOLON, r";"),
    (TokenType.COLON, r":"),
    (TokenType.LPAREN, r"\("),
    (TokenType.RPAREN, r"\)"),
    (TokenType.LBRACKET, r"\{"),
    (TokenType.RBRACKET, r"\}"),
    (TokenType.OPERATION, r"exp|arcsin|arccos|arctan|sin|cos|tan|[\+\-\*\/\^]"),
    (TokenType.SYMBOL, r"[a-z]"),
    (TokenType.SPACE, r"\s+"),
    (TokenType.OTHER, r".")
]

class ParserError(SystemError):
    pass

class ScriptToken:
    """Simple token implementation."""
    def __init__(self, literal: str, type: TokenType):
        self.literal = literal
        self.type = TokenType(type)

    def __repr__(self) -> str:
        return f"<Token :: {self.literal} [{self.type}]>"

def lex_script(script: str) -> list[ScriptToken]:
    """Tokenize a script"""
    try:
        token_pattern = '|'.join(f'(?P<{type.value}>{pattern})' for type, pattern in TOKEN_SPEC)
    except:
        raise SyntaxError("Incorrect token specification")
    
    tokens = list()
    for match in re.finditer(token_pattern, script):
        token_type = match.lastgroup
        token_value = match.group()

        if token_type == "SPACE":
            continue

        elif token_type == "OTHER":
            raise SyntaxError(f"Invalid token: {token_value}")
        
        else:
            tokens.append(ScriptToken(token_value, token_type))
    return tokens      

def run_script(script: str, log) -> None:
    """Starts the parsing process; executes the resulting script.

    Argument 'log' is a reference to the output log where output should be written.
    """
    global tokens
    tokens = lex_script(script)[::-1]

    script_ast = parse_script()
    execute(script=script_ast, output_log=log)
    
def parse_iterator_assignment():
    """Parse an iterator assignment for a for-loop.
    
    Example: "for (i : 3) {...}"

    <iterator_assignment> := LPAREN SYMBOL COLON INTEGER RPAREN
    """
    next_token = tokens.pop()
    if next_token.type != TokenType.LPAREN:
        raise ParserError("Expected left paren while parsing iterator assignment.")

    iterator = tokens.pop()
    if iterator.type != TokenType.SYMBOL:
        raise SyntaxError("Iterator in a for-loop must be a variable.")

    next_token = tokens.pop()
    if next_token.type != TokenType.COLON:
        raise SyntaxError("Expected a colon in iterator assignment.")

    count = tokens.pop()
    if count.type != TokenType.INTEGER:
        raise SyntaxError("Number of iterations must be an integer.")

    next_token = tokens.pop()
    if next_token.type != TokenType.RPAREN:
        raise SyntaxError("Expected a closing parentheses (')') while parsing iterator assignment.")
    
    return iterator.literal, count.literal

def parse_for_loop():
    """Parse a for loop.
    
    <for_loop> := FOR <iterator_assignment> LBRACKET <script> RBRACKET
    """
    next_token = tokens.pop()
    if next_token.type != TokenType.FOR:
        raise ParserError("Error in parsing logic...")

    iterator, count = parse_iterator_assignment()
    next_token = tokens.pop()
    if next_token.type != TokenType.LBRACKET:
        raise SyntaxError("Expected an opening brace '{' for the body of a for loop.")
    
    body = parse_script()

    next_token = tokens.pop()
    if next_token.type != TokenType.RBRACKET:
        raise SyntaxError("Expected a closing brace '}' for the body of a for loop.")
    return ForLoop(
        iterator=iterator,
        count=int(count),
        body=body
    )

def parse_while_loop():
    """Parse a while loop
    
    <while_loop> := WHILE <iterator_condition> LBRACKET <script> RBRACKET
    """
    raise ParserError("WHILE LOOPS NOT YET IMPLEMENTED")
    #TODO: Implement while loop grammar and logic.

def parse_control_block(): 
    """Parse a control block.
    
    <control_block> := <for_loop> | <while_loop>
    """
    next_token_type = tokens[-1].type
    if next_token_type == TokenType.FOR:
        return parse_for_loop()
    else:
        return parse_while_loop()

def parse_arguments_list():
    """Parse a list of arguments.

    <arguments_list> := LPAREN <expression> <arguments> RPAREN
    """
    next_token = tokens.pop()
    if next_token.type != TokenType.LPAREN:
        raise ParserError("Expected left paren ('(') to start a list of arguments.")
    
    arguments = [parse_expression()]

    next_token = tokens[-1]
    while next_token.type == TokenType.COMMA:
        tokens.pop()
        arguments.append(parse_expression())
        next_token = tokens[-1]

    next_token = tokens.pop()
    if next_token.type != TokenType.RPAREN:
        raise SyntaxError("Expected right paren (')') to close a list of arguments.")
    return arguments

def parse_command():
    """Parse a command.
    
    <command> := COMMAND <arguments_list>
    """
    command_name = tokens.pop().literal
    command_args = parse_arguments_list()
    return CommandStatement(command_name, command_args)

def parse_reference():
    """Parse a symbol reference (variable or function).
    
    <reference> := SYMBOL | SYMBOL <arguments_list>
    """
    name_token = tokens.pop()
    if name_token.type != TokenType.SYMBOL:
        raise ParserError("Expected a symbol as a function/variable name.") 
    name = name_token.literal

    arguments = None
    next_token = tokens[-1]
    if next_token.type == TokenType.LPAREN:
        arguments = parse_arguments_list()
    reference = ReferenceStatement(name=name, arguments=arguments)
    return reference

def parse_expression():
    """Parse an expression. 
    
    Algebraic grammar is not enforced here; rather, 
    these expressions are passed into LevyCAS' Pratt Parser.

    <expression> := LPAREN <expression> RPAREN | command <expression>
      | FLOAT <expression> | <reference> <expression> | INTEGER <expression> | OPERATION <expression> | ε
    """
    #TODO: Update this method to reflect the new rule.
    expression = ExpressionStatement()
    next_token = tokens[-1]
    if next_token.type not in (
        TokenType.LPAREN,
        TokenType.COMMAND,
        TokenType.FLOAT,
        TokenType.SYMBOL,
        TokenType.INTEGER,
        TokenType.OPERATION,
    ):
        raise ParserError("Expected valid expression token.")
    
    if next_token.type == TokenType.LPAREN:
        tokens.pop()
        expression.add_child(next_token.literal)
        next_token = tokens[-1]
        if next_token.type != TokenType.RPAREN:
            expression.add_child(parse_expression())
        next_token = tokens.pop()
        if next_token.type != TokenType.RPAREN:
            raise SyntaxError("Expected closing parentheses at the end of a subexpression.")
        expression.add_child(next_token.literal)

    elif next_token.type == TokenType.COMMAND:
        expression.add_child(parse_command())

    elif next_token.type == TokenType.SYMBOL:
        expression.add_child(parse_reference())

    else: #integer, float, or operation token
        tokens.pop()
        expression.add_child(next_token.literal)

    next_token = tokens[-1]
    if next_token.type in (
        TokenType.LPAREN,
        TokenType.COMMAND,
        TokenType.FLOAT,
        TokenType.SYMBOL,
        TokenType.INTEGER,
        TokenType.OPERATION,
    ):
        expression.add_child(parse_expression())
    return expression

def parse_parameters_list():
    """Parse a list of parameters (symbols)."""
    next_token = tokens.pop()
    if next_token.type != TokenType.LPAREN:
        raise ParserError("Expected left paren ('(') to start a list of parameters.")
    
    parameters = list()
    sym = tokens.pop()
    if sym.type != TokenType.SYMBOL:
        raise SyntaxError("Parameters must be symbols.")
    parameters.append(sym.literal)

    next_token = tokens[-1]
    while next_token.type == TokenType.COMMA:
        tokens.pop()
        sym = tokens.pop()
        if sym.type != TokenType.SYMBOL:
            raise SyntaxError("Parameters must be symbols.")
        parameters.append(sym.literal)
        next_token = tokens[-1]

    next_token = tokens.pop()
    if next_token.type != TokenType.RPAREN:
        raise SyntaxError("Expected closing parenthesis (')') to end a list of parameters.")
    return parameters

def parse_assignment():
    """Parse an assignment (function or variable). 
    
    Represents both function and variable assignments.
    
    <assignment> := SYMBOL <arguments_list> EQUALS <expression> | SYMBOL EQUALS <expression>
    """
    name_token = tokens.pop()
    if name_token.type != TokenType.SYMBOL:
        raise SyntaxError("Cannot assign a value to a non-symbol.")

    parameters = None
    next_token = tokens[-1]
    if next_token.type == TokenType.LPAREN: #Function assignment
        parameters = parse_parameters_list()

    next_token = tokens.pop()
    if next_token.type != TokenType.EQUALS:
        raise ParserError("Expected an equals ('=') in an assignment.")

    definition = parse_expression()
    return AssignmentStatement(
        name=name_token.literal,
        parameters=parameters,
        definition=definition
    )

def parse_print():
    """Parse a print statement
    
    <print> := PRINT <expression>
    """
    next_token = tokens.pop()
    if next_token.type != TokenType.PRINT:
        raise ParserError("Expected 'print' command...")

    return PrintStatement(expression=parse_expression())

def parse_statement():
    """Parse a statement
    
    statement := assignment SEMICOLON | print SEMICOLON
    """
    next_token_type = tokens[-1].type
    statement = None

    if next_token_type == TokenType.SYMBOL:
        statement = parse_assignment()

    elif next_token_type == TokenType.PRINT:
        statement = parse_print()

    if statement is None:
        raise SyntaxError("Expected a print statement or symbol assignment.")

    next_token = tokens.pop()
    if next_token.type != TokenType.SEMICOLON:
        raise SyntaxError("Expected a semicolon ';' at the end of a statement.")
    
    return statement
    
def parse_script():
    """Parsing entry point. 
    
    <script> := <control_block> <script> | <statement> <script> | ε
    """
    script = Script()
    if len(tokens) == 0:
        return script
    
    next_token = tokens[-1]

    if next_token.type in (
        TokenType.FOR, 
        TokenType.WHILE
    ):
        script.add_executable(parse_control_block())
        script.add_executable(parse_script())
    
    elif next_token.type in (
        TokenType.SYMBOL,
        TokenType.PRINT,
    ):
        script.add_executable(parse_statement())
        script.add_executable(parse_script())

    return script
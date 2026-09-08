"""How does it work? 

Expressions within a script are parsed using the LevyCAS built-in Pratt parser. This parser is built around that, essentially
a wrapper that extends the functionality of the basic expression parser into a fully fledged computer algebra system. Because of this,
much of the code here (especially the lexical analysis phase) looks very similar to that found in the Pratt parser. 

Each command in a script falls under three categories:

1. Control Logic:
The for loops and while loops that allow for complex logical branching.
    - Example: for (i : 3) {...}

2. Declarations:
Initializations of variables and functions.
    - Example: func f(x, y) = x + y;

3. Expressions: 
Simple statements of computation.
    - Example: f(3, 4) + 5;

4. Assignments:
Updates of a declared variables/function's value.
    - Example: x = x * x + 5;

Parsing uses a hardcoded one-token lookahead to ensure the correct path is taken, avoiding backtracking.
Statement are interpreted as they are read, using the global variables below:

- 'log': a reference to the output log where the output of each statement is written
- 'cas_environment': an object that represents the current state of the CAS as statements are interpreted.

The parser constructs an AST as it iterates over each token. The AST consists of encapsulated objects (located in `execution.py`)
that each contain a 'run' method.
"""

import re
from dataclasses import dataclass
from enum import Enum

from .execution import (
    AssignmentStatement,
    CommandStatement,
    ExpressionStatement,
    ForLoop,
    PrintStatement,
    ReferenceStatement,
    Script,
    WhileLoop,
    execute,
)

"""Recognized Token types"""
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
    (TokenType.OPERATION, r"ln|exp|arcsin|arccos|arctan|sin|cos|tan|[\+\-\*\/\^]"),
    (TokenType.SYMBOL, r"[a-z]"),
    (TokenType.SPACE, r"\s+"),
    (TokenType.OTHER, r".")
]

class ParserError(SystemError):
    pass

@dataclass
class ScriptToken:
    """Simple token implementation."""
    literal: str
    type: TokenType

    def __repr__(self) -> str:
        return f"<Token :: {self.literal} [{self.type}]>"

def lex_script(script: str) -> list[ScriptToken]:
    """Tokenize a script"""
    token_pattern = '|'.join(f'(?P<{type.value}>{pattern})' for type, pattern in TOKEN_SPEC)
    
    tokens = []
    for match in re.finditer(token_pattern, script):
        token_type = match.lastgroup
        token_value = match.group()

        if token_type == "SPACE":
            continue

        elif token_type == "OTHER":
            raise SyntaxError(f"Invalid token: {token_value}")
        
        else:
            tokens.append(ScriptToken(token_value, TokenType(token_type)))
    return tokens      

def run_script(script: str, log) -> None:
    """Starts the parsing process; executes the resulting script.

    Argument 'log' is a reference to the output log where output should be written.
        - Or, any class implementing a "write_line()" method.
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
    if next_token.type is not TokenType.LPAREN:
        raise SyntaxError("Expected left paren while parsing iterator assignment.")

    iterator = tokens.pop()
    if iterator.type is not TokenType.SYMBOL:
        raise SyntaxError("Iterator in a for-loop must be a variable.")

    next_token = tokens.pop()
    if next_token.type is not TokenType.COLON:
        raise SyntaxError("Expected a colon in iterator assignment.")

    count = tokens.pop()
    if count.type is not TokenType.INTEGER:
        raise SyntaxError("Number of iterations must be an integer.")

    next_token = tokens.pop()
    if next_token.type is not TokenType.RPAREN:
        raise SyntaxError("Expected a closing parenthesis (')') while parsing iterator assignment.")
    
    return iterator.literal, count.literal

def parse_for_loop():
    """Parse a for loop.
    
    <for_loop> := FOR <iterator_assignment> LBRACKET <script> RBRACKET
    """
    next_token = tokens.pop()
    if next_token.type is not TokenType.FOR:
        raise ParserError("Error in parsing logic...")

    iterator, count = parse_iterator_assignment()
    next_token = tokens.pop()
    if next_token.type is not TokenType.LBRACKET:
        raise SyntaxError("Expected an opening brace '{' to open the body of a for loop.")
    
    body = parse_script()

    if len(tokens) == 0 or tokens.pop().type is not TokenType.RBRACKET:
        raise SyntaxError("Expected a closing brace '}' to end the body of a for loop.")

    return ForLoop(
        iterator=iterator,
        count=int(count),
        body=body
    )

def parse_while_loop():
    """Parse a while loop
    
    <while_loop> := WHILE <iterator_condition> LBRACKET <script> RBRACKET
    """
    #TODO: Implement while loop grammar and logic.
    raise ParserError("WHILE LOOPS NOT YET IMPLEMENTED")

def parse_control_block(): 
    """Parse a control block.
    
    <control_block> := <for_loop> | <while_loop>
    """
    if tokens[-1].type is TokenType.FOR:
        return parse_for_loop()
    else:
        return parse_while_loop()

def parse_arguments_list():
    """Parse a list of arguments.

    <arguments_list> := LPAREN <expression> <arguments> RPAREN
    """
    next_token = tokens.pop()
    if next_token.type is not TokenType.LPAREN:
        raise ParserError("Expected left paren ('(') to start a list of arguments.")
    
    arguments = [parse_expression()]

    next_token = tokens[-1]
    while next_token.type is TokenType.COMMA:
        tokens.pop()
        arguments.append(parse_expression())
        next_token = tokens[-1]

    next_token = tokens.pop()
    if next_token.type is not TokenType.RPAREN:
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
    symbol = tokens.pop()
    name = symbol.literal
    if symbol.type is not TokenType.SYMBOL:
        raise ParserError(f"Expected a symbol as a function/variable name, not {name}")         

    arguments = None
    next_token = tokens[-1]
    if next_token.type is TokenType.LPAREN:
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
        raise ParserError("Expected valid expression token, not {next_token.literal}")

    match next_token:
        case ScriptToken(literal, TokenType.LPAREN):
            # parse a subexpression, then check for the closing paren
            tokens.pop()
            expression.add_child(literal)

            next_token = tokens[-1]
            if next_token.type is not TokenType.RPAREN:
                expression.add_child(parse_expression())

            next_token = tokens.pop()
            if next_token.type is not TokenType.RPAREN:
                raise SyntaxError(f"Expected closing parenthesis at the end of a subexpression, not {next_token.literal}")
            expression.add_child(next_token.literal)

        case ScriptToken(_, TokenType.COMMAND):
            expression.add_child(parse_command())

        case ScriptToken(_, TokenType.SYMBOL):
            expression.add_child(parse_reference())

        case ScriptToken(literal, _):
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
    if next_token.type is not TokenType.LPAREN:
        raise ParserError("Expected left paren ('(') to start a list of parameters.")
    
    parameters = []

    sym = tokens.pop()
    if sym.type is not TokenType.SYMBOL:
        raise SyntaxError("Parameters must be symbols.")
    parameters.append(sym.literal)

    next_token = tokens[-1]
    while next_token.type is TokenType.COMMA:
        tokens.pop()

        sym = tokens.pop()
        if sym.type is not TokenType.SYMBOL:
            raise SyntaxError(f"Parameters must be symbols, not {sym.literal}")
        
        parameters.append(sym.literal)
        next_token = tokens[-1]

    next_token = tokens.pop()
    if next_token.type is not TokenType.RPAREN:
        raise SyntaxError(f"Expected closing parenthesis (')') to end a list of parameters, not {next_token.literal}")
    
    return parameters

def parse_assignment():
    """Parse an assignment (function or variable). 
    
    Represents both function and variable assignments.
    
    <assignment> := SYMBOL <arguments_list> EQUALS <expression> | SYMBOL EQUALS <expression>
    """
    symbol = tokens.pop()
    if symbol.type is not TokenType.SYMBOL:
        raise SyntaxError(f"Cannot assign a value to a non-symbol. Expected a symbol from: {symbol}")

    parameters = None
    match tokens[-1]:
        case ScriptToken(_, TokenType.LPAREN):
            parameters = parse_parameters_list()

        case ScriptToken(literal, token_type) if token_type is not TokenType.EQUALS:
            raise ParserError(f"Expected an equals ('=') in an assignment, not {literal}")

    tokens.pop()
    definition = parse_expression()
    return AssignmentStatement(
        name=symbol.literal,
        parameters=parameters,
        definition=definition
    )

def parse_print():
    """Parse a print statement
    
    <print> := PRINT <expression>
    """
    next_token = tokens.pop()
    if next_token.type is not TokenType.PRINT:
        raise ParserError("Expected 'print' command...")

    return PrintStatement(expression=parse_expression())

def parse_statement():
    """Parse a statement
    
    statement := assignment SEMICOLON | print SEMICOLON
    """
    statement = None
    match tokens[-1]:
        case ScriptToken(_, TokenType.SYMBOL):
            statement = parse_assignment()

        case ScriptToken(_, TokenType.PRINT):
            statement = parse_print()

        case token:
            raise SyntaxError(f"Expected a print statement or symbol assignment, not {token}")

    # statement should end in a semicolon
    next_token = tokens.pop()
    if next_token.type is not TokenType.SEMICOLON:
        raise SyntaxError(f"Expected a semicolon ';' at the end of a statement, not {next_token}")

    return statement

def parse_script():
    """Parsing entry point. 
    
    <script> := <control_block> <script> | <statement> <script> | ε
    """
    script = Script()
    if len(tokens) == 0:
        return script

    match tokens[-1]:
        case ScriptToken(_, TokenType.FOR | TokenType.WHILE):
            script.add_executable(parse_control_block())
            script.add_executable(parse_script())

        case ScriptToken(_, TokenType.SYMBOL | TokenType.PRINT):
            script.add_executable(parse_statement())
            script.add_executable(parse_script())

        case ScriptToken(_, TokenType.LBRACKET):
            tokens.pop()
            script = parse_script()
            if len(tokens) == 0 or tokens.pop().type is not TokenType.RBRACKET:
                raise SyntaxError("Expected closing bracket to match script's opening brace")
            
        case ScriptToken(_, TokenType.RBRACKET):
            pass

        case ScriptToken(literal, token_type):
            raise SyntaxError(f"Expected the start of a valid statement, not '{literal}' ({token_type=})")
        
        case token:
            raise SyntaxError(f"Expected a valid token, not: {token}")

    return script
"""An implementation of a Pratt Parser for simple expressions"""
from .lexer import Token, tokenize
from ..expressions import *

#Global verbose vars for testing purposes
pv = False #parsing verbose 
lv = False #lexing verbose


"""Token specifications, matching regex strings"""
TOKEN_SPEC: list[tuple[str]] = [
    ("NUMBER",    r'(\d+\.?\d*|\d*\.\d+)'),   #Matches a decimal
    ("TRIG_SIN",       r'(?:i)sin'),           #Matches sin function, case insensitive
    ("TRIG_COS",       r'(?:i)cos'),           #Matches cos function, case insensitive
    ("TRIG_TAN",       r'(?:i)tan'),           #Matches tan function, case insensitive
    ("TRIG_CSC",       r'(?:i)csc'),           #Matches csc function, case insensitive
    ("TRIG_SEC",       r'(?:i)sec'),           #Matches sec function, case insensitive
    ("VARIABLE",  r'[a-zA-Z]'),               #Matches a single letter
    ("EXP",       r'\^'),                     #Matches a single exponential symbol  
    ("PLUS",      r'\+'),                     #Matches a plus sign
    ("MINUS",     r'-'),                      #Matches a minus sign
    ("MULT",      r'\*'),                     #Matches a multiplication sign
    ("DIV",       r'/'),                      #Matches a division sign
    ("FACT",      r'\!'),                     #Matches a factorial symbol
    ("LPAREN",    r'\('),                     #Matches a left paren
    ("RPAREN",    r'\)'),                     #Matches a right paren
    ("COMMA",     r'\,'),                     #Matches a comma
    ("SPACE",     r'\s+'),                    #Matches any whitespace
    ("OTHER",     r'.'),                      #Matches any invalid characters
    ("EOL",       r'\$')                      #Matches the End-of-Line character '$'
]

"""Token classes, matching associated Parsing classes"""
TOKEN_CLASS = {
    "NUMBER":   Integer,
    "TRIG_SIN":      Sin,
    "TRIG_COS":      Cos,
    "TRIG_TAN":      Tan,
    "TRIG_CSC":      Csc,
    "TRIG_SEC":      Sec,
    "VARIABLE": Variable,
    "PLUS":     Sum,
    "MULT":     Product,
    "DIV":      Div,
    "EXP":      Power,
    "FACT":     Factorial,
    "LPAREN":   Special,
    "RPAREN":   Special,
    "SPACE":    Special,
    "OTHER":    Special,
    "EOL":      Special
}

"""Operator precendences, matching associated binding powers"""
TOKEN_BP = {
    "NUMBER":   (0, 0),
    "TRIG_SIN": (0, 40),
    "TRIG_COS": (0, 40),
    "TRIG_TAN": (0, 40),
    "TRIG_CSC": (0, 40),
    "TRIG_SEC": (0, 40),
    "TRIG_COT": (0, 40),
    "VARIABLE": (0, 40),
    "PLUS":     (10, 15),
    "MINUS":    (10, 20), 
    "MULT":     (20, 25),
    "DIV":      (20, 25),
    "EXP":      (35, 30),
    "FACT":     (40, 40),
    "LPAREN":   (-1, -1),
    "RPAREN":   (-1, -1),
    "SPACE":    (-1, -1),
    "OTHER":    (-1, -1),
    "EOL":      (-1, -1)
}

def parse(expression: str, **symbols) -> Expression:
    """Parse an input expression into a LevyCAS Expression tree. 

    Args:
        expression (str): A mathematical expression string

    Returns:
        Expression.Expression: The root of the AST representing the input expression.
    """
    tokens: list[Token] = tokenize(expression, TOKEN_SPEC)
    tokens = expand(tokens, **symbols) #Expand implicit multiplications, if present
    tokens.append(Token("EOL", "$", -1)) #Append end of line token
    tokens = tokens[::-1] #Reverse token list to pop from end
    expr = pratt(tokens, 0, **symbols)
    assert tokens.pop().type == "EOL" and len(tokens) == 0
    return expr

def expand(tokens: list[Token], **symbols) -> list[Token]:
    """Expand implicit multiplications"""
    if lv:
        print(f"Expanding with: {symbols=}")
    expanded = list()
    for i in range(len(tokens)):
        curr = tokens[i]

        #Symbols previously defined as functions are replaced
        if curr.type == "VARIABLE":
            sym = symbols.get(curr.value, Variable(-1))
            if isinstance(sym, Function):
                curr.type = "FUNCTION"

        expanded.append(curr)

        #Implicit Multiplication is expanded
        next = tokens[i + 1] if i + 1 < len(tokens) else None
        if next:
            if curr.type in ("VARIABLE", "NUMBER", "RPAREN", "DECIMAL") and (next.type in ("VARIABLE", "LPAREN", "FUNCTION") or next.type.startswith("TRIG_")):
                expanded.append(Token("MULT", "*", curr.pos + curr.len))
    return expanded

def pratt(tokens: list[Token], bp: int, **symbols) -> Expression:
    """Recursive Pratt Parsing function

    Args:
        tokens (list[Token]): List of tokens
        bp (int): Right binding power of the preceding operator

    Returns:
        Expression.Expression: The root of the subtree parsed by this iteration
    """
    if lv:
        print(f"Tokens: {tokens[-1]}")

    curr = tokens.pop()
    if pv: 
        print(f"Parsing curr: {curr.type}: {curr.value}")

    #Parse first token as left hand side (NULL DENOTATIONS)

    if curr.type == "NUMBER":
        #Parse decimal number
        number = curr.value.split(".")
        if len(number) == 1:
            left = Integer(int(curr.value))
        else:
            assert len(number) == 2, f"Failed to parse number {curr.value}"
            whole, partial = number
            
            denominator = 10 ** len(partial)
            numerator = int(whole + partial)
            if denominator == 1:
                left =  Integer(numerator)
            else:
                left = Rational(numerator, denominator)

    elif curr.type == "VARIABLE":
        left = Variable(curr.value)

    elif curr.type.startswith("TRIG_"):
        right = pratt(tokens, TOKEN_BP[curr.type][1])
        left = TOKEN_CLASS[curr.type](right)

    elif curr.type == "FUNCTION":
        if pv:
            print(f"Parsing FUNCTION token: {curr.value}")
        left = symbols.get(curr.value, None) #Get the defined function from symbol table
        if left is None:
            raise ValueError("What??")
        left = left.copy() #Copy it over
        new_args = list()

        assert tokens[-1].type == "LPAREN", "Please parenthesize function arguments"
        tokens.pop() #Remove lparen before parsing arguments

        next_arg = pratt(tokens, 0, **symbols).sym_eval(**symbols)
        new_args.append(next_arg) #Get first argument
        next = tokens[-1]
        if pv:
            print(f"After returning first argument: {next=}")
        while next.type == "COMMA":
            if pv:
                print(f"Detected comma; looping: {new_args=}")
            tokens.pop() #Parse comma
            next_arg = pratt(tokens, 0, **symbols).sym_eval(**symbols)
            new_args.append(next_arg)
            next = tokens[-1]

        assert next.type == "RPAREN", "Please parenthesize function arguments"
        tokens.pop() #Parse rparen
        if pv:
            print(f"Adding args to function {curr.value}: {new_args}")
        left.add_args(*new_args)

    elif curr.type == "LPAREN":
        left = pratt(tokens, 0, **symbols)
        next = tokens.pop()
        if next.type != "RPAREN" and next.type != "COMMA":
            raise SyntaxError(f"Expected closing parenthesis from {next}")
        
    elif curr.type == "PLUS":
        left = pratt(tokens, 0, **symbols) #Ignore unary plus operator

    elif curr.type == "MINUS": #Unary minus operator is parsed into (-1) * Exp
        minus_rbp = TOKEN_BP["MINUS"][1] 
        right = pratt(tokens, minus_rbp, **symbols)
        left = Product(Integer(-1), right)

    else:
        raise SyntaxError(f"Expected null denotation from {curr}")

    #Parse operator and recurse on remaining expression
    while True:
        next = tokens[-1]
        if pv:
            print(f"Looping {left=}, {next=}")
        if next.type == "RPAREN" or next.type == "EOL": #Check that next token is not the end of an expression
            break #Break without consuming token

        if next.type == "COMMA": #End of a function argument.
            #Note that if an extraneous comma is present, the
            #end-of-line token will not be next, raising an error.

            #break with consuming token
            if pv:
                print(f"Detected comma, returning: {left}")
            break

        lbp, rbp = TOKEN_BP[next.type]

        if lbp <= 0 or rbp <= 0: #Check that next token is an operator
            raise SyntaxError(f"Expected operator from {next}")

        if lbp < bp: #Checks L/R associativity against previous operator
            break

        tokens.pop() #Consume token after precedence check

        if next.type == "MINUS":
            right = pratt(tokens, rbp, **symbols)
            left = Sum(left, Product(Integer(-1), right))
        elif next.type == "FACT":
            left = Factorial(left)
        else:
            right = pratt(tokens, rbp, **symbols)

            #Produce resulting expression.
            left = TOKEN_CLASS[next.type](left, right)

    return left
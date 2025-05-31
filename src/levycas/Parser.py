"""An implementation of a Pratt Parser for simple expressions"""
from .Lexer import Token, tokenize
from .Expression import *

"""Token specifications, matching regex strings"""
TOKEN_SPEC: list[tuple[str]] = [
    ("NUMBER",    r'\d+(\.\d*)?'),    #Matches an integer
    ("VARIABLE",  r'[a-z]'),          #Matches a single lowercase letter
    ("EXP",       r'\^'),             #Matches a single exponential symbol  
    ("PLUS",      r'\+'),             #Matches a plus sign
    ("MINUS",     r'-'),              #Matches a minus sign
    ("MULT",      r'\*'),             #Matches a multiplication sign
    ("DIV",       r'/'),              #Matches a division sign
    ("FACT",      r'\!'),             #Matches a factorial symbol
    ("LPAREN",    r'\('),             #Matches a left paren
    ("RPAREN",    r'\)'),             #Matches a right paren
    ("COMMA",     r'\,'),             #Matches a comma
    ("SPACE",     r'\s+'),            #Matches any whitespace
    ("OTHER",     r'.'),              #Matches any invalid characters
    ("EOL",       r'\$')              #Matches the End-of-Line character '$'
]

"""Token classes, matching associated Parsing classes"""
TOKEN_CLASS = {
    "NUMBER":   Integer,
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
    "VARIABLE": (0, 5),
    "PLUS":     (10, 15),
    "MINUS":    (10, 30), #Minus has the right binding power of MULT and left of PLUS
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
    expr = pratt(tokens, 0)
    assert tokens.pop().type == "EOL" and len(tokens) == 0
    return expr

def expand(tokens: list[Token], **symbols) -> list[Token]:
    """Expand implicit multiplications"""
    expanded = list()
    for i in range(len(tokens)):
        curr = tokens[i]

        #Symbols previously defined as functions are replaced
        if curr.type == "VARIABLE" and curr.value in symbols:
            curr.type = "FUNCTION" #Replace defined symbols with their function representations.

        expanded.append(curr)

        #Implicit Multiplication is expanded
        next = tokens[i + 1] if i + 1 < len(tokens) else None
        if next:
            if curr.type in ("VARIABLE", "NUMBER", "RPAREN") and next.type in ("VARIABLE", "LPAREN"):
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
    curr = tokens.pop()

    #Parse first token as left hand side (NULL DENOTATIONS)
    if curr.type == "NUMBER":
        left = Integer(int(curr.value))

    elif curr.type == "VARIABLE":
        left = Variable(curr.value)

    elif curr.type == "FUNCTION":
        left = Function(curr.value)
        left.add_args(pratt(tokens, 0))

    elif curr.type == "LPAREN":
        left = pratt(tokens, 0)
        next = tokens.pop()
        if next.type != "RPAREN":
            raise SyntaxError(f"Expected closing parenthesis from {next}")
        
    elif curr.type == "PLUS":
        left = pratt(tokens, 0) #Ignore unary plus operator

    elif curr.type == "MINUS": #Unary minus operator is parsed into (-1) * Exp
        minus_rbp = TOKEN_BP["MINUS"][1] 
        right = pratt(tokens, minus_rbp)
        left = Product(Integer(-1), right)

    else:
        raise SyntaxError(f"Expected null denotation from {curr}")

    #Parse operator and recurse on remaining expression
    while True:
        next = tokens[-1]
        if next.type == "RPAREN" or next.type == "EOL": #Check that next token is not the end of an expression
            break #Break without consuming token

        if next.type == "COMMA": #End of a function argument, get the next one
            left = [left]
            right = pratt(tokens, 0)
            if isinstance(right, list):
                left = left + right
            else:
                left.append(right)

        lbp, rbp = TOKEN_BP[next.type]

        if lbp <= 0 or rbp <= 0: #Check that next token is an operator
            raise SyntaxError(f"Expected operator from {next}")

        if lbp < bp: #Checks L/R associativity against previous operator
            break

        tokens.pop() #Consume token after precedence check

        if next.type == "MINUS":
            right = pratt(tokens, rbp)
            left = Sum(left, Product(Integer(-1), right))
        elif next.type == "FACT":
            left = Factorial(left)
        elif next.type == "FUNCTION":
            left = Function(left)
            right = pratt(tokens, 0)
            left.add_args(right)
        else:
            right = pratt(tokens, rbp)

            #Produce resulting expression.
            left = TOKEN_CLASS[next.type](left, right)

    return left
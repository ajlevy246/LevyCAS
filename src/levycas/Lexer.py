"""Tokenize an input expression string"""
import re

"""Token specifications, matching regex strings"""
TOKEN_LIST: list[tuple[str]] = [
    ("NUMBER", r'\d+(\.\d*)?'),   #Matches an integer or decimal
    ("VARIABLE", r'[a-z]'),       #Matches a single lowercase letter
    ("EQ", r'='),                 #Matches a single equals sign
    ("EXP", r'\^'),               #Matches a single exponential symbol  
    ("PLUS", r'\+'),              #Matches a plus sign
    ("MINUS", r'-'),              #Matches a minus sign
    ("MULT", r'\*'),              #Matches a multiplication sign
    ("DIV", r'/'),                #Matches a division sign
    ("LPAREN", r'\('),            #Matches a left paren
    ("RPAREN", '\)'),             #Matches a right paren
    ("SPACE", r'\s+'),            #Matches any whitespace
    ("OTHER", r'.')               #Matches any invalid characters
]

"""Regex pattern; concatenates the token specs"""
TOKEN_PATTERN: str = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_LIST)

class Token:
    """A token object is a substring + metadata
    """

    def __init__(self, token_type: str, token_value: str, token_pos: int) -> None:
        """Create a new token object.

        Args:
            token_type (str): The type of the matched substring.
            token_value (str): The matched substring in the expression.
            pos (int): The position of the matched substring in the expression.
        """
        self.type = token_type
        self.value = token_value
        self.pos = token_pos
        self.len = len(token_value)

    def __repr__(self) -> str:
        return f"<Token:: {self.type} [{self.pos}-{self.pos + self.len}]>"

def tokenize(expr: str) -> list[Token]:
    """Tokenize an expression string

    Args:
        expr (str): The input expression to tokenize
    """
    tokens = list()
    for match in re.finditer(TOKEN_PATTERN, expr):
        token_type = match.lastgroup
        token_value = match.group()
        token_pos = match.span()[0]

        if token_type == "SPACE":
            continue
        
        elif token_type == "OTHER":
            raise SyntaxError(f"Invalid token: {token_value} at position {match.span()[0]}")

        else: 
            tokens.append(Token(token_type, token_value, token_pos))
    
    return tokens
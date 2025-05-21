"""Tokenize an input expression string"""
import re

"""Token specifications, matching regex strings
"""
TOKEN_LIST: list[tuple[str]] = [
    ("NUMBER", r'\d+(\.\d*)?'),   #Matches an integer or decimal
    ("VARIABLE", r'[a-z]'),       #Matches a single lowercase letter
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

class Lexer:
    """A lexer object tokenizes a string"""

    def __init__(self, expr: str) -> None:
        """Create a new Lexer object

        Args:
            expr (str): The input expression to tokenize
        """
        token_pattern = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in TOKEN_LIST)
        self.tokens = list()
        for match in re.finditer(token_pattern, expr):
            print(match)

class Token:
    """A token object is a substring + metadata
    """

    def __init__(self, token_type: str, token_value: str, pos: int) -> None:
        """Create a new token object.

        Args:
            token_type (str): The type of the matched substring.
            token_value (str): The matched substring in the expression.
            pos (int): The position of the matched substring in the expression.
        """
        self.type = token_type
        self.value = token_value
        self.pos = pos
        self.len = len(token_value)


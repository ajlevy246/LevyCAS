"""Tokenize an input expression string"""
import re

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

def tokenize(expr: str, token_spec: list) -> list[Token]:
    """Tokenize an expression string

    Args:
        expr (str): The input expression to tokenize
        token_spec (list): The token specifications
    """
    try:
        token_pattern = '|'.join(f'(?P<{name}>{pattern})' for name, pattern in token_spec)
    except:
        raise SyntaxError("Incorrect token specification")

    tokens = list()
    for match in re.finditer(token_pattern, expr):
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
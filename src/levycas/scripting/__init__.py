"""This module presents a custom scripting language to interface with
the LevyCAS library without touching the Python core directly.

See a more detailed description and grammar at scripting/GRAMMAR.md.
 """
from .scripting import lex_script, parse_script, run_script

from .errors import ReferenceError, ExecutionError

__all__ = [
    'lex_script', 'parse_script', 'run_script',
    'ReferenceError', 'ExecutionError',
]

"""LevyCAS is an implementation of a Computer Algebra System written
in pure Python. It requires only the built-in regex (re) and math modules.

Install with the `tui` extra and run `levycas` for the interactive Textual user interface.
Or, check out https://alexlevy.me for an online LevyCAS demo, hosted with Gradio on Huggingface.

- Alex Levy (2025)
"""
from .expressions import *
from .operations import *
from .parser import *
from .scripting import *
from .cli import *
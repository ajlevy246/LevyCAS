import pytest

from levycas.cli.main import LevyCasApp
import levycas.cli.scripting.scripting as scripting
from levycas.cli.scripting.scripting import (
            lex_script, parse_script,
            ScriptToken as Token,
            TokenType as tk,
        )
from levycas.cli.scripting.errors import ExecutionError, ReferenceError
from levycas.cli.scripting.execution import *

class TestScriptingScreen:
    async def test_screen_load(self):
        cas = LevyCasApp() 
        async with cas.run_test() as pilot:
            await pilot.click()
            assert True

class TestScriptingParsing:
    def test_lexer(self):
        def tok_eq(expected, actual):
            val = expected.type == actual.type and expected.literal == actual.literal
            if not val:
                print(expected, actual)
            return val
        
        stmt = "f(x) = 4x + 3.5;"
        lexed = lex_script(stmt)
        tokens = [
            Token("f", tk.SYMBOL),  Token("(", tk.LPAREN),
            Token("x", tk.SYMBOL),  Token(")", tk.RPAREN),
            Token("=", tk.EQUALS),  Token("4", tk.INTEGER),
            Token("x", tk.SYMBOL),  Token("+", tk.OPERATION),
            Token("3.5", tk.FLOAT), Token(";", tk.SEMICOLON),
        ]
        assert all(tok_eq(expected, actual) for expected, actual in zip(tokens, lexed, strict=True))

        stmt = "4.55sinxsixn\\derivate(for : cos)"
        lexed = lex_script(stmt)
        tokens = [
            Token("4.55", tk.FLOAT), Token("sin", tk.OPERATION),
            Token("x", tk.SYMBOL), Token("s", tk.SYMBOL),
            Token("i", tk.SYMBOL), Token("x", tk.SYMBOL),
            Token("n", tk.SYMBOL), Token("\derivate", tk.COMMAND),
            Token("(", tk.LPAREN), Token("for", tk.FOR),
            Token(":", tk.COLON),  Token("cos", tk.OPERATION),
            Token(")", tk.RPAREN),
        ]
        assert all(tok_eq(expected, actual) for expected, actual in zip(tokens, lexed, strict=True))

        #TODO: Update the below behavior if float regex changes
        # Hard coded as a reminder if it breaks
        stmt = "print (44.55)"
        lexed = lex_script(stmt)
        tokens = [
            Token("print", tk.PRINT), Token("(", tk.LPAREN),
            Token("4", tk.INTEGER), Token("4.55", tk.FLOAT),
            Token(")", tk.RPAREN),
        ]
        assert all(tok_eq(expected, actual) for expected, actual in zip(tokens, lexed, strict=True))

    def test_simple_statements(self):
        stmt = "f(x) = 4x + 3; for (i : 3) {print(f(x));}"
        scripting.tokens = lex_script(stmt)[::-1]

        script = parse_script()
        parsed_statements = script.statements

        assert len(parsed_statements) == 2
        func, loop = parsed_statements

        assert (
            isinstance(func, AssignmentStatement)
            and func.name == "f"
            and func.parameters == ['x']
        )
        definition = func.definition
        assert isinstance(definition, ExpressionStatement) and len(definition.children) == 4
        reference = definition.children.pop(1)
        assert (
            definition.children == ['4', '+', '3']
            and isinstance(reference, ReferenceStatement)
            and reference.name == "x"
            and reference.arguments is None
        )


    def test_for_loops(self):
        ...

    def test_print(self):
        ...

    def test_definitions(self):
        ...

    def test_substitutions(self):
        ...

class TestScriptingExecution:
    ...
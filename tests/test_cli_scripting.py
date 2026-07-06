import pytest

from levycas.cli.__main__ import LevyCasApp
import levycas.cli.scripting.scripting as scripting
from levycas.cli.scripting.scripting import (
            lex_script, parse_script, run_script,
            ScriptToken as Token,
            TokenType as tk,
        )
from levycas.cli.scripting.errors import ExecutionError, ReferenceError
from levycas.cli.scripting.execution import *

class TestScriptingScreen:
    async def test_screen_load(self):
        cas = LevyCasApp() 
        async with cas.run_test() as pilot:
            await pilot.click("#scripting")

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
            Token("n", tk.SYMBOL), Token("\\derivate", tk.COMMAND),
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
        assert scripting.tokens == []
        assert script == \
            Script(statements=[
                AssignmentStatement(
                    name='f', 
                    parameters=['x'], 
                    definition=ExpressionStatement(
                        children=[
                            '4', 
                            ReferenceStatement(name='x', arguments=None),
                            '+',
                            '3'
                        ]
                    )
                ),
                Script(statements=[
                    ForLoop(
                        iterator='i',
                        count=3,
                        body=Script(statements=[
                            PrintStatement(
                                expression=ExpressionStatement(children=[
                                    '(',
                                    ReferenceStatement(
                                        name='f',
                                        arguments=[
                                            ExpressionStatement(children=[
                                                ReferenceStatement(
                                                    name='x',
                                                    arguments=None
                                                )
                                            ])
                                        ]
                                    ),
                                    ')',
                                ])
                            ),
                            Script(statements=[]), # TODO: Why is a blank script parsed here?
                        ])
                    ),
                    Script(statements=[]), #TODO: Why is a blank script parsed here?
                ])
            ])


    def test_for_loops(self):
        ...

    def test_print(self):
        ...

    def test_definitions(self):
        ...

    def test_substitutions(self):
        ...

class TestScriptingExecution:
    
    class Log:
        def __init__(self, output_record: list[str]):
            self.record = output_record

        def write_line(self, output: str):
            self.record.append(output)
    
    def test_simple_statements(self):
        stmt = "f(x) = 4x + 3; for (i : 3) {print(f(i));}"
        output_record = []
        log = self.Log(output_record)
        run_script(stmt, log)
        assert output_record == ['7', '11', '15']

        stmt = "f(x, y) = xcos(y) + ysin(x); g(x) = \\derivate(f(x, 0), x); print(g(x));"
        output_record = []
        log = self.Log(output_record)
        run_script(stmt, log)
        assert output_record == ['1']

    def test_commands(self):
        stmt = (
            "f(x, y) = xsin(x^2) + 2ycos(y);"
            "print \derivate(f(x, y), x);"
            "print \integrate(f(x, y), x);"
            "print \derivate(f(x, y), y);"
            "print \integrate(f(x, y), y);"
        )
        output_record = []
        log = self.Log(output_record)
        run_script(stmt, log)
        assert output_record == [
            'Sin(x²) + 2x²Cos(x²)',
            '-(1/2)Cos(x²) + 2yxCos(y)',
            '2Cos(y) - 2ySin(y)',
            '2Cos(y) + 2ySin(y) + yxSin(x²)',
        ]
            
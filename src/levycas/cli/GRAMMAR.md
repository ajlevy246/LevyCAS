# LevyCAS Scripting - Grammar

> **NOTE**: Allowing expressions like `f(f(a, 2))` (that is, arbitrary expressions as arguments) prevents implicit multiplication in expressions like `x(4x + 3)`, although these expressions can be parsed by LevyCAS. Normal implicit multiplication is still supported, like `(x + 1)(x + 2)` or `2(x^2)`.

> **TODO**: Check for problems with referencing functions that take no arguments, arising from empty `expression` rules.

> **NOTE**: Parsing of the final argument in a list of arguments will consume the `RPAREN` that was meant to close the list... thus parantheses are disallowed in arguments. Exceptions are when they appear as a reference, like `f(f(x))`. 
> - Allowed: `f(2x, 3x+4, a*b^c)`
> - Disallowed: `f(Sin(x), \derivate(2x))`...

> **TODO**: Due to the above, test for commands as arguments, as in `f(\derivate(Sin(x)))`, and just parens in commands by themselves, as in `\derivate(sin(x))`. Solution may be to add expression grammar (would not need to encode operator precedence or associativity).

**Entry Point**

```
script := control_block script | statement script | ε
```

**Control Logic**

```
control_block := for_loop | while_loop
for_loop := FOR iterator_assignment LBRACKET script RBRACKET
while_loop := WHILE iterator_condition LBRACKET script RBRACKET
iterator_assignment := LPAREN SYMBOL COLON INTEGER RPAREN
iterator_cond := LPAREN SYMBOL CONDITION INTEGER RPAREN
```

**Expressions**

```
statement := assignment SEMICOLON | print SEMICOLON
expression := LPAREN expression RPAREN | command expression | FLOAT expression | reference expression | INTEGER expression | OPERATION expression | ε
reference := SYMBOL | SYMBOL arguments_list
command := COMMAND arguments_list
assignment := SYMBOL parameters_list EQUALS expression | SYMBOL EQUALS expression
parameters_list := LPAREN SYMBOL parameters RPAREN
parameters := COMMA SYMBOL parameters | ε
arguments_list := LPAREN expression arguments RPAREN
arguments := COMMA expression arguments | ε
print := PRINT expression
```

**Literals (regex)**

```
COMMAND := "\\derivate|\\integrate|\\eval"
INTEGER := "\d+(?!\.)",
FLOAT := "(\d+\.?\d*|\d*\.\d+)"
FOR := "for"
WHILE := "while"
PRINT := "print"
COMMA := "\,"
EQUALS := "="
SEMICOLON, ";"
COLON := ":"
LPAREN := "\("
RPAREN := "\)"
LBRACKET := "\{"
RBRACKET := "\}"
OPERATION := "exp|arcsin|arccos|arctan|sin|cos|tan|[\+\-\*\/\^]"
SYMBOL := "[a-z]"
SPACE := "\s+"
OTHER := "."
``` 

# LevyCAS Scripting - Examples

**Example 1. Simple Calculus Operation**
```bash
f(x, y) = cos(x) + ysin(y);

print \integrate(f(x, y),y);
print \derivate(f(x, y),x);

for (i : 3) {
    print f(i, 0);
}
```
# LevyCAS Scripting - Grammar

Welcome to LevyCAS scripting! This module presents a simple custom scripting language
that can be used as an alternative to directly touching the Python core. 

The grammar below is a simple context-free, LL(1) grammar capturing the syntax of the scripting language. 
See the top-down 1-token lookahead parser in [`scripting/scripting.py`](scripting.py), and the structures it generates in [`scripting/execution.py`](execution.py).

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
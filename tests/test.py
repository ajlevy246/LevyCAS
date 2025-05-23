from levycas.Parser import parse
from os import system

while ((entered := input("Enter expression: ")) != "exit"):
    if entered == "clear":
        system('clear')
        continue

    try:
        expr = parse(entered)
        print(expr)
    except:
        print("Erra erra")
#!/usr/bin/env python3

from levycas.Parser import parse
from levycas.Expression import *
from os import system

symbols = dict()

def main():
    """Main CAS loop"""
    while ((entered := input("Command $>: ")) != "exit"):
        if entered == "clear":
            clear()
            continue
        if entered == "symbols":
            print("========== Symbol Table ==========")
            for index, (key, value) in enumerate(symbols.items()):
                print(f"{index}: {key} = {value}")
            print("==================================")
            continue
        if entered == "test":
            order()
            continue
        if entered == "simplify":
            simplify()
            continue
        if entered == "expand":
            expand()
            continue

        num_assignments = entered.count("=")
        if num_assignments == 0:
            expr = evaluate(entered)
            if expr:
                try:
                    print(f"{expr} = {expr.sym_eval(**symbols)}")
                except ValueError as e:
                    print(e)
                    continue

        elif num_assignments == 1:
            sym, expr = entered.split("=")
            sym = sym.strip()

            if len(sym) == 1: #If the symbol is a single character, it is a variable
                sym = evaluate(sym)
                expr = evaluate(expr)
                if expr:
                    var_val = expr.sym_eval(**symbols)
                    symbols[str(sym)] = var_val
                    print(f"{sym} = {var_val}")
                else:
                    print(f"Expression {expr} was invalid")
                continue

            #Otherwise, it is a function
            sym = sym.strip()
            function_name = sym[0]
            assert  function_name in symbols or isinstance(evaluate(function_name), Variable), f"Invalid name {function_name}"
            parameters = sym[1:].strip() #Remove function name
            assert parameters[0] == "(" and parameters[-1] == ")", f"Please parenthesize function parameters"
            parameters = parameters[1:-1] #Remove parentheses
            parameters = [evaluate(parameter) for parameter in parameters.split(",")]
            for parameter in parameters:
                assert isinstance(parameter, Variable), "Parameters must be variables"
            definition = evaluate(expr)
            if definition:
                parameter_repr = str(parameters[0])
                for parameter in parameters[1::]:
                    parameter_repr += f", {str(parameter)}"

                new_function = symbols.get(function_name, Variable("-"))
                #Will be a variable if it was previously declared as a symbol, 
                #or if it wasn't defined at all
                if isinstance(new_function, Variable):
                    new_function = Function(function_name)

                new_function.set_definition(definition)
                new_function.set_parameters(parameters)
                symbols[function_name] = new_function
            else:
                raise ValueError(f"{definition} is not a valid function definition")

        elif num_assignments > 1:
            print(f"Multiple assignments not allowed.")
        
def simplify():
    """Test simpification methods"""
    clear()
    while True:
        a = input("Simplify $> ")
        if a == "exit":
            break
        if a == "clear":
            clear()
            continue

        # try:  
        a = evaluate(a)
        original_a = str(a)
        simp_a = a.copy().simplify()
        print(f">> {original_a} -> {simp_a.sym_eval()}")
        
    clear()
    return

def order():
    clear()
    """Test total ordering of objects"""
    while True:
        a = input("First Expression $>: ")     
        if a == "exit":
            break
        if a == "clear":
            clear()
            continue

        try: 
            a = parse(a)
        except Exception as e:
            print(f"Error parsing {e}")
            continue

        b = input("Second Expression $>: ")
        if b == "exit":
            break
        if b == "clear":
            clear()
            continue
        
        try: 
            b = parse(b)
        except Exception as e:
            print(f"Error parsing expression {e}")
            return
        
        if a < b:
            print(f">> {a} < {b}")
        else:
            print(f">> {b} < {a}")
    clear()
    return

def expand():
    clear()
    while True:
        a = input("Expand $> ")
        if a == "clear":
            clear()
            continue
        if a == "exit":
            clear()
            return

        expr = evaluate(a)
        if expr:
            expanded  = expr.algebraic_expand()
            # print(f">> {expanded}")
            simplified = expanded.simplify()
            print(f">> {simplified}\n")



def evaluate(string: str) -> Expression:
    """Evaluate an expression string and return the result"""
    try:
        return parse(string, **symbols)
    except Exception as e:
        print(f"Error: {e}")
        return None

def clear():
    system('clear')
    print("========== LevyCAS ==========")

if __name__ == "__main__":
    clear()
    main()
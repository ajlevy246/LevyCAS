from levycas.Parser import parse
from levycas.Expression import *
from os import system

def main():
    """Main CAS loop"""
    assignments = dict()

    while ((entered := input("Enter expression: ")) != "exit"):
        if entered == "clear":
            clear()
            continue

        if entered == "vars":
            print("Current variable assignments:")
            for var, val in assignments.items():
                print(f"{var} = {val}")
            continue

        num_assignments = entered.count("=")
        if num_assignments == 0:
            expr = evaluate(entered)
            if expr:
                print(f"{expr} = {expr.eval(**assignments)}")

        elif num_assignments == 1:
            var, expr = entered.split("=")
            var = evaluate(var)
            if isinstance(var, Variable):
                var_name = var.name
                expr = evaluate(expr)
                if expr:
                    var_val = expr.eval(**assignments)
                    assignments[var_name] = var_val
                    print(f"{var_name} = {var_val}")
            
            else:
                print(f"Invalid variable name: '{var}'")

        elif num_assignments > 1:
            print(f"Multiple assignments not allowed.")
        
def evaluate(string: str) -> Expression:
    """Evaluate an expression string and return the result"""
    try:
        return parse(string)
    except Exception as e:
        print(e)
        return None
    
def clear():
    system('clear')
    print("========== LevyCAS ==========")

if __name__ == "__main__":
    clear()
    main()
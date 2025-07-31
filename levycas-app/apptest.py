import gradio as gr
from levycas import *

change_selection = lambda btn: btn

MENU_OPTIONS = {
    "Calculus": ["Derivate", "Integrate"],
    "Numerical": ["Prime Test", "Factor Integer"],
    "Polynomial": ["Calculate GCD", "Divide"],
}

ERROR_MESSAGE = "if the output is blank or yields an error message, levycas is unable to perform the requested operation. Please try again with different inputs!"

def render_calculus_operation(selection):
    def calculus_calculate(expr, wrt):
        try:
            expr, wrt = parse(expr), parse(wrt)
        except:
            return "Expression could not be parsed"
        
        if selection == "Derivate":
            return derivative(expr, wrt)
        elif selection == "Integrate":
            return integrate(expr, wrt)

    if selection == "Derivate":
        with gr.Row():
            expr = gr.Textbox(label="Expression", info="expression to derivate", placeholder="2sinx + cos(x^2)")
            wrt = gr.Textbox(label="Variable", info="variable of differention", placeholder="x")
    else:
        with gr.Row():
            expr = gr.Textbox(label="Expression", info="expression to integrate", placeholder="(1/2)sin(x)cos(x)")
            wrt = gr.Textbox(label="Variable", info="variable of integration", placeholder="x")

    output = gr.Textbox(
        value=calculus_calculate,
        inputs=[expr, wrt],
        label="Output",
        info=ERROR_MESSAGE,
    )

    examples = gr.Examples(
        examples=[
            ["4x^3 + 3x^2 + 2x", "x"],
            ["sin(x^2 + 2y)", "y"],
            ['exp(2x)+xcos(x)', 'x'],
        ],
        inputs=[expr, wrt]
    )

def render_numerical_operation(selection):
    def numerical_calculate(expr):
        try:
            as_int = parse(expr)
        except:
            return "Expression could not be parsed"

        if not isinstance(as_int, Integer):
            return "Please enter an integer"
        
        if selection == "Prime Test":
            return f"{expr} is prime!" if is_prime(as_int) else f"{expr} is not prime."
        elif selection == "Factor Integer":
            factors = factor_integer(as_int)
            factorization = ""
            for prime, mult in factors.items():
                factorization += f" {prime}^{mult} "
            return factorization

    if selection == "Prime Test":
        integer = gr.Textbox(label="Integer", info="integer to test for primality", placeholder="43859273483453")
    else:
        integer = gr.Textbox(label="Integer", info="integer to factor", placeholder="2^5*3^4*4^5")

    output = gr.Textbox(
        value=numerical_calculate,
        inputs=integer,
        label="Output",
        info=ERROR_MESSAGE,
    )

def render_polynomial_operation(selection):
    gr.Textbox(selection)

if __name__ == "__main__":
    with gr.Blocks() as cas_demo:
        menu_selection = gr.State()
        with gr.Row():
            for opt in MENU_OPTIONS.keys():
                btn = gr.Button(opt)
                btn.click(change_selection, btn, menu_selection)

        operation_selection = gr.State()

        @gr.render(inputs=menu_selection)
        def sub_menu(selection):
            if selection is None:
                return
            
            with gr.Row():
                for opt in MENU_OPTIONS[selection]:
                    btn = gr.Button(opt)
                    btn.click(change_selection, btn, operation_selection)

        @gr.render(inputs=[menu_selection, operation_selection])
        def render_operation(menu, operation):
            if menu is None or operation is None:
                return
            
            if menu == "Calculus":
                render_calculus_operation(operation)
            elif menu == "Numerical":
                render_numerical_operation(operation)
            elif menu == "Polynomial":
                render_polynomial_operation(operation)
            else:
               gr.Textbox("Operation not recognized")

    cas_demo.launch()
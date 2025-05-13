from sympy import *
from sympy.parsing.latex import parse_latex
import re

init_printing()


# --- Highlighting function ---
def highlight_latex(expr_latex, original, result):
    original_latex = latex(original)
    result_latex = r"\color{red}{" + latex(result) + "}"
    pattern = re.escape(original_latex)
    return re.sub(pattern, lambda m: result_latex, expr_latex, count=1)


# --- Expression helpers ---
def is_evaluable(expr):
    return not expr.is_Atom and expr.doit(deep=False) != expr


def find_deepest_evaluable(expr):
    for arg in expr.args:
        result = find_deepest_evaluable(arg)
        if result:
            return result
    if is_evaluable(expr):
        return expr
    return None


def replace_once(expr, target, value):
    if expr == target:
        return value, True
    if expr.args:
        new_args = []
        replaced = False
        for arg in expr.args:
            if replaced:
                new_args.append(arg)
            else:
                new_arg, replaced = replace_once(arg, target, value)
                new_args.append(new_arg)
        return expr.func(*new_args, evaluate=False), replaced
    return expr, False


# --- Step-by-step generator ---
def generate_steps(expr):
    steps = []
    current_expr = expr

    while True:
        target = find_deepest_evaluable(current_expr)
        if not target:
            break
        result = target.doit(deep=False)
        before_latex = latex(current_expr)
        current_expr, _ = replace_once(current_expr, target, result)
        highlighted = highlight_latex(before_latex, target, result)
        steps.append(
            {
                "description": f"Simplified {latex(target)} to {latex(result)}",
                "expression": highlighted,
            }
        )

    steps.append({"description": "Final Result", "expression": latex(current_expr)})
    return steps


# --- Safe parse and rebuild unevaluated expression ---
def parse_latex_unevaluated(latex_str):
    # Parse the expression first (evaluated)
    parsed = parse_latex(latex_str)

    def rebuild(expr):
        if expr.is_Atom:
            return expr
        new_args = [rebuild(arg) for arg in expr.args]
        return expr.func(*new_args, evaluate=False)

    return rebuild(parsed)


# --- MAIN ---
if __name__ == "__main__":
    latex_input = r"\left(\frac{1 + 1}{2}\right)^2 + \left(\frac{2}{4}\right)^3"
    expr = parse_latex_unevaluated(latex_input)

    print("Parsed Expression:", expr)
    print("Raw Structure:", srepr(expr))

    steps = generate_steps(expr)

    for i, step in enumerate(steps):
        print(f"\nStep {i}: {step['description']}")
        print(f"{step['expression']}")

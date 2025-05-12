from sympy.parsing.latex import parse_latex
from sympy import symbols

# Optional: define symbols if variables are present
x = symbols("x")

# Example LaTeX expression (arithmetic)
latex_expr = r"\frac{8}{2}+\frac{4}{1}"

# Parse LaTeX to SymPy
sympy_expr = parse_latex(latex_expr)

# Evaluate the expression
result = sympy_expr.evalf()

print("Parsed:", sympy_expr)
print("Result:", result)

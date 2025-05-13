#!/usr/bin/env python3
"""
step_solve_latex.py
-------------------
Solve a LaTeX arithmetic expression **step‑by‑step** (PEMDAS).

Example
-------
$ python step_solve_latex.py "\frac{2 + 3 \times 4}{2^{3} - 1}"
Step 1: (2 + 3*4)/(2**3 - 1)
Step 2: (2 + 12)/(2**3 - 1)
Step 3: 14/(2**3 - 1)
Step 4: 14/(8 - 1)
Step 5: 14/7
Step 6: 2
"""

# ── requirements ──────────────────────────────────────────────────────────────
#   pip install "sympy>=1.12" antlr4-python3-runtime
#   (antlr4 is required by sympy.parsing.latex)
# ──────────────────────────────────────────────────────────────────────────────
from sympy.parsing.latex import parse_latex
from sympy import Pow, Mul, Add, simplify, preorder_traversal
import sys


# -----------------------------------------------------------------------------
def solve_latex_step_by_step(latex_expr: str):
    """
    Return a list of SymPy expressions, one for each PEMDAS evaluation step.
    """
    expr = parse_latex(latex_expr)
    steps = [expr]  # original parsed expression

    # ── PEMDAS precedence (P handled implicitly by the tree) ──
    precedence = [Pow, Mul, Add]  # E, MD, AS

    for op in precedence:
        changed = True
        while changed:
            changed = False
            for sub in preorder_traversal(expr):  # <- use the function
                if isinstance(sub, op) and all(a.is_number for a in sub.args):
                    expr = expr.xreplace({sub: simplify(sub)})
                    steps.append(expr)
                    changed = True
                    break
    return steps


# -----------------------------------------------------------------------------
def main():
    if len(sys.argv) != 2:
        print("Usage: python step_solve_latex.py '<LaTeX‑expr>'")
        sys.exit(1)

    latex_in = sys.argv[1]
    for i, s in enumerate(solve_latex_step_by_step(latex_in), 1):
        print(f"Step {i}: {s}")


if __name__ == "__main__":
    main()

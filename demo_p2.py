"""Demostración de la conversión a Forma Normal de Chomsky.

    python demo_p2.py [archivo_de_gramática]      (por defecto grammars/1.txt)
"""
import os
import sys

from cnf import to_cnf_form
from grammar import Grammar, load_grammar
from simplify import simplify


def is_cnf(g: Grammar) -> bool:
    """Indica si todas las producciones tienen una de las dos formas CNF."""
    variables = set(g.productions)
    for bodies in g.productions.values():
        for body in bodies:
            terminal_rule = len(body) == 1 and body[0] not in variables
            binary_rule = len(body) == 2 and set(body) <= variables
            if not (terminal_rule or binary_rule):
                return False
    return True


def main() -> None:
    default = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grammars", "1.txt")
    original = load_grammar(sys.argv[1] if len(sys.argv) > 1 else default)
    simplified = simplify(original)
    cnf = to_cnf_form(simplified)

    print("== Gramática simplificada ==")
    print(simplified)
    print("\n== Forma Normal de Chomsky ==")
    print(cnf)

    auxiliaries = [name for name in cnf.variables if name not in simplified.productions]
    print("\n== Resumen ==")
    print(f"Variables auxiliares: {', '.join(auxiliaries) or '(ninguna)'}")
    print("Todas las producciones están en CNF: " + ("SÍ" if is_cnf(cnf) else "NO"))


if __name__ == "__main__":
    main()

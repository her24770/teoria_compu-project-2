"""Demostración paso a paso de la parte 1 (para el reporte).

    python3 demo_p1.py [archivo_de_gramática]      (por defecto grammars/1.txt)
"""
import os
import sys

from epsilon import eliminate_epsilon, find_nullable
from grammar import load_grammar
from unit import eliminate_unit, find_unit_pairs


def main() -> None:
    default = os.path.join(os.path.dirname(os.path.abspath(__file__)), "grammars", "1.txt")
    g = load_grammar(sys.argv[1] if len(sys.argv) > 1 else default)

    print("== Gramática original ==")
    print(g)
    print(f"Variables: {', '.join(g.variables)}")
    print(f"Terminales: {', '.join(g.terminals)}")

    nullable = find_nullable(g)
    print("\n== Paso 1: anulables ==")
    print("{" + ", ".join(sorted(nullable)) + "}")
    if g.start in nullable:
        print(f"Aviso: {g.start} es anulable; ε se excluye del lenguaje.")
    g1 = eliminate_epsilon(g)
    print("\n== Sin ε-producciones ==")
    print(g1)

    pairs = find_unit_pairs(g1)
    print("\n== Paso 2: pares unarios (sin los triviales (A,A)) ==")
    print(", ".join(f"({a},{b})" for a, b in pairs if a != b) or "(ninguno)")
    g2 = eliminate_unit(g1)
    print("\n== Sin producciones unarias ==")
    print(g2)


if __name__ == "__main__":
    main()

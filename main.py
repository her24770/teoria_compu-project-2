"""Programa principal: gramática -> CNF -> CYK -> SÍ/NO, tiempo y parse tree.

    python3 main.py                              # pide la frase por consola
    python3 main.py "She eats a cake with a fork"
    python3 main.py --grammar grammars/1.txt "( id * id ) + id"
    python3 main.py --steps "the cat drinks the beer"   # muestra la gramática en CNF

Contrato con CYK (``cyk.py``, parte 3):
    parse(g_cnf: Grammar, tokens: list[str]) -> (accepted: bool, tree, seconds: float)
donde ``tree`` es None si no se acepta, o ``(símbolo, [hijos])``; una hoja es
``(terminal, [])``.
"""
from __future__ import annotations

import argparse
import os
import sys

from grammar import Grammar, load_grammar
from simplify import simplify, to_cnf

DEFAULT_GRAMMAR = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "grammars", "english.txt"
)
PUNCTUATION = ".,;:!?"


def tokenize(phrase: str, g: Grammar) -> list[str]:
    """Separa por espacios y quita puntuación final.

    Pasa a minúsculas solo si la gramática no tiene terminales con mayúsculas.
    """
    case_sensitive = any(t != t.lower() for t in g.terminals)
    tokens = []
    for raw in phrase.split():
        token = raw.strip(PUNCTUATION) or raw
        tokens.append(token if case_sensitive else token.lower())
    return tokens


def format_tree(tree, prefix: str = "", is_last: bool = True, is_root: bool = True) -> str:
    """Dibuja el árbol con ramas tipo ``├──`` / ``└──``."""
    label, children = tree
    if is_root:
        lines = [label]
        child_prefix = ""
    else:
        lines = [prefix + ("└── " if is_last else "├── ") + label]
        child_prefix = prefix + ("    " if is_last else "│   ")
    for index, child in enumerate(children):
        last = index == len(children) - 1
        lines.append(format_tree(child, child_prefix, last, False))
    return "\n".join(lines)


def leaves(tree) -> list[str]:
    label, children = tree
    return [label] if not children else [x for c in children for x in leaves(c)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validador CYK de frases.")
    parser.add_argument("phrase", nargs="?", help="frase a validar (si falta, se pregunta)")
    parser.add_argument("-g", "--grammar", default=DEFAULT_GRAMMAR,
                        help="archivo de gramática (por defecto grammars/english.txt)")
    parser.add_argument("--steps", action="store_true",
                        help="muestra la gramática original, simplificada y en CNF")
    args = parser.parse_args(argv)

    try:
        grammar = load_grammar(args.grammar)
        simplified = simplify(grammar)
        cnf = to_cnf(grammar)
    except (OSError, ValueError, RuntimeError) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 2
    try:
        from cyk import parse
    except ImportError:
        print("Error: falta cyk.py con parse(g, tokens) (parte 3)", file=sys.stderr)
        return 2

    if args.steps:
        print("== Gramática original ==", grammar, sep="\n")
        print("\n== Simplificada (sin ε, unarias ni inútiles) ==", simplified, sep="\n")
        print("\n== Forma Normal de Chomsky ==", cnf, sep="\n")
        print()

    phrase = args.phrase if args.phrase is not None else input("Frase: ")
    tokens = tokenize(phrase, grammar)
    if not tokens:
        print("Error: la frase está vacía", file=sys.stderr)
        return 2

    unknown = [t for t in tokens if t not in cnf.terminals]
    accepted, tree, seconds = parse(cnf, tokens)

    print(f"Frase: {' '.join(tokens)}")
    print("Resultado: " + ("SÍ" if accepted else "NO"))
    if unknown:
        print(f"Palabras fuera de la gramática: {', '.join(unknown)}")
    print(f"Tiempo de CYK: {seconds * 1000:.4f} ms")
    if accepted and tree is not None:
        print("\nParse tree:")
        print(format_tree(tree))
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Reconocimiento y construccion de arboles con el algoritmo CYK.

La funcion publica :func:`parse` recibe una gramatica en Forma Normal de
Chomsky (CNF) y una secuencia de terminales. Ademas de decidir pertenencia,
guarda un backpointer por variable para reconstruir una derivacion.
"""
from __future__ import annotations

from time import perf_counter
from typing import Dict, List, Tuple, Union

from grammar import Grammar


# Alias de tipos escritos con ``typing`` para que el modulo funcione desde
# Python 3.9 (``TypeAlias`` y el operador ``|`` entre tipos requieren 3.10).
Tree = Tuple[str, List["Tree"]]
TerminalPointer = Tuple[str, str]
BinaryPointer = Tuple[str, int, str, str]
Backpointer = Union[TerminalPointer, BinaryPointer]
Cell = Dict[str, Backpointer]


def _production_indexes(
    grammar: Grammar,
) -> tuple[dict[str, list[str]], dict[tuple[str, str], list[str]]]:
    """Indexa las producciones CNF por terminal y por pareja de variables."""
    variables = set(grammar.productions)
    terminal_rules: dict[str, list[str]] = {}
    binary_rules: dict[tuple[str, str], list[str]] = {}

    for head, bodies in grammar.productions.items():
        for body in bodies:
            if len(body) == 1 and body[0] not in variables:
                terminal_rules.setdefault(body[0], []).append(head)
            elif len(body) == 2 and body[0] in variables and body[1] in variables:
                binary_rules.setdefault((body[0], body[1]), []).append(head)
            else:
                rendered = " ".join(body) if body else "epsilon"
                raise ValueError(
                    f"la gramatica no esta en CNF: {head} -> {rendered}"
                )

    return terminal_rules, binary_rules


def _build_tree(table: list[list[Cell]], start: int, length: int, symbol: str) -> Tree:
    """Reconstruye recursivamente el arbol indicado por los backpointers."""
    pointer = table[start][length - 1][symbol]

    if pointer[0] == "terminal":
        terminal = pointer[1]
        return symbol, [(terminal, [])]

    _, left_length, left_symbol, right_symbol = pointer
    left_tree = _build_tree(table, start, left_length, left_symbol)
    right_tree = _build_tree(
        table,
        start + left_length,
        length - left_length,
        right_symbol,
    )
    return symbol, [left_tree, right_tree]


def parse(g_cnf: Grammar, tokens: list[str]) -> tuple[bool, Tree | None, float]:
    """Decide si ``tokens`` pertenece a ``g_cnf`` mediante CYK.

    Retorna ``(aceptada, arbol, segundos)``. Si la cadena no pertenece al
    lenguaje, ``arbol`` es ``None``. La gramatica debe contener solamente
    reglas ``A -> terminal`` o ``A -> B C``.

    La tabla se representa como ``table[inicio][longitud - 1]``. Cada celda
    mapea una variable a uno de estos backpointers:

    * ``("terminal", token)`` para una produccion terminal.
    * ``("binary", corte, B, C)`` para una produccion binaria ``A -> B C``.

    Cuando hay ambiguedad se conserva la primera derivacion encontrada, segun
    el orden de las producciones y de los puntos de corte.
    """
    started = perf_counter()
    terminal_rules, binary_rules = _production_indexes(g_cnf)
    words = list(tokens)
    size = len(words)

    # CYK clasico en CNF no reconoce la cadena vacia.
    if size == 0:
        return False, None, perf_counter() - started

    table: list[list[Cell]] = [
        [{} for _ in range(size - start)] for start in range(size)
    ]

    # Caso base: variables que producen cada token directamente.
    for position, token in enumerate(words):
        for head in terminal_rules.get(token, []):
            table[position][0].setdefault(head, ("terminal", token))

    # Casos inductivos: combina todos los cortes de cada subcadena.
    for length in range(2, size + 1):
        for start in range(size - length + 1):
            cell = table[start][length - 1]
            for left_length in range(1, length):
                left_cell = table[start][left_length - 1]
                right_cell = table[start + left_length][length - left_length - 1]
                for left_symbol in left_cell:
                    for right_symbol in right_cell:
                        for head in binary_rules.get(
                            (left_symbol, right_symbol), []
                        ):
                            cell.setdefault(
                                head,
                                (
                                    "binary",
                                    left_length,
                                    left_symbol,
                                    right_symbol,
                                ),
                            )

    accepted = g_cnf.start in table[0][size - 1]
    tree = _build_tree(table, 0, size, g_cnf.start) if accepted else None
    return accepted, tree, perf_counter() - started

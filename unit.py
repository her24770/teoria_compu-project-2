"""Eliminación de producciones unarias (A -> B con B variable).

1. Pares unarios: (A, A) para toda variable; si (A, B) es par y B -> C es
   unaria, entonces (A, C) es par (cierre transitivo).
2. Para cada par (A, B) y cada producción NO unaria B -> α se agrega A -> α.

Se aplica después de eliminar ε-producciones (ver ``epsilon.py``).
"""
from __future__ import annotations

from grammar import Grammar


def _is_unit(body: tuple, variables: set[str]) -> bool:
    return len(body) == 1 and body[0] in variables


def find_unit_pairs(g: Grammar) -> list[tuple[str, str]]:
    """Pares (A, B) con A =>* B usando solo producciones unarias."""
    variables = set(g.productions)
    pairs = [(a, a) for a in g.productions]
    seen = set(pairs)
    index = 0
    while index < len(pairs):
        a, b = pairs[index]
        index += 1
        for body in g.productions.get(b, []):
            if _is_unit(body, variables):
                pair = (a, body[0])
                if pair not in seen:
                    seen.add(pair)
                    pairs.append(pair)
    return pairs


def eliminate_unit(g: Grammar) -> Grammar:
    """Devuelve una gramática equivalente sin producciones unarias."""
    variables = set(g.productions)
    result = Grammar(g.start)
    for head in g.productions:
        result.productions.setdefault(head, [])
    for a, b in find_unit_pairs(g):
        for body in g.productions[b]:
            if not _is_unit(body, variables):
                result.add(a, body)
    return result

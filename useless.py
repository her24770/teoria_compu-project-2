"""Eliminación de símbolos inútiles.

Un símbolo X es útil si existe una derivación S =>* αXβ =>* w con w solo de
terminales. Para quitar los inútiles hay que aplicar los dos pasos en este orden:

1. Quitar los que no generan ninguna cadena de terminales (y toda producción
   que los mencione).
2. Quitar los que no son alcanzables desde el símbolo inicial.

Si el símbolo inicial no genera nada, el lenguaje es vacío y la gramática
resultante conserva solo ``start`` sin producciones.
"""
from __future__ import annotations

from grammar import Grammar


def find_generating(g: Grammar) -> set[str]:
    """Variables que derivan alguna cadena de terminales (punto fijo)."""
    variables = set(g.productions)
    generating: set[str] = set()
    changed = True
    while changed:
        changed = False
        for head, bodies in g.productions.items():
            if head in generating:
                continue
            for body in bodies:
                if all(s not in variables or s in generating for s in body):
                    generating.add(head)
                    changed = True
                    break
    return generating


def find_reachable(g: Grammar) -> set[str]:
    """Símbolos (variables y terminales) alcanzables desde el símbolo inicial."""
    reachable = {g.start}
    pending = [g.start]
    while pending:
        head = pending.pop()
        for body in g.productions.get(head, []):
            for symbol in body:
                if symbol not in reachable:
                    reachable.add(symbol)
                    pending.append(symbol)
    return reachable


def eliminate_useless(g: Grammar) -> Grammar:
    """Devuelve una gramática equivalente sin símbolos inútiles."""
    variables = set(g.productions)
    generating = find_generating(g)

    step1 = Grammar(g.start)
    for head, bodies in g.productions.items():
        if head not in generating:
            continue
        step1.productions.setdefault(head, [])
        for body in bodies:
            if all(s not in variables or s in generating for s in body):
                step1.add(head, body)

    reachable = find_reachable(step1)
    result = Grammar(g.start)
    for head, bodies in step1.productions.items():
        if head in reachable:
            result.productions.setdefault(head, [])
            for body in bodies:
                result.add(head, body)
    return result

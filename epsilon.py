"""Eliminación de ε-producciones.

1. Anulables: A es anulable si A -> ε, o A -> X1...Xn con todos los Xi anulables
   (punto fijo).
2. Para cada producción A -> X1...Xn se agregan todas las variantes que resultan
   de omitir cualquier subconjunto de los Xi anulables (2^m variantes, m = número
   de anulables en el cuerpo), descartando la variante vacía.

El lenguaje resultante es L(G) - {ε}: si el símbolo inicial es anulable, la
cadena vacía deja de pertenecer al lenguaje (``start in find_nullable(g)`` lo
indica).
"""
from __future__ import annotations

from itertools import product

from grammar import Grammar


def find_nullable(g: Grammar) -> set[str]:
    """Conjunto de variables que derivan la cadena vacía."""
    nullable: set[str] = set()
    changed = True
    while changed:
        changed = False
        for head, bodies in g.productions.items():
            if head in nullable:
                continue
            if any(all(s in nullable for s in body) for body in bodies):
                nullable.add(head)
                changed = True
    return nullable


def _variants(body: tuple, nullable: set[str]):
    """Todas las formas de conservar u omitir cada símbolo anulable del cuerpo."""
    positions = [i for i, s in enumerate(body) if s in nullable]
    for keep in product((True, False), repeat=len(positions)):
        omit = {p for p, k in zip(positions, keep) if not k}
        yield tuple(s for i, s in enumerate(body) if i not in omit)


def eliminate_epsilon(g: Grammar) -> Grammar:
    """Devuelve una gramática equivalente (salvo ε) sin ε-producciones."""
    nullable = find_nullable(g)
    result = Grammar(g.start)
    for head, bodies in g.productions.items():
        result.productions.setdefault(head, [])
        for body in bodies:
            for variant in _variants(body, nullable):
                if variant:
                    result.add(head, variant)
    return result

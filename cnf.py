"""Conversión de una gramática simplificada a Forma Normal de Chomsky."""
from __future__ import annotations

from grammar import Grammar


def _symbols(g: Grammar) -> set[str]:
    """Devuelve todos los nombres usados por variables y terminales."""
    symbols = set(g.productions)
    for bodies in g.productions.values():
        for body in bodies:
            symbols.update(body)
    return symbols


def _fresh_variable(
    prefix: str, used: set[str], next_index: int
) -> tuple[str, int]:
    """Crea un nombre auxiliar que no colisione con símbolos existentes."""
    while f"{prefix}_{next_index}" in used:
        next_index += 1
    name = f"{prefix}_{next_index}"
    used.add(name)
    return name, next_index + 1


def _replace_terminals(g: Grammar) -> Grammar:
    """Reemplaza terminales dentro de cuerpos de longitud dos o mayor."""
    variables = set(g.productions)
    used = _symbols(g)
    terminal_variables: dict[str, str] = {}
    next_index = 1

    # Conserva el orden de las variables originales y agrega las auxiliares al final.
    result = Grammar(g.start, {head: [] for head in g.productions})

    for head, bodies in g.productions.items():
        for body in bodies:
            if len(body) < 2:
                result.add(head, body)
                continue

            converted = []
            for symbol in body:
                if symbol in variables:
                    converted.append(symbol)
                    continue

                if symbol not in terminal_variables:
                    name, next_index = _fresh_variable("T", used, next_index)
                    terminal_variables[symbol] = name
                converted.append(terminal_variables[symbol])
            result.add(head, converted)

    for terminal, variable in terminal_variables.items():
        result.add(variable, (terminal,))

    return result


def _decompose_long_bodies(g: Grammar) -> Grammar:
    """Descompone cada cuerpo largo en una cadena de cuerpos binarios."""
    used = _symbols(g)
    next_index = 1
    result = Grammar(g.start, {head: [] for head in g.productions})

    for head, bodies in g.productions.items():
        for body in bodies:
            if len(body) <= 2:
                result.add(head, body)
                continue

            current_head = head
            for symbol in body[:-2]:
                helper, next_index = _fresh_variable("C", used, next_index)
                result.add(current_head, (symbol, helper))
                current_head = helper
            result.add(current_head, body[-2:])

    return result


def to_cnf_form(g: Grammar) -> Grammar:
    """Convierte una gramática simplificada a Forma Normal de Chomsky.

    Primero sustituye los terminales que aparecen en cuerpos largos y luego
    descompone los cuerpos de tres o más símbolos. La entrada no se modifica.
    """
    return _decompose_long_bodies(_replace_terminals(g))

"""Conversión de una gramática simplificada a Forma Normal de Chomsky.
"""
from __future__ import annotations

from grammar import Grammar


def _symbols(g: Grammar) -> set[str]:
    """Devuelve todos los nombres usados por variables y terminales."""
    symbols = set(g.productions)
    for bodies in g.productions.values():
        for body in bodies:
            symbols.update(body)
    return symbols


def _fresh_variable(used: set[str], next_index: int) -> tuple[str, int]:
    """Crea un nombre ``T_n`` que no colisione con ningún símbolo existente."""
    while f"T_{next_index}" in used:
        next_index += 1
    name = f"T_{next_index}"
    used.add(name)
    return name, next_index + 1


def to_cnf_form(g: Grammar) -> Grammar:
    """Reemplaza terminales dentro de cuerpos de longitud dos o mayor.

    La entrada debe ser una gramática ya simplificada. La función construye
    una gramática nueva y reutiliza la misma variable auxiliar cuando un
    terminal aparece en varios cuerpos largos.
    """
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
                    name, next_index = _fresh_variable(used, next_index)
                    terminal_variables[symbol] = name
                converted.append(terminal_variables[symbol])
            result.add(head, converted)

    for terminal, variable in terminal_variables.items():
        result.add(variable, (terminal,))

    return result

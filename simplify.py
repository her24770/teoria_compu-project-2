"""Pipeline de simplificación: ε -> unarias -> inútiles -> CNF.

* ``simplify(g)`` aplica los tres pasos de simplificación (partes 1).
* ``to_cnf(g)`` agrega la conversión a Forma Normal de Chomsky, que vive en
  ``cnf.py`` (parte 2) y debe exponer ``to_cnf_form(g) -> Grammar``.
"""
from __future__ import annotations

from epsilon import eliminate_epsilon
from grammar import Grammar
from unit import eliminate_unit
from useless import eliminate_useless


def simplify(g: Grammar) -> Grammar:
    """Sin ε-producciones, sin unarias y sin símbolos inútiles (en ese orden)."""
    return eliminate_useless(eliminate_unit(eliminate_epsilon(g)))


def to_cnf(g: Grammar) -> Grammar:
    """Simplifica y convierte a CNF. Acepta gramáticas que ya estén en CNF."""
    try:
        from cnf import to_cnf_form
    except ImportError as error:  # la parte 2 todavía no está integrada
        raise RuntimeError(
            "falta cnf.py con to_cnf_form(g) (conversión a CNF, parte 2)"
        ) from error
    return to_cnf_form(simplify(g))

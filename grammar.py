"""Modelo de gramática libre de contexto y lector de archivos .txt.

Formato del archivo (una regla por línea, símbolos separados por espacios):

    E -> T X
    X -> + T X | e
    F -> ( E ) | id

* La flecha puede ser ``->`` o ``→``; las alternativas se separan con ``|``.
* ``e`` (también ``ε``, ``epsilon``) como alternativa completa es la cadena vacía.
* Una variable es todo símbolo que aparece a la izquierda de alguna regla;
  cualquier otro símbolo es un terminal.
* El símbolo inicial es la cabeza de la primera regla.
* Las líneas vacías y las que empiezan con ``#`` se ignoran.
"""
from __future__ import annotations

# Cuerpo vacío: la producción A -> ε se guarda como (A, ()).
EPSILON: tuple = ()
EPSILON_TOKENS = {"e", "ε", "ɛ", "epsilon", "eps"}
ARROWS = ("->", "→")

Body = tuple  # tuple[str, ...]


class GrammarError(ValueError):
    """Error de formato al leer una gramática."""


class Grammar:
    """CFG como diccionario variable -> lista de cuerpos (sin duplicados, en orden)."""

    def __init__(self, start: str, productions: dict | None = None):
        self.start = start
        self.productions: dict[str, list[Body]] = {}
        for head, bodies in (productions or {}).items():
            self.productions.setdefault(head, [])
            for body in bodies:
                self.add(head, body)
        self.productions.setdefault(start, [])

    def add(self, head: str, body) -> None:
        """Agrega head -> body si todavía no existe."""
        body = tuple(body)
        bodies = self.productions.setdefault(head, [])
        if body not in bodies:
            bodies.append(body)

    @property
    def variables(self) -> list[str]:
        return list(self.productions)

    @property
    def terminals(self) -> list[str]:
        variables = set(self.productions)
        seen: list[str] = []
        for bodies in self.productions.values():
            for body in bodies:
                for symbol in body:
                    if symbol not in variables and symbol not in seen:
                        seen.append(symbol)
        return seen

    def copy(self) -> "Grammar":
        return Grammar(self.start, self.productions)

    def as_sets(self) -> dict[str, set]:
        """Vista sin orden, útil para comparar gramáticas."""
        return {head: set(bodies) for head, bodies in self.productions.items()}

    def __eq__(self, other) -> bool:
        return (
            isinstance(other, Grammar)
            and self.start == other.start
            and self.as_sets() == other.as_sets()
        )

    def __str__(self) -> str:
        lines = []
        for head, bodies in self.productions.items():
            if not bodies:
                continue
            alts = " | ".join(" ".join(b) if b else "ε" for b in bodies)
            lines.append(f"{head} -> {alts}")
        return "\n".join(lines)

    def __repr__(self) -> str:
        return f"Grammar(start={self.start!r}, productions={self.productions!r})"


def parse_grammar(text: str) -> Grammar:
    """Construye una Grammar a partir del texto de un archivo de gramática."""
    productions: dict[str, list[Body]] = {}
    start = None
    for number, raw in enumerate(text.splitlines(), start=1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        arrow = next((a for a in ARROWS if a in line), None)
        if arrow is None:
            raise GrammarError(f"línea {number}: falta la flecha '->': {raw!r}")
        left, right = line.split(arrow, 1)
        head = left.strip()
        if not head or len(head.split()) != 1:
            raise GrammarError(
                f"línea {number}: la cabeza debe ser un único símbolo: {raw!r}"
            )
        if start is None:
            start = head
        bodies = productions.setdefault(head, [])
        for alternative in right.split("|"):
            tokens = alternative.split()
            if not tokens:
                raise GrammarError(
                    f"línea {number}: alternativa vacía (use 'e' para ε): {raw!r}"
                )
            is_epsilon = len(tokens) == 1 and tokens[0] in EPSILON_TOKENS
            body = EPSILON if is_epsilon else tuple(tokens)
            if body not in bodies:
                bodies.append(body)
    if start is None:
        raise GrammarError("la gramática está vacía")
    return Grammar(start, productions)


def load_grammar(path: str) -> Grammar:
    """Lee una gramática desde un archivo de texto UTF-8."""
    with open(path, encoding="utf-8") as handle:
        return parse_grammar(handle.read())

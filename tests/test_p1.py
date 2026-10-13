"""Pruebas de la parte 1: lector de gramáticas, ε-producciones y unarias.

Ejecutar desde la raíz del repo:
    python3 -m unittest discover -s tests -t . -v
"""
import os
import unittest

from epsilon import eliminate_epsilon, find_nullable
from grammar import Grammar, GrammarError, load_grammar, parse_grammar
from unit import eliminate_unit, find_unit_pairs

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def path(name: str) -> str:
    return os.path.join(ROOT, "grammars", name)


def language(g: Grammar, max_len: int, slack: int = 6) -> set:
    """Cadenas terminales de longitud <= max_len, por expansión del más a la izquierda."""
    variables = set(g.productions)
    found, seen, stack = set(), set(), [(g.start,)]
    while stack:
        form = stack.pop()
        if form in seen:
            continue
        seen.add(form)
        index = next((i for i, s in enumerate(form) if s in variables), None)
        if index is None:
            found.add(form)
            continue
        for body in g.productions[form[index]]:
            new = form[:index] + body + form[index + 1:]
            terminals = sum(1 for s in new if s not in variables)
            if terminals <= max_len and len(new) <= max_len + slack:
                stack.append(new)
    return found


class ParserTests(unittest.TestCase):
    def test_arrow_alternatives_and_epsilon(self):
        g = parse_grammar("S -> a S | e\n")
        self.assertEqual(g.start, "S")
        self.assertEqual(g.productions["S"], [("a", "S"), ()])

    def test_unicode_arrow_and_epsilon(self):
        g = parse_grammar("S → a | ε")
        self.assertEqual(g.productions["S"], [("a",), ()])

    def test_comments_blank_lines_and_repeated_head(self):
        g = parse_grammar("# c\n\nS -> a\n\nS -> b\nT -> S\n")
        self.assertEqual(g.productions["S"], [("a",), ("b",)])
        self.assertEqual(g.start, "S")

    def test_variables_and_terminals(self):
        g = load_grammar(path("1.txt"))
        self.assertEqual(g.variables, ["E", "X", "T", "Y", "F"])
        self.assertEqual(set(g.terminals), {"+", "*", "(", ")", "id"})

    def test_duplicates_removed(self):
        g = parse_grammar("S -> a | a | b")
        self.assertEqual(g.productions["S"], [("a",), ("b",)])

    def test_load_english_grammar(self):
        g = load_grammar(path("english.txt"))
        self.assertEqual(g.start, "S")
        self.assertEqual(g.productions["S"], [("NP", "VP")])
        self.assertIn(("Det", "N"), g.productions["NP"])
        self.assertIn(("she",), g.productions["NP"])
        self.assertEqual(len(g.productions["N"]), 11)
        self.assertEqual(set(g.productions["Det"]), {("a",), ("the",)})

    def test_load_cnf_grammar(self):
        g = load_grammar(path("1-cnf.txt"))
        self.assertEqual(g.start, "E")
        self.assertEqual(len(g.variables), 12)
        self.assertEqual(set(g.terminals), {"+", "*", "(", ")", "id"})
        self.assertEqual(g.productions["L"], [("(",)])

    def test_roundtrip_str(self):
        g = load_grammar(path("1.txt"))
        self.assertEqual(parse_grammar(str(g)), g)

    def test_errors(self):
        for bad in ("S a b", "S T -> a", "-> a", "S -> a |", "", "# solo comentario"):
            with self.subTest(bad=bad):
                with self.assertRaises(GrammarError):
                    parse_grammar(bad)


class EpsilonTests(unittest.TestCase):
    def test_nullable_simple(self):
        g = parse_grammar("S -> A B\nA -> a A | e\nB -> b B | e")
        self.assertEqual(find_nullable(g), {"S", "A", "B"})

    def test_nullable_indirect_and_not_nullable(self):
        g = parse_grammar("S -> A C\nA -> B\nB -> e\nC -> c")
        self.assertEqual(find_nullable(g), {"A", "B"})

    def test_nullable_1txt(self):
        self.assertEqual(find_nullable(load_grammar(path("1.txt"))), {"X", "Y"})

    def test_book_example_four_variants(self):
        # S -> A b A con A anulable genera 2^2 = 4 variantes (menos ninguna vacía).
        g = eliminate_epsilon(parse_grammar("S -> A b A\nA -> a | e"))
        self.assertEqual(
            set(g.productions["S"]), {("A", "b", "A"), ("b", "A"), ("A", "b"), ("b",)}
        )
        self.assertEqual(g.productions["A"], [("a",)])

    def test_1txt_matches_hand_solution(self):
        g = eliminate_epsilon(load_grammar(path("1.txt")))
        self.assertEqual(
            g.as_sets(),
            {
                "E": {("T", "X"), ("T",)},
                "X": {("+", "T", "X"), ("+", "T")},
                "T": {("F", "Y"), ("F",)},
                "Y": {("*", "F", "Y"), ("*", "F")},
                "F": {("(", "E", ")"), ("id",)},
            },
        )

    def test_no_epsilon_left(self):
        g = eliminate_epsilon(parse_grammar("S -> A S B | e\nA -> a | e\nB -> b | e"))
        self.assertTrue(all(body for bodies in g.productions.values() for body in bodies))

    def test_epsilon_free_grammar_unchanged(self):
        g = load_grammar(path("english.txt"))
        self.assertEqual(eliminate_epsilon(g), g)

    def test_input_not_mutated(self):
        g = load_grammar(path("1.txt"))
        before = g.copy()
        eliminate_epsilon(g)
        self.assertEqual(g, before)

    def test_language_preserved_minus_epsilon(self):
        for text in (
            "S -> A B\nA -> a A | e\nB -> b B | e",
            "S -> ( S ) S | e",
        ):
            g = parse_grammar(text)
            with self.subTest(text=text):
                expected = language(g, 6) - {()}
                self.assertEqual(language(eliminate_epsilon(g), 6), expected)

    def test_language_preserved_1txt(self):
        g = load_grammar(path("1.txt"))
        self.assertEqual(language(eliminate_epsilon(g), 5), language(g, 5) - {()})

    def test_start_symbol_only_epsilon_gives_empty_language(self):
        g = eliminate_epsilon(parse_grammar("S -> e"))
        self.assertEqual(g.productions["S"], [])
        self.assertEqual(language(g, 4), set())


class UnitTests(unittest.TestCase):
    def test_unit_pairs_chain(self):
        g = parse_grammar("A -> B | a\nB -> C\nC -> c")
        self.assertEqual(
            set(find_unit_pairs(g)),
            {("A", "A"), ("B", "B"), ("C", "C"), ("A", "B"), ("A", "C"), ("B", "C")},
        )

    def test_unit_pairs_cycle(self):
        g = parse_grammar("A -> B\nB -> A | b")
        self.assertEqual(
            set(find_unit_pairs(g)), {("A", "A"), ("B", "B"), ("A", "B"), ("B", "A")}
        )

    def test_terminal_body_is_not_unit(self):
        g = parse_grammar("A -> a")
        self.assertEqual(find_unit_pairs(g), [("A", "A")])

    def test_chain_elimination(self):
        g = eliminate_unit(parse_grammar("A -> B | a\nB -> C\nC -> c"))
        self.assertEqual(
            g.as_sets(),
            {"A": {("a",), ("c",)}, "B": {("c",)}, "C": {("c",)}},
        )

    def test_cycle_elimination(self):
        g = eliminate_unit(parse_grammar("A -> B\nB -> A | b"))
        self.assertEqual(g.as_sets(), {"A": {("b",)}, "B": {("b",)}})

    def test_no_unit_left(self):
        g = eliminate_unit(eliminate_epsilon(load_grammar(path("1.txt"))))
        variables = set(g.productions)
        for bodies in g.productions.values():
            for body in bodies:
                self.assertFalse(len(body) == 1 and body[0] in variables, body)

    def test_pipeline_1txt_matches_hand_solution(self):
        # Gramática "Nueva G" del ejemplo manuscrito (con X = E', Y = T').
        g = eliminate_unit(eliminate_epsilon(load_grammar(path("1.txt"))))
        self.assertEqual(
            g.as_sets(),
            {
                "E": {("T", "X"), ("F", "Y"), ("(", "E", ")"), ("id",)},
                "X": {("+", "T", "X"), ("+", "T")},
                "T": {("F", "Y"), ("(", "E", ")"), ("id",)},
                "Y": {("*", "F", "Y"), ("*", "F")},
                "F": {("(", "E", ")"), ("id",)},
            },
        )

    def test_pipeline_english_grammar_has_no_unit(self):
        g = load_grammar(path("english.txt"))
        out = eliminate_unit(eliminate_epsilon(g))
        # Ya no tenía unarias: debe quedar igual.
        self.assertEqual(out, g)

    def test_input_not_mutated(self):
        g = parse_grammar("A -> B\nB -> b")
        before = g.copy()
        eliminate_unit(g)
        self.assertEqual(g, before)

    def test_language_preserved(self):
        for text in (
            "E -> E + T | T\nT -> T * F | F\nF -> ( E ) | id",
            "S -> A | B\nA -> B | a\nB -> b | S c",
        ):
            g = parse_grammar(text)
            with self.subTest(text=text):
                self.assertEqual(language(eliminate_unit(g), 5), language(g, 5))

    def test_language_preserved_1txt_full_pipeline(self):
        g = load_grammar(path("1.txt"))
        out = eliminate_unit(eliminate_epsilon(g))
        self.assertEqual(language(out, 5), language(g, 5) - {()})


if __name__ == "__main__":
    unittest.main()

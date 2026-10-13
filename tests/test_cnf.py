"""Pruebas de la conversión a Forma Normal de Chomsky."""
import unittest

from cnf import to_cnf_form
from grammar import Grammar, load_grammar, parse_grammar
from simplify import simplify, to_cnf
from tests.test_p1 import language, path


class ReplaceTerminalsTests(unittest.TestCase):
    def test_replaces_terminal_in_long_body(self):
        g = parse_grammar("S -> A + B\nA -> a\nB -> b")

        out = to_cnf_form(g)

        self.assertEqual(out.productions["S"], [("A", "C_1")])
        self.assertEqual(out.productions["C_1"], [("T_1", "B")])
        self.assertEqual(out.productions["T_1"], [("+",)])

    def test_reuses_variable_for_repeated_terminal(self):
        g = parse_grammar("S -> a A | B a\nA -> x\nB -> y")

        out = to_cnf_form(g)

        self.assertEqual(
            set(out.productions["S"]),
            {("T_1", "A"), ("B", "T_1")},
        )
        self.assertEqual(out.productions["T_1"], [("a",)])

    def test_terminal_only_body_is_unchanged(self):
        g = parse_grammar("S -> a | A B\nA -> x\nB -> y")

        out = to_cnf_form(g)

        self.assertEqual(out.productions["S"], [("a",), ("A", "B")])
        self.assertNotIn("T_1", out.productions)

    def test_generated_name_avoids_all_existing_symbols(self):
        g = parse_grammar("S -> a A\nA -> T_2\nT_1 -> x")

        out = to_cnf_form(g)

        self.assertEqual(out.productions["S"], [("T_3", "A")])
        self.assertEqual(out.productions["T_3"], [("a",)])

    def test_long_bodies_contain_only_variables_after_replacement(self):
        g = parse_grammar("S -> a A + B\nA -> x\nB -> y")

        out = to_cnf_form(g)
        variables = set(out.productions)

        for bodies in out.productions.values():
            for body in bodies:
                if len(body) >= 2:
                    self.assertTrue(set(body) <= variables)

    def test_input_is_not_mutated(self):
        g = parse_grammar("S -> A + B\nA -> a\nB -> b")
        before = g.copy()

        to_cnf_form(g)

        self.assertEqual(g, before)


class DecomposeLongBodiesTests(unittest.TestCase):
    def test_binary_body_is_unchanged(self):
        g = parse_grammar("S -> A B\nA -> a\nB -> b")

        out = to_cnf_form(g)

        self.assertEqual(out, g)

    def test_decomposes_body_of_three_variables(self):
        g = parse_grammar("S -> A B C\nA -> a\nB -> b\nC -> c")

        out = to_cnf_form(g)

        self.assertEqual(out.productions["S"], [("A", "C_1")])
        self.assertEqual(out.productions["C_1"], [("B", "C")])

    def test_decomposes_body_of_four_variables(self):
        g = parse_grammar("S -> A B C D\nA -> a\nB -> b\nC -> c\nD -> d")

        out = to_cnf_form(g)

        self.assertEqual(out.productions["S"], [("A", "C_1")])
        self.assertEqual(out.productions["C_1"], [("B", "C_2")])
        self.assertEqual(out.productions["C_2"], [("C", "D")])

    def test_each_long_body_gets_different_helpers(self):
        g = parse_grammar(
            "S -> A B C | D E F\n"
            "A -> a\nB -> b\nC -> c\nD -> d\nE -> e1\nF -> f"
        )

        out = to_cnf_form(g)

        self.assertEqual(
            set(out.productions["S"]),
            {("A", "C_1"), ("D", "C_2")},
        )
        self.assertEqual(out.productions["C_1"], [("B", "C")])
        self.assertEqual(out.productions["C_2"], [("E", "F")])

    def test_helper_name_avoids_all_existing_symbols(self):
        g = parse_grammar(
            "S -> A B C\nA -> a\nB -> b\nC -> C_2\nC_1 -> x"
        )

        out = to_cnf_form(g)

        self.assertEqual(out.productions["S"], [("A", "C_3")])
        self.assertEqual(out.productions["C_3"], [("B", "C")])

    def test_result_has_only_cnf_production_shapes(self):
        g = parse_grammar(
            "S -> a A + B | C D\nA -> x\nB -> y\nC -> c\nD -> d"
        )

        out = to_cnf_form(g)
        variables = set(out.productions)

        for bodies in out.productions.values():
            for body in bodies:
                valid_terminal = len(body) == 1 and body[0] not in variables
                valid_pair = len(body) == 2 and set(body) <= variables
                self.assertTrue(valid_terminal or valid_pair, (body, variables))


class CnfIntegrationTests(unittest.TestCase):
    def assert_is_cnf(self, g: Grammar) -> None:
        variables = set(g.productions)
        for head, bodies in g.productions.items():
            for body in bodies:
                valid_terminal = len(body) == 1 and body[0] not in variables
                valid_pair = len(body) == 2 and set(body) <= variables
                self.assertTrue(
                    valid_terminal or valid_pair,
                    f"producción fuera de CNF: {head} -> {' '.join(body)}",
                )

    def test_project_grammars_convert_to_cnf(self):
        for name in ("1.txt", "english.txt"):
            original = load_grammar(path(name))

            with self.subTest(name=name):
                out = to_cnf(original)
                self.assert_is_cnf(out)
                self.assertEqual(out.start, original.start)
                self.assertEqual(set(out.terminals), set(original.terminals))

    def test_already_cnf_grammar_is_unchanged(self):
        g = load_grammar(path("1-cnf.txt"))

        out = to_cnf_form(g)

        self.assertEqual(out, g)
        self.assert_is_cnf(out)

    def test_empty_grammar_is_preserved(self):
        g = Grammar("S")

        out = to_cnf_form(g)

        self.assertEqual(out, g)
        self.assertEqual(out.productions, {"S": []})

    def test_language_is_preserved(self):
        g = parse_grammar(
            "S -> A S B | x C | A B\nA -> a\nB -> b\nC -> c"
        )

        out = to_cnf_form(g)

        self.assertEqual(language(out, 5, slack=12), language(g, 5, slack=12))
        self.assert_is_cnf(out)

    def test_pipeline_matches_explicit_composition(self):
        g = load_grammar(path("1.txt"))

        self.assertEqual(to_cnf(g), to_cnf_form(simplify(g)))


if __name__ == "__main__":
    unittest.main()

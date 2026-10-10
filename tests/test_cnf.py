"""Pruebas de la conversión a Forma Normal de Chomsky."""
import unittest

from cnf import to_cnf_form
from grammar import parse_grammar


class ReplaceTerminalsTests(unittest.TestCase):
    def test_replaces_terminal_in_long_body(self):
        g = parse_grammar("S -> A + B\nA -> a\nB -> b")

        out = to_cnf_form(g)

        self.assertEqual(out.productions["S"], [("A", "T_1", "B")])
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


if __name__ == "__main__":
    unittest.main()

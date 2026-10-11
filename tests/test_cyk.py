"""Pruebas unitarias y de integracion para el algoritmo CYK."""
import unittest

from cyk import parse
from grammar import Grammar, load_grammar, parse_grammar
from main import leaves, printable_tree
from simplify import to_cnf
from tests.test_p1 import path


class CykCoreTests(unittest.TestCase):
    def test_accepts_and_builds_expected_tree(self):
        grammar = parse_grammar("S -> NP VP\nNP -> she\nVP -> eats")

        accepted, tree, seconds = parse(grammar, ["she", "eats"])

        self.assertTrue(accepted)
        self.assertEqual(
            tree,
            (
                "S",
                [
                    ("NP", [("she", [])]),
                    ("VP", [("eats", [])]),
                ],
            ),
        )
        self.assertGreaterEqual(seconds, 0.0)

    def test_rejects_wrong_order(self):
        grammar = parse_grammar("S -> NP VP\nNP -> she\nVP -> eats")

        accepted, tree, seconds = parse(grammar, ["eats", "she"])

        self.assertFalse(accepted)
        self.assertIsNone(tree)
        self.assertIsInstance(seconds, float)

    def test_backpointers_reconstruct_three_token_derivation(self):
        grammar = parse_grammar(
            "S -> A X\nX -> B C\nA -> one\nB -> two\nC -> three"
        )

        accepted, tree, _ = parse(grammar, ["one", "two", "three"])

        self.assertTrue(accepted)
        self.assertEqual(leaves(tree), ["one", "two", "three"])
        self.assertEqual(tree[0], "S")
        self.assertEqual(tree[1][1][0], "X")

    def test_ambiguous_grammar_returns_one_valid_tree(self):
        grammar = parse_grammar("S -> S S | a")

        accepted, tree, _ = parse(grammar, ["a", "a", "a"])

        self.assertTrue(accepted)
        self.assertEqual(leaves(tree), ["a", "a", "a"])

    def test_unknown_token_is_rejected(self):
        grammar = parse_grammar("S -> known")

        self.assertEqual(parse(grammar, ["unknown"])[0:2], (False, None))

    def test_empty_input_is_rejected(self):
        grammar = parse_grammar("S -> word")

        self.assertEqual(parse(grammar, [])[0:2], (False, None))

    def test_input_tokens_are_not_modified(self):
        grammar = parse_grammar("S -> A B\nA -> a\nB -> b")
        tokens = ["a", "b"]

        parse(grammar, tokens)

        self.assertEqual(tokens, ["a", "b"])

    def test_rejects_non_cnf_grammar(self):
        grammar = parse_grammar("S -> A B C\nA -> a\nB -> b\nC -> c")

        with self.assertRaisesRegex(ValueError, "no esta en CNF"):
            parse(grammar, ["a", "b", "c"])

    def test_empty_language_rejects(self):
        grammar = Grammar("S")

        self.assertEqual(parse(grammar, ["anything"])[0:2], (False, None))

    def test_tree_has_ascii_fallback_for_windows_console(self):
        tree = ("S", [("a", []), ("b", [])])

        rendered = printable_tree(tree, "cp1252")

        self.assertIn("|-- a", rendered)
        self.assertIn("`-- b", rendered)


class CykProjectGrammarTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.english = to_cnf(load_grammar(path("english.txt")))
        cls.arithmetic = to_cnf(load_grammar(path("1.txt")))

    def assert_parse(self, grammar, phrase, expected):
        tokens = phrase.split()
        accepted, tree, seconds = parse(grammar, tokens)
        self.assertEqual(accepted, expected)
        self.assertGreaterEqual(seconds, 0.0)
        if expected:
            self.assertIsNotNone(tree)
            self.assertEqual(tree[0], grammar.start)
            self.assertEqual(leaves(tree), tokens)
        else:
            self.assertIsNone(tree)

    def test_english_phrases_in_language(self):
        for phrase in (
            "she eats a cake with a fork",
            "the cat drinks the beer",
            "he cooks",
            "she cuts the meat in the oven with a knife",
        ):
            with self.subTest(phrase=phrase):
                self.assert_parse(self.english, phrase, True)

    def test_english_phrases_not_in_language(self):
        for phrase in (
            "cake the eats she",
            "the cat",
            "she eats with",
            "she eats a pizza",
            "the the cat drinks",
            "she",
        ):
            with self.subTest(phrase=phrase):
                self.assert_parse(self.english, phrase, False)

    def test_arithmetic_phrases(self):
        self.assert_parse(self.arithmetic, "( id * id ) + id", True)
        self.assert_parse(self.arithmetic, "id + * id", False)
        self.assert_parse(self.arithmetic, "( id + id", False)


if __name__ == "__main__":
    unittest.main()

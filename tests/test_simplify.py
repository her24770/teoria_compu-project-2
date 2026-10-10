"""Pruebas de símbolos inútiles, del pipeline de simplificación y de main.py.

Las pruebas de extremo a extremo se ejecutan solo si ya existen ``cnf.py``
(parte 2) y ``cyk.py`` (parte 3); si no, se saltan.
"""
import contextlib
import importlib.util
import io
import os
import unittest

import main as cli
from epsilon import eliminate_epsilon
from grammar import load_grammar, parse_grammar
from simplify import simplify
from tests.test_p1 import language, path
from unit import eliminate_unit
from useless import eliminate_useless, find_generating, find_reachable

HAS_CNF = importlib.util.find_spec("cnf") is not None
HAS_CYK = importlib.util.find_spec("cyk") is not None
INTEGRATION = unittest.skipUnless(HAS_CNF and HAS_CYK, "faltan cnf.py y/o cyk.py")


class UselessTests(unittest.TestCase):
    def test_generating(self):
        g = parse_grammar("S -> A B | a\nA -> a\nB -> B b")
        self.assertEqual(find_generating(g), {"S", "A"})

    def test_reachable(self):
        g = parse_grammar("S -> A b\nA -> a\nC -> c")
        self.assertEqual(find_reachable(g), {"S", "A", "b", "a"})

    def test_non_generating_removed_then_unreachable(self):
        # Ejemplo del curso: S -> AB | a, A -> a (B no genera) => S -> a.
        g = eliminate_useless(parse_grammar("S -> A B | a\nA -> a\nB -> B b"))
        self.assertEqual(g.as_sets(), {"S": {("a",)}})

    def test_unreachable_removed(self):
        g = eliminate_useless(parse_grammar("S -> a\nA -> b"))
        self.assertEqual(g.as_sets(), {"S": {("a",)}})

    def test_order_matters(self):
        # Alcanzabilidad primero dejaría A; generadores primero la elimina con B.
        g = eliminate_useless(parse_grammar("S -> a | B\nB -> A b\nA -> A a"))
        self.assertEqual(g.as_sets(), {"S": {("a",)}})

    def test_start_not_generating_gives_empty_language(self):
        g = eliminate_useless(parse_grammar("S -> S a"))
        self.assertEqual(g.productions, {"S": []})
        self.assertEqual(language(g, 4), set())

    def test_useful_grammar_unchanged(self):
        for name in ("1.txt", "english.txt", "1-cnf.txt"):
            g = load_grammar(path(name))
            with self.subTest(name=name):
                self.assertEqual(eliminate_useless(g), g)

    def test_input_not_mutated(self):
        g = parse_grammar("S -> A B | a\nA -> a\nB -> B b")
        before = g.copy()
        eliminate_useless(g)
        self.assertEqual(g, before)

    def test_language_preserved(self):
        g = parse_grammar("S -> a S b | a b | A\nA -> A a\nC -> c S")
        out = eliminate_useless(g)
        self.assertEqual(language(out, 6), language(g, 6))
        self.assertNotIn("A", out.productions)
        self.assertNotIn("C", out.productions)


class SimplifyTests(unittest.TestCase):
    def test_pipeline_is_composition(self):
        g = load_grammar(path("1.txt"))
        self.assertEqual(
            simplify(g), eliminate_useless(eliminate_unit(eliminate_epsilon(g)))
        )

    def test_english_unchanged(self):
        g = load_grammar(path("english.txt"))
        self.assertEqual(simplify(g), g)

    def test_all_three_cleanups_together(self):
        g = parse_grammar(
            "S -> A B | C\nA -> a | e\nB -> b | A\nC -> D\nD -> d\nX -> x\nY -> Y y"
        )
        out = simplify(g)
        variables = set(out.productions)
        for head, bodies in out.productions.items():
            for body in bodies:
                self.assertTrue(body, "queda una ε-producción")
                self.assertFalse(len(body) == 1 and body[0] in variables, "queda unaria")
        self.assertNotIn("X", out.productions)
        self.assertNotIn("Y", out.productions)
        self.assertEqual(language(out, 4), language(g, 4) - {()})

    def test_1txt_result(self):
        out = simplify(load_grammar(path("1.txt")))
        self.assertEqual(
            out.as_sets(),
            {
                "E": {("T", "X"), ("F", "Y"), ("(", "E", ")"), ("id",)},
                "X": {("+", "T", "X"), ("+", "T")},
                "T": {("F", "Y"), ("(", "E", ")"), ("id",)},
                "Y": {("*", "F", "Y"), ("*", "F")},
                "F": {("(", "E", ")"), ("id",)},
            },
        )


class CliHelpersTests(unittest.TestCase):
    def setUp(self):
        self.english = load_grammar(path("english.txt"))
        self.arith = load_grammar(path("1.txt"))

    def test_tokenize_lowercases_and_strips_punctuation(self):
        self.assertEqual(
            cli.tokenize("She eats a Cake with a fork.", self.english),
            ["she", "eats", "a", "cake", "with", "a", "fork"],
        )

    def test_tokenize_extra_spaces(self):
        self.assertEqual(cli.tokenize("  the   cat  ", self.english), ["the", "cat"])

    def test_tokenize_arithmetic_keeps_symbols(self):
        self.assertEqual(
            cli.tokenize("( id * id ) + id", self.arith),
            ["(", "id", "*", "id", ")", "+", "id"],
        )

    def test_tokenize_keeps_case_if_grammar_has_uppercase_terminals(self):
        g = parse_grammar("S -> Hello World")
        self.assertEqual(cli.tokenize("Hello World", g), ["Hello", "World"])

    def test_format_tree(self):
        tree = ("S", [("NP", [("she", [])]), ("VP", [("eats", [])])])
        self.assertEqual(
            cli.format_tree(tree),
            "S\n├── NP\n│   └── she\n└── VP\n    └── eats",
        )

    def test_leaves(self):
        tree = ("S", [("NP", [("she", [])]), ("VP", [("eats", [])])])
        self.assertEqual(cli.leaves(tree), ["she", "eats"])


def run_cli(*args):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = cli.main(list(args))
    return code, out.getvalue(), err.getvalue()


@INTEGRATION
class EndToEndTests(unittest.TestCase):
    def check(self, phrase, expected, grammar=None):
        args = ["-g", path(grammar)] if grammar else []
        code, out, err = run_cli(*args, phrase)
        self.assertEqual(code, 0, err)
        self.assertIn("Resultado: " + ("SÍ" if expected else "NO"), out)
        self.assertIn("Tiempo de CYK:", out)
        return out

    def test_english_accepted(self):
        for phrase in (
            "She eats a cake with a fork",
            "The cat drinks the beer",
            "he cooks",
            "she cuts the meat in the oven with a knife",
        ):
            with self.subTest(phrase=phrase):
                out = self.check(phrase, True)
                self.assertIn("Parse tree:", out)

    def test_english_rejected(self):
        for phrase in (
            "cake the eats she",
            "the cat",
            "she eats with",
            "she eats a pizza",
            "the the cat drinks",
            "she",
        ):
            with self.subTest(phrase=phrase):
                out = self.check(phrase, False)
                self.assertNotIn("Parse tree:", out)

    def test_unknown_word_is_reported(self):
        out = self.check("she eats a pizza", False)
        self.assertIn("pizza", out)

    def test_tree_leaves_match_phrase(self):
        _, out, _ = run_cli("she eats a cake with a fork")
        block = out.split("Parse tree:\n", 1)[1]
        words = [line.split("── ")[-1] for line in block.splitlines()]
        for word in "she eats a cake with a fork".split():
            self.assertIn(word, words)

    def test_arithmetic_from_non_cnf_file(self):
        self.check("( id * id ) + id", True, "1.txt")
        self.check("id + * id", False, "1.txt")
        self.check("( id + id", False, "1.txt")

    def test_arithmetic_from_cnf_file(self):
        self.check("( id * id ) + id", True, "1-cnf.txt")
        self.check("id id", False, "1-cnf.txt")

    def test_steps_flag_prints_cnf(self):
        _, out, _ = run_cli("--steps", "he cooks")
        self.assertIn("Forma Normal de Chomsky", out)

    def test_missing_grammar_file(self):
        code, _, err = run_cli("-g", os.path.join("no", "existe.txt"), "he cooks")
        self.assertEqual(code, 2)
        self.assertIn("Error", err)

    def test_empty_phrase(self):
        code, _, err = run_cli("   ")
        self.assertEqual(code, 2)
        self.assertIn("vacía", err)


if __name__ == "__main__":
    unittest.main()

"""Mutation tests for coroutine translation (Task 7).

Monkeypatches key functions to verify that the test suite catches breakage
when coroutine detection or yield translation is disabled.

Written by independent validation agent — no existing test files were consulted.
"""

import pytest
from pathlib import Path

from src.translator.python_parser import PyFile, PyClass, PyMethod, parse_python
from src.translator.python_to_csharp import translate, translate_file
import src.translator.python_parser as parser_mod
import src.translator.python_to_csharp as translator_mod


ANGRY_BIRDS_DIR = Path(__file__).resolve().parents[2] / "examples" / "angry_birds" / "angry_birds_python"


class TestMutateHasYield:
    """Mutation: if _has_yield always returns False, coroutines lose IEnumerator."""

    def test_broken_has_yield_loses_ienumerator(self, monkeypatch):
        """When _has_yield is patched to always return False, the parser should
        mark no methods as coroutines, so translate output must lack IEnumerator."""
        monkeypatch.setattr(parser_mod, "_has_yield", lambda func: False)

        source = (
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def my_routine(self):\n"
            "        yield WaitForSeconds(1)\n"
        )
        parsed = parse_python(source)
        # Parser should now mark method as NOT a coroutine
        assert parsed.classes[0].methods[0].is_coroutine is False

        # Translating should produce void, not IEnumerator
        output = translate(parsed)
        assert "IEnumerator" not in output

    def test_broken_has_yield_loses_using_directive(self, monkeypatch):
        """When _has_yield is broken, using System.Collections should disappear."""
        monkeypatch.setattr(parser_mod, "_has_yield", lambda func: False)

        source = (
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def my_routine(self):\n"
            "        yield WaitForSeconds(1)\n"
        )
        parsed = parse_python(source)
        output = translate(parsed)
        assert "using System.Collections;" not in output


class TestMutateYieldTranslation:
    """Mutation: if yield translation is broken, yield lines appear wrong."""

    def test_broken_yield_handling_in_statement_translator(self, monkeypatch):
        """Monkeypatch _translate_py_statement to skip yield handling.
        Yield lines should then NOT produce 'yield return' in output."""
        original = translator_mod._translate_py_statement

        def broken_translate(line):
            # Skip the yield-specific handling — just fall through to expression
            if line.startswith("yield ") or line == "yield":
                # Pretend it's a regular expression — wrong behavior
                expr = translator_mod._translate_py_expression(line)
                return f"{expr};"
            return original(line)

        monkeypatch.setattr(translator_mod, "_translate_py_statement", broken_translate)

        pf = PyFile(
            imports=[],
            classes=[PyClass(
                name="TestClass",
                base_classes=["MonoBehaviour"],
                is_monobehaviour=True,
                fields=[],
                methods=[PyMethod(
                    name="my_coroutine",
                    body_source="yield WaitForSeconds(2)",
                    is_coroutine=True,
                )],
            )],
        )
        output = translate(pf)
        # The broken translator should NOT produce the correct "yield return new"
        assert "yield return new WaitForSeconds(2);" not in output


class TestMutateRealFile:
    """Mutation: monkeypatch on real file translation catches breakage."""

    def test_bird_file_loses_ienumerator_when_has_yield_broken(self, monkeypatch):
        """Translate bird.py with broken _has_yield — IEnumerator must vanish."""
        monkeypatch.setattr(parser_mod, "_has_yield", lambda func: False)
        output = translate_file(ANGRY_BIRDS_DIR / "bird.py")
        assert "IEnumerator" not in output

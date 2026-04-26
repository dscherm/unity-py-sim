"""Contract tests for coroutine translation (Task 7).

Validates that the Python parser and Python-to-C# translator correctly handle
coroutine patterns: yield detection, IEnumerator return types, yield return
statements, StartCoroutine calls, and System.Collections using directives.

Written by independent validation agent — no existing test files were consulted.
"""

import ast
import pytest

from src.translator.python_parser import (
    PyMethod, PyField, PyClass, PyFile,
    _has_yield, parse_python,
)
from src.translator.python_to_csharp import translate


# ── _has_yield contract tests ────────────────────────────────


class TestHasYield:
    """Contract: _has_yield detects yield / yield from in function AST nodes."""

    def test_returns_true_for_yield_statement(self):
        """A function with a bare yield must be detected as containing yield."""
        source = "def f():\n    yield"
        tree = ast.parse(source)
        func = tree.body[0]
        assert _has_yield(func) is True

    def test_returns_true_for_yield_expression(self):
        """A function with yield <value> must be detected."""
        source = "def f():\n    yield WaitForSeconds(1)"
        tree = ast.parse(source)
        func = tree.body[0]
        assert _has_yield(func) is True

    def test_returns_true_for_yield_none(self):
        """A function with yield None must be detected."""
        source = "def f():\n    yield None"
        tree = ast.parse(source)
        func = tree.body[0]
        assert _has_yield(func) is True

    def test_returns_false_for_no_yield(self):
        """A function without yield must not be detected as containing yield."""
        source = "def f():\n    return 42"
        tree = ast.parse(source)
        func = tree.body[0]
        assert _has_yield(func) is False

    def test_returns_false_for_empty_function(self):
        """A function with only pass must not be detected."""
        source = "def f():\n    pass"
        tree = ast.parse(source)
        func = tree.body[0]
        assert _has_yield(func) is False


# ── PyMethod.is_coroutine default ────────────────────────────


class TestPyMethodDefault:
    """Contract: PyMethod.is_coroutine defaults to False."""

    def test_default_is_false(self):
        m = PyMethod(name="foo")
        assert m.is_coroutine is False


# ── Parser detects coroutine ─────────────────────────────────


class TestParserCoroutineDetection:
    """Contract: parse_python marks methods with yield as is_coroutine=True."""

    def test_parser_detects_yield_wait_for_seconds(self):
        source = (
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def my_routine(self):\n"
            "        yield WaitForSeconds(1)\n"
        )
        parsed = parse_python(source)
        method = parsed.classes[0].methods[0]
        assert method.is_coroutine is True

    def test_parser_detects_yield_none(self):
        source = (
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def my_routine(self):\n"
            "        yield None\n"
        )
        parsed = parse_python(source)
        method = parsed.classes[0].methods[0]
        assert method.is_coroutine is True

    def test_parser_does_not_detect_coroutine_in_normal_method(self):
        source = (
            "from src.engine.core import MonoBehaviour\n"
            "class Foo(MonoBehaviour):\n"
            "    def update(self):\n"
            "        self.x = 1\n"
        )
        parsed = parse_python(source)
        method = parsed.classes[0].methods[0]
        assert method.is_coroutine is False


# ── Translator return type contracts ─────────────────────────


class TestTranslatorReturnType:
    """Contract: coroutine methods emit IEnumerator, others emit void."""

    def _make_file(self, method_body: str, is_coroutine: bool) -> PyFile:
        return PyFile(
            imports=[],
            classes=[PyClass(
                name="TestClass",
                base_classes=["MonoBehaviour"],
                is_monobehaviour=True,
                fields=[],
                methods=[PyMethod(
                    name="my_method",
                    body_source=method_body,
                    is_coroutine=is_coroutine,
                )],
            )],
        )

    def test_coroutine_emits_ienumerator(self):
        pf = self._make_file("yield None", is_coroutine=True)
        output = translate(pf)
        assert "IEnumerator" in output

    def test_non_coroutine_emits_void(self):
        pf = self._make_file("self.x = 1", is_coroutine=False)
        output = translate(pf)
        # Should have void but not IEnumerator
        assert "void" in output
        assert "IEnumerator" not in output


# ── Yield translation contracts ──────────────────────────────


class TestYieldTranslation:
    """Contract: yield statements translate to correct C# yield return forms."""

    def _translate_coroutine(self, body_source: str) -> str:
        pf = PyFile(
            imports=[],
            classes=[PyClass(
                name="TestClass",
                base_classes=["MonoBehaviour"],
                is_monobehaviour=True,
                fields=[],
                methods=[PyMethod(
                    name="my_coroutine",
                    body_source=body_source,
                    is_coroutine=True,
                )],
            )],
        )
        return translate(pf)

    def test_yield_wait_for_seconds(self):
        """yield WaitForSeconds(x) -> yield return new WaitForSeconds(x);"""
        output = self._translate_coroutine("yield WaitForSeconds(2)")
        assert "yield return new WaitForSeconds(2);" in output

    def test_yield_none(self):
        """yield None -> yield return null;"""
        output = self._translate_coroutine("yield None")
        assert "yield return null;" in output


# ── StartCoroutine translation ───────────────────────────────


class TestStartCoroutineTranslation:
    """Contract: self.start_coroutine(method()) -> StartCoroutine(method());"""

    def test_start_coroutine_call(self):
        pf = PyFile(
            imports=[],
            classes=[PyClass(
                name="TestClass",
                base_classes=["MonoBehaviour"],
                is_monobehaviour=True,
                fields=[],
                methods=[PyMethod(
                    name="update",
                    body_source="self.start_coroutine(self._my_routine())",
                    is_lifecycle=True,
                    is_coroutine=False,
                )],
            )],
        )
        output = translate(pf)
        assert "StartCoroutine(" in output
        # self. prefix on _my_routine should also be stripped
        assert "self.start_coroutine" not in output


# ── using System.Collections directive ───────────────────────


class TestUsingDirective:
    """Contract: using System.Collections; present iff class has coroutine."""

    def _make_class(self, is_coroutine: bool) -> str:
        pf = PyFile(
            imports=[],
            classes=[PyClass(
                name="TestClass",
                base_classes=["MonoBehaviour"],
                is_monobehaviour=True,
                fields=[],
                methods=[PyMethod(
                    name="my_method",
                    body_source="yield None" if is_coroutine else "self.x = 1",
                    is_coroutine=is_coroutine,
                )],
            )],
        )
        return translate(pf)

    def test_using_present_with_coroutine(self):
        output = self._make_class(is_coroutine=True)
        assert "using System.Collections;" in output

    def test_using_absent_without_coroutine(self):
        output = self._make_class(is_coroutine=False)
        assert "using System.Collections;" not in output

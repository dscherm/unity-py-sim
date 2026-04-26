"""Mutation tests for the post-pass rewrites in _translate_method.

These tests patch the translator's post-passes to a no-op and assert that
the contract tests for .Length and transform.children would fail. This
proves the contract tests actually exercise the post-passes (not some
other layer of the translator).

Mechanism: the post-passes are two inlined re.sub / re.finditer calls at
the end of _translate_method. We patch re.sub and re.finditer in the
python_to_csharp module to intercept only those call sites.
"""

from __future__ import annotations

import re
import tempfile
from pathlib import Path

import pytest

from src.translator import python_to_csharp
from src.translator.python_parser import parse_python_file


# ─── Fixtures ──────────────────────────────────────────────────────


_FIND_OBJECTS_SNIPPET = '''
from __future__ import annotations
from src.engine.core import MonoBehaviour, GameObject


class Mgr(MonoBehaviour):
    def play(self) -> None:
        pipes = GameObject.find_objects_of_type(Pipes)
        for i in range(len(pipes)):
            print(i)
'''

_CHILDREN_SNIPPET = '''
from __future__ import annotations
from src.engine.core import MonoBehaviour, GameObject


class Sp(MonoBehaviour):
    def spawn(self) -> None:
        pipes_go: GameObject | None = None
        if pipes_go is not None:
            for c in pipes_go.transform.children:
                print(c.game_object.name)
'''


def _translate(src: str) -> str:
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as f:
        f.write(src)
        path = f.name
    try:
        parsed = parse_python_file(path)
        return python_to_csharp.translate(parsed)
    finally:
        Path(path).unlink(missing_ok=True)


# ─── Sanity: unmutated baseline passes ─────────────────────────────


class TestBaseline:
    def test_pipes_length_present_without_mutation(self):
        cs = _translate(_FIND_OBJECTS_SNIPPET)
        assert "pipes.Length" in cs
        assert "pipes.Count" not in cs

    def test_transform_children_stripped_without_mutation(self):
        cs = _translate(_CHILDREN_SNIPPET)
        assert "transform.children" not in cs
        assert "foreach (Transform c in pipesGo.transform)" in cs


# ─── Mutation: disable .Count -> .Length rewrite ───────────────────


class TestMutateDotCountRewrite:
    """If we disable the rewrite that maps FindObjectsOfType locals'
    .Count to .Length, the contract assertion must FAIL. That proves
    the contract is testing the post-pass and not some upstream layer.
    """

    def test_disabling_count_rewrite_breaks_contract(self, monkeypatch):
        """Skip the exact re.sub that converts name.Count -> name.Length."""
        orig_sub = python_to_csharp.re.sub

        def fake_sub(pattern, repl, string, *args, **kwargs):
            # Pattern carries `\.Count\b` and repl carries `.Length`
            # when coming from the post-pass for FindObjectsOfType locals.
            pat_src = pattern if isinstance(pattern, str) else getattr(
                pattern, "pattern", ""
            )
            if ".Count" in pat_src and isinstance(repl, str) and ".Length" in repl:
                return string  # no-op: simulate the bug
            return orig_sub(pattern, repl, string, *args, **kwargs)

        monkeypatch.setattr(python_to_csharp.re, "sub", fake_sub)

        cs = _translate(_FIND_OBJECTS_SNIPPET)

        # With the rewrite disabled, we expect pipes.Count to survive, which
        # is the bug the post-pass is there to fix.
        assert "pipes.Count" in cs, (
            "Mutation should have left pipes.Count unrewritten.\n" + cs
        )
        # And .Length should NOT appear (no other path produces it here).
        assert "pipes.Length" not in cs, (
            "Unexpected .Length when rewrite is disabled.\n" + cs
        )


# ─── Mutation: disable transform.children rewrites ─────────────────


class TestMutateTransformChildrenRewrite:
    """If we disable the two post-passes that handle transform.children,
    the contract assertion must FAIL.
    """

    def test_disabling_children_rewrites_breaks_contract(self, monkeypatch):
        """Skip both re.sub calls that touch transform.children."""
        orig_sub = python_to_csharp.re.sub

        def fake_sub(pattern, repl, string, *args, **kwargs):
            pat_src = pattern if isinstance(pattern, str) else getattr(
                pattern, "pattern", ""
            )
            # Guard #1: the foreach-children rewrite
            if "transform" in pat_src and ".children" in pat_src and \
                    "foreach" in pat_src:
                return string
            # Guard #2: the bare transform.children strip
            if pat_src == r"\btransform\.children\b":
                return string
            return orig_sub(pattern, repl, string, *args, **kwargs)

        monkeypatch.setattr(python_to_csharp.re, "sub", fake_sub)

        cs = _translate(_CHILDREN_SNIPPET)

        # Without the rewrite we should see either `foreach (var ...)` over
        # transform.children OR the literal `transform.children` surviving.
        # Either way, the contract assertion would fail, so we verify at
        # least one of those remnants is present.
        has_var_foreach = re.search(
            r"foreach\s*\(\s*var\s+\w+\s+in\s+[\w.]*transform\.children\s*\)", cs
        ) is not None
        has_bare_children = "transform.children" in cs
        assert has_var_foreach or has_bare_children, (
            "Mutation failed to produce the pre-fix output.\n" + cs
        )
        # And the post-fix form must NOT appear.
        assert "foreach (Transform c in pipesGo.transform)" not in cs

"""Contract tests for the M-11 idiom catalog under data/idioms/.

These tests assert catalog-shape invariants that complement the existing
parametrized regression suite in tests/idioms/. They derive their expectations
from the catalog spec encoded in tools/build_idiom_catalog.py (docstring +
file-emission rules) — NOT from the existing test runner — so they catch
fixture-shape bugs the runner can't see.

Scope (intentionally minimal):
  1. Every safe.py is valid Python.
  2. Every safe.cs.expected is non-empty and ends with a newline.
  3. Every README.md mentions both `safe.py` and `safe.cs.expected`.
  4. Every unsafe.py has a paired unsafe.notes.md and vice versa.
  5. Every unsafe.notes.md contains an actionable rewrite instruction.
  6. At least 4 distinct feature areas exist under data/idioms/.
"""
from __future__ import annotations

from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
IDIOMS_ROOT = REPO_ROOT / "data" / "idioms"


def _idiom_dirs() -> list[Path]:
    """Return every leaf idiom directory (one that contains safe.py)."""
    if not IDIOMS_ROOT.exists():
        return []
    return sorted(p.parent for p in IDIOMS_ROOT.glob("*/*/safe.py"))


def _idiom_id(path: Path) -> str:
    return f"{path.parent.name}/{path.name}"


IDIOM_DIRS = _idiom_dirs()
IDIOM_IDS = [_idiom_id(p) for p in IDIOM_DIRS]


@pytest.mark.parametrize("idiom_dir", IDIOM_DIRS, ids=IDIOM_IDS)
def test_safe_py_is_valid_python(idiom_dir: Path) -> None:
    """Every safe.py must parse + compile as Python — no fixture corruption."""
    safe_py = idiom_dir / "safe.py"
    assert safe_py.is_file(), f"missing safe.py in {idiom_dir}"
    src = safe_py.read_text(encoding="utf-8")
    # compile() raises SyntaxError on bad input; that's the failure mode we want.
    compile(src, str(safe_py), "exec")


@pytest.mark.parametrize("idiom_dir", IDIOM_DIRS, ids=IDIOM_IDS)
def test_safe_cs_expected_nonempty_and_newline_terminated(idiom_dir: Path) -> None:
    """Frozen C# fixture must be present, non-empty, and end with '\\n'."""
    expected = idiom_dir / "safe.cs.expected"
    assert expected.is_file(), f"missing safe.cs.expected in {idiom_dir}"
    content = expected.read_text(encoding="utf-8")
    assert content.strip(), f"safe.cs.expected is empty or whitespace-only in {idiom_dir}"
    assert content.endswith("\n"), (
        f"safe.cs.expected in {idiom_dir} must end with a newline "
        f"(got trailing repr: {content[-5:]!r})"
    )


@pytest.mark.parametrize("idiom_dir", IDIOM_DIRS, ids=IDIOM_IDS)
def test_readme_mentions_safe_files(idiom_dir: Path) -> None:
    """README.md must reference both safe.py and safe.cs.expected for accuracy."""
    readme = idiom_dir / "README.md"
    assert readme.is_file(), f"missing README.md in {idiom_dir}"
    text = readme.read_text(encoding="utf-8")
    assert "safe.py" in text, f"README.md in {idiom_dir} does not mention 'safe.py'"
    assert "safe.cs.expected" in text, (
        f"README.md in {idiom_dir} does not mention 'safe.cs.expected'"
    )


@pytest.mark.parametrize("idiom_dir", IDIOM_DIRS, ids=IDIOM_IDS)
def test_unsafe_files_are_paired(idiom_dir: Path) -> None:
    """unsafe.py <-> unsafe.notes.md must always travel together."""
    has_py = (idiom_dir / "unsafe.py").is_file()
    has_notes = (idiom_dir / "unsafe.notes.md").is_file()
    assert has_py == has_notes, (
        f"{idiom_dir}: unsafe.py present={has_py} but unsafe.notes.md present={has_notes} "
        "— the paired-files invariant is violated."
    )


@pytest.mark.parametrize("idiom_dir", IDIOM_DIRS, ids=IDIOM_IDS)
def test_unsafe_notes_have_actionable_rewrite(idiom_dir: Path) -> None:
    """unsafe.notes.md must give the reader an actionable next step.

    We require at least one of the keywords {"rewrite", "instead", "use "}
    (case-insensitive, "use " with trailing space to avoid matching e.g.
    "abuse"). If a notes file is purely descriptive ("X is broken.") with no
    pointer to the safe form, the contrast is unactionable.
    """
    notes = idiom_dir / "unsafe.notes.md"
    if not notes.is_file():
        pytest.skip(f"{idiom_dir} has no unsafe.notes.md (safe-only idiom)")
    text = notes.read_text(encoding="utf-8").lower()
    keywords = ("rewrite", "instead", "use ")
    assert any(kw in text for kw in keywords), (
        f"unsafe.notes.md in {idiom_dir} contains none of {keywords!r} — "
        "the contrast is descriptive but not actionable."
    )


def test_at_least_four_distinct_feature_areas() -> None:
    """Catalog must span >=4 feature areas to remain a useful matrix."""
    assert IDIOMS_ROOT.is_dir(), f"data/idioms/ is missing at {IDIOMS_ROOT}"
    areas = {
        child.name
        for child in IDIOMS_ROOT.iterdir()
        if child.is_dir() and any(child.glob("*/safe.py"))
    }
    assert len(areas) >= 4, (
        f"Expected at least 4 distinct feature areas under data/idioms/, "
        f"got {len(areas)}: {sorted(areas)}"
    )

"""Idiom catalog regression suite (M-11).

For every `data/idioms/<area>/<name>/safe.py` we run the snippet tool with
`--diff safe.cs.expected` and assert exit=0. If the translator's behavior on a
catalogued idiom drifts, this test fails with the unified diff and forces an
explicit decision: either fix the translator or re-run
`python tools/build_idiom_catalog.py` to refresh the fixture intentionally.

The catalog is also a contract on its own structure — these tests verify every
idiom directory has the expected files and that no orphan directories exist.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
IDIOMS_ROOT = REPO_ROOT / "data" / "idioms"
SNIPPET_TOOL = REPO_ROOT / "tools" / "translate_snippet.py"


def _all_idiom_dirs() -> list[Path]:
    if not IDIOMS_ROOT.exists():
        return []
    out = []
    for area_dir in sorted(IDIOMS_ROOT.iterdir()):
        if not area_dir.is_dir() or area_dir.name.startswith("."):
            continue
        for idiom_dir in sorted(area_dir.iterdir()):
            if idiom_dir.is_dir():
                out.append(idiom_dir)
    return out


def _read_idiom_args(idiom_dir: Path) -> list[str]:
    """Extra CLI args for an idiom — encoded in `extra_args.txt` if present."""
    extra = idiom_dir / "extra_args.txt"
    if not extra.exists():
        return []
    return extra.read_text(encoding="utf-8").split()


@pytest.fixture(scope="session")
def idiom_dirs() -> list[Path]:
    dirs = _all_idiom_dirs()
    assert dirs, "expected at least one idiom under data/idioms/"
    return dirs


def test_catalog_has_idioms(idiom_dirs: list[Path]) -> None:
    """At least 15 idioms must exist (target is 20+; 15 floor catches accidental loss)."""
    assert len(idiom_dirs) >= 15, (
        f"idiom catalog shrunk to {len(idiom_dirs)} entries — expected ≥15"
    )


@pytest.mark.parametrize(
    "idiom_dir",
    _all_idiom_dirs(),
    ids=lambda p: f"{p.parent.name}/{p.name}",
)
def test_idiom_has_required_files(idiom_dir: Path) -> None:
    """Every idiom dir has safe.py + safe.cs.expected + README.md."""
    for required in ("safe.py", "safe.cs.expected", "README.md"):
        f = idiom_dir / required
        assert f.exists(), f"missing {required} in {idiom_dir}"
        assert f.stat().st_size > 0, f"{required} is empty in {idiom_dir}"


@pytest.mark.parametrize(
    "idiom_dir",
    _all_idiom_dirs(),
    ids=lambda p: f"{p.parent.name}/{p.name}",
)
def test_unsafe_idiom_has_paired_notes(idiom_dir: Path) -> None:
    """If unsafe.py exists, unsafe.notes.md must exist too — and vice versa."""
    has_unsafe_py = (idiom_dir / "unsafe.py").exists()
    has_unsafe_notes = (idiom_dir / "unsafe.notes.md").exists()
    if has_unsafe_py or has_unsafe_notes:
        assert has_unsafe_py and has_unsafe_notes, (
            f"unsafe.py and unsafe.notes.md must come together in {idiom_dir}"
        )


@pytest.mark.parametrize(
    "idiom_dir",
    _all_idiom_dirs(),
    ids=lambda p: f"{p.parent.name}/{p.name}",
)
def test_safe_py_translates_to_expected_csharp(idiom_dir: Path) -> None:
    """End-to-end: snippet tool --diff against the frozen fixture exits 0."""
    safe_py = idiom_dir / "safe.py"
    expected = idiom_dir / "safe.cs.expected"
    args = [
        sys.executable,
        str(SNIPPET_TOOL),
        "--file",
        str(safe_py),
        "--diff",
        str(expected),
        *_read_idiom_args(idiom_dir),
    ]
    proc = subprocess.run(args, capture_output=True, text=True, timeout=30)
    if proc.returncode != 0:
        pytest.fail(
            f"idiom {idiom_dir.parent.name}/{idiom_dir.name} drifted from fixture:\n"
            f"  exit code: {proc.returncode}\n"
            f"  diff:\n{proc.stdout}\n"
            f"  Re-run `python tools/build_idiom_catalog.py` if the drift is intentional."
        )


def test_no_orphan_idiom_directories() -> None:
    """No top-level files under data/idioms/ except README.md."""
    if not IDIOMS_ROOT.exists():
        pytest.skip("idiom catalog not yet generated")
    for entry in IDIOMS_ROOT.iterdir():
        if entry.is_file():
            assert entry.name == "README.md", (
                f"unexpected file at idiom-catalog root: {entry.name}"
            )

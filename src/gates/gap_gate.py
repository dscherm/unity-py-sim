"""Gap Gate — required CI check for Python ↔ Unity behavioral parity (M-12).

The gate runs on every PR and asserts:

    For every Unity API REFERENCED by a Python file TOUCHED in the PR diff,
    there must be a passing dual-path parity test under tests/parity/.

Two design rules (encoded per plan.md M-12):

  1. **Grandfather only untouched code.** Files NOT in the PR diff are exempt;
     files IN the diff must have all their Unity API references parity-tested,
     even if a particular reference predates the change. Stricter than
     'grandfather entire files until first touch'.

  2. **Auto-generate skeletons on missing coverage.** When the gate finds an
     uncovered API in a touched file, it invokes `tools/parity_scaffold.py`
     to write a skeleton + fails with a clear message ('skeleton written to X
     — fill in scenario_python and scenario_csharp_body, then re-run').

Usage:
    python -m src.gates.gap_gate --base master       # PR-style: diff vs master
    python -m src.gates.gap_gate --base HEAD~1       # ad-hoc: last commit only
    python -m src.gates.gap_gate --files a.py b.py   # explicit file list
    python -m src.gates.gap_gate --no-scaffold       # report only, no skeleton write

Exit codes:
    0 — every Unity API in touched files is parity-tested
    1 — uncovered APIs found; skeletons were written; agent should fill them in
    2 — argparse / I/O error
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PARITY_TESTS_DIR = REPO_ROOT / "tests" / "parity"
MATRIX_JSON = REPO_ROOT / "data" / "metrics" / "parity_matrix.json"
SCAFFOLD_TOOL = REPO_ROOT / "tools" / "parity_scaffold.py"


@dataclass(frozen=True)
class APIReference:
    """One Unity API mention found in a touched Python file."""
    file: Path
    unity_class: str
    unity_member: str  # "" for bare class references


@dataclass(frozen=True)
class GateResult:
    references: list[APIReference]
    untested: list[APIReference]
    skeletons_written: list[Path]


# ── Touched file detection ──────────────────────────────────────────────────


def _changed_files(base: str | None, files: list[str] | None) -> list[Path]:
    if files:
        return [REPO_ROOT / f for f in files]
    if not base:
        return []
    proc = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=AMR", base, "HEAD"],
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode != 0:
        raise SystemExit(f"git diff failed: {proc.stderr.strip()}")
    return [REPO_ROOT / line.strip() for line in proc.stdout.splitlines() if line.strip()]


def _is_in_scope(p: Path) -> bool:
    """Files the gate cares about — Python sources under src/ or examples/."""
    if p.suffix != ".py":
        return False
    try:
        rel = p.resolve().relative_to(REPO_ROOT)
        parts: tuple[str, ...] = rel.parts
        if parts and parts[0] not in ("src", "examples"):
            return False
    except ValueError:
        # File not under REPO_ROOT (e.g. test fixture). Accept if any path
        # part is "src" or "examples".
        parts = p.parts
        if not any(part in ("src", "examples") for part in parts):
            return False
    if not parts:
        return False
    if "tests" in parts:
        return False  # tests aren't subject to the gate
    return True


# ── API reference extraction ───────────────────────────────────────────────


def _load_matrix() -> dict:
    return json.loads(MATRIX_JSON.read_text(encoding="utf-8"))


def _build_api_index(matrix: dict) -> dict[str, set[str]]:
    """class -> {members} from the parity matrix. Empty-string member means
    the class itself counts as a row."""
    index: dict[str, set[str]] = {}
    for row in matrix["rows"]:
        cls = row["unity_class"]
        member = row["unity_member"] or ""
        index.setdefault(cls, set()).add(member)
    return index


def _scan_file_for_apis(path: Path, index: dict[str, set[str]]) -> set[tuple[str, str]]:
    """Return the (class, member) pairs from `index` that appear in this file.

    Uses a permissive regex match — any text occurrence of `<Class>` counts as
    a class reference; `<Class>.<member>` or `<class_lower>.<member_camel>`
    counts as a member reference. The Python sim uses snake_case names that
    the regex normalizes to the matrix's camelCase before checking.

    Subtleties:
      - Python attribute names are snake_case; we match both `Class.snake_case`
        and `Class.camelCase` against the index's camelCase entries.
      - We also match attribute access on the *class* via the engine module
        path (e.g. `transform.position` after `from src.engine.transform
        import Transform`).
    """
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return set()

    found: set[tuple[str, str]] = set()
    for cls, members in index.items():
        # The class may be mentioned PascalCase (`Transform`), snake_case
        # (`transform.position`), or lower-first (`transform`). All three
        # shapes count as a class reference for member-attribute scanning.
        cls_snake = _camel_to_snake(cls)
        cls_lower_first = cls[:1].lower() + cls[1:] if cls else ""
        if (cls not in text
                and cls_snake not in text
                and cls_lower_first not in text):
            continue
        # Class itself referenced (PascalCase only — snake_case alone isn't
        # strong enough to claim a class-level reference)
        if "" in members and cls in text:
            found.add((cls, ""))
        # Member references — try several name shapes
        for member in members:
            if not member:
                continue
            shapes = {member, _camel_to_snake(member), member[:1].lower() + member[1:]}
            # Look for `Class.member` or `var.member` patterns
            patterns = [rf"\b{re.escape(cls)}\.({'|'.join(re.escape(s) for s in shapes)})\b"]
            for s in shapes:
                # Accept attribute access on any variable named after the
                # python_class snake-cased — e.g. `transform.position`.
                patterns.append(rf"\b\w+\.{re.escape(s)}\b")
            for pat in patterns:
                if re.search(pat, text):
                    found.add((cls, member))
                    break
    return found


_CAMEL_TO_SNAKE = re.compile(r"(?<!^)(?=[A-Z])")


def _camel_to_snake(s: str) -> str:
    return _CAMEL_TO_SNAKE.sub("_", s).lower()


# ── Coverage check ─────────────────────────────────────────────────────────


def _untested_set(refs: set[tuple[str, str]], matrix: dict) -> set[tuple[str, str]]:
    """Filter to only the (class, member) pairs that are NOT parity-tested."""
    tested = {
        (r["unity_class"], r["unity_member"] or "")
        for r in matrix["rows"]
        if r.get("has_parity_test")
    }
    return refs - tested


# ── Auto-skeleton ───────────────────────────────────────────────────────────


def _write_skeletons(untested: list[APIReference], dry_run: bool = False) -> list[Path]:
    """Invoke tools/parity_scaffold.py for each untested API. Returns the list
    of skeleton file paths that NOW exist. Returns existing-skeleton paths too
    so the gate's failure message points the agent at them."""
    apis = sorted({f"{r.unity_class}.{r.unity_member}" if r.unity_member else r.unity_class
                   for r in untested})
    if not apis or dry_run:
        return _expected_skeleton_paths(untested)

    cmd = [sys.executable, str(SCAFFOLD_TOOL), "--apis", *apis]
    proc = subprocess.run(cmd, cwd=str(REPO_ROOT), capture_output=True, text=True)
    if proc.returncode != 0:
        raise SystemExit(f"parity_scaffold failed: {proc.stderr.strip()}")
    return _expected_skeleton_paths(untested)


def _expected_skeleton_paths(refs: list[APIReference]) -> list[Path]:
    paths: list[Path] = []
    for r in refs:
        cls_slug = re.sub(r"[^a-z0-9_]+", "_", r.unity_class.lower()).strip("_")
        if r.unity_member:
            mem_slug = re.sub(r"[^a-z0-9_]+", "_", r.unity_member.lower()).strip("_")
            paths.append(PARITY_TESTS_DIR / f"test_{cls_slug}_{mem_slug}_parity.py")
        else:
            paths.append(PARITY_TESTS_DIR / f"test_{cls_slug}_class_parity.py")
    return paths


# ── Main entrypoint ─────────────────────────────────────────────────────────


def run_gate(*, base: str | None = "master", files: list[str] | None = None,
             scaffold: bool = True) -> GateResult:
    matrix = _load_matrix()
    index = _build_api_index(matrix)

    changed = [p for p in _changed_files(base, files) if _is_in_scope(p)]

    refs: list[APIReference] = []
    refs_set: set[tuple[str, str]] = set()
    for fp in changed:
        for cls, member in _scan_file_for_apis(fp, index):
            ref = APIReference(file=fp, unity_class=cls, unity_member=member)
            if (cls, member) not in refs_set:
                refs.append(ref)
                refs_set.add((cls, member))

    untested_pairs = _untested_set(refs_set, matrix)
    untested_refs = [r for r in refs if (r.unity_class, r.unity_member) in untested_pairs]

    skeletons = _write_skeletons(untested_refs, dry_run=not scaffold) if untested_refs else []
    return GateResult(references=refs, untested=untested_refs, skeletons_written=skeletons)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Gap Gate — Python ↔ Unity parity-coverage check.")
    parser.add_argument("--base", default="master",
                        help="Git ref to diff against (default: master). Ignored if --files given.")
    parser.add_argument("--files", nargs="*", default=None,
                        help="Explicit list of Python files to check; bypasses git diff.")
    parser.add_argument("--no-scaffold", action="store_true",
                        help="Report only; do not write skeletons for missing coverage.")
    args = parser.parse_args(argv)

    try:
        result = run_gate(base=args.base, files=args.files, scaffold=not args.no_scaffold)
    except SystemExit:
        raise
    except Exception as e:  # noqa: BLE001
        print(f"gap_gate: error: {type(e).__name__}: {e}", file=sys.stderr)
        return 2

    if not result.references:
        print("gap_gate: no Unity API references in touched files (or no diff). PASS.")
        return 0

    print(f"gap_gate: scanned {len(result.references)} API reference(s) in touched files.")
    if not result.untested:
        print("gap_gate: every referenced API has a parity test. PASS.")
        return 0

    print(f"gap_gate: FAIL — {len(result.untested)} API reference(s) lack parity tests:")
    for ref in result.untested:
        api = f"{ref.unity_class}.{ref.unity_member}" if ref.unity_member else ref.unity_class
        try:
            rel = ref.file.relative_to(REPO_ROOT)
        except ValueError:
            rel = ref.file
        print(f"  - {api}  (referenced by {rel})")

    if result.skeletons_written:
        print(
            "\ngap_gate: skeleton parity tests have been written for each missing API "
            "(or already exist). Fill in scenario_python + scenario_csharp_body in:"
        )
        for p in result.skeletons_written:
            try:
                rel = p.relative_to(REPO_ROOT)
            except ValueError:
                rel = p
            print(f"  - {rel}")
        print(
            "\nThen remove the `# PARITY_SCAFFOLD_SKELETON` marker and the `@pytest.mark.skip` "
            "from each, refresh data/metrics/parity_matrix.json via "
            "`python -m src.gates.parity_matrix`, and re-run the gate."
        )

    return 1


if __name__ == "__main__":
    sys.exit(main())

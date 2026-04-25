"""Build the engine ↔ Unity API parity matrix from src/reference/mappings/.

Walks every JSON file in the reference mappings directory, normalizes
each entry into a flat row, and reports which APIs are: claimed,
implemented (have a Python module + class), and test-covered (have a
matching test file or test name in tests/parity/).

The output is a JSON document at data/metrics/parity_matrix.json with a
list of rows and aggregate counts. tools/render_parity_matrix.py reads
this and emits markdown.

Usage:
    python -m src.gates.parity_matrix
    python -m src.gates.parity_matrix --output data/metrics/parity_2026.json
"""

from __future__ import annotations

import argparse
import importlib
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent.parent
MAPPINGS_DIR = ROOT / "src" / "reference" / "mappings"
PARITY_TESTS_DIR = ROOT / "tests" / "parity"
OUTPUT_PATH = ROOT / "data" / "metrics" / "parity_matrix.json"


@dataclass
class ParityRow:
    unity_class: str
    unity_member: str  # method/property/lifecycle name; "" for whole-class
    kind: str  # "class" | "method" | "property" | "lifecycle" | "enum" | "pattern"
    python_class: str | None
    python_module: str | None
    python_member: str | None  # explicit python_method/python_property from mapping
    has_python_impl: bool
    has_parity_test: bool


def _normalize(entry: dict[str, Any], kind: str) -> ParityRow | None:
    unity_class = entry.get("unity_class") or entry.get("class") or ""
    if not unity_class:
        return None
    if kind == "method":
        member = entry.get("unity_method", "")
        py_member = entry.get("python_method")
    elif kind == "property":
        member = entry.get("unity_property", "")
        py_member = entry.get("python_property")
    elif kind == "lifecycle":
        member = entry.get("unity_method", "")
        py_member = entry.get("python_method")
    elif kind == "enum":
        member = entry.get("unity_value", "")
        py_member = entry.get("python_value")
    else:
        member = ""
        py_member = None
    return ParityRow(
        unity_class=unity_class,
        unity_member=member,
        kind=kind,
        python_class=entry.get("python_class"),
        python_module=entry.get("python_module"),
        python_member=py_member,
        has_python_impl=False,
        has_parity_test=False,
    )


def _check_python_impl(row: ParityRow, class_module_index: dict[str, str]) -> bool:
    """Static check: does the named class expose this Unity-named member at the class level?

    Static-only by design — no class instantiation, no side effects on
    global registries. Resolves the Python module via row.python_module,
    then the class index keyed on python_class (handles Unity supertypes
    like Object → GameObject), then unity_class. The member name is taken
    from row.python_member when set, otherwise camel→snake derived.

    Limitation: instance-only attributes set in __init__ (e.g. GameObject.layer,
    AudioSource.clip) are NOT detected — they are not class-level. Behavioral
    coverage of those attributes lives in tests/parity/, not here.
    """
    py_class = row.python_class or row.unity_class
    py_module = (
        row.python_module
        or (row.python_class and class_module_index.get(row.python_class))
        or class_module_index.get(row.unity_class)
    )
    if not py_module or not py_class:
        return False
    try:
        mod = importlib.import_module(py_module)
    except Exception:
        return False
    cls = getattr(mod, py_class, None)
    if cls is None:
        return False
    if not row.unity_member:
        return True
    candidates: list[str] = []
    if row.python_member:
        candidates.append(row.python_member)
    snake = (
        row.unity_member[0].lower()
        + "".join("_" + c.lower() if c.isupper() else c for c in row.unity_member[1:])
    )
    candidates.append(snake)
    for c in candidates:
        if hasattr(cls, c):
            return True
    return False


def _check_parity_test(row: ParityRow, test_dir: Path) -> bool:
    """Look for a test_*<class>*<member>* under tests/parity/ that mentions this API."""
    if not test_dir.exists():
        return False
    needle_class = row.unity_class.lower()
    needle_member = row.unity_member.lower() if row.unity_member else ""
    for test_file in test_dir.rglob("test_*.py"):
        text = test_file.read_text(encoding="utf-8", errors="ignore").lower()
        if needle_class not in text:
            continue
        if not needle_member:
            return True
        if needle_member in text:
            return True
    return False


def build_matrix(
    mappings_dir: Path = MAPPINGS_DIR,
    parity_tests_dir: Path = PARITY_TESTS_DIR,
) -> dict[str, Any]:
    rows: list[ParityRow] = []

    file_kinds = {
        "classes.json": "class",
        "methods.json": "method",
        "properties.json": "property",
        "enums.json": "enum",
        "patterns.json": "pattern",
    }
    for fname, kind in file_kinds.items():
        path = mappings_dir / fname
        if not path.exists():
            continue
        data = json.loads(path.read_text())
        if isinstance(data, list):
            for entry in data:
                row = _normalize(entry, kind)
                if row is not None:
                    rows.append(row)

    # Lifecycle has a different shape: top-level keys are
    # `execution_order` (list of method names) and `mappings`
    # (dict of {unity_method_name: detail_dict}). Only mappings
    # contributes parity rows.
    lifecycle_path = mappings_dir / "lifecycle.json"
    if lifecycle_path.exists():
        data = json.loads(lifecycle_path.read_text())
        if isinstance(data, dict):
            mappings = data.get("mappings", {})
            if isinstance(mappings, dict):
                for unity_method, detail in mappings.items():
                    if not isinstance(detail, dict):
                        continue
                    enriched = dict(detail)
                    enriched.setdefault("unity_method", unity_method)
                    enriched.setdefault("unity_class", "MonoBehaviour")
                    row = _normalize(enriched, "lifecycle")
                    if row is not None:
                        rows.append(row)

    # Build class -> python_module index from class rows so method/property
    # entries (which omit python_module) can resolve.
    class_module_index = {
        r.unity_class: r.python_module
        for r in rows
        if r.kind == "class" and r.python_module
    }

    for row in rows:
        row.has_python_impl = _check_python_impl(row, class_module_index)
        row.has_parity_test = _check_parity_test(row, parity_tests_dir)

    total = len(rows)
    impl_count = sum(1 for r in rows if r.has_python_impl)
    test_count = sum(1 for r in rows if r.has_parity_test)

    return {
        "total_apis": total,
        "implemented": impl_count,
        "with_parity_test": test_count,
        "implementation_pct": round(impl_count / total, 3) if total else 0.0,
        "parity_test_pct": round(test_count / total, 3) if total else 0.0,
        "by_kind": _group_by_kind(rows),
        "by_unity_class": _group_by_unity_class(rows),
        "rows": [asdict(r) for r in rows],
    }


def _group_by_kind(rows: list[ParityRow]) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for r in rows:
        bucket = out.setdefault(
            r.kind, {"total": 0, "implemented": 0, "with_parity_test": 0}
        )
        bucket["total"] += 1
        if r.has_python_impl:
            bucket["implemented"] += 1
        if r.has_parity_test:
            bucket["with_parity_test"] += 1
    return out


def _group_by_unity_class(rows: list[ParityRow]) -> dict[str, dict[str, int]]:
    out: dict[str, dict[str, int]] = {}
    for r in rows:
        bucket = out.setdefault(
            r.unity_class, {"total": 0, "implemented": 0, "with_parity_test": 0}
        )
        bucket["total"] += 1
        if r.has_python_impl:
            bucket["implemented"] += 1
        if r.has_parity_test:
            bucket["with_parity_test"] += 1
    return out


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--output", default=str(OUTPUT_PATH))
    p.add_argument("--mappings-dir", default=str(MAPPINGS_DIR))
    p.add_argument("--tests-dir", default=str(PARITY_TESTS_DIR))
    args = p.parse_args(argv)

    matrix = build_matrix(
        mappings_dir=Path(args.mappings_dir),
        parity_tests_dir=Path(args.tests_dir),
    )
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(matrix, indent=2) + "\n")
    print(
        f"[parity] {matrix['total_apis']} APIs, "
        f"{matrix['implemented']} implemented "
        f"({matrix['implementation_pct'] * 100:.1f}%), "
        f"{matrix['with_parity_test']} with tests "
        f"({matrix['parity_test_pct'] * 100:.1f}%)"
    )
    print(f"[parity] wrote {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

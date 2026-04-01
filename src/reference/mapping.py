"""Query layer for Unity->Python reference mappings."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


_MAPPINGS_DIR = Path(__file__).parent / "mappings"


def _load_json(filename: str) -> Any:
    with open(_MAPPINGS_DIR / filename, "r") as f:
        return json.load(f)


class ReferenceMapping:
    """Loads and queries the Unity->Python reference mapping data."""

    def __init__(self, mappings_dir: Path | None = None) -> None:
        d = mappings_dir or _MAPPINGS_DIR
        self._classes: list[dict] = json.loads((d / "classes.json").read_text())
        self._methods: list[dict] = json.loads((d / "methods.json").read_text())
        self._properties: list[dict] = json.loads((d / "properties.json").read_text())
        self._lifecycle: dict = json.loads((d / "lifecycle.json").read_text())
        self._enums: list[dict] = json.loads((d / "enums.json").read_text())
        self._patterns: list[dict] = json.loads((d / "patterns.json").read_text())
        self._notes: list[dict] = json.loads((d / "notes.json").read_text())

    # ── Class queries ────────────────────────────────────────

    def get_python_class(self, unity_class: str) -> dict | None:
        """Look up the Python equivalent of a Unity class."""
        for entry in self._classes:
            if entry["unity_class"] == unity_class:
                return entry
        return None

    def get_all_classes(self) -> list[dict]:
        return list(self._classes)

    # ── Method queries ───────────────────────────────────────

    def get_python_method(self, unity_class: str, unity_method: str) -> dict | None:
        """Look up the Python equivalent of a Unity method."""
        for entry in self._methods:
            if entry["unity_class"] == unity_class and entry["unity_method"] == unity_method:
                return entry
        return None

    def get_methods_for_class(self, unity_class: str) -> list[dict]:
        return [e for e in self._methods if e["unity_class"] == unity_class]

    # ── Property queries ─────────────────────────────────────

    def get_python_property(self, unity_class: str, unity_property: str) -> dict | None:
        for entry in self._properties:
            if entry["unity_class"] == unity_class and entry["unity_property"] == unity_property:
                return entry
        return None

    def get_properties_for_class(self, unity_class: str) -> list[dict]:
        return [e for e in self._properties if e["unity_class"] == unity_class]

    # ── Lifecycle queries ────────────────────────────────────

    def get_lifecycle_mapping(self, unity_method: str) -> dict | None:
        return self._lifecycle["mappings"].get(unity_method)

    def get_lifecycle_order(self) -> list[str]:
        return list(self._lifecycle["execution_order"])

    # ── Enum queries ─────────────────────────────────────────

    def get_enum_mapping(self, unity_enum: str) -> dict | None:
        for entry in self._enums:
            if entry["unity_enum"] == unity_enum:
                return entry
        return None

    # ── Pattern queries ──────────────────────────────────────

    def get_pattern(self, pattern_id: str) -> dict | None:
        for entry in self._patterns:
            if entry["pattern_id"] == pattern_id:
                return entry
        return None

    def get_patterns_by_category(self, category: str) -> list[dict]:
        return [e for e in self._patterns if e["category"] == category]

    def get_all_patterns(self) -> list[dict]:
        return list(self._patterns)

    # ── Notes ────────────────────────────────────────────────

    def get_note(self, topic: str) -> dict | None:
        for entry in self._notes:
            if entry["topic"] == topic:
                return entry
        return None

    def get_all_notes(self) -> list[dict]:
        return list(self._notes)

    # ── Search ───────────────────────────────────────────────

    def search(self, query: str) -> list[dict]:
        """Fuzzy search across all mappings. Returns matching entries."""
        q = query.lower()
        results = []
        for cls in self._classes:
            if q in cls["unity_class"].lower() or q in cls["python_class"].lower():
                results.append({"type": "class", **cls})
        for method in self._methods:
            if q in method["unity_method"].lower() or q in method["python_method"].lower():
                results.append({"type": "method", **method})
        for prop in self._properties:
            if q in prop["unity_property"].lower() or q in prop["python_property"].lower():
                results.append({"type": "property", **prop})
        for pattern in self._patterns:
            if q in pattern["name"].lower() or q in pattern.get("unity_pattern", "").lower():
                results.append({"type": "pattern", **pattern})
        return results

    # ── Completeness ─────────────────────────────────────────

    def completeness_report(self) -> dict:
        """Report mapping coverage statistics."""
        total_classes = len(self._classes)
        full = sum(1 for c in self._classes if c.get("completeness") == "full")
        partial = sum(1 for c in self._classes if c.get("completeness") == "partial")
        return {
            "total_classes": total_classes,
            "full": full,
            "partial": partial,
            "coverage_pct": round(full / total_classes * 100, 1) if total_classes > 0 else 0,
            "total_methods": len(self._methods),
            "total_properties": len(self._properties),
            "total_patterns": len(self._patterns),
            "total_notes": len(self._notes),
        }

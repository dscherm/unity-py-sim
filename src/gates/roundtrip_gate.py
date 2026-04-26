"""Roundtrip gate — C# -> Python -> C# equivalence scoring."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from src.translator.csharp_parser import parse_csharp, CSharpFile, CSharpClass
from src.translator.csharp_to_python import translate as cs_to_py_translate
from src.translator.python_parser import parse_python
from src.translator.python_to_csharp import translate as py_to_cs_translate


@dataclass
class RoundtripResult:
    file_name: str
    structural_score: float   # class/method name and structure match
    type_score: float         # field types match
    naming_score: float       # naming conventions preserved
    overall_score: float      # weighted average
    original_class_count: int
    roundtrip_class_count: int
    details: list[str]        # human-readable notes


def score_roundtrip(csharp_source: str, file_name: str = "<source>") -> RoundtripResult:
    """Score the roundtrip fidelity: C# -> Python -> C# -> compare."""
    details = []

    # Step 1: Parse original C#
    original = parse_csharp(csharp_source)

    # Step 2: Translate to Python
    python_source = cs_to_py_translate(original)

    # Step 3: Parse the Python (may fail if translated Python isn't valid)
    try:
        py_parsed = parse_python(python_source)
    except SyntaxError as e:
        details.append(f"Python parse error: {e}")
        return RoundtripResult(
            file_name=file_name, structural_score=0.0, type_score=0.0,
            naming_score=0.0, overall_score=0.0,
            original_class_count=len(original.classes), roundtrip_class_count=0,
            details=details,
        )

    # Step 4: Translate back to C#
    roundtrip_cs = py_to_cs_translate(py_parsed)

    # Step 5: Parse the roundtrip C#
    roundtrip = parse_csharp(roundtrip_cs)

    # Step 6: Compare
    structural = _score_structural(original, roundtrip, details)
    types = _score_types(original, roundtrip, details)
    naming = _score_naming(original, roundtrip, details)

    overall = structural * 0.4 + types * 0.3 + naming * 0.3

    return RoundtripResult(
        file_name=file_name,
        structural_score=round(structural, 3),
        type_score=round(types, 3),
        naming_score=round(naming, 3),
        overall_score=round(overall, 3),
        original_class_count=len(original.classes),
        roundtrip_class_count=len(roundtrip.classes),
        details=details,
    )


def score_roundtrip_file(path: str | Path) -> RoundtripResult:
    """Score roundtrip fidelity for a C# file."""
    source = Path(path).read_text(encoding="utf-8")
    return score_roundtrip(source, Path(path).name)


def _score_structural(original: CSharpFile, roundtrip: CSharpFile, details: list[str]) -> float:
    """Score structural similarity — classes, methods present."""
    if not original.classes:
        return 1.0

    score_parts = []

    for orig_cls in original.classes:
        # Find matching class in roundtrip
        rt_cls = _find_class(roundtrip, orig_cls.name)
        if rt_cls is None:
            details.append(f"MISSING class: {orig_cls.name}")
            score_parts.append(0.0)
            continue

        # Class found
        cls_score = 1.0

        # Check base class
        if orig_cls.is_monobehaviour and not rt_cls.is_monobehaviour:
            details.append(f"{orig_cls.name}: lost MonoBehaviour inheritance")
            cls_score -= 0.2

        # Check methods
        orig_methods = {m.name for m in orig_cls.methods}
        rt_methods = {m.name for m in rt_cls.methods}
        missing = orig_methods - rt_methods
        extra = rt_methods - orig_methods
        if missing:
            details.append(f"{orig_cls.name}: missing methods: {missing}")
            cls_score -= 0.1 * len(missing)
        if extra:
            details.append(f"{orig_cls.name}: extra methods: {extra}")

        # Check fields
        orig_fields = {f.name for f in orig_cls.fields}
        rt_fields = {f.name for f in rt_cls.fields}
        missing_fields = orig_fields - rt_fields
        if missing_fields:
            details.append(f"{orig_cls.name}: missing fields: {missing_fields}")
            cls_score -= 0.05 * len(missing_fields)

        score_parts.append(max(0.0, cls_score))

    return sum(score_parts) / len(score_parts) if score_parts else 1.0


def _score_types(original: CSharpFile, roundtrip: CSharpFile, details: list[str]) -> float:
    """Score type mapping accuracy."""
    if not original.classes:
        return 1.0

    total = 0
    matches = 0

    for orig_cls in original.classes:
        rt_cls = _find_class(roundtrip, orig_cls.name)
        if rt_cls is None:
            continue

        for orig_field in orig_cls.fields:
            total += 1
            rt_field = _find_field(rt_cls, orig_field.name)
            if rt_field and rt_field.type == orig_field.type:
                matches += 1
            elif rt_field:
                details.append(f"Type mismatch: {orig_cls.name}.{orig_field.name}: "
                             f"{orig_field.type} -> {rt_field.type}")

        for orig_method in orig_cls.methods:
            total += 1
            rt_method = _find_method(rt_cls, orig_method.name)
            if rt_method and rt_method.return_type == orig_method.return_type:
                matches += 1
            elif rt_method:
                details.append(f"Return type mismatch: {orig_cls.name}.{orig_method.name}: "
                             f"{orig_method.return_type} -> {rt_method.return_type}")

    return matches / total if total > 0 else 1.0


def _score_naming(original: CSharpFile, roundtrip: CSharpFile, details: list[str]) -> float:
    """Score naming convention preservation."""
    if not original.classes:
        return 1.0

    total = 0
    matches = 0

    for orig_cls in original.classes:
        rt_cls = _find_class(roundtrip, orig_cls.name)
        if rt_cls is None:
            continue

        # Class name should be preserved
        total += 1
        if rt_cls.name == orig_cls.name:
            matches += 1
        else:
            details.append(f"Class name changed: {orig_cls.name} -> {rt_cls.name}")

        # Method names should survive roundtrip
        for orig_method in orig_cls.methods:
            total += 1
            if _find_method(rt_cls, orig_method.name):
                matches += 1
            else:
                details.append(f"Method name lost: {orig_cls.name}.{orig_method.name}")

    return matches / total if total > 0 else 1.0


def _find_class(parsed: CSharpFile, name: str) -> CSharpClass | None:
    for cls in parsed.classes:
        if cls.name == name:
            return cls
    return None


def _find_field(cls: CSharpClass, name: str):
    for f in cls.fields:
        if f.name == name:
            return f
    return None


def _find_method(cls: CSharpClass, name: str):
    for m in cls.methods:
        if m.name == name:
            return m
    return None

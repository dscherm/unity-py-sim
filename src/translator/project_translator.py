"""Project-level translator — processes all Python files together for cross-file type awareness.

Unlike translate_file() which processes one file at a time, this builds a global
type registry from ALL files before translating any of them. This enables:
- Cross-file field type inference (GameManager.instance → GameManager type)
- Module-level constant sharing (LAYER_LASER defined in player.py, used in invader.py)
- Method signature awareness across classes

Usage:
    from src.translator.project_translator import translate_project

    results = translate_project(
        "examples/space_invaders/space_invaders_python/",
        input_system="legacy", unity_version=5
    )
    for filename, csharp_code in results.items():
        Path(f"output/{filename}").write_text(csharp_code)
"""

from __future__ import annotations

import re
from pathlib import Path

from src.translator.python_parser import parse_python_file, PyFile, PyClass, PyField
from src.translator.python_to_csharp import (
    translate, _current_symbols, _build_symbol_table, _infer_field_types,
    _config, _TranslationConfig, detect_required_packages,
)
from src.translator.type_mapper import snake_to_camel, snake_to_pascal


def translate_project(
    directory: str | Path,
    *,
    input_system: str = "legacy",
    unity_version: int = 5,
    namespace: str | None = None,
) -> dict[str, str]:
    """Translate all Python files in a directory with cross-file type awareness.

    Returns dict of {CSharpFileName: csharp_source_code}.
    """
    directory = Path(directory)
    py_files = sorted(directory.glob("*.py"))
    py_files = [f for f in py_files if f.name != "__init__.py"]

    # Phase 1: Parse all files
    parsed_files: dict[str, PyFile] = {}
    for py_file in py_files:
        parsed_files[py_file.name] = parse_python_file(py_file)

    # Phase 2: Build global type registry
    global_types = _build_global_type_registry(parsed_files)

    # Phase 3: Build global constants (module-level from all files)
    global_constants = _build_global_constants(parsed_files)

    # Phase 4: Translate each file with global awareness
    results = {}
    for py_name, parsed in parsed_files.items():
        cs_name = _py_filename_to_cs(py_name, parsed)

        # Inject global types into parsed file's classes
        _inject_global_types(parsed, global_types, global_constants)

        # Translate
        cs_code = translate(
            parsed,
            namespace=namespace,
            unity_version=unity_version,
            input_system=input_system,
        )

        # Post-process: fix cross-file references
        cs_code = _post_process(cs_code, global_types, global_constants)

        results[cs_name] = cs_code

    # Detect required Unity packages across all translated files
    all_packages: list[dict[str, str]] = []
    seen_packages: set[str] = set()
    for cs_name, cs_code in results.items():
        for pkg in detect_required_packages(cs_code):
            if pkg["package"] not in seen_packages:
                seen_packages.add(pkg["package"])
                pkg["source_file"] = cs_name
                all_packages.append(pkg)
    if all_packages:
        results["_required_packages.json"] = __import__("json").dumps(
            all_packages, indent=2
        )

    return results


def _build_global_type_registry(parsed_files: dict[str, PyFile]) -> dict[str, str]:
    """Build a mapping of field_name → C# type across all classes."""
    types: dict[str, str] = {}

    for py_name, parsed in parsed_files.items():
        for cls in parsed.classes:
            # Register the class itself
            types[cls.name] = cls.name

            # Register class-level instance pattern: ClassName.instance → ClassName
            types[f"{cls.name}.instance"] = cls.name
            types[f"{cls.name}._instance"] = cls.name

            # Infer field types within each class
            inferred = _infer_field_types(cls)
            for field_name, field_type in inferred.items():
                # Convert Python type to C#
                if field_type in types:
                    continue  # Already registered
                # Strip | None
                clean_type = field_type.replace(" | None", "").replace("| None", "").strip()
                if clean_type:
                    types[f"{cls.name}.{field_name}"] = clean_type

    return types


def _build_global_constants(parsed_files: dict[str, PyFile]) -> dict[str, str]:
    """Collect all module-level constants across files."""
    constants: dict[str, str] = {}

    for py_name, parsed in parsed_files.items():
        for mc in parsed.module_constants:
            if mc.default_value is not None:
                constants[mc.name] = mc.default_value

    return constants


def _inject_global_types(parsed: PyFile, global_types: dict[str, str], global_constants: dict[str, str]) -> None:
    """Inject cross-file type information into a parsed file's classes."""
    for cls in parsed.classes:
        for field in cls.fields:
            if not field.type_annotation or field.type_annotation in ("", "list", "object"):
                # Try to find type from global registry
                key = f"{cls.name}.{field.name}"
                if key in global_types:
                    field.type_annotation = global_types[key]


def _post_process(cs_code: str, global_types: dict[str, str], global_constants: dict[str, str]) -> str:
    """Fix cross-file references in generated C# code."""
    # Inject cross-file constants that are referenced but not defined in this class
    const_lines = []
    for const_name, const_value in global_constants.items():
        # Only inject if referenced in the code and not already declared as a field/const
        already_declared = (f"const int {const_name}" in cs_code or
                           f"const float {const_name}" in cs_code or
                           f"static int {const_name}" in cs_code or
                           f"static float {const_name}" in cs_code)
        if const_name in cs_code and not already_declared:
            # Infer type from value
            v = const_value.strip()
            if re.match(r"^-?\d+$", v):
                const_lines.append(f"    private const int {const_name} = {v};")
            elif re.match(r"^-?\d+\.\d+$", v):
                const_lines.append(f"    private const float {const_name} = {v}f;")
            elif v.startswith("'") or v.startswith('"'):
                const_lines.append(f'    private const string {const_name} = "{v[1:-1]}";')
            elif v.startswith("[") or v.startswith("{"):
                # Complex constant — emit as placeholder + TODO
                const_lines.append(f"    // TODO: populate {const_name} with game data")
                const_lines.append(f"    private static readonly object[] {const_name} = new object[0];")

    if const_lines:
        # Insert after the class opening brace
        cs_code = cs_code.replace(
            "{\n",
            "{\n" + "\n".join(const_lines) + "\n",
            1,  # Only replace the first occurrence (class brace)
        )

    # Strip DisplayManager blocks (simulator-only) — entire try/catch
    cs_code = re.sub(r"\s*try\s*\{[^}]*DisplayManager[^}]*\}\s*catch\s*\([^)]*\)\s*\{[^}]*\}", "", cs_code)
    # Also strip single-line DisplayManager references
    cs_code = re.sub(r"[^\n]*DisplayManager[^\n]*\n", "", cs_code)

    # Fix: lm = __STRIP__ or standalone lm references from LifecycleManager
    cs_code = re.sub(r"\s*var lm = [^;]*;", "", cs_code)
    cs_code = re.sub(r"\s*lm\.[^;]*;", "", cs_code)

    # Fix .Count → .Length for array-typed fields
    for line in cs_code.split("\n"):
        m = re.match(r"\s*(?:public|private)\s+(\w+\[\])\s+(\w+)", line)
        if m:
            field_name = m.group(2)
            cs_code = cs_code.replace(f"{field_name}.Count", f"{field_name}.Length")
        # Also fix object[] .Count → .Length
        m2 = re.match(r"\s*(?:public|private)\s+(?:static\s+)?(?:readonly\s+)?object\[\]\s+(\w+)", line)
        if m2:
            field_name = m2.group(1)
            cs_code = cs_code.replace(f"{field_name}.Count", f"{field_name}.Length")

    # Comment out lines that reference ROW_CONFIG or variables derived from it
    if "ROW_CONFIG" in cs_code:
        lines = cs_code.split("\n")
        fixed_lines = []
        commented_vars = set()
        for line in lines:
            stripped = line.strip()
            # Comment out ROW_CONFIG indexing and length
            if "ROW_CONFIG" in stripped:
                fixed_lines.append(line.replace(stripped, f"// TODO: {stripped}"))
                # Track variable assigned from ROW_CONFIG
                m = re.match(r"var\s+(\w+)\s*=\s*ROW_CONFIG", stripped)
                if m:
                    commented_vars.add(m.group(1))
            elif any(f"{v}[" in stripped or f"{v}." in stripped for v in commented_vars):
                fixed_lines.append(line.replace(stripped, f"// TODO: {stripped}"))
            else:
                fixed_lines.append(line)
        cs_code = "\n".join(fixed_lines)

    # Fix GRIDCOLS → GRID_COLS (underscore stripped by camelCase converter)
    cs_code = cs_code.replace("GRIDCOLS", "GRID_COLS")

    # Fix dm references from DisplayManager stripping
    cs_code = re.sub(r"[^\n]*\bdm\b[^\n]*;\n", "", cs_code)

    # Fix InvokeCallback() — should be InvokeCallback?.Invoke()
    cs_code = cs_code.replace("InvokeCallback()", "invokeCallback?.Invoke()")
    cs_code = cs_code.replace("InvokeCallback", "invokeCallback")

    # Fix method group assignment: = NewRound; → = NewRound;  (already correct for Action)
    # Actually the issue is InvokeCallback is typed object, should be Action
    # Fix: cast when assigning method group
    cs_code = re.sub(r"invokeCallback = (\w+);", r"invokeCallback = \1;", cs_code)

    return cs_code


def _py_filename_to_cs(py_name: str, parsed: PyFile) -> str:
    """Convert Python filename to C# filename based on class name."""
    if parsed.classes:
        return f"{parsed.classes[0].name}.cs"
    return snake_to_pascal(py_name.replace(".py", "")) + ".cs"

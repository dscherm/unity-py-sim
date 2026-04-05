"""Compilation gate — validates generated C# via syntax checks and optional dotnet build.

Two validation levels:
1. SyntaxCheck (always available): regex-based detection of common translation artifacts
   and C# syntax errors. Catches ~80% of issues without external tools.
2. CompilationCheck (requires dotnet SDK): builds generated C# against UnityEngine stubs.
   Only available when dotnet is on PATH.
"""

from __future__ import annotations

import os
import re
import shutil
import subprocess
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).parent.parent.parent


@dataclass
class CompilationResult:
    file_name: str
    syntax_passed: bool
    syntax_errors: list[str] = field(default_factory=list)
    syntax_warnings: list[str] = field(default_factory=list)
    build_passed: bool | None = None  # None = not attempted
    build_errors: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        if self.build_passed is not None:
            return self.build_passed
        return self.syntax_passed


# ── Syntax Check (no external deps) ─────────────────────────────

# Python artifacts that should never appear in valid C#
_PYTHON_ARTIFACTS = [
    (r"^\s*def\s+\w+", "Python 'def' keyword"),
    (r"^\s*from\s+\w+.*import\s+", "Python 'from...import' statement"),
    (r"^\s*import\s+\w+", "Python 'import' statement"),
    (r'^\s*"""', "Python docstring"),
    (r"^\s*'''", "Python docstring"),
    (r"\bself\.", "Python 'self.' reference"),
    (r"^\s*pass\s*;?\s*$", "Python 'pass' statement"),
    (r"^\s*except\s+", "Python 'except' keyword"),
    (r"^\s*elif\s+", "Python 'elif' keyword"),
    (r"^\s*try:\s*$", "Python 'try:' keyword"),
    (r"\bTrue\b", "Python 'True' literal (should be 'true')"),
    (r"\bFalse\b", "Python 'False' literal (should be 'false')"),
    (r"\bNone\b", "Python 'None' literal (should be 'null')"),
]

# Common C# syntax issues
_SYNTAX_CHECKS = [
    # Unbalanced braces checked separately
    (r":\s*$", "Colon at end of line (Python block syntax)"),
    (r"^\s*#\s", "Python-style comment (should be //)"),
]


def check_syntax(source: str, file_name: str = "<source>") -> CompilationResult:
    """Run syntax validation on generated C# source."""
    errors = []
    warnings = []

    lines = source.split("\n")

    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        if not stripped:
            continue

        # Skip comments and string literals (rough heuristic)
        if stripped.startswith("//") or stripped.startswith("/*"):
            continue

        for pattern, desc in _PYTHON_ARTIFACTS:
            if re.search(pattern, line):
                errors.append(f"L{i}: {desc}: {stripped[:80]}")

        for pattern, desc in _SYNTAX_CHECKS:
            if re.search(pattern, line):
                # Colon at EOL is only an error if it's not a case label or ternary
                if desc.startswith("Colon") and ("case " in stripped or "default:" in stripped):
                    continue
                if desc.startswith("Python-style comment"):
                    # # is a preprocessor directive in C#, but we flag it as warning
                    if not stripped.startswith("#region") and not stripped.startswith("#endregion"):
                        warnings.append(f"L{i}: {desc}: {stripped[:80]}")
                    continue
                errors.append(f"L{i}: {desc}: {stripped[:80]}")

    # Check balanced braces
    open_braces = source.count("{")
    close_braces = source.count("}")
    if open_braces != close_braces:
        errors.append(f"Unbalanced braces: {open_braces} open, {close_braces} close")

    # Check for class declaration
    if "class " not in source and "enum " not in source and "struct " not in source:
        warnings.append("No class/enum/struct declaration found")

    # Check for using directive
    if "using " not in source:
        warnings.append("No 'using' directives found")

    return CompilationResult(
        file_name=file_name,
        syntax_passed=len(errors) == 0,
        syntax_errors=errors,
        syntax_warnings=warnings,
    )


# ── Compilation Check (requires dotnet) ─────────────────────────

_STUBS_DIR = ROOT / "stubs"
_CSPROJ_TEMPLATE = """\
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net8.0</TargetFramework>
    <OutputType>Library</OutputType>
    <Nullable>enable</Nullable>
    <NoWarn>CS0414;CS0169;CS0649;CS8618;CS0108;CS0114;CS1624</NoWarn>
  </PropertyGroup>
</Project>
"""


def dotnet_available() -> bool:
    """Check if dotnet SDK is on PATH."""
    return shutil.which("dotnet") is not None


def check_compilation(source: str, file_name: str = "<source>") -> CompilationResult:
    """Run full compilation check: syntax + dotnet build if available."""
    result = check_syntax(source, file_name)

    if not dotnet_available():
        return result

    # Create temp project with stubs + generated file
    with tempfile.TemporaryDirectory(prefix="unity_gate_") as tmpdir:
        tmp = Path(tmpdir)

        # Write .csproj
        (tmp / "CompileCheck.csproj").write_text(_CSPROJ_TEMPLATE)

        # Copy stubs
        stubs_src = _STUBS_DIR / "UnityEngine.cs"
        if stubs_src.exists():
            shutil.copy(stubs_src, tmp / "UnityEngine.cs")

        stubs_input = _STUBS_DIR / "UnityEngine.InputSystem.cs"
        if stubs_input.exists():
            shutil.copy(stubs_input, tmp / "UnityEngine.InputSystem.cs")

        stubs_collections = _STUBS_DIR / "SystemCollections.cs"
        if stubs_collections.exists():
            shutil.copy(stubs_collections, tmp / "SystemCollections.cs")

        stubs_linq = _STUBS_DIR / "SystemLinq.cs"
        if stubs_linq.exists():
            shutil.copy(stubs_linq, tmp / "SystemLinq.cs")

        stubs_global = _STUBS_DIR / "GlobalUsings.cs"
        if stubs_global.exists():
            shutil.copy(stubs_global, tmp / "GlobalUsings.cs")

        # Write generated file
        (tmp / "Generated.cs").write_text(source, encoding="utf-8")

        # Build
        try:
            proc = subprocess.run(
                ["dotnet", "build", "--nologo", "-v", "quiet"],
                cwd=str(tmp),
                capture_output=True,
                text=True,
                timeout=30,
            )
            result.build_passed = proc.returncode == 0
            if proc.returncode != 0:
                # Extract error lines
                for line in proc.stderr.split("\n") + proc.stdout.split("\n"):
                    if ": error " in line:
                        result.build_errors.append(line.strip())
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            result.build_errors.append(f"Build failed: {e}")
            result.build_passed = False

    return result


def check_file(path: str | Path, file_name: str | None = None) -> CompilationResult:
    """Check a C# file from disk."""
    p = Path(path)
    source = p.read_text(encoding="utf-8")
    return check_compilation(source, file_name or p.name)

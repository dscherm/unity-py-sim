"""Convention gate — checks generated C# follows Unity conventions."""

from __future__ import annotations

import re
from dataclasses import dataclass, field

from src.translator.csharp_parser import parse_csharp, CSharpFile


@dataclass
class ConventionResult:
    passed: bool
    violations: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checks_run: int = 0
    checks_passed: int = 0


def check_conventions(source: str) -> ConventionResult:
    """Check Unity coding conventions on generated C#."""
    violations = []
    warnings = []
    checks_run = 0
    checks_passed = 0

    parsed = parse_csharp(source)

    for cls in parsed.classes:
        # Check 1: MonoBehaviour subclasses inherit correctly
        checks_run += 1
        if cls.is_monobehaviour:
            checks_passed += 1
        elif any("MonoBehaviour" in b for b in cls.base_classes):
            checks_passed += 1

        # Check 2: Using directive present
        checks_run += 1
        if "using UnityEngine;" in source:
            checks_passed += 1
        else:
            violations.append("Missing 'using UnityEngine;' directive")

        # Check 3: Lifecycle methods have correct signatures
        _LIFECYCLE_SIGS = {
            "Awake": ("void", []),
            "Start": ("void", []),
            "Update": ("void", []),
            "FixedUpdate": ("void", []),
            "LateUpdate": ("void", []),
            "OnDestroy": ("void", []),
            "OnEnable": ("void", []),
            "OnDisable": ("void", []),
            "OnCollisionEnter2D": ("void", ["Collision2D"]),
            "OnCollisionExit2D": ("void", ["Collision2D"]),
            "OnTriggerEnter2D": ("void", ["Collider2D"]),
            "OnTriggerExit2D": ("void", ["Collider2D"]),
        }

        for method in cls.methods:
            if method.name in _LIFECYCLE_SIGS:
                checks_run += 1
                expected_ret, expected_params = _LIFECYCLE_SIGS[method.name]
                if method.return_type != expected_ret:
                    violations.append(
                        f"{cls.name}.{method.name}: expected return type '{expected_ret}', "
                        f"got '{method.return_type}'"
                    )
                else:
                    checks_passed += 1

                # Check parameter count
                if expected_params:
                    checks_run += 1
                    if len(method.parameters) != len(expected_params):
                        violations.append(
                            f"{cls.name}.{method.name}: expected {len(expected_params)} params, "
                            f"got {len(method.parameters)}"
                        )
                    else:
                        checks_passed += 1

        # Check 4: No 'new MonoBehaviour()' (must use AddComponent)
        checks_run += 1
        if "new MonoBehaviour()" in source:
            violations.append("Found 'new MonoBehaviour()' — use AddComponent instead")
        else:
            checks_passed += 1

        # Check 5: SerializeField on private fields
        for f in cls.fields:
            if "SerializeField" in f.attributes:
                checks_run += 1
                if "private" in f.modifiers:
                    checks_passed += 1
                else:
                    warnings.append(
                        f"{cls.name}.{f.name}: [SerializeField] typically used with private fields"
                    )
                    checks_passed += 1  # Warning, not violation

        # Check 6: Class name matches PascalCase
        checks_run += 1
        if cls.name[0].isupper():
            checks_passed += 1
        else:
            violations.append(f"Class name '{cls.name}' should be PascalCase")

    return ConventionResult(
        passed=len(violations) == 0,
        violations=violations,
        warnings=warnings,
        checks_run=checks_run,
        checks_passed=checks_passed,
    )

# Fix Plan — Translator & Validation Gaps

Generated from end-to-end validation run (2026-04-07).
97 test failures across 3 root cause clusters + 4 C# structural gate failures.

---

## Critical

- [x] **[T1] Translate Python `in` operator to C# equivalents** — Python `x in dict` leaks as-is into C# output. Must translate to `dict.ContainsKey(x)` for dicts, `list.Contains(x)` for lists/sets. Causes 4 structural gate failures in Pacman V2 C# (AnimatedSprite.cs, GameManager.cs, GhostScatter.cs, Passage.cs). Add `_translate_in_operator()` to `python_to_csharp.py`, handle Compare nodes with `In`/`NotIn` ops in `_translate_py_expression()`. TDD: write failing tests first for `x in dict`, `x in list`, `x not in set`, `for k in dict` (already works). Validation agent writes contract + mutation tests.
- [x] **[T2] Fix Math.Max/Min → Mathf.Max/Min** — Lines 1520-1521 of python_to_csharp.py emit `Math.Max()` / `Math.Min()` instead of Unity's `Mathf.Max()` / `Mathf.Min()`. One-line fix per call. Also handle `abs()` → `Mathf.Abs()`, `round()` → `Mathf.Round()`. TDD: write tests asserting `Mathf.` prefix before fixing. Validation agent writes mutation tests proving `Math.` would fail.

## High

- [x] **[T3] Fix Input System translation (60+ test failures)** — Code exists at lines 1282-1332 but `translate_file()` doesn't pass `input_system` config through. The `translate_file()` function at line 44 calls `parse_python_file()` then `translate()` but may not forward the input_system parameter. Debug why `Input.get_key_down('escape')` produces empty Update() body instead of `Keyboard.current.escapeKey.wasPressedThisFrame`. Fix the parameter plumbing. TDD: write minimal reproduction test before fixing. Validation agent writes full input system contract tests.
- [x] **[T4] Bool truthiness — expand detection beyond explicit annotations** — Current code (lines 76-87) only detects bools from `": bool"` annotations or `True`/`False` defaults. Must also handle: compound conditions (`if flag and obj:`), properties from known Unity types (`gameObject.activeSelf`), and fields set to comparison results. TDD: write tests for compound conditions and inferred bools. Validation agent writes edge-case contract tests.

## Medium

- [x] **[T5] Update Pacman V2 ghost tests to match V2 API** — 30+ test failures in `test_pacman_tasks45_contract.py`, `test_pacman_tasks45_integration.py`, `test_pacman_tasks45_mutation.py` test against V1 ghost API (`GhostBehavior.enable(duration)`) but V2 restructured. These tests need rewriting — NOT the source code. Spawn validation agent to write fresh V2-aware contract/integration/mutation tests from the actual V2 source, then delete stale V1 tests.
- [x] **[T6] Register Pacman V2 in playtest.py** — `python tools/playtest.py pacman_v2` fails with "Unknown example". Add pacman_v2 entry to the playtest registry so headless validation works.

## Low

- [ ] **[T7] Pacman V2 Task 7 validation gate** — After T1-T4 fixes, re-run translator on Pacman V2 Python, re-run structural + convention gates. Target: 16/16 structural pass (currently 12/16). Update plan.md Task 7 to `"passes": true` when gates pass.

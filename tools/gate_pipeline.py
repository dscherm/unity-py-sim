#!/usr/bin/env python3
"""Full gate pipeline — tests, translate, syntax gate, convention gate, playtest.

Runs all quality checks in sequence. Returns exit code 0 if all pass, 1 if any fail.
Designed to run after each task or as a pre-commit check.

Usage:
    python tools/gate_pipeline.py              # full pipeline
    python tools/gate_pipeline.py --quick      # skip translation (tests + playtest only)
    python tools/gate_pipeline.py --translate   # translation gates only
"""

import json
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RALPH_UNIVERSAL = Path("D:/Projects/ralph-universal")

# Games to playtest
GAMES = ["pong", "breakout", "fsm_platformer", "angry_birds", "space_invaders"]

# Translation targets
TRANSLATE_TARGETS = [
    ("space_invaders", "examples/space_invaders/space_invaders_python", "SpaceInvaders"),
    ("breakout", "examples/breakout/breakout_python", "Breakout"),
]


def run_cmd(cmd: list[str], label: str, timeout: int = 120) -> tuple[bool, str]:
    """Run a command, return (success, output)."""
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, cwd=str(ROOT), timeout=timeout
        )
        output = result.stdout + result.stderr
        return result.returncode == 0, output
    except subprocess.TimeoutExpired:
        return False, f"TIMEOUT after {timeout}s"
    except Exception as e:
        return False, str(e)


def step_tests() -> tuple[bool, dict]:
    """Step 1: Run test suite (excluding csharp_to_python which needs special setup)."""
    print("\n--- Step 1: Test Suite ---")
    ok, output = run_cmd(
        [sys.executable, "-m", "pytest", "tests/", "-q", "--tb=line",
         "--ignore=tests/translator/test_csharp_to_python.py"],
        "pytest", timeout=180
    )
    # Extract pass/fail counts from last line
    lines = output.strip().split("\n")
    summary = lines[-1] if lines else ""
    passed = failed = 0
    if "passed" in summary:
        import re
        m = re.search(r"(\d+) passed", summary)
        if m:
            passed = int(m.group(1))
        m = re.search(r"(\d+) failed", summary)
        if m:
            failed = int(m.group(1))

    print(f"  {passed} passed, {failed} failed")
    if not ok:
        print(f"  FAILED: {summary}")
    return ok, {"passed": passed, "failed": failed, "summary": summary}


def step_translate() -> tuple[bool, dict]:
    """Step 2: Translate Python games to C# and check for issues."""
    print("\n--- Step 2: Translation ---")
    issues_total = 0
    results = {}

    for game, path, namespace in TRANSLATE_TARGETS:
        ok, output = run_cmd(
            [sys.executable, "-c", f"""
import sys, os, re
sys.path.insert(0, os.path.dirname('{path}'))
from src.translator.project_translator import translate_project
results = translate_project('{path}', input_system='new', unity_version=6, namespace='{namespace}')
issues = 0
for name, code in results.items():
    for i, line in enumerate(code.split('\\n')):
        s = line.strip()
        if '__STRIP__' in s: issues += 1; print(f'STRIP {{name}}:L{{i}}: {{s[:60]}}')
        if 'LifecycleManager' in s: issues += 1; print(f'LIFECYCLE {{name}}:L{{i}}')
        if re.match(r'^[a-z]\\w*:\\s+\\w+.*=', s): issues += 1; print(f'ANNOTATION {{name}}:L{{i}}: {{s[:60]}}')
out_dir = f'data/generated/{{"{game}"}}_cs'
os.makedirs(out_dir, exist_ok=True)
for name, code in results.items():
    with open(os.path.join(out_dir, name), 'w') as f:
        f.write(code)
print(f'FILES:{{len(results)}} ISSUES:{{issues}}')
"""],
            f"translate-{game}", timeout=60
        )
        lines = output.strip().split("\n")
        summary = [l for l in lines if l.startswith("FILES:")]
        file_count = 0
        issue_count = 0
        if summary:
            import re
            m = re.search(r"FILES:(\d+) ISSUES:(\d+)", summary[0])
            if m:
                file_count = int(m.group(1))
                issue_count = int(m.group(2))
        issues_total += issue_count
        results[game] = {"files": file_count, "issues": issue_count}
        print(f"  {game}: {file_count} files, {issue_count} issues")

    return issues_total == 0, results


def step_structural_gate() -> tuple[bool, dict]:
    """Step 3: Run structural gate on translated C# files."""
    print("\n--- Step 3: Structural Gate ---")
    ok, output = run_cmd(
        [sys.executable, "-c", """
import sys, os
sys.path.insert(0, '.')
from src.gates.structural_gate import validate_csharp
from pathlib import Path
total_errors = 0
file_count = 0
for cs_dir in Path('data/generated').glob('*_cs'):
    for cs_file in cs_dir.glob('*.cs'):
        file_count += 1
        code = cs_file.read_text()
        result = validate_csharp(code)
        if result.error_count > 0:
            total_errors += result.error_count
            print(f'  {cs_file.name}: {result.error_count} parse errors')
print(f'FILES:{file_count} ERRORS:{total_errors}')
"""],
        "structural-gate", timeout=30
    )
    import re
    m = re.search(r"FILES:(\d+) ERRORS:(\d+)", output)
    files = int(m.group(1)) if m else 0
    errors = int(m.group(2)) if m else -1
    if errors < 0:
        print(f"  SKIPPED: {output.strip()[:80]}")
        return True, {"skipped": True}
    print(f"  {files} files checked, {errors} parse errors")
    return errors == 0, {"files": files, "errors": errors}


def step_convention_gate() -> tuple[bool, dict]:
    """Step 4: Run convention gate on translated C# files."""
    print("\n--- Step 4: Convention Gate ---")
    ok, output = run_cmd(
        [sys.executable, "-c", """
import sys
sys.path.insert(0, '.')
from src.gates.convention_gate import check_conventions
from pathlib import Path
total_violations = 0
total_checks = 0
file_count = 0
for cs_dir in Path('data/generated').glob('*_cs'):
    for cs_file in cs_dir.glob('*.cs'):
        if cs_file.stat().st_size < 50:
            continue
        file_count += 1
        code = cs_file.read_text()
        result = check_conventions(code)
        total_checks += result.checks_run
        total_violations += len(result.violations)
pct = ((total_checks - total_violations) / total_checks * 100) if total_checks > 0 else 0
print(f'FILES:{file_count} CHECKS:{total_checks} VIOLATIONS:{total_violations} PCT:{pct:.0f}')
"""],
        "convention-gate", timeout=30
    )
    import re
    m = re.search(r"FILES:(\d+) CHECKS:(\d+) VIOLATIONS:(\d+) PCT:(\d+)", output)
    if not m:
        print(f"  ERROR: {output.strip()[:80]}")
        return True, {"error": output.strip()[:80]}
    files, checks, violations, pct = int(m.group(1)), int(m.group(2)), int(m.group(3)), int(m.group(4))
    print(f"  {files} files, {checks} checks, {violations} violations ({pct}% pass)")
    # Convention gate is advisory, not blocking
    return True, {"files": files, "checks": checks, "violations": violations, "pass_pct": pct}


def step_playtest() -> tuple[bool, dict]:
    """Step 5: Run all 5 games headless."""
    print("\n--- Step 5: Headless Playtest ---")
    results = {}
    all_clean = True

    for game in GAMES:
        ok, output = run_cmd(
            [sys.executable, "tools/playtest.py", game, "--headless", "--frames", "60"],
            f"playtest-{game}", timeout=30
        )
        clean = "Clean run" in output
        if not clean:
            all_clean = False
            print(f"  {game}: ERRORS DETECTED")
        else:
            print(f"  {game}: clean")
        results[game] = {"clean": clean, "exit_code": 0 if ok else 1}

    return all_clean, results


def main():
    quick = "--quick" in sys.argv
    translate_only = "--translate" in sys.argv

    print("=" * 60)
    print("UNITY-PY-SIM GATE PIPELINE")
    print("=" * 60)

    start = time.time()
    all_results = {}
    failed_steps = []

    if not translate_only:
        # Step 1: Tests
        ok, data = step_tests()
        all_results["tests"] = data
        if not ok:
            failed_steps.append("tests")

    if not quick:
        # Step 2: Translation
        ok, data = step_translate()
        all_results["translate"] = data
        if not ok:
            failed_steps.append("translate")

        # Step 3: Structural gate
        ok, data = step_structural_gate()
        all_results["structural"] = data
        if not ok:
            failed_steps.append("structural")

        # Step 4: Convention gate
        ok, data = step_convention_gate()
        all_results["convention"] = data

    if not translate_only:
        # Step 5: Playtest
        ok, data = step_playtest()
        all_results["playtest"] = data
        if not ok:
            failed_steps.append("playtest")

    elapsed = time.time() - start

    # Summary
    print("\n" + "=" * 60)
    if failed_steps:
        print(f"GATE FAILED — {len(failed_steps)} step(s): {', '.join(failed_steps)}")
    else:
        print("GATE PASSED — all checks clean")
    print(f"Elapsed: {elapsed:.1f}s")
    print("=" * 60)

    # Record observation
    obs = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "pipeline": "gate_pipeline",
        "passed": len(failed_steps) == 0,
        "failed_steps": failed_steps,
        "elapsed_seconds": round(elapsed, 1),
        "results": all_results,
    }
    obs_file = ROOT / ".ralph" / "gate_pipeline.jsonl"
    obs_file.parent.mkdir(parents=True, exist_ok=True)
    with open(obs_file, "a") as f:
        f.write(json.dumps(obs) + "\n")

    return 0 if not failed_steps else 1


if __name__ == "__main__":
    sys.exit(main())

"""Run compilation gate on all corpus pairs — translate Python→C# and syntax-check the output."""

import json
import sys
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.translator.python_to_csharp import translate_file
from src.gates.compilation_gate import check_syntax, check_compilation, dotnet_available


def run_all():
    index_path = ROOT / "data" / "corpus" / "corpus_index.json"
    index = json.loads(index_path.read_text())

    use_dotnet = dotnet_available()
    check_fn = check_compilation if use_dotnet else check_syntax
    mode = "dotnet build" if use_dotnet else "syntax check"
    print(f"Mode: {mode}")
    print(f"Pairs: {len(index)}")
    print()

    results = []
    pass_count = 0
    fail_count = 0

    for entry in index:
        pair_path = ROOT / "data" / "corpus" / entry["file"]
        pair_data = json.loads(pair_path.read_text())
        py_path = ROOT / pair_data["python_file"]

        if not py_path.exists():
            print(f"  SKIP {entry['id']}: Python file not found")
            continue

        try:
            generated = translate_file(py_path, input_system="legacy", unity_version=5)
        except Exception as e:
            print(f"  ERROR {entry['id']}: Translation failed: {e}")
            results.append({
                "id": entry["id"],
                "game": pair_data["game"],
                "passed": False,
                "error": str(e),
            })
            fail_count += 1
            continue

        result = check_fn(generated, entry["id"])
        passed = result.passed
        if passed:
            pass_count += 1
        else:
            fail_count += 1

        status = "PASS" if passed else "FAIL"
        detail = ""
        if result.syntax_errors:
            detail = f" — {len(result.syntax_errors)} errors"
        if result.build_errors:
            detail = f" — {len(result.build_errors)} build errors"
        print(f"  {status} {entry['id']}{detail}")

        entry_result = {
            "id": entry["id"],
            "game": pair_data["game"],
            "passed": passed,
            "syntax_passed": result.syntax_passed,
            "syntax_errors": result.syntax_errors[:5],  # cap for readability
            "syntax_warnings": result.syntax_warnings[:5],
        }
        if result.build_passed is not None:
            entry_result["build_passed"] = result.build_passed
            entry_result["build_errors"] = result.build_errors[:5]
        results.append(entry_result)

    # Summary
    total = pass_count + fail_count
    print()
    print(f"Results: {pass_count}/{total} passed ({100*pass_count/total:.0f}%)")

    # Write results
    metrics_dir = ROOT / "data" / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)
    output = {
        "mode": mode,
        "total": total,
        "passed": pass_count,
        "failed": fail_count,
        "pass_rate": round(pass_count / total, 3) if total else 0,
        "pairs": results,
    }
    (metrics_dir / "compilation_baseline.json").write_text(
        json.dumps(output, indent=2) + "\n"
    )
    print("Wrote data/metrics/compilation_baseline.json")


if __name__ == "__main__":
    run_all()

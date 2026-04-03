"""Forward-translation scoring — translate Python→C# and compare to hand-written reference.

Does NOT require tree_sitter_c_sharp. Uses regex-based extraction of class names,
method signatures, field names, and using directives from C# text.
"""

import json
import re
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT))

from src.translator.python_to_csharp import translate_file


@dataclass
class PairScore:
    pair_id: str
    game: str
    python_file: str
    csharp_file: str
    class_score: float = 0.0       # class names match
    method_score: float = 0.0      # method names present
    field_score: float = 0.0       # field names present
    using_score: float = 0.0       # using directives match
    overall_score: float = 0.0     # weighted average
    details: list[str] = field(default_factory=list)
    error: str | None = None


def _extract_classes(cs_text: str) -> list[str]:
    """Extract class/enum names from C# source."""
    return re.findall(r"(?:public\s+)?(?:class|enum|struct)\s+(\w+)", cs_text)


def _extract_methods(cs_text: str) -> list[str]:
    """Extract method names from C# source."""
    return re.findall(r"(?:void|int|float|bool|string|IEnumerator|var|\w+)\s+(\w+)\s*\(", cs_text)


def _extract_fields(cs_text: str) -> list[str]:
    """Extract field names from C# source (SerializeField, private, public)."""
    fields = re.findall(r"(?:private|public|protected)\s+(?:static\s+)?(?:\w+)\s+(\w+)\s*[;=]", cs_text)
    return fields


def _extract_usings(cs_text: str) -> set[str]:
    """Extract using directives."""
    return set(re.findall(r"using\s+([\w.]+);", cs_text))


def _jaccard(set_a: set, set_b: set) -> float:
    """Jaccard similarity between two sets."""
    if not set_a and not set_b:
        return 1.0
    union = set_a | set_b
    if not union:
        return 1.0
    return len(set_a & set_b) / len(union)


def _recall(reference: set, generated: set) -> float:
    """What fraction of reference items appear in generated."""
    if not reference:
        return 1.0
    return len(reference & generated) / len(reference)


def score_pair(pair_data: dict) -> PairScore:
    """Score a single translation pair."""
    py_path = ROOT / pair_data["python_file"]
    cs_path = ROOT / pair_data["unity_file"]
    pair_id = pair_data["id"]
    game = pair_data["game"]

    result = PairScore(
        pair_id=pair_id, game=game,
        python_file=pair_data["python_file"],
        csharp_file=pair_data["unity_file"],
    )

    if not py_path.exists():
        result.error = f"Python file not found: {py_path}"
        return result
    if not cs_path.exists():
        result.error = f"C# file not found: {cs_path}"
        return result

    # Generate C# from Python (use legacy input to match hand-written refs)
    try:
        generated = translate_file(py_path, input_system="legacy", unity_version=5)
    except Exception as e:
        result.error = f"Translation error: {e}"
        return result

    reference = cs_path.read_text(encoding="utf-8")

    # Score classes
    ref_classes = set(_extract_classes(reference))
    gen_classes = set(_extract_classes(generated))
    result.class_score = _jaccard(ref_classes, gen_classes)
    missing_classes = ref_classes - gen_classes
    if missing_classes:
        result.details.append(f"Missing classes: {missing_classes}")

    # Score methods (recall: what % of ref methods appear in generated)
    ref_methods = set(_extract_methods(reference))
    gen_methods = set(_extract_methods(generated))
    result.method_score = _recall(ref_methods, gen_methods)
    missing_methods = ref_methods - gen_methods
    if missing_methods:
        result.details.append(f"Missing methods: {missing_methods}")

    # Score fields (recall)
    ref_fields = set(_extract_fields(reference))
    gen_fields = set(_extract_fields(generated))
    result.field_score = _recall(ref_fields, gen_fields)
    missing_fields = ref_fields - gen_fields
    if missing_fields:
        result.details.append(f"Missing fields: {missing_fields}")

    # Score usings (jaccard)
    ref_usings = _extract_usings(reference)
    gen_usings = _extract_usings(generated)
    result.using_score = _jaccard(ref_usings, gen_usings)

    # Overall: weighted average
    result.overall_score = round(
        result.class_score * 0.3 +
        result.method_score * 0.35 +
        result.field_score * 0.25 +
        result.using_score * 0.1,
        3,
    )

    return result


def run_all():
    """Score all pairs in the corpus and write baseline.json."""
    index_path = ROOT / "data" / "corpus" / "corpus_index.json"
    index = json.loads(index_path.read_text())

    results = []
    for entry in index:
        pair_path = ROOT / "data" / "corpus" / entry["file"]
        pair_data = json.loads(pair_path.read_text())
        score = score_pair(pair_data)
        results.append(score)

    # Write baseline
    metrics_dir = ROOT / "data" / "metrics"
    metrics_dir.mkdir(parents=True, exist_ok=True)

    baseline = {
        "total_pairs": len(results),
        "avg_overall": round(sum(r.overall_score for r in results) / len(results), 3),
        "avg_class": round(sum(r.class_score for r in results) / len(results), 3),
        "avg_method": round(sum(r.method_score for r in results) / len(results), 3),
        "avg_field": round(sum(r.field_score for r in results) / len(results), 3),
        "avg_using": round(sum(r.using_score for r in results) / len(results), 3),
        "by_game": {},
        "pairs": [],
    }

    # Group by game
    games = sorted(set(r.game for r in results))
    for game in games:
        game_results = [r for r in results if r.game == game]
        baseline["by_game"][game] = {
            "count": len(game_results),
            "avg_overall": round(sum(r.overall_score for r in game_results) / len(game_results), 3),
            "avg_class": round(sum(r.class_score for r in game_results) / len(game_results), 3),
            "avg_method": round(sum(r.method_score for r in game_results) / len(game_results), 3),
            "avg_field": round(sum(r.field_score for r in game_results) / len(game_results), 3),
        }

    # Sort by overall score ascending (worst first)
    sorted_results = sorted(results, key=lambda r: r.overall_score)
    for r in sorted_results:
        baseline["pairs"].append({
            "id": r.pair_id,
            "game": r.game,
            "overall": r.overall_score,
            "class": r.class_score,
            "method": r.method_score,
            "field": r.field_score,
            "using": r.using_score,
            "details": r.details,
            "error": r.error,
        })

    (metrics_dir / "baseline.json").write_text(
        json.dumps(baseline, indent=2) + "\n"
    )

    # Print summary
    print(f"Scored {len(results)} pairs")
    print(f"Average overall: {baseline['avg_overall']}")
    print(f"Average class:   {baseline['avg_class']}")
    print(f"Average method:  {baseline['avg_method']}")
    print(f"Average field:   {baseline['avg_field']}")
    print(f"Average using:   {baseline['avg_using']}")
    print()
    for game, stats in baseline["by_game"].items():
        print(f"  {game}: {stats['count']} pairs, avg={stats['avg_overall']}")
    print()
    print("5 worst-scoring pairs:")
    for r in sorted_results[:5]:
        print(f"  {r.pair_id} ({r.game}): {r.overall_score} — {'; '.join(r.details[:2]) if r.details else r.error or 'ok'}")


if __name__ == "__main__":
    run_all()

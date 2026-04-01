"""Translation accuracy tracking — records scores to data/metrics/."""

from __future__ import annotations

import json
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class AccuracyScore:
    file_name: str
    timestamp: str
    structural_score: float  # 0-1: class/method structure match
    type_score: float        # 0-1: types correctly mapped
    naming_score: float      # 0-1: naming conventions correct
    overall_score: float     # 0-1: weighted average
    notes: str = ""


_METRICS_DIR = Path(__file__).parent.parent.parent / "data" / "metrics"


def record_accuracy(score: AccuracyScore, filename: str = "translation_accuracy.jsonl") -> None:
    """Append an accuracy score to the JSONL metrics file."""
    _METRICS_DIR.mkdir(parents=True, exist_ok=True)
    filepath = _METRICS_DIR / filename
    with open(filepath, "a") as f:
        f.write(json.dumps(asdict(score)) + "\n")


def record_roundtrip(file_name: str, fidelity: float, notes: str = "") -> None:
    """Record a roundtrip fidelity score."""
    _METRICS_DIR.mkdir(parents=True, exist_ok=True)
    filepath = _METRICS_DIR / "roundtrip_fidelity.jsonl"
    entry = {
        "file_name": file_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "fidelity": fidelity,
        "notes": notes,
    }
    with open(filepath, "a") as f:
        f.write(json.dumps(entry) + "\n")


def load_scores(filename: str = "translation_accuracy.jsonl") -> list[dict]:
    """Load all recorded accuracy scores."""
    filepath = _METRICS_DIR / filename
    if not filepath.exists():
        return []
    scores = []
    for line in filepath.read_text().strip().split("\n"):
        if line.strip():
            scores.append(json.loads(line))
    return scores

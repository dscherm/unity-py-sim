"""ASP-7 Gate — playground-fidelity check (advisory in CI, ratchets to required).

The gate enforces SUCCESS.md ASP-7:

    A game "passes" ASP-7 when the author needs <= J=5 runtime-behavior
    tweaks within 72h of the deploy commit to reach shippable feel.
    The criterion as a whole passes when >= N=3 games clear that bar.

Inputs are author-written feel journals at `data/lessons/<game>_feel_journal.md`
with a YAML frontmatter block (see `data/lessons/_feel_journal_template.md`
for the canonical schema). The gate parses, validates, and counts tweaks
within the [deploy_at, deploy_at + 72h] window per game.

Usage:
    python -m src.gates.asp7_gate              # enforce mode (CI default)
    python -m src.gates.asp7_gate --check      # advisory; always exit 0
    python -m src.gates.asp7_gate --json out.json  # write structured status

Exit codes:
    0 — total_passed >= N (or --check used regardless of result)
    1 — total_passed < N (enforce mode only)
    2 — schema / I/O error (e.g. missing required field, bad date)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
LESSONS_DIR = REPO_ROOT / "data" / "lessons"
DEFAULT_STATUS_PATH = REPO_ROOT / "data" / "metrics" / "asp7_status.json"

THRESHOLD_J = 5  # max tweaks per game within window
THRESHOLD_N = 3  # min games required to pass overall
WINDOW_HOURS = 72

ALLOWED_CATEGORIES = frozenset(
    {"physics-constant", "animation-timing", "audio-mix", "control-feel", "other"}
)
REQUIRED_FRONTMATTER_KEYS = frozenset({"game", "deploy_commit", "deploy_at", "tweaks"})
REQUIRED_TWEAK_KEYS = frozenset({"when", "what", "category"})

JOURNAL_GLOB = "*_feel_journal.md"
TEMPLATE_NAME = "_feel_journal_template.md"


def _relpath(p: Path) -> str:
    """Return path relative to REPO_ROOT when possible, else absolute.

    Always emits forward slashes via PurePath.as_posix() so journal_path
    values in asp7_status.json stay byte-identical between Windows
    development and the Linux CI runner that overwrites the file."""
    try:
        return p.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return Path(p).as_posix()


@dataclass
class GameResult:
    game: str
    deploy_commit: str
    deploy_at: str
    shipped_at: str | None
    tweak_count: int  # all tweaks in journal
    in_window_count: int  # tweaks within [deploy_at, deploy_at + 72h]
    passed: bool
    journal_path: str
    notes: str | None = None


@dataclass
class GateResult:
    games: list[GameResult] = field(default_factory=list)
    total_passed: int = 0
    asp7_passed: bool = False
    threshold_J: int = THRESHOLD_J
    threshold_N: int = THRESHOLD_N
    window_hours: int = WINDOW_HOURS

    def to_dict(self) -> dict[str, Any]:
        return {
            "games": [asdict(g) for g in self.games],
            "total_passed": self.total_passed,
            "asp7_passed": self.asp7_passed,
            "threshold_J": self.threshold_J,
            "threshold_N": self.threshold_N,
            "window_hours": self.window_hours,
        }


class JournalSchemaError(ValueError):
    """Raised when a journal's frontmatter is malformed or missing required fields."""


# ── Frontmatter parsing ────────────────────────────────────────────────────


_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---\s*(.*)$", re.DOTALL)


def _parse_frontmatter(path: Path) -> dict[str, Any]:
    """Read a journal file, extract and parse its YAML frontmatter."""
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as e:
        raise JournalSchemaError(f"{path}: cannot read ({e})") from e

    m = _FRONTMATTER_RE.match(text)
    if not m:
        raise JournalSchemaError(
            f"{path}: missing YAML frontmatter (expected '---\\n...\\n---' at start)"
        )

    try:
        data = yaml.safe_load(m.group(1))
    except yaml.YAMLError as e:
        raise JournalSchemaError(f"{path}: YAML parse error: {e}") from e

    if not isinstance(data, dict):
        raise JournalSchemaError(f"{path}: frontmatter must be a mapping")

    return data


def _parse_iso_utc(value: Any, *, field_name: str, where: Path) -> datetime:
    """Parse an ISO-8601 UTC timestamp; require explicit UTC suffix or offset."""
    if not isinstance(value, str):
        raise JournalSchemaError(
            f"{where}: {field_name} must be ISO-8601 string, got {type(value).__name__}"
        )
    s = value.strip()
    # Tolerate a trailing 'Z' (Python <3.11 datetime.fromisoformat doesn't).
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    try:
        dt = datetime.fromisoformat(s)
    except ValueError as e:
        raise JournalSchemaError(f"{where}: {field_name} not ISO-8601: {value!r} ({e})") from e
    if dt.tzinfo is None:
        raise JournalSchemaError(
            f"{where}: {field_name} missing timezone (use 'Z' or '+00:00'): {value!r}"
        )
    return dt.astimezone(timezone.utc)


def _validate_journal(data: dict[str, Any], path: Path) -> None:
    """Raise JournalSchemaError if the frontmatter is missing required fields
    or contains tweaks with invalid shape / categories."""
    missing = REQUIRED_FRONTMATTER_KEYS - set(data.keys())
    if missing:
        raise JournalSchemaError(
            f"{path}: missing required keys: {sorted(missing)}"
        )

    tweaks = data.get("tweaks") or []
    if not isinstance(tweaks, list):
        raise JournalSchemaError(f"{path}: 'tweaks' must be a list, got {type(tweaks).__name__}")

    for i, tw in enumerate(tweaks):
        if not isinstance(tw, dict):
            raise JournalSchemaError(
                f"{path}: tweak[{i}] must be a mapping, got {type(tw).__name__}"
            )
        missing_tw = REQUIRED_TWEAK_KEYS - set(tw.keys())
        if missing_tw:
            raise JournalSchemaError(
                f"{path}: tweak[{i}] missing required keys: {sorted(missing_tw)}"
            )
        cat = tw["category"]
        if cat not in ALLOWED_CATEGORIES:
            raise JournalSchemaError(
                f"{path}: tweak[{i}].category={cat!r} not in allowed set "
                f"{sorted(ALLOWED_CATEGORIES)}"
            )
        # Validate timestamp shape (parse but discard).
        _parse_iso_utc(tw["when"], field_name=f"tweak[{i}].when", where=path)


# ── Per-game evaluation ────────────────────────────────────────────────────


def _evaluate_journal(path: Path) -> GameResult:
    """Parse + validate a journal; compute tweak counts and pass status."""
    data = _parse_frontmatter(path)
    _validate_journal(data, path)

    deploy_at = _parse_iso_utc(data["deploy_at"], field_name="deploy_at", where=path)
    window_end = deploy_at + timedelta(hours=WINDOW_HOURS)
    tweaks = data.get("tweaks") or []

    in_window = 0
    for tw in tweaks:
        when = _parse_iso_utc(tw["when"], field_name="tweak.when", where=path)
        if deploy_at <= when <= window_end:
            in_window += 1

    passed = in_window <= THRESHOLD_J

    return GameResult(
        game=str(data["game"]),
        deploy_commit=str(data["deploy_commit"]),
        deploy_at=deploy_at.isoformat().replace("+00:00", "Z"),
        shipped_at=str(data["shipped_at"]) if data.get("shipped_at") else None,
        tweak_count=len(tweaks),
        in_window_count=in_window,
        passed=passed,
        journal_path=_relpath(path),
        notes=str(data["notes"]).strip() if data.get("notes") else None,
    )


# ── Discovery ──────────────────────────────────────────────────────────────


def _discover_journals(lessons_dir: Path) -> list[Path]:
    """Find all *_feel_journal.md files, excluding the canonical template."""
    if not lessons_dir.exists():
        return []
    return sorted(
        p for p in lessons_dir.glob(JOURNAL_GLOB) if p.name != TEMPLATE_NAME
    )


# ── Main entrypoint ────────────────────────────────────────────────────────


def run_gate(*, lessons_dir: Path = LESSONS_DIR) -> GateResult:
    """Discover, parse, evaluate every feel journal under lessons_dir."""
    result = GateResult()
    for path in _discover_journals(lessons_dir):
        result.games.append(_evaluate_journal(path))

    result.total_passed = sum(1 for g in result.games if g.passed)
    result.asp7_passed = result.total_passed >= THRESHOLD_N
    return result


def _format_summary(result: GateResult, *, mode: str) -> str:
    lines = [
        f"asp7_gate: {'CHECK' if mode == 'check' else 'ENFORCE'} mode "
        f"(J<={result.threshold_J} per game, N>={result.threshold_N} games, "
        f"{result.window_hours}h window)",
        f"asp7_gate: {result.total_passed}/{len(result.games)} game(s) below "
        f"the per-game tweak budget; need >= {result.threshold_N} to mark ASP-7 passing.",
    ]
    if not result.games:
        lines.append(
            "asp7_gate: no feel journals found "
            f"(expected `{_relpath(LESSONS_DIR)}/<game>_feel_journal.md`)."
        )
    for g in result.games:
        flag = "PASS" if g.passed else "FAIL"
        lines.append(
            f"  - {g.game}: {flag} ({g.in_window_count}/{result.threshold_J} in-window "
            f"tweaks; deploy_commit={g.deploy_commit})"
        )
    if result.asp7_passed:
        lines.append("asp7_gate: ASP-7 PASSING")
    else:
        lines.append("asp7_gate: ASP-7 not yet passing (advisory).")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="ASP-7 playground-fidelity gate.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Advisory mode: print status, always exit 0 unless schema error.",
    )
    parser.add_argument(
        "--json",
        default=None,
        metavar="PATH",
        help="Write structured status to PATH (JSON). Default: do not write.",
    )
    parser.add_argument(
        "--lessons-dir",
        default=str(LESSONS_DIR),
        help="Override journals directory (default: data/lessons/).",
    )
    parser.add_argument(
        "--write-status",
        action="store_true",
        help=f"Also write status to default location ({_relpath(DEFAULT_STATUS_PATH)}).",
    )
    args = parser.parse_args(argv)

    try:
        result = run_gate(lessons_dir=Path(args.lessons_dir))
    except JournalSchemaError as e:
        print(f"asp7_gate: schema error: {e}", file=sys.stderr)
        return 2
    except Exception as e:  # noqa: BLE001
        print(f"asp7_gate: error: {type(e).__name__}: {e}", file=sys.stderr)
        return 2

    print(_format_summary(result, mode="check" if args.check else "enforce"))

    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(
            json.dumps(result.to_dict(), indent=2) + "\n", encoding="utf-8"
        )
    if args.write_status:
        DEFAULT_STATUS_PATH.parent.mkdir(parents=True, exist_ok=True)
        DEFAULT_STATUS_PATH.write_text(
            json.dumps(result.to_dict(), indent=2) + "\n", encoding="utf-8"
        )

    if args.check:
        return 0
    return 0 if result.asp7_passed else 1


if __name__ == "__main__":
    sys.exit(main())

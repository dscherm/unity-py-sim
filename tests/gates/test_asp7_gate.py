"""Tests for src/gates/asp7_gate.py — ASP-7 playground-fidelity gate."""

from __future__ import annotations

import json
import textwrap
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from src.gates import asp7_gate
from src.gates.asp7_gate import (
    JournalSchemaError,
    THRESHOLD_J,
    THRESHOLD_N,
    main,
    run_gate,
)


# ── Helpers ────────────────────────────────────────────────────────────────


def _journal(
    *,
    game: str,
    deploy_at: str,
    tweaks: list[dict],
    deploy_commit: str = "deadbeef",
    shipped_at: str | None = None,
    notes: str | None = None,
) -> str:
    """Build a minimal feel journal markdown body."""
    fm = {
        "game": game,
        "deploy_commit": deploy_commit,
        "deploy_at": deploy_at,
        "tweaks": tweaks,
    }
    if shipped_at is not None:
        fm["shipped_at"] = shipped_at
    if notes is not None:
        fm["notes"] = notes

    import yaml  # local: only used in test fixtures

    return f"---\n{yaml.safe_dump(fm, sort_keys=False)}---\n\n# Body\n"


def _write_journal(dir_: Path, game: str, content: str) -> Path:
    p = dir_ / f"{game}_feel_journal.md"
    p.write_text(content, encoding="utf-8")
    return p


def _t(hours_after: float, base: str = "2026-04-25T00:00:00Z") -> str:
    """ISO timestamp `hours_after` hours after `base`."""
    base_dt = datetime.fromisoformat(base.replace("Z", "+00:00"))
    return (base_dt + timedelta(hours=hours_after)).isoformat().replace("+00:00", "Z")


# ── Test fixtures: passing / failing journals ──────────────────────────────


@pytest.fixture
def lessons_dir(tmp_path):
    d = tmp_path / "lessons"
    d.mkdir()
    return d


def _passing_journal(game: str, n_in_window: int = 1) -> str:
    """A journal with `n_in_window` tweaks at hours 1..n inside the window."""
    tweaks = [
        {"when": _t(i + 1), "what": f"tweak {i}", "category": "control-feel"}
        for i in range(n_in_window)
    ]
    return _journal(game=game, deploy_at=_t(0), tweaks=tweaks)


def _failing_journal(game: str) -> str:
    """A journal with J+1 tweaks all in window — fails."""
    tweaks = [
        {"when": _t(i + 1), "what": f"tweak {i}", "category": "physics-constant"}
        for i in range(THRESHOLD_J + 1)
    ]
    return _journal(game=game, deploy_at=_t(0), tweaks=tweaks)


# ── Tests ──────────────────────────────────────────────────────────────────


def test_three_games_pass_exits_0(lessons_dir, capsys):
    """AC-4(a): 3 games clearing the bar -> exit 0."""
    for g in ("breakout", "flappy_bird", "pong"):
        _write_journal(lessons_dir, g, _passing_journal(g, n_in_window=2))

    rc = main(["--lessons-dir", str(lessons_dir)])
    assert rc == 0
    out = capsys.readouterr().out
    assert "ASP-7 PASSING" in out
    assert "breakout: PASS" in out
    assert "flappy_bird: PASS" in out
    assert "pong: PASS" in out


def test_two_games_pass_exits_1(lessons_dir, capsys):
    """AC-4(b): 2 games clearing -> exit 1 in enforce mode."""
    _write_journal(lessons_dir, "breakout", _passing_journal("breakout"))
    _write_journal(lessons_dir, "flappy_bird", _passing_journal("flappy_bird"))

    rc = main(["--lessons-dir", str(lessons_dir)])
    assert rc == 1
    assert "ASP-7 not yet passing" in capsys.readouterr().out


def test_check_mode_always_exits_0(lessons_dir, capsys):
    """AC-4(f): --check exits 0 regardless of pass count."""
    # Even with zero journals, --check should exit 0.
    rc = main(["--lessons-dir", str(lessons_dir), "--check"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "CHECK" in out

    # And with only 1 game passing, --check still exits 0.
    _write_journal(lessons_dir, "breakout", _passing_journal("breakout"))
    rc = main(["--lessons-dir", str(lessons_dir), "--check"])
    assert rc == 0


def test_malformed_frontmatter_exits_2(lessons_dir, capsys):
    """AC-4(c): missing required field -> exit 2 with clear error."""
    bad = "---\ngame: broken\ndeploy_commit: abc\n# missing deploy_at and tweaks\n---\n"
    _write_journal(lessons_dir, "broken", bad)
    rc = main(["--lessons-dir", str(lessons_dir)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "missing required keys" in err
    assert "deploy_at" in err


def test_no_frontmatter_at_all_exits_2(lessons_dir, capsys):
    """A file without YAML frontmatter is a schema error, not a 0/1 result."""
    _write_journal(lessons_dir, "no_frontmatter", "just markdown body, no frontmatter\n")
    rc = main(["--lessons-dir", str(lessons_dir)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "missing YAML frontmatter" in err


def test_invalid_category_exits_2(lessons_dir, capsys):
    """Tweak category outside the allowed set is a schema error."""
    bad = _journal(
        game="bad_cat",
        deploy_at=_t(0),
        tweaks=[{"when": _t(1), "what": "x", "category": "made-up-category"}],
    )
    _write_journal(lessons_dir, "bad_cat", bad)
    rc = main(["--lessons-dir", str(lessons_dir)])
    assert rc == 2
    err = capsys.readouterr().err
    assert "category" in err
    assert "made-up-category" in err


def test_tweak_outside_72h_excluded(lessons_dir):
    """AC-4(d): a tweak after deploy_at + 72h is NOT counted in in_window_count."""
    tweaks = [
        {"when": _t(1), "what": "in-window", "category": "control-feel"},
        {"when": _t(75), "what": "out-of-window", "category": "control-feel"},
    ]
    _write_journal(
        lessons_dir,
        "windowed",
        _journal(game="windowed", deploy_at=_t(0), tweaks=tweaks),
    )

    result = run_gate(lessons_dir=lessons_dir)
    assert len(result.games) == 1
    g = result.games[0]
    assert g.tweak_count == 2
    assert g.in_window_count == 1
    assert g.passed is True


def test_empty_tweaks_counts_as_zero(lessons_dir):
    """AC-4(e): tweaks: [] -> in_window_count=0 -> passed."""
    _write_journal(
        lessons_dir,
        "clean",
        _journal(game="clean", deploy_at=_t(0), tweaks=[]),
    )
    result = run_gate(lessons_dir=lessons_dir)
    assert result.games[0].in_window_count == 0
    assert result.games[0].passed is True


def test_template_excluded_from_discovery(lessons_dir):
    """The canonical template lives next to journals but must not be evaluated."""
    template = lessons_dir / "_feel_journal_template.md"
    template.write_text("---\ngame: example\n---\n", encoding="utf-8")  # malformed on purpose
    # If discovery picked it up, this would raise.
    result = run_gate(lessons_dir=lessons_dir)
    assert result.games == []


def test_exactly_J_tweaks_is_passing(lessons_dir):
    """The bar is <= J, not < J."""
    tweaks = [
        {"when": _t(i + 1), "what": f"t{i}", "category": "physics-constant"}
        for i in range(THRESHOLD_J)
    ]
    _write_journal(
        lessons_dir,
        "right_at_bar",
        _journal(game="right_at_bar", deploy_at=_t(0), tweaks=tweaks),
    )
    result = run_gate(lessons_dir=lessons_dir)
    assert result.games[0].in_window_count == THRESHOLD_J
    assert result.games[0].passed is True


def test_J_plus_one_tweaks_fails(lessons_dir):
    """One over the bar fails."""
    _write_journal(lessons_dir, "over_bar", _failing_journal("over_bar"))
    result = run_gate(lessons_dir=lessons_dir)
    assert result.games[0].in_window_count == THRESHOLD_J + 1
    assert result.games[0].passed is False


def test_run_gate_returns_thresholds(lessons_dir):
    """The structured result exposes thresholds for downstream tools."""
    result = run_gate(lessons_dir=lessons_dir)
    assert result.threshold_J == THRESHOLD_J
    assert result.threshold_N == THRESHOLD_N
    assert result.window_hours == 72


def test_json_emit(lessons_dir, tmp_path, capsys):
    """--json writes a structured status file matching the GateResult shape."""
    _write_journal(lessons_dir, "g1", _passing_journal("g1", n_in_window=2))
    out_path = tmp_path / "status.json"
    rc = main(["--lessons-dir", str(lessons_dir), "--check", "--json", str(out_path)])
    assert rc == 0
    data = json.loads(out_path.read_text(encoding="utf-8"))
    assert data["threshold_J"] == THRESHOLD_J
    assert data["threshold_N"] == THRESHOLD_N
    assert data["total_passed"] == 1
    assert data["asp7_passed"] is False  # 1 < N=3
    assert data["games"][0]["game"] == "g1"
    assert data["games"][0]["passed"] is True


def test_iso_without_timezone_rejected(lessons_dir):
    """Missing TZ in ISO date is a schema error (we want explicit UTC)."""
    bad = textwrap.dedent(
        """\
        ---
        game: notz
        deploy_commit: abc
        deploy_at: "2026-04-25T00:00:00"
        tweaks: []
        ---
        """
    )
    _write_journal(lessons_dir, "notz", bad)
    with pytest.raises(JournalSchemaError) as exc:
        run_gate(lessons_dir=lessons_dir)
    assert "missing timezone" in str(exc.value)


def test_real_template_parses_cleanly():
    """The shipped template at data/lessons/_feel_journal_template.md must parse
    via the gate's own validator (template is the source of truth for schema)."""
    template_path = asp7_gate.LESSONS_DIR / asp7_gate.TEMPLATE_NAME
    if not template_path.exists():
        pytest.skip("template not present in this checkout")
    data = asp7_gate._parse_frontmatter(template_path)
    asp7_gate._validate_journal(data, template_path)


def test_main_writes_default_status_when_flag_set(lessons_dir, monkeypatch, tmp_path):
    """--write-status drops a JSON next to dashboard data."""
    status_path = tmp_path / "asp7_status.json"
    monkeypatch.setattr(asp7_gate, "DEFAULT_STATUS_PATH", status_path)
    _write_journal(lessons_dir, "g1", _passing_journal("g1"))
    rc = main(["--lessons-dir", str(lessons_dir), "--check", "--write-status"])
    assert rc == 0
    assert status_path.exists()
    data = json.loads(status_path.read_text())
    assert "games" in data and len(data["games"]) == 1

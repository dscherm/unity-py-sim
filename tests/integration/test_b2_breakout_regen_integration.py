"""B2 — End-to-end pipeline regression for the `_score_text`/`scoreText`
casing bug.

Runs the actual `python -m src.pipeline --game breakout` against the
real `examples/breakout/breakout_python/` source and asserts that the
regenerated `GameManager.cs` is internally consistent: every
underscore-prefixed Python field (`_score_text`, `_lives_text`,
`_status_text`) declares and accesses the same camelCase symbol.

The bug being guarded: declarations used `scoreText` (lstrip of `_`),
but `inst._score_text` access translated to `inst.ScoreText`
(PascalCase from `'' + 'Score' + 'Text'`). That produced CS1061 in
Unity's compiler.

Uses tmp_path so we never touch `data/generated/`.

Derived from the pipeline contract (CLI, exit code, output layout) —
NOT from reading any existing integration test.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BREAKOUT_SRC = REPO_ROOT / "examples" / "breakout" / "breakout_python"


pytestmark = pytest.mark.skipif(
    not BREAKOUT_SRC.is_dir(),
    reason="examples/breakout/breakout_python missing — fixture unavailable",
)


def _run_pipeline(out_dir: Path) -> subprocess.CompletedProcess:
    """Invoke the pipeline CLI exactly as a user would.

    The pipeline's contract is: given `--game breakout` and `--output X`,
    drop `Assets/_Project/Scripts/*.cs` under X using the corresponding
    `examples/breakout/breakout_python/` source tree.
    """
    cmd = [
        sys.executable,
        "-m",
        "src.pipeline",
        "--game",
        "breakout",
        "--output",
        str(out_dir),
    ]
    return subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        check=False,
    )


@pytest.fixture(scope="module")
def regenerated_breakout(tmp_path_factory) -> Path:
    """Run the pipeline once per test module."""
    out = tmp_path_factory.mktemp("b2_breakout_regen")
    proc = _run_pipeline(out)
    if proc.returncode != 0:
        pytest.fail(
            f"pipeline exited {proc.returncode}\n"
            f"STDOUT:\n{proc.stdout}\n"
            f"STDERR:\n{proc.stderr}\n"
        )
    scripts_dir = out / "Assets" / "_Project" / "Scripts"
    assert scripts_dir.is_dir(), f"missing scripts dir: {scripts_dir}"
    return scripts_dir


def _read_game_manager(scripts_dir: Path) -> str:
    gm = scripts_dir / "GameManager.cs"
    assert gm.is_file(), f"missing GameManager.cs in {scripts_dir}"
    return gm.read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "field_camel",
    ["scoreText", "livesText", "statusText"],
)
def test_underscore_field_declared_in_camel_case(regenerated_breakout, field_camel):
    """The Python `_score_text: Text = ...` field must surface in C#
    as a `scoreText` declaration — not `ScoreText` and not `_scoreText`.

    This is the field-declaration half of the consistency contract.
    """
    src = _read_game_manager(regenerated_breakout)

    # A real declaration line will look something like:
    #   `private Text scoreText;`
    #   `[SerializeField] private Text scoreText;`
    # Reject the PascalCase form anywhere on a `Text` declaration line.
    pascal = field_camel[0].upper() + field_camel[1:]

    # Must declare the camelCase form somewhere with a Text type.
    assert f"Text {field_camel}" in src, (
        f"GameManager.cs missing camelCase declaration `Text {field_camel}`. "
        f"Source excerpt:\n{src[:1500]}"
    )

    # Must NOT declare the PascalCase form on the same Text type
    # (that would be the bug's other half: PascalCase declaration).
    assert f"Text {pascal}" not in src, (
        f"GameManager.cs declared `Text {pascal}` — should be camelCase "
        f"`Text {field_camel}`."
    )


@pytest.mark.parametrize(
    "field_camel",
    ["scoreText", "livesText", "statusText"],
)
def test_underscore_field_access_uses_same_camel_case(regenerated_breakout, field_camel):
    """`inst._score_text.text = ...` from Python must translate to
    `inst.scoreText.text = ...` in C# — matching the declaration.

    This is the cross-instance attribute-access half of the consistency
    contract — it is the half that broke in the b72d967 regression
    because `snake_to_camel` returned `ScoreText` (PascalCase).
    """
    src = _read_game_manager(regenerated_breakout)
    pascal = field_camel[0].upper() + field_camel[1:]

    # The PascalCase access form is the smoking gun for the bug.
    assert f"inst.{pascal}" not in src, (
        f"GameManager.cs accesses `inst.{pascal}` (PascalCase) — "
        f"declaration is camelCase `{field_camel}`, so this is a CS1061 "
        f"in Unity. Source excerpt around it:\n"
        + _excerpt_around(src, f"inst.{pascal}")
    )

    # And the camelCase form should appear at least once (proving the
    # access path actually emits the field — not just that it skipped it).
    assert f"inst.{field_camel}" in src, (
        f"GameManager.cs never accesses `inst.{field_camel}` — the "
        f"`_update_display` body looks like it was dropped or rewritten. "
        f"Source excerpt:\n{src[:2000]}"
    )


def test_no_pascalcase_underscore_field_leaks_anywhere(regenerated_breakout):
    """Belt-and-suspenders sweep: across the whole regenerated project,
    no other `.cs` file should reference the buggy PascalCase forms
    either. (Other Breakout files don't reach into `_score_text`,
    but if they ever do, this catches the same regression.)"""
    forbidden = ["ScoreText", "LivesText", "StatusText"]

    # Filter: GameObject names like new GameObject("ScoreText") are
    # legitimate string literals — we only flag dotted access.
    for cs_path in regenerated_breakout.glob("*.cs"):
        text = cs_path.read_text(encoding="utf-8")
        for sym in forbidden:
            dotted = f".{sym}"
            assert dotted not in text, (
                f"{cs_path.name} contains forbidden PascalCase access "
                f"`{dotted}` — would be CS1061 against camelCase "
                f"declaration. Excerpt:\n"
                + _excerpt_around(text, dotted)
            )


def _excerpt_around(src: str, needle: str, ctx: int = 200) -> str:
    """Pull a small window around the first occurrence of `needle`."""
    i = src.find(needle)
    if i < 0:
        return "(not found)"
    start = max(0, i - ctx)
    end = min(len(src), i + len(needle) + ctx)
    return src[start:end]

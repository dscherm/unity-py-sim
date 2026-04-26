"""End-to-end integration test for the M-1 Breakout deploy fixes.

Drives `tools/gen_coplay.py` as a subprocess against the breakout example
and asserts the generated GeneratedSceneSetup.cs contains the fingerprints
of all three Gap B4/B5/B6 fixes.

This test does NOT require Unity to be installed — it parses the generated
C# string only.
"""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
RUNNER = REPO_ROOT / "examples" / "breakout" / "run_breakout.py"
MAPPING = REPO_ROOT / "data" / "mappings" / "breakout_mapping.json"


def _python() -> str:
    """Use the same Python that's running pytest."""
    return sys.executable


def _run_gen_coplay(out_path: Path) -> str:
    """Invoke tools/gen_coplay.py and return the generated C# string."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    cmd = [
        _python(),
        "-m",
        "tools.gen_coplay",
        "--runner",
        str(RUNNER),
        "--mapping",
        str(MAPPING),
        "--output",
        str(out_path),
        "--namespace",
        "Breakout",
    ]
    env = dict(os.environ)
    # Suppress any pygame/display init in headless test environment
    env.setdefault("SDL_VIDEODRIVER", "dummy")
    env["PYTHONPATH"] = str(REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    result = subprocess.run(
        cmd,
        cwd=str(REPO_ROOT),
        capture_output=True,
        text=True,
        env=env,
        timeout=180,
    )
    assert result.returncode == 0, (
        f"gen_coplay failed:\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
    )
    return out_path.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def generated_breakout_cs(tmp_path_factory) -> str:
    """Generate the breakout scene script once per module."""
    tmp = tmp_path_factory.mktemp("m1_breakout_regen")
    return _run_gen_coplay(tmp / "GeneratedSceneSetup.cs")


def test_regen_succeeds_and_produces_nonempty_cs(generated_breakout_cs: str):
    assert len(generated_breakout_cs) > 500, (
        "Generated scene setup C# is suspiciously short."
    )
    assert "public class GeneratedSceneSetup" in generated_breakout_cs


def test_regen_contains_b5_sprite_fallback(generated_breakout_cs: str):
    """Gap B5: the breakout mapping declares sprite_name for paddle/ball/brick;
    each must get the `?? AssetDatabase.LoadAssetAtPath<Sprite>` fallback."""
    cs = generated_breakout_cs
    for sprite_name, unity_path in [
        ("paddle_0", "Assets/Art/Sprites/paddle.png"),
        ("ball_0", "Assets/Art/Sprites/ball.png"),
        ("brick_0", "Assets/Art/Sprites/brick.png"),
    ]:
        assert f".OfType<Sprite>().FirstOrDefault(s => s.name == \"{sprite_name}\")" in cs, (
            f"Gap B5 regression: missing FirstOrDefault for {sprite_name}"
        )
        assert f"?? AssetDatabase.LoadAssetAtPath<Sprite>(\"{unity_path}\");" in cs, (
            f"Gap B5 regression: missing fallback for {unity_path}"
        )


def test_regen_uses_art_sprites_paths_only(generated_breakout_cs: str):
    """Gap B4: no `Assets/Sprites/` (legacy) path strings should remain."""
    cs = generated_breakout_cs
    # Allow Assets/_Project/... (project files), but no Assets/Sprites/
    bad = "\"Assets/Sprites/"
    assert bad not in cs, (
        f"Gap B4 regression: legacy 'Assets/Sprites/' path leaked into output.\n"
        f"First match context: {cs[max(0, cs.find(bad)-50):cs.find(bad)+80]}"
    )
    # Positive: Art/Sprites IS present
    assert "Assets/Art/Sprites/" in cs


def test_regen_b6_int_fields_use_intValue(generated_breakout_cs: str):
    """Gap B6: at least one int-typed serialized field must use .intValue.

    The Brick MonoBehaviour exposes `points` and `health` as int. Both are
    int-typed in the breakout python source, so the generator should emit
    `.intValue = <N>;` (no f suffix). Conversely, ball/paddle speed-like
    fields are float so they keep `.floatValue = <N>f;`.
    """
    cs = generated_breakout_cs
    # Find every prop_*.intValue or prop_*.floatValue line
    int_lines = [ln for ln in cs.splitlines() if ".intValue =" in ln]
    float_lines = [ln for ln in cs.splitlines() if ".floatValue =" in ln]

    # Must have at least one of each (Brick has int fields, ball/paddle have float)
    assert int_lines, (
        "Gap B6 regression: NO .intValue assignments emitted — every numeric "
        "field is being treated as float. Generated lines containing 'Value =':\n"
        + "\n".join(ln for ln in cs.splitlines() if "Value =" in ln)
    )
    # Sanity check: at least one float assignment too (otherwise dispatcher is one-sided broken)
    assert float_lines, (
        "Suspicious: no .floatValue assignments — verify breakout has float fields."
    )

    # No int assignment should carry an 'f' suffix
    for ln in int_lines:
        # Strip trailing semicolon/whitespace for the check
        # Format: `... prop_X.intValue = <literal>;`
        stripped = ln.rstrip(";").rstrip()
        # The literal should not end in 'f'
        assert not stripped.endswith("f"), (
            f"Gap B6 regression: int field has 'f' suffix: {ln!r}"
        )


def test_regen_b6_specific_brick_int_fields(generated_breakout_cs: str):
    """Stronger assertion when the breakout scene exposes Brick.points/health.

    If these fields aren't present in the serialized scene (older breakout
    layout), the test xfails informatively rather than masking a real bug.
    """
    cs = generated_breakout_cs
    has_points = "prop_points." in cs
    has_health = "prop_health." in cs
    if not (has_points or has_health):
        pytest.skip(
            "Breakout scene didn't serialize Brick.points or Brick.health — "
            "scene shape may have changed. Other B6 assertions still cover the dispatcher."
        )
    if has_points:
        assert "prop_points.intValue =" in cs, (
            "Brick.points should be int-typed -> .intValue. Found: "
            + next((ln for ln in cs.splitlines() if "prop_points." in ln), "<none>")
        )
    if has_health:
        assert "prop_health.intValue =" in cs, (
            "Brick.health should be int-typed -> .intValue. Found: "
            + next((ln for ln in cs.splitlines() if "prop_health." in ln), "<none>")
        )

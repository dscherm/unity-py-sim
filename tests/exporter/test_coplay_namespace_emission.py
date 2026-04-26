"""Contract: when the translator wraps generated MonoBehaviours in a
namespace, the CoPlay scene-setup and validation scripts MUST declare
`using <Namespace>;` so bare type references in `GetComponent<T>()`
and `AddComponent<T>()` calls resolve.

Without this directive, `dotnet build` (and therefore the home-machine
deploy step) fails with CS0246: "type or namespace name 'T' could
not be found." This was the root cause of the failed home_machine
deploy of Flappy Bird on 2026-04-26: every `GeneratedSceneSetup`
reference to `Player` / `Pipes` / `Spawner` / `Parallax` / `GameManager`
could not bind because the translator-emitted `namespace FlappyBird
{ ... }` wrapper was not joined by a corresponding `using FlappyBird;`
in the editor script.

The fix has two surfaces:
  1. `coplay_generator.generate_scene_script` already emits `using {ns};`
     when called with an explicit namespace argument — we lock that in.
  2. The driver scripts (`tools/gen_flappy_coplay.py`, `tools/gen_coplay.py`)
     must default the namespace to the per-game value the translator
     uses, so a no-flag regen produces a script that compiles.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


def _run_flappy_gen(tmp_path: Path, namespace: str | None = None) -> tuple[str, str]:
    out_cs = tmp_path / "GeneratedSceneSetup.cs"
    out_val = tmp_path / "GeneratedSceneValidation.cs"
    cmd = [
        sys.executable,
        str(REPO_ROOT / "tools" / "gen_flappy_coplay.py"),
        "--output", str(out_cs),
        "--validation-output", str(out_val),
    ]
    if namespace is not None:
        cmd += ["--namespace", namespace]
    proc = subprocess.run(
        cmd, cwd=REPO_ROOT, capture_output=True, text=True, check=False,
    )
    assert proc.returncode == 0, (
        f"generator failed (returncode={proc.returncode}):\n"
        f"stdout:\n{proc.stdout}\nstderr:\n{proc.stderr}"
    )
    return (
        out_cs.read_text(encoding="utf-8"),
        out_val.read_text(encoding="utf-8"),
    )


class TestExplicitNamespaceEmission:
    """When --namespace is provided, both scripts MUST declare it."""

    def test_setup_declares_using_when_explicit_namespace_passed(self, tmp_path):
        setup_cs, _ = _run_flappy_gen(tmp_path, namespace="FlappyBird")
        assert "using FlappyBird;" in setup_cs, (
            "GeneratedSceneSetup.cs must include `using FlappyBird;` "
            "to resolve bare class refs against the translator's "
            "namespace FlappyBird wrapper."
        )

    def test_validation_declares_using_when_explicit_namespace_passed(self, tmp_path):
        _, val_cs = _run_flappy_gen(tmp_path, namespace="FlappyBird")
        assert "using FlappyBird;" in val_cs, (
            "GeneratedSceneValidation.cs must include `using FlappyBird;`"
            " — without it, the validator's GetComponent<T>() calls hit "
            "CS0246 the same way the setup script does."
        )


class TestDefaultNamespaceAutoDerivation:
    """Without an explicit --namespace flag, the generator must still
    emit the right `using` directive — the translator already wraps
    Flappy Bird classes in `namespace FlappyBird`, so the default
    invocation must match that wrapper. A pipeline regen with no
    namespace flag (the documented happy path) produced a non-
    compiling editor script before this fix landed.
    """

    def test_setup_emits_using_for_default_invocation(self, tmp_path):
        setup_cs, _ = _run_flappy_gen(tmp_path, namespace=None)
        assert "using FlappyBird;" in setup_cs

    def test_validation_emits_using_for_default_invocation(self, tmp_path):
        _, val_cs = _run_flappy_gen(tmp_path, namespace=None)
        assert "using FlappyBird;" in val_cs

    def test_setup_uses_namespace_qualified_components(self, tmp_path):
        """Component refs in the default invocation must be qualified
        with the auto-derived namespace, matching the translator's
        wrapper. We assert at least one of the Flappy Bird-specific
        MonoBehaviour types appears with the prefix — covers both
        `GetComponent<FlappyBird.X>()` and the SerializedObject
        cross-reference pattern.
        """
        setup_cs, _ = _run_flappy_gen(tmp_path, namespace=None)
        assert any(
            f"FlappyBird.{cls}" in setup_cs
            for cls in ("Player", "Pipes", "Spawner", "Parallax", "GameManager")
        ), (
            "Default-invocation setup script must qualify at least one "
            "MonoBehaviour ref with the FlappyBird namespace prefix."
        )

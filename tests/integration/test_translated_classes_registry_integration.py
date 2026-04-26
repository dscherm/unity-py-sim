"""Integration: translated_classes registry end-to-end (gap 4 follow-up).

Covers the bridge-mode follow-up ``Wire translated_classes registry into
tools/gen_flappy_coplay.py and project_translator`` — originally recorded
in ``.ralph/bridge-state.json`` for pipeline
``coplay-gaps-upstream-2026-04-22``.

The shared helper ``src.translator.project_translator.get_translated_class_names``
must mirror the filter semantics the scene serializer already enforces
(components whose class is absent from the set are dropped) and both
scene generators (``tools/gen_flappy_coplay.py``, ``tools/gen_coplay.py``)
must wire the helper result into ``serialize_scene(translated_classes=...)``.
"""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest


# --------------------------------------------------------------------------
# Helper: shared class-name scanner
# --------------------------------------------------------------------------


def _write_pkg(tmp_path: Path, files: dict[str, str]) -> Path:
    pkg = tmp_path / "fake_pkg"
    pkg.mkdir()
    for name, body in files.items():
        (pkg / name).write_text(textwrap.dedent(body), encoding="utf-8")
    return pkg


def test_helper_returns_monobehaviour_classes_only(tmp_path: Path) -> None:
    from src.translator.project_translator import get_translated_class_names

    pkg = _write_pkg(tmp_path, {
        "player.py": """
            from src.engine.core import MonoBehaviour

            class Player(MonoBehaviour):
                pass
        """,
        "config.py": """
            class GameConfig:
                speed = 5.0
        """,
        "__init__.py": "",
    })

    names = get_translated_class_names(pkg)

    assert names == {"Player"}, (
        "Expected only the MonoBehaviour subclass; plain-Python classes "
        "and __init__.py must be excluded."
    )


def test_helper_handles_missing_directory(tmp_path: Path) -> None:
    from src.translator.project_translator import get_translated_class_names

    assert get_translated_class_names(tmp_path / "does_not_exist") == set()


def test_helper_returns_empty_for_package_with_no_py_files(tmp_path: Path) -> None:
    from src.translator.project_translator import get_translated_class_names

    empty_pkg = tmp_path / "empty_pkg"
    empty_pkg.mkdir()

    assert get_translated_class_names(empty_pkg) == set()


def test_helper_excludes_dunder_init(tmp_path: Path) -> None:
    from src.translator.project_translator import get_translated_class_names

    pkg = _write_pkg(tmp_path, {
        "__init__.py": """
            from src.engine.core import MonoBehaviour

            class LeakedHandler(MonoBehaviour):
                pass
        """,
        "ball.py": """
            from src.engine.core import MonoBehaviour

            class Ball(MonoBehaviour):
                pass
        """,
    })

    names = get_translated_class_names(pkg)

    assert "Ball" in names
    assert "LeakedHandler" not in names, (
        "__init__.py MonoBehaviours must not leak into the registry — the "
        "translator does not emit a .cs file for them."
    )


# --------------------------------------------------------------------------
# Integration: serializer filter applied end-to-end against a live engine
# --------------------------------------------------------------------------


def test_serializer_drops_component_absent_from_registry() -> None:
    """End-to-end: a MonoBehaviour whose class name is not in the registry
    must be dropped from the serialized scene even when it exists as a
    live Python component on a GameObject — this is exactly the Flappy
    Bird ``PlayButtonHandler`` / ``QuitHandler`` gap 4 case."""

    from src.engine.core import GameObject, MonoBehaviour, _clear_registry
    from src.exporter.scene_serializer import serialize_scene

    _clear_registry()

    class TranslatedPlayer(MonoBehaviour):
        pass

    class InlineOnlyHandler(MonoBehaviour):
        pass

    try:
        player_go = GameObject("Player")
        player_go.add_component(TranslatedPlayer)

        handler_go = GameObject("Handler")
        handler_go.add_component(InlineOnlyHandler)

        scene = serialize_scene(translated_classes={"TranslatedPlayer"})
    finally:
        _clear_registry()

    go_map = {go["name"]: go for go in scene["game_objects"]}
    assert "Player" in go_map
    assert "Handler" in go_map, (
        "GameObjects are never dropped by the filter — only their "
        "unregistered MonoBehaviour components should be."
    )

    player_mb_classes = {
        c.get("class_name") or c.get("type")
        for c in go_map["Player"].get("components", [])
    }
    handler_mb_classes = {
        c.get("class_name") or c.get("type")
        for c in go_map["Handler"].get("components", [])
    }

    assert "TranslatedPlayer" in player_mb_classes
    assert "InlineOnlyHandler" not in handler_mb_classes, (
        "Component whose class is absent from translated_classes must be "
        "dropped — see coplay_generator_gaps.md gap 4."
    )


def test_serializer_retains_all_components_when_registry_is_none() -> None:
    """Back-compat: no registry argument → no filtering. Passing ``None``
    must preserve the pre-gap-4 behaviour (no silent regressions for
    callers that haven't opted in)."""

    from src.engine.core import GameObject, MonoBehaviour, _clear_registry
    from src.exporter.scene_serializer import serialize_scene

    _clear_registry()

    class UnlistedHandler(MonoBehaviour):
        pass

    try:
        go = GameObject("Obj")
        go.add_component(UnlistedHandler)
        scene = serialize_scene()  # no translated_classes
    finally:
        _clear_registry()

    (obj,) = [g for g in scene["game_objects"] if g["name"] == "Obj"]
    classes = {c.get("class_name") or c.get("type") for c in obj.get("components", [])}

    assert "UnlistedHandler" in classes, (
        "Without translated_classes the serializer must emit every "
        "MonoBehaviour as-is."
    )


# --------------------------------------------------------------------------
# Integration: gen_coplay's runner-to-source-dir derivation
# --------------------------------------------------------------------------


def test_gen_coplay_derives_source_dir_from_runner_stem(tmp_path: Path) -> None:
    """``tools/gen_coplay.py`` must derive the Python package directory
    from the runner path when ``--source`` is omitted, mirroring the
    ``gen_flappy_coplay`` convention of ``examples/<game>/run_<game>.py``
    ↔ ``examples/<game>/<game>_python/``.  This is the linkage that lets
    existing call sites pick up the registry filter for free."""

    runner = tmp_path / "run_widget.py"
    runner.write_text("def setup_scene():\n    pass\n", encoding="utf-8")

    pkg = tmp_path / "widget_python"
    pkg.mkdir()
    (pkg / "widget.py").write_text(textwrap.dedent("""
        from src.engine.core import MonoBehaviour

        class Widget(MonoBehaviour):
            pass
    """), encoding="utf-8")

    # Replicate gen_coplay's derivation rule verbatim.
    stem = runner.stem
    derived = runner.parent / (
        stem[4:] + "_python" if stem.startswith("run_") else f"{stem}_python"
    )

    assert derived == pkg
    assert derived.is_dir()

    from src.translator.project_translator import get_translated_class_names
    assert get_translated_class_names(derived) == {"Widget"}


def test_gen_coplay_derivation_handles_runner_without_run_prefix(
    tmp_path: Path,
) -> None:
    """Runners that don't use the ``run_*.py`` naming convention fall back
    to ``<stem>_python``.  Covers fixtures like ``examples/foo/foo_main.py``."""

    runner = tmp_path / "demo_main.py"
    runner.write_text("def setup_scene():\n    pass\n", encoding="utf-8")

    pkg = tmp_path / "demo_main_python"
    pkg.mkdir()

    stem = runner.stem
    derived = runner.parent / (
        stem[4:] + "_python" if stem.startswith("run_") else f"{stem}_python"
    )

    assert derived == pkg
    assert derived.is_dir()


# --------------------------------------------------------------------------
# Regression: gen_flappy_coplay's wrapper still delegates to the shared helper
# --------------------------------------------------------------------------


def test_gen_flappy_coplay_wrapper_delegates_to_shared_helper() -> None:
    """``tools/gen_flappy_coplay.py`` kept a private ``_translated_class_names``
    wrapper for backwards-compat of any external callers / tests that
    reached into the script.  It must produce the same result as the
    shared helper — no divergence allowed."""

    flappy_pkg = Path("examples/flappy_bird/flappy_bird_python")
    if not flappy_pkg.is_dir():
        pytest.skip("flappy_bird fixture not present")

    from src.translator.project_translator import get_translated_class_names

    # Import the tool as a module to exercise the wrapper directly.
    import importlib.util
    import sys

    script = Path("tools/gen_flappy_coplay.py")
    spec = importlib.util.spec_from_file_location(
        "gen_flappy_coplay_under_test", script,
    )
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules["gen_flappy_coplay_under_test"] = mod
    spec.loader.exec_module(mod)

    wrapper_result = mod._translated_class_names(flappy_pkg)
    helper_result = get_translated_class_names(flappy_pkg)

    assert wrapper_result == helper_result
    assert "Player" in helper_result, (
        "Flappy Bird's translated package must include Player — if this "
        "ever trips the fixture itself has drifted."
    )

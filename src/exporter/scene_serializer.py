"""Capture a running Python scene into a portable JSON format.

Walks the scene graph and serializes all GameObjects, components, transforms,
and cross-object references into a JSON structure suitable for Unity reconstruction.

Usage:
    python -m src.exporter.scene_serializer <run_file.py> [--output path.json]
"""

from __future__ import annotations

import json
from typing import Any

from src.engine.core import _game_objects, GameObject, Component, MonoBehaviour
from src.engine.transform import Transform
from src.engine.rendering.renderer import SpriteRenderer
from src.engine.rendering.camera import Camera
from src.engine.audio import AudioSource, AudioListener
from src.engine.physics.rigidbody import Rigidbody2D, RigidbodyType2D
from src.engine.physics.collider import BoxCollider2D, CircleCollider2D
from src.engine.math.vector import Vector2, Vector3


def _vec2_to_list(v: Vector2) -> list[float]:
    return [v.x, v.y]


def _vec3_to_list(v: Vector3) -> list[float]:
    return [v.x, v.y, v.z]


def _serialize_component(comp: Component) -> dict[str, Any] | None:
    """Serialize a single component to a dict. Returns None for internal-only components."""
    if isinstance(comp, Transform):
        return {
            "type": "Transform",
            "position": _vec3_to_list(comp.position),
            "rotation": [comp.rotation.x, comp.rotation.y, comp.rotation.z, comp.rotation.w],
            "local_scale": _vec3_to_list(comp.local_scale),
            "parent": comp.parent.game_object.name if comp.parent else None,
        }

    if isinstance(comp, SpriteRenderer):
        return {
            "type": "SpriteRenderer",
            "color": list(comp.color),
            "size": _vec2_to_list(comp.size),
            "sorting_order": comp.sorting_order,
            "asset_ref": comp.asset_ref,
        }

    if isinstance(comp, Camera):
        return {
            "type": "Camera",
            "orthographic_size": comp.orthographic_size,
            "background_color": list(comp.background_color) if comp.background_color else None,
        }

    if isinstance(comp, AudioSource):
        return {
            "type": "AudioSource",
            "clip_ref": comp.clip_ref,
            "volume": comp.volume,
            "pitch": comp.pitch,
            "loop": comp.loop,
        }

    if isinstance(comp, AudioListener):
        return {"type": "AudioListener"}

    if isinstance(comp, Rigidbody2D):
        body_type = "Dynamic"
        if comp.body_type == RigidbodyType2D.STATIC:
            body_type = "Static"
        elif comp.body_type == RigidbodyType2D.KINEMATIC:
            body_type = "Kinematic"
        return {
            "type": "Rigidbody2D",
            "body_type": body_type,
            "mass": comp.mass,
            "gravity_scale": comp.gravity_scale,
        }

    if isinstance(comp, BoxCollider2D):
        result = {
            "type": "BoxCollider2D",
            "size": _vec2_to_list(comp.size),
            "is_trigger": comp.is_trigger,
        }
        if comp.shared_material:
            result["physics_material"] = {
                "bounciness": comp.shared_material.bounciness,
                "friction": comp.shared_material.friction,
            }
        return result

    if isinstance(comp, CircleCollider2D):
        result = {
            "type": "CircleCollider2D",
            "radius": comp.radius,
            "is_trigger": comp.is_trigger,
        }
        if comp.shared_material:
            result["physics_material"] = {
                "bounciness": comp.shared_material.bounciness,
                "friction": comp.shared_material.friction,
            }
        return result

    # MonoBehaviour subclasses — serialize type name and public fields
    if isinstance(comp, MonoBehaviour):
        data: dict[str, Any] = {
            "type": type(comp).__name__,
            "is_monobehaviour": True,
            "fields": {},
        }
        # Capture public fields that aren't private/internal
        for attr_name in dir(comp):
            if attr_name.startswith("_"):
                continue
            if callable(getattr(type(comp), attr_name, None)):
                continue
            try:
                val = getattr(comp, attr_name)
            except Exception:
                continue
            # Serialize based on type
            if isinstance(val, (int, float, str, bool)):
                data["fields"][attr_name] = val
            elif isinstance(val, Vector2):
                data["fields"][attr_name] = {"_type": "Vector2", "value": _vec2_to_list(val)}
            elif isinstance(val, Vector3):
                data["fields"][attr_name] = {"_type": "Vector3", "value": _vec3_to_list(val)}
            elif isinstance(val, GameObject):
                data["fields"][attr_name] = {"_type": "GameObjectRef", "name": val.name}
            elif val is None:
                data["fields"][attr_name] = None
        return data

    return None


def serialize_scene() -> dict[str, Any]:
    """Serialize the current scene state to a dict."""
    scene_data: dict[str, Any] = {
        "version": 1,
        "game_objects": [],
    }

    for go in _game_objects.values():
        go_data: dict[str, Any] = {
            "name": go.name,
            "tag": go.tag,
            "layer": go.layer,
            "active": go.active,
            "components": [],
        }

        for comp in go._components:
            comp_data = _serialize_component(comp)
            if comp_data is not None:
                go_data["components"].append(comp_data)

        scene_data["game_objects"].append(go_data)

    return scene_data


def _sanitize_for_json(obj: Any) -> Any:
    """Replace non-JSON values (inf, nan) with safe alternatives."""
    if isinstance(obj, float):
        if obj == float("inf"):
            return 999999.0
        if obj == float("-inf"):
            return -999999.0
        if obj != obj:  # NaN
            return 0.0
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, list):
        return [_sanitize_for_json(v) for v in obj]
    return obj


def serialize_scene_json(indent: int = 2) -> str:
    """Serialize to JSON string."""
    return json.dumps(_sanitize_for_json(serialize_scene()), indent=indent)


def serialize_from_setup(setup_func: callable) -> dict[str, Any]:
    """Run a setup function and serialize the resulting scene."""
    from src.engine.core import _clear_registry
    from src.engine.lifecycle import LifecycleManager
    from src.engine.physics.physics_manager import PhysicsManager

    _clear_registry()
    LifecycleManager._instance = None
    PhysicsManager._instance = None

    setup_func()
    scene_data = serialize_scene()

    _clear_registry()
    LifecycleManager._instance = None
    PhysicsManager._instance = None

    return scene_data


def main():
    """CLI entry point."""
    import sys
    import importlib.util
    import os
    from pathlib import Path

    args = sys.argv[1:]
    if not args:
        print("Usage: python -m src.exporter.scene_serializer <run_file.py> [--output path.json]")
        sys.exit(1)

    module_path = Path(args[0])
    output_path = None
    if "--output" in args:
        idx = args.index("--output")
        output_path = Path(args[idx + 1])

    sys.path.insert(0, os.getcwd())
    sys.path.insert(0, str(module_path.parent.resolve()))
    spec = importlib.util.spec_from_file_location("setup_module", str(module_path.resolve()))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    setup_func = None
    for name in ["setup_scene", "setup_level_1"]:
        if hasattr(module, name):
            setup_func = getattr(module, name)
            break

    if setup_func is None:
        print(f"ERROR: No setup function found in {module_path}")
        sys.exit(1)

    scene_data = serialize_from_setup(setup_func)

    go_count = len(scene_data["game_objects"])
    comp_count = sum(len(go["components"]) for go in scene_data["game_objects"])
    print(f"Serialized {go_count} GameObjects with {comp_count} components")

    json_str = json.dumps(_sanitize_for_json(scene_data), indent=2)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json_str, encoding="utf-8")
        print(f"Scene written to {output_path}")
    else:
        print(json_str)


if __name__ == "__main__":
    main()

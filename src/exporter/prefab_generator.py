"""Generate minimal Unity .prefab YAML stubs from prefab detection results.

Takes output from prefab_detector.detect_prefabs() and generates .prefab YAML
files that Unity can load. These are stubs — they define the GameObject hierarchy
and component slots, but sprites/materials are wired later via CoPlay MCP.

Each prefab gets a deterministic GUID derived from its class name (sha256),
ensuring regeneration produces stable references.

Usage:
    from src.exporter.prefab_generator import generate_prefab_files

    prefab_data = detect_prefabs("examples/breakout")
    files = generate_prefab_files(prefab_data)
    # files == {"Brick.prefab": "<yaml>", "Brick.prefab.meta": "<meta>", ...}
"""

from __future__ import annotations

import hashlib
from typing import Any


# Map Python component type names to Unity class IDs
# See: https://docs.unity3d.com/Manual/ClassIDReference.html
_UNITY_CLASS_IDS: dict[str, int] = {
    "Transform": 4,
    "SpriteRenderer": 212,
    "Rigidbody2D": 50,
    "BoxCollider2D": 61,
    "CircleCollider2D": 58,
    "PolygonCollider2D": 60,
    "EdgeCollider2D": 68,
    "AudioSource": 82,
    "Animator": 95,
    "Camera": 20,
}

# MonoBehaviour class ID in Unity
_MONOBEHAVIOUR_CLASS_ID = 114


def _deterministic_guid(name: str) -> str:
    """Generate a stable 32-hex-char GUID from a name via SHA-256."""
    return hashlib.sha256(name.encode("utf-8")).hexdigest()[:32]


def _deterministic_file_id(name: str, salt: str = "") -> int:
    """Generate a stable positive file ID from a name.

    Unity file IDs are signed 64-bit but typically small positive values.
    We use the lower 31 bits of a hash to stay safely positive.
    """
    h = hashlib.sha256(f"{name}:{salt}".encode("utf-8")).digest()
    return int.from_bytes(h[:4], "big") & 0x7FFFFFFF


def generate_prefab_yaml(class_name: str, components: list[str]) -> str:
    """Generate a minimal .prefab YAML for a single prefab.

    Args:
        class_name: The prefab name (e.g., "Brick").
        components: List of component type names (e.g., ["Rigidbody2D", "BoxCollider2D", "Brick"]).

    Returns:
        Unity YAML string for the .prefab file.
    """
    # Generate stable file IDs for each object in the prefab
    go_id = _deterministic_file_id(class_name, "GameObject")
    transform_id = _deterministic_file_id(class_name, "Transform")

    # Build component entries (Transform is always first)
    component_ids: list[tuple[int, int, str]] = []  # (file_id, class_id, name)
    component_ids.append((transform_id, 4, "Transform"))

    for comp_name in components:
        if comp_name == "Transform":
            continue
        comp_id = _deterministic_file_id(class_name, comp_name)
        class_id = _UNITY_CLASS_IDS.get(comp_name, _MONOBEHAVIOUR_CLASS_ID)
        component_ids.append((comp_id, class_id, comp_name))

    lines: list[str] = []
    lines.append("%YAML 1.1")
    lines.append("%TAG !u! tag:unity3d.com,2011:")

    # --- GameObject ---
    lines.append(f"--- !u!1 &{go_id}")
    lines.append("GameObject:")
    lines.append("  m_ObjectHideFlags: 0")
    lines.append("  serializedVersion: 6")
    lines.append("  m_Component:")
    for comp_id, class_id, _ in component_ids:
        lines.append(f"  - component: {{fileID: {comp_id}}}")
    lines.append("  m_Layer: 0")
    lines.append(f"  m_Name: {class_name}")
    lines.append("  m_TagString: Untagged")
    lines.append("  m_IsActive: 1")

    # --- Transform ---
    lines.append(f"--- !u!4 &{transform_id}")
    lines.append("Transform:")
    lines.append("  m_ObjectHideFlags: 0")
    lines.append("  m_PrefabInstance: {fileID: 0}")
    lines.append(f"  m_GameObject: {{fileID: {go_id}}}")
    lines.append("  m_LocalPosition: {x: 0, y: 0, z: 0}")
    lines.append("  m_LocalRotation: {x: 0, y: 0, z: 0, w: 1}")
    lines.append("  m_LocalScale: {x: 1, y: 1, z: 1}")
    lines.append("  m_Children: []")
    lines.append("  m_Father: {fileID: 0}")

    # --- Other components ---
    for comp_id, class_id, comp_name in component_ids:
        if comp_name == "Transform":
            continue

        lines.append(f"--- !u!{class_id} &{comp_id}")

        if class_id == _MONOBEHAVIOUR_CLASS_ID:
            # MonoBehaviour stub — wire the script reference via the same
            # deterministic GUID scheme the scaffolder uses when writing
            # `Assets/_Project/Scripts/<comp_name>.cs.meta` (see
            # project_scaffolder._write_cs_meta).  Both sides compute
            # `_deterministic_guid(f"script:{comp_name}")`, so Unity resolves
            # the binding on first import without hitting the random-GUID
            # drift that broke Flappy Bird Pipes instantiation
            # (flappy_bird_deploy.md gap 7).
            script_guid = _deterministic_guid(f"script:{comp_name}")
            lines.append("MonoBehaviour:")
            lines.append("  m_ObjectHideFlags: 0")
            lines.append(f"  m_GameObject: {{fileID: {go_id}}}")
            lines.append("  m_Enabled: 1")
            lines.append("  m_EditorHideFlags: 0")
            lines.append(f"  m_Script: {{fileID: 11500000, guid: {script_guid}, type: 3}}")
            lines.append(f"  m_Name: {comp_name}")
        elif comp_name == "SpriteRenderer":
            lines.append("SpriteRenderer:")
            lines.append("  m_ObjectHideFlags: 0")
            lines.append(f"  m_GameObject: {{fileID: {go_id}}}")
            lines.append("  m_Enabled: 1")
            lines.append("  m_Sprite: {fileID: 0}")
            lines.append("  m_Color: {r: 1, g: 1, b: 1, a: 1}")
        elif comp_name == "Rigidbody2D":
            lines.append("Rigidbody2D:")
            lines.append("  m_ObjectHideFlags: 0")
            lines.append(f"  m_GameObject: {{fileID: {go_id}}}")
            lines.append("  m_BodyType: 0")
            lines.append("  m_Mass: 1")
            lines.append("  m_LinearDrag: 0")
            lines.append("  m_AngularDrag: 0.05")
            lines.append("  m_GravityScale: 1")
        elif comp_name == "BoxCollider2D":
            lines.append("BoxCollider2D:")
            lines.append("  m_ObjectHideFlags: 0")
            lines.append(f"  m_GameObject: {{fileID: {go_id}}}")
            lines.append("  m_Enabled: 1")
            lines.append("  m_IsTrigger: 0")
            lines.append("  m_Size: {x: 1, y: 1}")
            lines.append("  m_Offset: {x: 0, y: 0}")
        elif comp_name == "CircleCollider2D":
            lines.append("CircleCollider2D:")
            lines.append("  m_ObjectHideFlags: 0")
            lines.append(f"  m_GameObject: {{fileID: {go_id}}}")
            lines.append("  m_Enabled: 1")
            lines.append("  m_IsTrigger: 0")
            lines.append("  m_Radius: 0.5")
            lines.append("  m_Offset: {x: 0, y: 0}")
        elif comp_name == "AudioSource":
            lines.append("AudioSource:")
            lines.append("  m_ObjectHideFlags: 0")
            lines.append(f"  m_GameObject: {{fileID: {go_id}}}")
            lines.append("  m_Enabled: 1")
            lines.append("  m_PlayOnAwake: 0")
            lines.append("  m_Volume: 1")
        else:
            # Generic built-in component stub
            lines.append(f"{comp_name}:")
            lines.append("  m_ObjectHideFlags: 0")
            lines.append(f"  m_GameObject: {{fileID: {go_id}}}")
            lines.append("  m_Enabled: 1")

    return "\n".join(lines) + "\n"


def generate_prefab_meta(class_name: str) -> str:
    """Generate a .prefab.meta file with a deterministic GUID.

    Args:
        class_name: The prefab name used to derive the GUID.

    Returns:
        Unity .meta file content.
    """
    guid = _deterministic_guid(f"prefab:{class_name}")
    return (
        f"fileFormatVersion: 2\n"
        f"guid: {guid}\n"
        f"PrefabImporter:\n"
        f"  externalObjects: {{}}\n"
        f"  userData:\n"
        f"  assetBundleName:\n"
        f"  assetBundleVariant:\n"
    )


def generate_prefab_files(
    prefab_data: dict[str, Any],
) -> dict[str, str]:
    """Generate .prefab and .prefab.meta files for all detected prefabs.

    Args:
        prefab_data: Output from prefab_detector.detect_prefabs().

    Returns:
        Dict of filename -> content (e.g., {"Brick.prefab": "...", "Brick.prefab.meta": "..."}).
    """
    files: dict[str, str] = {}

    for prefab in prefab_data.get("prefabs", []):
        class_name = prefab["class_name"]
        components = prefab.get("components", [])

        files[f"{class_name}.prefab"] = generate_prefab_yaml(class_name, components)
        files[f"{class_name}.prefab.meta"] = generate_prefab_meta(class_name)

    return files

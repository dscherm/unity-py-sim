"""Unity project scaffolder — creates a valid Unity project folder structure.

Takes translated C# files (from project_translator) and scaffolds them into
a standard Unity project layout with proper ProjectSettings, Packages/manifest.json,
and directory structure matching pacman_mapping.json conventions.

Usage:
    from src.exporter.project_scaffolder import scaffold_project

    scaffold_project(
        "breakout",
        Path("output/breakout_unity"),
        cs_files=translated,
        tags=["Player", "Enemy"],
    )
"""

from __future__ import annotations

import json
from pathlib import Path


# Files that should NOT be placed in the Scripts directory
_EXCLUDED_FILES = {"__init__.cs", "_required_packages.json"}

# Default Unity packages always included
_DEFAULT_PACKAGES: dict[str, str] = {
    "com.unity.render-pipelines.universal": "14.0.11",
    "com.unity.2d.sprite": "1.0.0",
    # Built-in modules required for Collider2D, Rigidbody2D, UI.Text, GameObject.Find
    "com.unity.modules.physics2d": "1.0.0",
    "com.unity.modules.audio": "1.0.0",
    "com.unity.modules.ui": "1.0.0",
    "com.unity.modules.uielements": "1.0.0",
    "com.unity.modules.imgui": "1.0.0",
}

# Well-known optional packages and their versions
_KNOWN_PACKAGE_VERSIONS: dict[str, str] = {
    "com.unity.inputsystem": "1.7.0",
    "com.unity.ugui": "1.0.0",
    "com.unity.render-pipelines.universal": "14.0.11",
    "com.unity.2d.sprite": "1.0.0",
    "com.unity.2d.tilemap": "1.0.0",
    "com.unity.2d.animation": "9.1.1",
    "com.unity.textmeshpro": "3.0.6",
}

# Standard Unity project directories to create
_PROJECT_DIRS = [
    "Assets/_Project/Scripts",
    "Assets/_Project/Prefabs",
    "Assets/_Project/Scenes",
    "Assets/Art/Sprites",
    "Assets/Editor",
    "Packages",
    "ProjectSettings",
]

_EDITOR_VERSION = "6000.4.0f1"


def scaffold_project(
    game_name: str,
    output_dir: Path,
    *,
    cs_files: dict[str, str],
    tags: list[str] | None = None,
    layers: dict[str, int] | None = None,
    required_packages: list[str] | None = None,
    physics: dict | None = None,
) -> Path:
    """Create a Unity project folder structure with translated C# files.

    Args:
        game_name: Name of the game (used in ProjectSettings).
        output_dir: Root directory for the Unity project.
        cs_files: Dict of filename -> C# source code (from translate_project).
        tags: Optional list of Unity tags to add to TagManager.asset.
        layers: Optional dict of layer_name -> layer_index (6+) for custom layers.
        required_packages: Optional list of additional Unity package names.
        physics: Optional dict with "gravity" ([x, y]) and "ignore_pairs"
            ([[layerA, layerB], ...]) for Physics2DSettings.asset generation.

    Returns:
        The output_dir Path.
    """
    output_dir = Path(output_dir)

    # 1. Create directory structure
    for rel_dir in _PROJECT_DIRS:
        (output_dir / rel_dir).mkdir(parents=True, exist_ok=True)

    # 2. Write C# files to Scripts directory
    scripts_dir = output_dir / "Assets" / "_Project" / "Scripts"
    for filename, content in cs_files.items():
        if filename in _EXCLUDED_FILES:
            continue
        if not filename.endswith(".cs"):
            continue
        (scripts_dir / filename).write_text(content, encoding="utf-8")

    # 3. Generate Packages/manifest.json
    _write_manifest(output_dir, cs_files, required_packages)

    # 4. Generate ProjectSettings files
    _write_project_version(output_dir)
    _write_project_settings(output_dir, game_name)

    # 5. Always generate TagManager.asset (with defaults if nothing provided)
    _write_tag_manager(output_dir, tags, layers)

    # 6. Generate Physics2DSettings.asset (always — defaults if no config)
    _write_physics_2d_settings(output_dir, physics)

    # 7. Generate minimal Scene.unity
    _write_scene(output_dir, game_name)

    return output_dir


def _write_manifest(
    output_dir: Path,
    cs_files: dict[str, str],
    required_packages: list[str] | None,
) -> None:
    """Write Packages/manifest.json with required Unity packages."""
    deps = dict(_DEFAULT_PACKAGES)

    # Add packages from _required_packages.json if present in cs_files
    pkg_json = cs_files.get("_required_packages.json")
    if pkg_json:
        try:
            pkg_list = json.loads(pkg_json)
            for pkg_info in pkg_list:
                pkg_name = pkg_info["package"]
                version = _KNOWN_PACKAGE_VERSIONS.get(pkg_name, "1.0.0")
                deps[pkg_name] = version
        except (json.JSONDecodeError, KeyError):
            pass

    # Add explicitly requested packages
    if required_packages:
        for pkg_name in required_packages:
            if pkg_name not in deps:
                version = _KNOWN_PACKAGE_VERSIONS.get(pkg_name, "1.0.0")
                deps[pkg_name] = version

    manifest = {"dependencies": deps}
    manifest_path = output_dir / "Packages" / "manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )


def _write_project_version(output_dir: Path) -> None:
    """Write ProjectSettings/ProjectVersion.txt."""
    pv_path = output_dir / "ProjectSettings" / "ProjectVersion.txt"
    pv_path.write_text(
        f"m_EditorVersion: {_EDITOR_VERSION}\n",
        encoding="utf-8",
    )


def _write_project_settings(output_dir: Path, game_name: str) -> None:
    """Write ProjectSettings/ProjectSettings.asset with game name."""
    ps_path = output_dir / "ProjectSettings" / "ProjectSettings.asset"
    ps_path.write_text(
        f"""%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!129 &1
PlayerSettings:
  productName: {game_name}
  companyName: DefaultCompany
  defaultScreenWidth: 1920
  defaultScreenHeight: 1080
""",
        encoding="utf-8",
    )


_DEFAULT_UNITY_TAGS = [
    "Untagged",
    "Respawn",
    "Finish",
    "EditorOnly",
    "MainCamera",
    "Player",
    "GameController",
]

# Builtin Unity layers — indices 0-7 are reserved by Unity
_BUILTIN_LAYERS: dict[int, str] = {
    0: "Default",
    1: "TransparentFX",
    2: "Ignore Raycast",
    # 3 is reserved (empty)
    4: "Water",
    5: "UI",
    # 6-7 reserved (empty)
}

# Total layer slots in Unity TagManager
_TOTAL_LAYER_SLOTS = 32


def _write_tag_manager(
    output_dir: Path,
    tags: list[str] | None,
    layers: dict[str, int] | None,
) -> None:
    """Write ProjectSettings/TagManager.asset with proper Unity YAML format.

    Always includes default Unity tags and builtin layers. Custom tags and
    layers are merged in.
    """
    # Build tags list: defaults + custom (deduped, preserving order)
    all_tags = list(_DEFAULT_UNITY_TAGS)
    if tags:
        for tag in tags:
            if tag not in all_tags:
                all_tags.append(tag)

    # Build layer array (32 slots)
    layer_array: list[str] = [""] * _TOTAL_LAYER_SLOTS
    for idx, name in _BUILTIN_LAYERS.items():
        layer_array[idx] = name
    if layers:
        for name, idx in layers.items():
            if 0 <= idx < _TOTAL_LAYER_SLOTS:
                layer_array[idx] = name

    lines: list[str] = []
    lines.append("%YAML 1.1")
    lines.append("%TAG !u! tag:unity3d.com,2011:")
    lines.append("--- !u!78 &1")
    lines.append("TagManager:")
    lines.append("  serializedVersion: 2")

    # Tags section
    lines.append("  tags:")
    for tag in all_tags:
        lines.append(f"  - {tag}")

    # Layers section (32 entries, empty ones as bare "  -")
    lines.append("  layers:")
    for name in layer_array:
        if name:
            lines.append(f"  - {name}")
        else:
            lines.append("  -")

    # Sorting layers section (Unity requires m_ prefix)
    lines.append("  m_SortingLayers:")
    lines.append("  - name: Default")
    lines.append("    uniqueID: 0")
    lines.append("    locked: 0")

    tm_path = output_dir / "ProjectSettings" / "TagManager.asset"
    tm_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Physics2DSettings
# ---------------------------------------------------------------------------

# Default Unity 2D gravity
_DEFAULT_GRAVITY = [0, -9.81]

# Number of physics layers in Unity
_NUM_LAYERS = 32

# All layers collide with all others by default
_ALL_COLLIDE = 0xFFFFFFFF


def _build_collision_matrix(
    ignore_pairs: list[list[str]],
    layers: dict[str, int] | None = None,
) -> list[int]:
    """Build a 32x32 layer collision matrix as a list of 32 bitmasks.

    Each entry ``matrix[i]`` is a 32-bit unsigned int where bit *j* indicates
    whether layer *i* collides with layer *j*.  By default every pair collides
    (all bits set).  For each pair in *ignore_pairs* the corresponding bits are
    cleared symmetrically.

    *layers* maps layer names to indices so that string-based ignore pairs can
    be resolved.  Unknown layer names are silently skipped.
    """
    matrix = [_ALL_COLLIDE] * _NUM_LAYERS
    if not ignore_pairs:
        return matrix

    layer_map = layers or {}

    for pair in ignore_pairs:
        if len(pair) != 2:
            continue
        name_a, name_b = pair
        idx_a = layer_map.get(name_a)
        idx_b = layer_map.get(name_b)
        if idx_a is None or idx_b is None:
            continue
        if not (0 <= idx_a < _NUM_LAYERS and 0 <= idx_b < _NUM_LAYERS):
            continue
        # Clear bit j in row i and bit i in row j
        matrix[idx_a] &= ~(1 << idx_b)
        matrix[idx_b] &= ~(1 << idx_a)

    return matrix


def _write_physics_2d_settings(
    output_dir: Path,
    physics: dict | None,
) -> None:
    """Write ProjectSettings/Physics2DSettings.asset in Unity YAML format.

    Generates gravity and a 32x32 layer collision matrix.
    """
    if physics is None:
        physics = {}

    gravity = physics.get("gravity", _DEFAULT_GRAVITY)
    ignore_pairs = physics.get("ignore_pairs", [])
    layers = physics.get("layers")
    matrix = _build_collision_matrix(ignore_pairs, layers)

    gx = gravity[0] if len(gravity) > 0 else 0
    gy = gravity[1] if len(gravity) > 1 else -9.81

    lines: list[str] = []
    lines.append("%YAML 1.1")
    lines.append("%TAG !u! tag:unity3d.com,2011:")
    lines.append("--- !u!19 &1")
    lines.append("Physics2DSettings:")
    lines.append("  m_Gravity:")
    lines.append(f"    x: {gx}")
    lines.append(f"    y: {gy}")
    lines.append("  m_DefaultMaterial: {fileID: 0}")
    lines.append("  m_VelocityIterations: 8")
    lines.append("  m_PositionIterations: 3")
    lines.append("  m_VelocityThreshold: 1")
    lines.append("  m_MaxLinearCorrection: 0.2")
    lines.append("  m_MaxAngularCorrection: 8")
    lines.append("  m_MaxTranslationSpeed: 100")
    lines.append("  m_MaxRotationSpeed: 360")
    lines.append("  m_QueriesHitTriggers: 1")
    lines.append("  m_QueriesStartInColliders: 1")
    lines.append("  m_AutoSimulation: 1")
    lines.append("  m_LayerCollisionMatrix:")

    for row_val in matrix:
        lines.append(f"    - {row_val}")

    ps_path = output_dir / "ProjectSettings" / "Physics2DSettings.asset"
    ps_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_scene(output_dir: Path, game_name: str) -> None:
    """Generate a minimal Scene.unity with camera + directional light.

    This lets Unity open the scene immediately. Full population happens
    via the CoPlay generator's Execute().
    """
    scene = """%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!29 &1
OcclusionCullingSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 2
  m_OcclusionBakeSettings:
    smallestOccluder: 5
    smallestHole: 0.25
    backfaceThreshold: 100
--- !u!104 &2
RenderSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 9
  m_Fog: 0
  m_AmbientSkyColor: {r: 0.212, g: 0.227, b: 0.259, a: 1}
  m_AmbientEquatorColor: {r: 0.114, g: 0.125, b: 0.133, a: 1}
  m_AmbientGroundColor: {r: 0.047, g: 0.043, b: 0.035, a: 1}
  m_AmbientIntensity: 1
  m_AmbientMode: 3
--- !u!157 &3
LightmapSettings:
  m_ObjectHideFlags: 0
  serializedVersion: 12
--- !u!196 &4
NavMeshSettings:
  serializedVersion: 2
  m_ObjectHideFlags: 0
--- !u!1 &100
GameObject:
  m_ObjectHideFlags: 0
  serializedVersion: 6
  m_Component:
  - component: {fileID: 101}
  - component: {fileID: 102}
  m_Layer: 0
  m_Name: Main Camera
  m_TagString: MainCamera
  m_IsActive: 1
--- !u!4 &101
Transform:
  m_ObjectHideFlags: 0
  m_PrefabInstance: {fileID: 0}
  m_GameObject: {fileID: 100}
  m_LocalPosition: {x: 0, y: 0, z: -10}
  m_LocalRotation: {x: 0, y: 0, z: 0, w: 1}
  m_LocalScale: {x: 1, y: 1, z: 1}
  m_Children: []
  m_Father: {fileID: 0}
--- !u!20 &102
Camera:
  m_ObjectHideFlags: 0
  serializedVersion: 2
  m_GameObject: {fileID: 100}
  m_Enabled: 1
  m_ClearFlags: 2
  m_BackGroundColor: {r: 0, g: 0, b: 0, a: 0}
  m_projectionMatrixMode: 1
  m_GateFitMode: 2
  m_SensorSize: {x: 36, y: 24}
  m_FOVAxisMode: 0
  orthographic: 1
  m_OrthographicSize: 16
  m_Depth: -1
  m_TargetDisplay: 0
--- !u!1 &200
GameObject:
  m_ObjectHideFlags: 0
  serializedVersion: 6
  m_Component:
  - component: {fileID: 201}
  - component: {fileID: 202}
  m_Layer: 0
  m_Name: Directional Light
  m_TagString: Untagged
  m_IsActive: 1
--- !u!4 &201
Transform:
  m_ObjectHideFlags: 0
  m_PrefabInstance: {fileID: 0}
  m_GameObject: {fileID: 200}
  m_LocalPosition: {x: 0, y: 3, z: 0}
  m_LocalRotation: {x: 0.40821788, y: -0.23456968, z: 0.10938163, w: 0.8754261}
  m_LocalScale: {x: 1, y: 1, z: 1}
  m_Children: []
  m_Father: {fileID: 0}
--- !u!108 &202
Light:
  m_ObjectHideFlags: 0
  serializedVersion: 10
  m_GameObject: {fileID: 200}
  m_Enabled: 1
  m_Type: 1
  m_Color: {r: 1, g: 1, b: 1, a: 1}
  m_Intensity: 1
  m_Range: 10
  m_SpotAngle: 30
  m_InnerSpotAngle: 21.80208
  m_CookieSize: 10
  m_Shadows:
    m_Type: 2
    m_Resolution: -1
    m_Strength: 1
"""
    scene_dir = output_dir / "Assets" / "_Project" / "Scenes"
    scene_dir.mkdir(parents=True, exist_ok=True)
    scene_path = scene_dir / "Scene.unity"
    scene_path.write_text(scene, encoding="utf-8")

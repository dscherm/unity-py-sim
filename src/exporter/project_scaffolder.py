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

_EDITOR_VERSION = "2022.3.0f1"


def scaffold_project(
    game_name: str,
    output_dir: Path,
    *,
    cs_files: dict[str, str],
    tags: list[str] | None = None,
    required_packages: list[str] | None = None,
) -> Path:
    """Create a Unity project folder structure with translated C# files.

    Args:
        game_name: Name of the game (used in ProjectSettings).
        output_dir: Root directory for the Unity project.
        cs_files: Dict of filename -> C# source code (from translate_project).
        tags: Optional list of Unity tags to add to TagManager.asset.
        required_packages: Optional list of additional Unity package names.

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

    # 5. Generate TagManager.asset if tags provided
    if tags:
        _write_tag_manager(output_dir, tags)

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


def _write_tag_manager(output_dir: Path, tags: list[str]) -> None:
    """Write ProjectSettings/TagManager.asset with custom tags."""
    tag_entries = "\n".join(f"  - {tag}" for tag in tags)
    tm_path = output_dir / "ProjectSettings" / "TagManager.asset"
    tm_path.write_text(
        f"""%YAML 1.1
%TAG !u! tag:unity3d.com,2011:
--- !u!78 &1
TagManager:
  tags:
{tag_entries}
  layers:
  - Default
  - TransparentFX
  - Ignore Raycast
  - Water
  - UI
""",
        encoding="utf-8",
    )

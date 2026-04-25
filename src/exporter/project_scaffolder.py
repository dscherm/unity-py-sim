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

import hashlib
import json
import math
import struct
import zlib
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
    # CoPlay MCP plugin — required for the generated Editor scripts
    # (GeneratedSceneSetup.cs / GeneratedSceneValidation.cs) to run via
    # the CoPlay tools menu and for MCP scene-reconstruction. Adding here
    # so home-machine deploy doesn't need the manual manifest edit that
    # FU-2 hit on Flappy Bird.
    "com.coplaydev.coplay": "https://github.com/CoplayDev/unity-plugin.git#beta",
}

# Well-known optional packages and their versions
_KNOWN_PACKAGE_VERSIONS: dict[str, str] = {
    # 1.11.x is the Unity-6-compatible line.  Older (1.7.0) throws
    # InvalidCastException in InputManager.OnUpdate on every editor tick
    # on Unity 6, likely due to event-buffer struct-layout differences
    # between the package and Unity 6's native input runtime.
    "com.unity.inputsystem": "1.11.2",
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
    prefab_data: dict | None = None,
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
        prefab_data: Optional output from prefab_detector.detect_prefabs().
            If provided, generates .prefab and .prefab.meta stubs in
            Assets/_Project/Prefabs/.

    Returns:
        The output_dir Path.
    """
    output_dir = Path(output_dir)

    # 1. Create directory structure
    for rel_dir in _PROJECT_DIRS:
        (output_dir / rel_dir).mkdir(parents=True, exist_ok=True)

    # 2. Write C# files to Scripts directory.  Each file also gets a .cs.meta
    # with a deterministic GUID (flappy_bird_deploy.md gap 7) so the prefab
    # generator's m_Script references — which use the same SHA-256 scheme —
    # resolve correctly on first project import.  Without this, Unity
    # assigns random GUIDs to each .cs on first import, the prefabs'
    # MonoBehaviour refs become dangling, and spawned clones have no
    # attached script (Update() never runs, pipes don't move, etc.).
    scripts_dir = output_dir / "Assets" / "_Project" / "Scripts"
    for filename, content in cs_files.items():
        if filename in _EXCLUDED_FILES:
            continue
        if not filename.endswith(".cs"):
            continue
        (scripts_dir / filename).write_text(content, encoding="utf-8")
        class_name = filename[:-3]  # strip `.cs`
        _write_cs_meta(scripts_dir / f"{filename}.meta", class_name)

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

    # 8. Generate .prefab stubs if prefab data provided
    if prefab_data:
        _write_prefabs(output_dir, prefab_data)

    _copy_project_sprites(game_name, output_dir)

    # 9. Generate default sprite assets (S7-1) — required so SpriteRenderers
    # actually render in the generated scene
    _write_default_sprites(output_dir)

    # 10. Generate BouncyBall physics material (S7-3) — used by ball-like
    # objects so they bounce indefinitely off walls/bricks
    _write_bouncy_ball_material(output_dir)

    # 11. Write AutoStart.cs fixture (flappy_bird_deploy.md gap 1).
    # When the translated scene has a GameManager that pauses at Start() and
    # expects a UI Play button's onClick to un-pause, no click handler is
    # emitted (PlayButtonHandler lives in run_*.py and is filtered by
    # coplay_generator_gaps.md gap 4).  AutoStart bridges that gap: a
    # reflection-based MonoBehaviour that invokes any singleton-style
    # GameManager.Play() it finds at runtime. Harmless for games without a
    # GameManager.
    _write_autostart(output_dir)

    # 12. Write AspectLock.cs fixture (flappy_bird_deploy.md gap 5).
    # Runtime letterbox so sprite art painted for one aspect doesn't
    # stretch/crop under Unity's default Game view aspect.  CoPlay
    # generator attaches it to Main Camera when the scene has an
    # orthographic camera.
    _write_aspect_lock(output_dir)

    # 13. Heal any existing Prefabs/*.prefab whose m_Script GUIDs drifted
    # from the deterministic .cs.meta scheme (flappy_bird_deploy.md gap 7
    # follow-on).  Without this, prefabs that were generated by an earlier
    # version of the scaffolder — or hand-created — still bind to the
    # stale random GUID Unity auto-assigned to the .cs, and Instantiate
    # silently drops the MonoBehaviour.
    _heal_prefab_script_guids(output_dir, cs_files)

    return output_dir


def _heal_prefab_script_guids(
    output_dir: Path,
    cs_files: dict[str, str],
) -> None:
    """Rewrite m_Script GUIDs in Prefabs/*.prefab so MonoBehaviour bindings
    resolve against the deterministic .cs.meta GUIDs this scaffolder writes.

    For each MonoBehaviour stub in a prefab:
      m_Script: {fileID: 11500000, guid: <old>, type: 3}
      m_Name: <ClassName>      ← the class identifier, written by prefab_generator

    If <ClassName>.cs is in cs_files, compute the deterministic GUID and
    replace <old> with it.  No-op when the GUID already matches.
    """
    from src.exporter.prefab_generator import _deterministic_guid
    import re

    prefab_dir = output_dir / "Assets" / "_Project" / "Prefabs"
    if not prefab_dir.is_dir():
        return

    # Build class_name -> deterministic_guid map from scaffolded .cs files.
    class_guids: dict[str, str] = {}
    for filename in cs_files:
        if not filename.endswith(".cs"):
            continue
        cls = filename[:-3]
        class_guids[cls] = _deterministic_guid(f"script:{cls}")

    # Prefab MonoBehaviour instances leave m_Name blank (Unity convention),
    # so we can't read the class name from inside the YAML.  Use the prefab
    # filename as the canonical class identifier — Pipes.prefab -> Pipes.
    # This catches the common single-script prefab case; multi-script
    # prefabs fall through unchanged (the GUIDs would need per-MonoBehaviour
    # class tagging by the upstream generator to heal automatically).
    # Two patterns to cover:
    #   - `m_Script: {fileID: 11500000, guid: <xxxxx>, type: 3}` (drifted GUID)
    #   - `m_Script: {fileID: 0}` (null ref, from pre-gap-7 generator output)
    drifted_pattern = re.compile(
        r"m_Script:\s*\{fileID:\s*11500000,\s*guid:\s*([0-9a-f]{32})"
        r",\s*type:\s*3\}",
    )
    null_pattern = re.compile(r"m_Script:\s*\{fileID:\s*0\}")

    for prefab_path in prefab_dir.glob("*.prefab"):
        cls_name = prefab_path.stem  # "Pipes.prefab" -> "Pipes"
        want = class_guids.get(cls_name)
        if want is None:
            continue
        content = prefab_path.read_text(encoding="utf-8")
        drifted = list(drifted_pattern.finditer(content))
        nulls = list(null_pattern.finditer(content))
        # Only heal if there's exactly one MonoBehaviour script slot (the
        # common root-class case).  Multi-script prefabs need richer
        # class→GUID mapping per MonoBehaviour; skip to avoid mis-wiring.
        if len(drifted) + len(nulls) != 1:
            continue
        healed_ref = f"m_Script: {{fileID: 11500000, guid: {want}, type: 3}}"
        if drifted:
            if drifted[0].group(1) == want:
                continue
            new_content = drifted_pattern.sub(healed_ref, content)
        else:
            new_content = null_pattern.sub(healed_ref, content)
        prefab_path.write_text(new_content, encoding="utf-8")


def _write_cs_meta(meta_path: Path, class_name: str) -> None:
    """Write a .cs.meta next to a scaffolded .cs file.

    Uses the same deterministic GUID scheme (`script:<class>`) that
    `prefab_generator._deterministic_guid` uses when emitting m_Script
    references, so prefab MonoBehaviour bindings resolve on first import.
    """
    from src.exporter.prefab_generator import _deterministic_guid
    guid = _deterministic_guid(f"script:{class_name}")
    meta_path.write_text(
        "fileFormatVersion: 2\n"
        f"guid: {guid}\n"
        "MonoImporter:\n"
        "  externalObjects: {}\n"
        "  serializedVersion: 2\n"
        "  defaultReferences: []\n"
        "  executionOrder: 0\n"
        "  icon: {instanceID: 0}\n"
        "  userData: \n"
        "  assetBundleName: \n"
        "  assetBundleVariant: \n",
        encoding="utf-8",
    )


def _write_aspect_lock(output_dir: Path) -> None:
    """Write Assets/_Project/Scripts/AspectLock.cs — a runtime letterbox.

    Closes data/lessons/flappy_bird_deploy.md gap 5.  Unity's Game view
    defaults to Free Aspect (usually landscape); Flappy Bird's portrait art
    (9:16) was painted for a narrower viewport.  AspectLock forces the
    Main Camera to render into a letterboxed rectangle whose aspect matches
    the game's design, regardless of Game view size.

    The scaffolder ships this as a fixture available to every generated
    project; the CoPlay generator attaches it to Main Camera only when the
    scene has an orthographic camera (which implies a 2D game with a
    specific intended aspect).  Default targetAspect = 9/16 (portrait);
    users change it in the Inspector for landscape games.
    """
    lock_cs = (
        "using UnityEngine;\n"
        "\n"
        "// Scaffolder fixture (data/lessons/flappy_bird_deploy.md gap 5).\n"
        "// Letterboxes Main Camera to a target aspect so sprite art painted\n"
        "// for one aspect doesn't stretch/crop when Unity's Game view uses\n"
        "// a different window shape.\n"
        "[RequireComponent(typeof(Camera))]\n"
        "[DisallowMultipleComponent]\n"
        "public class AspectLock : MonoBehaviour\n"
        "{\n"
        "    [Tooltip(\"Target width/height ratio. 9/16 = portrait (Flappy Bird). 16/9 = landscape.\")]\n"
        "    public float targetAspect = 9f / 16f;\n"
        "\n"
        "    Camera cam;\n"
        "    int lastW, lastH;\n"
        "\n"
        "    void Awake()\n"
        "    {\n"
        "        cam = GetComponent<Camera>();\n"
        "        Apply();\n"
        "    }\n"
        "\n"
        "    void Update()\n"
        "    {\n"
        "        if (Screen.width != lastW || Screen.height != lastH) Apply();\n"
        "    }\n"
        "\n"
        "    void Apply()\n"
        "    {\n"
        "        if (cam == null) return;\n"
        "        lastW = Screen.width; lastH = Screen.height;\n"
        "        float windowAspect = (float)Screen.width / Screen.height;\n"
        "        float scaleHeight = windowAspect / targetAspect;\n"
        "        if (scaleHeight < 1f)\n"
        "        {\n"
        "            // Window wider than target — letterbox top/bottom.\n"
        "            var r = cam.rect;\n"
        "            r.width = 1f;\n"
        "            r.height = scaleHeight;\n"
        "            r.x = 0f;\n"
        "            r.y = (1f - scaleHeight) / 2f;\n"
        "            cam.rect = r;\n"
        "        }\n"
        "        else\n"
        "        {\n"
        "            // Window narrower than target — pillarbox left/right.\n"
        "            float scaleWidth = 1f / scaleHeight;\n"
        "            var r = cam.rect;\n"
        "            r.width = scaleWidth;\n"
        "            r.height = 1f;\n"
        "            r.x = (1f - scaleWidth) / 2f;\n"
        "            r.y = 0f;\n"
        "            cam.rect = r;\n"
        "        }\n"
        "    }\n"
        "}\n"
    )
    (output_dir / "Assets" / "_Project" / "Scripts" / "AspectLock.cs").write_text(
        lock_cs, encoding="utf-8"
    )


def _write_autostart(output_dir: Path) -> None:
    """Write Assets/_Project/Scripts/AutoStart.cs — a reflection-based un-pauser.

    Generic across games: finds a `GameManager` type via reflection, reads its
    `instance` (or `Instance`) static field, and invokes its `Play()` method if
    present.  If any of those pieces don't exist, Start() returns silently.
    """
    autostart = (
        "using System.Reflection;\n"
        "using UnityEngine;\n"
        "\n"
        "// Scaffolder fixture (data/lessons/flappy_bird_deploy.md gap 1).\n"
        "// Un-pauses the game at runtime when GameManager.Start() calls\n"
        "// Pause() expecting a UI Play button that the generator can't wire.\n"
        "public class AutoStart : MonoBehaviour\n"
        "{\n"
        "    void Start()\n"
        "    {\n"
        "        var type = System.Type.GetType(\"GameManager\");\n"
        "        if (type == null) return;\n"
        "        var flags = BindingFlags.Public | BindingFlags.Static;\n"
        "        var field = type.GetField(\"instance\", flags) ?? type.GetField(\"Instance\", flags);\n"
        "        if (field == null) return;\n"
        "        var gm = field.GetValue(null);\n"
        "        if (gm == null) return;\n"
        "        var play = type.GetMethod(\"Play\");\n"
        "        if (play != null) play.Invoke(gm, null);\n"
        "    }\n"
        "}\n"
    )
    (output_dir / "Assets" / "_Project" / "Scripts" / "AutoStart.cs").write_text(
        autostart, encoding="utf-8"
    )


# ── Default sprite asset generation (S7-1) ───────────────────

# Map of sprite_name -> (width, height, generator_callable)
# Each generator returns a list of RGBA bytes.
def _gen_white_square(w: int, h: int) -> bytes:
    """Solid opaque white 32-bit RGBA texture."""
    pixel = b"\xff\xff\xff\xff"
    return pixel * (w * h)


def _gen_circle(size: int) -> bytes:
    """Anti-aliased white circle on transparent 32-bit RGBA texture."""
    cx = cy = (size - 1) / 2.0
    radius = (size / 2.0) - 1.0
    pixels = bytearray(size * size * 4)
    for y in range(size):
        for x in range(size):
            dist = math.hypot(x - cx, y - cy)
            # Antialias edge over 1 pixel band
            if dist <= radius - 1.0:
                a = 255
            elif dist >= radius + 1.0:
                a = 0
            else:
                # Smooth ramp from radius-1 to radius+1
                t = (radius + 1.0 - dist) / 2.0
                a = max(0, min(255, int(t * 255)))
            offset = (y * size + x) * 4
            pixels[offset] = 255
            pixels[offset + 1] = 255
            pixels[offset + 2] = 255
            pixels[offset + 3] = a
    return bytes(pixels)


def _encode_png(width: int, height: int, rgba: bytes) -> bytes:
    """Encode raw RGBA pixel data as a PNG byte stream (stdlib only).

    Uses 8-bit RGBA color type (6) with no filtering for each row.
    """
    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0)

    # Each row is prefixed with filter byte 0 (None), then RGBA bytes
    stride = width * 4
    raw = bytearray()
    for y in range(height):
        raw.append(0)  # no filter
        raw.extend(rgba[y * stride:(y + 1) * stride])
    idat = zlib.compress(bytes(raw), level=9)

    return sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")


def _stable_guid(seed: str) -> str:
    """32-char hex GUID derived deterministically from a string seed."""
    return hashlib.sha256(seed.encode("utf-8")).hexdigest()[:32]


def _sprite_meta_yaml(asset_path: str) -> str:
    """Generate a Unity .meta file for a sprite PNG.

    Critical settings (learned from breakout debug session 2026-04-13):
      - textureType: 8 (Sprite)
      - spriteMode: 1 (Single — NOT 2/Multiple, which requires sprite sheet defs)
      - filterMode: 0 (Point — pixel-art crisp)
      - spritePixelsToUnits: 32
    """
    guid = _stable_guid(asset_path)
    return (
        "fileFormatVersion: 2\n"
        f"guid: {guid}\n"
        "TextureImporter:\n"
        "  internalIDToNameTable: []\n"
        "  externalObjects: {}\n"
        "  serializedVersion: 13\n"
        "  mipmaps:\n"
        "    mipMapMode: 0\n"
        "    enableMipMap: 0\n"
        "    sRGBTexture: 1\n"
        "  isReadable: 0\n"
        "  textureFormat: 1\n"
        "  maxTextureSize: 2048\n"
        "  textureSettings:\n"
        "    serializedVersion: 2\n"
        "    filterMode: 0\n"
        "    aniso: 1\n"
        "    mipBias: 0\n"
        "    wrapU: 1\n"
        "    wrapV: 1\n"
        "    wrapW: 1\n"
        "  nPOTScale: 0\n"
        "  lightmap: 0\n"
        "  compressionQuality: 50\n"
        "  spriteMode: 1\n"
        "  spriteExtrude: 1\n"
        "  spriteMeshType: 1\n"
        "  alignment: 0\n"
        "  spritePivot: {x: 0.5, y: 0.5}\n"
        "  spritePixelsToUnits: 32\n"
        "  spriteBorder: {x: 0, y: 0, z: 0, w: 0}\n"
        "  spriteGenerateFallbackPhysicsShape: 1\n"
        "  alphaUsage: 1\n"
        "  alphaIsTransparency: 1\n"
        "  spriteTessellationDetail: -1\n"
        "  textureType: 8\n"
        "  textureShape: 1\n"
        "  userData: \n"
        "  assetBundleName: \n"
        "  assetBundleVariant: \n"
    )


def _write_bouncy_ball_material(output_dir: Path) -> None:
    """Write Assets/Art/BouncyBall.physicsMaterial2D (S7-3).

    A shared PhysicsMaterial2D with bounciness=1 and friction=0, used by
    ball-like objects so they bounce indefinitely off walls/bricks.
    """
    art_dir = output_dir / "Assets" / "Art"
    art_dir.mkdir(parents=True, exist_ok=True)
    mat_path = art_dir / "BouncyBall.physicsMaterial2D"
    meta_path = art_dir / "BouncyBall.physicsMaterial2D.meta"
    if mat_path.exists() and meta_path.exists():
        return
    mat_path.write_text(
        "%YAML 1.1\n"
        "%TAG !u! tag:unity3d.com,2011:\n"
        "--- !u!62 &6200000\n"
        "PhysicsMaterial2D:\n"
        "  serializedVersion: 2\n"
        "  m_ObjectHideFlags: 0\n"
        "  m_Name: BouncyBall\n"
        "  friction: 0\n"
        "  bounciness: 1\n",
        encoding="utf-8",
    )
    meta_path.write_text(
        "fileFormatVersion: 2\n"
        f"guid: {_stable_guid('Assets/Art/BouncyBall.physicsMaterial2D')}\n"
        "NativeFormatImporter:\n"
        "  externalObjects: {}\n"
        "  mainObjectFileID: 6200000\n"
        "  userData: \n"
        "  assetBundleName: \n"
        "  assetBundleVariant: \n",
        encoding="utf-8",
    )


_ASSETS_ROOT = Path(__file__).resolve().parent.parent.parent / "data" / "assets"


def _copy_project_sprites(game_name: str, output_dir: Path) -> int:
    """Mirror ``data/assets/<game_name>/Sprites/**`` into the Unity project.

    Each PNG gets a sibling ``.meta`` with deterministic GUID + pixel-art
    defaults (Point filter, PPU=32). Replaces the prior manual-drop step that
    produced dangling sprite references in generated projects. No-op when the
    source directory doesn't exist.

    Returns the number of PNGs copied.
    """
    source_dir = _ASSETS_ROOT / game_name / "Sprites"
    if not source_dir.is_dir():
        return 0

    sprites_out = output_dir / "Assets" / "Art" / "Sprites"
    sprites_out.mkdir(parents=True, exist_ok=True)

    import shutil
    count = 0
    for png in sorted(source_dir.rglob("*.png")):
        rel = png.relative_to(source_dir)
        dest = sprites_out / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(png, dest)
        meta_path = dest.parent / (rel.name + ".meta")
        # Preserve existing .meta so Unity-assigned GUIDs + PPU stay stable
        # across re-scaffolds. Prior runs that clobbered GUIDs broke prefab
        # references on the home machine.
        if not meta_path.exists():
            unity_rel = f"Assets/Art/Sprites/{rel.as_posix()}"
            meta_path.write_text(_sprite_meta_yaml(unity_rel), encoding="utf-8")
        count += 1
    return count


def _write_default_sprites(output_dir: Path) -> None:
    """Write WhiteSquare.png and Circle.png (with .meta) to Assets/Art/Sprites.

    Required so SpriteRenderers in the generated scene actually render — Unity
    SpriteRenderers with sprite=None render nothing regardless of color (S7-1,
    discovered in 2026-04-13 breakout debug session).
    """
    sprites_dir = output_dir / "Assets" / "Art" / "Sprites"
    sprites_dir.mkdir(parents=True, exist_ok=True)

    sprites: list[tuple[str, bytes]] = [
        ("WhiteSquare.png", _encode_png(32, 32, _gen_white_square(32, 32))),
        ("Circle.png", _encode_png(32, 32, _gen_circle(32))),
    ]

    for filename, png_bytes in sprites:
        png_path = sprites_dir / filename
        meta_path = sprites_dir / (filename + ".meta")
        # Idempotent: skip if both exist with same content (preserves manual edits)
        if png_path.exists() and meta_path.exists():
            continue
        png_path.write_bytes(png_bytes)
        asset_rel = f"Assets/Art/Sprites/{filename}"
        meta_path.write_text(_sprite_meta_yaml(asset_rel), encoding="utf-8")


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
    """Write ProjectSettings/ProjectSettings.asset with game name.

    `activeInputHandler: 2` selects BOTH input systems (old + new).  The
    translator emits Keyboard.current.*.wasPressedThisFrame (new Input
    System) in generated MonoBehaviours.  If the value defaulted to 0
    (Old Input Manager only), Unity's InputManager.OnUpdate throws
    InvalidCastException on every editor/play update.  Keeping Both
    means legacy Input.* calls also work if a helper script uses them.
    """
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
  activeInputHandler: 2
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

    # Layers section (32 entries).  Unity 6 rejects bare `  -` (null scalar)
    # with 'Parser Failure ... Expect : between key and value within mapping'
    # — empty slots must be the quoted empty-string scalar `  - ""`.
    # See data/lessons/coplay_generator_gaps.md gap 8.
    lines.append("  layers:")
    for name in layer_array:
        if name:
            lines.append(f"  - {name}")
        else:
            lines.append('  - ""')

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


def _write_prefabs(output_dir: Path, prefab_data: dict) -> None:
    """Write .prefab and .prefab.meta stubs for detected prefabs."""
    from src.exporter.prefab_generator import generate_prefab_files

    prefab_dir = output_dir / "Assets" / "_Project" / "Prefabs"
    prefab_dir.mkdir(parents=True, exist_ok=True)

    files = generate_prefab_files(prefab_data)
    for filename, content in files.items():
        (prefab_dir / filename).write_text(content, encoding="utf-8")

"""Generate a C# Unity editor script from scene JSON + asset mapping.

Reads the serialized scene (from scene_serializer.py) and asset mapping
(from assets/mapping.py), then produces a C# editor script that can be
executed via CoPlay MCP's execute_script to reconstruct the scene in Unity.

Usage:
    python -m src.exporter.coplay_generator <scene.json> <mapping.json> [--output path.cs]
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


# Components that Unity creates automatically or that we handle specially
SKIP_COMPONENTS = {"Transform", "Camera"}

# Map Python component types to Unity C# types
COMPONENT_TYPE_MAP = {
    "SpriteRenderer": "SpriteRenderer",
    "AudioSource": "AudioSource",
    "AudioListener": "AudioListener",
    "Rigidbody2D": "Rigidbody2D",
    "BoxCollider2D": "BoxCollider2D",
    "CircleCollider2D": "CircleCollider2D",
}


def _escape_cs_string(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def generate_scene_script(
    scene_data: dict[str, Any],
    mapping_data: dict[str, Any] | None = None,
    namespace: str = "",
) -> str:
    """Generate a C# editor script that reconstructs the scene.

    Args:
        scene_data: Scene JSON from scene_serializer
        mapping_data: Asset mapping JSON (optional, for sprite/audio assignment)
        namespace: C# namespace for MonoBehaviour scripts (e.g. "AngryBirds")

    Returns:
        C# source code for an editor script
    """
    sprite_mappings = mapping_data.get("sprites", {}) if mapping_data else {}
    audio_mappings = mapping_data.get("audio", {}) if mapping_data else {}

    lines: list[str] = []
    lines.append("using UnityEngine;")
    lines.append("using UnityEditor;")
    lines.append("using System.Linq;")
    lines.append("")
    lines.append("public class GeneratedSceneSetup")
    lines.append("{")
    lines.append("    public static string Execute()")
    lines.append("    {")
    lines.append("        string result = \"\";")
    lines.append("")

    # Collect tags needed
    tags = set()
    for go in scene_data.get("game_objects", []):
        if go.get("tag") and go["tag"] != "Untagged":
            tags.add(go["tag"])

    if tags:
        lines.append("        // === CREATE TAGS ===")
        lines.append("        var tagManager = new SerializedObject(AssetDatabase.LoadAllAssetsAtPath(\"ProjectSettings/TagManager.asset\")[0]);")
        lines.append("        var tagsProp = tagManager.FindProperty(\"tags\");")
        for tag in sorted(tags):
            lines.append(f"        _EnsureTag(tagsProp, \"{_escape_cs_string(tag)}\");")
        lines.append("        tagManager.ApplyModifiedProperties();")
        lines.append("")

    # Load unlit material for URP
    lines.append("        // === LOAD MATERIALS ===")
    lines.append("        var unlitMat = AssetDatabase.LoadAssetAtPath<Material>(")
    lines.append("            \"Packages/com.unity.render-pipelines.universal/Runtime/Materials/Sprite-Unlit-Default.mat\");")
    lines.append("")

    # Load sprite assets from mapping
    if sprite_mappings:
        lines.append("        // === LOAD SPRITE ASSETS ===")
        for ref, info in sprite_mappings.items():
            var_name = f"sprite_{ref}"
            unity_path = info.get("unity_path", "")
            sprite_name = info.get("sprite_name")
            if sprite_name:
                lines.append(f"        var {var_name} = AssetDatabase.LoadAllAssetsAtPath(\"{_escape_cs_string(unity_path)}\")")
                lines.append(f"            .OfType<Sprite>().FirstOrDefault(s => s.name == \"{_escape_cs_string(sprite_name)}\");")
            else:
                lines.append(f"        var {var_name} = AssetDatabase.LoadAssetAtPath<Sprite>(\"{_escape_cs_string(unity_path)}\");")
        lines.append("")

    # Process each GameObject
    lines.append("        // === CREATE GAMEOBJECTS ===")
    camera_go_name = None

    for go in scene_data.get("game_objects", []):
        go_name = go["name"]
        tag = go.get("tag", "Untagged")
        var = _safe_var_name(go_name)

        # Find transform component
        transform = None
        for comp in go.get("components", []):
            if comp["type"] == "Transform":
                transform = comp
                break

        # Check if it's the camera (already exists in scene)
        has_camera = any(c["type"] == "Camera" for c in go.get("components", []))
        if has_camera:
            camera_go_name = go_name
            lines.append(f"        // --- {go_name} (use existing Main Camera) ---")
            lines.append(f"        var {var} = Camera.main?.gameObject;")
            lines.append(f"        if ({var} != null)")
            lines.append("        {")
            lines.append(f"            var cam = {var}.GetComponent<Camera>();")
            for comp in go.get("components", []):
                if comp["type"] == "Camera":
                    lines.append(f"            cam.orthographicSize = {comp.get('orthographic_size', 5)}f;")
                    bg = comp.get("background_color")
                    if bg:
                        r, g, b = bg[0] / 255.0, bg[1] / 255.0, bg[2] / 255.0
                        lines.append(f"            cam.backgroundColor = new Color({r:.3f}f, {g:.3f}f, {b:.3f}f, 1f);")
                        lines.append(f"            cam.clearFlags = CameraClearFlags.SolidColor;")
            if transform:
                px, py, pz = transform["position"]
                lines.append(f"            {var}.transform.position = new Vector3({px}f, {py}f, {pz}f);")
            lines.append(f"            EditorUtility.SetDirty({var});")
            lines.append("        }")
            lines.append("")
            continue

        # Create new GameObject
        lines.append(f"        // --- {go_name} ---")
        lines.append(f"        var {var} = new GameObject(\"{_escape_cs_string(go_name)}\");")

        if tag != "Untagged":
            lines.append(f"        {var}.tag = \"{_escape_cs_string(tag)}\";")

        # Set transform
        if transform:
            px, py, pz = transform["position"]
            lines.append(f"        {var}.transform.position = new Vector3({px}f, {py}f, {pz}f);")
            sx, sy, sz = transform.get("local_scale", [1, 1, 1])
            if sx != 1 or sy != 1 or sz != 1:
                lines.append(f"        {var}.transform.localScale = new Vector3({sx}f, {sy}f, {sz}f);")

        # Add components
        for comp in go.get("components", []):
            ctype = comp["type"]
            if ctype in SKIP_COMPONENTS:
                continue
            _generate_component(lines, var, comp, sprite_mappings, audio_mappings, namespace)

        lines.append(f"        EditorUtility.SetDirty({var});")
        lines.append("")

    # Wire cross-references (MonoBehaviour fields referencing other GameObjects)
    lines.append("        // === WIRE CROSS-REFERENCES ===")
    for go in scene_data.get("game_objects", []):
        var = _safe_var_name(go["name"])
        for comp in go.get("components", []):
            if not comp.get("is_monobehaviour"):
                continue
            ctype = comp["type"]
            ns_prefix = f"{namespace}." if namespace else ""
            for field_name, field_val in comp.get("fields", {}).items():
                if isinstance(field_val, dict) and field_val.get("_type") == "GameObjectRef":
                    ref_name = field_val["name"]
                    ref_var = _safe_var_name(ref_name)
                    cs_field = _to_camel_case(field_name)
                    lines.append(f"        {{")
                    lines.append(f"            var so = new SerializedObject({var}.GetComponent<{ns_prefix}{ctype}>());")
                    lines.append(f"            var prop = so.FindProperty(\"{cs_field}\");")
                    lines.append(f"            if (prop != null) {{ prop.objectReferenceValue = {ref_var}; so.ApplyModifiedProperties(); }}")
                    lines.append(f"        }}")

    lines.append("")
    lines.append("        // === SAVE ===")
    lines.append("        UnityEditor.SceneManagement.EditorSceneManager.MarkSceneDirty(")
    lines.append("            UnityEditor.SceneManagement.EditorSceneManager.GetActiveScene());")
    lines.append("        UnityEditor.SceneManagement.EditorSceneManager.SaveOpenScenes();")
    lines.append("")
    lines.append(f"        result = \"Scene setup complete: {len(scene_data.get('game_objects', []))} GameObjects\";")
    lines.append("        return result;")
    lines.append("    }")
    lines.append("")

    # Helper: ensure tag exists
    if tags:
        lines.append("    static void _EnsureTag(SerializedProperty tagsProp, string tag)")
        lines.append("    {")
        lines.append("        for (int i = 0; i < tagsProp.arraySize; i++)")
        lines.append("            if (tagsProp.GetArrayElementAtIndex(i).stringValue == tag) return;")
        lines.append("        tagsProp.InsertArrayElementAtIndex(tagsProp.arraySize);")
        lines.append("        tagsProp.GetArrayElementAtIndex(tagsProp.arraySize - 1).stringValue = tag;")
        lines.append("    }")

    lines.append("}")
    lines.append("")

    return "\n".join(lines)


def _generate_component(
    lines: list[str],
    go_var: str,
    comp: dict[str, Any],
    sprite_mappings: dict,
    audio_mappings: dict,
    namespace: str,
) -> None:
    """Generate C# lines to add and configure a component."""
    ctype = comp["type"]

    if ctype == "SpriteRenderer":
        lines.append(f"        var {go_var}_sr = {go_var}.AddComponent<SpriteRenderer>();")
        asset_ref = comp.get("asset_ref")
        if asset_ref and asset_ref in sprite_mappings:
            lines.append(f"        if (sprite_{asset_ref} != null) {go_var}_sr.sprite = sprite_{asset_ref};")
        lines.append(f"        if (unlitMat != null) {go_var}_sr.sharedMaterial = unlitMat;")
        so = comp.get("sorting_order", 0)
        if so != 0:
            lines.append(f"        {go_var}_sr.sortingOrder = {so};")
        # Set color as tint if no sprite mapping
        if not asset_ref or asset_ref not in sprite_mappings:
            color = comp.get("color", [255, 255, 255])
            r, g, b = color[0] / 255.0, color[1] / 255.0, color[2] / 255.0
            lines.append(f"        {go_var}_sr.color = new Color({r:.3f}f, {g:.3f}f, {b:.3f}f, 1f);")

    elif ctype == "AudioSource":
        lines.append(f"        {go_var}.AddComponent<AudioSource>();")

    elif ctype == "AudioListener":
        lines.append(f"        {go_var}.AddComponent<AudioListener>();")

    elif ctype == "Rigidbody2D":
        lines.append(f"        var {go_var}_rb = {go_var}.AddComponent<Rigidbody2D>();")
        body_type = comp.get("body_type", "Dynamic")
        if body_type == "Static":
            lines.append(f"        {go_var}_rb.bodyType = RigidbodyType2D.Static;")
        elif body_type == "Kinematic":
            lines.append(f"        {go_var}_rb.bodyType = RigidbodyType2D.Kinematic;")
        mass = comp.get("mass", 1)
        if mass != 1 and mass < 999999:
            lines.append(f"        {go_var}_rb.mass = {mass}f;")
        gs = comp.get("gravity_scale", 1)
        if gs != 1:
            lines.append(f"        {go_var}_rb.gravityScale = {gs}f;")

    elif ctype == "BoxCollider2D":
        lines.append(f"        var {go_var}_bc = {go_var}.AddComponent<BoxCollider2D>();")
        size = comp.get("size", [1, 1])
        lines.append(f"        {go_var}_bc.size = new Vector2({size[0]}f, {size[1]}f);")
        if comp.get("is_trigger"):
            lines.append(f"        {go_var}_bc.isTrigger = true;")

    elif ctype == "CircleCollider2D":
        lines.append(f"        var {go_var}_cc = {go_var}.AddComponent<CircleCollider2D>();")
        radius = comp.get("radius", 0.5)
        lines.append(f"        {go_var}_cc.radius = {radius}f;")
        if comp.get("is_trigger"):
            lines.append(f"        {go_var}_cc.isTrigger = true;")

    elif comp.get("is_monobehaviour"):
        ns_prefix = f"{namespace}." if namespace else ""
        lines.append(f"        {go_var}.AddComponent<{ns_prefix}{ctype}>();")
        # Set simple serialized fields
        for field_name, field_val in comp.get("fields", {}).items():
            if isinstance(field_val, (int, float)) and not isinstance(field_val, bool):
                cs_field = _to_camel_case(field_name)
                # Use SerializedObject for private/serialized fields
                if field_val != 0:
                    lines.append(f"        // {ctype}.{cs_field} = {field_val}")


def _safe_var_name(name: str) -> str:
    """Convert a GameObject name to a safe C# variable name."""
    safe = name.replace(" ", "_").replace("-", "_").replace(".", "_")
    safe = "".join(c for c in safe if c.isalnum() or c == "_")
    if safe and safe[0].isdigit():
        safe = "go_" + safe
    return "go_" + safe


def _to_camel_case(snake_str: str) -> str:
    """Convert snake_case to camelCase."""
    parts = snake_str.split("_")
    return parts[0] + "".join(p.capitalize() for p in parts[1:])


def generate_from_files(
    scene_path: str | Path,
    mapping_path: str | Path | None = None,
    namespace: str = "",
) -> str:
    """Load files and generate the C# script."""
    scene_data = json.loads(Path(scene_path).read_text(encoding="utf-8"))
    mapping_data = None
    if mapping_path:
        mapping_data = json.loads(Path(mapping_path).read_text(encoding="utf-8"))
    return generate_scene_script(scene_data, mapping_data, namespace)


def main():
    import sys

    args = sys.argv[1:]
    if len(args) < 1:
        print("Usage: python -m src.exporter.coplay_generator <scene.json> [mapping.json] [--output path.cs] [--namespace Name]")
        sys.exit(1)

    scene_path = args[0]
    mapping_path = args[1] if len(args) > 1 and not args[1].startswith("--") else None

    output_path = None
    namespace = ""
    if "--output" in args:
        idx = args.index("--output")
        output_path = Path(args[idx + 1])
    if "--namespace" in args:
        idx = args.index("--namespace")
        namespace = args[idx + 1]

    cs_code = generate_from_files(scene_path, mapping_path, namespace)

    if output_path:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(cs_code, encoding="utf-8")
        print(f"Generated C# script: {output_path}")
    else:
        print(cs_code)


if __name__ == "__main__":
    main()

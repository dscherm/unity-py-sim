"""Contract tests for prefab_generator — validate Unity .prefab YAML format compliance.

These tests derive from the Unity .prefab serialization format specification:
- https://docs.unity3d.com/Manual/FormatDescription.html
- https://docs.unity3d.com/Manual/ClassIDReference.html

They do NOT test implementation details — only that output conforms to what Unity expects.
"""

from __future__ import annotations

import re

import pytest

from src.exporter.prefab_generator import (
    generate_prefab_files,
    generate_prefab_meta,
    generate_prefab_yaml,
)


# ── Helpers ──────────────────────────────────────────────────────


def _parse_yaml_documents(yaml_text: str) -> list[tuple[str, str, dict]]:
    """Parse Unity YAML into a list of (tag, fileID, header_line) tuples.

    Unity YAML uses ``--- !u!<classID> &<fileID>`` document separators.
    Returns list of (class_id_str, file_id_str, body_text).
    """
    docs = []
    # Split on document separators
    parts = re.split(r"^(--- !u!\d+ &\d+)$", yaml_text, flags=re.MULTILINE)
    # parts[0] is the header (%YAML, %TAG), then alternating separator/body
    for i in range(1, len(parts), 2):
        sep = parts[i]
        body = parts[i + 1] if i + 1 < len(parts) else ""
        m = re.match(r"--- !u!(\d+) &(\d+)", sep)
        if m:
            docs.append((m.group(1), m.group(2), body))
    return docs


def _extract_component_filerefs(yaml_text: str) -> list[int]:
    """Extract all fileID values from m_Component entries in a GameObject block."""
    ids = []
    for m in re.finditer(r"component:\s*\{fileID:\s*(\d+)\}", yaml_text):
        ids.append(int(m.group(1)))
    return ids


# ── YAML Header Contracts ────────────────────────────────────────


class TestYAMLHeaderContracts:
    """Unity requires specific YAML header directives."""

    def test_starts_with_yaml_1_1(self):
        """Unity .prefab files MUST start with %YAML 1.1 directive."""
        yaml = generate_prefab_yaml("TestObj", [])
        assert yaml.startswith("%YAML 1.1\n"), "Missing %YAML 1.1 header"

    def test_has_unity_tag_directive(self):
        """Unity .prefab files MUST have the !u! tag directive on line 2."""
        yaml = generate_prefab_yaml("TestObj", [])
        lines = yaml.split("\n")
        assert len(lines) >= 2
        assert lines[1] == "%TAG !u! tag:unity3d.com,2011:", (
            "Line 2 must be Unity tag directive"
        )

    def test_no_yaml_2_0(self):
        """Unity does NOT support YAML 2.0 — must be 1.1."""
        yaml = generate_prefab_yaml("TestObj", ["SpriteRenderer"])
        assert "%YAML 2.0" not in yaml


# ── GameObject Contracts ─────────────────────────────────────────


class TestGameObjectContracts:
    """Unity GameObject serialization requirements."""

    def test_gameobject_uses_class_id_1(self):
        """Unity GameObject class ID is 1 per ClassIDReference."""
        yaml = generate_prefab_yaml("Player", ["Rigidbody2D"])
        assert re.search(r"--- !u!1 &\d+", yaml), "GameObject must use class ID 1"

    def test_gameobject_serialized_version_6(self):
        """Current Unity GameObjects use serializedVersion: 6."""
        yaml = generate_prefab_yaml("Player", [])
        docs = _parse_yaml_documents(yaml)
        go_docs = [(cid, fid, body) for cid, fid, body in docs if cid == "1"]
        assert len(go_docs) >= 1, "Must have at least one GameObject document"
        for _, _, body in go_docs:
            assert "serializedVersion: 6" in body, (
                "GameObject must have serializedVersion: 6"
            )

    def test_gameobject_has_m_name(self):
        """GameObject must include m_Name field with the prefab name."""
        yaml = generate_prefab_yaml("Brick", [])
        assert "m_Name: Brick" in yaml

    def test_gameobject_has_m_layer(self):
        """GameObject must define m_Layer (default 0)."""
        yaml = generate_prefab_yaml("Brick", [])
        assert "m_Layer: 0" in yaml

    def test_gameobject_has_m_is_active(self):
        """GameObject must set m_IsActive (1 = active)."""
        yaml = generate_prefab_yaml("Brick", [])
        assert "m_IsActive: 1" in yaml

    def test_gameobject_has_m_tag_string(self):
        """GameObject must have m_TagString set."""
        yaml = generate_prefab_yaml("Brick", [])
        assert re.search(r"m_TagString:\s+\S+", yaml), "Must set m_TagString"


# ── Transform Contracts ──────────────────────────────────────────


class TestTransformContracts:
    """Unity requires every GameObject to have exactly one Transform."""

    def test_transform_always_present(self):
        """A .prefab MUST always have a Transform component (class ID 4)."""
        yaml = generate_prefab_yaml("Empty", [])
        assert re.search(r"--- !u!4 &\d+", yaml), "Transform (class ID 4) is mandatory"

    def test_transform_references_parent_gameobject(self):
        """Transform m_GameObject must reference the parent GameObject's fileID."""
        yaml = generate_prefab_yaml("Ball", ["Rigidbody2D"])
        docs = _parse_yaml_documents(yaml)

        # Find the GameObject fileID
        go_file_ids = [fid for cid, fid, _ in docs if cid == "1"]
        assert go_file_ids, "Must have a GameObject"
        go_id = go_file_ids[0]

        # Find the Transform body
        transform_docs = [(cid, fid, body) for cid, fid, body in docs if cid == "4"]
        assert transform_docs, "Must have a Transform"
        _, _, tbody = transform_docs[0]
        assert f"m_GameObject: {{fileID: {go_id}}}" in tbody, (
            "Transform must reference parent GameObject via m_GameObject fileID"
        )

    def test_transform_has_position_rotation_scale(self):
        """Transform must define local position, rotation, and scale."""
        yaml = generate_prefab_yaml("Obj", [])
        assert "m_LocalPosition:" in yaml
        assert "m_LocalRotation:" in yaml
        assert "m_LocalScale:" in yaml

    def test_transform_in_component_list(self):
        """Transform must be listed in the GameObject's m_Component array."""
        yaml = generate_prefab_yaml("Obj", ["BoxCollider2D"])
        docs = _parse_yaml_documents(yaml)
        transform_ids = [fid for cid, fid, _ in docs if cid == "4"]
        assert transform_ids
        component_refs = _extract_component_filerefs(yaml)
        assert int(transform_ids[0]) in component_refs, (
            "Transform fileID must appear in m_Component list"
        )

    def test_transform_class_id_is_4(self):
        """Unity Transform class ID is 4 per ClassIDReference."""
        yaml = generate_prefab_yaml("Obj", [])
        assert re.search(r"--- !u!4 &\d+", yaml)


# ── Component Cross-Reference Contracts ──────────────────────────


class TestComponentCrossReferenceContracts:
    """All components listed in m_Component must have corresponding YAML documents."""

    def test_all_component_refs_have_documents(self):
        """Every fileID in m_Component must have a matching --- !u!<N> &<fileID> entry."""
        yaml = generate_prefab_yaml("Enemy", ["Rigidbody2D", "BoxCollider2D", "SpriteRenderer"])
        component_refs = _extract_component_filerefs(yaml)
        docs = _parse_yaml_documents(yaml)
        doc_file_ids = {int(fid) for _, fid, _ in docs}

        for ref_id in component_refs:
            assert ref_id in doc_file_ids, (
                f"m_Component references fileID {ref_id} but no document defines it"
            )

    def test_no_orphan_components(self):
        """Non-GameObject documents should be referenced from m_Component (no orphans)."""
        yaml = generate_prefab_yaml("Enemy", ["CircleCollider2D", "AudioSource"])
        component_refs = set(_extract_component_filerefs(yaml))
        docs = _parse_yaml_documents(yaml)

        for cid, fid, _ in docs:
            if cid == "1":  # Skip the GameObject itself
                continue
            assert int(fid) in component_refs, (
                f"Document with fileID {fid} (classID {cid}) is not referenced in m_Component"
            )

    def test_component_m_gameobject_backreference(self):
        """Each component document must reference the parent GameObject via m_GameObject."""
        yaml = generate_prefab_yaml("Ship", ["Rigidbody2D", "SpriteRenderer"])
        docs = _parse_yaml_documents(yaml)
        go_ids = [fid for cid, fid, _ in docs if cid == "1"]
        assert go_ids
        go_id = go_ids[0]

        for cid, fid, body in docs:
            if cid == "1":
                continue
            assert f"m_GameObject: {{fileID: {go_id}}}" in body, (
                f"Component (classID {cid}, fileID {fid}) must reference parent GameObject"
            )


# ── Unity Class ID Contracts ────────────────────────────────────


class TestUnityClassIDContracts:
    """Unity class IDs from the official ClassIDReference table."""

    @pytest.mark.parametrize("component,expected_id", [
        ("Transform", "4"),
        ("SpriteRenderer", "212"),
        ("Rigidbody2D", "50"),
        ("BoxCollider2D", "61"),
        ("CircleCollider2D", "58"),
        ("AudioSource", "82"),
        ("Animator", "95"),
        ("Camera", "20"),
    ])
    def test_builtin_class_ids(self, component, expected_id):
        """Built-in Unity components must use their canonical class IDs."""
        yaml = generate_prefab_yaml("Test", [component])
        pattern = rf"--- !u!{expected_id} &\d+"
        assert re.search(pattern, yaml), (
            f"{component} must use class ID {expected_id}"
        )

    def test_unknown_component_uses_monobehaviour_114(self):
        """Custom scripts must use MonoBehaviour class ID 114."""
        yaml = generate_prefab_yaml("Test", ["MyCustomScript"])
        assert re.search(r"--- !u!114 &\d+", yaml), (
            "Custom components must use MonoBehaviour class ID 114"
        )

    def test_monobehaviour_has_m_script_field(self):
        """MonoBehaviour components must include m_Script reference."""
        yaml = generate_prefab_yaml("Test", ["PlayerController"])
        assert "m_Script:" in yaml, "MonoBehaviour must have m_Script field"


# ── .meta File Contracts ─────────────────────────────────────────


class TestMetaFileContracts:
    """Unity .meta file format requirements."""

    def test_meta_has_file_format_version_2(self):
        """Meta files must start with fileFormatVersion: 2."""
        meta = generate_prefab_meta("Brick")
        assert "fileFormatVersion: 2" in meta

    def test_meta_has_32_char_hex_guid(self):
        """Meta files must contain a 32-character hexadecimal GUID."""
        meta = generate_prefab_meta("Brick")
        m = re.search(r"guid:\s+([0-9a-f]+)", meta)
        assert m, "Meta file must contain a guid field"
        assert len(m.group(1)) == 32, f"GUID must be 32 hex chars, got {len(m.group(1))}"
        assert re.match(r"^[0-9a-f]{32}$", m.group(1)), "GUID must be lowercase hex"

    def test_meta_has_prefab_importer(self):
        """Prefab .meta files should specify PrefabImporter."""
        meta = generate_prefab_meta("Brick")
        assert "PrefabImporter:" in meta

    def test_different_prefabs_get_different_guids(self):
        """Each prefab must have a unique GUID."""
        meta_a = generate_prefab_meta("Brick")
        meta_b = generate_prefab_meta("Ball")
        guid_a = re.search(r"guid:\s+([0-9a-f]+)", meta_a).group(1)
        guid_b = re.search(r"guid:\s+([0-9a-f]+)", meta_b).group(1)
        assert guid_a != guid_b, "Different prefabs must have different GUIDs"

    def test_guid_is_deterministic(self):
        """Same prefab name must always produce the same GUID."""
        meta1 = generate_prefab_meta("Paddle")
        meta2 = generate_prefab_meta("Paddle")
        guid1 = re.search(r"guid:\s+([0-9a-f]+)", meta1).group(1)
        guid2 = re.search(r"guid:\s+([0-9a-f]+)", meta2).group(1)
        assert guid1 == guid2


# ── generate_prefab_files Contracts ──────────────────────────────


class TestGeneratePrefabFilesContracts:
    """Contract tests for the batch file generation entry point."""

    def test_generates_prefab_and_meta_pairs(self):
        """Each prefab must produce both a .prefab and .prefab.meta file."""
        data = {"prefabs": [{"class_name": "Brick", "components": ["BoxCollider2D"]}]}
        files = generate_prefab_files(data)
        assert "Brick.prefab" in files
        assert "Brick.prefab.meta" in files

    def test_handles_empty_prefab_list(self):
        """Empty prefab list should return empty dict."""
        files = generate_prefab_files({"prefabs": []})
        assert files == {}

    def test_handles_missing_prefabs_key(self):
        """Missing 'prefabs' key should return empty dict (not crash)."""
        files = generate_prefab_files({})
        assert files == {}

    def test_multiple_prefabs_produce_separate_files(self):
        """Each prefab class gets its own file pair."""
        data = {
            "prefabs": [
                {"class_name": "Brick", "components": []},
                {"class_name": "Ball", "components": ["Rigidbody2D"]},
            ]
        }
        files = generate_prefab_files(data)
        assert len(files) == 4  # 2 prefabs * 2 files each
        assert "Brick.prefab" in files
        assert "Ball.prefab" in files

    def test_file_ids_are_unique_across_prefabs(self):
        """Different prefabs must not share file IDs."""
        data = {
            "prefabs": [
                {"class_name": "A", "components": ["Rigidbody2D"]},
                {"class_name": "B", "components": ["Rigidbody2D"]},
            ]
        }
        files = generate_prefab_files(data)
        all_ids_a = set(re.findall(r"&(\d+)", files["A.prefab"]))
        all_ids_b = set(re.findall(r"&(\d+)", files["B.prefab"]))
        assert not all_ids_a & all_ids_b, "Different prefabs must have distinct file IDs"


# ── File ID Uniqueness Within a Prefab ───────────────────────────


class TestFileIDUniqueness:
    """All file IDs within a single .prefab must be unique."""

    def test_no_duplicate_file_ids(self):
        """A prefab with many components must not have duplicate &fileID values."""
        yaml = generate_prefab_yaml(
            "Complex",
            ["SpriteRenderer", "Rigidbody2D", "BoxCollider2D", "AudioSource", "MyScript"],
        )
        ids = re.findall(r"&(\d+)", yaml)
        assert len(ids) == len(set(ids)), f"Duplicate file IDs found: {ids}"

    def test_file_ids_are_positive(self):
        """Unity file IDs must be positive integers."""
        yaml = generate_prefab_yaml("Test", ["Rigidbody2D", "SpriteRenderer"])
        ids = [int(x) for x in re.findall(r"&(\d+)", yaml)]
        for fid in ids:
            assert fid > 0, f"File ID must be positive, got {fid}"

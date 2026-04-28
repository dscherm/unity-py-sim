"""Tests for prefab YAML stub generation."""


from src.exporter.prefab_generator import (
    generate_prefab_files,
    generate_prefab_meta,
    generate_prefab_yaml,
    _deterministic_guid,
    _deterministic_file_id,
)


# ---------------------------------------------------------------------------
# Deterministic IDs
# ---------------------------------------------------------------------------

class TestDeterministicIds:
    def test_guid_is_32_hex(self):
        guid = _deterministic_guid("Brick")
        assert len(guid) == 32
        assert all(c in "0123456789abcdef" for c in guid)

    def test_guid_is_stable(self):
        assert _deterministic_guid("Brick") == _deterministic_guid("Brick")

    def test_guid_differs_by_name(self):
        assert _deterministic_guid("Brick") != _deterministic_guid("Pellet")

    def test_file_id_is_positive(self):
        fid = _deterministic_file_id("Brick", "Transform")
        assert fid > 0

    def test_file_id_is_stable(self):
        a = _deterministic_file_id("Brick", "Transform")
        b = _deterministic_file_id("Brick", "Transform")
        assert a == b

    def test_file_id_differs_by_salt(self):
        a = _deterministic_file_id("Brick", "Transform")
        b = _deterministic_file_id("Brick", "Rigidbody2D")
        assert a != b


# ---------------------------------------------------------------------------
# Prefab YAML generation
# ---------------------------------------------------------------------------

class TestPrefabYaml:
    def test_has_yaml_header(self):
        yaml = generate_prefab_yaml("Brick", ["Rigidbody2D", "BoxCollider2D"])
        assert yaml.startswith("%YAML 1.1\n")
        assert "%TAG !u! tag:unity3d.com,2011:" in yaml

    def test_gameobject_has_name(self):
        yaml = generate_prefab_yaml("Brick", [])
        assert "m_Name: Brick" in yaml

    def test_transform_always_present(self):
        yaml = generate_prefab_yaml("Brick", [])
        assert "Transform:" in yaml
        assert "m_LocalPosition:" in yaml

    def test_rigidbody2d_present(self):
        yaml = generate_prefab_yaml("Brick", ["Rigidbody2D"])
        assert "Rigidbody2D:" in yaml
        assert "m_BodyType: 0" in yaml

    def test_boxcollider2d_present(self):
        yaml = generate_prefab_yaml("Brick", ["BoxCollider2D"])
        assert "BoxCollider2D:" in yaml
        assert "m_Size:" in yaml

    def test_circlecollider2d_present(self):
        yaml = generate_prefab_yaml("Brick", ["CircleCollider2D"])
        assert "CircleCollider2D:" in yaml
        assert "m_Radius:" in yaml

    def test_spriterenderer_present(self):
        yaml = generate_prefab_yaml("Brick", ["SpriteRenderer"])
        assert "SpriteRenderer:" in yaml
        assert "m_Sprite:" in yaml

    def test_audiosource_present(self):
        yaml = generate_prefab_yaml("Brick", ["AudioSource"])
        assert "AudioSource:" in yaml
        assert "m_PlayOnAwake: 0" in yaml

    def test_monobehaviour_for_custom_component(self):
        """MonoBehaviour stubs must reference the script asset via the
        deterministic GUID scheme the scaffolder uses when writing
        .cs.meta.  Null refs (`m_Script: {fileID: 0}`) cause Unity to
        drop the component on Instantiate — see flappy_bird_deploy.md
        gap 7 (Pipes clone had no Pipes script, Update() never ran,
        pipes never scrolled)."""
        from src.exporter.prefab_generator import _deterministic_guid
        yaml = generate_prefab_yaml("Brick", ["Brick"])
        assert "MonoBehaviour:" in yaml
        expected_guid = _deterministic_guid("script:Brick")
        assert f"m_Script: {{fileID: 11500000, guid: {expected_guid}, type: 3}}" in yaml
        assert "m_Name: Brick" in yaml

    def test_component_refs_in_gameobject(self):
        yaml = generate_prefab_yaml("Brick", ["Rigidbody2D", "BoxCollider2D"])
        # GameObject should list all components (Transform + 2)
        assert yaml.count("component: {fileID:") == 3  # Transform + Rb + Collider

    def test_multiple_components(self):
        comps = ["Rigidbody2D", "BoxCollider2D", "SpriteRenderer", "AudioSource", "Brick"]
        yaml = generate_prefab_yaml("Brick", comps)
        assert yaml.count("component: {fileID:") == 6  # Transform + 5

    def test_transform_in_components_not_duplicated(self):
        yaml = generate_prefab_yaml("Brick", ["Transform", "Rigidbody2D"])
        # Transform should appear once as a component, not duplicated
        lines = [l for l in yaml.split("\n") if l.strip().startswith("Transform:")]
        assert len(lines) == 1


# ---------------------------------------------------------------------------
# Meta file generation
# ---------------------------------------------------------------------------

class TestPrefabMeta:
    def test_has_guid(self):
        meta = generate_prefab_meta("Brick")
        assert "guid:" in meta
        assert len(meta.split("guid: ")[1].split("\n")[0]) == 32

    def test_has_prefab_importer(self):
        meta = generate_prefab_meta("Brick")
        assert "PrefabImporter:" in meta

    def test_guid_is_stable(self):
        a = generate_prefab_meta("Brick")
        b = generate_prefab_meta("Brick")
        assert a == b

    def test_guid_differs_by_name(self):
        a = generate_prefab_meta("Brick")
        b = generate_prefab_meta("Pellet")
        assert a != b


# ---------------------------------------------------------------------------
# Batch file generation
# ---------------------------------------------------------------------------

class TestGeneratePrefabFiles:
    def test_empty_prefab_data(self):
        files = generate_prefab_files({"prefabs": [], "scene_objects": []})
        assert files == {}

    def test_single_prefab(self):
        data = {
            "prefabs": [{"class_name": "Brick", "components": ["Rigidbody2D"]}],
            "scene_objects": [],
        }
        files = generate_prefab_files(data)
        assert "Brick.prefab" in files
        assert "Brick.prefab.meta" in files
        assert len(files) == 2

    def test_multiple_prefabs(self):
        data = {
            "prefabs": [
                {"class_name": "Brick", "components": []},
                {"class_name": "Pellet", "components": ["SpriteRenderer"]},
            ],
            "scene_objects": [],
        }
        files = generate_prefab_files(data)
        assert len(files) == 4
        assert "Brick.prefab" in files
        assert "Pellet.prefab" in files

    def test_scene_objects_ignored(self):
        data = {
            "prefabs": [{"class_name": "Brick", "components": []}],
            "scene_objects": [{"name": "Paddle"}],
        }
        files = generate_prefab_files(data)
        assert "Paddle.prefab" not in files


# ---------------------------------------------------------------------------
# Scaffolder integration
# ---------------------------------------------------------------------------

class TestScaffolderIntegration:
    def test_prefabs_written_to_project(self, tmp_path):
        from src.exporter.project_scaffolder import scaffold_project

        prefab_data = {
            "prefabs": [
                {"class_name": "Brick", "components": ["Rigidbody2D", "BoxCollider2D"]},
            ],
            "scene_objects": [],
        }
        scaffold_project(
            "test_game",
            tmp_path / "out",
            cs_files={"brick.cs": "// stub"},
            prefab_data=prefab_data,
        )
        prefab_dir = tmp_path / "out" / "Assets" / "_Project" / "Prefabs"
        assert (prefab_dir / "Brick.prefab").exists()
        assert (prefab_dir / "Brick.prefab.meta").exists()

        content = (prefab_dir / "Brick.prefab").read_text()
        assert "%YAML 1.1" in content
        assert "m_Name: Brick" in content
        assert "Rigidbody2D:" in content

    def test_no_prefab_data_no_prefab_files(self, tmp_path):
        from src.exporter.project_scaffolder import scaffold_project

        scaffold_project(
            "test_game",
            tmp_path / "out",
            cs_files={"brick.cs": "// stub"},
        )
        prefab_dir = tmp_path / "out" / "Assets" / "_Project" / "Prefabs"
        # Directory exists (from standard scaffold) but no .prefab files
        prefab_files = list(prefab_dir.glob("*.prefab"))
        assert len(prefab_files) == 0

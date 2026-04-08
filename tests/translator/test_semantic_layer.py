"""Tests for semantic_layer — post-processor that strips simulator artifacts from translated C#."""

import pytest

from src.translator.semantic_layer import transform


class TestStripPygameReferences:
    """Priority 1: Remove pygame/pymunk references that leaked through translation."""

    def test_strips_pygame_display_call(self):
        code = '''\
        try
        {
            pygame.display.SetCaption($"Score: {score}");
        }'''
        result = transform(code)
        assert "pygame" not in result

    def test_strips_pygame_type_annotations(self):
        code = "    public pygame.Surface spriteUp;\n    public pygame.Surface spriteDown;"
        result = transform(code)
        assert "pygame" not in result
        # Should replace with Sprite
        assert "Sprite" in result

    def test_strips_pygame_init_block(self):
        code = '''\
        if (!pygame.GetInit())
        {
            pygame.Init();
        }
        if (pygame.display.GetSurface() == null)
        {
            pygame.display.SetMode((1, 1), pygame.NOFRAME);
        }'''
        result = transform(code)
        assert "pygame" not in result

    def test_strips_pymunk_references(self):
        code = "    pymunk.Space space = new pymunk.Space();\n    pymunk.Body body;"
        result = transform(code)
        assert "pymunk" not in result

    def test_strips_pygame_image_load(self):
        code = '        var surf = pygame.image.Load(path).ConvertAlpha();'
        result = transform(code)
        assert "pygame" not in result

    def test_strips_pygame_transform_scale(self):
        code = '            surf = pygame.transform.Scale(surf, (sizePx, sizePx));'
        result = transform(code)
        assert "pygame" not in result


class TestStripSimulatorInternals:
    """Priority 1: Remove LifecycleManager, PhysicsManager, DisplayManager references."""

    def test_strips_lifecycle_manager(self):
        code = "    var lm = LifecycleManager.Instance;\n    lm.RegisterBehaviour(this);"
        result = transform(code)
        assert "LifecycleManager" not in result
        assert "lm." not in result

    def test_strips_physics_manager(self):
        code = "    PhysicsManager.Instance.Step(dt);\n    int x = 5;"
        result = transform(code)
        assert "PhysicsManager" not in result
        assert "int x = 5;" in result

    def test_strips_display_manager(self):
        code = "    DisplayManager.Instance.Render();\n    int y = 10;"
        result = transform(code)
        assert "DisplayManager" not in result
        assert "int y = 10;" in result

    def test_strips_app_run(self):
        code = "app.run();\nDebug.Log(\"done\");"
        result = transform(code)
        assert "app.run" not in result
        assert "Debug.Log" in result


class TestRewriteTypeHints:
    """Priority 2: Fix Python type annotations that leaked into C#."""

    def test_strips_nullable_reference_type(self):
        code = "    public GameManager? instance;"
        result = transform(code)
        assert "GameManager?" not in result
        assert "GameManager instance" in result

    def test_preserves_nullable_value_type(self):
        code = "    public int? sizePx;"
        result = transform(code)
        assert "int?" in result

    def test_strips_nullable_on_custom_types(self):
        code = "    public SpriteRenderer? BodySr = null;\n    public AnimatedSprite? BodyAnim = null;"
        result = transform(code)
        assert "SpriteRenderer?" not in result
        assert "AnimatedSprite?" not in result
        assert "SpriteRenderer BodySr" in result
        assert "AnimatedSprite BodyAnim" in result

    def test_rewrites_not_in_operator(self):
        """C# has no '!in' operator — should become !collection.Contains(item)."""
        code = "        if (pellet !in AllPellets)"
        result = transform(code)
        assert "!in" not in result
        assert "!AllPellets.Contains(pellet)" in result

    def test_strips_pygame_surface_nullable(self):
        code = "    public pygame.Surface? blueSprite = null;"
        result = transform(code)
        assert "pygame" not in result
        assert "Sprite" in result


class TestConstructorComments:
    """Priority 3: Annotate new GameObject() calls."""

    def test_adds_comment_to_new_gameobject(self):
        code = '        GameObject canvasGo = new GameObject("UICanvas");'
        result = transform(code)
        assert "// TODO: wire via Inspector or Instantiate" in result

    def test_preserves_gameobject_find(self):
        code = '        var go = GameObject.Find("Player");'
        result = transform(code)
        assert 'GameObject.Find("Player")' in result


class TestSingletonAnnotation:
    """Priority 4: Detect and annotate singleton pattern."""

    def test_annotates_singleton_instance(self):
        code = "    public static GameManager instance;"
        result = transform(code)
        assert "Singleton" in result

    def test_no_annotation_on_non_static(self):
        code = "    public GameManager instance;"
        result = transform(code)
        assert "Singleton" not in result


class TestPassthrough:
    """Valid Unity C# should pass through unchanged (modulo whitespace)."""

    def test_valid_unity_code_unchanged(self):
        code = """\
using UnityEngine;
public class Player : MonoBehaviour
{
    public float speed = 5f;
    void Update()
    {
        transform.Translate(Vector3.right * speed * Time.deltaTime);
    }
}"""
        result = transform(code)
        assert result.strip() == code.strip()

    def test_empty_string(self):
        assert transform("") == ""


class TestOnRealOutput:
    """Test against actual translated output from the Breakout project."""

    def test_breakout_gamemanager(self):
        """The Breakout GameManager.cs should have new GameObject() annotated."""
        from pathlib import Path
        cs_path = Path("data/generated/breakout_project/Assets/_Project/Scripts/GameManager.cs")
        if not cs_path.exists():
            pytest.skip("Breakout output not available")
        code = cs_path.read_text()
        result = transform(code)
        # Should annotate new GameObject calls
        assert "// TODO: wire via Inspector or Instantiate" in result
        # Should strip nullable reference types (GameManager?)
        assert "GameManager?" not in result

    def test_pacman_gamemanager(self):
        """Pacman GameManager.cs should have pygame stripped."""
        from pathlib import Path
        cs_path = Path("data/generated/pacman_v2_cs/GameManager.cs")
        if not cs_path.exists():
            pytest.skip("Pacman output not available")
        code = cs_path.read_text()
        result = transform(code)
        assert "pygame" not in result
        assert "!in" not in result

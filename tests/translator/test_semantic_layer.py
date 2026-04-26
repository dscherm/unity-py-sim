"""Tests for semantic_layer — post-processor that strips simulator artifacts from translated C#."""

import pytest

from src.translator.semantic_layer import transform, rewrite_singleton_access


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


class TestRewriteSingletonAccess:
    """S2-3: singleton access rewrite to [SerializeField] private reference."""

    def test_injects_serialized_field_into_consumer(self):
        cs = (
            "using UnityEngine;\n"
            "public class Enemy\n"
            "{\n"
            "    public void OnKill()\n"
            "    {\n"
            "        GameManager.Instance.score += 10;\n"
            "    }\n"
            "}\n"
        )
        out = rewrite_singleton_access(
            cs, singletons={"GameManager"}, current_classes={"Enemy"}
        )
        assert "[SerializeField] private GameManager gameManager;" in out
        # Call sites rewritten to the field reference.
        assert "gameManager.score += 10;" in out
        # Singleton access in method bodies (other than Awake) is gone.
        call_site_pos = out.index("gameManager.score += 10;")
        # Ensure no literal `GameManager.Instance.` appears at call sites.
        assert "GameManager.Instance." not in out[:call_site_pos + 30]

    def test_injects_awake_fallback_for_runtime_self_wiring(self):
        """data/lessons/flappy_bird_deploy.md gap 2: the injected
        [SerializeField] must have a self-wire fallback in Awake, else
        scenes without Inspector-wired singleton refs NPE at runtime.
        """
        cs = (
            "using UnityEngine;\n"
            "public class Enemy\n"
            "{\n"
            "    public void OnKill()\n"
            "    {\n"
            "        GameManager.Instance.score += 10;\n"
            "    }\n"
            "}\n"
        )
        out = rewrite_singleton_access(
            cs, singletons={"GameManager"}, current_classes={"Enemy"}
        )
        assert "void Awake()" in out
        assert "if (gameManager == null) gameManager = FindObjectOfType<GameManager>();" in out

    def test_awake_fallback_merged_into_existing_awake(self):
        """Don't overwrite a class's existing Awake — prepend into it."""
        cs = (
            "using UnityEngine;\n"
            "public class Enemy\n"
            "{\n"
            "    void Awake()\n"
            "    {\n"
            "        Debug.Log(\"existing awake body\");\n"
            "    }\n"
            "    public void OnKill()\n"
            "    {\n"
            "        GameManager.Instance.score += 10;\n"
            "    }\n"
            "}\n"
        )
        out = rewrite_singleton_access(
            cs, singletons={"GameManager"}, current_classes={"Enemy"}
        )
        # Only one Awake in the output — the existing one was extended.
        assert out.count("void Awake()") == 1
        # The original body is preserved.
        assert 'Debug.Log("existing awake body")' in out
        # And the self-wire line is inside (before or after) the existing body.
        assert "if (gameManager == null) gameManager = FindObjectOfType<GameManager>();" in out

    def test_does_not_rewrite_singleton_in_its_own_file(self):
        cs = (
            "using UnityEngine;\n"
            "public class GameManager\n"
            "{\n"
            "    public static GameManager Instance;\n"
            "    public void SomeMethod()\n"
            "    {\n"
            "        GameManager.Instance = this;\n"
            "    }\n"
            "}\n"
        )
        out = rewrite_singleton_access(
            cs, singletons={"GameManager"}, current_classes={"GameManager"}
        )
        # Must leave the singleton's own body untouched so init still works
        assert "[SerializeField] private GameManager" not in out
        assert "GameManager.Instance = this;" in out

    def test_reuses_existing_serialized_field_name(self):
        cs = (
            "using UnityEngine;\n"
            "public class Enemy\n"
            "{\n"
            "    [SerializeField] private GameManager gm;\n"
            "    public void OnKill()\n"
            "    {\n"
            "        GameManager.Instance.score += 10;\n"
            "    }\n"
            "}\n"
        )
        out = rewrite_singleton_access(
            cs, singletons={"GameManager"}, current_classes={"Enemy"}
        )
        # Should reuse `gm`, not inject a second field
        assert out.count("private GameManager") == 1
        assert "gm.score += 10;" in out

    def test_multiple_consumer_classes_each_get_own_field(self):
        cs = (
            "using UnityEngine;\n"
            "public class Enemy\n"
            "{\n"
            "    public void Hit() { GameManager.Instance.lives -= 1; }\n"
            "}\n"
            "public class Powerup\n"
            "{\n"
            "    public void Apply() { GameManager.Instance.score += 50; }\n"
            "}\n"
        )
        out = rewrite_singleton_access(
            cs, singletons={"GameManager"}, current_classes={"Enemy", "Powerup"}
        )
        # Both classes must get their own field
        assert out.count("[SerializeField] private GameManager gameManager;") == 2
        assert "gameManager.lives -= 1" in out
        assert "gameManager.score += 50" in out

    def test_unrelated_classes_untouched(self):
        """Singleton rewrite must not touch classes that don't reference the singleton."""
        cs = (
            "using UnityEngine;\n"
            "public class Bystander\n"
            "{\n"
            "    public void DoNothing() { var x = 1; }\n"
            "}\n"
        )
        out = rewrite_singleton_access(
            cs, singletons={"GameManager"}, current_classes={"Bystander"}
        )
        assert "[SerializeField]" not in out
        assert "var x = 1;" in out

    def test_transform_accepts_and_threads_singletons_kwarg(self):
        """Backward-compat: transform() without kwargs still works; with kwargs, rewrites happen."""
        cs = (
            "using UnityEngine;\n"
            "public class Enemy\n"
            "{\n"
            "    public void OnKill() { GameManager.Instance.score += 10; }\n"
            "}\n"
        )
        # No kwargs → no singleton rewrite
        out_plain = transform(cs)
        assert "[SerializeField]" not in out_plain
        # With kwargs → singleton rewrite fires
        out_with = transform(
            cs, singletons={"GameManager"}, current_classes={"Enemy"}
        )
        assert "[SerializeField] private GameManager gameManager;" in out_with
        assert "gameManager.score += 10" in out_with

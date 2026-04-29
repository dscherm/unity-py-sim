"""Default-sprite fallback for SpriteRenderers without an asset mapping.

Surfaced 2026-04-29 when Pong deployed cleanly under home_machine but the
local Editor view showed an empty playfield. The Python sim renders
paddles + ball as colored pygame rects (no source PNG), so the scene
serializer emits SpriteRenderer components with `color` but no
`asset_ref`. Unity's SpriteRenderer with `sprite=null` renders nothing
even when `color` and `size` are set — see line 619+ in
src/exporter/coplay_generator.py for the original color-only fallback.

The scaffolder ALWAYS copies `Assets/Art/Sprites/Circle.png` and
`WhiteSquare.png` into every generated project. The durable fix is to
fall back to one of these when no `asset_ref` mapping exists, choosing
based on sibling-collider shape:
  * CircleCollider2D sibling → Circle.png
  * BoxCollider2D / no collider → WhiteSquare.png

The color is then applied as a tint on top of the white sprite, so the
existing color-tint flow is preserved.
"""

from __future__ import annotations

from src.exporter.coplay_generator import generate_scene_script


def _scene_with_one_object(name: str, components: list[dict]) -> dict:
    """Wrap component list in a minimal scene_data shape."""
    return {
        "game_objects": [
            {
                "name": name,
                "tag": "Untagged",
                "layer": 0,
                "active": True,
                "components": [
                    {
                        "type": "Transform",
                        "position": [0.0, 0.0, 0.0],
                        "rotation": [0.0, 0.0, 0.0, 1.0],
                        "local_scale": [1.0, 1.0, 1.0],
                    },
                    *components,
                ],
                "children": [],
            }
        ]
    }


class TestSpriteRendererDefaultFallback:
    def test_circle_collider_sibling_gets_circle_default(self):
        """SpriteRenderer + CircleCollider2D + no asset_ref → load Circle.png."""
        scene = _scene_with_one_object(
            "Ball",
            [
                {"type": "CircleCollider2D", "radius": 0.25},
                {"type": "SpriteRenderer", "color": [255, 255, 0, 255], "sorting_order": 0},
            ],
        )
        cs = generate_scene_script(scene)
        assert "Assets/Art/Sprites/Circle.png" in cs, (
            f"Ball with CircleCollider2D missing Circle.png fallback:\n{cs}"
        )
        # Color tint still applied on top of the white sprite (yellow)
        assert "1.000f, 1.000f, 0.000f" in cs or "1f, 1f, 0f" in cs

    def test_box_collider_sibling_gets_white_square_default(self):
        """SpriteRenderer + BoxCollider2D + no asset_ref → load WhiteSquare.png."""
        scene = _scene_with_one_object(
            "Paddle",
            [
                {"type": "BoxCollider2D", "size": [0.5, 2.0]},
                {"type": "SpriteRenderer", "color": [100, 180, 255, 255], "sorting_order": 0},
            ],
        )
        cs = generate_scene_script(scene)
        assert "Assets/Art/Sprites/WhiteSquare.png" in cs, (
            f"Paddle with BoxCollider2D missing WhiteSquare.png fallback:\n{cs}"
        )
        # And NOT the circle fallback
        assert "Circle.png" not in cs

    def test_no_collider_gets_white_square_default(self):
        """SpriteRenderer alone (no collider) → WhiteSquare.png (the safer
        default for arbitrary scene props like CenterLine)."""
        scene = _scene_with_one_object(
            "CenterLine",
            [{"type": "SpriteRenderer", "color": [128, 128, 128, 255], "sorting_order": 0}],
        )
        cs = generate_scene_script(scene)
        assert "Assets/Art/Sprites/WhiteSquare.png" in cs

    def test_explicit_asset_ref_still_wins(self):
        """Regression guard: when a sprite mapping IS provided, the explicit
        asset_ref must win over the fallback."""
        scene = _scene_with_one_object(
            "Bird",
            [
                {"type": "CircleCollider2D", "radius": 0.5},
                {
                    "type": "SpriteRenderer",
                    "asset_ref": "bird_01",
                    "color": [255, 255, 255, 255],
                    "sorting_order": 1,
                },
            ],
        )
        mapping = {
            "sprites": {
                "bird_01": {
                    "unity_path": "Assets/Art/Sprites/Bird_01.png",
                    "ppu": 32,
                }
            }
        }
        cs = generate_scene_script(scene, mapping)
        # Explicit Bird_01 mapping is wired; do NOT fall back to Circle.png.
        assert "sprite_bird_01" in cs
        # The fallback assignment should NOT appear (explicit mapping wins).
        assert ".sprite = sprite_bird_01" in cs
        # Colored fallback also must NOT appear when an explicit ref is used.
        # (The pre-existing logic suppressed color-only emission when asset_ref
        # is mapped; the new fallback must do the same.)
        assert "AssetDatabase.LoadAssetAtPath<Sprite>(\"Assets/Art/Sprites/Circle.png\")" not in cs

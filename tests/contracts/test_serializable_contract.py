"""Contract tests for @serializable decorator.

Validates the behavioral contract of @serializable against Unity's
[System.Serializable] attribute semantics:
- Marks classes for serialization
- Works with dataclasses
- Auto-wraps plain classes with @dataclass
"""

import sys
import os
import dataclasses

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from src.engine.serialization import serializable


class TestSerializableDecorator:
    """Contract: @serializable sets _unity_serializable = True."""

    def test_sets_unity_serializable_flag(self):
        """@serializable must set _unity_serializable = True on the class."""

        @serializable
        @dataclasses.dataclass
        class Foo:
            x: int = 0

        assert hasattr(Foo, "_unity_serializable")
        assert Foo._unity_serializable is True

    def test_works_on_already_decorated_dataclass(self):
        """@serializable applied to an existing @dataclass preserves dataclass behavior."""

        @serializable
        @dataclasses.dataclass
        class Bar:
            name: str = "test"
            value: float = 1.5

        assert dataclasses.is_dataclass(Bar)
        b = Bar(name="hello", value=3.0)
        assert b.name == "hello"
        assert b.value == 3.0

    def test_auto_wraps_plain_class_with_dataclass(self):
        """@serializable on a plain class (not a dataclass) should auto-apply @dataclass."""

        @serializable
        class Plain:
            x: int = 5
            y: str = "hi"

        assert dataclasses.is_dataclass(Plain)
        assert Plain._unity_serializable is True
        p = Plain()
        assert p.x == 5
        assert p.y == "hi"

    def test_preserves_field_types(self):
        """Fields on a @serializable class retain their annotated types."""

        @serializable
        @dataclasses.dataclass
        class Typed:
            count: int = 0
            label: str = ""
            values: list = dataclasses.field(default_factory=list)

        t = Typed(count=42, label="test", values=[1, 2, 3])
        assert isinstance(t.count, int)
        assert isinstance(t.label, str)
        assert isinstance(t.values, list)

    def test_multiple_instances_independent(self):
        """Each instance of a @serializable class has independent field values."""

        @serializable
        @dataclasses.dataclass
        class Config:
            score: int = 0

        a = Config(score=10)
        b = Config(score=20)
        assert a.score == 10
        assert b.score == 20
        a.score = 99
        assert b.score == 20


class TestInvaderRowConfigContract:
    """Contract: InvaderRowConfig has correct field types and defaults."""

    def test_has_animation_sprites_field(self):
        from examples.space_invaders.space_invaders_python.invaders import InvaderRowConfig

        fields = {f.name: f for f in dataclasses.fields(InvaderRowConfig)}
        assert "animation_sprites" in fields

    def test_has_score_field_with_default_10(self):
        from examples.space_invaders.space_invaders_python.invaders import InvaderRowConfig

        fields = {f.name: f for f in dataclasses.fields(InvaderRowConfig)}
        assert "score" in fields
        assert fields["score"].default == 10

    def test_is_dataclass(self):
        from examples.space_invaders.space_invaders_python.invaders import InvaderRowConfig

        assert dataclasses.is_dataclass(InvaderRowConfig)

    def test_is_unity_serializable(self):
        from examples.space_invaders.space_invaders_python.invaders import InvaderRowConfig

        assert InvaderRowConfig._unity_serializable is True


class TestPowerupConfigContract:
    """Contract: PowerupConfig has correct field types."""

    def test_has_powerup_type_field(self):
        from examples.breakout.breakout_python.powerup import PowerupConfig

        fields = {f.name: f for f in dataclasses.fields(PowerupConfig)}
        assert "powerup_type" in fields

    def test_has_color_field(self):
        from examples.breakout.breakout_python.powerup import PowerupConfig

        fields = {f.name: f for f in dataclasses.fields(PowerupConfig)}
        assert "color" in fields

    def test_has_weight_field(self):
        from examples.breakout.breakout_python.powerup import PowerupConfig

        fields = {f.name: f for f in dataclasses.fields(PowerupConfig)}
        assert "weight" in fields

    def test_is_dataclass(self):
        from examples.breakout.breakout_python.powerup import PowerupConfig

        assert dataclasses.is_dataclass(PowerupConfig)

    def test_is_unity_serializable(self):
        from examples.breakout.breakout_python.powerup import PowerupConfig

        assert PowerupConfig._unity_serializable is True


class TestPowerupTypeContract:
    """Contract: PowerupType is an Enum with expected members."""

    def test_is_enum(self):
        from enum import Enum
        from examples.breakout.breakout_python.powerup import PowerupType

        assert issubclass(PowerupType, Enum)

    def test_has_expected_members(self):
        from examples.breakout.breakout_python.powerup import PowerupType

        assert hasattr(PowerupType, "WIDE_PADDLE")
        assert hasattr(PowerupType, "EXTRA_LIFE")
        assert hasattr(PowerupType, "SPEED_BALL")

    def test_members_have_string_values(self):
        from examples.breakout.breakout_python.powerup import PowerupType

        for member in PowerupType:
            assert isinstance(member.value, str)

"""Serialization utilities — @serializable decorator for Unity-compatible data classes.

In Unity, [System.Serializable] marks a class as serializable so it can appear
in the inspector and be saved to scenes. This decorator marks Python dataclasses
for the translator to emit [System.Serializable] on the C# side.

Usage:
    @serializable
    @dataclass
    class InvaderRowConfig:
        animation_sprites: list[tuple[int, int, int]]
        score: int = 10

Translator emits:
    [System.Serializable]
    public class InvaderRowConfig {
        public Color[] animationSprites;
        public int score = 10;
    }
"""

from __future__ import annotations

import dataclasses


def serializable(cls):
    """Mark a dataclass as [System.Serializable] for C# translation.

    If the class isn't already a dataclass, wraps it with @dataclass.
    Sets cls._unity_serializable = True for the translator to detect.
    """
    if not dataclasses.is_dataclass(cls):
        cls = dataclasses.dataclass(cls)
    cls._unity_serializable = True
    return cls

from __future__ import annotations
"""Spawner — Flappy Bird pipe spawner.

Line-by-line translation of Spawner.cs from zigurous/unity-flappy-bird-tutorial.
"""

from src.engine.core import MonoBehaviour, GameObject
from src.engine.math.vector import Vector3
from src.engine.math.quaternion import Quaternion
from src.engine.random import Random


class Spawner(MonoBehaviour):

    def __init__(self) -> None:
        super().__init__()
        self.prefab: GameObject | None = None   # public Pipes prefab
        self.spawn_rate: float = 1.0
        self.min_height: float = -1.0
        self.max_height: float = 2.0
        self.vertical_gap: float = 3.0

    def on_enable(self) -> None:
        self.invoke_repeating("spawn", self.spawn_rate, self.spawn_rate)

    def on_disable(self) -> None:
        self.cancel_invoke("spawn")

    def spawn(self) -> None:
        if self.prefab is None:
            return
        pipes_go = GameObject.instantiate(self.prefab, self.transform.position, Quaternion.identity)
        pipes_go.transform.position = pipes_go.transform.position + Vector3.up * Random.range(self.min_height, self.max_height)
        # Wire child Transform references on the Pipes component
        from examples.flappy_bird.flappy_bird_python.pipes import Pipes
        pipes_comp = pipes_go.get_component(Pipes)
        if pipes_comp is not None:
            pipes_comp.gap = self.vertical_gap
            # Find Top and Bottom children by name
            for child in pipes_go.transform.children:
                if child.game_object.name == "Top":
                    pipes_comp.top = child
                elif child.game_object.name == "Bottom":
                    pipes_comp.bottom = child

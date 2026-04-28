from src.engine.core import MonoBehaviour, WaitForSeconds
from typing import Iterator
class Spawner(MonoBehaviour):
    def spawn_loop(self) -> Iterator:
        yield WaitForSeconds(2.0)

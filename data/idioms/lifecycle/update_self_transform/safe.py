from src.engine.core import MonoBehaviour
from src.engine.math.vector import Vector3
class Mover(MonoBehaviour):
    def update(self):
        self.transform.position += Vector3(1.0, 0.0, 0.0)

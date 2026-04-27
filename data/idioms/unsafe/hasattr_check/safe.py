from src.engine.core import GameObject
class Probe:
    target: GameObject
    def safe_get(self):
        if self.target is not None:
            return self.target
        return None

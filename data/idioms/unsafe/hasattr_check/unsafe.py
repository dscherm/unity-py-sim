from src.engine.core import GameObject
class Probe:
    target: GameObject
    def safe_get(self):
        return self.target if hasattr(self, 'target') else None

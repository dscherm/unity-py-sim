from src.engine.core import MonoBehaviour
from src.engine.input_system import Input
class Player(MonoBehaviour):
    def update(self):
        if Input.get_key_down('space'):
            pass

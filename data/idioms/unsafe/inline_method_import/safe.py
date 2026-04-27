from src.engine.core import GameObject
class Loader:
    def find_player(self):
        return GameObject.find('Player')

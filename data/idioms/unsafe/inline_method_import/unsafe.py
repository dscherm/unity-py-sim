class Loader:
    def find_player(self):
        from src.engine.core import GameObject
        return GameObject.find('Player')

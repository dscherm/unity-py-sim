class Health:
    hp: int = 100
    def take_damage(self, dmg: int) -> None:
        self.hp -= dmg

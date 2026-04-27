class Score:
    points: int = 0
    def label(self) -> str:
        return 'Score: ' + str(self.points)

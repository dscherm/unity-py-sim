"""Score manager — Python equivalent of ScoreManager.cs"""

from src.engine.core import MonoBehaviour


class ScoreManager(MonoBehaviour):

    score_left: int = 0
    score_right: int = 0
    win_score: int = 5

    @staticmethod
    def add_score_left():
        ScoreManager.score_left += 1
        ScoreManager._check_win()

    @staticmethod
    def add_score_right():
        ScoreManager.score_right += 1
        ScoreManager._check_win()

    @staticmethod
    def reset_scores():
        ScoreManager.score_left = 0
        ScoreManager.score_right = 0

    @staticmethod
    def _check_win():
        if ScoreManager.score_left >= ScoreManager.win_score:
            print("Left Player Wins!")
        elif ScoreManager.score_right >= ScoreManager.win_score:
            print("Right Player Wins!")

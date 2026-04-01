"""Game manager — tracks score, lives, and game state."""

from src.engine.core import MonoBehaviour, GameObject


class GameManager(MonoBehaviour):

    score: int = 0
    lives: int = 3
    game_over: bool = False
    game_won: bool = False

    @staticmethod
    def reset():
        GameManager.score = 0
        GameManager.lives = 3
        GameManager.game_over = False
        GameManager.game_won = False

    @staticmethod
    def add_score(points: int):
        GameManager.score += points
        GameManager._update_display()

    @staticmethod
    def on_ball_lost():
        if GameManager.game_over or GameManager.game_won:
            return
        GameManager.lives -= 1
        if GameManager.lives <= 0:
            GameManager.game_over = True
            print("Game Over!")
        GameManager._update_display()

    @staticmethod
    def on_brick_destroyed():
        # Check win condition — count remaining bricks
        remaining = 0
        for go in list(GameObject._registry.values()):
            if go.tag == "Brick" and go.active:
                remaining += 1
        if remaining <= 0:
            GameManager.game_won = True
            print("You Win!")

    @staticmethod
    def _update_display():
        try:
            import pygame
            pygame.display.set_caption(
                f"Breakout — Score: {GameManager.score}  |  Lives: {GameManager.lives}  "
                f"(A/D move, Space launch, ESC quit)"
            )
        except Exception:
            pass

"""Game state enums matching the reference Angry Birds implementation."""

from enum import Enum


class SlingshotState(Enum):
    IDLE = "idle"
    USER_PULLING = "user_pulling"
    BIRD_FLYING = "bird_flying"


class GameState(Enum):
    START = "start"
    BIRD_MOVING_TO_SLINGSHOT = "bird_moving"
    PLAYING = "playing"
    WON = "won"
    LOST = "lost"


class BirdState(Enum):
    BEFORE_THROWN = "before_thrown"
    THROWN = "thrown"

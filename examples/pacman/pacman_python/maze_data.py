"""Maze data — classic Pacman maze layout.

28 columns x 31 rows. Origin at bottom-left.
Legend:
  W = wall
  . = pellet (path)
  o = power pellet
  - = empty path (no pellet, e.g. ghost house entrance)
  G = ghost house interior
  P = pacman start
  N = node (intersection) with pellet
  n = node (intersection) without pellet
  T = tunnel passage
  X = ghost house gate (one-way door)
"""

# Classic Pacman maze, row 0 = top of screen
MAZE: list[str] = [
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWW",  # row 0
    "W............WW............W",  # row 1
    "W.WWWW.WWWWW.WW.WWWWW.WWWW.W",  # row 2
    "WoWWWW.WWWWW.WW.WWWWW.WWWWoW",  # row 3
    "W.WWWW.WWWWW.WW.WWWWW.WWWW.W",  # row 4
    "W..........................W",  # row 5
    "W.WWWW.WW.WWWWWWWW.WW.WWWW.W",  # row 6
    "W.WWWW.WW.WWWWWWWW.WW.WWWW.W",  # row 7
    "W......WW....WW....WW......W",  # row 8
    "WWWWWW.WWWWW-WW-WWWWW.WWWWWW",  # row 9
    "WWWWWW.WWWWW-WW-WWWWW.WWWWWW",  # row 10
    "WWWWWW.WW----------WW.WWWWWW",  # row 11
    "WWWWWW.WW-WWW--WWW-WW.WWWWWW",  # row 12
    "WWWWWW.WW-WGGGGGGW-WW.WWWWWW",  # row 13
    "T------.--WGGGGGGW--.------T",  # row 14
    "WWWWWW.WW-WGGGGGGW-WW.WWWWWW",  # row 15
    "WWWWWW.WW-WWWWWWWW-WW.WWWWWW",  # row 16
    "WWWWWW.WW----------WW.WWWWWW",  # row 17
    "WWWWWW.WW-WWWWWWWW-WW.WWWWWW",  # row 18
    "WWWWWW.WW-WWWWWWWW-WW.WWWWWW",  # row 19
    "W............WW............W",  # row 20
    "W.WWWW.WWWWW.WW.WWWWW.WWWW.W",  # row 21
    "W.WWWW.WWWWW.WW.WWWWW.WWWW.W",  # row 22
    "Wo..WW.......P........WW..oW",  # row 23
    "WWW.WW.WW.WWWWWWWW.WW.WW.WWW",  # row 24
    "WWW.WW.WW.WWWWWWWW.WW.WW.WWW",  # row 25
    "W......WW....WW....WW......W",  # row 26
    "W.WWWWWWWWWW.WW.WWWWWWWWWW.W",  # row 27
    "W.WWWWWWWWWW.WW.WWWWWWWWWW.W",  # row 28
    "W..........................W",  # row 29
    "WWWWWWWWWWWWWWWWWWWWWWWWWWWW",  # row 30
]

MAZE_ROWS: int = len(MAZE)
MAZE_COLS: int = len(MAZE[0])

# Offset so maze is centered at world origin
MAZE_OFFSET_X: float = -MAZE_COLS / 2.0 + 0.5
MAZE_OFFSET_Y: float = MAZE_ROWS / 2.0 - 0.5


def cell_to_world(col: int, row: int) -> tuple[float, float]:
    """Convert maze grid coordinates to world position."""
    x = col + MAZE_OFFSET_X
    y = -row + MAZE_OFFSET_Y  # row 0 = top
    return (x, y)


def get_cell(col: int, row: int) -> str:
    """Get the cell type at a grid position."""
    if 0 <= row < MAZE_ROWS and 0 <= col < MAZE_COLS:
        return MAZE[row][col]
    return "W"


def is_intersection(col: int, row: int) -> bool:
    """Check if a path cell is a decision point where ghosts need to pick a direction.

    Returns True for T-junctions (3+), crossroads (4), AND corners (2 non-opposite).
    Straight corridors (2 opposite) return False — no decision needed.
    """
    if get_cell(col, row) == "W":
        return False
    open = []
    for dc, dr in [(0, -1), (0, 1), (-1, 0), (1, 0)]:
        if get_cell(col + dc, row + dr) != "W":
            open.append((dc, dr))
    if len(open) >= 3:
        return True
    if len(open) == 2:
        # Corner: two directions that aren't opposite (e.g. up+right, not up+down)
        (dc1, dr1), (dc2, dr2) = open
        if dc1 != -dc2 or dr1 != -dr2:
            return True
    return False

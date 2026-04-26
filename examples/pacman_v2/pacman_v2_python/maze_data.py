"""Maze data — classic Pacman maze layout for V2 (zigurous tutorial port).

28 columns x 31 rows. Origin at bottom-left.
Each wall cell maps to a Wall_XX.png tile index from the zigurous sprite sheet.

Legend:
  W = wall (tile index assigned by wall_tiles map)
  . = pellet (path)
  o = power pellet
  - = empty path (no pellet)
  G = ghost house interior
  P = pacman start
  T = tunnel passage
  X = ghost house gate
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

MAZE_OFFSET_X: float = -MAZE_COLS / 2.0 + 0.5
MAZE_OFFSET_Y: float = MAZE_ROWS / 2.0 - 0.5


def cell_to_world(col: int, row: int) -> tuple[float, float]:
    """Convert maze grid coordinates to world position."""
    x = col + MAZE_OFFSET_X
    y = -row + MAZE_OFFSET_Y
    return (x, y)


def get_cell(col: int, row: int) -> str:
    """Get the cell type at a grid position."""
    if 0 <= row < MAZE_ROWS and 0 <= col < MAZE_COLS:
        return MAZE[row][col]
    return "W"


def is_wall(col: int, row: int) -> bool:
    """Check if a cell is a wall (including ghost house walls)."""
    c = get_cell(col, row)
    return c == "W" or c == "X"


def neighbor_walls(col: int, row: int) -> dict[str, bool]:
    """Get which neighboring cells are walls. Used for wall tile selection."""
    return {
        "up": is_wall(col, row - 1),
        "down": is_wall(col, row + 1),
        "left": is_wall(col - 1, row),
        "right": is_wall(col + 1, row),
        "up_left": is_wall(col - 1, row - 1),
        "up_right": is_wall(col + 1, row - 1),
        "down_left": is_wall(col - 1, row + 1),
        "down_right": is_wall(col + 1, row + 1),
    }


def select_wall_tile(col: int, row: int) -> int:
    """Select the appropriate Wall_XX tile index based on neighboring walls.

    The zigurous tutorial uses 38 wall tile sprites (Wall_00 through Wall_37)
    for different wall configurations (straight, corner, T-junction, etc.).

    This uses a simplified mapping based on neighbor patterns. The exact mapping
    will be refined during playtesting to match the original maze appearance.
    """
    n = neighbor_walls(col, row)
    up, down, left, right = n["up"], n["down"], n["left"], n["right"]

    # Count adjacent walls
    adj = sum([up, down, left, right])

    if adj == 4:
        # Fully surrounded — interior fill
        return 0
    elif adj == 3:
        # T-junction or dead-end cap (3 walls, 1 open)
        if not up:
            return 1
        if not down:
            return 2
        if not left:
            return 3
        if not right:
            return 4
    elif adj == 2:
        # Straight wall or corner
        if up and down:
            return 5  # vertical straight
        if left and right:
            return 6  # horizontal straight
        if down and right:
            return 7  # corner: top-left
        if down and left:
            return 8  # corner: top-right
        if up and right:
            return 9  # corner: bottom-left
        if up and left:
            return 10  # corner: bottom-right
    elif adj == 1:
        # End cap
        if up:
            return 11
        if down:
            return 12
        if left:
            return 13
        if right:
            return 14
    elif adj == 0:
        # Isolated wall
        return 15

    return 0  # fallback

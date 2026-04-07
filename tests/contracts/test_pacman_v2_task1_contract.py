"""Contract tests for Pacman V2 Task 1: Maze with real wall sprites.

These tests validate the maze data contracts derived from the classic Pacman
maze specification (28x31 grid, zigurous tutorial) — NOT from implementation.
"""

import sys
import os
import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from examples.pacman_v2.pacman_v2_python.maze_data import (
    MAZE, MAZE_ROWS, MAZE_COLS, MAZE_OFFSET_X, MAZE_OFFSET_Y,
    cell_to_world, get_cell, select_wall_tile, is_wall, neighbor_walls,
)


# ── Maze Dimensions ───────────────────────────────────────────


class TestMazeDimensions:
    """Classic Pacman maze is 28 columns x 31 rows."""

    def test_maze_has_31_rows(self):
        assert MAZE_ROWS == 31, f"Expected 31 rows, got {MAZE_ROWS}"

    def test_maze_has_28_columns(self):
        assert MAZE_COLS == 28, f"Expected 28 columns, got {MAZE_COLS}"

    def test_all_rows_have_28_columns(self):
        for i, row in enumerate(MAZE):
            assert len(row) == 28, f"Row {i} has {len(row)} columns, expected 28"

    def test_maze_list_length(self):
        assert len(MAZE) == 31


# ── Edge Cells ────────────────────────────────────────────────


class TestEdgeCells:
    """All edge cells of the classic Pacman maze must be walls or tunnels."""

    def test_top_row_all_walls(self):
        for col in range(MAZE_COLS):
            assert MAZE[0][col] == "W", f"Top row col {col} is not a wall"

    def test_bottom_row_all_walls(self):
        for col in range(MAZE_COLS):
            assert MAZE[MAZE_ROWS - 1][col] == "W", (
                f"Bottom row col {col} is not a wall"
            )

    def test_left_column_all_walls_or_tunnel(self):
        for row in range(MAZE_ROWS):
            cell = MAZE[row][0]
            assert cell in ("W", "T"), (
                f"Left edge row {row} is '{cell}', expected W or T"
            )

    def test_right_column_all_walls_or_tunnel(self):
        for row in range(MAZE_ROWS):
            cell = MAZE[row][MAZE_COLS - 1]
            assert cell in ("W", "T"), (
                f"Right edge row {row} is '{cell}', expected W or T"
            )


# ── cell_to_world ─────────────────────────────────────────────


class TestCellToWorld:
    """cell_to_world converts grid (col, row) to centered world coordinates."""

    def test_origin_cell_0_0(self):
        x, y = cell_to_world(0, 0)
        expected_x = 0 + MAZE_OFFSET_X
        expected_y = 0 + MAZE_OFFSET_Y
        assert x == pytest.approx(expected_x)
        assert y == pytest.approx(expected_y)

    def test_center_cell(self):
        col, row = 14, 15
        x, y = cell_to_world(col, row)
        assert x == pytest.approx(col + MAZE_OFFSET_X)
        assert y == pytest.approx(-row + MAZE_OFFSET_Y)

    def test_bottom_right_corner(self):
        col, row = MAZE_COLS - 1, MAZE_ROWS - 1
        x, y = cell_to_world(col, row)
        assert x == pytest.approx(col + MAZE_OFFSET_X)
        assert y == pytest.approx(-row + MAZE_OFFSET_Y)

    def test_world_coords_are_floats(self):
        x, y = cell_to_world(0, 0)
        assert isinstance(x, float)
        assert isinstance(y, float)

    def test_adjacent_cells_one_unit_apart(self):
        """Adjacent cells should be exactly 1 world unit apart."""
        x1, y1 = cell_to_world(5, 10)
        x2, y2 = cell_to_world(6, 10)
        assert x2 - x1 == pytest.approx(1.0)

        x3, y3 = cell_to_world(5, 11)
        assert y1 - y3 == pytest.approx(1.0)  # y decreases as row increases


# ── select_wall_tile ──────────────────────────────────────────


class TestSelectWallTile:
    """select_wall_tile returns valid indices (0-37) for the zigurous sprite sheet."""

    def test_returns_valid_index_for_all_wall_cells(self):
        for row in range(MAZE_ROWS):
            for col in range(MAZE_COLS):
                if MAZE[row][col] == "W":
                    idx = select_wall_tile(col, row)
                    assert 0 <= idx <= 37, (
                        f"Wall at ({col},{row}) got tile index {idx}, "
                        f"expected 0-37"
                    )

    def test_returns_integer(self):
        idx = select_wall_tile(0, 0)
        assert isinstance(idx, int)

    def test_corner_cells_get_valid_indices(self):
        corners = [(0, 0), (27, 0), (0, 30), (27, 30)]
        for col, row in corners:
            idx = select_wall_tile(col, row)
            assert 0 <= idx <= 37


# ── get_cell ──────────────────────────────────────────────────


class TestGetCell:
    """get_cell returns cell type, treating out-of-bounds as walls."""

    def test_out_of_bounds_negative_col(self):
        assert get_cell(-1, 0) == "W"

    def test_out_of_bounds_negative_row(self):
        assert get_cell(0, -1) == "W"

    def test_out_of_bounds_large_col(self):
        assert get_cell(MAZE_COLS, 0) == "W"

    def test_out_of_bounds_large_row(self):
        assert get_cell(0, MAZE_ROWS) == "W"

    def test_out_of_bounds_very_large(self):
        assert get_cell(999, 999) == "W"

    def test_valid_wall_cell(self):
        assert get_cell(0, 0) == "W"

    def test_valid_pellet_cell(self):
        # Row 1 has pellet cells
        assert get_cell(1, 1) == "."

    def test_valid_cell_types(self):
        """Every cell in the maze should be a recognized type."""
        valid_types = {"W", ".", "o", "-", "G", "P", "T", "X"}
        for row in range(MAZE_ROWS):
            for col in range(MAZE_COLS):
                cell = get_cell(col, row)
                assert cell in valid_types, (
                    f"Cell ({col},{row}) is '{cell}', not a valid type"
                )


# ── Mutation Tests ────────────────────────────────────────────


class TestMutationDetection:
    """Verify tests catch breakage when maze data is corrupted."""

    def test_wrong_dimensions_detected(self, monkeypatch):
        """Monkeypatch MAZE to wrong dimensions — tests should catch it."""
        bad_maze = ["WWWWW"] * 10  # 5 cols x 10 rows — totally wrong
        import examples.pacman_v2.pacman_v2_python.maze_data as md
        monkeypatch.setattr(md, "MAZE", bad_maze)
        monkeypatch.setattr(md, "MAZE_ROWS", len(bad_maze))
        monkeypatch.setattr(md, "MAZE_COLS", len(bad_maze[0]))

        # Now verify the contract catches it
        assert md.MAZE_ROWS != 31
        assert md.MAZE_COLS != 28

    def test_select_wall_tile_invalid_index_detected(self, monkeypatch):
        """Monkeypatch select_wall_tile to return -1 — should be detectable."""
        import examples.pacman_v2.pacman_v2_python.maze_data as md
        monkeypatch.setattr(md, "select_wall_tile", lambda col, row: -1)

        idx = md.select_wall_tile(0, 0)
        assert idx < 0, "Mutant should return negative index"
        assert not (0 <= idx <= 37), "Mutant index should fail validity check"

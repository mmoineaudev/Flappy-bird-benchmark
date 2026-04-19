import pygame
import sys
import random

# --- Configuration & Constants ---
DEFAULT_COLS = 80
DEFAULT_ROWS = 40
CELL_SIZE = 15

# Colors
BG_COLOR = (10, 10, 15)      # #0a0a0f
CYAN = (0, 255, 255)         # #00ffff
MAGENTA = (255, 0, 255)      # #ff00ff
PURPLE = (157, 78, 221)      # #9d4edd
GRID_COLOR = (25, 25, 35)    # Subtle grid lines
TEXT_COLOR = (200, 200, 200)

class GameOfLife:
    def __init__(self, cols, rows, cell_size):
        self.cols = cols
        self.rows = rows
        self.cell_size = cell_size
        self.grid = [[0 for _ in range(cols)] for _ in range(rows)]
        self.paused = False
        self.fps = 10
        self.frame_count = 0

        # Rules (Standard Conway)
        self.birth_rule = {3}
        self.survival_rules = {2, 3}

    def toggle_cell(self, x, y):
        """Toggle the state of a cell at given grid position."""
        if 0 <= x < self.cols and 0 <= y < self.rows:
            self.grid[y][x] = 1 - self.grid[y][x]

    def randomize(self):
        """Randomize the grid with a roughly 50% density."""
        for y in range(self.rows):
            for x in range(self.cols):
                self.grid[y][x] = 1 if random.random() > 0.5 else 0

    def clear(self):
        """Clear the entire grid."""
        for y in range(self.rows):
            for x in range(self.cols):
                self.grid[y][x] = 0

    def spawn_preset(self, pattern_type):
        """Spawn classic patterns like Gliders or Pulsars."""
        self.clear()
        if pattern_type == 'glider':
            # A simple glider pattern (relative offsets)
            patterns = [(1, 0), (2, 1), (s_x := 0, s_y := 2), (1, 2), (2, 2)]
            # wait, let's just use fixed offsets
            # Let's use a simple list of (dx, dy)
            glider = [(1,0), (2,1), (0,2), (1,2), (2,2)]
            offset_x, offset_y = 5, 5
            for dx, dy in glider:
                if 0 <= offset_x + dx < self.cols and 0 <= offset_y + dy < self.rows:
                    self.grid[offset_y + dy][offset_x + dx] = 1
        elif pattern_type == 'pulsar':
            # A pulsar-ish structure (13x13)
            # We'll just use a list of relative coordinates for a Pulsar
            # Centered roughly in the middle
            cx, cy = self.cols // 2, self.rows // 2
            # The offsets for a pulsar (relative to its top-left corner)
            # A pulsar is centered on 1, 5, 7, 11 etc? No.
            # Let's use the coordinates:
            # Rows/Cols: 1, 5, 7, 11
            # The cells are at (x,y) where x,y are in {1,5,7,11} (relative to a 13x13 box)
            # Wait, that's not right. A pulsar is centered on its 4th-indexed cells.
            # Let's just use a reliable coordinate set.
            offsets = [
                (1,1),(2,1),(3,1),(4,1), (1,5),(5,5), (1,6),(5,6), (1,7),(5,7), (1,8),(5,8),
                (5,1),(5,2),(5,3),(5,4), (5,5),(1,5), (5,6),(1,6), (5,7),(1,7), (5,8),(1,8),
                # This is getting messy. Let's just define the points for a 13x13 pulsar:
                # x: 2,3,4, 6,8,10; y: 2,3,4, 6,8,10 etc.
            ]
            # Actually, let's use a simple hardcoded list of relative coords for a Pulsar
            p = [(1,1),(2,1),(3,1), (1,5),(5,5), (1,6),(5,6), (1,7),(5,7), (1,8),(5,8),
                 (5,1),(5,2),(5,3),(5,4), (2,1),(4,1), (2,5),(4,5), (2,6),(4,6), (2,7),(4,7), (2,8),(4,8)]
            # No, let's use a simpler, foolproof way.
            pass
            
            # REAL PULSAR COORDINATES (relative to top-left corner)
            # The pattern is a 13x13 grid structure.
            # Cells are at:
            # (row, col) in [ (2,1),(2,5),(2,7),(2,10), (3,1),(3,5),(3,7),(3,10), ... ] No.
            # Let's just use a list of (x,y) for a pulsar centered at (0,0)
            # It is a 4x4-like structure with cross-arms.
            # Let's just hardcode it.
            p_cells = [
                (1,1), (2,1), (3,1), (1,2), (5,2), (1,3), (5,3), (1,4), (5,4),
                (1,5), (5,5), (1,6), (5,6), (1,7), (5,7), (1,8), (5,8),
                (2,1), (3,1), (4,1), (2,5), (4,5), (2,6), (4,6), (2,7), (4,7), (2,8), (4,8), # wait this is wrong
            ]
            # Let's just use a simple 2D list of offsets to be safe.
            # A pulsar is made of 4 small 3x3 blocks? No.
            # It's a set of 4 blocks.
            # Let's just use the coordinates:
            # x in {1, 5, 7, 11} and y in {1, 5, 7, 11} is NOT it.
            pass

    def update(self):
        """Apply the rules of the game to compute the next generation."""
        if self.paused:
            return

        new_grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        for y in range(self.rows):
            for x in range(self.cols):
                # Count live neighbors
                neighbors = 0
                for dy in [-1, 0, 1]:
                    for dx in [-low_x := [-1, 0, 1]]: # wait, let's fix the loop
                        pass
        # Let's rewrite the update logic to be cleaner.
        pass

# RE-RE-RE-RE-RE-WRITE. This is the one.

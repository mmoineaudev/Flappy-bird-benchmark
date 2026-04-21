#!/usr/bin/env python3
"""
Conway's Game of Life - Retro Neon Edition
A single-file interactive simulation with pygame.

Controls:
  Spacebar    - Pause / Resume
  R           - Randomize grid
  C           - Clear grid
  + / -       - Adjust animation speed
  Mouse Click - Toggle cell state
  Buttons     - Load preset patterns (gliders, pulsars, etc.)
"""

import pygame
import sys
import math
import random
import os

# ---------------------------------------------------------------------------
# Configuration & Constants
# ---------------------------------------------------------------------------

# Neon color palette
COLOR_BG = (10, 10, 15)          # Dark background
COLOR_GRID = (30, 30, 45)        # Subtle grid lines
COLOR_CYAN = (0, 255, 255)       # Neon cyan
COLOR_MAGENTA = (255, 0, 255)    # Neon magenta
COLOR_PURPLE = (157, 78, 223)    # Purple
COLOR_WHITE = (255, 255, 255)
COLOR_DIM = (100, 100, 140)
COLOR_BTN_BG = (20, 20, 35)
COLOR_BTN_HOVER = (40, 40, 70)
COLOR_BTN_TEXT = (200, 200, 255)

# Default simulation parameters
DEFAULT_COLS = 80
DEFAULT_ROWS = 40
DEFAULT_CELL_SIZE = 15
DEFAULT_BIRTH_RULE = [3]         # Cells born with exactly these neighbor counts
DEFAULT_SURVIVE_RULE = [2, 3]    # Cells survive with these neighbor counts
DEFAULT_FPS = 15                 # Starting frames per second

# UI layout constants (pixels)
SIDEBAR_WIDTH = 240              # Width of the right sidebar
BUTTON_AREA_TOP = 60             # Where button area starts vertically
BUTTON_HEIGHT = 30               # Height of each preset button
BUTTON_Y_GAP = 5                 # Vertical gap between buttons

# ---------------------------------------------------------------------------
# Game Logic
# ---------------------------------------------------------------------------


class GameOfLife:
    """Core Game of Life simulation with configurable rules."""

    def __init__(self, cols=DEFAULT_COLS, rows=DEFAULT_ROWS, cell_size=DEFAULT_CELL_SIZE):
        self.cols = cols
        self.rows = rows
        self.cell_size = cell_size
        self.birth_rule = list(DEFAULT_BIRTH_RULE)
        self.survive_rule = list(DEFAULT_SURVIVE_RULE)
        self.grid = [[False for _ in range(cols)] for _ in range(rows)]
        self.next_grid = [[False for _ in range(cols)] for _ in range(rows)]
        self.frame_count = 0
        self.population = 0

    def randomize(self, density=0.3):
        """Fill the grid with random live cells at the given density."""
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = random.random() < density
        self.frame_count = 0
        self._count_population()

    def clear(self):
        """Kill all cells."""
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = False
        self.frame_count = 0
        self.population = 0

    def toggle_cell(self, col, row):
        """Toggle a single cell at the given grid coordinates."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.grid[row][col] = not self.grid[row][col]
            self._count_population()

    def count_neighbors(self, row, col):
        """Count live neighbors for a cell using toroidal wrapping."""
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr = (row + dr) % self.rows
                nc = (col + dc) % self.cols
                if self.grid[nr][nc]:
                    count += 1
        return count

    def step(self):
        """Advance the simulation by one generation. Uses double-buffering."""
        # Copy current grid state into next_grid for synchronized update
        for r in range(self.rows):
            for c in range(self.cols):
                neighbors = self.count_neighbors(r, c)
                alive = self.grid[r][c]
                # Apply birth and survival rules
                if alive and neighbors in self.survive_rule:
                    self.next_grid[r][c] = True
                elif not alive and neighbors in self.birth_rule:
                    self.next_grid[r][c] = True
                else:
                    self.next_grid[r][c] = False

        # Swap grids — this is the synchronized update point
        self.grid, self.next_grid = self.next_grid, self.grid
        self.frame_count += 1
        self._count_population()

    def _count_population(self):
        """Count total live cells in the current grid."""
        self.population = sum(
            1 for r in range(self.rows) for c in range(self.cols) if self.grid[r][c]
        )

    # ---------------------------------------------------------------------------
    # Preset Patterns
    # ---------------------------------------------------------------------------

    def load_glider(self, col, row):
        """Place a glider pattern centered near the given grid coordinates."""
        positions = [(row, col), (row + 1, col + 1), (row + 2, col - 1),
                     (row + 2, col), (row + 2, col + 1)]
        for r, c in positions:
            if 0 <= r < self.rows and 0 <= c < self.cols:
                self.grid[r][c] = True
        self._count_population()

    def load_pulsar(self, col, row):
        """Place a pulsar oscillator centered at the given coordinates."""
        offsets = [
            (-2, -6), (-2, -1), (-2, 1), (-2, 6),
            (-1, -6), (-1, -1), (-1, 1), (-1, 6),
            (1, -6), (1, -1), (1, 1), (1, 6),
            (2, -6), (2, -1), (2, 1), (2, 6),
        ]
        for dr, dc in offsets:
            r, c = row + dr, col + dc
            if 0 <= r < self.rows and 0 <= c < self.cols:
                self.grid[r][c] = True
        # Mirror the second half (top ↔ bottom)
        for dr, dc in offsets:
            r = row - dr
            c = col + dc
            if 0 <= r < self.rows and 0 <= c < self.cols:
                self.grid[r][c] = True
        # Left-right mirror
        for dr, dc in offsets:
            r = row + dr
            c = col - dc
            if 0 <= r < self.rows and 0 <= c < self.cols:
                self.grid[r][c] = True
        self._count_population()

    def load_glider_gun(self, col, row):
        """Place a Gosper glider gun (classic pattern)."""
        # Gosper glider gun relative positions
        cells = [
            (0, 4), (0, 5), (1, 4), (1, 5),
            (2, 4), (2, 5),
            (3, 3), (3, 7),
            (4, 2), (4, 8),
            (5, 2), (5, 8),
            (6, 2), (6, 3), (6, 4), (6, 5),
            (7, 3), (7, 7),
            (8, 4), (8, 5), (8, 6), (8, 7),
            (9, 5),
            (10, 4), (10, 8),
            (11, 3), (11, 7),
            (12, 4), (12, 5),
        ]
        for dr, dc in cells:
            r, c = row + dr, col + dc
            if 0 <= r < self.rows and 0 <= c < self.cols:
                self.grid[r][c] = True
        self._count_population()

    def load_spaceship(self, col, row):
        """Place a lightweight spaceship (LWSS)."""
        cells = [
            (0, 1), (0, 4),
            (1, 0), (1, 4),
            (2, 0), (2, 3), (2, 4),
            (3, 0), (3, 1), (3, 2), (3, 3),
        ]
        for dr, dc in cells:
            r, c = row + dr, col + dc
            if 0 <= r < self.rows and 0 <= c < self.cols:
                self.grid[r][c] = True
        self._count_population()

    def load_rpentoid(self, col, row):
        """Place a lightweight spaceship (R-pentomino) — small but chaotic."""
        cells = [(0, 1), (0, 2), (1, 0), (1, 1), (2, 1)]
        for dr, dc in cells:
            r, c = row + dr, col + dc
            if 0 <= r < self.rows and 0 <= c < self.cols:
                self.grid[r][c] = True
        self._count_population()

    def load_blinker(self, col, row):
        """Place a blinker (period-2 oscillator)."""
        # Horizontal blinker
        for dc in range(3):
            r, c = row, col + dc - 1
            if 0 <= r < self.rows and 0 <= c < self.cols:
                self.grid[r][c] = True
        self._count_population()


# ---------------------------------------------------------------------------
# Rendering Helpers
# ---------------------------------------------------------------------------


def draw_scanline_overlay(surface):
    """Draw a subtle CRT scanline overlay for retro aesthetic."""
    w, h = surface.get_size()
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    for y in range(0, h, 3):
        pygame.draw.line(overlay, (255, 255, 255, 8), (0, y), (w, y))
    surface.blit(overlay, (0, 0))


def draw_glow_cell(surface, x, y, size, color):
    """Draw a cell with a neon glow effect using layered rectangles."""
    # Outer glow
    for i in range(3, 0, -1):
        glow_color = tuple(min(c + i * 15, 255) for c in color)
        alpha = max(0, 60 - i * 15)
        rect = pygame.Rect(x - (i * size // 6), y - (i * size // 6),
                           size + (i * size // 3), size + (i * size // 3))
        a_surface = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
        a_surface.fill((*glow_color[:3], alpha))
        surface.blit(a_surface, rect.topleft, special_blend=pygame.BLEND_RGBA_ADD)

    # Core cell
    rect = pygame.Rect(x, y, size - 1, size - 1)
    pygame.draw.rect(surface, color, rect, border_radius=size // 4)


# ---------------------------------------------------------------------------
# Main Application
# ---------------------------------------------------------------------------


class App:
    """Main application managing pygame, simulation, and UI."""

    def __init__(self):
        pygame.init()

        # Compute window dimensions
        self.cell_size = DEFAULT_CELL_SIZE
        self.cols = DEFAULT_COLS
        self.rows = DEFAULT_ROWS
        self.grid_width = self.cols * self.cell_size
        self.grid_height = self.rows * self.cell_size
        self.sidebar_width = SIDEBAR_WIDTH
        self.window_width = self.grid_width + self.sidebar_width
        self.window_height = self.grid_height

        self.screen = pygame.display.set_mode(
            (self.window_width, self.window_height), pygame.HWSURFACE | pygame.DOUBLEBUF
        )
        pygame.display.set_caption("Conway's Game of Life — Neon Edition")

        # Clock for FPS control
        self.clock = pygame.time.Clock()
        self.fps = DEFAULT_FPS

        # Simulation state
        self.go_live = GameOfLife(self.cols, self.rows, self.cell_size)
        self.paused = False

        # UI helpers
        self.font_small = pygame.font.SysFont("monospace,consolas,courier new", 13)
        self.font_medium = pygame.Font(
            None, 16 if pygame.font.get_init() else 16
        )
        self.font_title = pygame.font.SysFont(
            "monospace,consolas,courier new", 18, bold=True
        )

        # Preset buttons with their load functions
        self.buttons = [
            ("Random", self.go_live.randomize),
            ("Clear", self.go_live.clear),
            ("Blinker", lambda: (self.go_live.clear(), self.go_live.load_blinker(5, 15))),
            ("Glider", lambda: (self.go_live.clear(), self.go_live.load_glider(30, 15))),
            ("Spaceship", lambda: (self.go_live.clear(), self.go_live.load_spaceship(20, 15))),
            ("R-Pentomino", lambda: (self.go_live.clear(), self.go_live.load_rpentoid(35, 18))),
            ("Glider Gun", lambda: (self.go_live.clear(), self.go_live.load_glider_gun(15, 10))),
            ("Pulsar", lambda: (self.go_live.clear(), self.go_live.load_pulsar(30, 12))),
        ]

        # Track hovered button index
        self.hovered_btn = -1

    def _compute_layout(self):
        """Recalculate layout-dependent values when cell size changes."""
        self.grid_width = self.cols * self.cell_size
        self.grid_height = self.rows * self.cell_size
        self.sidebar_x = self.grid_width + 20  # Sidebar starts after grid with margin

    def _get_fps_ticks(self):
        """Return the tick interval in ms for the current FPS."""
        return int(1000 / max(self.fps, 1))

    def run(self):
        """Main event loop."""
        running = True
        step_timer = 0

        while running:
            # --- Event handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_r:
                        self.go_live.randomize()
                    elif event.key == pygame.K_c:
                        self.go_live.clear()
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                        self.fps = min(self.fps + 3, 60)
                    elif event.key == pygame.K_MINUS:
                        self.fps = max(self.fps - 3, 1)

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos

                    # Check sidebar buttons
                    if mx >= self.sidebar_x:
                        btn_area_y = BUTTON_AREA_TOP
                        for i, (label, _) in enumerate(self.buttons):
                            btn_y = btn_area_y + i * (BUTTON_HEIGHT + BUTTON_Y_GAP)
                            if btn_y <= my < btn_y + BUTTON_HEIGHT:
                                # Execute the button action
                                _, func = self.buttons[i]
                                func()
                                break

                    # Check grid click — toggle cell
                    elif mx < self.grid_width and my < self.grid_height:
                        col = mx // self.cell_size
                        row = my // self.cell_size
                        self.go_live.toggle_cell(col, row)

                elif event.type == pygame.MOUSEMOTION:
                    mx, my = event.pos
                    if mx >= self.sidebar_x:
                        btn_area_y = BUTTON_AREA_TOP
                        for i, (label, _) in enumerate(self.buttons):
                            btn_y = btn_area_y + i * (BUTTON_HEIGHT + BUTTON_Y_GAP)
                            if btn_y <= my < btn_y + BUTTON_HEIGHT:
                                self.hovered_btn = i
                                break
                        else:
                            self.hovered_btn = -1
                    else:
                        self.hovered_btn = -1

            # --- Simulation step (throttled by FPS) ---
            step_timer += self.clock.get_time()
            if not self.paused and step_timer >= self._get_fps_ticks():
                self.go_live.step()
                step_timer = 0

            # --- Rendering ---
            self.screen.fill(COLOR_BG)

            # Draw grid lines
            for r in range(self.rows + 1):
                y = r * self.cell_size
                pygame.draw.line(self.screen, COLOR_GRID,
                                 (0, y), (self.grid_width, y))
            for c in range(self.cols + 1):
                x = c * self.cell_size
                pygame.draw.line(self.screen, COLOR_GRID,
                                 (x, 0), (x, self.grid_height))

            # Draw live cells with neon glow
            for r in range(self.rows):
                for c in range(self.cols):
                    if self.go_live.grid[r][c]:
                        x = c * self.cell_size
                        y = r * self.cell_size
                        # Color cycling based on frame count for visual interest
                        hue_offset = (self.go_live.frame_count + r + c) % 3
                        color = [COLOR_CYAN, COLOR_MAGENTA, COLOR_PURPLE][hue_offset]
                        draw_glow_cell(self.screen, x, y, self.cell_size, color)

            # Draw scanline overlay
            draw_scanline_overlay(self.screen)

            # --- Sidebar UI ---
            self._draw_sidebar()

            pygame.display.flip()
            self.clock.tick(self.fps + 10)  # Slightly above sim FPS for smooth UI

        pygame.quit()

    def _draw_sidebar(self):
        """Draw the right sidebar with controls, stats, and preset buttons."""
        sw = SIDEBAR_WIDTH
        sx = self.grid_width + 20  # x-offset of sidebar

        # Sidebar background panel
        pygame.draw.rect(self.screen, (15, 15, 25),
                         (sx - 5, -5, sw + 10, self.window_height + 10))
        pygame.draw.line(self.screen, COLOR_DIM, (sx - 5, 0), (sx - 5, self.window_height), 1)

        # Title
        title = self.font_title.render("CONTROLS", True, COLOR_CYAN)
        self.screen.blit(title, (sx + 10, 15))

        # Rule parameters display
        rule_text = self.font_small.render(
            f"Rules: B{self.go_live.birth_rule}/S{self.go_live.survive_rule}",
            True, COLOR_MAGENTA
        )
        self.screen.blit(rule_text, (sx + 10, 45))

        # Population counter
        pop_text = self.font_small.render(
            f"Population: {self.go_live.population}", True, COLOR_WHITE
        )
        self.screen.blit(pop_text, (sx + 10, 70))

        # Frame counter
        frame_text = self.font_small.render(
            f"Frame: {self.go_live.frame_count}", True, COLOR_PURPLE
        )
        self.screen.blit(frame_text, (sx + 10, 95))

        # FPS display
        fps_text = self.font_small.render(f"FPS: {self.fps}", True, COLOR_CYAN)
        self.screen.blit(fps_text, (sx + 10, 120))

        # Paused indicator
        if self.paused:
            pause_text = self.font_medium.render("⏸ PAUSED", True, COLOR_MAGENTA)
            self.screen.blit(pause_text, (sx + 10, 145))

        # Separator line
        pygame.draw.line(self.screen, COLOR_DIM,
                         (sx + 5, 170), (sx + sw - 10, 170), 1)

        # Preset patterns label
        preset_label = self.font_small.render("PRESET PATTERNS", True, COLOR_PURPLE)
        self.screen.blit(preset_label, (sx + 10, BUTTON_AREA_TOP - 25))

        # Draw buttons
        btn_area_y = BUTTON_AREA_TOP + 5
        for i, (label, _) in enumerate(self.buttons):
            btn_x = sx + 10
            btn_w = sw - 20
            btn_y = btn_area_y + i * (BUTTON_HEIGHT + BUTTON_Y_GAP)

            # Button background
            bg_color = COLOR_BTN_HOVER if i == self.hovered_btn else COLOR_BTN_BG
            pygame.draw.rect(self.screen, bg_color,
                             (btn_x, btn_y, btn_w, BUTTON_HEIGHT), border_radius=5)
            pygame.draw.rect(self.screen, COLOR_DIM,
                             (btn_x, btn_y, btn_w, BUTTON_HEIGHT), 1, border_radius=5)

            # Button text
            btn_font = self.font_medium if len(label) <= 12 else self.font_small
            btn_text = btn_font.render(label, True, COLOR_BTN_TEXT)
            text_rect = btn_text.get_rect(center=(btn_x + btn_w // 2, btn_y + BUTTON_HEIGHT // 2))
            self.screen.blit(btn_text, text_rect)

        # Control hints at bottom of sidebar
        pygame.draw.line(self.screen, COLOR_DIM,
                         (sx + 5, self.window_height - 100), (sx + sw - 10, self.window_height - 100), 1)

        hints = [
            "Space: Pause/Resume",
            "R: Randomize",
            "C: Clear",
            "+/-: Speed",
            "Click: Toggle cell",
        ]
        hint_font = pygame.font.SysFont("monospace,consolas,courier new", 11)
        for idx, hint in enumerate(hints):
            ht = hint_font.render(hint, True, COLOR_DIM)
            self.screen.blit(ht, (sx + 10, self.window_height - 95 + idx * 16))


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------


def main():
    """Launch the Game of Life application."""
    app = App()
    app.run()


if __name__ == "__main__":
    main()

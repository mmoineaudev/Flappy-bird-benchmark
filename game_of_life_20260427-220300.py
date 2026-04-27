#!/usr/bin/env python3
"""
Conway's Game of Life — Retro Neon Edition
Single-file Python/Pygame implementation with configurable rules,
neon glow visuals, CRT scanline overlay, and preset patterns.
"""

import pygame
import sys
import math
import random

# ─── Configuration ───────────────────────────────────────────────────────────

# Grid settings
GRID_COLS = 80
GRID_ROWS = 40
CELL_SIZE = 15

# Colors
BG_COLOR = (10, 10, 15)
GRID_LINE_COLOR = (20, 20, 30)
NEON_CYAN = (0, 255, 255)
NEON_MAGENTA = (255, 0, 255)
NEON_PURPLE = (157, 78, 221)
TEXT_COLOR = (200, 200, 220)
BUTTON_COLOR = (30, 30, 50)
BUTTON_HOVER = (50, 50, 80)
BUTTON_BORDER = (100, 100, 160)

# Default Game of Life rules (B3/S23)
BIRTH_RULES = {3}
SURVIVAL_MIN = 2
SURVIVAL_MAX = 3

# UI dimensions
UI_HEIGHT = 180  # space at bottom for buttons + info
SCREEN_WIDTH = GRID_COLS * CELL_SIZE
SCREEN_HEIGHT = GRID_ROWS * CELL_SIZE + UI_HEIGHT

# FPS range
MIN_FPS = 1
MAX_FPS = 60
START_FPS = 15

# ─── Classic Patterns ────────────────────────────────────────────────────────

PATTERNS = {
    "glider": [
        (0, 1), (1, 2), (2, 0), (2, 1), (2, 2),
    ],
    "blinker": [
        (1, 0), (1, 1), (1, 2),
    ],
    "toad": [
        (1, 1), (1, 2), (1, 3),
        (2, 0), (2, 1), (2, 2),
    ],
    "beacon": [
        (0, 0), (0, 1),
        (1, 0), (1, 1),
        (2, 2), (2, 3),
        (3, 2), (3, 3),
    ],
    "pulsar": [
        # Top
        (2, 0), (3, 0), (4, 0), (8, 0), (9, 0), (10, 0),
        (0, 2), (5, 2), (7, 2), (12, 2),
        (0, 3), (5, 3), (7, 3), (12, 3),
        (0, 4), (5, 4), (7, 4), (12, 4),
        (2, 5), (3, 5), (4, 5), (8, 5), (9, 5), (10, 5),
        # Bottom (mirrored)
        (2, 7), (3, 7), (4, 7), (8, 7), (9, 7), (10, 7),
        (0, 8), (5, 8), (7, 8), (12, 8),
        (0, 9), (5, 9), (7, 9), (12, 9),
        (0, 10), (5, 10), (7, 10), (12, 10),
        (2, 11), (3, 11), (4, 11), (8, 11), (9, 11), (10, 11),
        (2, 12), (3, 12), (4, 12), (8, 12), (9, 12), (10, 12),
    ],
    "lwss": [
        # Lightweight spaceship
        (1, 0), (4, 0),
        (0, 1),
        (0, 2), (4, 2),
        (0, 3), (1, 3), (2, 3), (3, 3),
    ],
    "pentadecathlon": [
        (1, 0), (2, 0), (3, 0),
        (2, 1),
        (2, 2),
        (2, 3),
        (1, 4), (2, 4), (3, 4),
        (2, 5),
        (2, 6),
        (2, 7),
    ],
}

# ─── Button definitions ──────────────────────────────────────────────────────

BUTTON_Y = SCREEN_HEIGHT - 50
BUTTON_HEIGHT = 40
BUTTON_PADDING = 10
BUTTON_START_X = 10

BUTTONS = []
for name in PATTERNS:
    # Measure text width for button sizing
    btn = pygame.Rect(BUTTON_START_X + len(BUTTONS) * (100 + BUTTON_PADDING), BUTTON_Y, 100, BUTTON_HEIGHT)
    BUTTONS.append({"name": name, "rect": btn, "hover": False})

INFO_Y = SCREEN_HEIGHT - UI_HEIGHT + 20

# ─── Game of Life Core ───────────────────────────────────────────────────────

class GameOfLife:
    """Parametrizable Game of Life engine."""

    def __init__(self, cols, rows, cell_size, birth_rules, surv_min, surv_max):
        self.cols = cols
        self.rows = rows
        self.cell_size = cell_size
        self.birth_rules = birth_rules
        self.survival_min = surv_min
        self.survival_max = surv_max
        self.grid = [[False] * cols for _ in range(rows)]
        self.frame = 0

    def randomize(self, density=0.3):
        """Fill grid randomly with given density."""
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = random.random() < density

    def clear(self):
        """Kill all cells."""
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = False

    def count_neighbors(self, r, c):
        """Count live neighbors with toroidal wrapping."""
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr = (r + dr) % self.rows
                nc = (c + dc) % self.cols
                if self.grid[nr][nc]:
                    count += 1
        return count

    def step(self):
        """Advance one generation. Returns new grid state."""
        new_grid = [[False] * self.cols for _ in range(self.rows)]
        for r in range(self.rows):
            for c in range(self.cols):
                neighbors = self.count_neighbors(r, c)
                if self.grid[r][c]:
                    # Survival check
                    if self.survival_min <= neighbors <= self.survival_max:
                        new_grid[r][c] = True
                else:
                    # Birth check
                    if neighbors in self.birth_rules:
                        new_grid[r][c] = True
        self.grid = new_grid
        self.frame += 1
        return self.grid

    def population(self):
        """Count live cells."""
        count = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if self.grid[r][c]:
                    count += 1
        return count

    def place_pattern(self, pattern_name):
        """Place a named pattern centered in the grid."""
        self.clear()
        if pattern_name not in PATTERNS:
            return
        pattern = PATTERNS[pattern_name]
        # Find bounding box
        min_r = min(p[1] for p in pattern)
        max_r = max(p[1] for p in pattern)
        min_c = min(p[0] for p in pattern)
        max_c = max(p[0] for p in pattern)
        pat_h = max_r - min_r + 1
        pat_w = max_c - min_c + 1
        offset_r = self.rows // 2 - pat_h // 2
        offset_c = self.cols // 2 - pat_w // 2
        for pr, pc in pattern:
            gr = (offset_r + pr) % self.rows
            gc = (offset_c + pc) % self.cols
            self.grid[gr][gc] = True

    def toggle_cell(self, col, row):
        """Toggle cell at grid coordinates."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.grid[row][col] = not self.grid[row][col]


# ─── Rendering Helpers ───────────────────────────────────────────────────────

def draw_glow_rect(surface, rect, color, radius=4):
    """Draw a rounded rectangle with a glow effect using layered alpha rects."""
    glow_layers = 3
    for layer in range(glow_layers, 0, -1):
        alpha_color = (color[0], color[1], color[2], max(0, 60 * layer))
        glow_surf = pygame.Surface((rect.width + 4 * layer, rect.height + 4 * layer), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, alpha_color, glow_surf.get_rect(), border_radius=radius + layer)
        surface.blit(glow_surf, (rect.x - 2 * layer, rect.y - 2 * layer))
    # Solid fill
    pygame.draw.rect(surface, color, rect, border_radius=radius)


def draw_neon_cell(surface, x, y, size, color):
    """Draw a single neon cell with glow."""
    # Glow
    glow_surf = pygame.Surface((size + 6, size + 6), pygame.SRCALPHA)
    glow_surf.fill((*color, 40))
    surface.blit(glow_surf, (x - 3, y - 3))
    # Core
    core_size = size - 2
    offset = 1
    inner = pygame.Surface((core_size, core_size), pygame.SRCALPHA)
    inner.fill((*color, 180))
    surface.blit(inner, (x + offset, y + offset))
    # Highlight
    highlight = pygame.Surface((core_size - 2, core_size - 2), pygame.SRCALPHA)
    highlight.fill((*color, 255))
    surface.blit(highlight, (x + offset + 1, y + offset + 1))


def draw_scanline_overlay(surface, width, height):
    """Draw subtle CRT scanline effect."""
    scanline_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(0, height, 3):
        pygame.draw.line(scanline_surf, (0, 0, 0, 25), (0, y), (width, y))
    surface.blit(scanline_surf, (0, 0))


# ─── Main Application ────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Game of Life — Neon Edition")
    clock = pygame.time.Clock()
    font_large = pygame.font.SysFont("monospace", 22, bold=True)
    font_small = pygame.font.SysFont("monospace", 14)
    font_button = pygame.font.SysFont("monospace", 13, bold=True)

    # Initialize game
    gol = GameOfLife(GRID_COLS, GRID_ROWS, CELL_SIZE, BIRTH_RULES, SURVIVAL_MIN, SURVIVAL_MAX)
    gol.randomize(0.35)

    paused = False
    fps = START_FPS
    target_time = 1000.0 / fps  # ms per frame
    elapsed = 0.0

    while True:
        dt = clock.tick(fps)
        elapsed += dt

        # ── Events ──────────────────────────────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    gol.randomize(0.35)
                elif event.key == pygame.K_c:
                    gol.clear()
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    fps = min(MAX_FPS, fps + 1)
                    target_time = 1000.0 / fps
                elif event.key == pygame.K_MINUS:
                    fps = max(MIN_FPS, fps - 1)
                    target_time = 1000.0 / fps

            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos

                # Check if click is on a button (UI area)
                if my >= BUTTON_Y:
                    for btn in BUTTONS:
                        if btn["rect"].collidepoint(mx, my):
                            gol.place_pattern(btn["name"])
                            break
                    else:
                        # Click in UI area but not on a button — ignore
                        pass
                else:
                    # Click on grid — toggle cell
                    col = mx // CELL_SIZE
                    row = (my) // CELL_SIZE
                    gol.toggle_cell(col, row)

        # ── Game logic ──────────────────────────────────────────────────
        if elapsed >= target_time:
            if not paused:
                gol.step()
            elapsed = 0.0

        # ── Rendering ───────────────────────────────────────────────────
        screen.fill(BG_COLOR)

        # Draw grid lines (subtle)
        for x in range(0, SCREEN_WIDTH, CELL_SIZE):
            pygame.draw.line(screen, GRID_LINE_COLOR, (x, 0), (x, GRID_ROWS * CELL_SIZE))
        for y in range(0, GRID_ROWS * CELL_SIZE, CELL_SIZE):
            pygame.draw.line(screen, GRID_LINE_COLOR, (0, y), (SCREEN_WIDTH, y))

        # Draw live cells with neon glow
        for r in range(gol.rows):
            for c in range(gol.cols):
                if gol.grid[r][c]:
                    x = c * CELL_SIZE
                    y = r * CELL_SIZE
                    # Cycle color based on position for visual variety
                    hue = (c + r) % 3
                    if hue == 0:
                        color = NEON_CYAN
                    elif hue == 1:
                        color = NEON_MAGENTA
                    else:
                        color = NEON_PURPLE
                    draw_neon_cell(screen, x, y, CELL_SIZE - 1, color)

        # Scanline overlay on game area only
        draw_scanline_overlay(screen, SCREEN_WIDTH, GRID_ROWS * CELL_SIZE)

        # ── UI area ─────────────────────────────────────────────────────
        # Divider line
        pygame.draw.line(screen, BUTTON_BORDER, (0, GRID_ROWS * CELL_SIZE),
                         (SCREEN_WIDTH, GRID_ROWS * CELL_SIZE), 1)

        # Info text
        pop_text = font_small.render(f"Pop: {gol.population()}", True, TEXT_COLOR)
        frame_text = font_small.render(f"Frame: {gol.frame}", True, TEXT_COLOR)
        rule_text = font_small.render(
            f"Rules: B{sorted(gol.birth_rules)}/S{gol.survival_min}-{gol.survival_max}",
            True, TEXT_COLOR
        )
        fps_text = font_small.render(f"Speed: {fps} fps", True, TEXT_COLOR)
        state_text = font_small.render("PAUSED" if paused else "RUNNING",
                                        True, (255, 100, 100) if paused else NEON_CYAN)

        screen.blit(pop_text, (10, INFO_Y))
        screen.blit(frame_text, (10, INFO_Y + 22))
        screen.blit(rule_text, (10, INFO_Y + 44))
        screen.blit(fps_text, (10, INFO_Y + 66))
        screen.blit(state_text, (10, INFO_Y + 88))

        # Control hints
        controls = [
            "Space: Pause  R: Random  C: Clear  +/-: Speed  Click: Toggle",
        ]
        for i, line in enumerate(controls):
            hint = font_small.render(line, True, (120, 120, 140))
            screen.blit(hint, (10, INFO_Y + 110 + i * 16))

        # Draw buttons
        for btn in BUTTONS:
            btn_rect = btn["rect"]
            # Check hover
            mouse_pos = pygame.mouse.get_pos()
            btn["hover"] = btn_rect.collidepoint(mouse_pos)

            color = BUTTON_HOVER if btn["hover"] else BUTTON_COLOR
            draw_glow_rect(screen, btn_rect, BUTTON_BORDER if btn["hover"] else (60, 60, 90), 6)
            pygame.draw.rect(screen, color, btn_rect, border_radius=6)

            label = font_button.render(btn["name"].capitalize(), True, TEXT_COLOR)
            label_rect = label.get_rect(center=btn_rect.center)
            screen.blit(label, label_rect)

        # Scanline overlay for entire screen (subtle)
        draw_scanline_overlay(screen, SCREEN_WIDTH, SCREEN_HEIGHT)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

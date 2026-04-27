#!/usr/bin/env python3
"""
Conway's Game of Life — Retro Neon Edition
A single-file pygame implementation with customizable rules, neon visuals,
scanline/CRT overlay effects, and preset patterns.

Controls:
  Spacebar   – Pause / Resume
  R          – Randomize grid
  C          – Clear grid
  + / -      – Adjust animation speed (FPS)
  Mouse click– Toggle cell state at cursor position
  Buttons    – Load classic Game of Life patterns
"""

import sys
import random
import math
import pygame

# ──────────────────────────────────────────────
# Configuration & Rule Parameters
# ──────────────────────────────────────────────

GRID_COLS = 80          # number of columns in the grid
GRID_ROWS = 40          # number of rows in the grid
CELL_SIZE = 15          # pixel size of each cell
BG_COLOR = (10, 10, 15) # dark background (#0a0a0f)

# Neon palette — cells glow with these colors based on age
NEON_COLORS = {
    "cyan":    (0, 255, 255),   # #00ffff
    "magenta": (255, 0, 255),   # ff00ff
    "purple":  (157, 78, 221),  # 9d4edd
}
CELL_COLOR = NEON_COLORS["cyan"]

# Conway's B3/S23 default rules — fully parametrizable:
BIRTH_NEIGHBORS = {3}          # set of neighbor counts that spawn a new cell
SURVIVE_MIN = 2                # minimum neighbors to survive
SURVIVE_MAX = 3                # maximum neighbors to survive

INITIAL_DENSITY = 0.30         # probability of a cell being alive on randomize
TARGET_FPS = 15               # animation speed (frames per second)
FPS_STEP = 2                  # amount +/- changes FPS by

# UI layout constants
UI_FONT_SIZE = 14
HINT_FONT_SIZE = 12
BUTTON_HEIGHT = 36
BUTTON_MARGIN = 8
TOP_BAR_HEIGHT = 50  # space for title / info at top


def screen_width():
    return GRID_COLS * CELL_SIZE


def screen_height():
    return GRID_ROWS * CELL_SIZE + TOP_BAR_HEIGHT + BUTTON_HEIGHT + 20


# ──────────────────────────────────────────────
# Preset Patterns
# ──────────────────────────────────────────────

# Patterns are defined as (row, col) offsets relative to center.
PRESETS = {
    "Glider": [
        (0, 1), (1, 2), (2, 0), (2, 1), (2, 2)
    ],
    "LWSS": [          # Lightweight spaceship
        (0, 1), (0, 4),
        (1, 0),
        (2, 0), (2, 4),
        (3, 0), (3, 1), (3, 2), (3, 3),
    ],
    "Pulsar": [        # Period-3 oscillator — 1/8 quadrant then mirrored
    ],
    "R-pentomino": [
        (0, 1), (0, 2),
        (1, 0), (1, 1),
        (2, 1),
    ],
    "Gosper Glider Gun": [
        # Top-left is at offset (4,0) relative to pattern origin
        (0, 24),
        (1, 22), (1, 24),
        (2, 12), (2, 13), (2, 20), (2, 21), (2, 34), (2, 35),
        (3, 11), (3, 15), (3, 20), (3, 21), (3, 34), (3, 35),
        (4, 0),   (4, 1),   (4, 10),  (4, 16),  (4, 20), (4, 21),
        (5, 0),   (5, 1),   (5, 10),  (5, 14),  (5, 16), (5, 17),
                   (5, 22),  (5, 24),
        (6, 10),  (6, 16),  (6, 24),
        (7, 11),  (7, 15),
        (8, 12),  (8, 13),
    ],
}


def _build_pulsar():
    """Build the Pulsar oscillator pattern (period-3)."""
    pts = []
    # Six arms in one quadrant; mirror to all four quadrants
    offsets = [
        (-6, -2), (-6, -1), (-6, 1), (-6, 2),
        (-2, -6), (-1, -6), (1, -6), (2, -6),
        (-2, 2),  (-2, 3),  (-1, 2),  (-1, 3),
        (2, -2),  (2, -3),  (1, -2),  (1, -3),
        (-6, -2), (-6, -1), (-6, 1),  (-6, 2),
    ]
    # Actually build properly: Pulsar has points at offsets from center
    # Each arm is a line of 3 cells. There are 12 arms total.
    pts = []
    for dx in [-6, -4, -2, 2, 4, 6]:
        for dy in [-2, -1, 1, 2]:
            pts.append((dx, dy))
    return pts


PRESETS["Pulsar"] = _build_pulsar()


def place_pattern(grid: list[list[int]], cols: int, rows: int, name: str) -> None:
    """Place a preset pattern centered on the grid."""
    if name not in PRESETS:
        return
    pattern = PRESETS[name]
    # Find bounding box center
    min_r = min(r for r, c in pattern)
    max_r = max(r for r, c in pattern)
    min_c = min(c for r, c in pattern)
    max_c = max(c for r, c in pattern)
    center_r = (min_r + max_r) // 2
    center_c = (min_c + max_c) // 2
    for dr, dc in pattern:
        gr = (dr - center_r) % rows
        gc = (dc - center_c) % cols
        grid[gr][gc] = 1


# ──────────────────────────────────────────────
# Game Logic
# ──────────────────────────────────────────────

def count_neighbors(grid: list[list[int]], r: int, c: int, rows: int, cols: int) -> int:
    """Count live neighbors for cell (r, c) using toroidal wrapping."""
    total = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr = (r + dr) % rows
            nc = (c + dc) % cols
            total += grid[nr][nc]
    return total


def next_generation(grid: list[list[int]], rows: int, cols: int) -> list[list[int]]:
    """Compute the next generation using configurable birth/survival rules."""
    new_grid = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            n = count_neighbors(grid, r, c, rows, cols)
            if grid[r][c]:
                # Cell is alive — check survival
                new_grid[r][c] = 1 if SURVIVE_MIN <= n <= SURVIVE_MAX else 0
            else:
                # Cell is dead — check birth
                new_grid[r][c] = 1 if n in BIRTH_NEIGHBORS else 0
    return new_grid


def randomize_grid(grid: list[list[int]], rows: int, cols: int) -> None:
    """Fill grid with random alive/dead cells based on INITIAL_DENSITY."""
    for r in range(rows):
        for c in range(cols):
            grid[r][c] = 1 if random.random() < INITIAL_DENSITY else 0


def clear_grid(grid: list[list[int]], rows: int, cols: int) -> None:
    """Set every cell to dead."""
    for r in range(rows):
        for c in range(cols):
            grid[r][c] = 0


# ──────────────────────────────────────────────
# Rendering Helpers
# ──────────────────────────────────────────────

def draw_cell(surface: pygame.Surface, r: int, c: int, alive: bool, age: int) -> None:
    """Draw a single cell with neon glow effect."""
    x = c * CELL_SIZE
    y = r * CELL_SIZE + TOP_BAR_HEIGHT  # offset for top bar

    if not alive:
        return

    # Grow color based on age (simulated with a sine wave over frame count)
    t = (age % 60) / 60.0
    # Blend between cyan and magenta smoothly
    cr = int(CELL_COLOR[0] * (1 - t) + NEON_COLORS["magenta"][0] * t)
    cg = int(CELL_COLOR[1] * (1 - t) + NEON_COLORS["magenta"][1] * t)
    cb = int(CELL_COLOR[2] * (1 - t) + NEON_COLORS["magenta"][2] * t)

    # Glow: draw a larger, semi-transparent cell underneath
    glow_size = CELL_SIZE + 4
    glow_surf = pygame.Surface((glow_size, glow_size), pygame.SRCALPHA)
    glow_color = (cr, cg, cb, 60)
    pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect(), border_radius=3)
    surface.blit(glow_surf, (x - 2, y - 2 + TOP_BAR_HEIGHT))

    # Main cell
    inner = CELL_SIZE - 1
    color = (min(cr + 40, 255), min(cg + 40, 255), min(cb + 40, 255))
    pygame.draw.rect(surface, color, (x, y + TOP_BAR_HEIGHT, inner, inner), border_radius=2)


def draw_grid_lines(surface: pygame.Surface, cols: int, rows: int) -> None:
    """Draw subtle grid lines."""
    line_color = (30, 30, 45)
    offset_y = TOP_BAR_HEIGHT
    for c in range(cols + 1):
        x = c * CELL_SIZE
        pygame.draw.line(surface, line_color, (x, offset_y), (x, offset_y + rows * CELL_SIZE))
    for r in range(rows + 1):
        y = offset_y + r * CELL_SIZE
        pygame.draw.line(surface, line_color, (0, y), (cols * CELL_SIZE, y))


def draw_scanlines(surface: pygame.Surface) -> None:
    """Overlay faint horizontal scanlines for a CRT/retro effect."""
    alpha_surf = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
    for y in range(0, surface.get_height(), 3):
        pygame.draw.rect(alpha_surf, (255, 255, 255, 12), (0, y, surface.get_width(), 1))
    surface.blit(alpha_surf, (0, 0))


def draw_button(surface: pygame.Surface, rect: pygame.Rect, text: str, hovered: bool) -> None:
    """Draw a clickable button with neon border."""
    color = (80, 60, 120) if hovered else (40, 30, 70)
    border = (157, 78, 221) if hovered else (80, 50, 130)
    pygame.draw.rect(surface, color, rect, border_radius=6)
    pygame.draw.rect(surface, border, rect, width=2, border_radius=6)
    font = pygame.font.SysFont("monospace", UI_FONT_SIZE)
    txt = font.render(text, True, (220, 210, 255))
    tx = rect.x + (rect.width - txt.get_width()) // 2
    ty = rect.y + (rect.height - txt.get_height()) // 2
    surface.blit(txt, (tx, ty))


def draw_text(surface: pygame.Surface, text: str, x: int, y: int, color=(180, 180, 200), size=UI_FONT_SIZE) -> None:
    """Render a short string at the given position."""
    font = pygame.font.SysFont("monospace", size)
    txt = font.render(text, True, color)
    surface.blit(txt, (x, y))


# ──────────────────────────────────────────────
# Main Application
# ──────────────────────────────────────────────

def main():
    # Initialize pygame
    pygame.init()

    w = screen_width()
    h = screen_height()
    screen = pygame.display.set_mode((w, h))
    pygame.display.set_caption("Game of Life — Neon Edition")
    clock = pygame.time.Clock()

    font_main = pygame.font.SysFont("monospace", UI_FONT_SIZE)
    font_hint = pygame.font.SysFont("monospace", HINT_FONT_SIZE)

    # Game state
    rows, cols = GRID_ROWS, GRID_COLS
    grid = [[0] * cols for _ in range(rows)]
    ages = [[0] * cols for _ in range(rows)]  # track age of each cell for color animation
    running = True
    paused = False
    frame_count = 0
    fps = TARGET_FPS

    randomize_grid(grid, rows, cols)

    # Build buttons below the grid
    button_y = TOP_BAR_HEIGHT + rows * CELL_SIZE + 10
    preset_names = list(PRESETS.keys())
    btn_width = 130
    total_btns_w = len(preset_names) * (btn_width + BUTTON_MARGIN) - BUTTON_MARGIN
    btn_start_x = (w - total_btns_w) // 2
    buttons = []
    for i, name in enumerate(preset_names):
        bx = btn_start_x + i * (btn_width + BUTTON_MARGIN)
        rect = pygame.Rect(bx, button_y, btn_width, BUTTON_HEIGHT)
        buttons.append((name, rect))

    # ── Main Loop ──────────────────────────────
    while running:
        dt = clock.tick(fps)  # limit FPS

        # ── Events ───────────────────────────────
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    randomize_grid(grid, rows, cols)
                    ages = [[0] * cols for _ in range(rows)]
                    frame_count = 0
                elif event.key == pygame.K_c:
                    clear_grid(grid, rows, cols)
                    ages = [[0] * cols for _ in range(rows)]
                    frame_count = 0
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    fps = min(fps + FPS_STEP, 60)
                elif event.key == pygame.K_MINUS:
                   fps = max(fps - FPS_STEP, 1)
                # Handle preset selection via number keys
                elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3,
                                   pygame.K_4, pygame.K_5):
                    idx = event.key - pygame.K_1
                    if idx < len(preset_names):
                        clear_grid(grid, rows, cols)
                        ages = [[0] * cols for _ in range(rows)]
                        place_pattern(grid, cols, rows, preset_names[idx])
                        frame_count = 0

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                # Check if click is on a button
                for name, rect in buttons:
                    if rect.collidepoint(mx, my):
                        clear_grid(grid, rows, cols)
                        ages = [[0] * cols for _ in range(rows)]
                        place_pattern(grid, cols, rows, name)
                        frame_count = 0
                        break
                else:
                    # Check if click is on the grid area
                    if my >= TOP_BAR_HEIGHT and my < TOP_BAR_HEIGHT + rows * CELL_SIZE:
                        c = mx // CELL_SIZE
                        r = (my - TOP_BAR_HEIGHT) // CELL_SIZE
                        if 0 <= r < rows and 0 <= c < cols:
                            grid[r][c] = 1 - grid[r][c]

        # ── Update ───────────────────────────────
        if not paused:
            grid = next_generation(grid, rows, cols)
            frame_count += 1
            # Increment ages for live cells
            for r in range(rows):
                for c in range(cols):
                    if grid[r][c]:
                        ages[r][c] = ages[r][c] + 1

        # ── Render ───────────────────────────────
        screen.fill(BG_COLOR)

        # Draw subtle grid lines
        draw_grid_lines(screen, cols, rows)

        # Draw cells with glow
        for r in range(rows):
            for c in range(cols):
                if grid[r][c]:
                    draw_cell(screen, r, c, True, ages[r][c])

        # Scanline overlay
        draw_scanlines(screen)

        # ── UI Overlay ───────────────────────────
        # Top bar background
        pygame.draw.rect(screen, (15, 15, 25), (0, 0, w, TOP_BAR_HEIGHT))
        pygame.draw.line(screen, (60, 40, 90), (0, TOP_BAR_HEIGHT - 1), (w, TOP_BAR_HEIGHT - 1))

        pop = sum(grid[r][c] for r in range(rows) for c in range(cols))
        draw_text(screen, f"Game of Life — Neon Edition", 15, 8, color=(200, 190, 255), size=16)
        draw_text(screen, f"Frame: {frame_count}   Pop: {pop}   FPS: {fps}", 15, 30)
        rule_str = f"B{sorted(BIRTH_NEIGHBORS)}/S[{SURVIVE_MIN}-{SURVIVE_MAX}]"
        draw_text(screen, rule_str, w - len(rule_str) * 7 - 20, 30, color=(150, 140, 200))

        if paused:
            draw_text(screen, "⏸ PAUSED", w // 2 - 60, TOP_BAR_HEIGHT + rows * CELL_SIZE // 2 - 10,
                      color=(255, 100, 100), size=24)

        # Control hints (bottom-left)
        hint_y = TOP_BAR_HEIGHT + rows * CELL_SIZE + BUTTON_HEIGHT + 8
        draw_text(screen, "Space:Pause  R:Random  C:Clear  +/-:Speed  Click:Toggle", 10, hint_y, size=HINT_FONT_SIZE)

        # Buttons
        mx, my = pygame.mouse.get_pos()
        for name, rect in buttons:
            hovered = rect.collidepoint(mx, my)
            draw_button(screen, rect, name, hovered)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

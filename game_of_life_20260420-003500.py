#!/usr/bin/env python3
"""
Conway's Game of Life — Retro Neon Edition
Parametrizable rules, CRT-style visuals, interactive controls.
"""

import pygame
import random
import sys
import math

# ── Config ──────────────────────────────────────────────────────────
GRID_W = 80                # columns
GRID_H = 40                # rows
CELL_SIZE = 15             # pixels per cell
FPS = 15                 # default animation speed (will vary with +/-)
BIRTH_NEIGHBORS = [3]    # neighbors needed to spawn a cell
SURVIVE_MIN = 2          # minimum neighbors to survive
SURVIVE_MAX = 3          # maximum neighbors to survive

# ── Colors ──────────────────────────────────────────────────────────
BG = (10, 10, 15)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
PURPLE = (157, 78, 221)
GRID_COLOR = (25, 25, 40)
TEXT_COLOR = (180, 180, 200)
BTN_BG = (30, 30, 50)
BTN_HOVER = (50, 50, 80)
BTN_ACTIVE = (0, 255, 255)

# ── Patterns ────────────────────────────────────────────────────────
PATTERNS = {
    "Glider": [
        (1, 0), (2, 1), (0, 2), (1, 2), (2, 2),
    ],
    "Pulsar": [
        # Top
        (4, 0), (5, 0), (6, 0), (10, 0), (11, 0), (12, 0),
        (0, 4), (0, 5), (0, 6), (0, 10), (0, 11), (0, 12),
        (1, 4), (1, 5), (1, 6), (1, 10), (1, 11), (1, 12),
        (2, 4), (2, 5), (2, 6), (2, 10), (2, 11), (2, 12),
        (3, 4), (3, 5), (3, 6), (3, 10), (3, 11), (3, 12),
        # Bottom
        (4, 18), (5, 18), (6, 18), (10, 18), (11, 18), (12, 18),
        (0, 22), (0, 23), (0, 24), (0, 25), (0, 26), (0, 27),
        (1, 22), (1, 23), (1, 24), (1, 25), (1, 26), (1, 27),
        (2, 22), (2, 23), (2, 24), (2, 25), (2, 26), (2, 27),
        (3, 22), (3, 23), (3, 24), (3, 25), (3, 26), (3, 27),
    ],
    "Gosper Glider Gun": [
        (24, 0), (22, 1), (24, 1), (12, 2), (13, 2), (20, 2), (21, 2), (34, 2), (35, 2),
        (11, 3), (15, 3), (20, 3), (21, 3), (34, 3), (35, 3), (0, 4), (1, 4), (10, 4),
        (16, 4), (20, 4), (21, 4), (0, 5), (1, 5), (10, 5), (14, 5), (16, 5), (17, 5),
        (22, 5), (24, 5), (10, 6), (16, 6), (24, 6), (11, 7), (15, 7), (12, 8), (13, 8),
    ],
    "R-Pentomino": [
        (1, 0), (2, 0), (0, 1), (1, 1), (1, 2),
    ],
    "Acorn": [
        (1, 0), (3, 1), (0, 2), (1, 2), (4, 2), (5, 2), (6, 2),
    ],
}

# ── Helper functions ────────────────────────────────────────────────
def count_neighbors(grid, x, y):
    """Count live neighbors using toroidal wrapping."""
    count = 0
    for dy in (-1, 0, 1):
        for dx in (-1, 0, 1):
            if dx == 0 and dy == 0:
                continue
            nx = (x + dx) % GRID_W
            ny = (y + dy) % GRID_H
            count += grid[ny][nx]
    return count


def next_generation(grid):
    """Compute the next generation from current grid."""
    new_grid = [[0] * GRID_W for _ in range(GRID_H)]
    for y in range(GRID_H):
        for x in range(GRID_W):
            n = count_neighbors(grid, x, y)
            if grid[y][x]:
                if SURVIVE_MIN <= n <= SURVIVE_MAX:
                    new_grid[y][x] = 1
            else:
                if n in BIRTH_NEIGHBORS:
                    new_grid[y][x] = 1
    return new_grid


def randomize_grid(grid):
    """Fill grid with random cells (~30% density)."""
    for y in range(GRID_H):
        for x in range(GRID_W):
            grid[y][x] = 1 if random.random() < 0.30 else 0


def clear_grid(grid):
    """Set every cell to dead."""
    for y in range(GRID_H):
        for x in range(GRID_W):
            grid[y][x] = 0


def apply_pattern(grid, name):
    """Clear grid and place a named pattern centered."""
    clear_grid(grid)
    if name not in PATTERNS:
        return
    cells = PATTERNS[name]
    if not cells:
        return
    min_x = min(c[0] for c in cells)
    max_x = max(c[0] for c in cells)
    min_y = min(c[1] for c in cells)
    max_y = max(c[1] for c in cells)
    off_x = (GRID_W - (max_x - min_x)) // 2 - min_x
    off_y = (GRID_H - (max_y - min_y)) // 2 - min_y
    for cx, cy in cells:
        nx = (cx + off_x) % GRID_W
        ny = (cy + off_y) % GRID_H
        grid[ny][nx] = 1


# ── UI Buttons ──────────────────────────────────────────────────────
class Button:
    """Simple clickable button with hover state."""
    def __init__(self, text, x, y, w, h, font):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.font = font
        self.hovered = False

    def draw(self, surface):
        color = BTN_HOVER if self.hovered else BTN_BG
        pygame.draw.rect(surface, color, self.rect, border_radius=4)
        if self.hovered:
            pygame.draw.rect(surface, BTN_ACTIVE, self.rect, 2, border_radius=4)
        txt_surf = self.font.render(self.text, True, TEXT_COLOR)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def handle_click(self, pos):
        return self.rect.collidepoint(pos)


# ── Main ────────────────────────────────────────────────────────────
def main():
    pygame.init()

    # Screen dims: grid area + UI sidebar
    grid_pixels_w = GRID_W * CELL_SIZE
    ui_w = 260
    screen_w = grid_pixels_w + ui_w
    screen_h = GRID_H * CELL_SIZE + 50  # small top bar for fps
    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("Game of Life — Retro Neon")
    clock = pygame.time.Clock()

    # Fonts
    font_small = pygame.font.SysFont("monospace", 14, bold=True)
    font_med = pygame.font.SysFont("monospace", 16, bold=True)
    font_big = pygame.font.SysFont("monospace", 22, bold=True)

    # State
    grid = [[0] * GRID_W for _ in range(GRID_H)]
    randomize_grid(grid)
    running = True
    paused = False
    frame = 0
    tick_delay = 1000 // FPS   # ms per tick
    last_tick = 0
    fps_display = FPS
    next_tick = pygame.time.get_ticks() + tick_delay

    # Scanline overlay
    scanline_surf = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)

    # Buttons: presets
    btn_y = 130
    btn_h = 36
    btn_gap = 42
    btn_w = 200
    buttons = []
    btn_labels = list(PATTERNS.keys())
    rows = 2
    cols = len(btn_labels) // rows + (1 if len(btn_labels) % rows else 0)
    x_start = (grid_pixels_w - (btn_w * cols)) // 2
    for i, label in enumerate(btn_labels):
        row = i // cols
        col = i % cols
        bx = x_start + col * (btn_w + 10)
        by = btn_y + row * btn_gap
        btn = Button(label, bx, by, btn_w, btn_h, font_small)
        buttons.append((label, btn))

    # ── Main loop ─────────────────────────────────────────────────────
    while running:
        now = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    randomize_grid(grid)
                    frame = 0
                elif event.key == pygame.K_c:
                    clear_grid(grid)
                    frame = 0
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    fps_display = min(fps_display + 2, 60)
                    tick_delay = 1000 // fps_display
                elif event.key == pygame.K_MINUS:
                    fps_display = max(fps_display - 2, 2)
                    tick_delay = 1000 // fps_display
                elif event.key == pygame.K_ESCAPE:
                    running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # Check buttons first (buttons are in the grid area)
                clicked_btn = None
                for label, btn in buttons:
                    if btn.handle_click(event.pos):
                        clicked_btn = label

                if clicked_btn:
                    apply_pattern(grid, clicked_btn)
                    frame = 0
                elif my < GRID_H * CELL_SIZE and mx < grid_pixels_w:
                    gx = mx // CELL_SIZE
                    gy = my // CELL_SIZE
                    if 0 <= gx < GRID_W and 0 <= gy < GRID_H:
                        grid[gy][gx] = 1 - grid[gy][gx]

        # Advance simulation
        if not paused and now >= next_tick:
            grid = next_generation(grid)
            frame += 1
            next_tick = now + tick_delay

        # ── Render ──────────────────────────────────────────────────────
        screen.fill(BG)

        # Draw cells with glow
        for y in range(GRID_H):
            for x in range(GRID_W):
                if grid[y][x]:
                    # Slight glow via layered rects
                    cx = x * CELL_SIZE
                    cy = y * CELL_SIZE
                    # Outer glow
                    glow = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    pygame.draw.rect(glow, (0, 200, 200, 30), (0, 0, CELL_SIZE, CELL_SIZE))
                    screen.blit(glow, (cx - 1, cy - 1))
                    # Main cell
                    pygame.draw.rect(screen, CYAN, (cx + 1, cy + 1, CELL_SIZE - 2, CELL_SIZE - 2), border_radius=2)

        # Grid lines
        for x in range(0, GRID_W * CELL_SIZE, CELL_SIZE):
            pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, GRID_H * CELL_SIZE))
        for y in range(0, GRID_H * CELL_SIZE, CELL_SIZE):
            pygame.draw.line(screen, GRID_COLOR, (0, y), (grid_pixels_w, y))

        # Scanline effect
        scanline_surf.fill((0, 0, 0, 0))
        for y in range(0, screen_h, 4):
            pygame.draw.line(scanline_surf, (0, 0, 0, 15), (0, y), (screen_w, y))
        screen.blit(scanline_surf, (0, 0))

        # ── UI Sidebar ──────────────────────────────────────────────────
        ui_start_x = grid_pixels_w + 10

        # Title
        title = font_big.render("GAME OF LIFE", True, CYAN)
        screen.blit(title, (ui_start_x, 10))

        # Stats
        population = sum(sum(row) for row in grid)
        stats = [
            f"Frame:   {frame}",
            f"Pop:     {population}",
            f"FPS:     {fps_display}",
            f"Status:  {'PAUSED' if paused else 'RUNNING'}",
            "",
            f"Rule B:  {BIRTH_NEIGHBORS}",
            f"Rule S:  {SURVIVE_MIN}-{SURVIVE_MAX}",
        ]
        for i, line in enumerate(stats):
            txt = font_small.render(line, True, TEXT_COLOR)
            screen.blit(txt, (ui_start_x, 55 + i * 20))

        # Control hints
        hints = [
            "CONTROLS:",
            "Space  — Pause",
            "R      — Randomize",
            "C      — Clear",
            "+ / -  — Speed",
            "Click  — Toggle",
            "Esc    — Quit",
        ]
        hint_color = (120, 120, 160)
        for i, line in enumerate(hints):
            txt = font_small.render(line, True, hint_color)
            screen.blit(txt, (ui_start_x, 250 + i * 18))

        # Preset buttons (drawn over grid area)
        for label, btn in buttons:
            btn.draw(screen)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

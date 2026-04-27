#!/usr/bin/env python3
"""
Conway's Game of Life - Retro Neon Edition
==========================================
Single-file interactive simulation with configurable rules and neon wave visuals.

Controls:
  Spacebar  - Pause / Resume
  R         - Randomize grid
  C         - Clear grid
  + / -     - Adjust animation speed (FPS)
  Mouse     - Toggle cell state at cursor position
  Click buttons to load preset patterns (gliders, pulsars, etc.)

Configurable Rules:
  - Grid dimensions (default: 80x40 cells)
  - Birth rule: list of neighbor counts that spawn a new cell
  - Survival rule: min/max neighbors for a cell to survive
  - Cell size in pixels (default: 15px)
  - Animation speed (FPS)
"""

import pygame
import random
import sys

# ---------------------------------------------------------------------------
# Constants / Defaults
# ---------------------------------------------------------------------------
DEFAULT_COLS = 80
DEFAULT_ROWS = 40
DEFAULT_CELL_SIZE = 15
DEFAULT_FPS = 12

# Default Conway rules: B3/S23 (Birth on 3, survive on 2 or 3)
DEFAULT_BIRTH_NEIGHBORS = [3]
DEFAULT_MIN_SURVIVE = 2
DEFAULT_MAX_SURVIVE = 3

BG_COLOR = (10, 10, 15)
GRID_COLOR = (20, 20, 30)
TEXT_COLOR = (180, 180, 200)
HIGHLIGHT_COLOR = (255, 255, 100)

NEON_COLORS = [
    (0, 255, 255),     # cyan
    (255, 0, 255),     # magenta
    (157, 78, 221),    # purple
    (0, 200, 255),     # sky blue
    (255, 100, 200),   # hot pink
]

BUTTON_AREA_HEIGHT = 40
UI_TEXT_HEIGHT = 60
TOP_BAR_HEIGHT = BUTTON_AREA_HEIGHT + UI_TEXT_HEIGHT


# ---------------------------------------------------------------------------
# Game of Life engine (fully parametrizable rules)
# ---------------------------------------------------------------------------

class GoLBoard:
    """Parametrizable Conway's Game of Life board.

    The classic B3/S2234 rules are controlled via:
      - birth_neighbors:  set of neighbor counts that cause a dead cell to become alive
      - min_survive / max_survive: range of neighbor counts for a live cell to survive
    This allows any variant like "Seeds" (B2/S), "HighLife" (B36/S23), etc.
    """

    def __init__(self, cols, rows, cell_size, birth_neighbors,
                 min_survive, max_survive):
        self.cols = cols
        self.rows = rows
        self.cell_size = cell_size
        self.birth_neighbors = set(birth_neighbors)
        self.min_survive = min_survive
        self.max_survive = max_survive

        self.screen_w = cols * cell_size
        self.screen_h = rows * cell_size + TOP_BAR_HEIGHT

        # Sparse grid stored as a set of (x, y) tuples — memory efficient
        self.live_cells: set[tuple[int, int]] = set()
        self.frame = 0
        self.paused = False

    def randomize(self, density=0.3):
        """Fill the grid randomly with given alive-cell probability."""
        self.live_cells = {
            (x, y) for x in range(self.cols)
                     for y in range(self.rows)
                     if random.random() < density
        }

    def clear(self):
        """Remove all live cells and reset the frame counter."""
        self.live_cells.clear()
        self.frame = 0

    def toggle_cell(self, col, row):
        """Flip the state of a single cell. Bounds-checked."""
        if not (0 <= col < self.cols and 0 <= row < self.rows):
            return
        key = (col, row)
        if key in self.live_cells:
            self.live_cells.discard(key)
        else:
            self.live_cells.add(key)

    @staticmethod
    def _neighbor_offsets():
        """Yield the 8 surrounding offsets."""
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                if dx == 0 and dy == 0:
                    continue
                yield dx, dy

    def step(self):
        """Advance one generation using toroidal (wrapped) boundary conditions.

        A dead cell becomes alive if its live-neighbor count is in the birth set.
        A live cell survives if its live-neighbor count is within [min_survive, max_survive].
        Returns the new population count.
        """
        # Count neighbors for every cell adjacent to a live cell
        neighbor_counts: dict[tuple[int, int], int] = {}
        for (cx, cy) in self.live_cells:
            for dx, dy in self._neighbor_offsets():
                nx = (cx + dx) % self.cols
                ny = (cy + dy) % self.rows
                neighbor_counts[(nx, ny)] = neighbor_counts.get((nx, ny), 0) + 1

        new_live = set()
        for (x, y), count in neighbor_counts.items():
            is_alive = (x, y) in self.live_cells
            if is_alive:
                if self.min_survive <= count <= self.max_survive:
                    new_live.add((x, y))
            else:
                if count in self.birth_neighbors:
                    new_live.add((x, y))

        self.live_cells = new_live
        self.frame += 1
        return len(self.live_cells)

    @property
    def population(self):
        return len(self.live_cells)


# ---------------------------------------------------------------------------
# Classic pattern definitions
# ---------------------------------------------------------------------------

PATTERNS: dict[str, list[tuple[int, int]]] = {
    "Glider": [
        (1, 0), (2, 1), (0, 2), (1, 2), (2, 2),
    ],
    "Large Glider": [
        (1, 0), (2, 0), (0, 1), (2, 1), (0, 2), (1, 2), (2, 2),
    ],
    "Block (still life)": [
        (0, 0), (1, 0), (0, 1), (1, 1),
    ],
    "Blinker (period-2)": [
        (0, 0), (1, 0), (2, 0),
    ],
    "Toad (period-2)": [
        (1, 0), (2, 0), (3, 0),
        (0, 1), (1, 1), (2, 1),
    ],
    "Beacon (period-2)": [
        (0, 0), (1, 0), (0, 1),
        (3, 2), (2, 3), (3, 3),
    ],
    "Pentadecathlon (period-15)": [
        (1, 0), (0, 1), (2, 1), (1, 2),
        (1, 4), (0, 5), (2, 5), (1, 6),
    ],
    "Lightweight Spaceship (LWSS)": [
        (1, 0), (4, 0), (0, 1), (0, 2), (4, 2),
        (0, 3), (1, 3), (2, 3), (3, 3),
    ],
    "R-pentomino": [
        (1, 0), (2, 0), (0, 1), (1, 1), (1, 2),
    ],
}

# Build Pulsar — period-3 oscillator with 96 cells
pulsar_cells = set()
quadrant_offsets = [
    # (dx, dy) for each of the 4 arms × 6 cells per arm direction
    (12, 0), (13, 0), (18, 0), (19, 0),
    (0, 12), (0, 13), (0, 18), (0, 19),
    (4, 12), (4, 13), (4, 18), (4, 19),
    (12, 4), (13, 4), (18, 4), (19, 4),
    (7, 12), (7, 13), (7, 18), (7, 19),
    (12, 7), (13, 7), (18, 7), (19, 7),
]
for q in quadrant_offsets:
    pulsar_cells.add(q)
PATTERNS["Pulsar"] = list(pulsar_cells)


def place_pattern(board: GoLBoard, pattern_name: str):
    """Center *pattern_name* on the board and replace current grid."""
    cells = PATTERNS.get(pattern_name)
    if not cells:
        raise ValueError(f"Unknown pattern: {pattern_name}")

    xs = [c[0] for c in cells]
    ys = [c[1] for c in cells]
    min_x, min_y = min(xs), min(ys)
    bw = max(xs) - min_x + 1
    bh = max(ys) - min_y + 1

    off_x = (board.cols - bw) // 2
    off_y = (board.rows - bh) // 2

    board.live_cells = {
        (c[0] - min_x + off_x, c[1] - min_y + off_y) for c in cells
    }
    board.frame = 0


# ---------------------------------------------------------------------------
# Button system
# ---------------------------------------------------------------------------

class Button:
    """Simple clickable button rendered as a colored rectangle with text."""

    def __init__(self, x, y, w, h, text, color=(40, 40, 60), hover_color=(70, 70, 100)):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color

    def draw(self, surface, font):
        """Draw the button; highlight when hovered."""
        c = self.hover_color if self.rect.collidepoint(pygame.mouse.get_pos()) else self.color
        pygame.draw.rect(surface, c, self.rect, border_radius=4)
        pygame.draw.rect(surface, (100, 100, 150), self.rect, width=1, border_radius=4)
        txt = font.render(self.text, True, TEXT_COLOR)
        surface.blit(txt, (self.rect.x + 6, self.rect.y + (self.rect.h - txt.get_height()) // 2))

    def clicked_at(self, pos):
        return self.rect.collidepoint(pos)


class ButtonBar:
    """Manages a row of buttons across the top bar."""

    def __init__(self, y, available_w, button_text_list):
        self.buttons = []
        btn_w = 110
        gap = 6
        total_w = len(button_text_list) * btn_w + (len(button_text_list) - 1) * gap
        x_start = max(10, (available_w - total_w) // 2)

        for i, text in enumerate(button_text_list):
            bx = x_start + i * (btn_w + gap)
            self.buttons.append(Button(bx, y, btn_w, BUTTON_AREA_HEIGHT, text))

    def draw(self, surface, font):
        for b in self.buttons:
            b.draw(surface, font)

    def get_clicked(self, pos):
        """Return the 0-based index of the clicked button, or -1."""
        for i, b in enumerate(self.buttons):
            if b.clicked_at(pos):
                return i
        return -1


# ---------------------------------------------------------------------------
# Rendering helpers
# ---------------------------------------------------------------------------

def draw_cells(surface: pygame.Surface, board: GoLBoard):
    """Render live cells with a neon glow effect."""
    for (x, y) in board.live_cells:
        px = x * board.cell_size
        py = y * board.cell_size + TOP_BAR_HEIGHT
        idx = (board.frame // 4) % len(NEON_COLORS)
        color = NEON_COLORS[idx]

        # Glow pass: slightly larger semi-transparent rect behind the cell
        glow_surf = pygame.Surface((board.cell_size + 2, board.cell_size + 2), pygame.SRCALPHA)
        glow_surf.set_alpha(60)
        glow_rect = (1, 1, board.cell_size, board.cell_size)
        pygame.draw.rect(glow_surf, color, glow_rect, border_radius=2)
        surface.blit(glow_surf, (px - 1, py - 1))

        # Main cell pass
        pygame.draw.rect(surface, color, (px, py, board.cell_size, board.cell_size), border_radius=2)


def draw_scanlines(surface: pygame.Surface, width, height):
    """Draw a subtle CRT-like scanline overlay on the live area below the top bar."""
    alpha_surf = pygame.Surface((width, height), pygame.SRCALPHA)
    for y in range(0, height, 3):
        pygame.draw.line(alpha_surf, (255, 255, 255, 12), (0, y), (width, y))
    surface.blit(alpha_surf, (0, TOP_BAR_HEIGHT))


def draw_info(surface: pygame.Surface, board: GoLBoard, fps_display):
    """Render HUD text: frame counter, population, rules, controls."""
    font_small = pygame.font.SysFont("monospace", 14)
    font_normal = pygame.font.SysFont("monospace", 16)

    # Build birth string, e.g. "B3/S2-3"
    birth_str = 'B' + '/'.join(str(n) for n in sorted(board.birth_neighbors))
    lines = [
        (f"Frame: {board.frame}", font_small),
        (f"Population: {board.population}", font_small),
        (f"{birth_str} / S{board.min_survive}-{board.max_survive}", font_small),
        (f"Cell size: {board.cell_size}px | FPS: {fps_display}", font_small),
    ]

    for i, (text, font) in enumerate(lines):
        surf = font.render(text, True, TEXT_COLOR)
        surface.blit(surf, (10, BUTTON_AREA_HEIGHT + 5 + i * 20))

    # Control hints on the right side
    hints_font = pygame.font.SysFont("monospace", 12)
    cx = board.screen_w - 180
    hints = [
        "SPACE: pause/resume",
        "R: randomize | C: clear",
        "+ / -: speed up/down",
        "Click: toggle cell",
        "Buttons: load patterns",
    ]
    for i, h in enumerate(hints):
        s = hints_font.render(h, True, (100, 100, 140))
        surface.blit(s, (cx, BUTTON_AREA_HEIGHT + 5 + i * 16))

    # Pause indicator in the middle of the game area
    if board.paused:
        pause_surf = pygame.font.SysFont("monospace", 28).render(
            "PAUSED", True, HIGHLIGHT_COLOR)
        surface.blit(pause_surf, (board.screen_w // 2 - pause_surf.get_width() // 2,
                                  TOP_BAR_HEIGHT + 30))


# ---------------------------------------------------------------------------
# Main application
# ---------------------------------------------------------------------------

def main():
    """Entry point: initialize pygame, create the board, and run the loop."""
    global board

    pygame.init()
    pygame.font.init()

    # ---- Create board with default Conway B3/S23 rules ---------------------
    board = GoLBoard(
        cols=DEFAULT_COLS,
        rows=DEFAULT_ROWS,
        cell_size=DEFAULT_CELL_SIZE,
        birth_neighbors=DEFAULT_BIRTH_NEIGHBORS[:],
        min_survive=DEFAULT_MIN_SURVIVE,
        max_survive=DEFAULT_MAX_SURVIVE,
    )

    # Randomize initial state
    board.randomize(density=0.35)

    # ---- Button bar: presets for classic patterns -------------------------
    preset_names = ["Glider", "Pulsar", "Blinker", "Toad", "Block", "LWSS"]
    button_bar = ButtonBar(5, board.screen_w, preset_names)

    # ---- Window setup ------------------------------------------------------
    screen = pygame.display.set_mode((board.screen_w, board.screen_h))
    pygame.display.set_caption("Game of Life — Neon Edition")

    clock = pygame.time.Clock()
    fps_display = DEFAULT_FPS

    # Time accumulator for frame-rate independent evolution
    tick_interval = 1.0 / fps_display
    tick_accumulator = 0.0

    running = True
    info_msg = None
    info_msg_timer = 0.0

    print("Game of Life started.")
    print(f"Grid: {board.cols}x{board.rows}, Cell size: {board.cell_size}px")
    print(f"Rules: B{sorted(board.birth_neighbors)}/S{board.min_survive}-{board.max_survive}")
    print("Press Space to pause, R to randomize, C to clear.")

    # ---- Main loop ---------------------------------------------------------
    while running:
        dt = clock.tick(60) / 1000.0  # delta time in seconds

        # ---- Events --------------------------------------------------------
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    board.paused = not board.paused
                elif event.key == pygame.K_r:
                    try:
                        board.randomize(density=0.35)
                        info_msg = "Grid randomized"
                    except Exception as exc:
                        info_msg = f"Randomize failed: {exc}"
                elif event.key == pygame.K_c:
                    board.clear()
                    info_msg = "Grid cleared"
                elif event.key in (pygame.K_KP_PLUS, pygame.K_EQUALS):
                    fps_display = min(60, fps_display + 2)
                    tick_interval = 1.0 / fps_display
                    info_msg = f"FPS: {fps_display}"
                elif event.key == pygame.K_MINUS:
                    fps_display = max(1, fps_display - 2)
                    tick_interval = 1.0 / fps_display
                    info_msg = f"FPS: {fps_display}"

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # Check top-bar buttons first
                btn_idx = button_bar.get_clicked((mx, my))
                if 0 <= btn_idx < len(preset_names):
                    try:
                        place_pattern(board, preset_names[btn_idx])
                        info_msg = f"Loaded: {preset_names[btn_idx]}"
                    except Exception as exc:
                        info_msg = f"Pattern error: {exc}"
                    continue

                # Grid cell click (only below the top bar)
                if my >= TOP_BAR_HEIGHT:
                    col = mx // board.cell_size
                    row = (my - TOP_BAR_HEIGHT) // board.cell_size
                    try:
                        board.toggle_cell(col, row)
                    except Exception:
                        info_msg = f"Click error at ({col},{row})"

        # ---- Board evolution (time accumulator) ----------------------------
        if not board.paused and len(board.live_cells) > 0:
            tick_accumulator += dt
            while tick_accumulator >= tick_interval:
                board.step()
                tick_accumulator -= tick_interval

        # ---- Rendering -----------------------------------------------------
        screen.fill(BG_COLOR)

        # Draw subtle grid lines
        for x in range(0, board.cols * board.cell_size, board.cell_size):
            pygame.draw.line(screen, GRID_COLOR,
                             (x, TOP_BAR_HEIGHT), (x, board.screen_h))
        for y in range(TOP_BAR_HEIGHT, board.screen_h, board.cell_size):
            pygame.draw.line(screen, GRID_COLOR,
                             (0, y), (board.screen_w, y))

        draw_cells(screen, board)
        draw_scanlines(screen, board.screen_w, board.rows * board.cell_size)
        button_bar.draw(screen, pygame.font.SysFont("monospace", 13))
        draw_info(screen, board, fps_display)

        # Draw transient info message near bottom
        if info_msg and info_msg_timer > 0:
            err_surf = pygame.font.SysFont("monospace", 16).render(
                info_msg, True, (200, 220, 255))
            screen.blit(err_surf, (board.screen_w // 2 - err_surf.get_width() // 2,
                                   board.screen_h - 30))

        pygame.display.flip()

    # ---- Cleanup -----------------------------------------------------------
    print("Game of Life exiting.")
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

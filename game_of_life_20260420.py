#!/usr/bin/env python3
"""
Conway's Game of Life — Retro Neon Benchmark Edition
Single-file pygame implementation with synchronized map rendering.

Map Synchronization Strategy:
  We use double-buffering with an atomic swap pattern. The simulation maintains
  two grids (current and next). During each generation step, the next grid is
  fully computed before being atomically swapped into place. This guarantees
  that rendering always sees a complete, consistent state — never a half-updated
  grid. Mouse interaction also operates on the current buffer exclusively,
  avoiding race conditions between user input and simulation updates.

UI Layout:
  Screen is divided into non-overlapping regions:
    - Top bar (y: 0-50): title + stats
    - Left panel (x: 0-220): rules display + control hints
    - Grid area (x: 230+, y: 60+): the game grid
    - Bottom bar (y: screen_height-70): preset pattern buttons
"""

import pygame
import sys
import random
import math
import copy

# ---------------------------------------------------------------------------
# Constants & Configuration
# ---------------------------------------------------------------------------

SCREEN_WIDTH = 1400
SCREEN_HEIGHT = 850

# Retro neon palette
BG_COLOR = (10, 10, 15)
GRID_BG = (14, 14, 22)
CELL_COLORS = [
    (0, 255, 255),   # cyan
    (255, 0, 255),   # magenta
    (157, 78, 221),  # purple
]
GRID_LINE_COLOR = (30, 30, 50)
TEXT_COLOR = (200, 200, 220)
TITLE_COLOR = (0, 255, 255)
HINT_COLOR = (140, 140, 170)
BUTTON_BG = (30, 20, 50)
BUTTON_HOVER = (60, 40, 90)
BUTTON_TEXT = (200, 200, 255)
STAT_COLOR = (0, 255, 200)

# UI layout constants (non-overlapping regions)
TOP_BAR_HEIGHT = 55
LEFT_PANEL_WIDTH = 230
BOTTOM_BAR_HEIGHT = 75
GRID_MARGIN = 10  # padding around grid area

# Grid defaults
DEFAULT_COLS = 65   # fits in remaining width at cell_size=15
DEFAULT_ROWS = 48   # fits in remaining height at cell_size=15
DEFAULT_CELL_SIZE = 15

# Game rules (Conway's B3/S23)
DEFAULT_BIRTH_RULES = [3]
DEFAULT_SURVIVAL_MIN = 2
DEFAULT_SURVIVAL_MAX = 3

FPS_DISPLAY = 60


# ---------------------------------------------------------------------------
# Pattern Definitions
# ---------------------------------------------------------------------------

PATTERNS = {
    "Glider": [
        (0, 1), (1, 2), (2, 0), (2, 1), (2, 2),
    ],
    "LWSS": [
        (0, 1), (0, 4), (1, 0), (2, 0), (2, 4),
        (3, 0), (3, 1), (3, 2), (3, 3),
    ],
    "Pulsar": [
        # Pulsar — period-3 oscillator. Relative coords from top-left of bounding box (7x12)
        # Top half
        (0, 2), (0, 3), (0, 4), (0, 7), (0, 8), (0, 9),
        (2, 0), (2, 5), (2, 7), (2, 12),
        (3, 0), (3, 5), (3, 7), (3, 12),
        (4, 0), (4, 5), (4, 7), (4, 12),
        # Bottom half (symmetric)
        (7, 2), (7, 3), (7, 4), (7, 7), (7, 8), (7, 9),
    ],
    "Gosper Glider Gun": [
        # Gosper glider gun — the first known infinite-growth pattern
        (0, 24),
        (1, 22), (1, 24),
        (2, 12), (2, 13), (2, 20), (2, 21), (2, 34), (2, 35),
        (3, 11), (3, 15), (3, 20), (3, 21), (3, 34), (3, 35),
        (4, 0), (4, 1), (4, 10), (4, 16), (4, 20), (4, 21),
        (5, 0), (5, 1), (5, 10), (5, 14), (5, 16), (5, 17),
        (5, 22), (5, 24),
        (6, 10), (6, 16), (6, 24),
        (7, 11), (7, 15),
        (8, 12), (8, 13),
    ],
    "R-pentomino": [
        (0, 1), (0, 2), (1, 0), (1, 1), (2, 1),
    ],
    "Acorn": [
        (0, 1), (1, 3), (2, 0), (2, 1), (2, 4), (2, 5), (2, 6),
    ],
}


# ---------------------------------------------------------------------------
# Game of Life Engine (double-buffered, synchronized)
# ---------------------------------------------------------------------------

class GOLEngine:
    """
    Core simulation engine using double-buffering for guaranteed state consistency.

    The grid is stored as a list-of-lists where True = alive, False = dead.
    Two buffers are maintained: _current and _next.  Advance() computes the
    entire next generation into _next, then atomically swaps references so
    that rendering always sees a complete state.
    """

    def __init__(self, cols, rows, cell_size, birth_rules, survival_min, survival_max):
        self.cols = cols
        self.rows = rows
        self.cell_size = cell_size
        self.birth_rules = set(birth_rules)
        self.survival_min = survival_min
        self.survival_max = survival_max

        # --- Double buffer: two identical-sized grids -----------------------
        self._current = [[False] * cols for _ in range(rows)]
        self._next = [[False] * cols for _ in range(rows)]

        self.frame_count = 0
        self.population = 0

    # -- Public API --------------------------------------------------------

    def randomize(self, density=0.3):
        """Fill the current buffer with a random pattern."""
        for r in range(self.rows):
            for c in range(self.cols):
                self._current[r][c] = random.random() < density
        self.population = self._count_population()

    def clear(self):
        """Kill every cell in the current buffer."""
        for r in range(self.rows):
            for c in range(self.cols):
                self._current[r][c] = False
        self.population = 0

    def place_pattern(self, pattern_name, anchor_row, anchor_col):
        """Place a named pattern centred near (anchor_row, anchor_col)."""
        if pattern_name not in PATTERNS:
            return
        cells = PATTERNS[pattern_name]
        # Compute bounding box to centre the pattern
        max_r = max(r for r, _ in cells)
        max_c = max(c for r, c in cells)
        off_r = anchor_row - max_r // 2
        off_c = anchor_col - max_c // 2

        # Write into a *copy* of current so we don't interfere with simulation
        new_grid = [row[:] for row in self._current]
        alive = 0
        for dr, dc in cells:
            nr, nc = off_r + dr, off_c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                if not new_grid[nr][nc]:
                    alive += 1
                new_grid[nr][nc] = True
        # Atomic swap
        self._current = new_grid
        self.population = self._count_population()

    def toggle_cell(self, row, col):
        """Flip the state of a single cell in the current buffer."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self._current[row][col] = not self._current[row][col]
            self.population += 1 if self._current[row][col] else -1

    def advance(self):
        """Compute the next generation and swap buffers atomically."""
        for r in range(self.rows):
            for c in range(self.cols):
                neighbors = self._count_neighbors(r, c)
                alive = self._current[r][c]
                if alive:
                    self._next[r][c] = (self.survival_min <= neighbors <= self.survival_max)
                else:
                    self._next[r][c] = (neighbors in self.birth_rules)

        # Atomic swap — after this line, _current is fully consistent.
        self._current, self._next = self._next, self._current
        self.frame_count += 1
        self.population = self._count_population()

    def get_cell(self, row, col):
        """Read the state of a cell from the current buffer."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self._current[row][col]
        return False

    @property
    def grid(self):
        """Expose the current buffer for rendering (read-only)."""
        return self._current

    # -- Internal helpers --------------------------------------------------

    def _count_neighbors(self, row, col):
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                # Toroidal wrapping
                if 0 <= nr < self.rows and 0 <= nc < self.cols:
                    if self._current[nr][nc]:
                        count += 1
        return count

    def _count_population(self):
        total = 0
        for r in range(self.rows):
            for c in range(self.cols):
                if self._current[r][c]:
                    total += 1
        return total


# ---------------------------------------------------------------------------
# UI Helpers (all positions are fixed to avoid overlap)
# ---------------------------------------------------------------------------

class UIManager:
    """
    Manages all on-screen UI elements. Every element has a hard-coded,
    non-overlapping region so the interface is always usable regardless
    of grid size or generation state.
    """

    def __init__(self, font_path=None):
        # Font setup — try system fonts first, fall back to pygame defaults
        self.font_title = pygame.font.Font(font_path, 26) if font_path else pygame.font.SysFont("monospace", 26, bold=True)
        self.font_stat = pygame.font.Font(font_path, 18) if font_path else pygame.font.SysFont("monospace", 18)
        self.font_hint = pygame.font.Font(font_path, 14) if font_path else pygame.font.SysFont("monospace", 14)
        self.font_btn = pygame.font.Font(font_path, 13) if font_path else pygame.font.SysFont("monospace", 13)

        # Button layout — fixed positions in bottom bar region
        btn_w = 160
        btn_h = 38
        btn_y = SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT + 12
        self.buttons = []
        for i, name in enumerate(PATTERNS.keys()):
            x = LEFT_PANEL_WIDTH + (SCREEN_WIDTH - LEFT_PANEL_WIDTH) // 2 - (len(PATTERNS) * btn_w) // 2 + i * btn_w
            self.buttons.append({"name": name, "x": x, "y": btn_y, "w": btn_w, "h": btn_h, "hover": False})

        # Rule display text lines
        self._rule_lines = []
        self._hint_lines = []
        self._build_hint_lines()

    def _build_hint_lines(self):
        """Pre-build hint text so it doesn't change each frame."""
        hints = [
            "Controls:",
            "[SPACE] Pause / Resume",
            "[R]      Randomize",
            "[C]      Clear",
            "[+] [-]  Speed +/-",
            "[Click]  Toggle cell",
            "[Buttons] Place patterns",
        ]
        self._hint_lines = [self.font_hint.render(h, True, HINT_COLOR) for h in hints]

    def update_rule_display(self, engine):
        """Rebuild rule display text from current engine config."""
        birth_str = ",".join(str(b) for b in sorted(engine.birth_rules))
        self._rule_lines = [
            ("Rule Params", TITLE_COLOR),
            (f"Birth:  {birth_str}", TEXT_COLOR),
            (f"Survive: {engine.survival_min}-{engine.survival_max}", TEXT_COLOR),
            (f"Grid: {engine.cols}x{engine.rows}", TEXT_COLOR),
            (f"Cell: {engine.cell_size}px", TEXT_COLOR),
        ]

    def render(self, screen, engine, paused):
        """Draw all UI elements in their fixed regions."""
        # ---- Top bar -------------------------------------------------------
        pygame.draw.rect(screen, BG_COLOR, (0, 0, SCREEN_WIDTH, TOP_BAR_HEIGHT))
        pygame.draw.line(screen, GRID_LINE_COLOR, (0, TOP_BAR_HEIGHT), (SCREEN_WIDTH, TOP_BAR_HEIGHT), 1)

        title = self.font_title.render("GAME OF LIFE", True, TITLE_COLOR)
        screen.blit(title, (15, TOP_BAR_HEIGHT // 2 - title.get_height() // 2))

        # Stats — right-aligned in top bar, no overlap with title
        stats_text = [
            f"Frame: {engine.frame_count}",
            f"Pop:   {engine.population}",
            f"FPS:   {engine._fps_display}" if hasattr(engine, '_fps_display') else "",
        ]
        stat_x = SCREEN_WIDTH - 250
        for i, line in enumerate(stats_text):
            surf = self.font_stat.render(line, True, STAT_COLOR)
            screen.blit(surf, (stat_x, TOP_BAR_HEIGHT // 2 - surf.get_height() // 2 + i * 24))

        if paused:
            pause_text = self.font_title.render("PAUSED", True, (255, 100, 100))
            pw = pause_text.get_width()
            screen.blit(pause_text, (SCREEN_WIDTH // 2 - pw // 2, TOP_BAR_HEIGHT // 2 - pause_text.get_height() // 2))

        # ---- Left panel ----------------------------------------------------
        panel_x = LEFT_PANEL_WIDTH
        panel_w = SCREEN_WIDTH - LEFT_PANEL_WIDTH - GRID_MARGIN
        panel_y = TOP_BAR_HEIGHT + GRID_MARGIN
        panel_h = SCREEN_HEIGHT - TOP_BAR_HEIGHT - BOTTOM_BAR_HEIGHT - 2 * GRID_MARGIN

        pygame.draw.rect(screen, GRID_BG, (0, TOP_BAR_HEIGHT, LEFT_PANEL_WIDTH, panel_h))
        pygame.draw.line(screen, GRID_LINE_COLOR, (LEFT_PANEL_WIDTH, TOP_BAR_HEIGHT),
                         (LEFT_PANEL_WIDTH, SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT), 1)

        # Rule display in left panel
        ry = TOP_BAR_HEIGHT + 20
        for label, color in self._rule_lines:
            surf = self.font_stat.render(label, True, color)
            screen.blit(surf, (15, ry))
            ry += 24

        # Hint display below rules
        hy = ry + 15
        for hint_surf in self._hint_lines:
            screen.blit(hint_surf, (15, hy))
            hy += 20

        # ---- Grid area background ------------------------------------------
        grid_x = LEFT_PANEL_WIDTH + GRID_MARGIN
        grid_y = TOP_BAR_HEIGHT + GRID_MARGIN
        grid_w = SCREEN_WIDTH - LEFT_PANEL_WIDTH - 2 * GRID_MARGIN
        grid_h = SCREEN_HEIGHT - TOP_BAR_HEIGHT - BOTTOM_BAR_HEIGHT - 2 * GRID_MARGIN

        pygame.draw.rect(screen, GRID_BG, (grid_x - 1, grid_y - 1, grid_w + 2, grid_h + 2))
        pygame.draw.rect(screen, GRID_LINE_COLOR, (grid_x - 1, grid_y - 1, grid_w + 2, grid_h + 2), 1)

        # ---- Bottom bar (buttons) ------------------------------------------
        pygame.draw.rect(screen, BG_COLOR, (0, SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT, SCREEN_WIDTH, BOTTOM_BAR_HEIGHT))
        pygame.draw.line(screen, GRID_LINE_COLOR, (0, SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT),
                         (SCREEN_WIDTH, SCREEN_HEIGHT - BOTTOM_BAR_HEIGHT), 1)

    def render_buttons(self, screen):
        """Draw the preset pattern buttons in the bottom bar."""
        for btn in self.buttons:
            color = BUTTON_HOVER if btn["hover"] else BUTTON_BG
            pygame.draw.rect(screen, color, (btn["x"], btn["y"], btn["w"], btn["h"]), border_radius=6)
            pygame.draw.rect(screen, TITLE_COLOR, (btn["x"], btn["y"], btn["w"], btn["h"]), 2, border_radius=6)
            text = self.font_btn.render(btn["name"], True, BUTTON_TEXT)
            tx = btn["x"] + btn["w"] // 2 - text.get_width() // 2
            ty = btn["y"] + btn["h"] // 2 - text.get_height() // 2
            screen.blit(text, (tx, ty))

    def handle_button_click(self, mouse_pos):
        """Return pattern name if a button was clicked, else None."""
        for btn in self.buttons:
            if btn["x"] <= mouse_pos[0] <= btn["x"] + btn["w"] and \
               btn["y"] <= mouse_pos[1] <= btn["y"] + btn["h"]:
                return btn["name"]
        return None

    def update_button_hover(self, mouse_pos):
        """Update hover state for buttons based on mouse position."""
        for btn in self.buttons:
            btn["hover"] = (btn["x"] <= mouse_pos[0] <= btn["x"] + btn["w"] and
                            btn["y"] <= mouse_pos[1] <= btn["y"] + btn["h"])


# ---------------------------------------------------------------------------
# Neon glow renderer
# ---------------------------------------------------------------------------

def draw_glowing_grid(screen, engine, grid_x, grid_y):
    """
    Render the game grid with neon glow effect.
    Each alive cell is drawn as a bright core surrounded by a blurred halo.
    The grid is rendered in one pass so there's no tearing between cells.
    """
    cs = engine.cell_size
    grid = engine.grid  # read from current buffer (guaranteed consistent)

    for r in range(engine.rows):
        for c in range(engine.cols):
            x = grid_x + c * cs
            y = grid_y + r * cs

            if grid[r][c]:
                color = CELL_COLORS[(r + c) % len(CELL_COLORS)]
                # Glow halo (larger, semi-transparent)
                glow_surf = pygame.Surface((cs + 8, cs + 8), pygame.SRCALPHA)
                alpha_color = (*color, 60)
                pygame.draw.ellipse(glow_surf, alpha_color, (2, 2, cs + 4, cs + 4))
                screen.blit(glow_surf, (x - 4, y - 4))

                # Core cell
                core_surf = pygame.Surface((cs, cs), pygame.SRCALPHA)
                core_alpha = (*color, 255)
                pygame.draw.rect(core_surf, core_alpha, (0, 0, cs, cs), border_radius=2)
                screen.blit(core_surf, (x, y))
            else:
                # Dead cell — draw grid line only if it's the last row/col or neighbor is alive
                # Optimization: only draw faint lines near live cells
                has_alive_neighbor = False
                for dr in (-1, 0, 1):
                    for dc in (-1, 0, 1):
                        nr, nc = r + dr, c + dc
                        if 0 <= nr < engine.rows and 0 <= nc < engine.cols:
                            if grid[nr][nc]:
                                has_alive_neighbor = True
                                break
                    if has_alive_neighbor:
                        break

                # Draw subtle grid lines for cells near live ones or at boundaries
                is_edge = (r == 0 or c == 0 or r == engine.rows - 1 or c == engine.cols - 1)
                if has_alive_neighbor or is_edge:
                    pygame.draw.rect(screen, GRID_LINE_COLOR, (x, y, cs, cs), 1)


def draw_scanline_overlay(screen):
    """Draw a subtle CRT scanline overlay on top of everything."""
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    for y in range(0, screen.get_height(), 3):
        pygame.draw.line(overlay, (255, 255, 255, 12), (0, y), (screen.get_width(), y))
    screen.blit(overlay, (0, 0))


# ---------------------------------------------------------------------------
# Main Application
# ---------------------------------------------------------------------------

class GOLApp:
    """Top-level application managing pygame lifecycle and game loop."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Game of Life — Retro Neon")
        self.clock = pygame.time.Clock()

        # Engine: use grid dimensions that fit within the allocated area
        cols = (SCREEN_WIDTH - LEFT_PANEL_WIDTH - 2 * GRID_MARGIN) // DEFAULT_CELL_SIZE
        rows = (SCREEN_HEIGHT - TOP_BAR_HEIGHT - BOTTOM_BAR_HEIGHT - 2 * GRID_MARGIN) // DEFAULT_CELL_SIZE
        # Clamp to a reasonable range
        cols = max(30, min(cols, 100))
        rows = max(20, min(rows, 80))

        self.engine = GOLEngine(
            cols=cols,
            rows=rows,
            cell_size=DEFAULT_CELL_SIZE,
            birth_rules=DEFAULT_BIRTH_RULES,
            survival_min=DEFAULT_SURVIVAL_MIN,
            survival_max=DEFAULT_SURVIVAL_MAX,
        )

        self.ui = UIManager()
        self.paused = True
        self.speed = 15  # generations per second
        self._accum = 0.0  # accumulator for fixed-timestep updates
        self.grid_x = LEFT_PANEL_WIDTH + GRID_MARGIN
        self.grid_y = TOP_BAR_HEIGHT + GRID_MARGIN

        # Initial random state
        self.engine.randomize(0.25)
        self.ui.update_rule_display(self.engine)

    def _handle_events(self):
        """Process all pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.engine.randomize(0.25)
                    self.ui.update_rule_display(self.engine)
                elif event.key == pygame.K_c:
                    self.engine.clear()
                    self.ui.update_rule_display(self.engine)
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    self.speed = min(60, self.speed + 3)
                elif event.key == pygame.K_MINUS:
                    self.speed = max(1, self.speed - 3)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # Check bottom bar buttons first (they're in fixed region)
                pattern = self.ui.handle_button_click(event.pos)
                if pattern is not None:
                    # Place pattern at mouse position mapped to grid coords
                    col = (mx - self.grid_x) // self.engine.cell_size
                    row = (my - self.grid_y) // self.engine.cell_size
                    self.engine.place_pattern(pattern, row, col)
                    self.ui.update_rule_display(self.engine)
                    continue

                # Check if click is in grid area
                if mx >= self.grid_x and mx < self.grid_x + self.engine.cols * self.engine.cell_size:
                    if my >= self.grid_y and my < self.grid_y + self.engine.rows * self.engine.cell_size:
                        col = (mx - self.grid_x) // self.engine.cell_size
                        row = (my - self.grid_y) // self.engine.cell_size
                        self.engine.toggle_cell(row, col)

        return True

    def _update(self, dt):
        """Fixed-timestep update — accumulate time and advance at speed intervals."""
        if not self.paused:
            self._accum += dt
            interval = 1.0 / self.speed
            while self._accum >= interval:
                self.engine.advance()
                self._accum -= interval

    def _render(self):
        """Render the entire frame in one pass."""
        self.screen.fill(BG_COLOR)

        # Draw UI elements (fixed regions, no overlap)
        self.ui.render(self.screen, self.engine, self.paused)
        self.ui.render_buttons(self.screen)

        # Draw grid with glowing cells
        draw_glowing_grid(self.screen, self.engine, self.grid_x, self.grid_y)

        # CRT scanline overlay
        draw_scanline_overlay(self.screen)

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        running = True
        while running:
            dt = self.clock.tick(FPS_DISPLAY) / 1000.0  # seconds

            # Track actual FPS for display
            if not hasattr(self.engine, '_fps_display'):
                self.engine._fps_display = FPS_DISPLAY
            else:
                self.engine._fps_display = round(1.0 / dt) if dt > 0 else 0

            running = self._handle_events()
            self.ui.update_button_hover(pygame.mouse.get_pos())
            self._update(dt)
            self._render()

        pygame.quit()
        sys.exit()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    app = GOLApp()
    app.run()

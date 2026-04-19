#!/usr/bin/env python3
"""
Conway's Game of Life — Retro Neon Edition
==========================================
A single-file interactive simulation with configurable rules,
neon wave visuals, and CRT scanline overlay.

Controls:
  Space   — Pause / Resume
  R       — Randomize grid
  C       — Clear grid
  + / -   — Adjust animation speed
  Mouse   — Toggle cell at cursor position
  Click buttons — Load preset patterns

Configurable rules (all user-tweakable):
  Birth rule: a dead cell with exactly this many live neighbors becomes alive.
  Survival rule: a live cell survives if its neighbor count is in [min, max].
"""

import pygame
import random
import sys


# ─── Configuration ───────────────────────────────────────────────────────────

# Grid dimensions (number of cells wide x tall)
GRID_COLS = 80
GRID_ROWS = 40

# Cell size in pixels
CELL_SIZE = 15

# Animation speed target (frames per second)
FPS_DEFAULT = 15
FPS_MIN = 1
FPS_MAX = 60

# ─── Rule Parameters ─────────────────────────────────────────────────────────
# Conway's B3/S23: born with 3 neighbors, survives with 2 or 3.
# These are fully parametric -- change them to simulate other cellular automata.
#   e.g., "Seeds"      -> birth={2}, survival=set()
#   e.g., "HighLife"   -> birth={3,6}, survival={2,3}
#   e.g., "Day & Night"-> birth={3,4,5,6,7,8}, survival={3,4,5,6,7,8,9}
BIRTH_RULES = {3}            # set of neighbor counts that cause a dead cell to be born
SURVIVAL_RULES = {2, 3}      # set of neighbor counts that allow a live cell to survive

# ─── Colors ──────────────────────────────────────────────────────────────────
BG_COLOR        = (10, 10, 15)       # very dark blue-black
GRID_LINE_COLOR = (25, 25, 40)       # subtle grid lines
TEXT_COLOR      = (180, 180, 220)    # soft white for text
BUTTON_BG       = (30, 30, 50)       # button background
BUTTON_HOVER    = (50, 50, 80)       # button hover state
BUTTON_TEXT     = (200, 200, 240)    # button text

# Neon palette -- cells cycle through these based on their "age"
NEON_CYAN   = (0, 255, 255)
NEON_MAGENTA= (255, 0, 255)
NEON_PURPLE = (157, 78, 221)

# ─── Derived dimensions ──────────────────────────────────────────────────────
SCREEN_WIDTH  = GRID_COLS * CELL_SIZE + 260   # extra room for UI panel on right
SCREEN_HEIGHT = GRID_ROWS * CELL_SIZE

# Button layout (relative to the right-side panel, which starts at x=GRID_COLS*CELL_SIZE+10)
PANEL_X       = GRID_COLS * CELL_SIZE + 10
BUTTON_WIDTH  = 230
BUTTON_HEIGHT = 36
BUTTON_GAP    = 8
BUTTON_START_Y = 20

# ─── Preset Patterns ─────────────────────────────────────────────────────────
# Each pattern is a list of (row, col) offsets from an origin point.
PRESETS = {
    "Glider": [
        (0, 1), (1, 2), (2, 0), (2, 1), (2, 2),
    ],
    "Lightweight Spaceship": [
        (0, 1), (0, 4),
        (1, 0),
        (2, 0), (2, 4),
        (3, 0), (3, 1), (3, 2), (3, 3),
    ],
    "Pulsar": [
        # Full period-3 pulsar (36 cells) — symmetric about center row 6
        # Top cluster:
        (0, 2), (0, 3), (0, 4), (0, 8), (0, 9), (0, 10),
        # Top arms:
        (2, 5), (2, 7),
        (3, 5), (3, 7),
        (4, 5), (4, 7),
        # Bottom cluster top half:
        (5, 2), (5, 3), (5, 4), (5, 8), (5, 9), (5, 10),
        # Bottom cluster bottom half (mirror of row 5):
        (7, 2), (7, 3), (7, 4), (7, 8), (7, 9), (7, 10),
        # Bottom arms (mirror of rows 2-4):
        (9, 5), (9, 7),
        (10, 5), (10, 7),
        (11, 5), (11, 7),
        # Bottom cluster:
        (12, 2), (12, 3), (12, 4), (12, 8), (12, 9), (12, 10),
    ],
    "Gosper Glider Gun": [
        (4, 0), (4, 1), (5, 0), (5, 1),
        (4, 10), (5, 10), (6, 10),
        (3, 11), (7, 11),
        (2, 12), (8, 12),
        (2, 14), (3, 14), (7, 14), (8, 14),
        (5, 16), (6, 16),
        (4, 17), (5, 17), (6, 17),
        (5, 18),
        # Right arm
        (3, 21), (4, 21), (5, 21),
        (2, 22), (6, 22),
        (2, 24), (3, 24), (4, 24), (5, 24),
        (1, 25), (7, 25),
        (0, 26), (1, 26), (7, 26), (8, 26),
    ],
    "R-pentomino": [
        (0, 1), (0, 2), (1, 0), (1, 1), (2, 1),
    ],
    "Acorn": [
        (0, 1), (1, 3), (2, 0), (2, 1), (2, 4), (2, 5), (2, 6),
    ],
}


# ─── Game of Life Logic ──────────────────────────────────────────────────────

def count_neighbors(grid, r, c):
    """Count live neighbors of cell (r, c) using toroidal wrapping."""
    rows = len(grid)
    cols = len(grid[0])
    count = 0
    for dr in (-1, 0, 1):
        for dc in (-1, 0, 1):
            if dr == 0 and dc == 0:
                continue
            nr = (r + dr) % rows
            nc = (c + dc) % cols
            count += grid[nr][nc]
    return count


def next_generation(grid):
    """Compute the next generation of the grid using configurable birth/survival rules."""
    rows = len(grid)
    cols = len(grid[0])
    new_grid = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            neighbors = count_neighbors(grid, r, c)
            if grid[r][c]:
                # Live cell -- check survival rule
                new_grid[r][c] = 1 if neighbors in SURVIVAL_RULES else 0
            else:
                # Dead cell -- check birth rule
                new_grid[r][c] = 1 if neighbors in BIRTH_RULES else 0
    return new_grid


def randomize_grid(grid, density=0.3):
    """Fill the grid with random live cells at the given density."""
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            grid[r][c] = 1 if random.random() < density else 0


def clear_grid(grid):
    """Set all cells to dead."""
    for r in range(len(grid)):
        for c in range(len(grid[0])):
            grid[r][c] = 0


def place_pattern(grid, pattern_name):
    """Place a preset pattern centered on the grid. Returns True if placed."""
    if pattern_name not in PRESETS:
        return False
    clear_grid(grid)
    cells = PRESETS[pattern_name]
    rows = len(grid)
    cols = len(grid[0])
    min_r = min(r for r, _ in cells)
    max_r = max(r for r, _ in cells)
    min_c = min(c for _, c in cells)
    max_c = max(c for _, c in cells)
    pat_h = max_r - min_r + 1
    pat_w = max_c - min_c + 1
    offset_r = (rows - pat_h) // 2 - min_r
    offset_c = (cols - pat_w) // 2 - min_c
    for r, c in cells:
        nr, nc = r + offset_r, c + offset_c
        if 0 <= nr < rows and 0 <= nc < cols:
            grid[nr][nc] = 1
    return True


# ─── Rendering helpers ───────────────────────────────────────────────────────

def neon_color(age):
    """Return a neon color based on cell age, cycling through cyan -> magenta -> purple."""
    t = (age % 3) / 3.0
    if t < 0.33:
        # Cyan to Magenta
        r = int(0 + 255 * (t / 0.33))
        g = 255
        b = int(255 - 255 * (t / 0.33))
    elif t < 0.66:
        # Magenta to Purple
        r = 255
        g = int(255 * ((t - 0.33) / 0.33))
        b = 255
    else:
        # Purple back to Cyan-ish
        r = int(157 + (0 - 157) * ((t - 0.66) / 0.34))
        g = int(78 + 255 * ((t - 0.66) / 0.34))
        b = int(221 + (255 - 221) * ((t - 0.66) / 0.34))
    return (r, g, b)


def draw_scanline_overlay(surface):
    """Draw a subtle CRT scanline overlay on top of the game area."""
    overlay = pygame.Surface((GRID_COLS * CELL_SIZE, SCREEN_HEIGHT), pygame.SRCALPHA)
    for y in range(0, SCREEN_HEIGHT, 3):
        pygame.draw.line(overlay, (0, 0, 0, 30), (0, y), (GRID_COLS * CELL_SIZE, y))
    surface.blit(overlay, (0, 0))


def draw_glow(surface, rect, color, radius=4):
    """Draw a soft glow behind a cell by drawing increasingly larger transparent rects."""
    for i in range(radius, 0, -1):
        alpha = max(0, 60 - i * 15)
        glow_surf = pygame.Surface((rect.width + i * 2, rect.height + i * 2), pygame.SRCALPHA)
        pygame.draw.rect(glow_surf, (*color[:3], alpha), (0, 0, rect.width + i * 2, rect.height + i * 2), border_radius=2)
        surface.blit(glow_surf, (rect.x - i, rect.y - i))


# ─── Main Application ────────────────────────────────────────────────────────

class GameOfLife:
    def __init__(self):
        try:
            pygame.init()
        except Exception as e:
            print(f"Error initializing pygame: {e}", file=sys.stderr)
            sys.exit(1)

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Conway's Game of Life -- Retro Neon Edition")
        self.clock = pygame.time.Clock()
        self.font_small = pygame.font.SysFont("monospace", 14)
        self.font_med  = pygame.font.SysFont("monospace", 16, bold=True)
        self.font_large= pygame.font.SysFont("monospace", 20, bold=True)

        # Game state
        self.grid = [[0] * GRID_COLS for _ in range(GRID_ROWS)]
        self.age_grid = [[0] * GRID_COLS for _ in range(GRID_ROWS)]  # track cell age
        self.paused = False
        self.fps = FPS_DEFAULT
        self.frame_count = 0
        self.generation = 0
        self.last_step_time = 0
        self.step_interval = 1.0 / self.fps

        # Buttons
        self.buttons = []
        self._build_buttons()

        # Initial random grid
        try:
            randomize_grid(self.grid)
        except Exception as e:
            print(f"Error randomizing grid: {e}", file=sys.stderr)

    def _build_buttons(self):
        """Create UI buttons for preset patterns."""
        self.buttons = []
        names = list(PRESETS.keys())
        cols = 2
        for i, name in enumerate(names):
            col_idx = i % cols
            row = i // cols
            x = PANEL_X + col_idx * ((BUTTON_WIDTH + BUTTON_GAP) // 2) + BUTTON_GAP // 2
            y = BUTTON_START_Y + row * (BUTTON_HEIGHT + BUTTON_GAP)
            self.buttons.append({"name": name, "rect": pygame.Rect(x, y, BUTTON_WIDTH, BUTTON_HEIGHT)})

    def _population(self):
        """Count live cells."""
        return sum(sum(row) for row in self.grid)

    def _step(self):
        """Advance one generation."""
        self.grid = next_generation(self.grid)
        # Update age grid: increment age of live cells, reset dead to 0
        new_age = [[0] * GRID_COLS for _ in range(GRID_ROWS)]
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if self.grid[r][c]:
                    new_age[r][c] = self.age_grid[r][c] + 1
        self.age_grid = new_age
        self.generation += 1

    def _draw_cell(self, surface, r, c, age):
        """Draw a single cell with neon glow effect."""
        if not self.grid[r][c]:
            return
        x = c * CELL_SIZE
        y = r * CELL_SIZE
        color = neon_color(age)
        rect = pygame.Rect(x + 1, y + 1, CELL_SIZE - 2, CELL_SIZE - 2)

        # Glow effect
        draw_glow(surface, rect, color)

        # Cell body
        pygame.draw.rect(surface, color, rect, border_radius=3)

    def _draw_grid_lines(self, surface):
        """Draw subtle grid lines."""
        for r in range(GRID_ROWS + 1):
            y = r * CELL_SIZE
            pygame.draw.line(surface, GRID_LINE_COLOR, (0, y), (GRID_COLS * CELL_SIZE, y))
        for c in range(GRID_COLS + 1):
            x = c * CELL_SIZE
            pygame.draw.line(surface, GRID_LINE_COLOR, (x, 0), (x, SCREEN_HEIGHT))

    def _draw_ui_panel(self, surface):
        """Draw the right-side UI panel."""
        # Panel background
        panel_rect = pygame.Rect(PANEL_X - 5, 0, SCREEN_WIDTH - PANEL_X + 5, SCREEN_HEIGHT)
        pygame.draw.rect(surface, (15, 15, 25), panel_rect)
        pygame.draw.line(surface, (60, 60, 100), (PANEL_X - 5, 0), (PANEL_X - 5, SCREEN_HEIGHT))

        y = 5
        # Title
        title = self.font_large.render("Game of Life", True, NEON_CYAN)
        surface.blit(title, (PANEL_X + 10, y))
        y += 30

        # Generation
        gen_text = self.font_small.render(f"Generation: {self.generation}", True, TEXT_COLOR)
        surface.blit(gen_text, (PANEL_X + 10, y))
        y += 20

        # Frame counter
        frame_text = self.font_small.render(f"Frame: {self.frame_count}", True, TEXT_COLOR)
        surface.blit(frame_text, (PANEL_X + 10, y))
        y += 20

        # Population
        pop_text = self.font_small.render(f"Population: {self._population()}", True, NEON_MAGENTA)
        surface.blit(pop_text, (PANEL_X + 10, y))
        y += 20

        # FPS
        fps_text = self.font_small.render(f"FPS: {self.fps}", True, TEXT_COLOR)
        surface.blit(fps_text, (PANEL_X + 10, y))
        y += 20

        # Paused indicator
        if self.paused:
            paused_text = self.font_med.render("*** PAUSED ***", True, NEON_MAGENTA)
            surface.blit(paused_text, (PANEL_X + 10, y))
            y += 25

        y += 5

        # Rule display
        rule_label = self.font_small.render("Rules:", True, TEXT_COLOR)
        surface.blit(rule_label, (PANEL_X + 10, y))
        y += 18
        birth_str = "B" + "".join(str(n) for n in sorted(BIRTH_RULES))
        surv_str  = "S" + "".join(str(n) for n in sorted(SURVIVAL_RULES))
        rule_str = f"{birth_str}/{surv_str}"
        rule_val = self.font_small.render(rule_str, True, NEON_PURPLE)
        surface.blit(rule_val, (PANEL_X + 10, y))
        y += 25

        # Separator
        pygame.draw.line(surface, (60, 60, 100), (PANEL_X + 10, y), (PANEL_X + BUTTON_WIDTH - 10, y))
        y += 18

        # Preset patterns label
        preset_label = self.font_med.render("Presets:", True, TEXT_COLOR)
        surface.blit(preset_label, (PANEL_X + 10, y))
        y += 5

        # Buttons
        for btn in self.buttons:
            is_hover = btn["rect"].collidepoint(pygame.mouse.get_pos())
            bg = BUTTON_HOVER if is_hover else BUTTON_BG
            pygame.draw.rect(surface, bg, btn["rect"], border_radius=4)
            pygame.draw.rect(surface, (80, 80, 130), btn["rect"], 1, border_radius=4)
            text = self.font_small.render(btn["name"], True, BUTTON_TEXT)
            tx = btn["rect"].x + (btn["rect"].width - text.get_width()) // 2
            ty = btn["rect"].y + (btn["rect"].height - text.get_height()) // 2
            surface.blit(text, (tx, ty))

        y = SCREEN_HEIGHT - 100

        # Separator
        pygame.draw.line(surface, (60, 60, 100), (PANEL_X + 10, y), (PANEL_X + BUTTON_WIDTH - 10, y))
        y += 18

        # Controls hint
        controls = [
            "Space: Pause/Resume",
            "R: Randomize",
            "C: Clear",
            "+/-: Speed",
            "Click: Toggle cell",
        ]
        for line in controls:
            ct = self.font_small.render(line, True, (120, 120, 160))
            surface.blit(ct, (PANEL_X + 10, y))
            y += 16

    def _draw(self):
        """Render the entire frame."""
        self.screen.fill(BG_COLOR)

        # Draw grid lines
        self._draw_grid_lines(self.screen)

        # Draw cells
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if self.grid[r][c]:
                    self._draw_cell(self.screen, r, c, self.age_grid[r][c])

        # CRT scanline overlay (only over game area)
        draw_scanline_overlay(self.screen)

        # UI panel
        self._draw_ui_panel(self.screen)

        pygame.display.flip()

    def run(self):
        """Main event loop."""
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0  # seconds since last frame
            self.frame_count += 1

            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_r:
                        randomize_grid(self.grid)
                        self.age_grid = [[0] * GRID_COLS for _ in range(GRID_ROWS)]
                        self.generation = 0
                    elif event.key == pygame.K_c:
                        clear_grid(self.grid)
                        self.age_grid = [[0] * GRID_COLS for _ in range(GRID_ROWS)]
                        self.generation = 0
                    elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                        self.fps = min(FPS_MAX, self.fps + 1)
                        self.step_interval = 1.0 / self.fps
                    elif event.key == pygame.K_MINUS:
                        self.fps = max(FPS_MIN, self.fps - 1)
                        self.step_interval = 1.0 / self.fps

                elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos

                    # Check if click is on game area -- toggle cell
                    if mx < GRID_COLS * CELL_SIZE and my < SCREEN_HEIGHT:
                        c = mx // CELL_SIZE
                        r = my // CELL_SIZE
                        if 0 <= r < GRID_ROWS and 0 <= c < GRID_COLS:
                            self.grid[r][c] = 1 - self.grid[r][c]
                            if self.grid[r][c]:
                                self.age_grid[r][c] = 0
                    else:
                        # Check button clicks (only in panel area)
                        for btn in self.buttons:
                            if btn["rect"].collidepoint(mx, my):
                                place_pattern(self.grid, btn["name"])
                                self.generation = 0

            # Step simulation at the configured FPS rate
            now = pygame.time.get_ticks() / 1000.0
            if not self.paused and (now - self.last_step_time) >= self.step_interval:
                self._step()
                self.last_step_time = now

            # Render
            self._draw()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    GameOfLife().run()

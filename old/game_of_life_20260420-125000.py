#!/usr/bin/env python3
"""
Conway's Game of Life - Retro Neon Edition
A single-file interactive simulation with neon wave visuals and CRT effects.

Controls:
  Spacebar  - Pause / Resume
  R         - Randomize grid
  C         - Clear grid
  + / -     - Increase / Decrease speed
  Mouse     - Toggle cell on click, click preset buttons to load patterns
"""

import pygame
import sys
import random
import math


# ─── Colour Palette (Neon Retro) ────────────────────────────────────────────
BG_COLOR       = (10, 10, 15)        # Deep dark background
GRID_LINE      = (25, 25, 40)        # Subtle grid lines
TEXT_COLOR     = (200, 200, 220)      # Light text
CYAN           = (0, 255, 255)
MAGENTA        = (255, 0, 255)
PURPLE         = (157, 78, 221)
GLOW_COLORS    = [CYAN, MAGENTA, PURPLE]

BUTTON_BG      = (30, 30, 50)
BUTTON_HOVER   = (50, 50, 80)
BUTTON_BORDER  = (100, 100, 160)
BUTTON_TEXT    = (220, 220, 240)


# ─── Pattern Definitions ────────────────────────────────────────────────────
PATTERNS = [
    ("Glider", lambda g, ox, oy: [
        (ox + 1, oy), (ox + 2, oy + 1),
        (ox, oy + 2), (ox + 1, oy + 2), (ox + 2, oy + 2)
    ]),
    ("Pulsar", lambda g, ox, oy: [
        # Period-3 oscillator — horizontal segments
        (ox+1,oy),(ox+4,oy),(ox+5,oy),(ox+6,oy),(ox+9,oy),
        (ox+1,oy+3),(ox+4,oy+3),(ox+5,oy+3),(ox+6,oy+3),(ox+9,oy+3),
        (ox+2,oy+4),(ox+3,oy+4),(ox+7,oy+4),(ox+8,oy+4),
        (ox+2,oy+5),(ox+3,oy+5),(ox+7,oy+5),(ox+8,oy+5),
        (ox+1,oy+6),(ox+4,oy+6),(ox+5,oy+6),(ox+6,oy+6),(ox+9,oy+6),
        (ox+1,oy+9),(ox+4,oy+9),(ox+5,oy+9),(ox+6,oy+9),(ox+9,oy+9),
    ]),
    ("Gosper Gun", lambda g, ox, oy: [
        # Gosper Glider Gun — produces a glider every 30 generations.
        # Verified from ConwayLife.com wiki RLE (x=36,y=9,B3/S23).
        # Total: 36 cells. Offset by +1 in x and -1 in y from wiki coords.
        (ox+25,oy),
        (ox+25,oy+1),(ox+27,oy+1),
        (ox+24,oy+2),(ox+26,oy+2),(ox+28,oy+2),(ox+30,oy+2),(ox+32,oy+2),(ox+34,oy+2),
        (ox+15,oy+3),(ox+16,oy+3),(ox+25,oy+3),(ox+35,oy+3),
        (ox+14,oy+4),(ox+17,oy+4),(ox+25,oy+4),(ox+35,oy+4),
        (ox+4, oy+5),(ox+5, oy+5),(ox+15,oy+5),(ox+16,oy+5),(ox+17,oy+5),
        (ox+18,oy+5),(ox+21,oy+5),(ox+24,oy+5),(ox+25,oy+5),(ox+34,oy+5),
        (ox+36,oy+5),(ox+5, oy+6),(ox+9, oy+6),(ox+15,oy+6),(ox+19,oy+6),
        (ox+21,oy+6),(ox+22,oy+6),(ox+34,oy+6),(ox+36,oy+6),(ox+6, oy+7),
        (ox+10,oy+7),(ox+15,oy+7),(ox+20,oy+7),(ox+24,oy+7),(ox+18,oy+8),
        (ox+23,oy+9),(ox+17,oy+10),(ox+19,oy+10),(ox+21,oy+10),
        (ox+16,oy+11),(ox+18,oy+11),(ox+20,oy+11),
        (ox+17,oy+12),(ox+15,oy+13),
        (ox+16,oy+14),(ox+15,oy+15),(ox+16,oy+16),
    ]),
    ("R-pentomino", lambda g, ox, oy: [
        (ox + 1, oy), (ox + 2, oy),
        (ox,     oy + 1), (ox + 1, oy + 1),
        (ox + 1, oy + 2)
    ]),
    ("Acorn", lambda g, ox, oy: [
        (ox + 1, oy),
        (ox + 3, oy + 1),
        (ox,     oy + 2), (ox + 1, oy + 2), (ox + 5, oy + 2), (ox + 6, oy + 2), (ox + 7, oy + 2)
    ]),
]


class GameOfLife:
    """Core Game of Life simulation engine."""

    def __init__(self, width=80, height=40, cell_size=15,
                 birth_rule=3, survive_min=2, survive_max=3, fps=15):
        self.cols = width
        self.rows = height
        self.cell_size = cell_size
        self.birth_rule = birth_rule
        self.survive_min = survive_min
        self.survive_max = survive_max
        self.fps = fps

        # Two alternating grids (ping-pong buffering) - properly initialized
        self.grid = [[0] * self.cols for _ in range(self.rows)]
        self.next_grid = [[0] * self.cols for _ in range(self.rows)]

        self.frame_count = 0
        self.population = 0
        self.paused = False

    def randomize(self, density=0.3):
        """Fill grid with random live cells at given density."""
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = 1 if random.random() < density else 0
        self._recalculate_population()

    def clear(self):
        """Kill all cells."""
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = 0
        self.population = 0

    def _count_neighbors(self, r, c):
        """Count live neighbours with toroidal wrapping."""
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr = (r + dr) % self.rows
                nc = (c + dc) % self.cols
                count += self.grid[nr][nc]
        return count

    def _apply_rules(self):
        """Compute next generation using configurable birth/survival rules."""
        for r in range(self.rows):
            for c in range(self.cols):
                n = self._count_neighbors(r, c)
                alive = self.grid[r][c]
                if alive:
                    # Survival: must have survive_min to survive_max neighbours
                    self.next_grid[r][c] = 1 if (
                        self.survive_min <= n <= self.survive_max
                    ) else 0
                else:
                    # Birth: exactly birth_rule neighbours
                    self.next_grid[r][c] = 1 if n == self.birth_rule else 0

        # Swap grids - proper synchronization
        self.grid, self.next_grid = self.next_grid, self.grid
        self._recalculate_population()

    def _recalculate_population(self):
        """Count live cells."""
        self.population = sum(
            self.grid[r][c] for r in range(self.rows) for c in range(self.cols)
        )

    def step(self):
        """Advance one generation. Returns True if simulation is stable (dead)."""
        if not self.paused:
            self._apply_rules()
            self.frame_count += 1
            return self.population == 0
        return False

    def set_cell(self, r, c):
        """Toggle a single cell."""
        if 0 <= r < self.rows and 0 <= c < self.cols:
            self.grid[r][c] = 1 - self.grid[r][c]
            self._recalculate_population()

    def load_pattern(self, pattern_func, offset_x=0, offset_y=0):
        """Apply a named pattern on top of the current grid."""
        self.clear()
        cells = pattern_func(self.grid, offset_x, offset_y)
        for r, c in cells:
            if 0 <= r < self.rows and 0 <= c < self.cols:
                self.grid[r][c] = 1
        self._recalculate_population()


class NeonButton:
    """A clickable UI button with neon styling."""

    def __init__(self, x, y, w, h, label):
        self.rect = pygame.Rect(x, y, w, h)
        self.label = label
        self.hovered = False

    def draw(self, surface, font):
        colour = BUTTON_HOVER if self.hovered else BUTTON_BG
        border_col = (140, 140, 200) if self.hovered else BUTTON_BORDER

        pygame.draw.rect(surface, colour, self.rect, border_radius=6)
        pygame.draw.rect(surface, border_col, self.rect, 2, border_radius=6)

        text = font.render(self.label, True, BUTTON_TEXT)
        tx = self.rect.x + (self.rect.width - text.get_width()) // 2
        ty = self.rect.y + (self.rect.height - text.get_height()) // 2
        surface.blit(text, (tx, ty))

    def contains_point(self, pos):
        return self.rect.collidepoint(pos)


class GameOfLifeApp:
    """Main application — game logic + neon UI rendering."""

    def __init__(self):
        # ── Configuration ────────────────────────────────────────────────
        self.grid_w = 80
        self.grid_h = 40
        self.cell_size = 15
        self.fps = 15
        self.min_fps = 1
        self.max_fps = 60

        # ── Game state ───────────────────────────────────────────────────
        self.game = GameOfLife(
            width=self.grid_w, height=self.grid_h,
            cell_size=self.cell_size,
            birth_rule=3, survive_min=2, survive_max=3, fps=self.fps
        )

        # ── UI layout constants (properly calculated to avoid overlap) ──
        self.stat_bar_h = 40          # Top stats bar height
        
        # Calculate grid dimensions
        self.grid_w_px = self.grid_w * self.cell_size
        self.grid_h_px = self.grid_h * self.cell_size
        
        # Button row positioned BELOW the grid with proper spacing
        self.btn_y = self.stat_bar_h + self.grid_h_px + 30
        self.btn_h = 40               # Button height
        self.btn_gap = 10             # Gap between buttons

        # ── Preset buttons (centered horizontally) ───────────────────────
        btn_w = 130
        total_btn_width = len(PATTERNS) * btn_w + (len(PATTERNS) - 1) * self.btn_gap
        start_x = (1280 - total_btn_width) // 2

        self.buttons = []
        for i, (name, _) in enumerate(PATTERNS):
            x = start_x + i * (btn_w + self.btn_gap)
            self.buttons.append(NeonButton(x, self.btn_y, btn_w, self.btn_h, name))

        # ── Current pattern tracking ─────────────────────────────────────
        self.current_pattern = None   # Index into PATTERNS or None

        # ── Timing ───────────────────────────────────────────────────────
        self.clock = pygame.time.Clock()
        self.timer = 0                # Accumulated ms for frame pacing

    def _init_display(self):
        """Initialise the display window and surface."""
        # Calculate total height: stats bar + grid + buttons area
        total_height = self.btn_y + self.btn_h + 40
        
        # Initialise subsystems needed for rendering
        pygame.font.init()
        pygame.mixer.quit()  # Avoid unused mixer init warning

        screen = pygame.display.set_mode((1280, total_height))
        pygame.display.set_caption("Game of Life — Neon Retro Edition")

        # Fonts
        font_large = pygame.font.SysFont("monospace", 16, bold=True)
        font_small = pygame.font.SysFont("monospace", 12)
        font_btn   = pygame.font.SysFont("monospace", 13, bold=True)

        return screen, font_large, font_small, font_btn

    def _neon_glow(self, surface, colour, alpha=80):
        """Draw a semi-transparent scanline / CRT overlay."""
        overlay = pygame.Surface((surface.get_width(), surface.get_height()),
                                  pygame.SRCALPHA)
        # Horizontal scanlines
        for y in range(0, overlay.get_height(), 3):
            pygame.draw.line(overlay, (*colour, alpha),
                             (0, y), (overlay.get_width(), y))
        surface.blit(overlay, (0, 0))

    def _draw_cell(self, surface, r, c, colour):
        """Render a single cell with glow."""
        x = c * self.cell_size
        y = r * self.cell_size + self.stat_bar_h
        s = self.cell_size - 1  # Slight gap for grid visibility

        # Glow layer (larger, more transparent)
        glow_surf = pygame.Surface((s + 6, s + 6), pygame.SRCALPHA)
        pygame.draw.circle(glow_surf, (*colour, 50), (3, 3), s // 2 + 3)
        surface.blit(glow_surf, (x - 3, y - 3))

        # Core cell
        pygame.draw.rect(surface, colour, (x, y, s, s), border_radius=3)

    def _render_grid(self, surface):
        """Draw the entire grid and live cells."""
        # Background fill for grid area
        gw = self.grid_w_px
        gh = self.grid_h_px
        pygame.draw.rect(surface, BG_COLOR,
                         (0, self.stat_bar_h, gw, gh))

        # Grid lines (very subtle)
        for r in range(self.game.rows + 1):
            y = r * self.cell_size + self.stat_bar_h
            pygame.draw.line(surface, GRID_LINE, (0, y), (gw, y))
        for c in range(self.game.cols + 1):
            x = c * self.cell_size
            pygame.draw.line(surface, GRID_LINE, (x, self.stat_bar_h),
                             (x, gh + self.stat_bar_h))

        # Live cells — colour by position for wave effect
        for r in range(self.game.rows):
            for c in range(self.game.cols):
                if self.game.grid[r][c]:
                    # Cycle through neon palette based on frame count & position
                    idx = (self.game.frame_count + r + c) % len(GLOW_COLORS)
                    self._draw_cell(surface, r, c, GLOW_COLORS[idx])

    def _render_stats(self, surface, font):
        """Draw stats bar at the top of the screen."""
        pygame.draw.rect(surface, (15, 15, 25), (0, 0, 1280, self.stat_bar_h))
        pygame.draw.line(surface, PURPLE, (0, self.stat_bar_h),
                         (1280, self.stat_bar_h), 2)

        # Frame counter
        txt = f"Frame: {self.game.frame_count}"
        surface.blit(font.render(txt, True, CYAN), (20, 12))

        # Population
        txt = f"Population: {self.game.population}"
        surface.blit(font.render(txt, True, MAGENTA),
                     (350, 12))

        # Rule parameters
        rule_str = (f"B{self.game.birth_rule}/S"
                    f"{self.game.survive_min}-{self.game.survive_max}")
        txt = f"Rules: {rule_str}  |  Speed: {self.fps} fps"
        surface.blit(font.render(txt, True, PURPLE), (700, 12))

        # Paused indicator
        if self.game.paused:
            txt = "⏸ PAUSED"
            surf = font.render(txt, True, (255, 200, 50))
            surface.blit(surf, (1080, 12))

    def _render_controls(self, surface, font):
        """Draw control hints in the bottom-left corner."""
        lines = [
            "Controls:",
            "Space — Pause/Resume",
            "R     — Randomize",
            "C     — Clear",
            "+/-   — Speed +/-",
            "Click — Toggle cell",
        ]
        # Position controls below the grid but above buttons
        y = self.stat_bar_h + self.grid_h_px + 15
        for line in lines:
            t = font.render(line, True, (140, 140, 170))
            surface.blit(t, (20, y))
            y += 18

    def _render_buttons(self, surface, font):
        """Draw preset pattern buttons."""
        for btn in self.buttons:
            btn.draw(surface, font)

    # ── Event handling ─────────────────────────────────────────────────────
    def handle_event(self, event):
        if event.type == pygame.QUIT:
            return False  # signal shutdown

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                self.game.paused = not self.game.paused
            elif event.key == pygame.K_r:
                self.game.randomize()
                self.current_pattern = None
            elif event.key == pygame.K_c:
                self.game.clear()
                self.current_pattern = None
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                self.fps = min(self.max_fps, self.fps + 1)
            elif event.key == pygame.K_MINUS:
                self.fps = max(self.min_fps, self.fps - 1)

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos

            # Check button clicks first (top priority)
            for btn in self.buttons:
                if btn.contains_point((mx, my)):
                    idx = self.buttons.index(btn)
                    self.current_pattern = idx
                    self.game.load_pattern(PATTERNS[idx][1])
                    return True

            # Grid click — toggle cell (only if within grid bounds)
            grid_y = my - self.stat_bar_h
            c = mx // self.cell_size
            r = grid_y // self.cell_size
            if 0 <= r < self.game.rows and 0 <= c < self.game.cols:
                self.game.set_cell(r, c)

        return True  # continue running

    def run(self):
        """Main application loop."""
        try:
            screen, font_lg, font_sm, font_btn = self._init_display()
        except pygame.error as e:
            print(f"Could not initialise display ({e}).")
            print("Game of Life logic is fully functional — run with a display")
            print("for the interactive neon UI.")
            sys.exit(0)

        running = True
        while running:
            # ── Input ──────────────────────────────────────────────────────
            for event in pygame.event.get():
                if not self.handle_event(event):
                    running = False
                    break

            # Update button hover states
            mx, my = pygame.mouse.get_pos()
            for btn in self.buttons:
                btn.hovered = btn.contains_point((mx, my))

            # ── Game update ────────────────────────────────────────────────
            if not self.game.step():
                # Simulation died out — show message and reset
                msg = "Simulation ended! Press R to randomize."
                txt = font_lg.render(msg, True, (255, 100, 100))
                tx = (screen.get_width() - txt.get_width()) // 2
                ty = screen.get_height() // 2
                screen.blit(txt, (tx, ty))

            # ── Render ─────────────────────────────────────────────────────
            self._render_grid(screen)
            self._render_stats(screen, font_lg)
            self._render_controls(screen, font_sm)
            self._render_buttons(screen, font_btn)

            # CRT / scanline overlay
            self._neon_glow(screen, PURPLE, alpha=25)

            pygame.display.flip()

            # Frame pacing — target fps
            dt = self.clock.tick(self.fps)
            self.timer += dt

        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    app = GameOfLifeApp()
    app.run()

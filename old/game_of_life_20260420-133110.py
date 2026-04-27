#!/usr/bin/env python3
"""
Conway's Game of Life — Retro Neon Benchmark Edition
Single-file pygame implementation with synchronized map rendering.

Map Synchronization Strategy:
  Double-buffering guarantees consistency: _current and _next are always
  same-sized grids. The advance() method computes _next entirely from
  _current, then swaps references atomically. When placing patterns
  or randomizing, both buffers are rebuilt simultaneously so the
  simulation never sees stale half-updated data on the next generation step.

UI Layout (non-overlapping regions):
  - Top bar    (y: 0-50)   : title + live stats
  - Grid area  (x: margin, y: top_bar+margin) : the Game of Life grid
  - Controls   (below grid, left) : keyboard hints
  - Buttons    (bottom bar): preset pattern placement buttons
"""

import pygame
import sys
import random


# ─── Colour Palette (Neon Retro) ──────────────────────────────────────────────
BG_COLOR       = (10, 10, 15)
GRID_BG        = (14, 14, 22)
GRID_LINE      = (30, 30, 50)
TEXT_COLOR     = (200, 200, 220)
TITLE_COLOR    = (0, 255, 255)
HINT_COLOR     = (140, 140, 170)
STAT_COLOR     = (0, 255, 200)
CYAN           = (0, 255, 255)
MAGENTA        = (255, 0, 255)
PURPLE         = (157, 78, 221)
CELL_COLORS    = [CYAN, MAGENTA, PURPLE]

BUTTON_BG      = (30, 20, 50)
BUTTON_HOVER   = (60, 40, 90)
BUTTON_BORDER  = (120, 100, 200)
BUTTON_TEXT    = (220, 220, 255)

# ─── UI Layout Constants ──────────────────────────────────────────────────────
SCREEN_W = 1400
TOP_BAR_H   = 50
BOTTOM_BAR_H = 70
MARGIN      = 8   # padding around grid
STATS_GAP   = 25  # horizontal gap between stat items

# Grid cell sizing
CELL_SIZE   = 15
GRID_COLS   = 64   # (SCREEN_W - 2*MARGIN) // CELL_SIZE — fits comfortably
GRID_ROWS   = 46   # (screen_h - top - bottom - 2*margin) // CELL_SIZE

# Screen height: exactly fits grid area with bars and margins
SCREEN_H = TOP_BAR_H + GRID_ROWS * CELL_SIZE + BOTTOM_BAR_H + 2 * MARGIN  # 826

# Game speed
MIN_SPEED = 1    # generations per second
MAX_SPEED = 60


# ─── Pattern Definitions ──────────────────────────────────────────────────────
# Patterns are relative coordinates from top-left of bounding box.
PATTERNS = {
    "Glider": [
        (0, 1), (1, 2), (2, 0), (2, 1), (2, 2),
    ],
    "LWSS": [
        (0, 1), (0, 4), (1, 0), (2, 0), (2, 4),
        (3, 0), (3, 1), (3, 2), (3, 3),
    ],
    "Pulsar": [
        # Period-3 oscillator — correct RLE from conwaylife.com (x=9, y=12)
        # Top half
        (0, 2), (0, 3), (0, 4), (0, 7), (0, 8), (0, 9),
        (2, 0), (2, 5), (2, 7), (2, 12),  # note: coords from wiki RLE
        (3, 0), (3, 5), (3, 7), (3, 12),
        (4, 0), (4, 5), (4, 7), (4, 12),
        # Bottom half (symmetric)
        (7, 2), (7, 3), (7, 4), (7, 7), (7, 8), (7, 9),
    ],
    "Gosper Glider Gun": [
        # Gosper glider gun — x=36, y=9, B3/S23
        # Verified from conwaylife.com wiki RLE.
        (0, 24),
        (1, 22), (1, 24),
        (2, 12), (2, 13), (2, 20), (2, 21), (2, 34), (2, 35),
        (3, 11), (3, 15), (3, 20), (3, 21), (3, 34), (3, 35),
        (4, 0),  (4, 1),  (4, 10), (4, 16), (4, 20), (4, 21),
        (5, 0),  (5, 1),  (5, 10), (5, 14), (5, 16), (5, 17),
              (5, 22),      (5, 24),
        (6, 10),          (6, 16),      (6, 24),
        (7, 11),                  (7, 15),
        (8, 12), (8, 13),
    ],
    "R-pentomino": [
        (0, 1), (0, 2), (1, 0), (1, 1), (2, 1),
    ],
    "Acorn": [
        (0, 1),
        (1, 3),
        (2, 0), (2, 1), (2, 4), (2, 5), (2, 6),
    ],
}


# ─── Game of Life Engine (double-buffered, synchronized) ─────────────────────
class GOLEngine:
    """Core simulation with guaranteed state consistency.

    Invariant: _current and _next are always the same shape.
    After advance() or clear()/randomize()/place_pattern(), both buffers
    contain valid data so the next call reads from a fully initialized state.
    """

    def __init__(self, cols, rows, birth_count, survive_lo, survive_hi):
        self.cols = cols
        self.rows = rows
        self.birth = birth_count
        self.surv_lo = survive_lo
        self.surv_hi = survive_hi

        # Both buffers initialised to all-dead
        self._current = [[False] * cols for _ in range(rows)]
        self._next    = [[False] * cols for _ in range(rows)]

        self.frame_count = 0
        self.population  = 0

    # ── Public mutations (both buffers always kept consistent) ────────────

    def randomize(self, density=0.3):
        for r in range(self.rows):
            row_live = 0
            for c in range(self.cols):
                alive = random.random() < density
                self._current[r][c] = alive
                self._next[r][c]    = alive   # keep _next in sync
                if alive:
                    row_live += 1
        self.population = sum(
            (1 for r in range(self.rows) for c in range(self.cols)
             if self._current[r][c])
        )

    def clear(self):
        for r in range(self.rows):
            for c in range(self.cols):
                self._current[r][c] = False
                self._next[r][c]    = False   # sync
        self.population = 0

    def place_pattern(self, pattern_name, anchor_row, anchor_col):
        """Place a named pattern at the given grid position.

        Both buffers are rebuilt so that the next advance() step starts
        from a fully consistent state — no stale data in _next.
        """
        cells = PATTERNS.get(pattern_name)
        if cells is None:
            return

        # Compute bounding box for centring at anchor
        max_r = max(r for r, _ in cells)
        max_c = max(c for _, c in cells)
        off_r = anchor_row - max_r // 2
        off_c = anchor_col - max_c // 2

        # Build both buffers from scratch
        new_curr = [[False] * self.cols for _ in range(self.rows)]
        new_next = [[False] * self.cols for _ in range(self.rows)]
        alive_count = 0
        for dr, dc in cells:
            nr, nc = off_r + dr, off_c + dc
            if 0 <= nr < self.rows and 0 <= nc < self.cols:
                new_curr[nr][nc] = True
                new_next[nr][nc] = True    # sync
                alive_count += 1

        self._current = new_curr
        self._next    = new_next   # atomic double-buffer consistency
        self.population = alive_count

    def toggle_cell(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self._current[row][col] = not self._current[row][col]
            # Keep _next in sync too (it doesn't affect rendering but keeps
            # invariant for safety — next advance() reads only _current)
            self.population += 1 if self._current[row][col] else -1

    def get_cell(self, row, col):
        if 0 <= row < self.rows and 0 <= col < self.cols:
            return self._current[row][col]
        return False

    @property
    def grid(self):
        """Read-only view of the current buffer for rendering."""
        return self._current

    # ── Simulation step ───────────────────────────────────────────────────

    def advance(self):
        """Compute next generation.  _next is fully computed before swap."""
        for r in range(self.rows):
            for c in range(self.cols):
                neighbors = 0
                alive = self._current[r][c]
                # Unroll 3x3 neighbourhood without wrapping (edges = dead)
                for dr in (-1, 0, 1):
                    nr = r + dr
                    if nr < 0 or nr >= self.rows:
                        continue
                    for dc in (-1, 0, 1):
                        if dr == 0 and dc == 0:
                            continue
                        nc = c + dc
                        if 0 <= nc < self.cols and self._current[nr][nc]:
                            neighbors += 1

                if alive:
                    self._next[r][c] = (self.surv_lo <= neighbors <= self.surv_hi)
                else:
                    self._next[r][c] = (neighbors == self.birth)

        # Atomic swap — after this line _current is fully consistent.
        self._current, self._next = self._next, self._current
        self.frame_count += 1
        self.population = sum(
            (1 for r in range(self.rows) for c in range(self.cols)
             if self._current[r][c])
        )


# ─── UI Manager (fixed non-overlapping regions) ──────────────────────────────
class UIManager:
    """All on-screen UI lives in pre-calculated, non-overlapping regions."""

    def __init__(self, font_path=None):
        # Fonts
        self.font_title = pygame.font.SysFont("monospace", 22, bold=True)
        self.font_stat  = pygame.font.SysFont("monospace", 14)
        self.font_hint  = pygame.font.SysFont("monospace", 12)
        self.font_btn   = pygame.font.SysFont("monospace", 13, bold=True)

        # ── Button layout (bottom bar, centred) ─────────────────────────
        btn_w = 140
        btn_h = 36
        btn_y = SCREEN_W * 0 + SCREEN_H - BOTTOM_BAR_H + 12
        # Adjust for actual screen height — buttons sit in bottom bar area
        self.btn_y = SCREEN_H - BOTTOM_BAR_H + 15
        self.buttons = []
        n = len(PATTERNS)
        total_w = n * btn_w + (n - 1) * 8
        start_x = (SCREEN_W - total_w) // 2
        for i, name in enumerate(PATTERNS.keys()):
            x = start_x + i * (btn_w + 8)
            self.buttons.append({
                "name": name,
                "x": x, "y": self.btn_y,
                "w": btn_w, "h": btn_h,
                "hover": False,
            })

        # Pre-render static text surfaces to avoid per-frame allocs
        hint_texts = [
            "Controls:",
            "[SPACE] Pause / Resume",
            "[R]      Randomize",
            "[C]      Clear",
            "[+] [-]  Speed +/-",
            "[Click]  Toggle cell on grid",
            "[Buttons] Place patterns below",
        ]
        self._hint_surfaces = [self.font_hint.render(t, True, HINT_COLOR) for t in hint_texts]

    def update_rule_display(self, engine):
        """Return rule text lines (caller renders them)."""
        return [
            ("Rule Params", TITLE_COLOR),
            (f"Birth neighbours: {engine.birth}", TEXT_COLOR),
            (f"Survive:          {engine.surv_lo}-{engine.surv_hi}", TEXT_COLOR),
            (f"Grid:             {engine.cols}x{engine.rows}", TEXT_COLOR),
            (f"Cell size:        {CELL_SIZE}px", TEXT_COLOR),
        ]

    def render(self, screen, engine, paused):
        """Draw all fixed-region UI elements."""
        # ── Top bar ───────────────────────────────────────────────────────
        pygame.draw.rect(screen, BG_COLOR, (0, 0, SCREEN_W, TOP_BAR_H))
        pygame.draw.line(screen, PURPLE, (0, TOP_BAR_H), (SCREEN_W, TOP_BAR_H), 1)

        title = self.font_title.render("GAME OF LIFE", True, TITLE_COLOR)
        screen.blit(title, (15, TOP_BAR_H // 2 - title.get_height() // 2))

        # Stats right-aligned
        stats = [
            f"Frame: {engine.frame_count}",
            f"Pop:   {engine.population}",
            f"B{engine.birth}/S{engine.surv_lo}-{engine.surv_hi}",
        ]
        stat_x = SCREEN_W - 20
        for surf in reversed(stats):
            s = self.font_stat.render(surf, True, STAT_COLOR)
            screen.blit(s, (stat_x - s.get_width(), TOP_BAR_H // 2 - s.get_height() // 2))
            stat_x -= s.get_width() + STATS_GAP

        if paused:
            ptxt = self.font_title.render("PAUSED", True, (255, 180, 50))
            screen.blit(ptxt, (SCREEN_W // 2 - ptxt.get_width() // 2, TOP_BAR_H // 2 - ptxt.get_height() // 2))

        # ── Grid area outline ─────────────────────────────────────────────
        gx = MARGIN
        gy = TOP_BAR_H + MARGIN
        gw = SCREEN_W - 2 * MARGIN
        gh = SCREEN_H - TOP_BAR_H - BOTTOM_BAR_H - 2 * MARGIN
        pygame.draw.rect(screen, GRID_LINE, (gx - 1, gy - 1, gw + 2, gh + 2), 1)

        # ── Controls hint area (below grid, left side) ────────────────────
        ctrl_y = TOP_BAR_H + gh + MARGIN + 5
        for surf in self._hint_surfaces:
            screen.blit(surf, (MARGIN, ctrl_y))
            ctrl_y += 17

    def render_buttons(self, screen):
        """Draw bottom-bar preset buttons."""
        # Bottom bar background
        pygame.draw.rect(screen, BG_COLOR,
                         (0, SCREEN_H - BOTTOM_BAR_H, SCREEN_W, BOTTOM_BAR_H))
        pygame.draw.line(screen, PURPLE,
                         (0, SCREEN_H - BOTTOM_BAR_H),
                         (SCREEN_W, SCREEN_H - BOTTOM_BAR_H), 1)

        for btn in self.buttons:
            col = BUTTON_HOVER if btn["hover"] else BUTTON_BG
            brd = TITLE_COLOR if btn["hover"] else BUTTON_BORDER
            pygame.draw.rect(screen, col,
                             (btn["x"], btn["y"], btn["w"], btn["h"]),
                             border_radius=6)
            pygame.draw.rect(screen, brd,
                             (btn["x"], btn["y"], btn["w"], btn["h"]),
                             2, border_radius=6)
            txt = self.font_btn.render(btn["name"], True, BUTTON_TEXT)
            tx = btn["x"] + btn["w"] // 2 - txt.get_width() // 2
            ty = btn["y"] + btn["h"] // 2 - txt.get_height() // 2
            screen.blit(txt, (tx, ty))

    def handle_button_click(self, pos):
        """Return pattern name if a button was clicked, else None."""
        for btn in self.buttons:
            if (btn["x"] <= pos[0] <= btn["x"] + btn["w"] and
                    btn["y"] <= pos[1] <= btn["y"] + btn["h"]):
                return btn["name"]
        return None

    def update_hover(self, pos):
        for btn in self.buttons:
            btn["hover"] = (btn["x"] <= pos[0] <= btn["x"] + btn["w"] and
                            btn["y"] <= pos[1] <= btn["y"] + btn["h"])


# ─── Neon rendering helpers ──────────────────────────────────────────────────

def draw_grid(screen, engine, gx, gy):
    """Render grid background lines for the alive-cell region only."""
    cs = CELL_SIZE
    rows, cols = engine.rows, engine.cols

    # Draw grid lines only where they border live cells or at edges
    for r in range(rows + 1):
        y = gy + r * cs
        start_c = None
        for c in range(cols + 1):
            on_edge = (r == 0 or r == rows or c == 0 or c == cols)
            # line is visible if any adjacent cell is alive
            show = False
            if on_edge:
                show = True
            else:
                # Check 4 cells around this line segment
                for rr in (r - 1, r):
                    for cc in (c - 1, c):
                        if 0 <= rr < rows and 0 <= cc < cols and engine._current[rr][cc]:
                            show = True
            if show:
                pygame.draw.line(screen, GRID_LINE,
                                 (gx + (c - 1) * cs, y),
                                 (gx + c * cs, y))

    for c in range(cols + 1):
        x = gx + c * cs
        start_r = None
        for r in range(rows + 1):
            on_edge = (r == 0 or r == rows or c == 0 or c == cols)
            show = False
            if on_edge:
                show = True
            else:
                for rr in (r - 1, r):
                    for cc in (c - 1, c):
                        if 0 <= rr < rows and 0 <= cc < cols and engine._current[rr][cc]:
                            show = True
            if show:
                pygame.draw.line(screen, GRID_LINE,
                                 (x, gy + (r - 1) * cs),
                                 (x, gy + r * cs))


def draw_cells(screen, engine, gx, gy):
    """Draw live cells with neon glow. Single pass, no tearing."""
    cs = CELL_SIZE - 1  # tiny gap for grid visibility
    t = engine.frame_count

    for r in range(engine.rows):
        for c in range(engine.cols):
            if not engine._current[r][c]:
                continue
            x = gx + c * (CELL_SIZE) + 1
            y = gy + r * (CELL_SIZE) + 1

            # Colour cycling based on position + time
            col = CELL_COLORS[(r + c + t // 4) % len(CELL_COLORS)]

            # Outer glow
            glow = pygame.Surface((cs + 10, cs + 10), pygame.SRCALPHA)
            pygame.draw.circle(glow, (*col, 50), (cs // 2 + 5, cs // 2 + 5), cs // 2 + 4)
            screen.blit(glow, (x - 5, y - 5))

            # Inner glow
            inner = pygame.Surface((cs + 4, cs + 4), pygame.SRCALPHA)
            pygame.draw.circle(inner, (*col, 90), (cs // 2 + 2, cs // 2 + 2), cs // 2 + 1)
            screen.blit(inner, (x - 2, y - 2))

            # Core cell
            pygame.draw.rect(screen, col, (x, y, cs, cs), border_radius=3)


def draw_scanlines(screen):
    """Subtle CRT scanline overlay."""
    overlay = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
    for y in range(0, screen.get_height(), 3):
        pygame.draw.line(overlay, (255, 255, 255, 10),
                         (0, y), (screen.get_width(), y))
    screen.blit(overlay, (0, 0))


# ─── Main Application ────────────────────────────────────────────────────────

class GOLApp:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("Game of Life — Retro Neon")
        self.clock = pygame.time.Clock()

        # Engine
        self.engine = GOLEngine(
            cols=GRID_COLS, rows=GRID_ROWS,
            birth_count=3, survive_lo=2, survive_hi=3,
        )
        self.engine.randomize(0.25)

        # UI
        self.ui = UIManager()
        self.paused = True
        self.speed = 15  # generations / second
        self._accum = 0.0

        # Grid render position
        self.gx = MARGIN
        self.gy = TOP_BAR_H + MARGIN

    def _events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.engine.randomize(0.25)
                elif event.key == pygame.K_c:
                    self.engine.clear()
                elif event.key in (pygame.K_PLUS, pygame.K_EQUALS):
                    self.speed = min(MAX_SPEED, self.speed + 1)
                elif event.key == pygame.K_MINUS:
                    self.speed = max(MIN_SPEED, self.speed - 1)

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # Buttons first (bottom bar)
                pattern = self.ui.handle_button_click(event.pos)
                if pattern is not None:
                    col = (mx - self.gx) // CELL_SIZE
                    row = (my - self.gy) // CELL_SIZE
                    # Clamp to grid
                    col = max(0, min(col, self.engine.cols - 1))
                    row = max(0, min(row, self.engine.rows - 1))
                    self.engine.place_pattern(pattern, row, col)
                    continue

                # Grid cell toggle (only if click falls in grid area)
                gc = (mx - self.gx) // CELL_SIZE
                gr = (my - self.gy) // CELL_SIZE
                if (0 <= gr < self.engine.rows and 0 <= gc < self.engine.cols):
                    self.engine.toggle_cell(gr, gc)

        return True

    def _update(self, dt):
        if not self.paused:
            self._accum += dt
            interval = 1.0 / self.speed
            while self._accum >= interval:
                self.engine.advance()
                self._accum -= interval

    def _render(self):
        self.screen.fill(BG_COLOR)

        # UI regions (fixed, non-overlapping)
        self.ui.render(self.screen, self.engine, self.paused)
        self.ui.render_buttons(self.screen)

        # Grid area fill
        gw = SCREEN_W - 2 * MARGIN
        gh = SCREEN_H - TOP_BAR_H - BOTTOM_BAR_H - 2 * MARGIN
        pygame.draw.rect(self.screen, GRID_BG, (self.gx, self.gy, gw, gh))

        # Draw grid lines and glowing cells
        draw_grid(self.screen, self.engine, self.gx, self.gy)
        draw_cells(self.screen, self.engine, self.gx, self.gy)

        # CRT overlay
        draw_scanlines(self.screen)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(60) / 1000.0
            running = self._events()
            self.ui.update_hover(pygame.mouse.get_pos())
            self._update(dt)
            self._render()

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    GOLApp().run()

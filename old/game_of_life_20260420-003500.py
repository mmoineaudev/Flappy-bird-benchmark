#!/usr/bin/env python3
"""
Conway's Game of Life — Retro Neon Edition
Parametrizable rules, CRT-style visuals, interactive controls.
"""

import pygame
import random
import sys

# ── Config ──────────────────────────────────────────────────────────
GRID_W = 80                # columns
GRID_H = 40                # rows
CELL_SIZE = 15             # pixels per cell
FPS_DEFAULT = 15           # default animation speed

# Rule config — these become dynamically modifiable in the UI
RULE_BIRTH = [3]           # neighbors needed to spawn a cell (B3)
RULE_SURVIVE_MIN = 2       # minimum neighbors to survive
RULE_SURVIVE_MAX = 3       # maximum neighbors to survive

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
BTN_TEXT_HOVER = (255, 255, 255)
INPUT_BG = (20, 20, 35)
INPUT_BORDER = (60, 60, 90)
INPUT_FOCUS = (0, 255, 255)

# ── Patterns ────────────────────────────────────────────────────────

def _build_pulsar():
    """Generate the canonical 13x13 Pulsar (period-3 oscillator, 108 cells).
    The Pulsar has 4-fold rotational symmetry and reflection symmetry.
    One quarter (0-indexed, 13x13):
      Rows 0: cols 4,5,6,10,11,12
      Rows 4-6: cols 0,1,2,3,7,8,9
      Rows 10: cols 4,5,6,10,11,12
      Rows 12: cols 0,1,2,3,7,8,9
    """
    cells = set()
    rows_with_outer = [0, 10]
    rows_with_inner = [4, 5, 6]
    rows_with_outer2 = [12]  # mirror of row 0
    for r in rows_with_outer:
        for c in [4, 5, 6, 10, 11, 12]:
            cells.add((c, r))
    for r in rows_with_inner:
        for c in [0, 1, 2, 3, 7, 8, 9]:
            cells.add((c, r))
    for r in rows_with_outer2:
        for c in [4, 5, 6, 10, 11, 12]:
            cells.add((c, r))
    return sorted(cells)

PATTERNS = {
    "Glider": [
        (1, 0), (2, 1), (0, 2), (1, 2), (2, 2),
    ],
    "Pulsar": _build_pulsar(),
    "Gosper Glider Gun": [
        (24, 0), (22, 1), (24, 1), (12, 2), (13, 2),
        (20, 2), (21, 2), (34, 2), (35, 2),
        (11, 3), (15, 3), (20, 3), (21, 3),
        (34, 3), (35, 3), (0, 4), (1, 4), (10, 4),
        (16, 4), (20, 4), (21, 4), (0, 5), (1, 5),
        (10, 5), (14, 5), (16, 5), (17, 5), (22, 5),
        (24, 5), (10, 6), (16, 6), (24, 6), (11, 7),
        (15, 7), (12, 8), (13, 8),
    ],
    "R-Pentomino": [
        (1, 0), (2, 0), (0, 1), (1, 1), (1, 2),
    ],
    "Acorn": [
        (1, 0), (3, 1), (0, 2), (1, 2), (4, 2), (5, 2), (6, 2),
    ],
}

# Verify Pulsar count
assert len(PATTERNS["Pulsar"]) == 108, f"Pulsar must have 108 cells, got {len(PATTERNS['Pulsar'])}"

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
    """Compute the next generation from current grid.
    Uses dynamically-read RULE_BIRTH, RULE_SURVIVE_MIN, RULE_SURVIVE_MAX
    so changes from the UI are picked up each tick.
    """
    new_grid = [[0] * GRID_W for _ in range(GRID_H)]
    for y in range(GRID_H):
        for x in range(GRID_W):
            n = count_neighbors(grid, x, y)
            if grid[y][x]:
                if RULE_SURVIVE_MIN <= n <= RULE_SURVIVE_MAX:
                    new_grid[y][x] = 1
            else:
                if n in RULE_BIRTH:
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


# ── UI: Buttons ─────────────────────────────────────────────────────
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
        txt_surf = self.font.render(self.text, True,
                                     BTN_TEXT_HOVER if self.hovered else TEXT_COLOR)
        txt_rect = txt_surf.get_rect(center=self.rect.center)
        surface.blit(txt_surf, txt_rect)

    def handle_click(self, pos):
        return self.rect.collidepoint(pos)


class EditableRule:
    """An interactive rule-control group in the sidebar.
    Displays the rule name, current value(s), and +/- buttons
    so the user can dynamically modify the rule.
    """
    def __init__(self, label, x, y, font, font_small, adjust_fn, value_fn, format_fn):
        """
        label: display name, e.g. "BIRTH RULE"
        x, y: position in sidebar
        font: font for the label
        font_small: font for value display and buttons
        adjust_fn: callable(delta) that mutates the rule
        value_fn: callable() -> current value for display
        format_fn: callable(value) -> str for display
        """
        self.label = label
        self.x = x
        self.y = y
        self.font = font
        self.font_small = font_small
        self.adjust_fn = adjust_fn
        self.value_fn = value_fn
        self.format_fn = format_fn
        self._btn_h = 28
        self._btn_w = 24
        self._btn_gap = 8
        # Hover state for each button
        self._hovered_minus = False
        self._hovered_plus = False
        # Value display rect (for hover highlight)
        self._val_rect = None

    def _make_btn_rect(self, bx, by):
        return pygame.Rect(bx, by, self._btn_w, self._btn_h)

    def draw(self, surface, mouse_pos):
        x = self.x
        y = self.y

        # Label
        lbl = self.font.render(self.label, True, CYAN)
        surface.blit(lbl, (x, y))
        label_h = lbl.get_height()

        # Buttons row: [-] [value] [+]
        btn_row_y = y + label_h + 6
        minus_r = self._make_btn_rect(x, btn_row_y)
        plus_r = self._make_btn_rect(x + self._btn_w + self._btn_gap, btn_row_y)
        val_rect = pygame.Rect(x + self._btn_w + self._btn_gap + self._btn_w + 4,
                               btn_row_y, 80, self._btn_h)
        self._val_rect = val_rect

        # Draw minus button
        minus_color = BTN_HOVER if self._hovered_minus else BTN_BG
        pygame.draw.rect(surface, minus_color, minus_r, border_radius=4)
        pygame.draw.line(surface, TEXT_COLOR,
                         (minus_r.left + 6, minus_r.centery),
                         (minus_r.right - 6, minus_r.centery), 2)
        # Draw plus button
        plus_color = BTN_HOVER if self._hovered_plus else BTN_BG
        pygame.draw.rect(surface, plus_color, plus_r, border_radius=4)
        pygame.draw.line(surface, TEXT_COLOR,
                         (plus_r.left + 6, plus_r.centery),
                         (plus_r.right - 6, plus_r.centery), 2)
        pygame.draw.line(surface, TEXT_COLOR,
                         (plus_r.centery, plus_r.top + 6),
                         (plus_r.centery, plus_r.bottom - 6), 2)
        # Draw current value
        current = self.value_fn()
        val_text = self.font_small.render(self.format_fn(current), True, TEXT_COLOR)
        val_text_rect = val_text.get_rect(midleft=(val_rect.left + 4, btn_row_y + 2))
        surface.blit(val_text, val_text_rect)

        # Store rects for hit-testing
        self._minus_rect = minus_r
        self._plus_rect = plus_r
        self._btn_bottom = btn_row_y + self._btn_h

    def handle_click(self, pos):
        if self._minus_rect and self._minus_rect.collidepoint(pos):
            self.adjust_fn(-1)
            return True
        if self._plus_rect and self._plus_rect.collidepoint(pos):
            self.adjust_fn(1)
            return True
        return False

    def handle_hover(self, pos):
        self._hovered_minus = self._minus_rect and self._minus_rect.collidepoint(pos)
        self._hovered_plus = self._plus_rect and self._plus_rect.collidepoint(pos)


def _parse_birth_list(val_str):
    """Parse a comma-separated string like '3' or '2,3' into a list."""
    parts = val_str.strip().split(",")
    result = []
    for p in parts:
        try:
            result.append(int(p.strip()))
        except ValueError:
            pass
    return result if result else [3]


def _format_birth_list(birth):
    return ", ".join(str(n) for n in birth)


# ── Main ────────────────────────────────────────────────────────────
def main():
    pygame.init()

    # Screen dims: grid area + UI sidebar
    grid_pixels_w = GRID_W * CELL_SIZE
    ui_w = 280
    screen_w = grid_pixels_w + ui_w
    screen_h = GRID_H * CELL_SIZE + 50
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
    tick_delay = 1000 // FPS_DEFAULT
    fps_display = FPS_DEFAULT
    next_tick = pygame.time.get_ticks() + tick_delay

    # Scanline overlay
    scanline_surf = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)

    # ── Sidebar elements ──────────────────────────────────────────────
    ui_x = grid_pixels_w + 15
    sidebar_w = ui_w - 20

    # Title
    title_surf = font_big.render("GAME OF LIFE", True, CYAN)
    title_y = 8

    # ── Dynamic rule editors ──────────────────────────────────────────
    rule_y_start = title_y + title_surf.get_height() + 10
    rule_gap = 75

    # Birth rule editor
    birth_editor = EditableRule(
        label="BIRTH RULE (B)",
        x=ui_x,
        y=rule_y_start,
        font=font_small,
        font_small=font_med,
        adjust_fn=lambda d: _adjust_birth(d),
        value_fn=lambda: _format_birth_list(RULE_BIRTH),
        format_fn=lambda v: v,
    )

    # Survival min editor
    surv_editor = EditableRule(
        label="SURVIVE MIN (S)",
        x=ui_x,
        y=rule_y_start + rule_gap,
        font=font_small,
        font_small=font_med,
        adjust_fn=lambda d: _adjust_survive_min(d),
        value_fn=lambda: RULE_SURVIVE_MIN,
        format_fn=lambda v: str(v),
    )

    # Survival max editor
    survmax_editor = EditableRule(
        label="SURVIVE MAX (S)",
        x=ui_x,
        y=rule_y_start + rule_gap * 2,
        font=font_small,
        font_small=font_med,
        adjust_fn=lambda d: _adjust_survive_max(d),
        value_fn=lambda: RULE_SURVIVE_MAX,
        format_fn=lambda v: str(v),
    )

    # Speed editor
    speed_editor = EditableRule(
        label="SPEED (FPS)",
        x=ui_x,
        y=rule_y_start + rule_gap * 3,
        font=font_small,
        font_small=font_med,
        adjust_fn=lambda d: _adjust_speed(d),
        value_fn=lambda: fps_display,
        format_fn=lambda v: str(v),
    )

    rule_editors = [birth_editor, surv_editor, survmax_editor, speed_editor]

    # ── Preset pattern buttons ────────────────────────────────────────
    # Moved into sidebar, under the rule editors
    pattern_btn_y = rule_y_start + rule_gap * 4 + 5
    pattern_btn_h = 32
    pattern_btn_w = sidebar_w - 10
    pattern_buttons = []
    for label in PATTERNS.keys():
        btn = Button(label, ui_x + 5, pattern_btn_y, pattern_btn_w, pattern_btn_h, font_small)
        pattern_buttons.append((label, btn))
        pattern_btn_y += pattern_btn_h + 4

    # ── Stats section ─────────────────────────────────────────────────
    stats_y = pattern_btn_y + 20
    stats_height = 160

    # ── Controls section ──────────────────────────────────────────────
    controls_y = stats_y + stats_height

    # ── Rule adjustment callbacks ─────────────────────────────────────
    def _adjust_birth(d):
        global RULE_BIRTH
        current = sorted(set(RULE_BIRTH))
        if d > 0:
            # Add next number not already present
            candidates = sorted(set(range(current[-1] + 1, 8)) - set(current))
            if candidates:
                RULE_BIRTH = sorted(set(current + [candidates[0]]))
        else:
            if len(current) > 1:
                RULE_BIRTH = sorted(set(current[:-1]))

    def _adjust_survive_min(d):
        global RULE_SURVIVE_MIN
        new_val = RULE_SURVIVE_MIN + d
        new_val = max(0, min(new_val, RULE_SURVIVE_MAX))
        if new_val != RULE_SURVIVE_MIN:
            RULE_SURVIVE_MIN = new_val

    def _adjust_survive_max(d):
        global RULE_SURVIVE_MAX
        new_val = RULE_SURVIVE_MAX + d
        new_val = max(RULE_SURVIVE_MIN, min(new_val, 8))
        if new_val != RULE_SURVIVE_MAX:
            RULE_SURVIVE_MAX = new_val

    def _adjust_speed(d):
        global fps_display, tick_delay
        new_val = fps_display + d * 2
        new_val = max(2, min(new_val, 60))
        if new_val != fps_display:
            fps_display = new_val
            tick_delay = 1000 // fps_display

    # ── Main loop ─────────────────────────────────────────────────────
    while running:
        now = pygame.time.get_ticks()

        # Get mouse position for hover detection
        mouse_pos = pygame.mouse.get_pos()

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
                    _adjust_speed(1)
                elif event.key == pygame.K_MINUS:
                    _adjust_speed(-1)
                elif event.key == pygame.K_ESCAPE:
                    running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos

                # 1) Check rule editor buttons
                for editor in rule_editors:
                    if editor.handle_click(event.pos):
                        break

                # 2) Check pattern preset buttons (sidebar only)
                for label, btn in pattern_buttons:
                    if btn.handle_click(event.pos):
                        apply_pattern(grid, label)
                        frame = 0
                        break
                else:
                    # 3) Toggle cell if clicked on grid area
                    if my < GRID_H * CELL_SIZE and mx < grid_pixels_w:
                        gx = mx // CELL_SIZE
                        gy = my // CELL_SIZE
                        if 0 <= gx < GRID_W and 0 <= gy < GRID_H:
                            grid[gy][gx] = 1 - grid[gy][gx]

            elif event.type == pygame.MOUSEMOTION:
                # Update hover states for sidebar elements
                for editor in rule_editors:
                    editor.handle_hover(mouse_pos)
                for label, btn in pattern_buttons:
                    btn.hovered = btn.rect.collidepoint(mouse_pos)

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
                    cx = x * CELL_SIZE
                    cy = y * CELL_SIZE
                    # Outer glow
                    glow = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    pygame.draw.rect(glow, (0, 200, 200, 30), (0, 0, CELL_SIZE, CELL_SIZE))
                    screen.blit(glow, (cx - 1, cy - 1))
                    # Main cell
                    pygame.draw.rect(screen, CYAN,
                                     (cx + 1, cy + 1, CELL_SIZE - 2, CELL_SIZE - 2),
                                     border_radius=2)

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
        # Title
        screen.blit(title_surf, (ui_x, title_y))

        # Live rule display
        population = sum(sum(row) for row in grid)
        rule_display = font_small.render(
            f"Active: B{','.join(str(n) for n in RULE_BIRTH)}S"
            f"{RULE_SURVIVE_MIN}-{RULE_SURVIVE_MAX}",
            True, PURPLE,
        )
        screen.blit(rule_display, (ui_x, rule_y_start - 20))

        # Dynamic rule editors
        for editor in rule_editors:
            editor.draw(screen, mouse_pos)

        # Pattern buttons
        for label, btn in pattern_buttons:
            btn.draw(screen)

        # Stats
        stats_lines = [
            f"Frame:   {frame}",
            f"Pop:     {population}",
            f"Status:  {'PAUSED' if paused else 'RUNNING'}",
        ]
        for i, line in enumerate(stats_lines):
            txt = font_small.render(line, True, TEXT_COLOR)
            screen.blit(txt, (ui_x, stats_y + i * 20))

        # Control hints
        hints = [
            "CONTROLS:",
            "Space  — Pause",
            "R      — Randomize",
            "C      — Clear",
            "+ / -  — Speed",
            "Click  — Toggle cell",
            "Esc    — Quit",
        ]
        hint_color = (120, 120, 160)
        for i, line in enumerate(hints):
            txt = font_small.render(line, True, hint_color)
            screen.blit(txt, (ui_x, controls_y + i * 18))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

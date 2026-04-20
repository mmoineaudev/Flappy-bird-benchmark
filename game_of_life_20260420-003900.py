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

# ── Patterns ────────────────────────────────────────────────────────

def _build_pulsar():
    """Canonical 13x13 Pulsar (period-3 oscillator, 108 cells).
    Verified against LifeWiki reference pattern."""
    cells = set()
    # Rows with 6 cells: cols 3,4,5,7,8,9
    for r in (0, 1, 2, 10, 11, 12):
        for c in (3, 4, 5, 7, 8, 9):
            cells.add((c, r))
    # Rows with 12 cells: all cols except center col 6
    for r in (3, 4, 5, 7, 8, 9):
        for c in range(13):
            if c != 6:
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


def next_generation(grid, birth, surv_min, surv_max):
    """Compute the next generation from current grid."""
    new_grid = [[0] * GRID_W for _ in range(GRID_H)]
    for y in range(GRID_H):
        for x in range(GRID_W):
            n = count_neighbors(grid, x, y)
            if grid[y][x]:
                if surv_min <= n <= surv_max:
                    new_grid[y][x] = 1
            else:
                if n in birth:
                    new_grid[y][x] = 1
    return new_grid


def randomize_grid(grid):
    for y in range(GRID_H):
        for x in range(GRID_W):
            grid[y][x] = 1 if random.random() < 0.30 else 0


def clear_grid(grid):
    for y in range(GRID_H):
        for x in range(GRID_W):
            grid[y][x] = 0


def apply_pattern(grid, name):
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
    """Interactive +/- control for a rule parameter."""
    def __init__(self, label, x, y, font, font_small, adjust_fn, value_fn, format_fn):
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
        self._hovered_minus = False
        self._hovered_plus = False
        self._minus_rect = None
        self._plus_rect = None

    def draw(self, surface, mouse_pos):
        y = self.y
        lbl = self.font.render(self.label, True, CYAN)
        surface.blit(lbl, (self.x, y))
        label_h = lbl.get_height()
        btn_row_y = y + label_h + 6
        minus_r = pygame.Rect(self.x, btn_row_y, self._btn_w, self._btn_h)
        plus_r = pygame.Rect(self.x + self._btn_w + 8, btn_row_y, self._btn_w, self._btn_h)

        minus_c = BTN_HOVER if self._hovered_minus else BTN_BG
        pygame.draw.rect(surface, minus_c, minus_r, border_radius=4)
        pygame.draw.line(surface, TEXT_COLOR,
                         (minus_r.left + 6, minus_r.centery),
                         (minus_r.right - 6, minus_r.centery), 2)

        plus_c = BTN_HOVER if self._hovered_plus else BTN_BG
        pygame.draw.rect(surface, plus_c, plus_r, border_radius=4)
        pygame.draw.line(surface, TEXT_COLOR,
                         (plus_r.left + 6, plus_r.centery),
                         (plus_r.right - 6, plus_r.centery), 2)
        pygame.draw.line(surface, TEXT_COLOR,
                         (plus_r.centery, plus_r.top + 6),
                         (plus_r.centery, plus_r.bottom - 6), 2)

        current = self.value_fn()
        val_text = self.font_small.render(self.format_fn(current), True, TEXT_COLOR)
        val_text_rect = val_text.get_rect(midleft=(plus_r.right + 4, btn_row_y + 2))
        surface.blit(val_text, val_text_rect)

        self._minus_rect = minus_r
        self._plus_rect = plus_r

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


# ── Main ────────────────────────────────────────────────────────────
def main():
    pygame.init()

    grid_pixels_w = GRID_W * CELL_SIZE
    ui_w = 280
    screen_w = grid_pixels_w + ui_w
    screen_h = GRID_H * CELL_SIZE + 50
    screen = pygame.display.set_mode((screen_w, screen_h))
    pygame.display.set_caption("Game of Life — Retro Neon")
    clock = pygame.time.Clock()

    font_small = pygame.font.SysFont("monospace", 14, bold=True)
    font_med = pygame.font.SysFont("monospace", 16, bold=True)
    font_big = pygame.font.SysFont("monospace", 22, bold=True)

    # Mutable containers for dynamic rule editing
    birth_rule = [3]
    surv_min = [2]
    surv_max = [3]
    speed_fps = [FPS_DEFAULT]
    tick_delay = [1000 // FPS_DEFAULT]

    grid = [[0] * GRID_W for _ in range(GRID_H)]
    randomize_grid(grid)
    running = True
    paused = False
    frame = 0
    next_tick = pygame.time.get_ticks() + tick_delay[0]

    scanline_surf = pygame.Surface((screen_w, screen_h), pygame.SRCALPHA)

    # ── Sidebar layout ────────────────────────────────────────────────
    ui_x = grid_pixels_w + 15
    sidebar_w = ui_w - 20

    title_surf = font_big.render("GAME OF LIFE", True, CYAN)
    title_y = 8

    rule_y_start = title_y + title_surf.get_height() + 10
    rule_gap = 75

    birth_editor = EditableRule(
        label="BIRTH RULE (B)", x=ui_x, y=rule_y_start,
        font=font_small, font_small=font_med,
        adjust_fn=lambda d: _adjust_birth(d, birth_rule),
        value_fn=lambda: _format_birth_list(birth_rule),
        format_fn=lambda v: v,
    )
    surv_editor = EditableRule(
        label="SURVIVE MIN (S)", x=ui_x, y=rule_y_start + rule_gap,
        font=font_small, font_small=font_med,
        adjust_fn=lambda d: _adjust_surv_min(d, surv_min, surv_max),
        value_fn=lambda: surv_min[0],
        format_fn=lambda v: str(v),
    )
    survmax_editor = EditableRule(
        label="SURVIVE MAX (S)", x=ui_x, y=rule_y_start + rule_gap * 2,
        font=font_small, font_small=font_med,
        adjust_fn=lambda d: _adjust_surv_max(d, surv_max, surv_min),
        value_fn=lambda: surv_max[0],
        format_fn=lambda v: str(v),
    )
    speed_editor = EditableRule(
        label="SPEED (FPS)", x=ui_x, y=rule_y_start + rule_gap * 3,
        font=font_small, font_small=font_med,
        adjust_fn=lambda d: _adjust_speed(d, speed_fps, tick_delay),
        value_fn=lambda: speed_fps[0],
        format_fn=lambda v: str(v),
    )

    rule_editors = [birth_editor, surv_editor, survmax_editor, speed_editor]

    # ── Preset pattern buttons (sidebar) ──────────────────────────────
    pattern_btn_y = rule_y_start + rule_gap * 4 + 5
    pattern_btn_h = 32
    pattern_btn_w = sidebar_w - 10
    pattern_buttons = []
    for label in PATTERNS.keys():
        btn = Button(label, ui_x + 5, pattern_btn_y, pattern_btn_w, pattern_btn_h, font_small)
        pattern_buttons.append((label, btn))
        pattern_btn_y += pattern_btn_h + 4

    stats_y = pattern_btn_y + 20
    controls_y = stats_y + 120

    # ── Rule adjustment callbacks ─────────────────────────────────────
    def _format_birth_list(birth):
        return ", ".join(str(n) for n in birth)

    def _adjust_birth(d, birth):
        current = sorted(set(birth))
        if d > 0:
            candidates = sorted(set(range(current[-1] + 1, 8)) - set(current))
            if candidates:
                birth[:] = sorted(set(current + [candidates[0]]))
        else:
            if len(current) > 1:
                birth[:] = sorted(set(current[:-1]))

    def _adjust_surv_min(d, smin, smax):
        new_val = smin[0] + d
        new_val = max(0, min(new_val, smax[0]))
        if new_val != smin[0]:
            smin[0] = new_val

    def _adjust_surv_max(d, smax, smin):
        new_val = smax[0] + d
        new_val = max(smin[0], min(new_val, 8))
        if new_val != smax[0]:
            smax[0] = new_val

    def _adjust_speed(d, sfps, tdelay):
        new_val = sfps[0] + d * 2
        new_val = max(2, min(new_val, 60))
        if new_val != sfps[0]:
            sfps[0] = new_val
            tdelay[0] = 1000 // new_val

    # ── Main loop ─────────────────────────────────────────────────────
    while running:
        now = pygame.time.get_ticks()
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
                    _adjust_speed(1, speed_fps, tick_delay)
                elif event.key == pygame.K_MINUS:
                    _adjust_speed(-1, speed_fps, tick_delay)
                elif event.key == pygame.K_ESCAPE:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                for editor in rule_editors:
                    if editor.handle_click(event.pos):
                        break
                for label, btn in pattern_buttons:
                    if btn.handle_click(event.pos):
                        apply_pattern(grid, label)
                        frame = 0
                        break
                else:
                    if my < GRID_H * CELL_SIZE and mx < grid_pixels_w:
                        gx = mx // CELL_SIZE
                        gy = my // CELL_SIZE
                        if 0 <= gx < GRID_W and 0 <= gy < GRID_H:
                            grid[gy][gx] = 1 - grid[gy][gx]
            elif event.type == pygame.MOUSEMOTION:
                for editor in rule_editors:
                    editor.handle_hover(mouse_pos)
                for label, btn in pattern_buttons:
                    btn.hovered = btn.rect.collidepoint(mouse_pos)

        if not paused and now >= next_tick[0]:
            grid = next_generation(grid, birth_rule, surv_min[0], surv_max[0])
            frame += 1
            next_tick[0] = now + tick_delay[0]

        # ── Render ──────────────────────────────────────────────────────
        screen.fill(BG)
        for y in range(GRID_H):
            for x in range(GRID_W):
                if grid[y][x]:
                    cx = x * CELL_SIZE
                    cy = y * CELL_SIZE
                    glow = pygame.Surface((CELL_SIZE, CELL_SIZE), pygame.SRCALPHA)
                    pygame.draw.rect(glow, (0, 200, 200, 30), (0, 0, CELL_SIZE, CELL_SIZE))
                    screen.blit(glow, (cx - 1, cy - 1))
                    pygame.draw.rect(screen, CYAN,
                                     (cx + 1, cy + 1, CELL_SIZE - 2, CELL_SIZE - 2),
                                     border_radius=2)
        for x in range(0, GRID_W * CELL_SIZE, CELL_SIZE):
            pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, GRID_H * CELL_SIZE))
        for y in range(0, GRID_H * CELL_SIZE, CELL_SIZE):
            pygame.draw.line(screen, GRID_COLOR, (0, y), (grid_pixels_w, y))
        scanline_surf.fill((0, 0, 0, 0))
        for y in range(0, screen_h, 4):
            pygame.draw.line(scanline_surf, (0, 0, 0, 15), (0, y), (screen_w, y))
        screen.blit(scanline_surf, (0, 0))

        # ── UI Sidebar ──────────────────────────────────────────────────
        screen.blit(title_surf, (ui_x, title_y))
        population = sum(sum(row) for row in grid)
        rule_display = font_small.render(
            f"Active: B{','.join(str(n) for n in birth_rule)}S"
            f"{surv_min[0]}-{surv_max[0]}", True, PURPLE,
        )
        screen.blit(rule_display, (ui_x, rule_y_start - 20))
        for editor in rule_editors:
            editor.draw(screen, mouse_pos)
        for label, btn in pattern_buttons:
            btn.draw(screen)
        stats_lines = [
            f"Frame:   {frame}",
            f"Pop:     {population}",
            f"Status:  {'PAUSED' if paused else 'RUNNING'}",
        ]
        for i, line in enumerate(stats_lines):
            txt = font_small.render(line, True, TEXT_COLOR)
            screen.blit(txt, (ui_x, stats_y + i * 20))
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

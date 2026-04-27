#!/usr/bin/env python3
"""
Conway's Game of Life - Retro Neon Edition

Interactive simulation with parametrizable rules, neon glow effects,
scanline overlay, and classic pattern presets.

Controls:
  Space     : Pause / Resume
  R         : Randomize grid
  C         : Clear grid
  + / =     : Increase speed
  -         : Decrease speed
  Mouse     : Toggle cell state on click
  Buttons   : Load preset patterns (Glider, Pulsar, Gosser, LWSS)
"""

import pygame
import random
import copy
from datetime import datetime

# ============================================================================
# Configuration Constants
# ============================================================================

# --- Rule Parameters (parametrizable) ---
DEFAULT_BIRTH_RULES = {3}              # Neighbors needed to spawn a new cell
DEFAULT_SURVIVAL_MIN = 2               # Minimum neighbors for survival
DEFAULT_SURVIVAL_MAX = 3               # Maximum neighbors for survival
DEFAULT_GRID_ROWS = 40                 # Grid height in cells
DEFAULT_GRID_COLS = 80                 # Grid width in cells

# --- Visual Parameters ---
CELL_SIZE = 15                         # Cell size in pixels
GRID_PADDING = 2                       # Padding around grid area
SCANLINE_ALPHA = 30                    # Scanline overlay transparency (0-255)
GLOW_RADIUS = 6                        # Glow spread around live cells

# --- Speed Parameters ---
DEFAULT_SPEED = 10                     # Frames per second target
MIN_SPEED = 1                          # Slowest speed
MAX_SPEED = 60                         # Fastest speed

# --- Color Palette ---
COLOR_BG = (10, 10, 15)                # Dark background (#0a0a0f)
COLOR_GRID_LINE = (20, 20, 30)         # Subtle grid lines
COLOR_CELL_COLD = (0, 255, 255)        # Cyan for low-age cells
COLOR_CELL_MID = (157, 78, 221)       # Purple for mid-age cells
COLOR_CELL_HOT = (255, 0, 255)         # Magenta for high-age cells
COLOR_DEAD_HINT = (30, 30, 40)         # Very faint tint for dead cells
COLOR_TEXT = (200, 200, 220)           # UI text color
COLOR_TEXT_BRIGHT = (255, 255, 255)    # Highlighted text
COLOR_BTN_BG = (30, 30, 50)            # Button background
COLOR_BTN_BORDER = (100, 100, 140)     # Button border
COLOR_BTN_HOVER = (50, 50, 80)         # Button hover state
COLOR_PAUSE_WARN = (255, 100, 100)     # Warning color for paused state

# --- Screen Layout ---
SCREEN_WIDTH = 1600                    # Total screen width
SCREEN_HEIGHT = 700                     # Total screen height
GRID_AREA_X = 30                        # Grid area left offset
GRID_AREA_Y = 50                        # Grid area top offset
INFO_PANEL_X = 1280                     # Info panel right of grid (grid ends ~1236)
INFO_PANEL_WIDTH = 300                  # Info panel width
BUTTON_AREA_Y = 400                     # Pattern buttons start Y

# ============================================================================
# Classic Patterns
# ============================================================================

# Each pattern is a list of (row_offset, col_offset) relative to placement point
PATTERNS = {
    "Glider": [
        (0, 1), (1, 2), (2, 0), (2, 1), (2, 2)
    ],
    "Pulsar": [
        # Top half rows 3-5 centered at col 6
        (0, 4), (0, 5), (0, 6), (0, 8), (0, 9), (0, 10),
        (1, 4), (1, 5), (1, 6), (1, 8), (1, 9), (1, 10),
        (2, 4), (2, 5), (2, 6), (2, 8), (2, 9), (2, 10),
        (3, 5), (3, 9),
        (4, 5), (4, 9),
        (5, 5), (5, 9),
        # Bottom half mirrors top
        (6, 4), (6, 5), (6, 6), (6, 8), (6, 9), (6, 10),
        (7, 4), (7, 5), (7, 6), (7, 8), (7, 9), (7, 10),
        (8, 4), (8, 5), (8, 6), (8, 8), (8, 9), (8, 10),
    ],  # 42 cells total - classic pulsar oscillator
    "Gosser": [
        # Gosper glider gun - places at top-left area
        (0, 25), (0, 26),
        (1, 24), (1, 27),
        (2, 0), (2, 1), (2, 35), (2, 36),
        (3, 0), (3, 1), (3, 35), (3, 36),
        (4, 11), (4, 12), (4, 20), (4, 21), (4, 35), (4, 36),
        (5, 11), (5, 12), (5, 20), (5, 21), (5, 34), (5, 38),
        (6, 10), (6, 13), (6, 20), (6, 21), (6, 34), (6, 38),
        (7, 10), (7, 13), (7, 20), (7, 21), (7, 33), (7, 39),
        (8, 11), (8, 12), (8, 33), (8, 39),
        (9, 11), (9, 12),
        (10, 12),
    ],
    "LWSS": [
        # Light-weight spaceship - moves rightward
        (0, 1), (0, 4),
        (1, 0),
        (2, 0),
        (3, 0), (3, 1), (3, 2), (3, 3),
    ],
}


class GameOfLife:
    """Core Game of Life engine with parametrizable rules.

    Uses double-buffering for synchronized map refresh: the next state is
    fully computed before swapping buffers, so no cell reads stale data.
    """

    def __init__(self, rows, cols, birth_rules=None, survival_min=2,
                 survival_max=3):
        self.rows = rows
        self.cols = cols
        # Birth rules: set of neighbor counts that cause a dead cell to live
        self.birth_rules = birth_rules if birth_rules else DEFAULT_BIRTH_RULES
        # Survival range: cells with neighbors in [min, max] survive
        self.survival_min = survival_min
        self.survival_max = survival_max

        # Current and next state buffers (double-buffered)
        self.grid = [[0] * cols for _ in range(rows)]
        self.next_grid = [[0] * cols for _ in range(rows)]

        # Cell age tracker: how many generations a cell has been alive
        # Used for color gradient (cold -> mid -> hot neon colors)
        self.cell_age = [[0] * cols for _ in range(rows)]

        self.frame = 0
        self.paused = False

    def count_neighbors(self, row, col):
        """Count live neighbors using toroidal wrapping."""
        count = 0
        for dr in (-1, 0, 1):
            for dc in (-1, 0, 1):
                if dr == 0 and dc == 0:
                    continue
                nr = (row + dr) % self.rows
                nc = (col + dc) % self.cols
                count += self.grid[nr][nc]
        return count

    def step(self):
        """Advance one generation. Double-buffered for synchronization."""
        # Compute next state entirely from current grid
        for r in range(self.rows):
            for c in range(self.cols):
                neighbors = self.count_neighbors(r, c)

                if self.grid[r][c] == 1:
                    # Survival rule: cell lives if neighbors in [min, max]
                    if self.survival_min <= neighbors <= self.survival_max:
                        self.next_grid[r][c] = 1
                        self.cell_age[r][c] += 1
                    else:
                        self.next_grid[r][c] = 0
                        self.cell_age[r][c] = 0  # Reset age on death
                else:
                    # Birth rule: dead cell becomes alive if neighbors in set
                    if neighbors in self.birth_rules:
                        self.next_grid[r][c] = 1
                        self.cell_age[r][c] = 1  # Newborn starts at age 1
                    else:
                        self.next_grid[r][c] = 0

        # Swap buffers atomically - now next_grid becomes current grid
        self.grid, self.next_grid = self.next_grid, self.grid
        self.frame += 1

    def toggle_cell(self, row, col):
        """Toggle a cell's state at the given position."""
        if 0 <= row < self.rows and 0 <= col < self.cols:
            self.grid[row][col] = 1 - self.grid[row][col]
            if self.grid[row][col] == 1:
                self.cell_age[row][col] = 1
            else:
                self.cell_age[row][col] = 0

    def randomize(self, density=0.2):
        """Fill grid with random live cells at given density."""
        for r in range(self.rows):
            for c in range(self.cols):
                if random.random() < density:
                    self.grid[r][c] = 1
                    self.cell_age[r][c] = random.randint(1, 5)
                else:
                    self.grid[r][c] = 0
                    self.cell_age[r][c] = 0

    def clear(self):
        """Kill all cells and reset ages."""
        for r in range(self.rows):
            for c in range(self.cols):
                self.grid[r][c] = 0
                self.cell_age[r][c] = 0
        self.frame = 0

    def load_pattern(self, pattern_name, placement_row=5, placement_col=10):
        """Load a preset pattern at the specified anchor position."""
        self.clear()
        if pattern_name in PATTERNS:
            for dr, dc in PATTERNS[pattern_name]:
                r = (placement_row + dr) % self.rows
                c = (placement_col + dc) % self.cols
                self.grid[r][c] = 1
                self.cell_age[r][c] = 1

    def get_population(self):
        """Count total live cells."""
        return sum(sum(row) for row in self.grid)


class NeonRenderer:
    """Handles all rendering with neon glow, scanlines, and UI layout.

    Layout strategy to prevent overlap:
    - Grid occupies left area (GRID_AREA_X to INFO_PANEL_X)
    - Info panel sits on the right side (INFO_PANEL_X onward)
    - Pattern buttons are below the info panel with fixed spacing
    - Each zone has explicit padding boundaries
    """

    def __init__(self, game, speed):
        self.game = game
        self.speed = speed
        self.clock = pygame.time.Clock()

        # Compute grid pixel dimensions from cell count and size
        self.grid_pixel_width = game.cols * CELL_SIZE + GRID_PADDING * 2
        self.grid_pixel_height = game.rows * CELL_SIZE + GRID_PADDING * 2

        # Initialize display - ensure it fits the screen
        pygame.init()
        font_size = 16
        pygame.font.init()
        self.font = pygame.font.SysFont("consolas", font_size)
        self.font_small = pygame.font.SysFont("consolas", 13)
        self.font_title = pygame.font.SysFont("consolas", 20, bold=True)

        # Create pattern buttons with fixed dimensions and spacing
        btn_width = 120
        btn_height = 36
        btn_gap = 10
        self.buttons = []
        panel_left = INFO_PANEL_X + 20

        for i, name in enumerate(PATTERNS.keys()):
            # Arrange buttons in a grid: 2 columns
            col_idx = i % 2
            row_idx = i // 2
            bx = panel_left + col_idx * (btn_width + btn_gap)
            by = BUTTON_AREA_Y + row_idx * (btn_height + btn_gap)
            self.buttons.append({
                "name": name,
                "rect": pygame.Rect(bx, by, btn_width, btn_height),
                "hovered": False
            })

        # Calculate total screen height needed for all elements
        last_btn_bottom = BUTTON_AREA_Y + (len(self.buttons) // 2 + 1) * (btn_height + btn_gap)
        total_height = max(SCREEN_HEIGHT, last_btn_bottom + 60)

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, total_height))
        pygame.display.set_caption("Conway's Game of Life - Neon Edition")

        # Pre-render scanline overlay surface for performance
        self._create_scanline_overlay()

    def _create_scanline_overlay(self):
        """Create a reusable scanline overlay surface."""
        self.scanline_surface = pygame.Surface(
            (SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA
        )
        for y in range(0, SCREEN_HEIGHT, 2):
            pygame.draw.line(self.scanline_surface,
                             (0, 0, 0, SCANLINE_ALPHA),
                             (0, y), (SCREEN_WIDTH, y))

    def _get_cell_color(self, age):
        """Interpolate neon color based on cell age.

        Cold cyan -> Purple -> Hot magenta as cells survive longer.
        """
        if age <= 2:
            return COLOR_CELL_COLD
        elif age <= 8:
            # Blend from cyan to purple
            t = min((age - 2) / 6.0, 1.0)
            r = int(COLOR_CELL_COLD[0] * (1 - t) + COLOR_CELL_MID[0] * t)
            g = int(COLOR_CELL_COLD[1] * (1 - t) + COLOR_CELL_MID[1] * t)
            b = int(COLOR_CELL_COLD[2] * (1 - t) + COLOR_CELL_MID[2] * t)
            return (r, g, b)
        else:
            # Blend from purple to magenta
            t = min(min((age - 8) / 10.0, 1.0), 1.0)
            r = int(COLOR_CELL_MID[0] * (1 - t) + COLOR_CELL_HOT[0] * t)
            g = int(COLOR_CELL_MID[1] * (1 - t) + COLOR_CELL_HOT[1] * t)
            b = int(COLOR_CELL_MID[2] * (1 - t) + COLOR_CELL_HOT[2] * t)
            return (r, g, b)

    def _draw_grid(self):
        """Draw the game grid with neon glow effects."""
        surface = self.screen

        # Draw subtle grid lines for structure
        for r in range(self.game.rows + 1):
            y = GRID_AREA_Y + r * CELL_SIZE
            pygame.draw.line(surface, COLOR_GRID_LINE,
                             (GRID_AREA_X - GRID_PADDING, y),
                             (GRID_AREA_X - GRID_PADDING + self.game.cols * CELL_SIZE, y))
        for c in range(self.game.cols + 1):
            x = GRID_AREA_X - GRID_PADDING + c * CELL_SIZE
            pygame.draw.line(surface, COLOR_GRID_LINE,
                             (x, GRID_AREA_Y - GRID_PADDING),
                             (x, GRID_AREA_Y - GRID_PADDING + self.game.rows * CELL_SIZE))

        # Draw cells with glow effect
        for r in range(self.game.rows):
            for c in range(self.game.cols):
                if self.game.grid[r][c] == 1:
                    pixel_x = GRID_AREA_X + c * CELL_SIZE
                    pixel_y = GRID_AREA_Y + r * CELL_SIZE

                    # Glow halo (larger circle behind cell)
                    glow_surf = pygame.Surface((CELL_SIZE + GLOW_RADIUS * 2,
                                                CELL_SIZE + GLOW_RADIUS * 2),
                                               pygame.SRCALPHA)
                    color = self._get_cell_color(self.game.cell_age[r][c])
                    glow_color = (*color, 100)
                    pygame.draw.circle(glow_surf, glow_color,
                                       (CELL_SIZE // 2 + GLOW_RADIUS // 2,
                                        CELL_SIZE // 2 + GLOW_RADIUS // 2),
                                       GLOW_RADIUS)
                    glow_rect = glow_surf.get_rect(
                        center=(pixel_x + CELL_SIZE // 2,
                                pixel_y + CELL_SIZE // 2))
                    surface.blit(glow_surf, glow_rect.topleft)

                    # Core cell rectangle
                    pygame.draw.rect(surface, color,
                                     (pixel_x + 1, pixel_y + 1,
                                      CELL_SIZE - 2, CELL_SIZE - 2))

    def _draw_info_panel(self):
        """Draw the info panel with stats and controls. No overlap with grid."""
        surface = self.screen
        x = INFO_PANEL_X
        y = GRID_AREA_Y
        line_height = 24

        # Title
        title_surf = self.font_title.render("Game of Life", True, COLOR_TEXT_BRIGHT)
        surface.blit(title_surf, (x + 10, y))
        y += 35

        # Separator line
        pygame.draw.line(surface, COLOR_BTN_BORDER, (x + 10, y),
                         (x + INFO_PANEL_WIDTH - 20, y))
        y += 15

        # Frame counter
        frame_text = f"Frame: {self.game.frame}"
        color = COLOR_PAUSE_WARN if self.game.paused else COLOR_TEXT_BRIGHT
        surf = self.font.render(frame_text, True, color)
        surface.blit(surf, (x + 10, y))
        y += line_height

        # Population count
        pop = self.game.get_population()
        pop_text = f"Population: {pop}"
        surface.blit(self.font.render(pop_text, True, COLOR_TEXT),
                     (x + 10, y))
        y += line_height

        # Status indicator
        status = "PAUSED" if self.game.paused else "RUNNING"
        status_color = COLOR_PAUSE_WARN if self.game.paused else (0, 255, 100)
        surface.blit(self.font.render(f"Status: {status}", True, status_color),
                     (x + 10, y))
        y += line_height

        # Speed
        speed_text = f"Speed: {self.speed} fps"
        surface.blit(self.font.render(speed_text, True, COLOR_TEXT),
                     (x + 10, y))
        y += line_height

        # Separator before rules
        pygame.draw.line(surface, COLOR_BTN_BORDER, (x + 10, y),
                         (x + INFO_PANEL_WIDTH - 20, y))
        y += 15

        # Rule parameters section
        self.font.render("Rules:", True, COLOR_TEXT_BRIGHT)
        surface.blit(self.font_title.render("Rule Parameters", True, COLOR_TEXT_BRIGHT),
                     (x + 10, y))
        y += 28

        birth_str = ", ".join(str(b) for b in sorted(self.game.birth_rules))
        survival_str = f"[{self.game.survival_min}, {self.game.survival_max}]"
        grid_dim_str = f"{self.game.cols} x {self.game.rows}"

        surface.blit(self.font.render(f"Birth: {birth_str}", True, COLOR_TEXT),
                     (x + 15, y))
        y += line_height
        surface.blit(self.font.render(f"Survival: {survival_str}", True, COLOR_TEXT),
                     (x + 15, y))
        y += line_height
        surface.blit(self.font.render(f"Grid: {grid_dim_str}", True, COLOR_TEXT),
                     (x + 15, y))
        y += line_height

        # Separator before controls
        pygame.draw.line(surface, COLOR_BTN_BORDER, (x + 10, y),
                         (x + INFO_PANEL_WIDTH - 20, y))
        y += 15

        # Controls section
        surface.blit(self.font_title.render("Controls", True, COLOR_TEXT_BRIGHT),
                     (x + 10, y))
        y += 28

        controls = [
            "Space: Pause/Resume",
            "R: Randomize",
            "C: Clear grid",
            "+/-: Adjust speed",
            "Click: Toggle cell",
        ]
        for ctrl in controls:
            surface.blit(self.font_small.render(ctrl, True, COLOR_TEXT),
                         (x + 10, y))
            y += line_height

    def _draw_buttons(self):
        """Draw pattern preset buttons with hover detection."""
        surface = self.screen

        # Title for button section
        btn_title_y = BUTTON_AREA_Y - 30
        pygame.draw.line(surface, COLOR_BTN_BORDER,
                         (INFO_PANEL_X + 10, btn_title_y),
                         (INFO_PANEL_X + INFO_PANEL_WIDTH - 20, btn_title_y))
        surface.blit(self.font_title.render("Pattern Presets", True, COLOR_TEXT_BRIGHT),
                     (INFO_PANEL_X + 15, btn_title_y - 5))

        for btn in self.buttons:
            rect = btn["rect"]
            color = COLOR_BTN_HOVER if btn["hovered"] else COLOR_BTN_BG

            # Button background with border
            pygame.draw.rect(surface, COLOR_BTN_BORDER, rect, 2)
            pygame.draw.rect(surface, color, rect.inflate(-2, -2))

            # Button text
            text_surf = self.font_small.render(btn["name"], True, COLOR_TEXT_BRIGHT)
            text_rect = text_surf.get_rect(center=rect.center)
            surface.blit(text_surf, text_rect)

    def render(self):
        """Full frame render. Called every display cycle."""
        # Clear background
        self.screen.fill(COLOR_BG)

        # Draw all layers - grid first, then info panel, then buttons
        self._draw_grid()
        self._draw_info_panel()
        self._draw_buttons()

        # Apply scanline overlay for retro CRT effect
        self.screen.blit(self.scanline_surface, (0, 0))

        pygame.display.flip()


class App:
    """Main application loop handling input and game state."""

    def __init__(self):
        # Initialize game engine with default parameters
        self.game = GameOfLife(
            rows=DEFAULT_GRID_ROWS,
            cols=DEFAULT_GRID_COLS,
            birth_rules=DEFAULT_BIRTH_RULES.copy(),
            survival_min=DEFAULT_SURVIVAL_MIN,
            survival_max=DEFAULT_SURVIVAL_MAX,
        )

        # Initialize renderer with game reference
        self.renderer = NeonRenderer(self.game, DEFAULT_SPEED)
        self.speed = DEFAULT_SPEED

        # Load a default pattern for immediate visual feedback
        self.game.load_pattern("Glider", 10, 20)

        self.running = True
        self._handle_events()

    def _pixel_to_cell(self, pixel_x, pixel_y):
        """Convert screen pixel coordinates to grid cell indices.

        Critical for synchronization: accounts for grid offset and padding
        to ensure mouse clicks map to the correct cells.
        """
        col = (pixel_x - GRID_AREA_X) // CELL_SIZE
        row = (pixel_y - GRID_AREA_Y) // CELL_SIZE
        if 0 <= row < self.game.rows and 0 <= col < self.game.cols:
            return (row, col)
        return None

    def _handle_events(self):
        """Process all pygame events and update game state."""
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                    break

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Toggle pause/resume
                        self.game.paused = not self.game.paused

                    elif event.key == pygame.K_r:
                        # Randomize grid
                        self.game.randomize()

                    elif event.key == pygame.K_c:
                        # Clear grid
                        self.game.clear()

                    elif event.key in (pygame.K_EQUALS, pygame.K_PLUS):
                        # Increase speed
                        self.speed = min(self.speed + 5, MAX_SPEED)
                        self.renderer.speed = self.speed

                    elif event.key == pygame.K_MINUS:
                        # Decrease speed
                        self.speed = max(self.speed - 5, MIN_SPEED)
                        self.renderer.speed = self.speed

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mx, my = event.pos

                    # Check button clicks first (priority over grid clicks)
                    clicked_button = False
                    for btn in self.renderer.buttons:
                        if btn["rect"].collidepoint(mx, my):
                            self.game.load_pattern(btn["name"], 5, 10)
                            clicked_button = True
                            break

                    # If no button was clicked, toggle cell under cursor
                    if not clicked_button:
                        cell = self._pixel_to_cell(mx, my)
                        if cell:
                            self.game.toggle_cell(*cell)

                if event.type == pygame.MOUSEMOTION:
                    mx, my = event.pos
                    # Update button hover states for visual feedback
                    for btn in self.renderer.buttons:
                        btn["hovered"] = btn["rect"].collidepoint(mx, my)

            # Game logic update - only advance when not paused
            if not self.game.paused and self.running:
                self.game.step()

            # Render the current state
            self.renderer.render()
            self.renderer.clock.tick(self.speed)

        pygame.quit()


if __name__ == "__main__":
    print("Launching Conway's Game of Life - Neon Edition")
    print(f"Grid: {DEFAULT_GRID_COLS}x{DEFAULT_GRID_ROWS}, Cell: {CELL_SIZE}px")
    print(f"Rules: Birth={DEFAULT_BIRTH_RULES}, Survival=[{DEFAULT_SURVIVAL_MIN},{DEFAULT_SURVIVAL_MAX}]")
    print("Controls: Space(pause) R(random) C(clear) +/- (speed)")
    app = App()

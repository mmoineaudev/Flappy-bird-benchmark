#!/usr/bin/env python3
"""
Conway's Game of Life - Neon Wave Edition
A retro-styled interactive simulation with customizable rules.

Game Rules (Parametrizable):
- Birth rule: A dead cell becomes alive if it has exactly N live neighbors
- Survival rule: A live cell survives if it has between M and K live neighbors

Default Conway's Rules (B3/S23):
- Birth: 3 neighbors
- Survival: 2-3 neighbors

Visual Style:
- Dark background with neon cyan/magenta/purple elements
- CRT scanline effects for retro feel
- Glowing cells with subtle grid overlay
"""

import pygame
import random
import sys
from collections import deque

# ============================================================================
# CONFIGURATION - Customize these parameters
# ============================================================================

# Grid dimensions (number of cells)
GRID_WIDTH = 80
GRID_HEIGHT = 40

# Cell size in pixels
CELL_SIZE = 15

# Animation speed (frames per second)
FPS = 30

# Game Rules - Conway's original B3/S23 rules
BIRTH_NEIGHBORS = 3          # Dead cell needs exactly this many neighbors to be born
SURVIVAL_MIN = 2             # Live cell needs at least this many to survive
SURVIVAL_MAX = 3             # Live cell needs at most this many to survive

# Colors (neon wave palette)
COLOR_BACKGROUND = (10, 10, 15)           # Dark background
COLOR_GRID = (20, 20, 30)                  # Subtle grid lines
COLOR_CELLS = [(0, 255, 255), (255, 0, 255), (157, 78, 221)]  # Cyan, Magenta, Purple
COLOR_TEXT = (255, 255, 255)
COLOR_HIGHLIGHT = (255, 255, 0)            # Yellow for highlights

# CRT Scanline effect intensity (0-1)
SCANLINE_INTENSITY = 0.15

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def count_neighbors(grid, x, y):
    """Count live neighbors for a cell at position (x, y) with toroidal wrapping."""
    count = 0
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx == 0 and dy == 0:
                continue
            # Toroidal (wrap-around) grid
            nx = (x + dx) % GRID_WIDTH
            ny = (y + dy) % GRID_HEIGHT
            count += grid[nx][ny]
    return count

def compute_next_generation(grid):
    """Compute the next generation based on configurable rules."""
    new_grid = [[0 for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            neighbors = count_neighbors(grid, x, y)
            if grid[x][y] == 1:
                # Survival rule
                if SURVIVAL_MIN <= neighbors <= SURVIVAL_MAX:
                    new_grid[x][y] = 1
            else:
                # Birth rule
                if neighbors == BIRTH_NEIGHBORS:
                    new_grid[x][y] = 1
    return new_grid

def count_population(grid):
    """Count total live cells."""
    return sum(sum(row) for row in grid)

def randomize_grid(grid):
    """Randomly populate the grid (20% chance per cell)."""
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            grid[x][y] = 1 if random.random() < 0.2 else 0

def clear_grid(grid):
    """Clear all cells."""
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            grid[x][y] = 0

# ============================================================================
# PRESET PATTERNS
# ============================================================================

def add_pattern(grid, pattern_name, start_x, start_y):
    """Add a classic Game of Life pattern to the grid."""
    patterns = {
        "glider": [
            (1, 0), (2, 1), (0, 2), (1, 2), (2, 2)
        ],
        "blinker": [
            (0, 0), (1, 0), (2, 0),
            (0, 1), (1, 1), (2, 1)
        ],
        "beacon": [
            (0, 0), (1, 0), (0, 1), (1, 1),
            (4, 4), (5, 4), (4, 5), (5, 5)
        ],
        "gosper_glider": [
            (1, 0), (3, 1), (0, 2), (1, 2), (2, 2), (3, 2), (0, 3), (4, 3),
            (0, 4), (4, 4), (1, 5), (2, 5), (3, 5)
        ],
        "pulsar": [
            (1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0),
            (0, 1), (8, 1),
            (0, 2), (8, 2),
            (0, 3), (8, 3),
            (0, 4), (8, 4),
            (0, 5), (8, 5),
            (0, 6), (8, 6),
            (0, 7), (1, 7), (2, 7), (3, 7), (4, 7), (5, 7), (6, 7), (7, 7)
        ],
    }
    
    if pattern_name in patterns:
        for dx, dy in patterns[pattern_name]:
            px = (start_x + dx) % GRID_WIDTH
            py = (start_y + dy) % GRID_HEIGHT
            grid[px][py] = 1

# ============================================================================
# CRT SCANLINE EFFECT
# ============================================================================

def apply_scanlines(surface, intensity):
    """Apply CRT scanline overlay effect."""
    width, height = surface.get_size()
    for y in range(0, height, 3):
        alpha = int(255 * intensity)
        pygame.draw.line(surface, (0, 0, 0), (0, y), (width, y), 1)

# ============================================================================
# MAIN GAME CLASS
# ============================================================================

class GameOfLife:
    def __init__(self):
        """Initialize the Game of Life simulation."""
        pygame.init()
        
        # Calculate window size including UI space
        self.cell_width = GRID_WIDTH * CELL_SIZE
        self.cell_height = GRID_HEIGHT * CELL_SIZE
        self.ui_height = 150  # Space for UI elements
        self.window_width = self.cell_width + 300
        self.window_height = max(self.cell_height, self.ui_height) + 50
        
        self.screen = pygame.display.set_mode((self.window_width, self.window_height))
        pygame.display.set_caption("Game of Life - Neon Wave Edition")
        
        # Clock for FPS control
        self.clock = pygame.time.Clock()
        self.fps = FPS
        
        # Initialize grid
        self.grid = [[0 for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]
        randomize_grid(self.grid)
        
        # Game state
        self.running = True
        self.paused = False
        self.frame_count = 0
        self.population = count_population(self.grid)
        
        # UI state
        self.show_hints = True
        self.mouse_pressed = False
        
        # Font initialization
        self.font_small = pygame.font.Font(None, 16)
        self.font_medium = pygame.font.Font(None, 20)
        self.font_large = pygame.font.Font(None, 28)
        
        # Pattern presets for quick access
        self.patterns = ["glider", "blinker", "beacon", "gosper_glider", "pulsar"]
        self.current_pattern_idx = 0
        
    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                
                elif event.key == pygame.K_r:
                    randomize_grid(self.grid)
                    self.population = count_population(self.grid)
                
                elif event.key == pygame.K_c:
                    clear_grid(self.grid)
                    self.population = 0
                
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    self.fps = min(60, self.fps + 5)
                
                elif event.key == pygame.K_MINUS:
                    self.fps = max(1, self.fps - 5)
                
                elif event.key == pygame.K_h:
                    self.show_hints = not self.show_hints
                
                elif event.key == pygame.K_p:
                    # Cycle through preset patterns
                    self.current_pattern_idx = (self.current_pattern_idx + 1) % len(self.patterns)
                    clear_grid(self.grid)
                    add_pattern(self.grid, self.patterns[self.current_pattern_idx], 5, 5)
                    self.population = count_population(self.grid)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.mouse_pressed = True
                    self.toggle_cell_at_mouse(event.pos)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.mouse_pressed = False
            
            elif event.type == pygame.MOUSEMOTION:
                if self.mouse_pressed:
                    self.toggle_cell_at_mouse(event.pos)
    
    def toggle_cell_at_mouse(self, pos):
        """Toggle cell state at mouse position."""
        x, y = pos
        # Check if click is on grid area
        if 0 <= x < self.cell_width and 0 <= y < self.cell_height:
            cell_x = x // CELL_SIZE
            cell_y = y // CELL_SIZE
            self.grid[cell_x][cell_y] = 1 - self.grid[cell_x][cell_y]
            self.population += 1 if self.grid[cell_x][cell_y] else -1
    
    def update(self):
        """Update game state."""
        if not self.paused:
            self.grid = compute_next_generation(self.grid)
            self.frame_count += 1
            self.population = count_population(self.grid)
    
    def draw(self):
        """Draw everything to the screen."""
        # Clear background
        self.screen.fill(COLOR_BACKGROUND)
        
        # Draw grid lines (subtle)
        for x in range(0, self.cell_width, CELL_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID, (x, 0), (x, self.cell_height))
        for y in range(0, self.cell_height, CELL_SIZE):
            pygame.draw.line(self.screen, COLOR_GRID, (0, y), (self.cell_width, y))
        
        # Draw live cells with neon glow effect
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                if self.grid[x][y] == 1:
                    # Color cycling based on position and time
                    color_idx = (x + y + self.frame_count // 10) % len(COLOR_CELLS)
                    color = COLOR_CELLS[color_idx]
                    
                    # Draw cell with slight glow (bigger rect for glow effect)
                    glow_rect = pygame.Rect(
                        x * CELL_SIZE - 1,
                        y * CELL_SIZE - 1,
                        CELL_SIZE + 2,
                        CELL_SIZE + 2
                    )
                    pygame.draw.rect(self.screen, color, glow_rect)
                    
                    # Inner cell for depth
                    inner_rect = pygame.Rect(
                        x * CELL_SIZE + 2,
                        y * CELL_SIZE + 2,
                        CELL_SIZE - 4,
                        CELL_SIZE - 4
                    )
                    pygame.draw.rect(self.screen, (255, 255, 255), inner_rect)
        
        # Apply CRT scanline effect
        apply_scanlines(self.screen, SCANLINE_INTENSITY)
        
        # Draw UI panel on the right
        self.draw_ui()
        
        # Update display
        pygame.display.flip()
    
    def draw_ui(self):
        """Draw the UI panel with statistics and controls."""
        ui_x = self.cell_width + 20
        ui_y = 20
        
        # Panel background (semi-transparent)
        panel_rect = pygame.Rect(ui_x - 10, ui_y - 10, 280, 300)
        pygame.draw.rect(self.screen, (20, 20, 30), panel_rect)
        
        # Frame counter
        frame_text = self.font_large.render(f"Frame: {self.frame_count}", True, COLOR_TEXT)
        self.screen.blit(frame_text, (ui_x, ui_y))
        ui_y += 35
        
        # Population count
        pop_color = COLOR_CELLS[self.frame_count % len(COLOR_CELLS)]
        pop_text = self.font_large.render(f"Population: {self.population}", True, pop_color)
        self.screen.blit(pop_text, (ui_x, ui_y))
        ui_y += 35
        
        # Rule display
        rule_text = self.font_small.render(
            f"Rules: B{BIRTH_NEIGHBORS}/S{SURVIVAL_MIN}-{SURVIVAL_MAX}",
            True, COLOR_TEXT
        )
        self.screen.blit(rule_text, (ui_x, ui_y))
        ui_y += 25
        
        # FPS
        fps_text = self.font_small.render(f"Speed: {self.fps} FPS", True, COLOR_TEXT)
        self.screen.blit(fps_text, (ui_x, ui_y))
        ui_y += 30
        
        # Separator line
        pygame.draw.line(self.screen, COLOR_GRID, (ui_x, ui_y), (ui_x + 260, ui_y))
        ui_y += 20
        
        # Control hints
        if self.show_hints:
            hints = [
                "Controls:",
                "Space - Pause/Resume",
                "R - Randomize",
                "C - Clear",
                "+/- - Adjust Speed",
                "P - New Pattern",
                "H - Toggle Hints",
                "Esc - Quit",
            ]
            for hint in hints:
                hint_text = self.font_small.render(hint, True, COLOR_TEXT)
                self.screen.blit(hint_text, (ui_x, ui_y))
                ui_y += 20
        
        # Draw current pattern name
        pattern_text = self.font_medium.render(
            f"Pattern: {self.patterns[self.current_pattern_idx]}",
            True, COLOR_HIGHLIGHT
        )
        self.screen.blit(pattern_text, (ui_x, ui_y))
    
    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
        
        pygame.quit()
        sys.exit()

# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Entry point - create and run the game."""
    game = GameOfLife()
    game.run()

if __name__ == "__main__":
    main()

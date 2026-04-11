#!/usr/bin/env python3
"""
Conway's Game of Life - Python/Pygame Implementation
Retro neon wave aesthetic with customizable rules and interactive controls.

Controls:
    Spacebar: Pause/Resume
    R: Randomize grid
    C: Clear grid
    + / -: Adjust animation speed
    Mouse click: Toggle cell state at cursor position
"""

import pygame
import random
import sys
from typing import List, Tuple

# ============================================================================
# CONFIGURABLE PARAMETERS - Game Rules and Settings
# ============================================================================

# Grid dimensions (number of cells)
GRID_WIDTH = 80
GRID_HEIGHT = 40

# Cell size in pixels
CELL_SIZE = 15

# Animation speed (frames per second for simulation updates)
DEFAULT_FPS = 10

# Default rule parameters (Conway's Game of Life: B3/S23)
# Birth rule: number of live neighbors required to spawn a new cell
BIRTH_RULE = 3

# Survival rule: range of live neighbors for a cell to survive [min, max]
SURVIVAL_MIN = 2
SURVIVAL_MAX = 3

# Color palette - Neon wave retro aesthetic
COLORS = {
    'background': (10, 10, 15),        # Dark background #0a0a0f
    'grid_line': (20, 20, 40),         # Subtle grid lines
    'cell_cyan': (0, 255, 255),        # Neon cyan #00ffff
    'cell_magenta': (255, 0, 255),     # Neon magenta #ff00ff
    'cell_purple': (157, 78, 221),     # Neon purple #9d4edd
    'text_primary': (0, 255, 255),     # Primary text color
    'text_secondary': (157, 78, 221),  # Secondary text color
    'scanline': (0, 0, 0, 30),         # Semi-transparent scanlines
}

# Window dimensions calculated from grid settings
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE + 60  # Extra space for UI


# ============================================================================
# GAME LOGIC - Conway's Game of Life Rules Engine
# ============================================================================

def create_empty_grid() -> List[List[int]]:
    """Create an empty grid filled with dead cells (0)."""
    return [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]


def create_random_grid() -> List[List[int]]:
    """Create a grid with random cell states (25% live probability)."""
    return [[random.randint(0, 1) for _ in range(GRID_WIDTH)] 
            for _ in range(GRID_HEIGHT)]


def count_neighbors(grid: List[List[int]], x: int, y: int) -> int:
    """
    Count the number of live neighbors for a cell at position (x, y).
    Uses toroidal wrapping (edges connect to opposite sides).
    
    Args:
        grid: The current game grid
        x: X coordinate of the cell
        y: Y coordinate of the cell
    
    Returns:
        Number of live neighbors (0-8)
    """
    count = 0
    for dy in range(-1, 2):
        for dx in range(-1, 2):
            if dx == 0 and dy == 0:
                continue  # Skip the cell itself
            # Toroidal wrapping - edges connect to opposite sides
            nx = (x + dx) % GRID_WIDTH
            ny = (y + dy) % GRID_HEIGHT
            count += grid[ny][nx]
    return count


def apply_rules(grid: List[List[int]], 
                birth_rule: int = BIRTH_RULE,
                survival_min: int = SURVIVAL_MIN,
                survival_max: int = SURVIVAL_MAX) -> List[List[int]]:
    """
    Apply Conway's Game of Life rules to generate the next generation.
    
    Rules:
    - Birth: A dead cell with exactly `birth_rule` live neighbors becomes alive
    - Survival: A live cell survives if it has between `survival_min` and 
      `survival_max` (inclusive) live neighbors
    
    Args:
        grid: Current generation grid
        birth_rule: Number of neighbors needed for birth
        survival_min: Minimum neighbors for survival
        survival_max: Maximum neighbors for survival
    
    Returns:
        New grid representing the next generation
    """
    new_grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
    
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            neighbors = count_neighbors(grid, x, y)
            
            if grid[y][x] == 1:
                # Cell is alive - check survival conditions
                if survival_min <= neighbors <= survival_max:
                    new_grid[y][x] = 1
            else:
                # Cell is dead - check birth conditions
                if neighbors == birth_rule:
                    new_grid[y][x] = 1
    
    return new_grid


def count_population(grid: List[List[int]]) -> int:
    """Count the total number of live cells in the grid."""
    return sum(sum(row) for row in grid)


# ============================================================================
# PRESET PATTERNS - Classic Game of Life configurations
# ============================================================================

def place_glider(grid: List[List[int]], x: int, y: int) -> None:
    """Place a glider pattern at the specified position."""
    pattern = [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)]
    for dx, dy in pattern:
        nx, ny = (x + dx) % GRID_WIDTH, (y + dy) % GRID_HEIGHT
        grid[ny][nx] = 1


def place_pulsar(grid: List[List[int]], x: int, y: int) -> None:
    """Place a pulsar oscillator pattern at the specified position."""
    # Pulsar is a period-3 oscillator
    offsets = [
        (2, 0), (3, 0), (4, 0), (6, 0), (7, 0), (8, 0),
        (0, 2), (9, 2),
        (0, 3), (9, 3),
        (0, 4), (9, 4),
        (2, 6), (3, 6), (4, 6), (6, 6), (7, 6), (8, 6),
        (2, 9), (3, 9), (4, 9), (6, 9), (7, 9), (8, 9)
    ]
    for dx, dy in offsets:
        if 0 <= x + dx < GRID_WIDTH and 0 <= y + dy < GRID_HEIGHT:
            grid[y + dy][x + dx] = 1


def place_gosper_glider_gun(grid: List[List[int]], x: int, y: int) -> None:
    """Place a Gosper Glider Gun pattern (fires gliders periodically)."""
    pattern = [
        (24, 0), (22, 1), (24, 1), (12, 2), (13, 2), 
        (21, 2), (23, 2), (12, 3), (13, 3), (21, 3), 
        (23, 3), (6, 4), (8, 4), (12, 4), (13, 4), 
        (16, 4), (17, 4), (21, 4), (22, 4), (6, 5),
        (8, 5), (16, 5), (17, 5), (1, 6), (2, 6), 
        (3, 6), (2, 7), (3, 7)
    ]
    for dx, dy in pattern:
        if 0 <= x + dx < GRID_WIDTH and 0 <= y + dy < GRID_HEIGHT:
            grid[y + dy][x + dx] = 1


# ============================================================================
# RENDERING - Pygame Graphics with Neon Effects
# ============================================================================

class GameOfLifeRenderer:
    """Handles all rendering operations for the Game of Life simulation."""
    
    def __init__(self, width: int, height: int):
        """Initialize pygame and create the display surface."""
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Conway's Game of Life - Neon Wave")
        
        # Create surfaces for effects
        self.glow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        self.scanline_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Load fonts for UI text
        self.font_large = pygame.font.Font(None, 36)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_small = pygame.font.Font(None, 18)
        
        # Create scanline pattern (horizontal lines for CRT effect)
        self._create_scanlines()
    
    def _create_scanlines(self) -> None:
        """Generate a scanline overlay pattern for retro CRT effect."""
        for y in range(0, self.scanline_surface.get_height(), 2):
            pygame.draw.line(
                self.scanline_surface,
                COLORS['scanline'],
                (0, y),
                (self.scanline_surface.get_width(), y)
            )
    
    def draw_cell(self, x: int, y: int, color: Tuple[int, int, int], 
                  glow_strength: int = 10) -> None:
        """
        Draw a single cell with neon glow effect.
        
        Args:
            x: Grid X coordinate
            y: Grid Y coordinate  
            color: RGB color tuple for the cell
            glow_strength: Intensity of the glow effect (larger = more glow)
        """
        px = x * CELL_SIZE
        py = y * CELL_SIZE
        
        # Draw glow layers (larger, more transparent rectangles)
        for size in range(glow_strength, 0, -2):
            alpha = min(100, 50 + size * 3)
            glow_color = (*color[:3], alpha)
            glow_rect = pygame.Rect(
                px - size, py - size,
                CELL_SIZE + size * 2, CELL_SIZE + size * 2
            )
            glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), 
                                       pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, glow_color, glow_surf.get_rect())
            self.glow_surface.blit(glow_surf, glow_rect.topleft)
        
        # Draw the actual cell (bright core)
        cell_rect = pygame.Rect(px + 1, py + 1, CELL_SIZE - 2, CELL_SIZE - 2)
        pygame.draw.rect(self.screen, color, cell_rect)
    
    def draw_grid_lines(self) -> None:
        """Draw subtle grid lines in the background."""
        for x in range(0, WINDOW_WIDTH, CELL_SIZE):
            pygame.draw.line(self.screen, COLORS['grid_line'],
                           (x, 0), (x, GRID_HEIGHT * CELL_SIZE))
        for y in range(0, GRID_HEIGHT * CELL_SIZE, CELL_SIZE):
            pygame.draw.line(self.screen, COLORS['grid_line'],
                           (0, y), (WINDOW_WIDTH, y))
    
    def draw_cells(self, grid: List[List[int]], frame: int) -> None:
        """
        Draw all live cells on the screen with color cycling.
        
        Args:
            grid: Current game grid
            frame: Current frame number (for color cycling animation)
        """
        self.glow_surface.fill((0, 0, 0, 0))  # Clear glow layer
        
        # Cycle through neon colors based on frame
        colors = [COLORS['cell_cyan'], COLORS['cell_magenta'], 
                  COLORS['cell_purple']]
        
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if grid[y][x] == 1:
                    # Select color based on position and time for variety
                    color_idx = (frame + x + y) % len(colors)
                    self.draw_cell(x, y, colors[color_idx])
        
        # Blit glow effects to main screen
        self.screen.blit(self.glow_surface, (0, 0))
    
    def draw_ui(self, frame: int, population: int, fps: int, 
                paused: bool, birth_rule: int, survival: Tuple[int, int]) -> None:
        """
        Draw the user interface overlay with statistics and controls.
        
        Args:
            frame: Current simulation frame
            population: Number of live cells
            fps: Current animation speed
            paused: Whether the simulation is paused
            birth_rule: Current birth rule value
            survival: (min, max) survival rule values
        """
        ui_y = GRID_HEIGHT * CELL_SIZE + 5
        
        # Status line
        status = "PAUSED" if paused else "RUNNING"
        status_color = COLORS['cell_magenta'] if paused else COLORS['cell_cyan']
        status_text = self.font_medium.render(f"[{status}]", True, status_color)
        self.screen.blit(status_text, (10, ui_y))
        
        # Statistics
        stats_text = self.font_small.render(
            f"Frame: {frame:6d} | Population: {population:5d} | FPS: {fps}",
            True, COLORS['text_primary']
        )
        self.screen.blit(stats_text, (10, ui_y + 25))
        
        # Rule display
        rules_text = self.font_small.render(
            f"Rules: B{birth_rule}/S{survival[0]}-{survival[1]}",
            True, COLORS['text_secondary']
        )
        self.screen.blit(rules_text, (WINDOW_WIDTH - 250, ui_y))
        
        # Control hints
        controls = [
            "SPACE: Pause/Resume",
            "R: Randomize | C: Clear",
            "+/-: Speed | Click: Toggle cell"
        ]
        for i, ctrl in enumerate(controls):
            ctrl_text = self.font_small.render(ctrl, True, COLORS['text_secondary'])
            self.screen.blit(ctrl_text, (WINDOW_WIDTH - 200, ui_y + 5 + i * 18))
    
    def draw_scanlines(self) -> None:
        """Draw scanline overlay for retro CRT effect."""
        self.screen.blit(self.scanline_surface, (0, 0))
    
    def update_display(self) -> None:
        """Update the pygame display."""
        pygame.display.flip()


# ============================================================================
# MAIN GAME LOOP - Event handling and simulation orchestration
# ============================================================================

def main():
    """Main entry point for the Game of Life simulation."""
    
    # Initialize renderer
    renderer = GameOfLifeRenderer(WINDOW_WIDTH, WINDOW_HEIGHT)
    
    # Initialize game state
    grid = create_random_grid()  # Start with random pattern
    frame = 0
    fps = DEFAULT_FPS
    paused = False
    
    # Create update timer
    clock = pygame.time.Clock()
    update_timer = 0
    
    # Main game loop
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                
                elif event.key == pygame.K_r:
                    grid = create_random_grid()
                
                elif event.key == pygame.K_c:
                    grid = create_empty_grid()
                
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    fps = min(60, fps + 1)
                
                elif event.key == pygame.K_MINUS or event.key == pygame.K_UNDERSCORE:
                    fps = max(1, fps - 1)
                
                # Pattern placement shortcuts
                elif event.key == pygame.K_g:
                    place_glider(grid, GRID_WIDTH // 2, GRID_HEIGHT // 2)
                
                elif event.key == pygame.K_p:
                    place_pulsar(grid, GRID_WIDTH // 2 - 5, GRID_HEIGHT // 2 - 5)
                
                elif event.key == pygame.K_u:
                    place_gosper_glider_gun(grid, 5, 10)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mx, my = pygame.mouse.get_pos()
                    gx = mx // CELL_SIZE
                    gy = my // CELL_SIZE
                    if 0 <= gx < GRID_WIDTH and 0 <= gy < GRID_HEIGHT:
                        grid[gy][gx] = 1 - grid[gy][gx]  # Toggle cell
        
        # Update simulation (if not paused)
        if not paused:
            update_timer += clock.get_time()
            # Calculate milliseconds per frame based on fps
            ms_per_frame = 1000 / fps if fps > 0 else 1000
            
            if update_timer >= ms_per_frame:
                grid = apply_rules(grid)
                frame += 1
                update_timer = 0
        
        # Rendering
        renderer.screen.fill(COLORS['background'])
        renderer.draw_grid_lines()
        renderer.draw_cells(grid, frame)
        renderer.draw_ui(frame, count_population(grid), fps, paused, 
                        BIRTH_RULE, (SURVIVAL_MIN, SURVIVAL_MAX))
        renderer.draw_scanlines()
        renderer.update_display()
        
        # Cap the rendering framerate (separate from simulation speed)
        clock.tick(60)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

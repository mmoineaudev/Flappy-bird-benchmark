#!/usr/bin/env python3
"""
Conway's Game of Life - Neon Wave Retro Edition
A parametrizable implementation with customizable rules and retro aesthetics.

Game Rules Configuration:
- A cell is BORN if it has exactly 'birth_rule' live neighbors
- A cell SURVIVES if it has between 'survival_min' and 'survival_max' live neighbors
- All other cells die or remain dead

Classic Conway's Rules (default):
- Birth: 3 neighbors
- Survival: 2-3 neighbors

Other interesting rule sets:
- "High Life": Birth=3, Survival=5-6 (creates pulsars)
- "Gardener's Delight": Birth=2, Survival=4-5
- "Drift": Birth=3, Survival=3-4
"""

import pygame
import numpy as np
import random
import sys
from datetime import datetime

# ==================== CONFIGURATION ====================

# Grid dimensions (cells)
GRID_WIDTH = 80
GRID_HEIGHT = 40

# Cell size in pixels
CELL_SIZE = 15

# Animation speed (frames per second)
FPS = 30

# Rule parameters (Conway's Classic Game of Life)
BIRTH_RULE = 3
SURVIVAL_MIN = 2
SURVIVAL_MAX = 3

# Color palette (neon wave aesthetic)
COLOR_BG = (10, 10, 15)  # Dark background
COLOR_CELL_ALIVE = (0, 255, 255)  # Cyan
COLOR_CELL_DEAD = (157, 78, 238)  # Purple for dead cells with glow
COLOR_GRID = (30, 30, 40)  # Subtle grid lines
COLOR_TEXT = (255, 255, 255)

# Screen dimensions (calculated from grid and cell size)
SCREEN_WIDTH = GRID_WIDTH * CELL_SIZE
SCREEN_HEIGHT = GRID_HEIGHT * CELL_SIZE + 100  # Extra space for UI


class GameOfLife:
    """Conway's Game of Life simulation engine with configurable rules."""
    
    def __init__(self, width, height, birth_rule, surv_min, surv_max):
        self.width = width
        self.height = height
        self.birth_rule = birth_rule
        self.survival_min = surv_min
        self.survival_max = surv_max
        
        # Initialize grid (0 = dead, 1 = alive)
        self.grid = np.zeros((height, width), dtype=np.uint8)
        self.next_grid = np.zeros((height, width), dtype=np.uint8)
        
        # Statistics
        self.frame_count = 0
        self.population = 0
        
    def randomize(self):
        """Randomly initialize the grid with 30% chance of each cell being alive."""
        self.grid = (np.random.random((self.height, self.width)) < 0.3).astype(np.uint8)
        self.update_population()
        
    def clear(self):
        """Clear all cells to dead state."""
        self.grid.fill(0)
        self.next_grid.fill(0)
        self.population = 0
        
    def count_neighbors(self, x, y):
        """Count live neighbors for a cell at position (x, y) with wrap-around."""
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx = (x + dx) % self.width
                ny = (y + dy) % self.height
                count += self.grid[ny, nx]
        return count
    
    def update(self):
        """Apply Game of Life rules to compute next generation."""
        self.next_grid.fill(0)
        
        for y in range(self.height):
            for x in range(self.width):
                neighbors = self.count_neighbors(x, y)
                current_state = self.grid[y, x]
                
                if current_state == 1:
                    # Cell is alive - check survival rules
                    if self.survival_min <= neighbors <= self.survival_max:
                        self.next_grid[y, x] = 1
                else:
                    # Cell is dead - check birth rule
                    if neighbors == self.birth_rule:
                        self.next_grid[y, x] = 1
        
        # Swap grids
        self.grid, self.next_grid = self.next_grid, self.grid
        self.frame_count += 1
        self.update_population()
    
    def update_population(self):
        """Update the population count."""
        self.population = int(np.sum(self.grid))
    
    def toggle_cell(self, x, y):
        """Toggle cell state at position (x, y)."""
        if 0 <= y < self.height and 0 <= x < self.width:
            self.grid[y, x] = 1 - self.grid[y, x]
            self.update_population()


class RetroRenderer:
    """Retro neon wave renderer with CRT effects."""
    
    def __init__(self, screen, cell_size):
        self.screen = screen
        self.cell_size = cell_size
        self.width = screen.get_width() // cell_size
        self.height = screen.get_height() // cell_size
        self.scanline_surface = None
        self._create_scanline_effect()
    
    def _create_scanline_effect(self):
        """Create scanline overlay for retro CRT effect."""
        self.scanline_surface = pygame.Surface((self.width, self.height))
        for y in range(0, self.height, 2):
            pygame.draw.line(self.scanline_surface, (0, 0, 0, 128), 
                           (0, y), (self.width, y))
    
    def draw_grid(self, game, color_alive, color_dead, color_grid):
        """Draw the Game of Life grid with neon effects."""
        self.screen.fill(color_dead)
        
        # Draw alive cells with glow effect
        for y in range(game.height):
            for x in range(game.width):
                if game.grid[y, x] == 1:
                    rect = pygame.Rect(
                        x * self.cell_size,
                        y * self.cell_size,
                        self.cell_size - 1,
                        self.cell_size - 1
                    )
                    # Create glow by drawing larger first
                    glow_rect = pygame.Rect(
                        x * self.cell_size - 2,
                        y * self.cell_size - 2,
                        self.cell_size + 3,
                        self.cell_size + 3
                    )
                    pygame.draw.rect(self.screen, color_alive, glow_rect)
                    pygame.draw.rect(self.screen, color_alive, rect)
        
        # Draw subtle grid lines
        for x in range(0, self.width * self.cell_size, self.cell_size):
            pygame.draw.line(self.screen, color_grid, 
                           (x, 0), (x, self.height * self.cell_size))
        for y in range(0, self.height * self.cell_size, self.cell_size):
            pygame.draw.line(self.screen, color_grid, 
                           (0, y), (self.width * self.cell_size, y))
        
        # Apply scanline effect
        if self.scanline_surface:
            self.screen.blit(self.scanline_surface, (0, 0))
    
    def draw_ui(self, game, fps, font_small, font_large):
        """Draw on-screen UI elements."""
        ui_height = 80
        offset_y = self.height * self.cell_size
        
        # Draw control panel background
        panel_rect = pygame.Rect(0, offset_y, self.width * self.cell_size, ui_height)
        pygame.draw.rect(self.screen, (20, 20, 30), panel_rect)
        pygame.draw.line(self.screen, COLOR_CELL_ALIVE, 
                       (0, offset_y), (self.width * self.cell_size, offset_y), 2)
        
        # Frame counter
        frame_text = f"Frame: {game.frame_count}"
        fps_text = f"FPS: {fps}"
        pop_text = f"Population: {game.population}"
        
        font_small.set_bold(True)
        frame_surface = font_small.render(frame_text, True, COLOR_TEXT)
        fps_surface = font_small.render(fps_text, True, COLOR_TEXT)
        pop_surface = font_small.render(pop_text, True, COLOR_TEXT)
        
        self.screen.blit(frame_surface, (10, offset_y + 5))
        self.screen.blit(fps_surface, (150, offset_y + 5))
        self.screen.blit(pop_surface, (300, offset_y + 5))
        
        # Rule parameters
        rule_text = f"Rules: Birth={game.birth_rule}, Survival={game.survival_min}-{game.survival_max}"
        rule_surface = font_small.render(rule_text, True, COLOR_CELL_ALIVE)
        self.screen.blit(rule_surface, (10, offset_y + 30))
        
        # Control hints
        hints = [
            "Space: Pause/Resume | R: Randomize | C: Clear | +/-: Speed | Click: Toggle",
            f"Current Speed: {fps} FPS"
        ]
        for i, hint in enumerate(hints):
            hint_surface = font_small.render(hint, True, (200, 200, 255))
            self.screen.blit(hint_surface, (10, offset_y + 60 + i * 20))


def main():
    """Main entry point."""
    # Initialize pygame
    pygame.init()
    
    # Create screen with resizable flag
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Game of Life - Neon Wave Edition")
    
    # Clock for controlling FPS
    clock = pygame.time.Clock()
    
    # Initialize fonts
    font_large = pygame.font.Font(None, 24)
    font_small = pygame.font.Font(None, 16)
    
    # Create game instance with default rules
    game = GameOfLife(
        GRID_WIDTH, GRID_HEIGHT,
        BIRTH_RULE, SURVIVAL_MIN, SURVIVAL_MAX
    )
    game.randomize()
    
    # Initialize renderer
    renderer = RetroRenderer(screen, CELL_SIZE)
    
    # Game state
    paused = False
    speed = FPS
    
    # Main loop
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                
                elif event.key == pygame.K_SPACE:
                    paused = not paused
                
                elif event.key == pygame.K_r:
                    game.randomize()
                
                elif event.key == pygame.K_c:
                    game.clear()
                
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_KP_PLUS:
                    speed = min(speed + 5, 60)
                
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    speed = max(speed - 5, 5)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    x = event.pos[0] // CELL_SIZE
                    y = event.pos[1] // CELL_SIZE
                    game.toggle_cell(x, y)
            
            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                renderer = RetroRenderer(screen, CELL_SIZE)
        
        # Update game logic
        if not paused:
            game.update()
        
        # Render
        renderer.draw_grid(game, COLOR_CELL_ALIVE, COLOR_BG, COLOR_GRID)
        renderer.draw_ui(game, clock.get_fps(), font_small, font_large)
        
        pygame.display.flip()
        clock.tick(speed)
    
    # Cleanup
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()

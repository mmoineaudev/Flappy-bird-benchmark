#!/usr/bin/env python3
"""
Conway's Game of Life - Python Pygame Implementation
Neon Retro Aesthetic with CRT Effects
"""

import pygame
import random
import math

# Constants
CELL_SIZE = 15
GRID_WIDTH = 80
GRID_HEIGHT = 40
BG_COLOR = (10, 10, 15)
GRID_COLOR = (30, 30, 50)
SCANLINE_COLOR = (0, 0, 0, 50)
FPS = 30

# Neon colors (cyan, magenta, purple)
NEON_CYAN = (0, 255, 255)
NEON_MAGENTA = (255, 0, 255)
NEON_PURPLE = (157, 78, 221)

class GameOfLife:
    def __init__(self):
        pygame.init()
        
        # Calculate window size
        self.width = GRID_WIDTH * CELL_SIZE
        self.height = GRID_HEIGHT * CELL_SIZE
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Game of Life - Conway's Simulation")
        
        # Font setup
        self.font = pygame.font.SysFont('monospace', 14, bold=True)
        self.small_font = pygame.font.SysFont('monospace', 10)
        
        # Grid and rules
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.born_rule = 3  # Birth when exactly 3 neighbors
        self.survive_min = 2  # Minimum neighbors to survive
        self.survive_max = 3  # Maximum neighbors to survive
        
        # Animation state
        self.running = True
        self.paused = False
        self.speed = FPS
        self.frame_count = 0
        self.population = 0
        
        # CRT effect
        self.scanline_offset = 0
        
        # Initialize grid with random pattern
        self.randomize_grid()
    
    def count_neighbors(self, x, y):
        """Count live neighbors for a cell."""
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT:
                    count += self.grid[ny][nx]
        return count
    
    def update_grid(self):
        """Apply Game of Life rules."""
        new_grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                neighbors = self.count_neighbors(x, y)
                
                # Birth rule
                if self.grid[y][x] == 0 and neighbors == self.born_rule:
                    new_grid[y][x] = 1
                
                # Survival rule
                elif self.grid[y][x] == 1 and self.survive_min <= neighbors <= self.survive_max:
                    new_grid[y][x] = 1
        
        self.grid = new_grid
    
    def randomize_grid(self):
        """Randomize grid with 20% density."""
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                self.grid[y][x] = 1 if random.random() < 0.2 else 0
        self.frame_count = 0
    
    def clear_grid(self):
        """Clear the grid."""
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.frame_count = 0
    
    def get_cell_color(self, x, y, age=0):
        """Get neon color with glow effect based on position and age."""
        # Color cycling based on position and time
        offset = (self.frame_count + x * 3 + y * 2) % 3
        
        if offset == 0:
            base_color = NEON_CYAN
        elif offset == 1:
            base_color = NEON_MAGENTA
        else:
            base_color = NEON_PURPLE
        
        # Add slight brightness variation for glow effect
        brightness = random.randint(200, 255)
        return (
            min(255, base_color[0] * brightness // 255),
            min(255, base_color[1] * brightness // 255),
            min(255, base_color[2] * brightness // 255)
        )
    
    def draw(self):
        """Render the game."""
        self.screen.fill(BG_COLOR)
        
        # Draw grid cells with glow effect
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    color = self.get_cell_color(x, y)
                    
                    # Draw main cell
                    rect = pygame.Rect(
                        x * CELL_SIZE,
                        y * CELL_SIZE,
                        CELL_SIZE - 1,
                        CELL_SIZE - 1
                    )
                    pygame.draw.rect(self.screen, color, rect)
                    
                    # Draw glow effect (larger, semi-transparent version)
                    glow_rect = pygame.Rect(
                        x * CELL_SIZE - 2,
                        y * CELL_SIZE - 2,
                        CELL_SIZE + 4,
                        CELL_SIZE + 4
                    )
                    glow_surface = pygame.Surface((CELL_SIZE + 6, CELL_SIZE + 6), pygame.SRCALPHA)
                    pygame.draw.rect(glow_surface, (*color, 50), glow_surface.get_rect())
                    self.screen.blit(glow_surface, glow_rect.topleft)
        
        # Draw grid lines
        for x in range(0, self.width, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, self.height), 1)
        for y in range(0, self.height, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (self.width, y), 1)
        
        # Draw scanlines
        self.scanline_offset = (self.scanline_offset + 1) % 4
        for y in range(self.scanline_offset, self.height, 4):
            pygame.draw.line(self.screen, SCANLINE_COLOR, (0, y), (self.width, y))
        
        # Calculate population
        self.population = sum(sum(row) for row in self.grid)
        
        # Draw UI
        self.draw_ui()
    
    def draw_ui(self):
        """Draw on-screen UI elements."""
        # Stats panel
        stats_x = 10
        stats_y = 10
        
        # Title
        title = self.font.render("GAME OF LIFE", True, NEON_CYAN)
        self.screen.blit(title, (stats_x, stats_y))
        
        # Stats
        stats = [
            f"Frame: {self.frame_count}",
            f"Population: {self.population}",
            f"Born Rule: {self.born_rule}",
            f"Survive: [{self.survive_min}, {self.survive_max}]",
            f"Speed: {FPS} FPS",
        ]
        
        for i, stat in enumerate(stats):
            text = self.small_font.render(stat, True, NEON_MAGENTA)
            self.screen.blit(text, (stats_x, stats_y + 30 + i * 15))
        
        # Controls hint
        controls = [
            "Controls:",
            "SPACE - Pause/Resume",
            "R - Randomize",
            "C - Clear",
            "+/- - Adjust Speed",
            "Click - Toggle Cell"
        ]
        
        control_x = self.width - 180
        for i, control in enumerate(controls):
            text = self.small_font.render(control, True, NEON_PURPLE)
            self.screen.blit(text, (control_x, stats_y + 30 + i * 15))
        
        # Pause indicator
        if self.paused:
            pause_text = self.font.render("PAUSED", True, (255, 100, 100))
            text_rect = pause_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(pause_text, text_rect)
    
    def handle_input(self):
        """Handle keyboard and mouse input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                
                elif event.key == pygame.K_r:
                    self.randomize_grid()
                
                elif event.key == pygame.K_c:
                    self.clear_grid()
                
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    self.speed = min(60, self.speed + 5)
                
                elif event.key == pygame.K_MINUS:
                    self.speed = max(1, self.speed - 5)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    x, y = pygame.mouse.get_pos()
                    grid_x = x // CELL_SIZE
                    grid_y = y // CELL_SIZE
                    
                    if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                        self.grid[grid_y][grid_x] = 1 if self.grid[grid_y][grid_x] == 0 else 0
    
    def run(self):
        """Main game loop."""
        clock = pygame.time.Clock()
        
        while self.running:
            self.handle_input()
            
            if not self.paused:
                self.update_grid()
                self.frame_count += 1
            
            self.draw()
            
            # Cap framerate
            clock.tick(self.speed)
            pygame.display.flip()
        
        pygame.quit()

def main():
    """Main entry point."""
    game = GameOfLife()
    game.run()

if __name__ == "__main__":
    main()
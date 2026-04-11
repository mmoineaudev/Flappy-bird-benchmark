#!/usr/bin/env python3
"""
Conway's Game of Life - Retro Neon Edition
Parametrizable rules with CRT aesthetic effects
"""

import pygame
import random
import sys
from typing import List, Tuple

# Configuration
GRID_WIDTH = 80
GRID_HEIGHT = 40
CELL_SIZE = 15
FPS = 60

# Retro color palette
BACKGROUND = (10, 10, 15)
NEON_CYAN = (0, 255, 255)
NEON_MAGENTA = (255, 0, 255)
NEON_PURPLE = (157, 78, 237)
GRID_COLOR = (30, 30, 40)

# Game of Life rules (configurable)
BIRTH_RULE = 3          # Number of neighbors to birth a cell
SURVIVE_MIN = 2         # Minimum neighbors to survive
SURVIVE_MAX = 3         # Maximum neighbors to survive

class GameOfLife:
    def __init__(self, width: int, height: int, cell_size: int):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid = [[False for _ in range(width)] for _ in range(height)]
        self.paused = False
        self.frame_count = 0
        
    def randomize(self):
        """Fill grid with random cells"""
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = random.random() < 0.3
    
    def clear(self):
        """Clear all cells"""
        self.grid = [[False for _ in range(self.width)] for _ in range(self.height)]
    
    def count_neighbors(self, x: int, y: int) -> int:
        """Count live neighbors with wrapping edges"""
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx = (x + dx) % self.width
                ny = (y + dy) % self.height
                if self.grid[ny][nx]:
                    count += 1
        return count
    
    def update(self):
        """Advance simulation by one generation"""
        if self.paused:
            return
        
        new_grid = [[False for _ in range(self.width)] for _ in range(self.height)]
        
        for y in range(self.height):
            for x in range(self.width):
                neighbors = self.count_neighbors(x, y)
                current = self.grid[y][x]
                
                # Apply Game of Life rules
                if current and SURVIVE_MIN <= neighbors <= SURVIVE_MAX:
                    new_grid[y][x] = True
                elif not current and neighbors == BIRTH_RULE:
                    new_grid[y][x] = True
        
        self.grid = new_grid
        self.frame_count += 1
    
    def get_population(self) -> int:
        """Count total live cells"""
        return sum(sum(row) for row in self.grid)
    
    def toggle_cell(self, x: int, y: int):
        """Toggle cell at grid position"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = not self.grid[y][x]


class RetroRenderer:
    def __init__(self, screen: pygame.Surface, game: GameOfLife):
        self.screen = screen
        self.game = game
        self.font_large = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)
        self.scanline_alpha = 0
    
    def draw_grid(self):
        """Draw the cell grid with neon glow effect"""
        for y in range(self.game.height + 1):
            pygame.draw.line(self.screen, GRID_COLOR, 
                           (0, y * self.game.cell_size),
                           (self.game.width * self.game.cell_size, y * self.game.cell_size))
        
        for x in range(self.game.width + 1):
            pygame.draw.line(self.screen, GRID_COLOR,
                           (x * self.game.cell_size, 0),
                           (x * self.game.cell_size, self.game.height * self.game.cell_size))
    
    def draw_cells(self):
        """Draw live cells with neon colors"""
        for y in range(self.game.height):
            for x in range(self.game.width):
                if self.game.grid[y][x]:
                    # Cycle through neon colors based on position and frame
                    hue_cycle = (x + y + self.game.frame_count // 10) % 3
                    color = [NEON_CYAN, NEON_MAGENTA, NEON_PURPLE][hue_cycle]
                    
                    # Draw cell with slight glow effect
                    rect = pygame.Rect(x * self.game.cell_size + 1, 
                                      y * self.game.cell_size + 1,
                                      self.game.cell_size - 2,
                                      self.game.cell_size - 2)
                    pygame.draw.rect(self.screen, color, rect)
    
    def draw_scanlines(self):
        """Add retro CRT scanline effect"""
        self.scanline_alpha = (self.scanline_alpha + 1) % 20
        
        for y in range(0, self.screen.get_height(), 4):
            alpha = 15 if y % 8 < 2 else 0
            scanline = pygame.Surface((self.screen.get_width(), 2))
            scanline.set_alpha(alpha)
            scanline.fill((255, 255, 255))
            self.screen.blit(scanline, (0, y))
    
    def draw_ui(self):
        """Draw on-screen UI elements"""
        # Frame counter
        frame_text = self.font_small.render(f"Frame: {self.game.frame_count}", True, NEON_CYAN)
        self.screen.blit(frame_text, (10, 10))
        
        # Population count
        pop_text = self.font_small.render(f"Population: {self.game.get_population()}", True, NEON_MAGENTA)
        self.screen.blit(pop_text, (10, 40))
        
        # Rules display
        rules_text = self.font_small.render(f"Rules: B{BIRTH_RULE}/S{SURVIVE_MIN}-{SURVIVE_MAX}", True, NEON_PURPLE)
        self.screen.blit(rules_text, (10, 70))
        
        # Control hints
        controls = [
            "Space: Pause/Resume",
            "R: Randomize",
            "C: Clear",
            "+/-: Speed",
            "Click: Toggle cell"
        ]
        for i, control in enumerate(controls):
            text = self.font_small.render(control, True, (200, 200, 200))
            self.screen.blit(text, (self.screen.get_width() - 250, 10 + i * 20))
        
        # Pause indicator
        if self.game.paused:
            pause_text = self.font_large.render("PAUSED", True, NEON_CYAN)
            rect = pause_text.get_rect(center=(self.screen.get_width() // 2, 
                                               self.screen.get_height() // 2))
            self.screen.blit(pause_text, rect)
    
    def draw(self):
        """Render complete frame"""
        self.screen.fill(BACKGROUND)
        self.draw_grid()
        self.draw_cells()
        self.draw_scanlines()
        self.draw_ui()


def main():
    pygame.init()
    
    # Create screen
    screen_width = GRID_WIDTH * CELL_SIZE
    screen_height = GRID_HEIGHT * CELL_SIZE
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Game of Life - Retro Neon Edition")
    
    # Initialize game and renderer
    game = GameOfLife(GRID_WIDTH, GRID_HEIGHT, CELL_SIZE)
    game.randomize()
    renderer = RetroRenderer(screen, game)
    
    clock = pygame.time.Clock()
    running = True
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    game.paused = not game.paused
                elif event.key == pygame.K_r:
                    game.randomize()
                elif event.key == pygame.K_c:
                    game.clear()
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    pass  # Speed adjustment placeholder
                elif event.key == pygame.K_MINUS:
                    pass  # Speed adjustment placeholder
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    x = event.pos[0] // CELL_SIZE
                    y = event.pos[1] // CELL_SIZE
                    game.toggle_cell(x, y)
        
        game.update()
        renderer.draw()
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()

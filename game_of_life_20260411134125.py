#!/usr/bin/env python3
"""
Conway's Game of Life Simulation with Pygame
Features: Retro styling with neon wave visuals, dark background, glowing cells,
          scanline/CRT effects, and interactive controls.
"""

import pygame
import random
import sys
import time

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 1024, 768
GRID_WIDTH = 80
GRID_HEIGHT = 40
CELL_SIZE = 15
FPS = 10

# Colors
BACKGROUND = (10, 10, 15)
GRID_COLOR = (30, 30, 40)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)
PURPLE = (157, 78, 221)
GLow_COLOR = CYAN  # Default glow color

# Create the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Conway's Game of Life - Pygame Version")
clock = pygame.time.Clock()

# Font setup
font = pygame.font.SysFont(None, 24)
title_font = pygame.font.SysFont(None, 36)

class GameOfLife:
    def __init__(self, width, height, cell_size=15):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        self.next_grid = [[0 for _ in range(width)] for _ in range(height)]
        self.generation = 0
        self.population = 0
        self.running = True
        self.speed = FPS
        self.birth_rule = 3  # Number of live neighbors required to spawn a new cell
        self.survival_min = 2  # Minimum live neighbors for survival
        self.survival_max = 3  # Maximum live neighbors for survival
        
    def randomize(self):
        """Randomize the grid with live cells"""
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = random.randint(0, 1)
        self.update_population()
        
    def clear(self):
        """Clear the grid"""
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = 0
        self.generation = 0
        self.update_population()
        
    def update_population(self):
        """Count the number of live cells"""
        self.population = sum(sum(row) for row in self.grid)
        
    def count_neighbors(self, x, y):
        """Count the number of live neighbors for a cell"""
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = (x + dx) % self.width, (y + dy) % self.height
                count += self.grid[ny][nx]
        return count
        
    def update(self):
        """Update the grid based on Conway's Game of Life rules"""
        if not self.running:
            return
            
        for y in range(self.height):
            for x in range(self.width):
                neighbors = self.count_neighbors(x, y)
                
                # Apply rules
                if self.grid[y][x] == 1:  # Cell is alive
                    if neighbors < self.survival_min or neighbors > self.survival_max:
                        self.next_grid[y][x] = 0  # Dies
                    else:
                        self.next_grid[y][x] = 1  # Survives
                else:  # Cell is dead
                    if neighbors == self.birth_rule:
                        self.next_grid[y][x] = 1  # Born
                    else:
                        self.next_grid[y][x] = 0  # Stays dead
                        
        # Swap grids
        self.grid, self.next_grid = self.next_grid, self.grid
        self.generation += 1
        self.update_population()
        
    def toggle_cell(self, x, y):
        """Toggle the state of a cell"""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = 1 - self.grid[y][x]
            self.update_population()
            
    def draw(self, screen):
        """Draw the grid with neon glow effects"""
        # Draw background
        screen.fill(BACKGROUND)
        
        # Draw grid lines
        for y in range(0, HEIGHT, self.cell_size):
            pygame.draw.line(screen, GRID_COLOR, (0, y), (WIDTH, y))
        for x in range(0, WIDTH, self.cell_size):
            pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, HEIGHT))
            
        # Draw cells with glow effect
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == 1:
                    # Draw cell body
                    rect = pygame.Rect(x * self.cell_size, y * self.cell_size, 
                                     self.cell_size, self.cell_size)
                    pygame.draw.rect(screen, GLow_COLOR, rect)
                    
                    # Draw glow effect (slightly larger rectangle with alpha)
                    glow_rect = pygame.Rect(x * self.cell_size - 2, y * self.cell_size - 2,
                                          self.cell_size + 4, self.cell_size + 4)
                    glow_surface = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                    glow_color = (*GLow_COLOR, 100)  # Add alpha for glow effect
                    pygame.draw.rect(glow_surface, glow_color, (0, 0, glow_rect.width, glow_rect.height))
                    screen.blit(glow_surface, glow_rect)
        
        # Draw scanline overlay effect
        scanline_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        for y in range(0, HEIGHT, 4):
            pygame.draw.line(scanline_surface, (0, 0, 0, 30), (0, y), (WIDTH, y))
        screen.blit(scanline_surface, (0, 0))
        
        # Draw UI elements
        self.draw_ui(screen)
        
    def draw_ui(self, screen):
        """Draw on-screen UI elements"""
        # Title
        title = title_font.render("Conway's Game of Life", True, CYAN)
        screen.blit(title, (10, 10))
        
        # Stats
        stats = [
            f"Generation: {self.generation}",
            f"Population: {self.population}",
            f"Speed: {self.speed} FPS",
            f"Rules: B{self.birth_rule}/S{self.survival_min}-{self.survival_max}"
        ]
        
        for i, stat in enumerate(stats):
            text = font.render(stat, True, MAGENTA)
            screen.blit(text, (10, 50 + i * 30))
            
        # Controls
        controls = [
            "Controls:",
            "Space - Pause/Resume",
            "R - Randomize",
            "C - Clear",
            "+/- - Speed Up/Down",
            "Click - Toggle Cell"
        ]
        
        for i, control in enumerate(controls):
            text = font.render(control, True, PURPLE)
            screen.blit(text, (WIDTH - 250, 10 + i * 30))

def main():
    # Create game instance
    game = GameOfLife(GRID_WIDTH, GRID_HEIGHT, CELL_SIZE)
    
    # Randomize initial state
    game.randomize()
    
    # Main loop
    running = True
    last_time = time.time()
    
    while running:
        current_time = time.time()
        delta_time = current_time - last_time
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game.running = not game.running
                elif event.key == pygame.K_r:
                    game.randomize()
                elif event.key == pygame.K_c:
                    game.clear()
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    game.speed = min(game.speed + 2, 60)
                elif event.key == pygame.K_MINUS:
                    game.speed = max(game.speed - 2, 2)
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    x, y = pygame.mouse.get_pos()
                    grid_x = x // game.cell_size
                    grid_y = y // game.cell_size
                    game.toggle_cell(grid_x, grid_y)
        
        # Update game state
        if delta_time >= 1.0 / game.speed:
            game.update()
            last_time = current_time
            
        # Draw everything
        game.draw(screen)
        
        # Update display
        pygame.display.flip()
        clock.tick(FPS)
        
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
#!/usr/bin/env python3
"""
Conway's Game of Life - Retro Neon Wave Version
Python/Pygame implementation with CRT/scanline effects
"""

import pygame
import sys
import time
from datetime import datetime

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
GRID_WIDTH = 80
GRID_HEIGHT = 40
CELL_SIZE = 15
BORDER = 2  # Border width
SCANLINE_COUNT = 30

# Colors
COLOR_BG = (10, 10, 15)      # Dark background
COLOR_GRID = (20, 20, 30)   # Subtle grid lines
COLOR_CELL_CYAN = (0, 255, 255)      # Cyan neon
COLOR_CELL_MAGENTA = (255, 0, 255)   # Magenta neon
COLOR_CELL_PURPLE = (157, 78, 222)   # Purple neon
COLOR_TEXT = (200, 200, 230)         # Text color
COLOR_SCANLINE = (0, 0, 0, 40)       # Semi-transparent for scanlines

# Rule parameters (configurable)
RULE_BIRTH = 3          # Number of neighbors to spawn a cell
RULE_SURVIVE_MIN = 2    # Minimum neighbors to survive
RULE_SURVIVE_MAX = 3    # Maximum neighbors to survive
FPS_TARGET = 10         # Animation speed

class GameOfLife:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        self.paused = False
        self.frame_count = 0
        self.last_update = time.time()
        self.current_color = COLOR_CELL_CYAN
        self.color_cycle_speed = 0.5  # Seconds per color change
        
    def get_neighbor_count(self, x, y):
        """Count alive neighbors for a cell"""
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                    
                nx, ny = x + i, y + j
                # Wrap around (torus topology)
                if nx < 0:
                    nx += self.width
                if ny < 0:
                    ny += self.height
                if nx >= self.width:
                    nx -= self.width
                if ny >= self.height:
                    ny -= self.height
                    
                count += self.grid[ny][nx]
        return count
    
    def update(self):
        """Update the grid according to Game of Life rules"""
        if self.paused:
            return
            
        new_grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        for y in range(self.height):
            for x in range(self.width):
                neighbors = self.get_neighbor_count(x, y)
                
                # Apply rules
                if self.grid[y][x] == 1:
                    # Cell is alive
                    if RULE_SURVIVE_MIN <= neighbors <= RULE_SURVIVE_MAX:
                        new_grid[y][x] = 1
                    else:
                        new_grid[y][x] = 0
                else:
                    # Cell is dead
                    if neighbors == RULE_BIRTH:
                        new_grid[y][x] = 1
                    else:
                        new_grid[y][x] = 0
        
        self.grid = new_grid
        self.frame_count += 1
        
        # Cycle colors periodically
        current_time = time.time()
        if (current_time - self.last_update) > self.color_cycle_speed:
            self.last_update = current_time
            self.cycle_color()
    
    def cycle_color(self):
        """Cycle between neon colors"""
        if self.current_color == COLOR_CELL_CYAN:
            self.current_color = COLOR_CELL_MAGENTA
        elif self.current_color == COLOR_CELL_MAGENTA:
            self.current_color = COLOR_CELL_PURPLE
        else:
            self.current_color = COLOR_CELL_CYAN
    
    def randomize(self):
        """Fill grid with random cells"""
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = 1 if pygame.time.get_ticks() % (x * y + 1) < 50 else 0
    
    def clear(self):
        """Clear the grid"""
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = 0
    
    def toggle_cell(self, mouse_x, mouse_y):
        """Toggle cell state at position"""
        grid_x = mouse_x // CELL_SIZE
        grid_y = mouse_y // CELL_SIZE
        
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            self.grid[grid_y][grid_x] = 1 - self.grid[grid_y][grid_x]
    
    def get_population(self):
        """Count live cells"""
        return sum(sum(row) for row in self.grid)

# Initialize game
game = GameOfLife(GRID_WIDTH, GRID_HEIGHT)
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Game of Life - Retro Neon Wave")

# Set random initial state
game.randomize()

# FPS clock
clock = pygame.time.Clock()
font = pygame.font.SysFont('monospace', 14)

def draw_grid():
    """Draw the grid with retro effects"""
    # Fill background
    screen.fill(COLOR_BG)
    
    # Draw cells
    for y in range(game.height):
        for x in range(game.width):
            if game.grid[y][x] == 1:
                # Draw cell with glow effect
                rect = pygame.Rect(
                    x * CELL_SIZE, 
                    y * CELL_SIZE, 
                    CELL_SIZE - BORDER, 
                    CELL_SIZE - BORDER
                )
                # Draw cell with neon color
                pygame.draw.rect(screen, game.current_color, rect)
    
    # Draw grid lines
    for x in range(0, SCREEN_WIDTH, CELL_SIZE):
        pygame.draw.line(screen, COLOR_GRID, (x, 0), (x, SCREEN_HEIGHT), 1)
    for y in range(0, SCREEN_HEIGHT, CELL_SIZE):
        pygame.draw.line(screen, COLOR_GRID, (0, y), (SCREEN_WIDTH, y), 1)

def draw_scanlines():
    """Draw retro scanline effect"""
    line_height = SCREEN_HEIGHT // SCANLINE_COUNT
    for i in range(SCANLINE_COUNT):
        y = i * line_height
        alpha = SCANLINE_COUNT - i
        color_with_alpha = (COLOR_SCANLINE[0], COLOR_SCANLINE[1], COLOR_SCANLINE[2], alpha)
        
        # Use per-pixel surface manipulation for scanlines
        scanline_surface = pygame.Surface((SCREEN_WIDTH, line_height))
        scanline_surface.fill(color_with_alpha)
        scanline_surface.set_alpha(alpha // 4)  # Make it subtle
        screen.blit(scanline_surface, (0, y))

def draw_ui():
    """Draw on-screen UI elements"""
    # Stats display
    stats_y = 10
    stats_lines = [
        f"Frame: {game.frame_count}",
        f"Population: {game.get_population()}",
        f"FPS: {clock.get_fps():.1f}",
        f"Rules: B={RULE_BIRTH}, S=[{RULE_SURVIVE_MIN}-{RULE_SURVIVE_MAX}]",
        f"Grid: {GRID_WIDTH}x{GRID_HEIGHT}",
        f"Speed: {game.color_cycle_speed:.1f}s/cycle",
    ]
    
    for i, line in enumerate(stats_lines):
        text = font.render(line, True, COLOR_TEXT)
        screen.blit(text, (10, stats_y + i * 20))
    
    # Controls hint
    controls_y = SCREEN_HEIGHT - 80
    controls = [
        "Controls: [Space] Pause/Resume | [R] Randomize | [C] Clear",
        "          [+] Speed Up | [-] Slow Down | [Mouse] Toggle Cell"
    ]
    
    for i, line in enumerate(controls):
        text = font.render(line, True, (150, 150, 180))
        screen.blit(text, (10, controls_y + i * 20))

def main():
    global RULE_BIRTH, RULE_SURVIVE_MIN, RULE_SURVIVE_MAX, FPS_TARGET
    
    running = True
    frame_time = 1.0 / FPS_TARGET
    
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game.paused = not game.paused
                
                elif event.key == pygame.K_r:
                    game.randomize()
                
                elif event.key == pygame.K_c:
                    game.clear()
                
                elif event.key == pygame.K_PLUS or event.key == pygame.K_UP:
                    FPS_TARGET = min(FPS_TARGET + 5, 60)
                    frame_time = 1.0 / FPS_TARGET
                
                elif event.key == pygame.K_MINUS or event.key == pygame.K_DOWN:
                    FPS_TARGET = max(FPS_TARGET - 5, 1)
                    frame_time = 1.0 / FPS_TARGET
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    game.toggle_cell(event.pos[0], event.pos[1])
        
        # Update game state
        current_time = time.time()
        if not game.paused and (current_time - game.last_update) >= frame_time:
            game.update()
            game.last_update = current_time
        
        # Render
        draw_grid()
        draw_scanlines()
        draw_ui()
        
        pygame.display.flip()
        clock.tick(FPS_TARGET)
    
    pygame.quit()
    sys.exit(0)

if __name__ == "__main__":
    main()

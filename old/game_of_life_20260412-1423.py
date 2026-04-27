#!/usr/bin/env python3
"""
Conway's Game of Life - Retro Neon Edition
A parametrizable Game of Life simulation with neon wave visuals and CRT scanline effects.
"""

import pygame
import random
import time
from datetime import datetime

# Configuration constants
CELL_SIZE = 15
GRID_WIDTH = 80
GRID_HEIGHT = 40
FPS = 30

# Colors - Neon palette
COLOR_BG = (10, 10, 15)          # Dark background
COLOR_GRID = (30, 30, 50)        # Subtle grid lines
COLOR_CELL_CYAN = (0, 255, 255)  # Cyan neon
COLOR_CELL_MAGENTA = (255, 0, 255)  # Magenta neon
COLOR_CELL_PURPLE = (157, 78, 221)  # Purple neon

# Rule parameters (parametrizable)
BIRTH_RULE = 3        # Cells born if exactly 3 neighbors
SURVIVAL_MIN = 2      # Survive if 2 or more neighbors
SURVIVAL_MAX = 3      # Survive if at most 3 neighbors

class GameOfLife:
    """Parametrizable Conway's Game of Life implementation."""
    
    def __init__(self, width=GRID_WIDTH, height=GRID_HEIGHT, cell_size=CELL_SIZE):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.cols = width // cell_size
        self.rows = height // cell_size
        
        # Initialize grid with random cells (10% density)
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.randomize()
        
        # Timing
        self.last_update = time.time()
        self.update_interval = 1.0 / FPS
        
        # Stats
        self.frame_count = 0
        self.population = 0
    
    def randomize(self):
        """Randomize grid with specified density."""
        for i in range(self.rows):
            for j in range(self.cols):
                self.grid[i][j] = 1 if random.random() < 0.1 else 0
        self.update_stats()
    
    def clear(self):
        """Clear all cells."""
        self.grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        self.update_stats()
    
    def update_stats(self):
        """Update population count."""
        self.population = sum(sum(row) for row in self.grid)
    
    def get_neighbors(self, x, y):
        """Count live neighbors for cell at position (x, y)."""
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.cols and 0 <= ny < self.rows:
                    count += self.grid[ny][nx]
        return count
    
    def update(self):
        """Update grid based on Game of Life rules."""
        new_grid = [row[:] for row in self.grid]
        
        for i in range(self.rows):
            for j in range(self.cols):
                neighbors = self.get_neighbors(j, i)
                cell = self.grid[i][j]
                
                # Birth rule
                if cell == 0 and neighbors == BIRTH_RULE:
                    new_grid[i][j] = 1
                # Survival rule
                elif cell == 1 and (SURVIVAL_MIN <= neighbors <= SURVIVAL_MAX):
                    new_grid[i][j] = 1
                else:
                    new_grid[i][j] = 0
        
        self.grid = new_grid
        self.update_stats()
        self.frame_count += 1
    
    def toggle_cell(self, mouse_x, mouse_y):
        """Toggle cell at mouse position."""
        col = mouse_x // self.cell_size
        row = mouse_y // self.cell_size
        
        if 0 <= col < self.cols and 0 <= row < self.rows:
            self.grid[row][col] = 1 - self.grid[row][col]
            self.update_stats()
    
    def draw(self, screen):
        """Render the grid with neon styling."""
        # Draw background
        screen.fill(COLOR_BG)
        
        # Draw grid lines (subtle)
        for i in range(self.cols + 1):
            x = i * self.cell_size
            pygame.draw.line(screen, COLOR_GRID, (x, 0), (x, self.height))
        for j in range(self.rows + 1):
            y = j * self.cell_size
            pygame.draw.line(screen, COLOR_GRID, (0, y), (self.width, y))
        
        # Draw live cells with glow effect
        for i in range(self.rows):
            for j in range(self.cols):
                if self.grid[i][j] == 1:
                    x = j * self.cell_size
                    y = i * self.cell_size
                    
                    # Main cell color based on position (wave pattern)
                    pos = (x + y) % 3
                    if pos == 0:
                        color = COLOR_CELL_CYAN
                    elif pos == 1:
                        color = COLOR_CELL_MAGENTA
                    else:
                        color = COLOR_CELL_PURPLE
                    
                    # Draw cell with glow effect (draw larger, lighter rects)
                    for offset in [0, -1, 1]:
                        for offset_y in [0, -1, 1]:
                            if 0 <= x + offset < self.width and 0 <= y + offset_y < self.height:
                                pygame.draw.rect(
                                    screen,
                                    (color[0]//2, color[1]//2, color[2]//2),
                                    (x + offset, y + offset_y, self.cell_size, self.cell_size)
                                )
                    
                    # Draw main cell
                    pygame.draw.rect(screen, color, (x, y, self.cell_size, self.cell_size))
    
    def draw_ui(self, screen):
        """Draw UI elements."""
        font = pygame.font.SysFont('monospace', 16)
        
        # Stats
        frame_text = font.render(f"Frame: {self.frame_count}", True, (200, 200, 200))
        pop_text = font.render(f"Population: {self.population}", True, (200, 200, 200))
        
        screen.blit(frame_text, (10, 10))
        screen.blit(pop_text, (10, 30))
        
        # Rules
        rule_text = font.render(
            f"Rules: B{BIRTH_RULE}/S{SURVIVAL_MIN}-{SURVIVAL_MAX}",
            True, (180, 180, 180)
        )
        screen.blit(rule_text, (10, self.height - 30))
        
        # Controls
        controls = [
            "SPACE: Pause/Resume",
            "R: Randomize",
            "C: Clear",
            "+/-: Speed",
            "Click: Toggle cell"
        ]
        
        for idx, line in enumerate(controls):
            text = font.render(line, True, (150, 150, 150))
            screen.blit(text, (self.width - 250, 10 + idx * 20))

def draw_scanlines(screen):
    """Draw CRT scanline overlay effect."""
    for y in range(0, screen.get_height(), 2):
        pygame.draw.line(screen, (0, 0, 0), (0, y), (screen.get_width(), y), 1)

def main():
    """Main game loop."""
    # Initialize pygame
    pygame.init()
    
    # Set up display
    width = GRID_WIDTH * CELL_SIZE
    height = GRID_HEIGHT * CELL_SIZE
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Game of Life - Retro Neon Edition")
    
    # Create game instance
    game = GameOfLife()
    
    # Clock for controlling FPS
    clock = pygame.time.Clock()
    
    # Running state
    running = True
    paused = False
    
    # Speed control
    speed_multiplier = 1.0
    
    print("Game of Life - Retro Neon Edition")
    print("Controls:")
    print("  SPACE: Pause/Resume")
    print("  R: Randomize")
    print("  C: Clear")
    print("  +/-: Adjust speed")
    print("  Mouse click: Toggle cell")
    
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    game.randomize()
                elif event.key == pygame.K_c:
                    game.clear()
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    speed_multiplier = min(speed_multiplier * 1.5, 10.0)
                elif event.key == pygame.K_MINUS:
                    speed_multiplier = max(speed_multiplier / 1.5, 0.1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    game.toggle_cell(event.pos[0], event.pos[1])
        
        # Update game state
        if not paused:
            current_time = time.time()
            if current_time - game.last_update >= (1.0 / FPS) * speed_multiplier:
                game.update()
                game.last_update = current_time
        
        # Render
        game.draw(screen)
        draw_scanlines(screen)
        game.draw_ui(screen)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()

if __name__ == "__main__":
    main()
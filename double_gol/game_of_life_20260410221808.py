import pygame
import numpy as np
import random
from datetime import datetime

# --- Configuration & Rules ---
# Default parameters for the Game of Life
GRID_WIDTH = 80
GRID_HEIGHT = 40
CELL_SIZE = 15
FPS = 10

# Birth rule: number of live neighbors required to spawn a new cell
BIRTH_RULE = [3]
# Survival rule: minimum and maximum live neighbors for a cell to survive
SURVIVAL_RULE = [2, 3]

# Colors (Neon/Retro Aesthetic)
COLOR_BG = (10, 10, 15)           # Dark background #0a0a0f
COLOR_CELL_CYAN = (0, 255, 255)   # #00ffff
COLOR_CELL_MAGENTA = (255, 0, 255)# #ff00ff
COLOR_CELL_PURPLE = (157, 78, 221)# #9d4edd
COLOR_GRID = (30, 30, 45)         # Subtle grid lines
COLOR_TEXT = (255, 255, 255)

class GameOfLife:
    def __init__(self, width, height, cell_size):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid = np.zeros((height, width), dtype=int)
        self.paused = False
        self.fps = FPS
        self.frame_count = 0

    def randomize(self):
        self.grid = np.random.choice([0, 1], size=(self.height, self.width), p=[0.8, 0.2])

    def clear(self):
        self.grid.fill(0)

    def toggle_cell(self, x, y):
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y, x] = 1 - self.grid[y, x]

    def update(self):
        if self.paused:
            return

        # Count neighbors using a convolution-like approach with numpy
        # Padding to handle edges (toroidal/wrap-around behavior)
        padded_grid = np.pad(self.grid, 1, mode='wrap')
        neighbors = (
            padded_grid[0:-2, 0:-2] + padded_grid[0:-2, 1:-1] + padded_grid[0:-2, 2:] +
            padded_grid[1:-1, 0:-2]                      + padded_grid[1:-1, 2:] +
            padded_grid[2:  , 0:-2] + padded_grid[2:  , 1:-1] + padded_grid[2:  , 2:]
        )

        # Apply rules
        new_grid = self.grid.copy()
        
        # Birth
        for rule in BIRTH_RULE:
            new_grid[(self.grid == 0) & (neighbors == rule)] = 1
            
        # Survival
        # A cell survives if its neighbor count is within the survival range
        survival_mask = (self.grid == 1) & (np.isin(neighbors, SURVIVAL_RULE))
        new_grid[~survival_mask & (self.grid == 1)] = 0
        
        # Actually, it's simpler to just calculate the new state directly:
        # new_grid = zeros
        # if neighbors in birth: new_grid = 1
        # if neighbors in survival and current == 1: new_grid = 1
        
        final_grid = np.zeros_like(self.grid)
        # Births
        for r in BIRTH_RULE:
            final_grid[(self.grid == 0) & (neighbors == r)] = 1
        # Survivals
        for s in SURVIVAL_RULE:
            final_grid[(self.grid == 1) & (neighbors == s)] = 1
            
        self.grid = final_grid
        self.frame_count += 1

    def draw(self, screen):
        screen.fill(COLOR_BG)

        # Draw Grid Lines
        for x in range(0, self.width * self.cell_size + 1, self.cell_size):
            pygame.draw.line(screen, COLOR_GRID, (x, 0), (x, self.height * self.cell_size))
        for y in range(0, self.height * self.cell_size + 1, self.cell_size):
            pygame.draw.line(screen, COLOR_GRID, (0, y), (self.width * self.cell_size, y))

        # Draw Cells with "Glow" effect (simulated by drawing a slightly larger/fuzzier cell)
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y, x] == 1:
                    # Pick a neon color based on position or just cycle
                    color = COLOR_CELL_CYAN if (x + y) % 3 == 0 else (COLOR_CELL_MAGENTA if (x + y) % 3 == 1 else COLOR_CELL_PURPLE)
                    
                    rect = pygame.Rect(x * self.cell_size + 1, y * self.cell_size + 1, self.cell_size - 2, self.cell_size - 2)
                    pygame.draw.rect(screen, color, rect)
                    
                    # Simple "glow" approximation: a smaller, brighter center
                    inner_rect = pygame.Rect(x * self.cell_size + 4, y * self.cell_size + 4, self.cell_size - 8, self.cell_size - 8)
                    pygame.draw.rect(screen, (255, 255, 255), inner_rect)

        # Draw UI Elements
        font = pygame.font.SysFont("monospace", 16)
        
        # Stats
        pop_text = font.render(f"Pop: {np.sum(self.grid)}", True, COLOR_TEXT)
        frame_text = font.render(f"Frame: {self.frame_count}", True, COLOR_TEXT)
        rules_text = font.render(f"Rules: B{BIRTH_RULE} S{SURVIVAL_RULE}", True, COLOR_TEXT)
        controls_text = font.render("Space: Pause | R: Rand | C: Clear | +/-: Speed", True, COLOR_TEXT)

        screen.blit(pop_text, (10, 10))
        screen.blit(frame_text, (10, 30))
        screen.blit(rules_text, (10, 50))
        screen.blit(controls_text, (10, self.height * self.cell_size - 20))

def main():
    pygame.init()
    width = GRID_WIDTH * CELL_SIZE
    height = GRID_HEIGHT * CELL_SIZE + 60 # Extra space for UI
    screen = pygame.display.set_mode((width, height))
    pygame.display.set_caption("Game of Life - Neon Edition")
    clock = pygame.time.Clock()

    game = GameOfLife(GRID_WIDTH, GRID_HEIGHT, CELL_SIZE)
    game.randomize()

    running = True
    while running:
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
                elif event.key == pygame.K_EQUALS: # '+' key
                    game.fps = min(60, game.fps + 1)
                elif event.key == pygame.K_MINUS: # '-' key
                    game.fps = max(1, game.fps - 1)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                # Adjust for UI area
                grid_x = mx // CELL_SIZE
                grid_y = my // CELL_SIZE
                game.toggle_cell(grid_x, grid_y)

        game.update()
        game.draw(screen)
        
        pygame.display.flip()
        clock.tick(game.fps)

    pygame.quit()

if __name__ == "__main__":
    main()

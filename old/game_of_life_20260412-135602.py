import pygame
import random
import sys
import time

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
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
NEON_COLORS = [CYAN, MAGENTA, PURPLE]

# Create the screen
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Conway's Game of Life - Retro Neon Edition")
clock = pygame.time.Clock()

# Font setup
font_small = pygame.font.SysFont('courier', 16)
font_medium = pygame.font.SysFont('courier', 24)
font_large = pygame.font.SysFont('courier', 32)

class GameOfLife:
    def __init__(self):
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.running = False
        self.generation = 0
        self.fps = FPS
        self.birth_rule = 3
        self.survival_min = 2
        self.survival_max = 3
        self.cell_size = CELL_SIZE
        self.grid_width = GRID_WIDTH
        self.grid_height = GRID_HEIGHT
        self.scanline_overlay = True
        
        # Initialize with random pattern
        self.randomize_grid()
        
        # UI elements
        self.frame_counter = 0
        self.population = 0
        
    def randomize_grid(self):
        """Fill the grid with random live cells"""
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                self.grid[y][x] = random.randint(0, 1)
        self.update_population()
        
    def clear_grid(self):
        """Clear the entire grid"""
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                self.grid[y][x] = 0
        self.update_population()
        
    def update_population(self):
        """Count the number of live cells"""
        self.population = sum(sum(row) for row in self.grid)
        
    def count_neighbors(self, x, y):
        """Count live neighbors for a cell"""
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = (x + dx) % self.grid_width, (y + dy) % self.grid_height
                count += self.grid[ny][nx]
        return count
        
    def update(self):
        """Update the grid according to Conway's Game of Life rules"""
        if not self.running:
            return
            
        new_grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                neighbors = self.count_neighbors(x, y)
                if self.grid[y][x] == 1:  # Cell is alive
                    if self.survival_min <= neighbors <= self.survival_max:
                        new_grid[y][x] = 1
                else:  # Cell is dead
                    if neighbors == self.birth_rule:
                        new_grid[y][x] = 1
                        
        self.grid = new_grid
        self.generation += 1
        self.update_population()
        
    def toggle_cell(self, x, y):
        """Toggle the state of a cell"""
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
            self.grid[y][x] = 1 - self.grid[y][x]
            self.update_population()
            
    def draw_grid(self):
        """Draw the grid with retro styling"""
        # Draw grid cells
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                if self.grid[y][x] == 1:
                    # Choose a neon color
                    color = random.choice(NEON_COLORS)
                    pygame.draw.rect(screen, color, 
                                   (x * self.cell_size, y * self.cell_size, 
                                    self.cell_size, self.cell_size))
                    
                    # Add glow effect
                    glow_rect = pygame.Rect(x * self.cell_size - 2, 
                                          y * self.cell_size - 2,
                                          self.cell_size + 4, 
                                          self.cell_size + 4)
                    pygame.draw.rect(screen, color, glow_rect, 1)
                    
        # Draw grid lines
        for x in range(0, SCREEN_WIDTH, self.cell_size):
            pygame.draw.line(screen, GRID_COLOR, (x, 0), (x, SCREEN_HEIGHT))
        for y in range(0, SCREEN_HEIGHT, self.cell_size):
            pygame.draw.line(screen, GRID_COLOR, (0, y), (SCREEN_WIDTH, y))
            
    def draw_ui(self):
        """Draw UI elements"""
        # Draw frame counter
        frame_text = font_medium.render(f"Frame: {self.frame_counter}", True, CYAN)
        screen.blit(frame_text, (10, 10))
        
        # Draw population count
        pop_text = font_medium.render(f"Population: {self.population}", True, MAGENTA)
        screen.blit(pop_text, (10, 40))
        
        # Draw rule parameters
        rules_text = font_small.render(f"Rules: B{self.birth_rule}/S{self.survival_min}-{self.survival_max}", True, PURPLE)
        screen.blit(rules_text, (10, 70))
        
        # Draw generation count
        gen_text = font_medium.render(f"Generation: {self.generation}", True, CYAN)
        screen.blit(gen_text, (10, 100))
        
        # Draw controls
        controls_y = SCREEN_HEIGHT - 150
        controls = [
            "Controls:",
            "Space - Pause/Resume",
            "R - Randomize",
            "C - Clear",
            "+/- - Speed",
            "Click - Toggle Cell",
            "Buttons below for patterns"
        ]
        
        for i, text in enumerate(controls):
            ctrl_text = font_small.render(text, True, CYAN)
            screen.blit(ctrl_text, (10, controls_y + i * 20))
            
    def draw_scanline_overlay(self):
        """Draw scanline overlay for CRT effect"""
        if self.scanline_overlay:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 50))  # Semi-transparent black
            screen.blit(overlay, (0, 0))
            
    def draw_buttons(self):
        """Draw preset pattern buttons"""
        button_height = 30
        button_width = 120
        button_spacing = 10
        start_x = SCREEN_WIDTH - button_width - 10
        start_y = 10
        
        # Glider button
        pygame.draw.rect(screen, PURPLE, (start_x, start_y, button_width, button_height))
        glider_text = font_small.render("Glider", True, (255, 255, 255))
        screen.blit(glider_text, (start_x + 10, start_y + 5))
        
        # Pulsar button
        pygame.draw.rect(screen, MAGENTA, (start_x, start_y + button_height + button_spacing, button_width, button_height))
        pulsar_text = font_small.render("Pulsar", True, (255, 255, 255))
        screen.blit(pulsar_text, (start_x + 10, start_y + button_height + button_spacing + 5))
        
    def load_glider_pattern(self):
        """Load a glider pattern"""
        self.clear_grid()
        # Glider pattern
        glider = [(1, 0), (2, 1), (0, 2), (1, 2), (2, 2)]
        for x, y in glider:
            if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
                self.grid[y][x] = 1
        self.update_population()
        
    def load_pulsar_pattern(self):
        """Load a pulsar pattern"""
        self.clear_grid()
        # Pulsar pattern (centered)
        pulsar = [
            (3, 1), (4, 1), (5, 1), (9, 1), (10, 1), (11, 1),
            (1, 3), (6, 3), (8, 3), (13, 3),
            (1, 4), (6, 4), (8, 4), (13, 4),
            (1, 5), (6, 5), (8, 5), (13, 5),
            (3, 6), (4, 6), (5, 6), (9, 6), (10, 6), (11, 6),
            (3, 8), (4, 8), (5, 8), (9, 8), (10, 8), (11, 8),
            (1, 9), (6, 9), (8, 9), (13, 9),
            (1, 10), (6, 10), (8, 10), (13, 10),
            (1, 11), (6, 11), (8, 11), (13, 11),
            (3, 12), (4, 12), (5, 12), (9, 12), (10, 12), (11, 12)
        ]
        for x, y in pulsar:
            if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
                self.grid[y][x] = 1
        self.update_population()

# Create game instance
game = GameOfLife()

# Main game loop
running = True
while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game.running = not game.running
            elif event.key == pygame.K_r:
                game.randomize_grid()
            elif event.key == pygame.K_c:
                game.clear_grid()
            elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                game.fps = min(60, game.fps + 5)
            elif event.key == pygame.K_MINUS:
                game.fps = max(1, game.fps - 5)
                
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Left mouse button
                x, y = event.pos
                grid_x = x // game.cell_size
                grid_y = y // game.cell_size
                
                # Check if click is on buttons
                button_width = 120
                button_height = 30
                button_y1 = 10
                button_y2 = button_y1 + button_height + 10
                
                if (SCREEN_WIDTH - button_width - 10 <= x <= SCREEN_WIDTH - 10 and 
                    button_y1 <= y <= button_y1 + button_height):
                    # Glider button clicked
                    game.load_glider_pattern()
                elif (SCREEN_WIDTH - button_width - 10 <= x <= SCREEN_WIDTH - 10 and 
                      button_y2 <= y <= button_y2 + button_height):
                    # Pulsar button clicked
                    game.load_pulsar_pattern()
                else:
                    # Toggle cell state
                    game.toggle_cell(grid_x, grid_y)
    
    # Update game state
    if game.running:
        game.update()
        
    # Draw everything
    screen.fill(BACKGROUND)
    game.draw_grid()
    game.draw_ui()
    game.draw_buttons()
    game.draw_scanline_overlay()
    
    # Update frame counter
    game.frame_counter += 1
    
    pygame.display.flip()
    clock.tick(game.fps)

pygame.quit()
sys.exit()
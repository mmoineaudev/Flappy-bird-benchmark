#!/usr/bin/env python3
"""
Conway's Game of Life - Retro Neon Edition
Interactive single-file simulation with user-configurable rules and neon visuals.
"""

import pygame
import random
from datetime import datetime

# Color palette (retro neon theme)
COLOR_BG = (10, 10, 15)  # Dark background
COLOR_GRID = (30, 30, 40)  # Subtle grid lines
COLOR_CYAN = (0, 255, 255)
COLOR_MAGENTA = (255, 0, 255)
COLOR_PURPLE = (157, 78, 221)
COLOR_WHITE = (255, 255, 255)

# Default parameters
GRID_WIDTH = 80
GRID_HEIGHT = 40
CELL_SIZE = 15
FPS = 10

# Conway's Game of Life rules (B/S notation)
# B = birth, S = survival - numbers are neighbor counts
DEFAULT_BIRTH_RULE = 3
DEFAULT_SURVIVAL_RULES = (2, 3)

class GameOfLife:
    def __init__(self):
        """Initialize the Game of Life simulation."""
        # Initialize grid
        self.width = GRID_WIDTH
        self.height = GRID_HEIGHT
        self.cell_size = CELL_SIZE
        
        # Current and next generation grids
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.next_grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        # Game state
        self.generation = 0
        self.population = 0
        self.running = True
        
        # Rules
        self.birth_rule = DEFAULT_BIRTH_RULE
        self.survival_rules = DEFAULT_SURVIVAL_RULES
        
        # Animation speed
        self.fps = FPS
        
        # Initialize with random pattern
        self.randomize()
    
    def count_neighbors(self, x, y):
        """Count live neighbors for cell at position (x, y)."""
        count = 0
        for dx in [-1, 0, 1]:
            for dy in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    count += self.grid[ny][nx]
        return count
    
    def update(self):
        """Apply Conway's Game of Life rules to advance one generation."""
        self.next_grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        
        for y in range(self.height):
            for x in range(self.width):
                neighbors = self.count_neighbors(x, y)
                alive = self.grid[y][x]
                
                if alive:
                    # Survival rule: cell survives if neighbor count is in survival rules
                    if neighbors in self.survival_rules:
                        self.next_grid[y][x] = 1
                    else:
                        # Underpopulation or overcrowding - cell dies
                        pass
                else:
                    # Birth rule: cell is born if neighbor count matches birth rule
                    if neighbors == self.birth_rule:
                        self.next_grid[y][x] = 1
        
        # Swap grids
        self.grid = self.next_grid
        
        # Update statistics
        self.generation += 1
        self.population = sum(sum(row) for row in self.grid)
    
    def randomize(self):
        """Randomize the grid with a pattern."""
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = 1 if random.random() < 0.3 else 0
        self.generation = 0
    
    def clear(self):
        """Clear the grid."""
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.next_grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.generation = 0
        self.population = 0
    
    def toggle_cell(self, x, y):
        """Toggle cell state at given position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = 1 - self.grid[y][x]
    
    def set_preset_pattern(self, pattern_name):
        """Load a classic Game of Life pattern."""
        self.clear()
        
        # Glider preset
        if pattern_name == "glider":
            glider = [
                [0, 1, 0],
                [0, 0, 1],
                [1, 1, 1]
            ]
            center_x = self.width // 2
            center_y = self.height // 2
            for dy, row in enumerate(glider):
                for dx, val in enumerate(row):
                    if val == 1:
                        self.grid[center_y + dy][center_x + dx] = 1
        
        # Pulsar preset
        elif pattern_name == "pulsar":
            # Simple pulsar-like pattern
            pulsar = [
                [0, 1, 1, 1, 0, 1, 1, 1, 0],
                [1, 0, 0, 0, 1, 0, 0, 0, 1],
                [1, 0, 0, 0, 1, 0, 0, 0, 1],
                [1, 0, 0, 0, 1, 0, 0, 0, 1],
                [0, 1, 1, 1, 0, 1, 1, 1, 0]
            ]
            center_x = self.width // 2
            center_y = self.height // 2
            for dy, row in enumerate(pulsar):
                for dx, val in enumerate(row):
                    if val == 1:
                        self.grid[center_y + dy][center_x + dx] = 1
        else:
            # Default to random if pattern not found
            self.randomize()


class Button:
    """Simple button class for UI interaction."""
    def __init__(self, x, y, width, height, text, callback, color=COLOR_PURPLE):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.callback = callback
        self.color = color
        self.hover_color = [min(c + 30, 255) for c in color]
    
    def draw(self, surface, font):
        """Draw the button."""
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.color
        
        pygame.draw.rect(surface, color, self.rect, border_radius=5)
        pygame.draw.rect(surface, COLOR_WHITE, self.rect, 2, border_radius=5)
        
        text_surf = font.render(self.text, True, COLOR_WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)
    
    def handle_event(self, event):
        """Handle button click events."""
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and self.rect.collidepoint(event.pos):
                self.callback()


def draw_scanline_overlay(surface, height):
    """Draw scanline/CRT effect overlay."""
    for y in range(0, height, 2):
        pygame.draw.line(surface, (10, 10, 15), (0, y), (surface.get_width(), y), 1)


def main():
    """Main game loop."""
    # Initialize Pygame
    pygame.init()
    
    # Calculate screen dimensions
    screen_width = GRID_WIDTH * CELL_SIZE + 200  # Extra space for UI
    screen_height = GRID_HEIGHT * CELL_SIZE
    
    # Create window
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Conway's Game of Life - Retro Neon")
    
    # Font setup
    font = pygame.font.SysFont("Courier New", 12, bold=True)
    ui_font = pygame.font.SysFont("Courier New", 10)
    
    # Initialize game
    game = GameOfLife()
    
    # Create UI buttons
    buttons = []
    button_y = GRID_HEIGHT * CELL_SIZE + 20
    
    def set_preset(pattern):
        game.set_preset_pattern(pattern)
    
    buttons.append(Button(20, button_y, 80, 30, "Glider", lambda: set_preset("glider")))
    buttons.append(Button(110, button_y, 80, 30, "Pulsar", lambda: set_preset("pulsar")))
    buttons.append(Button(200, button_y, 80, 30, "Random", game.randomize))
    buttons.append(Button(290, button_y, 80, 30, "Clear", game.clear))
    
    clock = pygame.time.Clock()
    
    running = True
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Keyboard controls
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game.running = not game.running
                elif event.key == pygame.K_r:
                    game.randomize()
                elif event.key == pygame.K_c:
                    game.clear()
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    game.fps = min(game.fps + 2, 30)
                elif event.key == pygame.K_MINUS:
                    game.fps = max(game.fps - 2, 2)
            
            # Mouse controls
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    # Check if clicking on buttons
                    button_clicked = False
                    for btn in buttons:
                        if btn.rect.collidepoint(event.pos):
                            btn.handle_event(event)
                            button_clicked = True
                            break
                    
                    # If not clicking buttons, toggle cell
                    if not button_clicked:
                        grid_x = event.pos[0] // CELL_SIZE
                        grid_y = event.pos[1] // CELL_SIZE
                        game.toggle_cell(grid_x, grid_y)
        
        # Update game state
        if game.running:
            game.update()
        
        # Drawing
        screen.fill(COLOR_BG)
        
        # Draw grid
        for y in range(game.height):
            for x in range(game.width):
                cell = game.grid[y][x]
                color = COLOR_CYAN
                if cell == 1:
                    # Add glow effect with alternating colors
                    color_idx = (x + y) % 3
                    if color_idx == 0:
                        color = COLOR_CYAN
                    elif color_idx == 1:
                        color = COLOR_MAGENTA
                    else:
                        color = COLOR_PURPLE
                    
                    rect = pygame.Rect(
                        x * game.cell_size,
                        y * game.cell_size,
                        game.cell_size - 1,
                        game.cell_size - 1
                    )
                    pygame.draw.rect(screen, color, rect)
        
        # Draw grid lines
        for x in range(0, screen_width, game.cell_size):
            pygame.draw.line(screen, COLOR_GRID, (x, 0), (x, screen_height))
        for y in range(0, screen_height, game.cell_size):
            pygame.draw.line(screen, COLOR_GRID, (0, y), (screen_width, y))
        
        # Draw scanline overlay
        draw_scanline_overlay(screen, screen_height)
        
        # Draw UI panel
        ui_x = GRID_WIDTH * CELL_SIZE + 10
        
        # Title
        title_surf = font.render("Game of Life", True, COLOR_WHITE)
        screen.blit(title_surf, (ui_x, 10))
        
        # Generation counter
        gen_surf = ui_font.render(f"Generation: {game.generation}", True, COLOR_CYAN)
        screen.blit(gen_surf, (ui_x, 35))
        
        # Population
        pop_surf = ui_font.render(f"Population: {game.population}", True, COLOR_MAGENTA)
        screen.blit(pop_surf, (ui_x, 50))
        
        # Rules
        rule_text = f"B/{game.birth_rule}/S{tuple(game.survival_rules)}"
        rule_surf = ui_font.render(f"Rules: {rule_text}", True, COLOR_PURPLE)
        screen.blit(rule_surf, (ui_x, 65))
        
        # Speed
        speed_surf = ui_font.render(f"Speed: {game.fps} FPS", True, COLOR_WHITE)
        screen.blit(speed_surf, (ui_x, 80))
        
        # Controls
        controls = [
            "Controls:",
            "Space: Pause/Resume",
            "R: Randomize",
            "C: Clear",
            "+/-: Speed",
            "Click: Toggle cell"
        ]
        
        for i, line in enumerate(controls):
            control_surf = ui_font.render(line, True, (150, 150, 150))
            screen.blit(control_surf, (ui_x, 110 + i * 15))
        
        # Draw buttons
        for btn in buttons:
            btn.draw(screen, font)
        
        pygame.display.flip()
        clock.tick(game.fps)
    
    pygame.quit()


if __name__ == "__main__":
    main()
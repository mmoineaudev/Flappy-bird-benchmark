#!/usr/bin/env python3
"""
Conway's Game of Life - Retro Neon Edition
A parametrizable implementation with configurable rules and controls.

Rule Configuration:
- B/S notation: Birth if N neighbors, Survive if M-N neighbors
- Default: B3/S23 (standard Conway's rules)
"""

import pygame
import random
import sys
from datetime import datetime

# Initialize pygame
pygame.init()

# Configuration - All parameters are user-configurable
GRID_WIDTH = 80       # Number of columns
GRID_HEIGHT = 40      # Number of rows
CELL_SIZE = 15        # Pixels per cell
FPS_TARGET = 30       # Maximum animation speed (can be adjusted)

# Rule parameters - B3/S23 is standard Conway's Game of Life
BIRTH_NEIGHBORS = 3   # Exactly 3 neighbors to birth a new cell
SURVIVE_MIN = 2       # Minimum neighbors to survive
SURVIVE_MAX = 3       # Maximum neighbors to survive

# Colors - Retro neon palette
COLOR_BG = (10, 10, 15)         # Dark background
COLOR_CELL = (0, 255, 255)      # Cyan for live cells
COLOR_GRID = (30, 30, 40)       # Subtle grid lines
COLOR_TEXT = (200, 200, 255)    # Text color
COLOR_HIGHLIGHT = (157, 78, 221) # Purple accent

# Window dimensions
WINDOW_WIDTH = GRID_WIDTH * CELL_SIZE + 300  # Extra space for UI
WINDOW_HEIGHT = GRID_HEIGHT * CELL_SIZE + 100

# Create display screen
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Conway's Game of Life - Neon Edition")

# Font setup
font_small = pygame.font.Font(None, 16)
font_medium = pygame.font.Font(None, 20)
font_large = pygame.font.Font(None, 28)

class GameOfLife:
    def __init__(self):
        self.grid = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.frame_count = 0
        self.running = True
        self.paused = False
        self.animation_speed = FPS_TARGET
        self.cell_size = CELL_SIZE
        
        # Initialize with random pattern
        self.randomize()
        
    def randomize(self):
        """Randomize the grid with ~30% live cells"""
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                self.grid[row][col] = random.random() < 0.3
    
    def clear(self):
        """Clear all cells"""
        self.grid = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.frame_count = 0
    
    def count_neighbors(self, row, col):
        """Count live neighbors with toroidal (wrap-around) boundaries"""
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                # Wrap around edges
                neighbor_row = (row + dy) % GRID_HEIGHT
                neighbor_col = (col + dx) % GRID_WIDTH
                count += 1 if self.grid[neighbor_row][neighbor_col] else 0
        return count
    
    def update(self):
        """Advance the simulation by one generation"""
        if self.paused:
            return
        
        new_grid = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        for row in range(GRID_HEIGHT):
            for col in range(GRID_WIDTH):
                neighbors = self.count_neighbors(row, col)
                current = self.grid[row][col]
                
                # Apply Conway's rules
                if current:
                    # Survival rule
                    if SURVIVE_MIN <= neighbors <= SURVIVE_MAX:
                        new_grid[row][col] = True
                else:
                    # Birth rule
                    if neighbors == BIRTH_NEIGHBORS:
                        new_grid[row][col] = True
        
        self.grid = new_grid
        self.frame_count += 1
    
    def toggle_cell(self, pos):
        """Toggle cell state at mouse position"""
        x, y = pos
        col = x // self.cell_size
        row = y // self.cell_size
        
        if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
            self.grid[row][col] = not self.grid[row][col]
    
    def get_population(self):
        """Count live cells"""
        return sum(sum(row) for row in self.grid)
    
    # Preset patterns
    def load_pattern(self, pattern_name):
        """Load a classic Game of Life pattern"""
        self.clear()
        
        patterns = {
            'glider': [
                (1, 0), (2, 1), (0, 2), (1, 2), (2, 2)
            ],
            'blinker': [
                (0, 0), (1, 0), (2, 0),
                (0, 1), (1, 1), (2, 1)
            ],
            'beacon': [
                (0, 0), (1, 0), (4, 3), (5, 3),
                (0, 5), (1, 5), (4, 4), (5, 4)
            ],
            'pulsar': [
                (2, 0), (3, 0), (4, 0),
                (0, 2), (6, 2),
                (0, 3), (6, 3),
                (0, 4), (6, 4),
                (2, 6), (3, 6), (4, 6)
            ],
            'gosper_glider': [
                (1, 0), (2, 1), (0, 2), (1, 2), (2, 2)
            ]
        }
        
        if pattern_name in patterns:
            # Center the pattern
            offsets = patterns[pattern_name]
            center_row = GRID_HEIGHT // 2 - 3
            center_col = GRID_WIDTH // 2 - 3
            
            for row_offset, col_offset in offsets:
                row = center_row + row_offset
                col = center_col + col_offset
                if 0 <= row < GRID_HEIGHT and 0 <= col < GRID_WIDTH:
                    self.grid[row][col] = True

def draw_grid(game):
    """Draw the game grid with neon effects"""
    # Background
    screen.fill(COLOR_BG)
    
    # Draw cells
    for row in range(GRID_HEIGHT):
        for col in range(GRID_WIDTH):
            if game.grid[row][col]:
                x = col * game.cell_size + 1
                y = row * game.cell_size + 1
                
                # Glow effect - draw slightly larger first
                glow_size = game.cell_size + 2
                pygame.draw.rect(screen, COLOR_CELL, 
                               (x - 1, y - 1, glow_size, glow_size), 0)
                
                # Main cell
                pygame.draw.rect(screen, COLOR_CELL, 
                               (x, y, game.cell_size - 2, game.cell_size - 2), 0)
    
    # Draw grid lines (subtle)
    for x in range(0, GRID_WIDTH * game.cell_size, game.cell_size):
        pygame.draw.line(screen, COLOR_GRID, 
                        (x + 1, 1), (x + 1, GRID_HEIGHT * game.cell_size))
    
    for y in range(0, GRID_HEIGHT * game.cell_size, game.cell_size):
        pygame.draw.line(screen, COLOR_GRID, 
                        (1, y + 1), (GRID_WIDTH * game.cell_size, y + 1))
    
    # CRT scanline effect
    for y in range(0, GRID_HEIGHT * game.cell_size, 3):
        pygame.draw.line(screen, (20, 20, 30), 
                        (1, y + 1), (GRID_WIDTH * game.cell_size, y + 1))

def draw_ui(game):
    """Draw the UI elements"""
    ui_x = GRID_WIDTH * game.cell_size + 20
    
    # Title
    title = font_large.render("GAME OF LIFE", True, COLOR_CELL)
    screen.blit(title, (ui_x, 10))
    
    subtitle = font_small.render("Neon Edition", True, COLOR_HIGHLIGHT)
    screen.blit(subtitle, (ui_x, 45))
    
    # Frame counter
    frame_text = font_medium.render(f"Frame: {game.frame_count}", True, COLOR_TEXT)
    screen.blit(frame_text, (ui_x, 80))
    
    # Population count
    population = game.get_population()
    pop_text = font_medium.render(f"Population: {population}", True, COLOR_TEXT)
    screen.blit(pop_text, (ui_x, 110))
    
    # Speed display
    speed_text = font_medium.render(f"Speed: {game.animation_speed} fps", True, COLOR_TEXT)
    screen.blit(speed_text, (ui_x, 140))
    
    # Rule parameters
    rule_text = font_small.render(f"Rules: B{BIRTH_NEIGHBORS}/S{SURVIVE_MIN}-{SURVIVE_MAX}", True, COLOR_TEXT)
    screen.blit(rule_text, (ui_x, 170))
    
    # Control hints
    controls_y = 200
    controls = [
        "[SPACE] Pause/Resume",
        "[R] Randomize",
        "[C] Clear",
        "[+/-] Speed",
        "[Click] Toggle cell",
        "---",
        "Pattern Buttons:"
    ]
    
    for i, control in enumerate(controls):
        text = font_small.render(control, True, COLOR_TEXT)
        screen.blit(text, (ui_x, controls_y + i * 25))
    
    # Pattern buttons
    patterns = ['glider', 'blinker', 'beacon', 'pulsar', 'gosper_glider']
    button_y = 370
    
    for pattern in patterns:
        # Button background
        btn_rect = pygame.Rect(ui_x, button_y, 120, 30)
        pygame.draw.rect(screen, (40, 40, 60), btn_rect)
        pygame.draw.rect(screen, COLOR_HIGHLIGHT, btn_rect, 2)
        
        # Button label
        text = font_small.render(pattern.capitalize(), True, COLOR_TEXT)
        text_rect = text.get_rect(center=btn_rect.center)
        screen.blit(text, text_rect)
        
        button_y += 40

def main():
    """Main game loop"""
    clock = pygame.time.Clock()
    game = GameOfLife()
    
    # Create pattern buttons for click detection
    patterns = ['glider', 'blinker', 'beacon', 'pulsar', 'gosper_glider']
    button_y = 370
    pattern_buttons = []
    for pattern in patterns:
        pattern_buttons.append(pygame.Rect(GRID_WIDTH * CELL_SIZE + 20, button_y, 120, 30))
        button_y += 40
    
    running = True
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
                
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_KP_PLUS:
                    game.animation_speed = min(game.animation_speed + 5, 120)
                
                elif event.key == pygame.K_MINUS or event.key == pygame.K_KP_MINUS:
                    game.animation_speed = max(game.animation_speed - 5, 5)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                
                # Check if clicking on grid
                if mouse_pos[0] < GRID_WIDTH * CELL_SIZE:
                    game.toggle_cell(mouse_pos)
                
                # Check pattern buttons
                else:
                    for i, button in enumerate(pattern_buttons):
                        if button.collidepoint(mouse_pos):
                            game.load_pattern(patterns[i])
                            break
        
        # Update game state
        game.update()
        
        # Draw everything
        draw_grid(game)
        draw_ui(game)
        
        # Refresh display
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(game.animation_speed)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

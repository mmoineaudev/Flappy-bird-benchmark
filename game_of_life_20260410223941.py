#!/usr/bin/env python3
"""
Conway's Game of Life - Neon Retro Edition
Python/Pygame implementation with CRT effects and neon aesthetics.
"""

import pygame
import random
import sys
from enum import Enum

# ============================================================================
# Rule Configuration
# ============================================================================
# Conway's standard rules: B3/S23 (Birth with 3 neighbors, Survival with 2-3)
# Parametrizable for experimentation with different rule sets
RULES = {
    'birth': 3,              # Number of live neighbors needed to spawn a new cell
    'survival_min': 2,       # Minimum live neighbors for survival
    'survival_max': 3,       # Maximum live neighbors for survival
}

# Visual configuration
GRID_WIDTH = 80
GRID_HEIGHT = 40
CELL_SIZE = 15
FPS = 60

# Color palette - Neon wave theme with retro CRT feel
COLORS = {
    'background': (10, 10, 15),          # Dark background #0a0a0f
    'alive_cyan': (0, 255, 255),         # Cyan #00ffff
    'alive_magenta': (255, 0, 255),      # Magenta #ff00ff
    'alive_purple': (157, 78, 237),      # Purple #9d4edd
    'grid_line': (30, 30, 40),           # Subtle grid lines
    'text': (200, 200, 220),             # Text color
    'scanline': (255, 255, 255, 30),     # Scanline overlay with alpha
}

# ============================================================================
# Game of Life Engine
# ============================================================================
class GameOfLife:
    """Core Game of Life simulation engine."""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[False for _ in range(width)] for _ in range(height)]
        self.frame = 0
        
    def randomize(self):
        """Randomize grid with ~30% live cells."""
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = random.random() < 0.3
    
    def clear(self):
        """Clear all cells."""
        self.grid = [[False for _ in range(self.width)] for _ in range(self.height)]
    
    def count_neighbors(self, x, y):
        """Count live neighbors with toroidal (wrap-around) boundary."""
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
    
    def step(self):
        """Advance simulation by one generation."""
        new_grid = [[False for _ in range(self.width)] for _ in range(self.height)]
        
        for y in range(self.height):
            for x in range(self.width):
                neighbors = self.count_neighbors(x, y)
                current = self.grid[y][x]
                
                # Apply rules: Birth or Survival
                if current and RULES['survival_min'] <= neighbors <= RULES['survival_max']:
                    new_grid[y][x] = True  # Survive
                elif not current and neighbors == RULES['birth']:
                    new_grid[y][x] = True  # Birth
                
                self.grid = new_grid
                self.frame += 1
    
    def get_population(self):
        """Count live cells."""
        return sum(sum(row) for row in self.grid)
    
    def toggle_cell(self, x, y):
        """Toggle cell state at position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = not self.grid[y][x]


# ============================================================================
# Visual Effects
# ============================================================================
class CRTEffect:
    """Retro CRT scanline and glow effects."""
    
    def __init__(self, screen, width, height):
        self.screen = screen
        self.width = width
        self.height = height
        self.scanline_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
    def draw_scanlines(self):
        """Draw subtle horizontal scanline effect."""
        self.scanline_surface.fill((0, 0, 0, 0))
        for y in range(0, self.height, 3):
            pygame.draw.line(self.scanline_surface, (255, 255, 255, 20), 
                           (0, y), (self.width, y))
        return self.scanline_surface
    
    def draw_glow(self, surface):
        """Add subtle glow effect to alive cells."""
        # Create a blurred version for glow
        glow_surface = pygame.Surface((surface.get_width(), surface.get_height()), 
                                     pygame.SRCALPHA)
        glow_surface.fill((0, 0, 0, 0))
        
        # Draw larger semi-transparent shapes behind cells
        for y in range(0, self.height, CELL_SIZE):
            for x in range(0, self.width, CELL_SIZE):
                if random.random() < 0.1:  # Random glow flicker
                    color = random.choice([COLORS['alive_cyan'], 
                                         COLORS['alive_magenta'], 
                                         COLORS['alive_purple']])
                    glow_rect = pygame.Rect(x - 2, y - 2, CELL_SIZE + 4, CELL_SIZE + 4)
                    pygame.draw.rect(glow_surface, (*color[:3], 50), glow_rect)
        
        return glow_surface


# ============================================================================
# UI Elements
# ============================================================================
class UIOverlay:
    """On-screen UI for stats and controls."""
    
    def __init__(self):
        pygame.font.init()
        self.font_small = pygame.font.Font(None, 16)
        self.font_medium = pygame.font.Font(None, 24)
        self.font_large = pygame.font.Font(None, 32)
        
    def draw(self, screen, game, speed):
        """Draw all UI elements."""
        # Frame counter
        frame_text = self.font_large.render(f"Frame: {game.frame}", True, 
                                           COLORS['text'])
        screen.blit(frame_text, (10, 10))
        
        # Population count
        pop_text = self.font_medium.render(f"Population: {game.get_population()}", 
                                          True, COLORS['alive_cyan'])
        screen.blit(pop_text, (10, 50))
        
        # Rule parameters
        rule_text = self.font_small.render(
            f"Rules: B{RULES['birth']}/S{RULES['survival_min']}-{RULES['survival_max']}",
            True, COLORS['alive_magenta'])
        screen.blit(rule_text, (10, 85))
        
        # Speed display
        speed_text = self.font_small.render(f"Speed: {speed:.1f} FPS", 
                                           True, COLORS['alive_purple'])
        screen.blit(speed_text, (10, 110))
        
        # Control hints
        controls = [
            "Controls:",
            "Space: Pause/Resume",
            "R: Randomize",
            "C: Clear",
            "+/-: Speed",
            "Click: Toggle cell"
        ]
        for i, control in enumerate(controls):
            text = self.font_small.render(control, True, (150, 150, 170))
            screen.blit(text, (GRID_WIDTH * CELL_SIZE + 20, 10 + i * 25))


# ============================================================================
# Main Game
# ============================================================================
class GameOfLifeApp:
    """Main application class."""
    
    def __init__(self):
        pygame.init()
        
        # Calculate screen size
        self.screen_width = GRID_WIDTH * CELL_SIZE
        self.screen_height = GRID_HEIGHT * CELL_SIZE
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Game of Life - Neon Retro Edition")
        
        # Initialize components
        self.game = GameOfLife(GRID_WIDTH, GRID_HEIGHT)
        self.crt = CRTEffect(self.screen, self.screen_width, self.screen_height)
        self.ui = UIOverlay()
        
        # Random initial pattern
        self.game.randomize()
        
        # State
        self.paused = False
        self.speed = FPS
        self.clock = pygame.time.Clock()
        self.running = True
        
    def handle_events(self):
        """Process input events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                
                elif event.key == pygame.K_r:
                    self.game.randomize()
                
                elif event.key == pygame.K_c:
                    self.game.clear()
                
                elif event.key == pygame.K_EQUALS or event.key == pygame.K_PLUS:
                    self.speed = min(self.speed + 1, FPS)
                
                elif event.key == pygame.K_MINUS:
                    self.speed = max(self.speed - 1, 1)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    x = event.pos[0] // CELL_SIZE
                    y = event.pos[1] // CELL_SIZE
                    self.game.toggle_cell(x, y)
    
    def update(self):
        """Update game state."""
        if not self.paused:
            # Update at target FPS
            delay = 1.0 / self.speed
            pygame.time.wait(int(delay * 1000))
            self.game.step()
    
    def draw(self):
        """Render everything."""
        # Clear background
        self.screen.fill(COLORS['background'])
        
        # Draw grid lines (subtle)
        for x in range(0, GRID_WIDTH * CELL_SIZE, CELL_SIZE):
            pygame.draw.line(self.screen, COLORS['grid_line'], 
                           (x, 0), (x, GRID_HEIGHT * CELL_SIZE))
        for y in range(0, GRID_HEIGHT * CELL_SIZE, CELL_SIZE):
            pygame.draw.line(self.screen, COLORS['grid_line'], 
                           (0, y), (GRID_WIDTH * CELL_SIZE, y))
        
        # Draw alive cells with color cycling
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.game.grid[y][x]:
                    # Cycle colors based on position and time
                    hue_index = (x + y + self.game.frame // 10) % 3
                    color = [COLORS['alive_cyan'], 
                            COLORS['alive_magenta'], 
                            COLORS['alive_purple']][hue_index]
                    
                    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, 
                                      CELL_SIZE - 1, CELL_SIZE - 1)
                    pygame.draw.rect(self.screen, color, rect)
        
        # Draw scanline effect
        scanlines = self.crt.draw_scanlines()
        self.screen.blit(scanlines, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
        
        # Draw UI overlay
        self.ui.draw(self.screen, self.game, self.speed)
        
        # Pause indicator
        if self.paused:
            pause_text = self.font_large.render("PAUSED", True, COLORS['alive_magenta'])
            rect = pause_text.get_rect(center=(GRID_WIDTH * CELL_SIZE // 2, 
                                               GRID_HEIGHT * CELL_SIZE // 2))
            self.screen.blit(pause_text, rect)
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(60)  # Cap at 60 FPS
        
        pygame.quit()
        sys.exit()


# ============================================================================
# Entry Point
# ============================================================================
if __name__ == "__main__":
    try:
        app = GameOfLifeApp()
        app.run()
    except Exception as e:
        print(f"Error: {e}")
        pygame.quit()
        sys.exit(1)

#!/usr/bin/env python3
"""
Conway's Game of Life - Retro Neon Implementation with Pygame

Features:
- Parametrizable game rules (birth/survival rules)
- Retro aesthetic: dark background, neon cells, scanlines, CRT effects
- Interactive controls with keyboard and mouse
- Real-time statistics and rule display
"""

import pygame
import sys
from datetime import datetime

# ============================================================================
# CONFIGURATION
# ============================================================================

# Grid settings
GRID_WIDTH = 80
GRID_HEIGHT = 40
CELL_SIZE = 15
PADDING = 20

# Color palette (neron wave theme)
COLOR_BG = (10, 10, 15)        # Dark background
COLOR_GRID = (30, 30, 40)      # Subtle grid lines
COLOR_CELL_CYAN = (0, 255, 255)     # Cyan neon
COLOR_CELL_MAGENTA = (255, 0, 255)  # Magenta neon
COLOR_CELL_PURPLE = (157, 78, 222)  # Purple neon
COLOR_TEXT = (200, 200, 220)   # Text color

# Neon glow effect settings
GLOW_RADIUS = 15
GLOW_OPACITY = 100

# Retro effect settings
ENABLE_SCANLINES = True
SCANLINE_HEIGHT = 2
SCANLINE_OPACITY = 30

# Game rules (parametrizable)
DEFAULT_BIRTH_RULE = 3          # Number of neighbors to spawn new cell
DEFAULT_SURVIVE_MIN = 2         # Minimum neighbors to survive
DEFAULT_SURVIVE_MAX = 3         # Maximum neighbors to survive

# Animation settings
DEFAULT_FPS = 10


class GameOfLife:
    """Main Game of Life simulation class."""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.grid = [[0 for _ in range(width)] for _ in range(height)]
        self.next_grid = [[0 for _ in range(width)] for _ in range(height)]
        
        # Rule configuration
        self.birth_rule = DEFAULT_BIRTH_RULE
        self.survive_min = DEFAULT_SURVIVE_MIN
        self.survive_max = DEFAULT_SURVIVE_MAX
        
        # Game state
        self.paused = False
        self.frame_count = 0
        self.population = 0
        
        # Timing
        self.last_update = datetime.now()
        self.fps = DEFAULT_FPS
        
        # Color cycling
        self.color_cycle = 0
        self.color_options = [COLOR_CELL_CYAN, COLOR_CELL_MAGENTA, COLOR_CELL_PURPLE]
    
    def randomize(self):
        """Fill grid with random cells."""
        import random
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = 1 if random.random() < 0.2 else 0
        self.update_population()
    
    def clear(self):
        """Clear the grid (all dead cells)."""
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = 0
        self.population = 0
    
    def update_population(self):
        """Count live cells."""
        self.population = sum(sum(row) for row in self.grid)
    
    def get_neighbors(self, x, y):
        """Count live neighbors for a cell (toroidal wrapping)."""
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx = (x + dx) % self.width
                ny = (y + dy) % self.height
                count += self.grid[ny][nx]
        return count
    
    def update(self):
        """Update grid state according to Game of Life rules."""
        if self.paused:
            return
        
        # Apply rules to each cell
        for y in range(self.height):
            for x in range(self.width):
                neighbors = self.get_neighbors(x, y)
                current = self.grid[y][x]
                
                if current == 1:
                    # Survival rule: cell survives if neighbors in [survive_min, survive_max]
                    if self.survive_min <= neighbors <= self.survive_max:
                        self.next_grid[y][x] = 1
                    else:
                        self.next_grid[y][x] = 0
                else:
                    # Birth rule: cell spawns if neighbors == birth_rule
                    if neighbors == self.birth_rule:
                        self.next_grid[y][x] = 1
                    else:
                        self.next_grid[y][x] = 0
        
        # Copy next grid to current grid
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = self.next_grid[y][x]
        
        self.frame_count += 1
        self.update_population()
        
        # Cycle colors for dynamic neon effect
        self.color_cycle = (self.color_cycle + 1) % len(self.color_options)
    
    def toggle_cell(self, mouse_x, mouse_y):
        """Toggle cell state at mouse position."""
        grid_x = (mouse_x - PADDING) // CELL_SIZE
        grid_y = (mouse_y - PADDING) // CELL_SIZE
        
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            self.grid[grid_y][grid_x] = 1 - self.grid[grid_y][grid_x]
            self.update_population()
    
    def set_cell(self, mouse_x, mouse_y, state=1):
        """Set cell state at mouse position (for dragging)."""
        grid_x = (mouse_x - PADDING) // CELL_SIZE
        grid_y = (mouse_y - PADDING) // CELL_SIZE
        
        if 0 <= grid_x < self.width and 0 <= grid_y < self.height:
            self.grid[grid_y][grid_x] = state


class Renderer:
    """Pygame renderer with retro neon effects."""
    
    def __init__(self, game, cell_size):
        self.game = game
        self.cell_size = cell_size
        
        # Calculate window size
        width = game.width * cell_size + 2 * PADDING
        height = game.height * cell_size + 2 * PADDING
        
        pygame.init()
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Game of Life - Retro Neon")
        
        # Create glow surface
        self.glow_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        
        # Font for UI
        pygame.font.init()
        self.font = pygame.font.Font(None, 20)
        self.small_font = pygame.font.Font(None, 16)
    
    def draw_grid_lines(self):
        """Draw subtle grid lines."""
        color = COLOR_GRID
        width = self.game.width * self.cell_size + 2 * PADDING
        height = self.game.height * self.cell_size + 2 * PADDING
        
        # Vertical lines
        for x in range(self.game.width + 1):
            px = PADDING + x * self.cell_size
            pygame.draw.line(self.screen, color, 
                           (px, PADDING), 
                           (px, height - PADDING), 1)
        
        # Horizontal lines
        for y in range(self.game.height + 1):
            py = PADDING + y * self.cell_size
            pygame.draw.line(self.screen, color,
                           (PADDING, py),
                           (width - PADDING, py), 1)
    
    def draw_cells(self):
        """Draw live cells with neon glow effect."""
        current_color = self.game.color_options[self.game.color_cycle]
        
        for y in range(self.game.height):
            for x in range(self.game.width):
                if self.game.grid[y][x] == 1:
                    px = PADDING + x * self.cell_size
                    py = PADDING + y * self.cell_size
                    
                    # Draw cell with glow effect
                    glow_rect = pygame.Rect(px - 2, py - 2, 
                                          self.cell_size + 4, 
                                          self.cell_size + 4)
                    
                    # Outer glow ring
                    glow_color = (current_color[0] // 3, 
                                current_color[1] // 3, 
                                current_color[2] // 3,
                                GLOW_OPACITY)
                    glow_surf = pygame.Surface((glow_rect.width, glow_rect.height), pygame.SRCALPHA)
                    pygame.draw.ellipse(glow_surf, glow_color, 
                                      glow_surf.get_rect(), 3)
                    self.screen.blit(glow_surf, (glow_rect.x, glow_rect.y))
                    
                    # Inner bright cell
                    cell_rect = pygame.Rect(px, py, self.cell_size, self.cell_size)
                    pygame.draw.rect(self.screen, current_color, cell_rect)
                    
                    # Cell border
                    pygame.draw.rect(self.screen, (255, 255, 255), cell_rect, 1)
    
    def draw_scanlines(self):
        """Draw retro scanline effect."""
        if not ENABLE_SCANLINES:
            return
        
        width = self.game.width * self.cell_size + 2 * PADDING
        height = self.game.height * self.cell_size + 2 * PADDING
        
        for y in range(0, height, SCANLINE_HEIGHT * 2):
            scanline = pygame.Surface((width, SCANLINE_HEIGHT), pygame.SRCALPHA)
            scanline.fill((0, 0, 0, SCANLINE_OPACITY))
            self.screen.blit(scanline, (0, y))
    
    def draw_ui(self):
        """Draw on-screen UI elements."""
        # Game statistics
        fps_text = self.font.render(f"FPS: {self.game.fps}", True, COLOR_TEXT)
        frame_text = self.font.render(f"Frame: {self.game.frame_count}", True, COLOR_TEXT)
        pop_text = self.font.render(f"Population: {self.game.population}", True, COLOR_TEXT)
        
        # Rule info
        rule_text = self.font.render(f"Rules: B{self.game.birth_rule} S{self.game.survive_min}-{self.game.survive_max}", 
                                   True, COLOR_TEXT)
        
        # Controls hint
        controls = [
            "[Space] Pause/Resume",
            "[R] Randomize",
            "[C] Clear",
            "[+] [-] Speed",
            "[Mouse] Toggle Cell"
        ]
        
        self.screen.blit(fps_text, (10, 10))
        self.screen.blit(frame_text, (10, 35))
        self.screen.blit(pop_text, (10, 60))
        self.screen.blit(rule_text, (10, 85))
        
        # Draw controls in corner
        for i, control in enumerate(controls):
            text = self.small_font.render(control, True, COLOR_TEXT)
            self.screen.blit(text, (10, 120 + i * 20))
        
        # Pause indicator
        if self.game.paused:
            pause_text = self.font.render("PAUSED", True, COLOR_CELL_CYAN)
            text_rect = pause_text.get_rect(center=(self.screen.get_width() // 2, 30))
            self.screen.blit(pause_text, text_rect)
    
    def render(self):
        """Render the complete frame."""
        # Clear screen with background color
        self.screen.fill(COLOR_BG)
        
        # Draw grid lines
        self.draw_grid_lines()
        
        # Draw cells
        self.draw_cells()
        
        # Draw retro effects
        self.draw_scanlines()
        
        # Draw UI
        self.draw_ui()
        
        # Update display
        pygame.display.flip()


def main():
    """Main game loop."""
    # Initialize game
    game = GameOfLife(GRID_WIDTH, GRID_HEIGHT)
    game.randomize()  # Start with random pattern
    
    # Initialize renderer
    renderer = Renderer(game, CELL_SIZE)
    
    # Mouse drag state
    mouse_dragging = False
    
    # Main loop
    clock = pygame.time.Clock()
    running = True
    
    while running:
        # Handle events
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
                    game.fps = min(game.fps + 5, 60)
                elif event.key == pygame.K_MINUS or event.key == pygame.K_DOWN:
                    game.fps = max(game.fps - 5, 1)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_dragging = True
                    game.toggle_cell(event.pos[0], event.pos[1])
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click
                    mouse_dragging = False
            
            elif event.type == pygame.MOUSEMOTION:
                if mouse_dragging:
                    game.set_cell(event.pos[0], event.pos[1], 1)
        
        # Update game logic based on FPS
        now = datetime.now()
        interval = 1.0 / game.fps
        
        if (now - game.last_update).total_seconds() >= interval:
            game.update()
            game.last_update = now
        
        # Render frame
        renderer.render()
        clock.tick(60)  # Cap at 60 FPS for smooth rendering
    
    # Cleanup
    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()

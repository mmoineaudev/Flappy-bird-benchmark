#!/usr/bin/env python3
"""
Conway's Game of Life - Retro Neon Edition
A single-file pygame implementation with customizable rules and retro styling.
"""

import pygame
import random
import sys
from typing import List, Tuple

# ==================== CONFIGURATION ====================
# Grid settings
GRID_WIDTH = 80
GRID_HEIGHT = 40
CELL_SIZE = 15

# Game rules (parametrizable)
BIRTH_RULE = [3]  # Cells born with exactly these neighbor counts
SURVIVAL_RULE = [2, 3]  # Cells survive with these neighbor counts

# Colors (neon retro palette)
BACKGROUND_COLOR = (10, 10, 15)
NEON_CYAN = (0, 255, 255)
NEON_MAGENTA = (255, 0, 255)
NEON_PURPLE = (157, 78, 221)
GRID_COLOR = (30, 30, 40)
TEXT_COLOR = (200, 200, 220)

# Animation
FPS = 30


# ==================== GAME PATTERNS ====================
PATTERNS = {
    "glider": [
        (0, 1), (1, 2), (2, 0), (2, 1), (2, 2)
    ],
    "pulsar": [
        # Pulsar oscillator pattern
        (-6,-4), (-6,-3), (-6,-2), (-6,2), (-6,3), (-6,4),
        (-4,-6), (-4,-1), (-4,1), (-4,6),
        (-3,-6), (-3,-1), (-3,1), (-3,6),
        (-2,-6), (-2,-1), (-2,1), (-2,6),
        (-1,-4), (-1,-3), (-1,-2), (-1,2), (-1,3), (-1,4),
        (1,-4), (1,-3), (1,-2), (1,2), (1,3), (1,4),
        (2,-6), (2,-1), (2,1), (2,6),
        (3,-6), (3,-1), (3,1), (3,6),
        (4,-6), (4,-1), (4,1), (4,6),
        (6,-4), (6,-3), (6,-2), (6,2), (6,3), (6,4)
    ],
    "gosper_glider_gun": [
        # Gosper Glider Gun
        (5, 1), (5, 2), (6, 1), (6, 2),
        (15, 1), (15, 2), (15, 3),
        (13, 4), (17, 4),
        (12, 5), (18, 5),
        (11, 6), (19, 6),
        (10, 7), (20, 7),
        (21, 5), (21, 6), (21, 7),
        (1, 9), (1, 10), (2, 9), (2, 10),
        (11, 8), (11, 9), (11, 10),
        (12, 7), (12, 11),
        (13, 6), (13, 12),
        (14, 5), (14, 13),
        (15, 4), (15, 14),
        (16, 6), (16, 12),
        (17, 7), (17, 11),
        (18, 9), (19, 8), (19, 10)
    ],
    "block": [(0, 0), (0, 1), (1, 0), (1, 1)],
    "beehive": [(1, 0), (2, -1), (0, 1), (3, 1), (0, 2), (3, 2), (1, 3), (2, 3)],
    "loaf": [(1, 0), (2, -1), (0, 1), (3, 1), (0, 2), (3, 2), (1, 3), (2, 3), (1, 4)],
    "boat": [(0, 0), (1, 0), (0, 1), (2, 1), (1, 2)],
    "tub": [(0, 0), (2, 0), (1, 1), (1, 2)],
    "beacon": [(0, 0), (1, 0), (0, 1), (3, 2), (2, 3), (3, 3)],
    "toad": [(1, 0), (2, 0), (3, 0), (0, 1), (1, 1), (2, 1)],
    "lwss": [(1, 0), (4, 0), (0, 1), (0, 2), (0, 3), (4, 3), (1, 4), (2, 4), (3, 4)]
}


# ==================== GAME CLASS ====================
class GameOfLife:
    def __init__(self):
        pygame.init()
        self.screen_width = GRID_WIDTH * CELL_SIZE
        self.screen_height = GRID_HEIGHT * CELL_SIZE
        
        # Create screen with fullscreen option (comment out for windowed)
        # self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        self.screen = pygame.display.set_mode((self.screen_width + 250, self.screen_height))
        pygame.display.set_caption("Conway's Game of Life - Neon Retro Edition")
        
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.big_font = pygame.font.Font(None, 36)
        
        # Initialize grid
        self.grid = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Game state
        self.running = True
        self.paused = False
        self.fps = FPS
        self.frame_count = 0
        
        # Initialize with random pattern
        self.randomize_grid()
        
        # Button setup
        self.buttons = []
        self.create_pattern_buttons()
        
    def create_pattern_buttons(self):
        """Create clickable buttons for preset patterns."""
        button_y = 20
        button_x_start = self.screen_width + 30
        
        pattern_names = ["Glider", "Pulsar", "Gosper Gun", "Block", "Beehive", 
                        "Toad", " LWSS", "Tub", "Boat", "Beacon"]
        
        for i, name in enumerate(pattern_names):
            btn_width = 100
            btn_height = 25
            x = button_x_start + (i % 3) * (btn_width + 10)
            y = button_y + (i // 3) * (btn_height + 10)
            self.buttons.append({
                'name': name,
                'rect': pygame.Rect(x, y, btn_width, btn_height),
                'color': NEON_PURPLE
            })
            
        # Clear button
        clear_btn = {
            'name': 'Clear',
            'rect': pygame.Rect(button_x_start, 150, 80, 25),
            'color': (200, 50, 50)
        }
        self.buttons.append(clear_btn)
        
        # Random button
        random_btn = {
            'name': 'Randomize',
            'rect': pygame.Rect(button_x_start, 180, 100, 25),
            'color': NEON_CYAN
        }
        self.buttons.append(random_btn)
        
    def randomize_grid(self):
        """Fill grid with random cells."""
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                self.grid[y][x] = random.random() < 0.3
                
    def place_pattern(self, pattern_name: str, offset_x: int = 20, offset_y: int = 20):
        """Place a preset pattern on the grid."""
        if pattern_name == "Clear":
            self.grid = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
            return
            
        if pattern_name == "Randomize":
            self.randomize_grid()
            return
            
        pattern = PATTERNS.get(pattern_name.lower().replace(" ", "_"))
        if not pattern:
            return
            
        # Clear grid first
        self.grid = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        # Place pattern with bounds checking
        for dx, dy in pattern:
            px = offset_x + dx
            py = offset_y + dy
            if 0 <= px < GRID_WIDTH and 0 <= py < GRID_HEIGHT:
                self.grid[py][px] = True
                
    def count_neighbors(self, x: int, y: int) -> int:
        """Count live neighbors for a cell (with wrap-around)."""
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx = (x + dx) % GRID_WIDTH
                ny = (y + dy) % GRID_HEIGHT
                if self.grid[ny][nx]:
                    count += 1
        return count
        
    def update(self):
        """Advance the simulation by one generation."""
        if self.paused:
            return
            
        new_grid = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                neighbors = self.count_neighbors(x, y)
                current = self.grid[y][x]
                
                # Apply Game of Life rules
                if current:
                    new_grid[y][x] = neighbors in SURVIVAL_RULE
                else:
                    new_grid[y][x] = neighbors in BIRTH_RULE
                    
        self.grid = new_grid
        self.frame_count += 1
        
    def get_cell_at_pos(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        """Get grid coordinates from screen position."""
        x, y = pos
        if x < 0 or y < 0:
            return -1, -1
        gx = min(x // CELL_SIZE, GRID_WIDTH - 1)
        gy = min(y // CELL_SIZE, GRID_HEIGHT - 1)
        return gx, gy
        
    def draw(self):
        """Render the game to screen."""
        # Clear background
        self.screen.fill(BACKGROUND_COLOR)
        
        # Draw grid cells with neon glow effect
        for y in range(GRID_HEIGHT):
            for x in range(GRID_WIDTH):
                if self.grid[y][x]:
                    # Neon glow by drawing multiple layers
                    glow_color = (0, 200, 200)
                    pygame.draw.rect(self.screen, glow_color, 
                                   (x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                    
                    # Inner brighter cell
                    inner_color = NEON_CYAN
                    pygame.draw.rect(self.screen, inner_color,
                                   (x * CELL_SIZE + 2, y * CELL_SIZE + 2, 
                                    CELL_SIZE - 4, CELL_SIZE - 4))
        
        # Draw subtle grid lines
        for x in range(0, self.screen_width, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (x, 0), (x, self.screen_height))
        for y in range(0, self.screen_height, CELL_SIZE):
            pygame.draw.line(self.screen, GRID_COLOR, (0, y), (self.screen_width, y))
            
        # Draw scanline effect (retro CRT feel)
        for y in range(0, self.screen_height, 4):
            pygame.draw.line(self.screen, (20, 20, 30), 
                           (0, y), (self.screen_width, y), 1)
        
        # Draw UI elements
        self.draw_ui()
        
        # Draw pattern buttons
        self.draw_buttons()
        
        pygame.display.flip()
        
    def draw_ui(self):
        """Draw on-screen UI elements."""
        # Frame counter
        frame_text = self.font.render(f"Frame: {self.frame_count}", True, TEXT_COLOR)
        self.screen.blit(frame_text, (10, 10))
        
        # Population count
        population = sum(sum(row) for row in self.grid)
        pop_text = self.font.render(f"Population: {population}", True, TEXT_COLOR)
        self.screen.blit(pop_text, (10, 35))
        
        # Rules display
        rules_text = self.font.render(f"Birth: {BIRTH_RULE}, Survive: {SURVIVAL_RULE}", 
                                     True, NEON_CYAN)
        self.screen.blit(rules_text, (10, 60))
        
        # Controls hint
        controls = [
            "Space: Pause/Resume",
            "R: Randomize",
            "C: Clear",
            "+/-: Speed",
            "Click: Toggle cell"
        ]
        
        for i, control in enumerate(controls):
            ctrl_text = self.font.render(control, True, (150, 150, 180))
            btn_x = self.screen_width + 30
            self.screen.blit(ctrl_text, (btn_x, 250 + i * 20))
            
        # FPS display
        fps_text = self.font.render(f"FPS: {int(self.clock.get_fps())}", True, NEON_PURPLE)
        self.screen.blit(fps_text, (10, self.screen_height - 25))
        
    def draw_buttons(self):
        """Draw all control buttons."""
        for btn in self.buttons:
            pygame.draw.rect(self.screen, btn['color'], btn['rect'])
            btn_text = self.font.render(btn['name'], True, (255, 255, 255))
            text_rect = btn_text.get_rect(center=btn['rect'].center)
            self.screen.blit(btn_text, text_rect)
            
    def handle_events(self):
        """Process pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    self.paused = not self.paused
                elif event.key == pygame.K_r:
                    self.randomize_grid()
                elif event.key == pygame.K_c:
                    self.grid = [[False for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    self.fps = min(self.fps + 5, 120)
                elif event.key == pygame.K_MINUS:
                    self.fps = max(self.fps - 5, 5)
                    
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    pos = pygame.mouse.get_pos()
                    gx, gy = self.get_cell_at_pos(pos)
                    
                    # Check if button clicked
                    for btn in self.buttons:
                        if btn['rect'].collidepoint(pos):
                            self.place_pattern(btn['name'])
                            break
                    else:
                        # Toggle cell if not clicking button
                        if gx >= 0 and gy >= 0:
                            self.grid[gy][gx] = not self.grid[gy][gx]
                            
    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(self.fps)
            
        pygame.quit()
        sys.exit()


# ==================== MAIN ENTRY POINT ====================
if __name__ == "__main__":
    print("=" * 60)
    print("Conway's Game of Life - Neon Retro Edition")
    print("=" * 60)
    print(f"Grid: {GRID_WIDTH}x{GRID_HEIGHT} cells ({CELL_SIZE}px each)")
    print(f"Rules: Birth on {BIRTH_RULE}, Survive on {SURVIVAL_RULE}")
    print(f"Controls: Space=Pause, R=Randomize, C=Clear, +/-=Speed")
    print("=" * 60)
    
    game = GameOfLife()
    game.run()

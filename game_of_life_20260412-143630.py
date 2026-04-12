#!/usr/bin/env python3
"""
Conway's Game of Life - Interactive Simulation
Retro neon aesthetic with CRT scanline effects
"""

import pygame
import random
import sys
from datetime import datetime

# =============================================================================
# CONFIGURATION - Make these parameters adjustable at runtime
# =============================================================================
GRID_WIDTH = 80      # Number of cells horizontally
GRID_HEIGHT = 40     # Number of cells vertically
CELL_SIZE = 15       # Pixels per cell
FPS = 30            # Default animation speed

# Colors (neon palette)
BACKGROUND = (10, 10, 15)        # Dark background
NEON_CYAN = (0, 255, 255)        # Cyan for live cells
NEON_MAGENTA = (255, 0, 255)     # Magenta for hover/cursor
NEON_PURPLE = (157, 78, 221)     # Purple accent
GRID_COLOR = (40, 40, 50)        # Subtle grid lines
TEXT_COLOR = (200, 200, 255)     # UI text

# Default Game of Life rules
BIRTH_RULE = 3          # Need exactly 3 neighbors to birth
SURVIVAL_MIN = 2        # Minimum neighbors to survive
SURVIVAL_MAX = 3        # Maximum neighbors to survive

# =============================================================================
# INITIALIZATION
# =============================================================================
def init_pygame():
    """Initialize Pygame with proper settings."""
    pygame.init()
    pygame.display.set_caption("Game of Life - Neon Edition")
    
    # Calculate window size
    width = GRID_WIDTH * CELL_SIZE
    height = GRID_HEIGHT * CELL_SIZE + 100  # Extra space for UI
    
    screen = pygame.display.set_mode((width, height))
    clock = pygame.time.Clock()
    
    return screen, clock

# =============================================================================
# GAME STATE
# =============================================================================
class GameOfLife:
    def __init__(self, width=GRID_WIDTH, height=GRID_HEIGHT):
        self.width = width
        self.height = height
        self.grid = [[False for _ in range(width)] for _ in range(height)]
        self.running = True
        self.paused = False
        self.frame_count = 0
        self.population = 0
        
    def randomize(self):
        """Create a random initial pattern."""
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = random.random() < 0.3
        self.update_population()
    
    def clear(self):
        """Clear the entire grid."""
        for x in range(self.width):
            for y in range(self.height):
                self.grid[x][y] = False
        self.population = 0
    
    def set_cell(self, x, y, state):
        """Toggle or set a cell's state."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[x][y] = state
            if state:
                self.population += 1
            else:
                self.population -= 1
    
    def update_population(self):
        """Count live cells."""
        self.population = sum(sum(row) for row in self.grid)
    
    def next_generation(self, birth_rule=BIRTH_RULE, survival_min=SURVIVAL_MIN, 
                        survival_max=SURVIVAL_MAX):
        """Calculate the next generation based on Conway's rules."""
        new_grid = [row[:] for row in self.grid]
        
        for y in range(self.height):
            for x in range(self.width):
                # Count live neighbors (including diagonals)
                neighbors = 0
                for dx in [-1, 0, 1]:
                    for dy in [-1, 0, 1]:
                        if dx == 0 and dy == 0:
                            continue
                        nx, ny = x + dx, y + dy
                        if 0 <= nx < self.width and 0 <= ny < self.height:
                            if self.grid[ny][nx]:
                                neighbors += 1
                
                # Apply rules
                if self.grid[y][x]:
                    # Survival rule
                    if survival_min <= neighbors <= survival_max:
                        new_grid[y][x] = True
                    else:
                        new_grid[y][x] = False
                else:
                    # Birth rule
                    if neighbors == birth_rule:
                        new_grid[y][x] = True
        
        self.grid = new_grid
        self.frame_count += 1
    
    def get_cell_at(self, mouse_x, mouse_y):
        """Get grid coordinates from mouse position."""
        grid_x = mouse_x // CELL_SIZE
        grid_y = (mouse_y - 100) // CELL_SIZE  # Subtract UI height
        return grid_x, grid_y

# =============================================================================
# RENDERING
# =============================================================================
def draw_grid(screen, game, hovered_x, hovered_y):
    """Draw the game grid with neon effects."""
    
    # Draw subtle background grid
    for x in range(0, screen.get_width(), CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (x, 100), (x, screen.get_height()))
    for y in range(100, screen.get_height(), CELL_SIZE):
        pygame.draw.line(screen, GRID_COLOR, (0, y), (screen.get_width(), y))
    
    # Draw live cells with glow effect
    glow_radius = 5
    
    for y in range(game.height):
        for x in range(game.width):
            if game.grid[y][x]:
                # Create glow effect using multiple circles
                pygame.draw.circle(screen, NEON_CYAN, 
                                  (x * CELL_SIZE + CELL_SIZE // 2, 
                                   y * CELL_SIZE + CELL_SIZE // 2),
                                  glow_radius, 1)
                pygame.draw.circle(screen, NEON_CYAN, 
                                  (x * CELL_SIZE + CELL_SIZE // 2, 
                                   y * CELL_SIZE + CELL_SIZE // 2),
                                  glow_radius - 2, 1)
    
    # Draw hover cursor
    if hovered_x >= 0 and hovered_y >= 0:
        pygame.draw.rect(screen, NEON_MAGENTA, 
                        (hovered_x * CELL_SIZE, hovered_y * CELL_SIZE + 100,
                         CELL_SIZE, CELL_SIZE), 2)

def draw_ui(screen, game, rules):
    """Draw the user interface overlay."""
    font = pygame.font.Font(None, 24)
    small_font = pygame.font.Font(None, 18)
    
    # Frame counter
    frame_text = f"Frame: {game.frame_count}"
    text_surface = font.render(frame_text, True, TEXT_COLOR)
    screen.blit(text_surface, (10, 10))
    
    # Population count
    pop_text = f"Population: {game.population}"
    text_surface = font.render(pop_text, True, TEXT_COLOR)
    screen.blit(text_surface, (10, 40))
    
    # Rules display
    rules_text = f"Birth:{rules['birth']} Surv:{rules['min']}-{rules['max']}"
    text_surface = small_font.render(rules_text, True, NEON_PURPLE)
    screen.blit(text_surface, (10, 75))
    
    # Control hints
    hint_lines = [
        "SPACE: Pause/Resume",
        "R: Randomize | C: Clear",
        "+/-: Speed | Click: Toggle"
    ]
    y_offset = 120
    for line in hint_lines:
        text_surface = small_font.render(line, True, (150, 150, 200))
        screen.blit(text_surface, (10, y_offset))
        y_offset += 20

def draw_scanlines(screen):
    """Draw subtle CRT scanline effect."""
    for y in range(0, screen.get_height(), 4):
        pygame.draw.line(screen, (0, 0, 0), (0, y), (screen.get_width(), y), 1)

# =============================================================================
# PRESET PATTERNS
# =============================================================================
def apply_preset(pattern_name):
    """Apply a classic Game of Life pattern to the grid."""
    game = GameOfLife()
    patterns = {
        "glider": [
            (1, 0), (2, 1), (0, 2), (1, 2), (2, 2)
        ],
        "pulsar": [
            (2, 0), (3, 0), (4, 0), (8, 0), (9, 0), (10, 0),
            (0, 2), (5, 2), (7, 2), (10, 2),
            (0, 5), (5, 5), (7, 5), (10, 5),
            (2, 7), (3, 7), (4, 7), (8, 7), (9, 7), (10, 7),
            (0, 9), (5, 9), (7, 9), (10, 9),
            (2, 10), (3, 10), (4, 10), (8, 10), (9, 10), (10, 10)
        ],
        "lwss": [
            (0, 0), (1, 0), (2, 0), (3, 0),
            (0, 1), (4, 1),
            (0, 2), (1, 2), (2, 2), (3, 2)
        ],
        "beacon": [
            (0, 0), (1, 0), (0, 1), (1, 1),
            (4, 4), (5, 4), (4, 5), (5, 5)
        ]
    }
    
    if pattern_name in patterns:
        width, height = len(patterns[pattern_name][0][0], len(patterns[pattern_name]))
        game.width = max(width, game.width)
        game.height = max(height, game.height)
        
        for x, y in patterns[pattern_name]:
            if 0 <= x < game.width and 0 <= y < game.height:
                game.set_cell(x, y, True)
        game.update_population()

# =============================================================================
# MAIN GAME LOOP
# =============================================================================
def main():
    """Main game loop."""
    screen, clock = init_pygame()
    
    # Get current timestamp for filename
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"game_of_life_{timestamp}.py"
    print(f"Game of Life simulation loaded: {filename}")
    
    # Initialize game
    game = GameOfLife(GRID_WIDTH, GRID_HEIGHT)
    game.randomize()
    
    # Rules configuration
    rules = {
        'birth': BIRTH_RULE,
        'min': SURVIVAL_MIN,
        'max': SURVIVAL_MAX
    }
    
    # Speed settings
    current_fps = FPS
    speed_delta = 1
    
    # Mouse tracking
    hovered_x, hovered_y = -1, -1
    
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
                
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    current_fps = min(120, current_fps + speed_delta)
                
                elif event.key == pygame.K_MINUS:
                    current_fps = max(5, current_fps - speed_delta)
                
                # Preset patterns
                elif event.key == pygame.K_1:
                    apply_preset("glider")
                elif event.key == pygame.K_2:
                    apply_preset("pulsar")
                elif event.key == pygame.K_3:
                    apply_preset("lwss")
                elif event.key == pygame.K_4:
                    apply_preset("beacon")
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mx, my = pygame.mouse.get_pos()
                    grid_x, grid_y = game.get_cell_at(mx, my)
                    
                    if grid_x >= 0 and grid_y >= 0:
                        current_state = game.grid[grid_y][grid_x]
                        game.set_cell(grid_x, grid_y, not current_state)
                        game.update_population()
        
        # Update game state
        if not game.paused:
            game.next_generation(
                rules['birth'], 
                rules['min'], 
                rules['max']
            )
        
        # Calculate hover position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        hovered_x, hovered_y = game.get_cell_at(mouse_x, mouse_y)
        
        # Clear screen
        screen.fill(BACKGROUND)
        
        # Draw components
        draw_grid(screen, game, hovered_x, hovered_y)
        draw_scanlines(screen)
        draw_ui(screen, game, rules)
        
        # Update display
        pygame.display.flip()
        clock.tick(current_fps)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
"""
Git commit command:
git add game_of_life_*.py
git commit -m "made by [MODEL_NAME]"
git push origin master
"""

"""
Retro-Style Neon Conway's Game of Life Simulation
Created by [MODEL_NAME]
"""

import pygame
import random
import sys

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 700
CELL_SIZE = 15
GRID_WIDTH = SCREEN_WIDTH // CELL_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // CELL_SIZE
BG_COLOR = (10, 10, 15)  # Dark background
GRID_COLOR = (30, 30, 50)  # Subtle grid lines
SCANLINE_COLOR = (0, 0, 0)
SCANLINE_ALPHA = 100

# Neon colors
NEON_CYAN = (0, 255, 255)
NEON_MAGENTA = (255, 0, 255)
NEON_PURPLE = (157, 78, 221)

class GameOfLife:
    def __init__(self):
        self.grid_width = GRID_WIDTH
        self.grid_height = GRID_HEIGHT
        
        # Default game rules
        self.birth_rule = 3  # Cell born if exactly 3 neighbors
        self.survival_min = 2  # Cell survives if at least X neighbors
        self.survival_max = 3  # Cell survives if at most Y neighbors
        
        # Animation settings
        self.fps = 30
        self.cell_size = CELL_SIZE
        
        # Initialize grid
        self.grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        # Statistics
        self.frame_count = 0
        self.population = 0
        
    def randomize_grid(self):
        """Randomize the grid with a given density."""
        density = 0.3
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                self.grid[y][x] = 1 if random.random() < density else 0
        self.frame_count = 0
        self.update_population()
    
    def clear_grid(self):
        """Clear all cells from the grid."""
        self.grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        self.frame_count = 0
        self.population = 0
    
    def update_population(self):
        """Count live cells."""
        self.population = sum(sum(row) for row in self.grid)
    
    def get_neighbors(self, x, y):
        """Get the count of live neighbors for a cell at position (x, y)."""
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx, ny = x + dx, y + dy
                if 0 <= nx < self.grid_width and 0 <= ny < self.grid_height:
                    count += self.grid[ny][nx]
        return count
    
    def next_generation(self):
        """Compute the next generation based on Conway's Game of Life rules."""
        new_grid = [[0 for _ in range(self.grid_width)] for _ in range(self.grid_height)]
        
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                neighbors = self.get_neighbors(x, y)
                
                if self.grid[y][x] == 1:
                    # Survival rule
                    if self.survival_min <= neighbors <= self.survival_max:
                        new_grid[y][x] = 1
                else:
                    # Birth rule
                    if neighbors == self.birth_rule:
                        new_grid[y][x] = 1
        
        self.grid = new_grid
        self.frame_count += 1
        self.update_population()
    
    def toggle_cell(self, x, y):
        """Toggle the state of a cell at position (x, y)."""
        if 0 <= x < self.grid_width and 0 <= y < self.grid_height:
            self.grid[y][x] = 1 - self.grid[y][x]
            self.update_population()
    
    def draw_cell(self, surface, x, y, alive):
        """Draw a single cell with neon glow effect."""
        rect = pygame.Rect(
            x * self.cell_size,
            y * self.cell_size,
            self.cell_size,
            self.cell_size
        )
        
        if alive:
            # Draw glow effect
            glow_surface = pygame.Surface((self.cell_size + 4, self.cell_size + 4), pygame.SRCALPHA)
            pygame.draw.rect(glow_surface, (*NEON_CYAN, 100), glow_surface.get_rect(), border_radius=2)
            surface.blit(glow_surface, (rect.x - 2, rect.y - 2))
            
            # Draw main cell with neon color
            pygame.draw.rect(surface, NEON_CYAN, rect, border_radius=2)
        else:
            pygame.draw.rect(surface, GRID_COLOR, rect, 1)
    
    def draw(self, surface):
        """Draw the grid and all cells."""
        for y in range(self.grid_height):
            for x in range(self.grid_width):
                self.draw_cell(surface, x, y, self.grid[y][x])
    
    def draw_ui(self, surface):
        """Draw UI elements on screen."""
        font = pygame.font.SysFont('Courier New', 16)
        
        # Info panel background
        panel_rect = pygame.Rect(10, 10, 320, 130)
        pygame.draw.rect(surface, (20, 20, 30), panel_rect, border_radius=5)
        pygame.draw.rect(surface, NEON_MAGENTA, panel_rect, 2, border_radius=5)
        
        # Statistics
        info_lines = [
            f"Frame: {self.frame_count}",
            f"Population: {self.population}",
            f"Birth Rule: {self.birth_rule}",
            f"Survival: [{self.survival_min}-{self.survival_max}]",
            f"Speed: {self.fps} FPS"
        ]
        
        for i, line in enumerate(info_lines):
            text = font.render(line, True, (200, 200, 200))
            surface.blit(text, (20, 20 + i * 20))
        
        # Controls hint
        control_text = font.render("Controls:", True, NEON_CYAN)
        surface.blit(control_text, (20, 100))
        
        controls = [
            "SPACE: Pause/Resume",
            "R: Randomize",
            "C: Clear",
            "+/-: Speed",
            "Click: Toggle cell"
        ]
        
        for i, control in enumerate(controls):
            ctrl_surface = font.render(control, True, (180, 180, 180))
            surface.blit(ctrl_surface, (20, 120 + i * 18))
    
    def draw_scanlines(self, surface):
        """Draw CRT scanline effect."""
        scanline_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        
        for y in range(0, SCREEN_HEIGHT, 2):
            pygame.draw.line(
                scanline_surface,
                (*SCANLINE_COLOR, SCANLINE_ALPHA),
                (0, y),
                (SCREEN_WIDTH, y),
                1
            )
        
        surface.blit(scanline_surface, (0, 0))

# Preset patterns
def load_pattern(grid, pattern_name):
    """Load a classic Game of Life pattern into the grid."""
    grid.clear_grid()
    
    patterns = {
        'glider': [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
        'pulsar': [
            # Pulsar pattern
            (4, 0), (4, 1), (4, 5), (4, 6),
            (8, 0), (8, 1), (8, 5), (8, 6),
            (0, 4), (1, 4), (5, 4), (6, 4),
            (0, 8), (1, 8), (5, 8), (6, 8)
        ],
        'gosper_gun': [
            # Gosper glider gun
            (20, 0), (20, 1), (20, 10), (20, 11),
            (21, 0), (21, 1), (21, 10), (21, 11),
            (22, 5), (22, 6), (22, 7), (22, 8),
            (24, 3), (24, 4), (24, 9), (24, 10),
            (34, 2), (34, 3), (34, 4), (35, 2), (35, 3), (35, 4),
            (36, 1), (36, 5),
            (37, 0), (37, 6),
            (38, 0), (38, 6),
            (39, 1), (39, 5),
            (40, 3), (40, 4),
            (45, 3), (45, 4), (45, 5),
            (48, 2), (48, 3), (48, 4)
        ],
        'spaceship': [(0, 0), (0, 1), (0, 4), (1, 0), (1, 4), (2, 0), (2, 4), (3, 1), (3, 2), (3, 3)]
    }
    
    if pattern_name in patterns:
        for x, y in patterns[pattern_name]:
            grid.grid[y][x] = 1
        grid.update_population()

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Neon Game of Life - Retro Edition")
    
    game = GameOfLife()
    game.randomize_grid()
    
    clock = pygame.time.Clock()
    running = True
    paused = False
    
    # Create buttons for preset patterns
    button_font = pygame.font.SysFont('Courier New', 14)
    buttons = [
        {'rect': pygame.Rect(10, SCREEN_HEIGHT - 80, 100, 30), 'text': 'Glider', 'action': lambda: load_pattern(game, 'glider')},
        {'rect': pygame.Rect(120, SCREEN_HEIGHT - 80, 100, 30), 'text': 'Pulsar', 'action': lambda: load_pattern(game, 'pulsar')},
        {'rect': pygame.Rect(230, SCREEN_HEIGHT - 80, 100, 30), 'text': 'Gun', 'action': lambda: load_pattern(game, 'gosper_gun')},
        {'rect': pygame.Rect(340, SCREEN_HEIGHT - 80, 100, 30), 'text': 'Ship', 'action': lambda: load_pattern(game, 'spaceship')}
    ]
    
    print(f"Game of Life simulation created at: {filepath}")
    print("Press SPACE to pause/resume")
    print("Press R to randomize")
    print("Press C to clear")
    print("Press +/- to adjust speed")
    print("Click on grid to toggle cells")
    print("Use buttons below to load preset patterns")
    
    while running:
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    paused = not paused
                elif event.key == pygame.K_r:
                    game.randomize_grid()
                elif event.key == pygame.K_c:
                    game.clear_grid()
                elif event.key == pygame.K_PLUS or event.key == pygame.K_EQUALS:
                    game.fps = min(60, game.fps + 5)
                elif event.key == pygame.K_MINUS:
                    game.fps = max(1, game.fps - 5)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    
                    # Check if clicking on buttons
                    button_clicked = False
                    for button in buttons:
                        if button['rect'].collidepoint(mouse_x, mouse_y):
                            button['action']()
                            button_clicked = True
                            break
                    
                    # Otherwise toggle cell
                    if not button_clicked and mouse_y < SCREEN_HEIGHT - 90:
                        grid_x = mouse_x // game.cell_size
                        grid_y = mouse_y // game.cell_size
                        game.toggle_cell(grid_x, grid_y)
        
        # Update game state
        if not paused:
            game.next_generation()
        
        # Drawing
        screen.fill(BG_COLOR)
        
        # Draw grid and cells
        game.draw(screen)
        
        # Draw scanlines for retro effect
        game.draw_scanlines(screen)
        
        # Draw UI
        game.draw_ui(screen)
        
        # Draw buttons
        for button in buttons:
            color = NEON_PURPLE if button['rect'].collidepoint(pygame.mouse.get_pos()) else (30, 30, 50)
            pygame.draw.rect(screen, color, button['rect'], border_radius=5)
            pygame.draw.rect(screen, NEON_CYAN, button['rect'], 2, border_radius=5)
            
            text = button_font.render(button['text'], True, (255, 255, 255))
            text_rect = text.get_rect(center=button['rect'].center)
            screen.blit(text, text_rect)
        
        # Pause indicator
        if paused:
            pause_text = font.render("PAUSED", True, NEON_MAGENTA)
            pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            screen.blit(pause_text, pause_rect)
        
        pygame.display.flip()
        clock.tick(game.fps)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

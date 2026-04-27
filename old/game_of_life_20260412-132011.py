#!/usr/bin/env python3
"""
Conway's Game of Life Simulation with Retro Neon Styling

Features:
- Parametrizable game rules (birth/survival conditions)
- Retro aesthetic with neon colors and scanline overlay
- Interactive controls: pause, randomize, clear, speed adjustment
- Mouse interaction for cell toggling
- Classic pattern presets (glider, pulsar, etc.)
"""

import pygame
import sys
import math
from typing import List, Tuple, Set

# ============================================================================
# Configuration Constants
# ============================================================================

# Grid configuration
GRID_WIDTH = 80
GRID_HEIGHT = 40
CELL_SIZE = 15

# Colors - Retro neon palette
COLOR_BG = (10, 10, 15)  # Dark background
COLOR_GRID = (20, 20, 30)  # Subtle grid lines
COLOR_CELLS = [
    (0, 255, 255),    # Cyan
    (255, 0, 255),    # Magenta
    (157, 78, 222),   # Purple
]
COLOR_TEXT = (200, 200, 230)  # Light text color
COLOR_SCANLINE = (0, 0, 0, 30)  # Semi-transparent black for scanlines

# Game configuration
FPS_MIN = 5
FPS_MAX = 60
DEFAULT_FPS = 15

# Classic patterns
PATTERNS = {
    "Glider": [(0, 1), (1, 2), (2, 0), (2, 1), (2, 2)],
    "Pulsar": [(-2, 0), (-1, 0), (1, 0), (2, 0), (0, -1), (0, 2)],
    "Block": [(0, 0), (1, 0), (0, 1), (1, 1)],
    "T-Pulsar": [(-1, 0), (0, 0), (1, 0), (0, -1)],
    "Pentile": [(-1, 0), (0, 0), (1, 0), (-2, 1), (2, 1), (-2, 2), (2, 2), (-1, 3), (0, 3), (1, 3)]
}


class GameOfLife:
    """Conway's Game of Life implementation with retro neon visuals."""

    def __init__(self, width: int = GRID_WIDTH, height: int = GRID_HEIGHT,
                 cell_size: int = CELL_SIZE):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.grid: List[List[int]] = [[0] * width for _ in range(height)]
        
        # Game state
        self.is_running = False
        self.fps = DEFAULT_FPS
        self.frame_count = 0
        self.generation = 0
        
        # Rule configuration (parametrizable)
        self.birth_rule = 3      # Number of neighbors to spawn new cell
        self.survival_min = 2    # Minimum neighbors to survive
        self.survival_max = 3    # Maximum neighbors to survive
        
        # Timing for animation
        self.last_update = 0
        
        # UI button positions
        self.buttons = self._create_buttons()

    def _create_buttons(self) -> List[Tuple[str, int, int, int, int]]:
        """Create clickable pattern buttons."""
        buttons = []
        x_start = 10
        y_start = 10
        btn_width = 80
        btn_height = 25
        spacing = 5
        
        for i, (name, _) in enumerate(PATTERNS.items()):
            x = x_start + (btn_width + spacing) * (i % 3)
            y = y_start + (btn_height + spacing) * (i // 3)
            buttons.append((name, x, y, btn_width, btn_height))
        
        return buttons

    def toggle_cell(self, mouse_x: int, mouse_y: int):
        """Toggle cell state at given coordinates."""
        col = mouse_x // self.cell_size
        row = mouse_y // self.cell_size
        if 0 <= col < self.width and 0 <= row < self.height:
            self.grid[row][col] = 1 - self.grid[row][col]

    def clear(self):
        """Clear the entire grid."""
        self.grid = [[0] * self.width for _ in range(self.height)]
        self.generation = 0

    def randomize(self):
        """Fill grid with random cells."""
        import random
        for row in range(self.height):
            for col in range(self.width):
                self.grid[row][col] = 1 if random.random() < 0.2 else 0

    def apply_pattern(self, pattern_name: str):
        """Apply a classic pattern to the center of the grid."""
        if pattern_name not in PATTERNS:
            return
        
        self.clear()
        pattern = PATTERNS[pattern_name]
        center_x = self.width // 2
        center_y = self.height // 2
        
        for dx, dy in pattern:
            col = center_x + dx
            row = center_y + dy
            if 0 <= col < self.width and 0 <= row < self.height:
                self.grid[row][col] = 1

    def count_neighbors(self, row: int, col: int) -> int:
        """Count live neighbors for a cell (toroidal wrapping)."""
        count = 0
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0:
                    continue
                
                neighbor_row = (row + i) % self.height
                neighbor_col = (col + j) % self.width
                count += self.grid[neighbor_row][neighbor_col]
        
        return count

    def update(self) -> bool:
        """Update the grid state according to Conway's rules."""
        if not self.is_running:
            return False
        
        # Create new grid for next generation
        new_grid = [[0] * self.width for _ in range(self.height)]
        
        for row in range(self.height):
            for col in range(self.width):
                neighbors = self.count_neighbors(row, col)
                current = self.grid[row][col]
                
                # Apply rules
                if current == 1:
                    # Survival rule: cell survives if neighbors in [survival_min, survival_max]
                    if self.survival_min <= neighbors <= self.survival_max:
                        new_grid[row][col] = 1
                else:
                    # Birth rule: dead cell becomes alive if exactly birth_rule neighbors
                    if neighbors == self.birth_rule:
                        new_grid[row][col] = 1
        
        self.grid = new_grid
        self.generation += 1
        return True

    def get_population(self) -> int:
        """Count live cells in the grid."""
        return sum(sum(row) for row in self.grid)

    def get_button_at(self, mouse_x: int, mouse_y: int) -> str | None:
        """Check if mouse click hits any pattern button."""
        for name, x, y, w, h in self.buttons:
            if x <= mouse_x <= x + w and y <= mouse_y <= y + h:
                return name
        return None


class GameRenderer:
    """Handles all rendering operations with retro neon styling."""

    def __init__(self, game: GameOfLife):
        self.game = game
        self.width = game.width * game.cell_size
        self.height = game.height * game.cell_size
        
        # Initialize pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height + 150))
        pygame.display.set_caption("Game of Life - Retro Neon")
        
        # Setup fonts
        pygame.font.init()
        self.font_small = pygame.font.SysFont("monospace", 12)
        self.font_large = pygame.font.SysFont("monospace", 16)

    def draw_grid(self):
        """Draw the background grid."""
        self.screen.fill(COLOR_BG)
        
        # Draw subtle grid lines
        for x in range(0, self.width + 1, self.game.cell_size):
            pygame.draw.line(
                self.screen, COLOR_GRID,
                (x, 0), (x, self.height),
                1
            )
        
        for y in range(0, self.height + 1, self.game.cell_size):
            pygame.draw.line(
                self.screen, COLOR_GRID,
                (0, y), (self.width, y),
                1
            )

    def draw_cells(self):
        """Draw live cells with neon glow effect."""
        for row in range(self.game.height):
            for col in range(self.game.width):
                if self.game.grid[row][col] == 1:
                    x = col * self.game.cell_size
                    y = row * self.game.cell_size
                    
                    # Select color based on position for variety
                    color_idx = (row + col) % len(COLOR_CELLS)
                    color = COLOR_CELLS[color_idx]
                    
                    # Draw cell with glow effect
                    pygame.draw.rect(
                        self.screen, color,
                        (x + 1, y + 1, self.game.cell_size - 2, self.game.cell_size - 2)
                    )
                    
                    # Add glow overlay
                    glow_surface = pygame.Surface(
                        (self.game.cell_size - 2, self.game.cell_size - 2),
                        pygame.SRCALPHA
                    )
                    glow_surface.fill((*color, 100))
                    self.screen.blit(glow_surface, (x + 1, y + 1))

    def draw_ui(self):
        """Draw on-screen UI elements."""
        y_offset = self.height + 10
        
        # Frame counter
        frame_text = self.font_small.render(
            f"Frame: {self.game.frame_count}", True, COLOR_TEXT
        )
        self.screen.blit(frame_text, (10, y_offset))
        
        # Population count
        pop_text = self.font_small.render(
            f"Population: {self.game.get_population()}", True, COLOR_TEXT
        )
        self.screen.blit(pop_text, (150, y_offset))
        
        # Generation counter
        gen_text = self.font_small.render(
            f"Generation: {self.game.generation}", True, COLOR_TEXT
        )
        self.screen.blit(gen_text, (300, y_offset))
        
        # FPS display
        fps_text = self.font_small.render(
            f"Speed: {self.game.fps} FPS", True, COLOR_TEXT
        )
        self.screen.blit(fps_text, (450, y_offset))
        
        # Run state
        state_text = self.font_small.render(
            "PAUSED" if not self.game.is_running else "RUNNING", True,
            (255, 100, 100) if not self.game.is_running else (100, 255, 100)
        )
        self.screen.blit(state_text, (580, y_offset))

    def draw_rules(self):
        """Draw rule parameters."""
        y_offset = self.height + 35
        
        rules = [
            f"Birth: {self.game.birth_rule}",
            f"Survival: {self.game.survival_min}-{self.game.survival_max}"
        ]
        
        for i, rule in enumerate(rules):
            rule_text = self.font_small.render(rule, True, COLOR_TEXT)
            self.screen.blit(rule_text, (10, y_offset + i * 20))

    def draw_controls(self):
        """Draw control hints in corner."""
        controls = [
            "Spacebar: Pause/Resume",
            "R: Randomize",
            "C: Clear",
            "+/-: Speed",
            "Mouse: Toggle Cell"
        ]
        
        y_offset = self.height + 95
        for i, control in enumerate(controls):
            text = self.font_small.render(control, True, (150, 150, 180))
            self.screen.blit(text, (self.width - 220, y_offset + i * 18))

    def draw_buttons(self):
        """Draw pattern buttons."""
        for name, x, y, w, h in self.game.buttons:
            # Button background
            pygame.draw.rect(
                self.screen, (50, 50, 60),
                (x, y, w, h)
            )
            
            # Button border
            pygame.draw.rect(
                self.screen, COLOR_CELLS[hash(name) % len(COLOR_CELLS)],
                (x, y, w, h), 2
            )
            
            # Button text
            text = self.font_small.render(name, True, COLOR_TEXT)
            self.screen.blit(text, (x + 10, y + 6))

    def draw_scanlines(self):
        """Draw scanline overlay for retro feel."""
        for y in range(0, self.height, 3):
            scanline_surface = pygame.Surface(
                (self.width, 2), pygame.SRCALPHA
            )
            scanline_surface.fill(COLOR_SCANLINE)
            self.screen.blit(scanline_surface, (0, y))

    def render(self):
        """Render the complete frame."""
        self.draw_grid()
        self.draw_cells()
        self.draw_ui()
        self.draw_rules()
        self.draw_buttons()
        self.draw_controls()
        self.draw_scanlines()
        
        pygame.display.flip()


def main():
    """Main game loop."""
    try:
        # Initialize game
        game = GameOfLife()
        renderer = GameRenderer(game)
        
        clock = pygame.time.Clock()
        
        running = True
        while running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game.is_running = not game.is_running
                    
                    elif event.key == pygame.K_r:
                        game.randomize()
                    
                    elif event.key == pygame.K_c:
                        game.clear()
                    
                    elif event.key == pygame.K_PLUS or event.key == pygame.K_UP:
                        game.fps = min(game.fps + 5, FPS_MAX)
                    
                    elif event.key == pygame.K_MINUS or event.key == pygame.K_DOWN:
                        game.fps = max(game.fps - 5, FPS_MIN)
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        # Check pattern buttons first
                        pattern_name = game.get_button_at(event.pos[0], event.pos[1])
                        if pattern_name:
                            game.apply_pattern(pattern_name)
                        else:
                            game.toggle_cell(event.pos[0], event.pos[1])
            
            # Update game state
            current_time = pygame.time.get_ticks()
            if current_time - game.last_update >= 1000 // game.fps:
                if game.update():
                    game.frame_count += 1
                game.last_update = current_time
            
            # Render frame
            renderer.render()
            clock.tick(60)  # Cap at 60 FPS for smooth UI
        
        pygame.quit()
        sys.exit(0)
    
    except Exception as e:
        print(f"Error: {e}")
        pygame.quit()
        sys.exit(1)


if __name__ == "__main__":
    main()

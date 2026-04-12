"""
Conway's Game of Life - Retro Neon Wave Simulation
Python/Pygame implementation with configurable rules and retro aesthetics.
"""

import pygame
import random
import time
from typing import List, Tuple, Optional

# ============================================================================
# CONFIGURATION
# ============================================================================

# Grid configuration
GRID_WIDTH = 80
GRID_HEIGHT = 40
CELL_SIZE = 15

# Visual configuration
BACKGROUND_COLOR = (10, 10, 15)
NEON_COLORS = [
    (0, 255, 255),   # Cyan
    (255, 0, 255),   # Magenta
    (157, 78, 222),  # Purple
]
GRID_LINE_COLOR = (20, 20, 30)

# Game rules (parametrizable)
DEFAULT_BIRTH_NEIGHBORS = [3]          # Birth rule: cell spawns if exactly N neighbors
DEFAULT_SURVIVE_MIN_NEIGHBORS = 2      # Minimum neighbors to survive
DEFAULT_SURVIVE_MAX_NEIGHBORS = 3      # Maximum neighbors to survive

# Animation configuration
FPS = 10
MAX_FPS = 60

# ============================================================================
# GAME OF LIFE LOGIC
# ============================================================================

class GameOfLife:
    """Conway's Game of Life implementation with configurable rules."""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.reset()
    
    def reset(self):
        """Reset grid to empty state."""
        self.grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        self.generation = 0
    
    def randomize(self):
        """Fill grid with random cells."""
        for y in range(self.height):
            for x in range(self.width):
                self.grid[y][x] = 1 if random.random() < 0.2 else 0
        self.generation = 0
    
    def clear(self):
        """Clear all cells."""
        self.reset()
    
    def toggle_cell(self, x: int, y: int):
        """Toggle cell state at position."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = 1 - self.grid[y][x]
    
    def get_neighbors(self, x: int, y: int) -> int:
        """Count live neighbors for a cell (with toroidal wrapping)."""
        count = 0
        for dy in [-1, 0, 1]:
            for dx in [-1, 0, 1]:
                if dx == 0 and dy == 0:
                    continue
                nx = (x + dx) % self.width
                ny = (y + dy) % self.height
                count += self.grid[ny][nx]
        return count
    
    def update(self, birth_neighbors: List[int] = None,
               survive_min: int = None, survive_max: int = None) -> bool:
        """
        Update grid state using Game of Life rules.
        
        Args:
            birth_neighbors: List of neighbor counts that cause birth (default: [3])
            survive_min: Minimum neighbors to survive (default: 2)
            survive_max: Maximum neighbors to survive (default: 3)
        Returns:
            True if grid changed, False otherwise
        """
        if birth_neighbors is None:
            birth_neighbors = DEFAULT_BIRTH_NEIGHBORS
        if survive_min is None:
            survive_min = DEFAULT_SURVIVE_MIN_NEIGHBORS
        if survive_max is None:
            survive_max = DEFAULT_SURVIVE_MAX_NEIGHBORS
        
        new_grid = [[0 for _ in range(self.width)] for _ in range(self.height)]
        changed = False
        
        for y in range(self.height):
            for x in range(self.width):
                neighbors = self.get_neighbors(x, y)
                current = self.grid[y][x]
                
                # Apply rules
                if current == 0:
                    # Birth rule: spawn if neighbor count matches birth config
                    if neighbors in birth_neighbors:
                        new_grid[y][x] = 1
                    else:
                        new_grid[y][x] = 0
                else:
                    # Survival rule: survive if neighbors in range
                    if survive_min <= neighbors <= survive_max:
                        new_grid[y][x] = 1
                    else:
                        new_grid[y][x] = 0
                
                if new_grid[y][x] != current:
                    changed = True
        
        self.grid = new_grid
        self.generation += 1
        return changed
    
    def get_population(self) -> int:
        """Count live cells."""
        return sum(sum(row) for row in self.grid)
    
    def set_cell(self, x: int, y: int, state: int):
        """Set cell state directly."""
        if 0 <= x < self.width and 0 <= y < self.height:
            self.grid[y][x] = max(0, min(1, state))

# ============================================================================
# RENDERER
# ============================================================================

class GameRenderer:
    """Retro neon wave renderer with Pygame."""
    
    def __init__(self, game: GameOfLife):
        self.game = game
        self.width = game.width * CELL_SIZE
        self.height = game.height * CELL_SIZE
        
        # Initialize Pygame
        pygame.init()
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Game of Life - Retro Neon Wave")
        
        # Create grid surface for efficient rendering
        self.grid_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        
        # Create scanline surface with alpha
        self.scanline_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.scanline_surface.set_colorkey(None)  # Enable alpha blending
        
        # Draw scanlines on the surface
        self.scanline_surface.fill((0, 0, 0, 0))  # Clear with transparency
        for y in range(0, self.height, 4):
            rect = pygame.Rect(0, y, self.width, 2)
            pygame.draw.rect(self.scanline_surface, (0, 0, 0, 50), rect)
        
        # Clock for FPS control
        self.clock = pygame.time.Clock()
    
    def draw_grid(self):
        """Draw grid lines and background."""
        self.grid_surface.fill(BACKGROUND_COLOR)
        
        # Draw vertical lines
        for x in range(0, self.width + 1, CELL_SIZE):
            color = (30, 30, 40) if x % (CELL_SIZE * 5) == 0 else GRID_LINE_COLOR
            pygame.draw.line(self.grid_surface, color, (x, 0), (x, self.height), 1)
        
        # Draw horizontal lines
        for y in range(0, self.height + 1, CELL_SIZE):
            color = (30, 30, 40) if y % (CELL_SIZE * 5) == 0 else GRID_LINE_COLOR
            pygame.draw.line(self.grid_surface, color, (0, y), (self.width, y), 1)
    
    def draw_cells(self):
        """Draw live cells with neon glow effect."""
        for y in range(self.game.height):
            for x in range(self.game.width):
                if self.game.grid[y][x] == 1:
                    # Calculate neon color based on position and generation
                    color_idx = (x + y + self.game.generation // 5) % len(NEON_COLORS)
                    color = NEON_COLORS[color_idx]
                    
                    # Draw cell with glow effect
                    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    pygame.draw.rect(self.grid_surface, color, rect)
                    
                    # Add outer glow ring
                    glow_rect = pygame.Rect(rect.left - 1, rect.top - 1, 
                                          rect.width + 2, rect.height + 2)
                    glow_color = tuple(min(255, int(c * 0.6)) for c in color)
                    pygame.draw.rect(self.grid_surface, glow_color, glow_rect, 1)
    
    def draw_ui(self, fps: float):
        """Draw on-screen UI elements."""
        font = pygame.font.SysFont('monospace', 14)
        
        # Statistics
        stats = [
            f"Frame: {self.game.generation}",
            f"Population: {self.game.get_population()}",
            f"FPS: {fps:.1f}",
            f"Rules: B{self.game.DEFAULT_BIRTH_NEIGHBORS}, S{self.game.DEFAULT_SURVIVE_MIN_NEIGHBORS}-{self.game.DEFAULT_SURVIVE_MAX_NEIGHBORS}"
        ]
        
        y_pos = 5
        for text in stats:
            label = font.render(text, True, (200, 200, 220))
            self.screen.blit(label, (10, y_pos))
            y_pos += 20
    
    def draw_scanlines(self):
        """Draw retro scanline overlay."""
        for rect in self.scanlines:
            self.screen.fill((0, 0, 0, 50), rect, special_flags=pygame.SRCALPHA)
    
    def render(self, fps: float, paused: bool = False):
        """Render entire frame."""
        # Draw grid and cells
        self.draw_grid()
        self.draw_cells()
        
        # Copy to main screen
        self.screen.blit(self.grid_surface, (0, 0))
        
        # Draw scanlines
        self.draw_scanlines()
        
        # Draw UI
        self.draw_ui(fps)
        
        # Pause indicator
        if paused:
            font = pygame.font.SysFont('monospace', 48)
            pause_label = font.render("PAUSED", True, (255, 255, 255))
            rect = pause_label.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(pause_label, rect)
        
        pygame.display.flip()
    
    def handle_events(self) -> Tuple[bool, bool]:
        """Handle input events. Returns (should_exit, paused)."""
        should_exit = False
        mouse_pressed = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                should_exit = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    return True, True  # Toggle pause
                elif event.key == pygame.K_r:
                    self.game.randomize()
                elif event.key == pygame.K_c:
                    self.game.clear()
                elif event.key == pygame.K_ESCAPE:
                    should_exit = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_pressed = True
                    x, y = event.pos
                    grid_x = x // CELL_SIZE
                    grid_y = y // CELL_SIZE
                    self.game.toggle_cell(grid_x, grid_y)
        
        return should_exit, False
    
    def get_mouse_position(self) -> Optional[Tuple[int, int]]:
        """Get current mouse position in grid coordinates."""
        mouse_state = pygame.mouse.get_pressed()
        if mouse_state[0]:  # Left button pressed
            x, y = pygame.mouse.get_pos()
            grid_x = x // CELL_SIZE
            grid_y = y // CELL_SIZE
            if 0 <= grid_x < self.game.width and 0 <= grid_y < self.game.height:
                return (grid_x, grid_y)
        return None
    
    def draw_drawing_cells(self, mouse_pos: Optional[Tuple[int, int]]):
        """Draw cells being drawn with mouse."""
        if mouse_pos:
            x, y = mouse_pos
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(self.grid_surface, (100, 255, 255), rect, 2)
    
    def cleanup(self):
        """Clean up resources."""
        pygame.quit()

# ============================================================================
# MAIN APPLICATION
# ============================================================================

def main():
    """Main application loop."""
    # Initialize game
    game = GameOfLife(GRID_WIDTH, GRID_HEIGHT)
    game.randomize()
    
    # Initialize renderer
    renderer = GameRenderer(game)
    
    # Game state
    paused = False
    fps = FPS
    last_update = time.time()
    
    print("Game started - Press SPACE to pause, R to randomize, C to clear")
    print("Controls: SPACE=pause, R=randomize, C=clear, +/-=speed, ESC=exit")
    
    try:
        while True:
            # Handle input
            should_exit, space_pressed = renderer.handle_events()
            
            # Handle speed controls
            keys = pygame.key.get_pressed()
            if keys[pygame.K_PLUS] or keys[pygame.K_PLUS]:
                fps = min(MAX_FPS, fps + 5)
            if keys[pygame.K_MINUS]:
                fps = max(1, fps - 5)
            
            # Handle drag drawing
            mouse_pos = renderer.get_mouse_position()
            if mouse_pos:
                game.set_cell(mouse_pos[0], mouse_pos[1], 1)
            
            # Update game logic
            current_time = time.time()
            if not paused and current_time - last_update >= 1.0 / fps:
                game.update()
                last_update = current_time
            
            # Render frame
            renderer.render(fps, paused)
            
            if should_exit:
                break
                
            # Limit FPS for rendering
            renderer.clock.tick(60)
    
    finally:
        renderer.cleanup()

if __name__ == "__main__":
    main()

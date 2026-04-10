import pygame
import random
import sys

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
GRAVITY = 0.5
JUMP_STRENGTH = -8
PIPE_SPEED = 3
PIPE_SPAWN_INTERVAL = 1500
PIPE_GAP = 150
PIPE_WIDTH = 60

# Colors for fallback (if images fail to load)
DARK_COLORS = ['#2F4F4F', '#483D8B', '#8B0000', '#556B2F', '#4B0082']
LIGHT_COLORS = ['#ADD8E6', '#FFB6C1', '#90EE90', '#FFFFE0', '#E0FFFF', '#F0FFF0']
DARK_BROWN = '#8B4513'
YELLOW = '#FFD700'
DARK_GREEN = '#228B22'
LIGHT_BROWN = '#A0522D'
DARK_GRAY = '#696969'

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 36)
large_font = pygame.font.Font(None, 72)

# Try to load images for better cosmetics
def load_images():
    """Load game assets - use colored shapes as fallback if images fail"""
    images = {}
    
    # Create a yellow bird sprite (original Flappy Bird style)
    try:
        # Yellow body with white eye and orange beak
        bird_surface = pygame.Surface((34, 24), pygame.SRCALPHA)
        
        # Yellow body
        pygame.draw.ellipse(bird_surface, (255, 206, 0), (0, 0, 34, 24))
        
        # White eye with black pupil
        pygame.draw.circle(bird_surface, (255, 255, 255), (24, 8), 8)
        pygame.draw.circle(bird_surface, (0, 0, 0), (26, 8), 3)
        
        # Orange beak
        pygame.draw.polygon(bird_surface, (255, 140, 0), [(28, 12), (34, 14), (28, 16)])
        
        images['bird'] = bird_surface
        
        # Create green pipe sprite with border
        pipe_surface = pygame.Surface((PIPE_WIDTH, 100), pygame.SRCALPHA)
        
        # Main green body
        pygame.draw.rect(pipe_surface, (107, 224, 34), (0, 0, PIPE_WIDTH, 100))
        
        # Darker border
        pygame.draw.rect(pipe_surface, (50, 160, 0), (0, 0, PIPE_WIDTH, 100), 3)
        
        # Pipe cap
        cap_height = 25
        pygame.draw.rect(pipe_surface, (107, 224, 34), (-5, 100 - cap_height, PIPE_WIDTH + 10, cap_height))
        pygame.draw.rect(pipe_surface, (50, 160, 0), (-5, 100 - cap_height, PIPE_WIDTH + 10, cap_height), 3)
        
        images['pipe'] = pipe_surface
        
        # Create ground sprite with grass pattern
        ground_surface = pygame.Surface((SCREEN_WIDTH, 50), pygame.SRCALPHA)
        
        # Brown base
        pygame.draw.rect(ground_surface, (139, 69, 19), (0, 0, SCREEN_WIDTH, 50))
        
        # Grass top with green stripes
        grass_colors = [(144, 238, 144), (154, 205, 50), (107, 142, 35)]
        for i in range(0, SCREEN_WIDTH, 20):
            color = grass_colors[i % len(grass_colors)]
            pygame.draw.rect(ground_surface, color, (i, 0, 18, 8))
        
        images['ground'] = ground_surface
        
    except Exception as e:
        print(f"Image loading failed: {e}, using fallback colors")
        images = None
    
    return images

# Try to load background image
def create_background():
    """Create a nice sky background with clouds"""
    bg_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    
    # Sky gradient (light blue)
    for y in range(SCREEN_HEIGHT):
        r = min(255, 135 + y * 0.3)
        g = min(255, 206 + y * 0.2)
        b = min(255, 235 - y * 0.2)
        pygame.draw.line(bg_surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    # Add some clouds
    cloud_positions = [(50, 80), (200, 120), (320, 60), (150, 200)]
    for cx, cy in cloud_positions:
        # Cloud body
        pygame.draw.ellipse(bg_surface, (240, 240, 240), (cx - 30, cy - 15, 60, 30))
        pygame.draw.ellipse(bg_surface, (240, 240, 240), (cx - 15, cy - 25, 30, 25))
    
    return bg_surface

# Load assets
images = load_images()
background = create_background()

class Bird:
    def __init__(self):
        self.x = 100
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.angle = 0
        
    def draw(self):
        if images and 'bird' in images:
            # Rotate bird based on velocity
            angle = min(90, max(-90, self.velocity * 5))
            rotated_bird = pygame.transform.rotate(images['bird'], -angle)
            rect = rotated_bird.get_rect(center=(self.x, self.y))
            screen.blit(rotated_bird, rect)
        else:
            # Fallback to colored shape (yellow bird)
            bird_surface = pygame.Surface((34, 24), pygame.SRCALPHA)
            
            # Yellow body
            pygame.draw.ellipse(bird_surface, (255, 206, 0), (0, 0, 34, 24))
            
            # White eye with black pupil
            pygame.draw.circle(bird_surface, (255, 255, 255), (24, 8), 8)
            pygame.draw.circle(bird_surface, (0, 0, 0), (26, 8), 3)
            
            # Orange beak
            pygame.draw.polygon(bird_surface, (255, 140, 0), [(28, 12), (34, 14), (28, 16)])
            
            screen.blit(bird_surface, (self.x - 17, self.y - 12))
        
    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity
        
    def jump(self):
        self.velocity = JUMP_STRENGTH

class Pipe:
    def __init__(self):
        self.x = SCREEN_WIDTH
        self.width = PIPE_WIDTH
        self.gap_y = random.randint(100, SCREEN_HEIGHT - 100 - PIPE_GAP)
        self.passed = False
        
    def draw(self):
        if images and 'pipe' in images:
            # Draw top pipe (flipped)
            top_pipe = pygame.transform.flip(images['pipe'], False, True)
            screen.blit(top_pipe, (self.x, self.gap_y - 100))
            
            # Draw bottom pipe
            screen.blit(images['pipe'], (self.x, self.gap_y + PIPE_GAP))
        else:
            # Fallback to colored rectangles
            
            # Top pipe
            pygame.draw.rect(screen, DARK_GREEN, (self.x, 0, self.width, self.gap_y))
            pygame.draw.rect(screen, (50, 160, 0), (self.x, 0, self.width, self.gap_y), 3)
            
            # Bottom pipe
            pygame.draw.rect(screen, DARK_GREEN, (self.x, self.gap_y + PIPE_GAP, self.width, SCREEN_HEIGHT - self.gap_y - PIPE_GAP))
            pygame.draw.rect(screen, (50, 160, 0), (self.x, self.gap_y + PIPE_GAP, self.width, SCREEN_HEIGHT - self.gap_y - PIPE_GAP), 3)
        
    def update(self):
        self.x -= PIPE_SPEED
        
    def get_rects(self):
        top_rect = pygame.Rect(self.x, 0, self.width, self.gap_y)
        bottom_rect = pygame.Rect(self.x, self.gap_y + PIPE_GAP, self.width, SCREEN_HEIGHT - self.gap_y - PIPE_GAP)
        return top_rect, bottom_rect

class Ground:
    def __init__(self):
        self.offset = 0
        
    def draw(self):
        if images and 'ground' in images:
            screen.blit(images['ground'], (self.offset, SCREEN_HEIGHT - 50))
            # Draw second copy for seamless scrolling
            screen.blit(images['ground'], (self.offset - SCREEN_WIDTH, SCREEN_HEIGHT - 50))
        else:
            pygame.draw.rect(screen, DARK_BROWN, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))

def check_collision(bird, pipes):
    # Create bird hitbox (slightly smaller than visual for fairness)
    bird_rect = pygame.Rect(bird.x - 12, bird.y - 10, 24, 20)
    
    # Check ground collision
    if bird.y + 12 >= SCREEN_HEIGHT - 50:
        return True
        
    for pipe in pipes:
        top_rect, bottom_rect = pipe.get_rects()
        if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
            return True
            
    return False

def main():
    bird = Bird()
    ground = Ground()
    pipes = []
    score = 0
    best_score = 0
    last_pipe_spawn = pygame.time.get_ticks()
    game_over = False
    
    running = True
    while running:
        current_time = pygame.time.get_ticks()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_q:
                    running = False
                    
                if event.key == pygame.K_SPACE:
                    if game_over:
                        # Restart game
                        bird = Bird()
                        ground = Ground()
                        pipes = []
                        score = 0
                        last_pipe_spawn = current_time
                        game_over = False
                    else:
                        bird.jump()
        
        # Draw background
        screen.blit(background, (0, 0))
        
        if not game_over:
            # Spawn pipes
            if current_time - last_pipe_spawn > PIPE_SPAWN_INTERVAL:
                pipes.append(Pipe())
                last_pipe_spawn = current_time
            
            # Update and draw bird
            bird.update()
            bird.draw()
            
            # Update and draw pipes
            for pipe in pipes[:]:
                pipe.update()
                pipe.draw()
                
                # Check if bird passed the pipe
                if not pipe.passed and pipe.x + pipe.width < bird.x:
                    pipe.passed = True
                    score += 1
                
                # Remove off-screen pipes
                if pipe.x + pipe.width < 0:
                    pipes.remove(pipe)
            
            # Check collision
            if check_collision(bird, pipes):
                game_over = True
                if score > best_score:
                    best_score = score
            
            # Draw ground
            ground.draw()
            
            # Draw score (top right)
            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            pygame.draw.rect(screen, (0, 0, 0), (SCREEN_WIDTH - 140, 10, 130, 36))
            screen.blit(score_text, (SCREEN_WIDTH - 130, 18))
        
        else:
            # Game over screen
            bird.draw()
            ground.draw()
            
            for pipe in pipes:
                pipe.draw()
            
            # Semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            screen.blit(overlay, (0, 0))
            
            # Show best score in the center of the screen
            game_over_text = large_font.render("GAME OVER", True, (255, 215, 0))
            score_text = font.render(f"Score: {score}", True, (255, 255, 255))
            best_text = font.render(f"Best: {best_score}", True, (255, 255, 255))
            
            # Draw game over box
            box_width = max(game_over_text.get_width(), score_text.get_width() + best_text.get_width()) + 40
            box_height = 180
            box_x = SCREEN_WIDTH // 2 - box_width // 2
            box_y = SCREEN_HEIGHT // 2 - box_height // 2
            
            pygame.draw.rect(screen, (255, 248, 220), (box_x, box_y, box_width, box_height))
            pygame.draw.rect(screen, (139, 69, 19), (box_x, box_y, box_width, box_height), 4)
            
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, box_y + 15))
            screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, box_y + 60))
            screen.blit(best_text, (SCREEN_WIDTH//2 - best_text.get_width()//2, box_y + 95))
            
            restart_text = font.render("Press SPACE to restart", True, (255, 255, 255))
            quit_text = font.render("Press Q or Esc to quit", True, (255, 255, 255))
            
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, box_y + 140))
            screen.blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2, box_y + 170))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

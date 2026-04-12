import pygame
import random
import sys
import io
from PIL import Image, ImageDraw

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird - Cosmetic Version")

# --- Asset Generation ---

def create_bird_surface():
    """Procedurally creates a bird image using PIL to mimic the original look."""
    size = 40
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Body (Yellow ellipse)
    draw.ellipse([5, 10, 35, 30], fill=(255, 255, 0))
    # Wing (White)
    draw.ellipse([8, 18, 22, 25], fill=(255, 255, 255))
    # Eye (White with black pupil)
    draw.ellipse([25, 12, 32, 19], fill=(255, 255, 255))
    draw.ellipse([28, 14, 30, 16], fill=(0, 0, 0))
    # Beak (Orange)
    draw.polygon([(32, 20), (40, 23), (32, 26)], fill=(255, 165, 0))

    # Convert PIL to Pygame Surface
    mode = img.mode
    size = img.size
    data = img.tobytes()
    return pygame.image.fromstring(data, size, mode)

def create_background_surface():
    """Creates a sky with clouds."""
    img = Image.new("RGB", (SCREEN_WIDTH, SCREEN_HEIGHT), (135, 206, 235)) # Sky Blue
    draw = ImageDraw.Draw(img)

    # Add some clouds
    for _ in range(5):
        cx = random.randint(0, SCREEN_WIDTH)
        cy = random.randint(50, 200)
        radius = random.randint(30, 60)
        draw.ellipse([cx - radius, cy - radius // 2, cx + radius, cy + radius // 2], fill=(255, 255, 255, 180))

    mode = img.mode
    size = img.size
    data = img.tobytes()
    return pygame.image.fromstring(data, size, mode)

# Pre-generate assets
BIRD_SPRITE = create_bird_surface()
BACKGROUND_SPRITE = create_background_surface()

# Colors
LAND_COLORS = [(101, 67, 33), (255, 255, 0)]  # Dark brown or yellow
PIPE_COLORS = [(34, 139, 34), (139, 69, 19), (64, 64, 64)]  # Dark green, light brown, dark gray

# Game Constants
GRAVITY = 0.25
FLAP_STRENGTH = -6
PIPE_SPEED = 3
PIPE_GAP = 160
PIPE_FREQUENCY = 1500 # milliseconds

class Bird:
    def __init__(self):
        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.size = 40
        self.image = BIRD_SPRITE

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity

    def draw(self, surface):
        # Rotate slightly based on velocity
        rotated_image = pygame.transform.rotate(self.image, -self.velocity * 3)
        rect = rotated_image.get_rect(center=(self.x + self.size // 2, self.y + self.size // 2))
        surface.blit(rotated_image, rect.topleft)

    def get_rect(self):
        # Using a slightly smaller hit-box for fairness
        return pygame.Rect(self.x + 5, self.y + 5, self.size - 10, self.size - 10)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = 60
        self.gap_y = random.randint(100, SCREEN_HEIGHT - 250)
        self.color = random.choice(PIPE_COLORS)
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self, surface):
        # Top pipe with a rim
        pygame.draw.rect(surface, self.color, (self.x, 0, self.width, self.gap_y))
        pygame.draw.rect(surface, (255, 255, 255), (self.x - 2, self.gap_y - 20, self.width + 4, 20)) # Rim
        
        # Bottom pipe with a rim
        pygame.draw.rect(surface, self.color, (self.x, self.gap_y + PIPE_GAP, self.width, SCREEN_HEIGHT))
        pygame.draw.rect(surface, (255, 255, 255), (self.x - 2, self.gap_y + PIPE_GAP, self.width + 4, 20)) # Rim

    def get_rects(self):
        top_rect = pygame.Rect(self.x, 0, self.width, self.gap_y)
        bottom_rect = pygame.Rect(self.x, self.gap_y + PIPE_GAP, self.width, SCREEN_HEIGHT)
        return top_rect, bottom_rect

def main():
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 32, bold=True)
    big_font = pygame.font.SysFont("Arial", 48, bold=True)

    best_score = 0
    
    def reset_game():
        return Bird(), [], 0, pygame.time.get_ticks(), 0

    bird, pipes, score, last_pipe_time, game_over = reset_game()
    land_color = random.choice(LAND_COLORS)

    running = True
    while running:
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_over:
                        bird, pipes, score, last_pipe_time, game_over = reset_game()
                        land_color = random.choice(LAND_COLORS)
                    else:
                        bird.flap()
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    running = False

        if not game_over:
            # Update Bird
            bird.update()

            # Update Pipes
            current_time = pygame.time.get_ticks()
            if current_time - last_pipe_time > PIPE_FREQUENCY:
                pipes.append(Pipe(SCREEN_WIDTH))
                last_pipe_time = current_time

            for pipe in pipes[:]:
                pipe.update()
                if pipe.x + pipe.width < 0:
                    pipes.remove(pipe)
                
                # Score increment
                if not pipe.passed and bird.x > pipe.x + pipe.width:
                    score += 1
                    pipe.passed = True

                # Collision detection
                top_rect, bottom_rect = pipe.get_rects()
                if bird.get_rect().colliderect(top_rect) or bird.get_rect().colliderect(bottom_rect):
                    game_over = True

            # Boundary collision
            if bird.y < 0 or bird.y + bird.size > SCREEN_HEIGHT - 50:
                game_over = True

            if game_over:
                if score > best_score:
                    best_score = score

        # Draw everything
        screen.blit(BACKGROUND_SPRITE, (0, 0))
        
        for pipe in pipes:
            pipe.draw(screen)

        bird.draw(screen)

        # Draw Land
        pygame.draw.rect(screen, land_color, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))
        pygame.draw.rect(screen, (50, 30, 10), (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 5)) # Top edge of land

        # Draw Score
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        # Shadow for readability
        shadow = font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(shadow, (SCREEN_WIDTH - 122, 22))
        screen.blit(score_text, (SCREEN_WIDTH - 120, 20))

        if game_over:
            # Draw a semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 128))
            screen.blit(overlay, (0,0))

            over_text = big_font.render("GAME OVER", True, (255, 255, 255))
            best_text = font.render(f"Best Score: {best_score}", True, (255, 255, 255))
            restart_text = font.render("Press SPACE to Restart", True, (200, 200, 200))
            quit_text = font.render("Press Q or ESC to Quit", True, (200, 200, 200))
            
            screen.blit(over_text, (SCREEN_WIDTH // 2 - over_text.get_width() // 2, SCREEN_HEIGHT // 3))
            screen.blit(best_text, (SCREEN_WIDTH // 2 - best_text.get_width() // 2, SCREEN_HEIGHT // 3 + 60))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2))
            screen.blit(quit_text, (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

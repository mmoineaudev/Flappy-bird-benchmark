import pygame
import random
import sys

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60

# Colors
LIGHT_COLORS = [
    (173, 216, 230),  # Light Blue
    (176, 224, 230),  # Powder Blue
    (135, 206, 235),  # Sky Blue
    (144, 238, 144),  # Light Green
    (255, 250, 205),  # Lemon Chiffon
    (240, 248, 255),  # Alice Blue
]

DARK_COLORS = [
    (0, 0, 139),      # Dark Blue
    (0, 100, 0),      # Dark Green
    (139, 69, 19),    # Saddle Brown
    (25, 25, 25),     # Very Dark Gray
    (47, 79, 79),     # Dark Slate Gray
    (0, 0, 0),        # Black
]

PIPE_COLORS = [
    (0, 100, 0),      # Dark Green
    (139, 69, 19),    # Dark Brown (actually Saddle Brown)
    (105, 105, 105),  # Dim Gray
]

LAND_COLORS = [
    (139, 69, 19),    # Dark Brown
    (255, 215, 0),    # Gold (Yellowish)
]

class Bird:
    def __init__(self):
        self.reset()
        self.shape = random.choice(['square', 'circle', 'triangle'])
        self.color = random.choice(DARK_COLORS)

    def reset(self):
        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.gravity = 0.5
        self.jump_strength = -8

    def jump(self):
        # Requirement 3: Pressing SPACE multiple times will accelerate the bird.
        # In Flappy Bird, "acceleration" usually means a stronger upward impulse.
        self.velocity = self.jump_strength

    def update(self):
        self.velocity += self.gravity
        self.y += self.velocity

    def draw(self, screen):
        if self.shape == 'square':
            pygame.draw.rect(screen, self.color, (self.x, self.y, 30, 30))
        elif self.shape == 'circle':
            pygame.draw.circle(screen, self.color, (int(self.x + 15), int(self.y + 15)), 15)
        elif self.shape == 'triangle':
            points = [(self.x, self.y + 30), (self.x + 15, self.y), (self.x + 30, self.y + 30)]
            pygame.draw.polygon(screen, self.color, points)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, 30, 30)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = 50
        self.gap = 150
        self.top_height = random.randint(50, SCREEN_HEIGHT - self.gap - 100)
        self.bottom_y = self.top_height + self.gap
        self.color = random.choice(PIPE_COLORS)
        self.passed = False

    def update(self):
        self.x -= 3

    def draw(self, screen):
        # Top pipe
        pygame.draw.rect(screen, self.color, (self.x, 0, self.width, self.top_height))
        # Bottom pipe
        pygame.draw.rect(screen, self.color, (self.x, self.bottom_y, self.width, SCREEN_HEIGHT - self.bottom_y))

    def get_rects(self):
        top_rect = pygame.Rect(self.x, 0, self.width, self.top_height)
        bottom_rect = pygame.Rect(self.x, self.bottom_y, self.width, SCREEN_HEIGHT - self.bottom_y)
        return top_rect, bottom_rect

def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Flappy Bird")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)
    large_font = pygame.font.SysFont("Arial", 48)

    bg_color = random.choice(LIGHT_COLORS)
    land_color = random.choice(LAND_COLORS)
    
    bird = Bird()
    pipes = []
    pipe_timer = 0
    score = 0
    high_score = 0
    game_active = True

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_active:
                        bird.jump()
                    else:
                        # Restarting is pressing SPACE again
                        bird.__init__()
                        pipes = []
                        pipe_timer = 0
                        score = 0
                        game_active = True
                if event.key == pygame.K_q or event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

        if game_active:
            # Update bird
            bird.update()

            # Pipe spawning logic (randomly spaced)
            pipe_timer += 1
            if pipe_timer > random.randint(60, 120):
                pipes.append(Pipe(SCREEN_WIDTH))
                pipe_timer = 0

            # Update pipes
            for pipe in pipes[:]:
                pipe.update()
                if pipe.x + pipe.width < 0:
                    pipes.remove(pipe)
                
                # Score increment if passed pipes
                if not pipe.passed and pipe.x + pipe.width < bird.x:
                    score += 1
                    pipe.passed = True

            # Collision Detection
            bird_rect = bird.get_rect()
            # Hit land?
            if bird.y + 30 >= SCREEN_HEIGHT - 50:
                game_active = False
            
            for pipe in pipes:
                top_r, bottom_r = pipe.get_rects()
                if bird_rect.colliderect(top_r) or bird_rect.colliderect(bottom_r):
                    game_active = False

            # Out of bounds (top)
            if bird.y < 0:
                game_active = False

        # --- DRAWING ---
        screen.fill(bg_color)

        for pipe in pipes:
            pipe.draw(screen)

        # Draw land
        pygame.draw.rect(screen, land_color, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))

        bird.draw(screen)

        # Score on top right side
        score_surface = font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_surface, (SCREEN_WIDTH - score_surface.get_width() - 10, 10))

        if not game_active:
            if score > high_score:
                high_score = score
            
            # Show best score inside the screen
            msg = large_font.render("GAME OVER", True, (255, 0, 0))
            high_msg = font.render(f"Best Score: {high_score}", True, (0, 0, 0))
            restart_msg = font.render("Press SPACE to Restart", True, (0, 0, 0))
            quit_msg = font.render("Press Q or ESC to Quit", True, (0, 0, 0))

            screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 3))
            screen.blit(high_msg, (SCREEN_WIDTH // 2 - high_msg.get_width() // 2, SCREEN_HEIGHT // 3 + 50))
            screen.blit(restart_msg, (SCREEN_WIDTH // 2 - restart_msg.get_width() // 2, SCREEN_HEIGHT // 2))
            screen.blit(quit_msg, (SCREEN_WIDTH // 2 - quit_msg.get_width() // 2, SCREEN_HEIGHT // 2 + 30))

        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    main()

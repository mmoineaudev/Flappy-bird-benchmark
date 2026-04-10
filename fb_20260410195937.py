import pygame
import random
import sys

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Flappy Bird")

# Colors
def get_random_light_color():
    return (random.randint(200, 255), random.randint(200, 255), random.randint(200, 255))

def get_random_dark_color():
    return (random.randint(0, 100), random.randint(0, 100), random.randint(0, 100))

BACKGROUND_COLOR = (173, 216, 230)  # Initial light blue
LAND_COLORS = [(101, 67, 33), (255, 255, 0)]  # Dark brown or yellow
PIPE_COLORS = [(0, 100, 0), (139, 69, 19), (64, 64, 64)]  # Dark green, light brown, dark gray

# Game Constants
GRAVITY = 0.25
FLAP_STRENGTH = -6
PIPE_SPEED = 3
PIPE_GAP = 150
PIPE_FREQUENCY = 1500 # milliseconds

class Bird:
    def __init__(self):
        self.x = 50
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.size = 30
        self.shape = random.choice(['square', 'circle', 'triangle'])
        self.color = get_random_dark_color()

    def flap(self):
        self.velocity = FLAP_STRENGTH

    def update(self):
        self.velocity += GRAVITY
        self.y += self.velocity

    def draw(self, surface):
        if self.shape == 'square':
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.size, self.size))
        elif self.shape == 'circle':
            pygame.draw.circle(surface, self.color, (self.x + self.size // 2, self.y + self.size // 2), self.size // 2)
        elif self.shape == 'triangle':
            points = [
                (self.x + self.size // 2, self.y),
                (self.x, self.y + self.size),
                (self.x + self.size, self.y + self.size)
            ]
            pygame.draw.polygon(surface, self.color, points)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.size, self.size)

class Pipe:
    def __init__(self, x):
        self.x = x
        self.width = 50
        self.gap_y = random.randint(100, SCREEN_HEIGHT - 250)
        self.color = random.choice(PIPE_COLORS)
        self.passed = False

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self, surface):
        # Top pipe
        pygame.draw.rect(surface, self.color, (self.x, 0, self.width, self.gap_y))
        # Bottom pipe
        pygame.draw.rect(surface, self.color, (self.x, self.gap_y + PIPE_GAP, self.width, SCREEN_HEIGHT))

    def get_rects(self):
        top_rect = pygame.Rect(self.x, 0, self.width, self.gap_y)
        bottom_rect = pygame.Rect(self.x, self.gap_y + PIPE_GAP, self.width, SCREEN_HEIGHT)
        return top_rect, bottom_rect

def main():
    global BACKGROUND_COLOR
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 32)
    big_font = pygame.font.SysFont("Arial", 48)

    best_score = 0
    
    def reset_game():
        global BACKGROUND_COLOR
        BACKGROUND_COLOR = get_random_light_color()
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
            if bird.y < 0 or bird.y + bird.size > SCREEN_HEIGHT - 50: # 50 is land height
                game_over = True
            
            # Check if collision with land (though bird.y check covers most)
            if bird.y + bird.size >= SCREEN_HEIGHT - 50:
                game_over = True

            if game_over:
                if score > best_score:
                    best_score = score

        # Draw everything
        screen.fill(BACKGROUND_COLOR)
        
        for pipe in pipes:
            pipe.draw(screen)

        bird.draw(screen)

        # Draw Land
        pygame.draw.rect(screen, land_color, (0, SCREEN_HEIGHT - 50, SCREEN_WIDTH, 50))

        # Draw Score
        score_text = font.render(f"Score: {score}", True, (0, 0, 0))
        screen.blit(score_text, (SCREEN_WIDTH - 120, 20))

        if game_over:
            over_text = big_font.render("GAME OVER", True, (255, 0, 0))
            best_text = font.render(f"Best Score: {best_score}", True, (0, 0, 0))
            restart_text = font.render("Press SPACE to Restart", True, (0, 0, 0))
            quit_text = font.render("Press Q or ESC to Quit", True, (0, 0, 0))
            
            screen.blit(over_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 3))
            screen.blit(best_text, (SCREEN_WIDTH // 2 - 70, SCREEN_HEIGHT // 3 + 50))
            screen.blit(restart_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2))
            screen.blit(quit_text, (SCREEN_WIDTH // 2 - 120, SCREEN_HEIGHT // 2 + 40))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

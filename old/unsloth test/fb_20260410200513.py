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

# Colors
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

class Bird:
    def __init__(self):
        self.x = 100
        self.y = SCREEN_HEIGHT // 2
        self.velocity = 0
        self.shape = random.choice(['square', 'circle', 'triangle'])
        self.color = random.choice(DARK_COLORS)
        self.size = 30
        
    def draw(self):
        if self.shape == 'square':
            pygame.draw.rect(screen, self.color, (self.x - self.size//2, self.y - self.size//2, self.size, self.size))
        elif self.shape == 'circle':
            pygame.draw.circle(screen, self.color, (self.x, self.y), self.size//2)
        elif self.shape == 'triangle':
            points = [
                (self.x, self.y - self.size//2),
                (self.x - self.size//2, self.y + self.size//2),
                (self.x + self.size//2, self.y + self.size//2)
            ]
            pygame.draw.polygon(screen, self.color, points)
            
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
        self.color = random.choice([DARK_GREEN, LIGHT_BROWN, DARK_GRAY])
        self.passed = False
        
    def draw(self):
        # Top pipe
        pygame.draw.rect(screen, self.color, (self.x, 0, self.width, self.gap_y))
        # Bottom pipe
        pygame.draw.rect(screen, self.color, (self.x, self.gap_y + PIPE_GAP, self.width, SCREEN_HEIGHT - self.gap_y - PIPE_GAP))
        
    def update(self):
        self.x -= PIPE_SPEED
        
    def get_rects(self):
        top_rect = pygame.Rect(self.x, 0, self.width, self.gap_y)
        bottom_rect = pygame.Rect(self.x, self.gap_y + PIPE_GAP, self.width, SCREEN_HEIGHT - self.gap_y - PIPE_GAP)
        return top_rect, bottom_rect

class Ground:
    def __init__(self):
        self.color = random.choice([DARK_BROWN, YELLOW])
        self.y = SCREEN_HEIGHT - 50
        
    def draw(self):
        pygame.draw.rect(screen, self.color, (0, self.y, SCREEN_WIDTH, 50))

def check_collision(bird, pipes):
    bird_rect = pygame.Rect(bird.x - bird.size//2, bird.y - bird.size//2, bird.size, bird.size)
    
    # Check ground collision
    if bird.y + bird.size//2 >= SCREEN_HEIGHT - 50:
        return True
        
    for pipe in pipes:
        top_rect, bottom_rect = pipe.get_rects()
        if bird_rect.colliderect(top_rect) or bird_rect.colliderect(bottom_rect):
            return True
            
    return False

def main():
    # Random background color (light shade)
    bg_color = random.choice(LIGHT_COLORS)
    
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
        
        # Background color
        screen.fill(bg_color)
        
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
            score_text = font.render(f"Score: {score}", True, (0, 0, 0))
            screen.blit(score_text, (SCREEN_WIDTH - 150, 20))
        
        else:
            # Game over screen
            bird.draw()
            ground.draw()
            
            for pipe in pipes:
                pipe.draw()
            
            # Show best score in the center of the screen
            game_over_text = large_font.render("GAME OVER", True, (0, 0, 0))
            score_text = font.render(f"Score: {score}", True, (0, 0, 0))
            best_text = font.render(f"Best: {best_score}", True, (0, 0, 0))
            
            screen.blit(game_over_text, (SCREEN_WIDTH//2 - game_over_text.get_width()//2, SCREEN_HEIGHT//2 - 80))
            screen.blit(score_text, (SCREEN_WIDTH//2 - score_text.get_width()//2, SCREEN_HEIGHT//2 - 20))
            screen.blit(best_text, (SCREEN_WIDTH//2 - best_text.get_width()//2, SCREEN_HEIGHT//2 + 30))
            
            restart_text = font.render("Press SPACE to restart", True, (0, 0, 0))
            quit_text = font.render("Press Q or Esc to quit", True, (0, 0, 0))
            
            screen.blit(restart_text, (SCREEN_WIDTH//2 - restart_text.get_width()//2, SCREEN_HEIGHT//2 + 80))
            screen.blit(quit_text, (SCREEN_WIDTH//2 - quit_text.get_width()//2, SCREEN_HEIGHT//2 + 120))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

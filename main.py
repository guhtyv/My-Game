import pygame
import random

# Initialize Pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Mario Jumps Pipes")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)  # Ground color

# Mario class
class Mario:
    def __init__(self):
        self.x = 100
        self.y = SCREEN_HEIGHT - 100  # Starts on the ground
        self.velocity = 0
        self.gravity = 0.5
        self.jump_strength = -15  # Set to -15 for average jump height (balanced)
        self.on_ground = False
        self.image = pygame.image.load('mario.png')  # Replace with your sprite
        self.image = pygame.transform.scale(self.image, (50, 50))
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def jump(self):
        if self.on_ground:
            self.velocity = self.jump_strength
            self.on_ground = False

    def update(self, pipes, ground_height, camera_y):
        self.velocity += self.gravity
        self.y += self.velocity
        self.rect.center = (self.x, self.y)

        # Check collision with ground (ground at y = SCREEN_HEIGHT - ground_height + camera_y)
        ground_y = SCREEN_HEIGHT - ground_height + camera_y
        if self.y + self.rect.height // 2 >= ground_y:
            self.y = ground_y - self.rect.height // 2
            self.velocity = 0
            self.on_ground = True

        # Check collision with pipes
        for pipe in pipes:
            if pipe.collide(self):
                return True  # Game over on collision
        return False

    def draw(self, screen, camera_y):
        screen.blit(self.image, (self.rect.x, self.rect.y - camera_y))

# Pipe class (now as platforms with dangerous collision)
class Pipe:
    def __init__(self, x, height):
        self.x = x
        self.width = 80
        self.height = height
        self.color = GREEN
        self.rect = pygame.Rect(self.x, SCREEN_HEIGHT - height, self.width, self.height)

    def update(self):
        self.x -= 5  # Pipe movement speed
        self.rect.x = self.x

    def draw(self, screen, camera_y):
        pygame.draw.rect(screen, self.color, (self.rect.x, self.rect.y - camera_y, self.rect.width, self.rect.height))

    def collide(self, mario):
        if mario.rect.colliderect(self.rect):
            # If Mario is falling and only touches the top (landing), it's okay
            # Increased buffer from 10 to 30 for more lenient landing
            if mario.velocity > 0 and mario.rect.bottom <= self.rect.top + 30:
                mario.y = self.rect.top - mario.rect.height // 2
                mario.velocity = 0
                mario.on_ground = True
                return False  # Not game over
            else:
                return True  # Game over on touching sides or bottom
        return False

# Main game function
def main():
    clock = pygame.time.Clock()
    mario = Mario()
    pipes = []
    score = 0
    ground_height = 50  # Ground height
    font = pygame.font.SysFont(None, 36)
    current_height = 100  # Initial pipe height
    camera_y = 0  # Camera offset
    camera_active = False  # Camera not following at start

    running = True
    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    mario.jump()
                    # Removed camera activation on first jump

        # Update camera: follows Mario only after activation (now after score >= 10)
        if camera_active:
            camera_y = max(0, mario.y - SCREEN_HEIGHT // 2)

        # Update Mario
        if mario.update(pipes, ground_height, camera_y):
            running = False  # Game over on collision

        # Generate pipes (reduced distance to 250 pixels between end of one and start of next for closer pipes)
        if not pipes or pipes[-1].x + pipes[-1].width + 250 <= SCREEN_WIDTH:
            pipes.append(Pipe(SCREEN_WIDTH, current_height))
            current_height += 30  # Height gradually increases by 30 pixels
            # Removed the cap: pipes will keep getting taller indefinitely

        # Update and draw pipes
        for pipe in pipes[:]:
            pipe.update()
            pipe.draw(screen, camera_y)
            if pipe.x + pipe.width < 0:
                pipes.remove(pipe)
                score += 1
                # Activate camera only after score reaches 10
                if score >= 10:
                    camera_active = True

        # Draw ground (ground always visible, but camera rises)
        ground_y = SCREEN_HEIGHT - ground_height - camera_y
        if ground_y < SCREEN_HEIGHT:  # Draw only if ground is visible
            pygame.draw.rect(screen, BROWN, (0, ground_y, SCREEN_WIDTH, ground_height))

        # Draw Mario
        mario.draw(screen, camera_y)

        # Display score
        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    # Game over screen
    screen.fill(BLACK)
    game_over_text = font.render("Game Over! Press R to Restart", True, WHITE)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                waiting = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    return True  # Signal to restart instead of recursive call

    return False  # Signal to quit

if __name__ == "__main__":
    while True:
        if not main():
            break
    pygame.quit()
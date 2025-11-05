import pygame
import os
import random

pygame.init()
pygame.mixer.init()


SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT,))
pygame.display.set_caption("Mario pipes adventure")

WHITE = (0, 150, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BROWN = (139, 69, 19)
RED = (255, 0, 0)

try:
    jump_sound = pygame.mixer.Sound('jump.wav')
except:
    jump_sound = None

def main():
    try:
        pygame.mixer.music.load('background.mp3')
        pygame.mixer.music.play(-1)
    except:
        pass

    clock = pygame.time.Clock()
    mario = Mario()
    pipes = []
    score = 0
    ground_height = 50
    font = pygame.font.SysFont(None, 36)
    camera_y = 0
    camera_active = False
    pipe_count = 0
    last_height = 0

    running = True
    while running:
        screen.fill(WHITE)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    mario.jump()
                if event.key == pygame.K_q:
                    running = False
            if event.type == pygame.KEYUP:
                if event.key in (pygame.K_a, pygame.K_d):
                    mario.stop_horizontal()

        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]:
            mario.move_left()
        if keys[pygame.K_d]:
            mario.move_right()

        if camera_active:
            camera_y = max(0, mario.y - SCREEN_HEIGHT // 2)

        if mario.update(pipes, ground_height, camera_y):
            running = False

        if not pipes or pipes[-1].x + pipes[-1].width + 250 <= SCREEN_WIDTH:
            pipe_count += 1
            if pipe_count <= 3:
                ladder_heights = [100, 200, 300]
                height = ladder_heights[pipe_count - 1]
                last_height = height
            else:
                min_height = max(100, last_height - 100)
                max_height = min(SCREEN_HEIGHT - 100, last_height + 100)
                height = random.randint(min_height, max_height)
                last_height = height
            pipes.append(Pipe(SCREEN_WIDTH, height))

        for pipe in pipes[:]:
            pipe.update()
            pipe.draw(screen, camera_y)
            if pipe.x + pipe.width < 0:
                pipes.remove(pipe)
                score += 1
                if score >= 10:
                    camera_active = True

        ground_y = SCREEN_HEIGHT - ground_height - camera_y
        if ground_y < SCREEN_HEIGHT:
            pygame.draw.rect(screen, BROWN, (0, ground_y, SCREEN_WIDTH, ground_height))

        mario.draw(screen, camera_y)

        score_text = font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_text, (10, 10))

        pygame.display.flip()
        clock.tick(60)

    screen.fill(BLACK)
    game_over_text = font.render("Game Over! Press R to Restart or Q to Quit", True, WHITE)
    screen.blit(game_over_text, (SCREEN_WIDTH // 2 - 200, SCREEN_HEIGHT // 2))
    pygame.display.flip()

    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    pygame.mixer.music.stop()
                    mario.__init__()
                    pipes.clear()
                    score = 0
                    camera_y = 0
                    camera_active = False
                    pipe_count = 0
                    last_height = 0
                    return True
                if event.key == pygame.K_q:
                    return False
    return False

class Mario:
    def __init__(self):
        self.x = 100
        self.y = SCREEN_HEIGHT - 100
        self.velocity_x = 0
        self.velocity_y = 0
        self.gravity = 0.5
        self.jump_strength = -15
        self.move_speed = 5
        self.on_ground = False
        self.facing_right = True
        if os.path.exists('mario.png'):
            self.image = pygame.image.load('mario.png')
            self.image = pygame.transform.scale(self.image, (50, 50))
        else:
            self.image = pygame.Surface((50, 50))
            self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.rect.center = (self.x, self.y)

    def jump(self):
        if self.on_ground:
            self.velocity_y = self.jump_strength
            self.on_ground = False
            if jump_sound:
                jump_sound.play()

    def move_left(self):
        self.velocity_x = -self.move_speed
        self.facing_right = False

    def move_right(self):
        self.velocity_x = self.move_speed
        self.facing_right = True

    def stop_horizontal(self):
        self.velocity_x = 0

    def update(self, pipes, ground_height, camera_y):
        self.velocity_y += self.gravity
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.rect.width))
        self.rect.center = (self.x, self.y)

        ground_y = SCREEN_HEIGHT - ground_height + camera_y
        if self.y + self.rect.height // 2 >= ground_y:
            self.y = ground_y - self.rect.height // 2
            self.velocity_y = 0
            self.on_ground = True

        for pipe in pipes:
            if pipe.collide(self):
                return True
        return False

    def draw(self, screen, camera_y):
        screen.blit(self.image, (self.rect.x, self.rect.y - camera_y))

class Pipe:
    def __init__(self, x, height):
        self.x = x
        self.width = 80
        self.height = height
        self.color = GREEN
        self.rect = pygame.Rect(self.x, SCREEN_HEIGHT - height, self.width, self.height)

    def update(self):
        self.x -= 5
        self.rect.x = self.x

    def draw(self, screen, camera_y):
        pygame.draw.rect(screen, self.color, (self.rect.x, self.rect.y - camera_y, self.rect.width, self.rect.height))

    def collide(self, mario):
        if mario.rect.colliderect(self.rect):
            if mario.velocity_y > 0 and mario.rect.bottom <= self.rect.top + 20:
                mario.y = self.rect.top - mario.rect.height // 2
                mario.velocity_y = 0
                mario.on_ground = True
                return False
            else:
                return True
        return False

if __name__ == "__main__":
    while True:
        if not main():
            break
    pygame.quit()

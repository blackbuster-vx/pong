from pygame import *
from pygame.locals import *
from random import randint

WIN_WIDTH = 700
WIN_HEIGHT = 500
FPS = 60

img_platform = "platforming.png"
img_ball = "ball.png"

game = True
finish = False

mixer.init()
mixer.music.load("Original Tetris theme (Tetris Soundtrack).mp3")
mixer.music.set_volume(0.4)
mixer.music.play(-1)  # Loop music forever

bounce_sound = mixer.Sound("mixkit-basketball-ball-hard-hit-2093.wav")  # Make sure this file exists

window = display.set_mode((WIN_WIDTH, WIN_HEIGHT))
display.set_caption("Pong!")
clock = time.Clock()

font.init()
font1 = font.SysFont("Arial", 36)

score = 0
lives = 1 

class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__()
        self.image = transform.scale(image.load(player_image), (size_x, size_y))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x = player_x
        self.rect.y = player_y

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Platform(GameSprite):
    def update(self):
        keys = key.get_pressed()
        if keys[K_UP] and self.rect.y > 5:
            self.rect.y -= self.speed
        if keys[K_DOWN] and self.rect.y < WIN_HEIGHT - self.rect.height:
            self.rect.y += self.speed

class EnemyPlatform(GameSprite):
    def update(self, ball):
        if self.rect.centery < ball.rect.centery and self.rect.bottom < WIN_HEIGHT:
            self.rect.y += self.speed + 2.5
        elif self.rect.centery > ball.rect.centery and self.rect.top > 0:
            self.rect.y -= self.speed + 2.5

class Ball(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, speed_x, speed_y):
        super().__init__(player_image, player_x, player_y, size_x, size_y, 0)
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.last_speedup = 0

    def update(self):
        global lives, finish, score
        self.rect.x += self.speed_x
        self.rect.y += self.speed_y
        # Bounce off top/bottom
        if self.rect.top < 0 or self.rect.bottom > WIN_HEIGHT:
            self.speed_y *= -1
        # Out of bounds left or right
        if self.rect.left < 0 or self.rect.right > WIN_WIDTH:
            lives -= 1
            finish = True
        # Increase speed at thresholds (only once per threshold)
        for threshold, increment in [(10, 1), (20, 1), (30, 2), (40, 2), (50,3), (70,4)]:
            if score >= threshold and self.last_speedup < threshold:
                self.speed_x += 1 if self.speed_x > 0 else -1
                self.speed_y += 1 if self.speed_y > 0 else -1
                self.last_speedup = threshold

# Create sprites
player = Platform(img_platform, 10, WIN_HEIGHT // 2 - 50, 20, 100, 7)
enemy = EnemyPlatform(img_platform, WIN_WIDTH - 30, WIN_HEIGHT // 2 - 50, 20, 100, 7)
ball_sprite = Ball(img_ball, WIN_WIDTH // 2 - 20, WIN_HEIGHT // 2 - 20, 40, 40, 6, 6)  # Ball is now 40x40
balls = sprite.Group()
balls.add(ball_sprite)

def reset_game():
    global score, lives, finish, ball_sprite, balls
    score = 0
    lives = 1
    finish = False
    ball_sprite = Ball(img_ball, WIN_WIDTH // 2 - 20, WIN_HEIGHT // 2 - 20, 40, 40, 6, 6)  # Ball is now 40x40
    balls.empty()
    balls.add(ball_sprite)
    mixer.music.stop()
    mixer.music.play(-1)  # Restart and loop music

while game:
    for e in event.get():
        if e.type == QUIT:
            game = False
        elif e.type == KEYDOWN:
            if e.key == K_r and finish:
                reset_game()
                

    if not finish:
        window.fill((255, 255, 255))

        # Draw vertical bar in the middle
        draw.line(window, (200, 200, 200), (WIN_WIDTH // 2, 0), (WIN_WIDTH // 2, WIN_HEIGHT), 5)

        player.update()
        player.reset()

        enemy.update(ball_sprite)
        enemy.reset()

        balls.update()
        balls.draw(window)

        # Ball collision with player
        if sprite.spritecollide(player, balls, False):
            ball_sprite.speed_x *= -1
            score += 1
            ball_sprite.rect.x = player.rect.right + 1
            bounce_sound.play()

        # Ball collision with enemy
        if sprite.spritecollide(enemy, balls, False):
            ball_sprite.speed_x *= -1
            score += 1
            ball_sprite.rect.x = enemy.rect.left - ball_sprite.rect.width - 1
            bounce_sound.play()

        if lives <= 0:
            finish = True

        text_score = font1.render(f"Score: {score}", True, (50, 50, 255))
        text_lives = font1.render(f"Lives: {lives}", True, (255, 50, 50))
        window.blit(text_score, (10, 10))
        window.blit(text_lives, (10, 50))

    else:
        game_over_text = font1.render("GAME OVER! Press R to restart", True, (255, 0, 0))
        final_score = font1.render(f"Final Score: {score}", True, (255, 255, 255))
        window.blit(game_over_text, (140, 200))
        window.blit(final_score, (250, 250))

    display.update()
    clock.tick(FPS)
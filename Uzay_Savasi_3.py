import pygame
import random
import os

# Renk tanımlamaları
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)

# Pygame başlat
pygame.init()

# Ekran ayarları
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Uzay Savaşları")

# Resim yolu
current_dir = os.path.dirname(os.path.abspath(__file__))
image_path = os.path.join(current_dir, "assets", "uzay_gemisi.png")


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        try:
            self.image = pygame.image.load(image_path).convert_alpha()
        except pygame.error as e:
            print(f"Resim yüklenemedi: {e}")
            self.image = pygame.Surface((50, 30))
            self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.speed = 5
        self.can = 3

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((5, 10))
        self.image.fill(RED)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -8

    def update(self):
        self.rect.y += self.speed
        if self.rect.bottom < 0:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((30, 30))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect(center=(random.randint(30, WIDTH - 30), 0))
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()
            pygame.event.post(pygame.event.Event(pygame.USEREVENT + 2))


# Gruplar ve global değişkenler
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
score = 0  # ✅ Score burada tanımlandı!

# Yazı tipi
font = pygame.font.Font(None, 36)
game_over_font = pygame.font.Font(None, 72)

# Oyun döngüsü
clock = pygame.time.Clock()
running = True
game_over = False
ENEMY_SPAWN = pygame.USEREVENT + 1
pygame.time.set_timer(ENEMY_SPAWN, 1000)

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                bullet = Bullet(player.rect.centerx, player.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)

        elif event.type == ENEMY_SPAWN and not game_over:
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies.add(enemy)

        elif event.type == pygame.USEREVENT + 2 and not game_over:
            player.can -= 1
            if player.can <= 0:
                game_over = True

    if not game_over:
        # Çarpışma kontrolü ve puan artışı
        for bullet in bullets:
            hits = pygame.sprite.spritecollide(bullet, enemies, True)
            for hit in hits:
                bullet.kill()
                score += 10  # ✅ Score burada güncelleniyor

        all_sprites.update()

    screen.fill(BLACK)
    all_sprites.draw(screen)

    # Bilgi paneli
    if not game_over:
        puan_text = font.render(f"Puan: {score}", True, WHITE)
        can_text = font.render(f"Can: {player.can}", True, RED)
        screen.blit(puan_text, (10, 10))
        screen.blit(can_text, (WIDTH - 120, 10))
    else:
        game_over_text = game_over_font.render("GAME OVER", True, RED)
        restart_text = font.render("Yeniden başlamak için R'ye basın", True, WHITE)
        screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2 - 50))
        screen.blit(restart_text, (WIDTH // 2 - 180, HEIGHT // 2 + 50))

    pygame.display.flip()

    if game_over:
        keys = pygame.key.get_pressed()
        if keys[pygame.K_r]:
            # Tüm değişkenleri ve grupları sıfırla
            player.can = 3
            score = 0
            game_over = False
            enemies.empty()
            bullets.empty()
            all_sprites.empty()
            all_sprites.add(player)

pygame.quit()
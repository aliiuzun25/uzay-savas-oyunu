import pygame
import random  # ✅ Random modülü eklendi
import os

# Renk tanımlamaları (BÜYÜK HARF ile)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)  # ✅ RED tanımlandı

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
            self.image.fill(WHITE) # ✅ WHITE artık tanımlı
        self.rect = self.image.get_rect(center=(WIDTH//2, HEIGHT-50))

# ... (Diğer sınıflar ve oyun döngüsü aynı kalacak) ...

        # ... (Oyun döngüsü ve diğer kodlar aynı kalacak) ...
        self.speed = 5

    # ... (Önceki kodun geri kalanı aynı kalacak) ...

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


# Gruplar
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()

player = Player()
all_sprites.add(player)

# Puan
score = 0
font = pygame.font.Font(None, 36)

# Oyun döngüsü
clock = pygame.time.Clock()
running = True
ENEMY_SPAWN = pygame.USEREVENT + 1
pygame.time.set_timer(ENEMY_SPAWN, 1000)

while running:
    clock.tick(60)

    # Olay kontrolü
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                bullet = Bullet(player.rect.centerx, player.rect.top)
                all_sprites.add(bullet)
                bullets.add(bullet)
        elif event.type == ENEMY_SPAWN:
            enemy = Enemy()
            all_sprites.add(enemy)
            enemies.add(enemy)

    # Çarpışma kontrolü
    for bullet in bullets:
        hits = pygame.sprite.spritecollide(bullet, enemies, True)
        for hit in hits:
            bullet.kill()
            score += 10

    # Güncellemeler
    all_sprites.update()

    # Çizimler
    screen.fill(BLACK)
    all_sprites.draw(screen)

    # Puanı göster
    text = font.render(f"Puan: {score}", True, WHITE)
    screen.blit(text, (10, 10))

    pygame.display.flip()

pygame.quit()
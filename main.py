import pygame
import random
import os
import json
from datetime import datetime

# Pygame başlat
pygame.init()
pygame.mixer.init()

# Ekran ayarları
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Uzay Savaşları")

# Renkler
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (128, 0, 128)

# Assets klasör yapısı
ASSETS_DIR = "assets"
SOUNDS_DIR = os.path.join(ASSETS_DIR, "sounds")
os.makedirs(SOUNDS_DIR, exist_ok=True)


# Ses dosyaları için varsayılan fonksiyon
def create_silent_sound():
    sound = pygame.mixer.Sound(buffer=bytearray(44))
    sound.set_volume(0)
    return sound


# Ses dosyalarını yükle
try:
    shoot_sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "shoot.wav"))
    explosion_sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "explosion.wav"))
    bonus_sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "bonus.wav"))
    game_over_sound = pygame.mixer.Sound(os.path.join(SOUNDS_DIR, "game_over.wav"))
except:
    print("Ses dosyaları bulunamadı! Sessiz modda çalışılıyor.")
    shoot_sound = create_silent_sound()
    explosion_sound = create_silent_sound()
    bonus_sound = create_silent_sound()
    game_over_sound = create_silent_sound()


# Resim yükleme fonksiyonu
def load_image(name, scale=1):
    try:
        path = os.path.join(ASSETS_DIR, name)
        image = pygame.image.load(path).convert_alpha()
        if scale != 1:
            size = image.get_size()
            image = pygame.transform.scale(image, (int(size[0] * scale), int(size[1] * scale)))
        return image
    except:
        # Varsayılan resimler
        size = (50, 50)
        surf = pygame.Surface(size, pygame.SRCALPHA)
        if "player" in name:
            pygame.draw.polygon(surf, GREEN, [(25, 0), (0, 50), (50, 50)])
        elif "enemy" in name or "fast_enemy" in name:
            color = RED if "enemy" in name else PURPLE
            pygame.draw.polygon(surf, color, [(0, 0), (50, 0), (25, 50)])
            if "fast_enemy" in name:
                pygame.draw.line(surf, YELLOW, (10, 40), (40, 40), 3)
        elif "heart" in name:
            surf = pygame.Surface((30, 30), pygame.SRCALPHA)
            pygame.draw.polygon(surf, RED, [(15, 0), (0, 10), (0, 20), (15, 30), (30, 20), (30, 10)])
        return surf


# Oyuncu adı alma fonksiyonu (DÜZELTME: Fonksiyon tanımını başa aldık)
def get_player_name():
    name = ""
    input_active = True
    font = pygame.font.Font(None, 36)

    while input_active:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ""
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name:
                    return name
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isalnum():
                    name += event.unicode

        screen.fill(BLACK)
        title = font.render("İsminizi girin (ENTER ile devam):", True, WHITE)
        name_text = font.render(name, True, GREEN)
        screen.blit(title, (WIDTH // 2 - 150, HEIGHT // 2 - 20))
        screen.blit(name_text, (WIDTH // 2 - 50, HEIGHT // 2 + 20))
        pygame.display.flip()
    return name


# Skor sistem fonksiyonları
def load_scores():
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE, "r") as f:
            return json.load(f)
    return []


def save_scores(scores):
    with open(SCORE_FILE, "w") as f:
        json.dump(scores, f)


# Oyun sınıfları
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = load_image("player.png", 0.5)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.speed = 5
        self.can = 5
        self.fire_mode = "single"
        self.bonus_time = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

        if self.fire_mode != "single" and pygame.time.get_ticks() > self.bonus_time:
            self.fire_mode = "single"

    def shoot(self):
        shoot_sound.play()
        bullets = []
        if self.fire_mode == "single":
            bullets.append(Bullet(self.rect.centerx, self.rect.top))
        elif self.fire_mode == "triple":
            bullets.append(Bullet(self.rect.centerx - 15, self.rect.top, angle=20))
            bullets.append(Bullet(self.rect.centerx, self.rect.top))
            bullets.append(Bullet(self.rect.centerx + 15, self.rect.top, angle=-20))
        elif self.fire_mode == "five":
            bullets.append(Bullet(self.rect.left + 10, self.rect.top, angle=30))
            bullets.append(Bullet(self.rect.left + 25, self.rect.top, angle=15))
            bullets.append(Bullet(self.rect.centerx, self.rect.top))
            bullets.append(Bullet(self.rect.right - 25, self.rect.top, angle=-15))
            bullets.append(Bullet(self.rect.right - 10, self.rect.top, angle=-30))
        return bullets

    def activate_bonus(self, bonus_type):
        bonus_sound.play()
        if bonus_type == "triple":
            self.fire_mode = "triple"
            self.bonus_time = pygame.time.get_ticks() + 10000
        elif bonus_type == "five":
            self.fire_mode = "five"
            self.bonus_time = pygame.time.get_ticks() + 8000


class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle=0):
        super().__init__()
        self.image = pygame.Surface((8, 20), pygame.SRCALPHA)
        self.image.fill(GREEN)
        if angle != 0:
            self.image = pygame.transform.rotate(self.image, angle)
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = -8
        self.angle = angle

    def update(self):
        self.rect.y += self.speed
        if self.angle != 0:
            self.rect.x += self.angle * 0.5
        if self.rect.bottom < 0:
            self.kill()


class Enemy(pygame.sprite.Sprite):
    def __init__(self, fast=False):
        super().__init__()
        self.fast = fast
        image_name = "fast_enemy.png" if fast else "enemy.png"
        self.original_image = load_image(image_name, 0.1)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(random.randint(30, WIDTH - 30), 0))
        self.speed = random.randint(3, 7) if fast else random.randint(2, 5)

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()
            pygame.event.post(pygame.event.Event(pygame.USEREVENT + 2))


class Bonus(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.types = ["triple", "five"]
        self.type = random.choice(self.types)
        color = BLUE if self.type == "triple" else YELLOW
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (15, 15), 15)
        pygame.draw.circle(self.image, WHITE, (15, 15), 10, 2)

        if self.type == "triple":
            pygame.draw.line(self.image, WHITE, (5, 20), (15, 10), 2)
            pygame.draw.line(self.image, WHITE, (15, 10), (15, 20), 2)
            pygame.draw.line(self.image, WHITE, (15, 10), (25, 20), 2)
        else:
            pygame.draw.line(self.image, WHITE, (5, 20), (10, 10), 2)
            pygame.draw.line(self.image, WHITE, (10, 10), (15, 20), 2)
            pygame.draw.line(self.image, WHITE, (15, 10), (20, 20), 2)
            pygame.draw.line(self.image, WHITE, (20, 10), (25, 20), 2)

        self.rect = self.image.get_rect(center=(random.randint(30, WIDTH - 30), 0))
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class Heart:
    def __init__(self, x, y):
        self.image = load_image("heart.png")
        self.rect = self.image.get_rect(topleft=(x, y))


# Skor dosyası yolu (DÜZELTME: Fonksiyonlardan önce tanımlandı)
SCORE_FILE = os.path.join(ASSETS_DIR, "highscores.json")

# Oyun başlatma
player_name = get_player_name()
if not player_name:
    pygame.quit()
    exit()

# Oyun hazırlığı
all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bonuses = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
score = 0
highscores = load_scores()
hearts = [Heart(10 + i * 35, 10) for i in range(player.can)]

# Yazı tipleri
font = pygame.font.Font(None, 36)
game_over_font = pygame.font.Font(None, 72)
score_font = pygame.font.Font(None, 28)

# Oyun döngüsü
clock = pygame.time.Clock()
running = True
game_over = False
ENEMY_SPAWN = pygame.USEREVENT + 1
FAST_ENEMY_SPAWN = pygame.USEREVENT + 4
BONUS_SPAWN = pygame.USEREVENT + 3
pygame.time.set_timer(ENEMY_SPAWN, 1000)
pygame.time.set_timer(FAST_ENEMY_SPAWN, 3000)
pygame.time.set_timer(BONUS_SPAWN, 15000)

while running:
    clock.tick(60)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE and not game_over:
                for bullet in player.shoot():
                    all_sprites.add(bullet)
                    bullets.add(bullet)
            elif event.key == pygame.K_r and game_over:
                player.can = 5
                player.fire_mode = "single"
                hearts = [Heart(10 + i * 35, 10) for i in range(player.can)]
                score = 0
                game_over = False
                enemies.empty()
                bullets.empty()
                bonuses.empty()
                all_sprites.empty()
                all_sprites.add(player)

        elif event.type == ENEMY_SPAWN and not game_over:
            enemy = Enemy(fast=False)
            all_sprites.add(enemy)
            enemies.add(enemy)

        elif event.type == FAST_ENEMY_SPAWN and not game_over:
            enemy = Enemy(fast=True)
            all_sprites.add(enemy)
            enemies.add(enemy)

        elif event.type == BONUS_SPAWN and not game_over:
            bonus = Bonus()
            all_sprites.add(bonus)
            bonuses.add(bonus)

        elif event.type == pygame.USEREVENT + 2 and not game_over:
            player.can -= 1
            explosion_sound.play()
            if len(hearts) > 0:
                hearts.pop()
            if player.can <= 0:
                game_over = True
                game_over_sound.play()
                highscores.append({
                    "name": player_name,
                    "score": score,
                    "date": datetime.now().strftime("%d/%m/%Y %H:%M")
                })
                highscores.sort(key=lambda x: x["score"], reverse=True)
                highscores = highscores[:10]
                save_scores(highscores)

    if not game_over:
        for bullet in bullets:
            hits = pygame.sprite.spritecollide(bullet, enemies, True)
            for hit in hits:
                bullet.kill()
                explosion_sound.play()
                score += 20 if hit.fast else 10

        bonus_hits = pygame.sprite.spritecollide(player, bonuses, True)
        for bonus in bonus_hits:
            player.activate_bonus(bonus.type)
            score += 20

        all_sprites.update()

    # Çizimler
    screen.fill(BLACK)
    all_sprites.draw(screen)

    for heart in hearts:
        screen.blit(heart.image, heart.rect)

    puan_text = font.render(f"Puan: {score}", True, WHITE)
    fire_text = font.render(f"Atış: {player.fire_mode}", True, GREEN if player.fire_mode != "single" else WHITE)
    screen.blit(puan_text, (WIDTH - 150, 10))
    screen.blit(fire_text, (WIDTH - 150, 40))

    if game_over:
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        screen.blit(overlay, (0, 0))

        game_over_text = game_over_font.render("GAME OVER", True, RED)
        score_text = font.render(f"Skor: {score}", True, WHITE)
        restart_text = font.render("Yeniden başlamak için R'ye basın", True, WHITE)

        screen.blit(game_over_text, (WIDTH // 2 - 150, HEIGHT // 2 - 100))
        screen.blit(score_text, (WIDTH // 2 - 50, HEIGHT // 2))
        screen.blit(restart_text, (WIDTH // 2 - 180, HEIGHT // 2 + 50))

        y_pos = HEIGHT // 2 + 100
        title = score_font.render("En İyi Skorlar:", True, GREEN)
        screen.blit(title, (WIDTH // 2 - 80, y_pos))

        for i, record in enumerate(highscores[:5]):
            record_text = score_font.render(
                f"{i + 1}. {record['name']}: {record['score']} ({record['date']})",
                True, WHITE
            )
            screen.blit(record_text, (WIDTH // 2 - 150, y_pos + 30 + i * 30))

    pygame.display.flip()

pygame.quit()
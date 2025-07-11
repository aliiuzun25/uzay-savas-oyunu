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


def create_silent_sound():
    sound = pygame.mixer.Sound(buffer=bytearray(44))
    sound.set_volume(0)
    return sound


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


def load_image(name, scale=0.1):
    try:
        path = os.path.join(ASSETS_DIR, name)
        image = pygame.image.load(path).convert_alpha()
        if scale != 1:
            size = image.get_size()
            image = pygame.transform.scale(image, (int(size[0] * scale), int(size[1] * scale)))
        return image
    except:
        size = (30, 30)
        surf = pygame.Surface(size, pygame.SRCALPHA)
        if "player" in name:
            pygame.draw.polygon(surf, GREEN, [(15, 0), (0, 30), (30, 30)])
        elif "enemy" in name or "enemy2" in name:
            color = RED if "enemy" in name else PURPLE
            pygame.draw.polygon(surf, color, [(0, 0), (30, 0), (15, 30)])
            if "enemy2" in name:
                pygame.draw.line(surf, YELLOW, (5, 25), (25, 25), 2)
        elif "heart" in name:
            surf = pygame.Surface((40, 40), pygame.SRCALPHA)
            pygame.draw.polygon(surf, RED, [(20, 0), (0, 15), (0, 25), (20, 40), (40, 25), (40, 15)])
        return surf


def get_player_name():
    name = "#Oyuncu 1"
    input_active = True
    font = pygame.font.Font(None, 36)
    input_rect = pygame.Rect(WIDTH // 2 - 50, HEIGHT // 2 + 20, 200, 32)

    while input_active:
        mouse_pos = pygame.mouse.get_pos()
        mouse_click = pygame.mouse.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return ""
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return name if name.strip() else "#Oyuncu 1"
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif event.unicode.isalnum() or event.unicode.isspace():
                    if len(name) < 15:
                        name += event.unicode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(mouse_pos):
                    name = ""

        screen.fill(BLACK)
        pygame.draw.rect(screen, WHITE, input_rect, 2)
        title = font.render("İsminizi girin (ENTER ile devam):", True, WHITE)
        name_text = font.render(name, True, GREEN if name != "#Oyuncu 1" else (150, 150, 150))
        screen.blit(title, (WIDTH // 2 - 150, HEIGHT // 2 - 20))
        screen.blit(name_text, (input_rect.x + 5, input_rect.y + 5))
        pygame.display.flip()

    return name if name.strip() else "#Oyuncu 1"


def load_scores():
    if os.path.exists(SCORE_FILE):
        with open(SCORE_FILE, "r") as f:
            return json.load(f)
    return []


def save_scores(scores):
    with open(SCORE_FILE, "w") as f:
        json.dump(scores, f)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.original_image = load_image("player.png", 0.3)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(WIDTH // 2, HEIGHT - 50))
        self.speed = 5
        self.can = 5
        self.fire_mode = "single"
        self.bonus_end_time = 0

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and self.rect.left > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.right < WIDTH:
            self.rect.x += self.speed

        if self.fire_mode != "single" and pygame.time.get_ticks() > self.bonus_end_time:
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
            self.bonus_end_time = pygame.time.get_ticks() + 8000
        elif bonus_type == "five":
            self.fire_mode = "five"
            self.bonus_end_time = pygame.time.get_ticks() + 15000

#Arkaplan yanıp sönen yıldızlar.
class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.randint(1, 3)
        self.color = (
            random.randint(200, 255),  # R
            random.randint(200, 255),  # G
            random.randint(200, 255)  # B
        )
        self.speed = random.uniform(0.05, 0.2)
        self.flicker_intensity = random.uniform(0.7, 1.3)

    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)

    def draw(self, surface):
        # Rastgele parlama efekti
        flicker = random.uniform(0.7, 1.3)
        r = min(255, int(self.color[0] * flicker))
        g = min(255, int(self.color[1] * flicker))
        b = min(255, int(self.color[2] * flicker))
        pygame.draw.circle(surface, (r, g, b), (int(self.x), int(self.y)), self.size)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, x, y, angle=0):
        super().__init__()
        self.image = pygame.Surface((5, 15), pygame.SRCALPHA)
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
        image_name = "enemy2.png" if fast else "enemy.png"
        self.original_image = load_image(image_name)
        self.image = self.original_image
        self.rect = self.image.get_rect(center=(random.randint(30, WIDTH - 30), 0))
        self.speed = random.randint(4, 8) if fast else random.randint(2, 5)

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
        self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (12, 12), 12)
        pygame.draw.circle(self.image, WHITE, (12, 12), 8, 1)

        if self.type == "triple":
            pygame.draw.line(self.image, WHITE, (3, 17), (12, 7), 1)
            pygame.draw.line(self.image, WHITE, (12, 7), (12, 17), 1)
            pygame.draw.line(self.image, WHITE, (12, 7), (21, 17), 1)
        else:
            pygame.draw.line(self.image, WHITE, (3, 17), (8, 7), 1)
            pygame.draw.line(self.image, WHITE, (8, 7), (12, 17), 1)
            pygame.draw.line(self.image, WHITE, (12, 7), (16, 17), 1)
            pygame.draw.line(self.image, WHITE, (16, 7), (21, 17), 1)

        self.rect = self.image.get_rect(center=(random.randint(30, WIDTH - 30), 0))
        self.speed = 3

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class Heart:
    def __init__(self, x, y):
        self.image = load_image("heart.png", scale=1.5)
        self.rect = self.image.get_rect(topleft=(x, y))


SCORE_FILE = os.path.join(ASSETS_DIR, "highscores.json")

player_name = get_player_name()
if not player_name:
    pygame.quit()
    exit()

all_sprites = pygame.sprite.Group()
bullets = pygame.sprite.Group()
enemies = pygame.sprite.Group()
bonuses = pygame.sprite.Group()
player = Player()
all_sprites.add(player)
score = 0
highscores = load_scores()
hearts = [Heart(10 + i * 55, 10) for i in range(player.can)]

# YILDIZLARI OLUŞTUR (200 adet)
stars = [Star() for _ in range(200)]  # <-- BU SATIRI EKLEYİN

font = pygame.font.Font(None, 36)
game_over_font = pygame.font.Font(None, 72)
score_font = pygame.font.Font(None, 28)

clock = pygame.time.Clock()
running = True
game_over = False
ENEMY_SPAWN = pygame.USEREVENT + 1
FAST_ENEMY_SPAWN = pygame.USEREVENT + 4
BONUS_SPAWN = pygame.USEREVENT + 3
pygame.time.set_timer(ENEMY_SPAWN, 1000)
pygame.time.set_timer(FAST_ENEMY_SPAWN, 2500)
pygame.time.set_timer(BONUS_SPAWN, 7000)

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
                hearts = [Heart(10 + i * 30, 10) for i in range(player.can)]
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
                score += 25 if hit.fast else 10

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

    # Yıldızları çiz (arka plana)
    for star in stars:
        star.draw(screen)

    # Diğer çizimler (spritelar, metinler vb.)
    all_sprites.draw(screen)

    # Metinleri oluştur
    puan_text = font.render(f"Puan: {score}", True, WHITE)
    fire_text = font.render(f"Atış: {player.fire_mode}", True, GREEN if player.fire_mode != "single" else WHITE)

    # Sağa dayalı çizimler
    right_margin = WIDTH - 10

    # Puan (üst satır)
    screen.blit(puan_text, (right_margin - puan_text.get_width(), 10))

    # Atış modu (orta satır)
    screen.blit(fire_text, (right_margin - fire_text.get_width(), 40))

    # Sayaç (alt satır - sadece bonus aktifken)
    if player.fire_mode != "single":
        remaining_time = max(0, (player.bonus_end_time - pygame.time.get_ticks()) // 1000)
        timer_text = font.render(f"Atış Zamanı: {remaining_time}s", True, YELLOW)
        screen.blit(timer_text, (right_margin - timer_text.get_width(), 70))

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
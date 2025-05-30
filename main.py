import pygame
import random
import os

pygame.init()
pygame.mixer.init()

# إعداد الشاشة
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("🚀")

# الألوان
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GRAY = (100, 100, 100)
YELLOW = (255, 255, 0)

# تحميل الأصوات
explosion_sound = pygame.mixer.Sound("assets/impactPlate_medium_003.ogg")
powerup_sound = pygame.mixer.Sound("assets/powerup.ogg")

# تحميل الخلفيات
backgrounds = [
    pygame.image.load("assets/background1.jpg").convert(),
    pygame.image.load("assets/background3.jpg").convert(),
    pygame.image.load("assets/background2.jpg").convert(),
]
for i in range(len(backgrounds)):
    backgrounds[i] = pygame.transform.scale(backgrounds[i], (WIDTH, HEIGHT))

# تحميل صور الأنيميشن (3 صور للشخصية)
player_frames = [
    pygame.image.load("assets/character_purple_climb_a.png").convert_alpha(),
    pygame.image.load("assets/character_purple_front.png").convert_alpha(),
    pygame.image.load("assets/character_purple_hit.png").convert_alpha(),
]
for i in range(len(player_frames)):
    player_frames[i] = pygame.transform.scale(player_frames[i], (60, 60))
    player_frames[i] = pygame.transform.rotate(player_frames[i], 180)

# صور أخرى
explosion_img = pygame.image.load("assets/explosion.png").convert_alpha()
explosion_img = pygame.transform.scale(explosion_img, (60, 60))
shield_icon = pygame.Surface((20, 20), pygame.SRCALPHA)
pygame.draw.circle(shield_icon, WHITE, (10, 10), 10, 2)  # دائرة بيضاء شفافة للدرع
upgrade_icon = pygame.Surface((20, 20), pygame.SRCALPHA)
pygame.draw.rect(upgrade_icon, WHITE, (4, 4, 12, 12), 2)  # مربع أبيض للتطور

# قوالب
asteroid_img = pygame.Surface((40, 40), pygame.SRCALPHA)
pygame.draw.circle(asteroid_img, RED, (20, 20), 20)
bullet_img = pygame.Surface((10, 4))
bullet_img.fill(WHITE)

# إعدادات اللاعب
player_speed = 5
frame_index = 0
frame_delay = 5
frame_count = 0

score_font = pygame.font.SysFont(None, 36)
game_over_font = pygame.font.SysFont(None, 72)

# متغيرات Power-ups
shield_active = False
shield_timer = 0
weapon_upgrade = False
weapon_timer = 0

# أعلى نتيجة
high_score = 0
if os.path.exists("highscore.txt"):
    with open("highscore.txt", "r") as f:
        try:
            high_score = int(f.read())
        except:
            high_score = 0

def reset_game():
    global player_x, player_y, asteroids, bullets, asteroid_speed, spawn_delay, spawn_counter, score, level, game_over
    global shield_active, shield_timer, weapon_upgrade, weapon_timer
    player_x = WIDTH // 2
    player_y = HEIGHT - 80
    asteroids = []
    bullets = []
    asteroid_speed = 5
    spawn_delay = 30
    spawn_counter = 0
    score = 0
    level = 1
    game_over = False
    shield_active = False
    shield_timer = 0
    weapon_upgrade = False
    weapon_timer = 0

def draw_button(rect, text, hover=False):
    color = GREEN if hover else GRAY
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, WHITE, rect, 2)
    btn_text = score_font.render(text, True, WHITE)
    text_rect = btn_text.get_rect(center=rect.center)
    screen.blit(btn_text, text_rect)

reset_game()
running = True
clock = pygame.time.Clock()

while running:
    clock.tick(60)

    bg_index = min((level - 1) // 3, len(backgrounds) - 1)
    screen.blit(backgrounds[bg_index], (0, 0))

    if not game_over:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if weapon_upgrade:
                    bullets.append([player_x + 10, player_y])
                    bullets.append([player_x + 40, player_y])
                else:
                    bullets.append([player_x + 25, player_y])

        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and player_x > 0:
            player_x -= player_speed
        if keys[pygame.K_RIGHT] and player_x < WIDTH - player_frames[0].get_width():
            player_x += player_speed

        frame_count += 1
        if frame_count >= frame_delay:
            frame_count = 0
            frame_index = (frame_index + 1) % len(player_frames)

        screen.blit(player_frames[frame_index], (player_x, player_y))

        spawn_counter += 1
        if spawn_counter >= spawn_delay:
            spawn_counter = 0
            x_pos = random.randint(0, WIDTH - 40)
            # spawn either asteroid or power-up
            if random.random() < 0.1:
                power_type = random.choice(["shield", "upgrade"])
                asteroids.append([x_pos, -40, power_type])  # power-up with type
            else:
                asteroids.append([x_pos, -40])  # regular asteroid

        # رسم وإدارة الطابات
        for asteroid in asteroids[:]:
            asteroid[1] += asteroid_speed

            # رسم حسب نوع الطابة
            if len(asteroid) == 2:
                # كويكب عادي
                screen.blit(asteroid_img, asteroid[:2])
            else:
                # طابة قوة - ترسم دائرة صفراء + أيكون داخلها
                pygame.draw.circle(screen, YELLOW, (asteroid[0] + 20, asteroid[1] + 20), 20)
                # ارسم الأيقونة داخل الدائرة
                if asteroid[2] == "shield":
                    screen.blit(shield_icon, (asteroid[0] + 10, asteroid[1] + 10))
                elif asteroid[2] == "upgrade":
                    screen.blit(upgrade_icon, (asteroid[0] + 10, asteroid[1] + 10))

            if asteroid[1] > HEIGHT:
                asteroids.remove(asteroid)

        for bullet in bullets[:]:
            bullet[1] -= 10
            screen.blit(bullet_img, bullet)
            if bullet[1] < -10:
                bullets.remove(bullet)

        # تصادم الرصاص مع الطابات والكويكبات
        for bullet in bullets[:]:
            bullet_rect = bullet_img.get_rect(topleft=(bullet[0], bullet[1]))
            for asteroid in asteroids[:]:
                asteroid_rect = pygame.Rect(asteroid[0], asteroid[1], 40, 40)
                if bullet_rect.colliderect(asteroid_rect):
                    if len(asteroid) == 3:
                        # إذا كانت طابة قوة، فقط حذفها وتشغيل صوت خاص
                        powerup_sound.play()
                    else:
                        explosion_sound.play()
                        score += 10
                    asteroids.remove(asteroid)
                    if bullet in bullets:
                        bullets.remove(bullet)
                    break

        # إدارة وقت الدرع والتطور (5 ثواني)
        if shield_active and pygame.time.get_ticks() - shield_timer > 5000:
            shield_active = False
        if weapon_upgrade and pygame.time.get_ticks() - weapon_timer > 5000:
            weapon_upgrade = False

        # تصادم اللاعب مع الطابات والكويكبات
        player_rect = player_frames[0].get_rect(topleft=(player_x, player_y))
        for asteroid in asteroids[:]:
            asteroid_rect = pygame.Rect(asteroid[0], asteroid[1], 40, 40)
            if player_rect.colliderect(asteroid_rect):
                if len(asteroid) == 3:
                    # طابة قوة - تفعل الدرع أو التطور بدون خسارة
                    if asteroid[2] == "shield":
                        shield_active = True
                        shield_timer = pygame.time.get_ticks()
                    elif asteroid[2] == "upgrade":
                        weapon_upgrade = True
                        weapon_timer = pygame.time.get_ticks()
                    powerup_sound.play()
                    asteroids.remove(asteroid)
                else:
                    # كويكب عادي - إذا درع نشط يتكسر الدرع، إذا لا خسارة
                    if shield_active:
                        shield_active = False
                        asteroids.remove(asteroid)
                    else:
                        explosion_sound.play()
                        screen.blit(explosion_img, (player_x, player_y))
                        pygame.display.update()
                        pygame.time.delay(500)
                        game_over = True
                    break

        if score >= level * 100:
            level += 1
            asteroid_speed += 1
            if spawn_delay > 10:
                spawn_delay -= 2

        score_text = score_font.render(f"Score: {score}  Level: {level}  High: {high_score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # عرض حالة الدرع أو التطور مع المؤقت
        if shield_active:
            remaining = max(0, 5 - (pygame.time.get_ticks() - shield_timer) // 1000)
            shield_text = score_font.render(f"Shield: {remaining}s", True, GREEN)
            screen.blit(shield_text, (10, 50))
        if weapon_upgrade:
            remaining = max(0, 5 - (pygame.time.get_ticks() - weapon_timer) // 1000)
            upgrade_text = score_font.render(f"Upgrade: {remaining}s", True, GREEN)
            screen.blit(upgrade_text, (10, 80))

    else:
        if score > high_score:
            high_score = score
            with open("highscore.txt", "w") as f:
                f.write(str(high_score))

        text = game_over_font.render("Game Over", True, RED)
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - 100))

        btn_width, btn_height = 200, 50
        btn_restart = pygame.Rect(WIDTH // 2 - btn_width - 20, HEIGHT // 2, btn_width, btn_height)
        btn_quit = pygame.Rect(WIDTH // 2 + 20, HEIGHT // 2, btn_width, btn_height)

        mouse_pos = pygame.mouse.get_pos()
        mouse_clicked = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_clicked = True

        draw_button(btn_restart, "Restart", btn_restart.collidepoint(mouse_pos))
        draw_button(btn_quit, "Quit", btn_quit.collidepoint(mouse_pos))

        if mouse_clicked:
            if btn_restart.collidepoint(mouse_pos):
                reset_game()
            elif btn_quit.collidepoint(mouse_pos):
                running = False

    pygame.display.flip()

pygame.quit()

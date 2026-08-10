# -*- coding: utf-8 -*-
"""
Gems and Meteors - Python Graphical (Pygame) Version
Created by Jules
Natively self-installs pygame, downloads assets from the remote server if missing,
supports Endless and Level Modes, active enemies, bullet systems, configurable spaceships,
local scoreboards, starry backgrounds, and particle explosions.
"""

import os
import sys
import time
import random
import urllib.request
import subprocess

# Self-install pygame if missing
try:
    import pygame
except ImportError:
    print("Installing Pygame library for graphical interface...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pygame"])
        import pygame
    except Exception as e:
        print(f"Could not automatically install pygame: {e}")
        print("Please install it manually using: pip install pygame")
        sys.exit(1)

# Ensure data and cache folders exist
os.makedirs("cache", exist_ok=True)
os.makedirs("data", exist_ok=True)

# Remote server configuration
URL_PREFIX = "http://markspi.ddns.me/game/sounds/"
ASSETS = {
    "music.mp3": "music.mp3",
    "boom.wav": "boom.wav",
    "damage.wav": "damage.wav",
    "gem.wav": "gem.wav",
    "heart.wav": "heart.wav"
}

def download_asset_if_missing(filename):
    filepath = os.path.join("cache", filename)
    if not os.path.exists(filepath):
        print(f"Downloading missing asset {filename} from server...")
        try:
            url = URL_PREFIX + filename
            urllib.request.urlretrieve(url, filepath)
            print(f"Successfully downloaded {filename}.")
        except Exception as e:
            print(f"Could not download {filename} from server (offline or server issues): {e}")

# Download all assets
for asset_name in ASSETS.values():
    download_asset_if_missing(asset_name)

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Window Setup
WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Gems and Meteors - Graphical Edition")
clock = pygame.time.Clock()

# Color Definitions
COLOR_BG = (10, 10, 25)
COLOR_WHITE = (255, 255, 255)
COLOR_GREY = (120, 120, 120)
COLOR_RED = (240, 50, 50)
COLOR_GREEN = (50, 240, 50)
COLOR_BLUE = (50, 150, 255)
COLOR_YELLOW = (240, 220, 50)
COLOR_CYAN = (50, 240, 240)
COLOR_MAGENTA = (240, 50, 240)

# Load Sound Objects cleanly
sounds = {}
for name, filename in ASSETS.items():
    filepath = os.path.join("cache", filename)
    if os.path.exists(filepath):
        try:
            if name == "music.mp3":
                pass # Play via pygame.mixer.music
            else:
                sounds[name] = pygame.mixer.Sound(filepath)
        except Exception:
            pass

def play_sfx(name):
    if not settings_mute and name in sounds:
        sounds[name].play()

def play_music():
    if not settings_mute:
        music_path = os.path.join("cache", "music.mp3")
        if os.path.exists(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.play(-1)
            except Exception:
                pass

def stop_music():
    pygame.mixer.music.stop()

# Game State Configs
settings_gmode = 1 # 1: Levels, 0: Endless
settings_difficulty = 1 # 1: Easy, 2: Medium, 3: Hard, 4: Expert
settings_sym_idx = 0
settings_mute = False

SPACESHIP_TEMPLATES = [
    "UFO Classic",
    "Arrow Ship",
    "Starfighter",
    "Vanguard"
]

# Star background generator
stars = [[random.randint(0, WIDTH), random.randint(0, HEIGHT), random.uniform(1, 3.5)] for _ in range(120)]

def draw_starry_bg(scroll_speed=1.5):
    screen.fill(COLOR_BG)
    for star in stars:
        # Move star down
        star[1] += star[2] * scroll_speed
        if star[1] > HEIGHT:
            star[1] = 0
            star[0] = random.randint(0, WIDTH)
        color_val = int(star[2] * 70)
        pygame.draw.circle(screen, (color_val, color_val, color_val + 30), (int(star[0]), int(star[1])), int(star[2]))

# High Scores Database
local_scores = []

def load_scores():
    global local_scores
    local_scores = []
    if os.path.exists("data/local_scores.data"):
        try:
            with open("data/local_scores.data", "r") as f:
                for line in f:
                    parts = line.strip().split(";")
                    if len(parts) >= 8:
                        local_scores.append({
                            "name": parts[0],
                            "fs": int(parts[1]),
                            "score": int(parts[2]),
                            "bonus": int(parts[3]),
                            "level": int(parts[4]),
                            "difficulty": int(parts[5]),
                            "gems": int(parts[6]),
                            "damage": int(parts[8]) if len(parts) > 8 else 0
                        })
        except Exception:
            pass
    local_scores.sort(key=lambda s: s["fs"], reverse=True)

def save_local_score(name, fs, score_val, bonus, lvl, diff, gms, dmg):
    try:
        with open("data/local_scores.data", "a") as f:
            f.write(f"{name};{fs};{score_val};{bonus};{lvl};{diff};{gms};00:00:00.00;{dmg}\n")
    except Exception:
        pass

def draw_text(text, font, color, x, y, center=True):
    surf = font.render(text, True, color)
    rect = surf.get_rect()
    if center:
        rect.center = (x, y)
    else:
        rect.topleft = (x, y)
    screen.blit(surf, rect)

# Main Game Loop
def run_game():
    global settings_gmode, settings_difficulty, settings_sym_idx, settings_mute

    cols = 13 if settings_difficulty == 1 else (11 if settings_difficulty == 2 else (9 if settings_difficulty == 3 else 7))
    cell_w = 400 // cols
    cell_h = 32
    map_x_offset = (WIDTH - 400) // 2

    # Map grid of rows
    map_rows = [[" " for _ in range(cols)] for _ in range(22)]

    # Player position (near top)
    player_col = cols // 2
    player_row = 3

    score = 0
    gems_count = 0
    lives = 3
    special_shields = 0
    bullets_left = 10
    level = 1
    damage_taken = 0

    player_bullets = [] # list of [col, row]
    enemy_bullets = [] # list of [col, row]

    level_goal_row = 150
    level_scroll_count = 0

    speed_fps = {1: 8, 2: 12, 3: 18, 4: 24}
    current_fps = speed_fps[settings_difficulty]

    # Particles for animations
    particles = [] # list of [x, y, dx, dy, color, size, age]

    def add_explosion(x, y, color):
        for _ in range(20):
            particles.append([
                x, y,
                random.uniform(-4, 4), random.uniform(-4, 4),
                color,
                random.randint(3, 7),
                20
            ])

    play_music()

    running = True
    paused = False
    game_over = False

    font_large = pygame.font.Font(None, 48)
    font_med = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 24)

    # Move player smoothly
    move_cooldown = 0

    while running:
        dt = clock.tick(30)

        # Input Events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    paused = not paused
                    if paused:
                        stop_music()
                    else:
                        play_music()
                elif (event.key == pygame.K_SPACE or event.key == pygame.K_RETURN) and not paused and not game_over:
                    # Fire Weapon
                    if settings_gmode == 1:
                        if bullets_left > 0:
                            bullets_left -= 1
                            player_bullets.append([player_col, player_row + 1]) # fires down, +y relative
                            play_sfx("damage.wav")
                        elif special_shields > 0:
                            special_shields -= 1
                            bullets_left = 9
                            player_bullets.append([player_col, player_row + 1]) # fires down, +y relative
                            play_sfx("boom.wav")
                    else:
                        # Original boom clear in Endless
                        if special_shields > 0:
                            special_shields -= 1
                            play_sfx("boom.wav")
                            for r in range(len(map_rows)):
                                for c in range(cols):
                                    if map_rows[r][c] not in (" ", "G", "H", "S"):
                                        map_rows[r][c] = "."
                                        add_explosion(map_x_offset + c * cell_w + cell_w//2, r * cell_h + cell_h//2, COLOR_WHITE)

        if paused:
            # Draw pause overlay
            draw_starry_bg(0.2)
            pygame.draw.rect(screen, (20, 20, 40, 200), (100, 200, 400, 400))
            draw_text("GAME PAUSED", font_large, COLOR_RED, WIDTH//2, 250)

            draw_text("[1] Resume Game", font_med, COLOR_WHITE, WIDTH//2, 350)
            draw_text(f"[2] Toggle Sound: {'Muted' if settings_mute else 'Sound ON'}", font_med, COLOR_WHITE, WIDTH//2, 410)
            draw_text("[3] Quit to Main Menu", font_med, COLOR_WHITE, WIDTH//2, 470)

            pygame.display.flip()

            keys = pygame.key.get_pressed()
            if keys[pygame.K_1]:
                paused = False
                play_music()
            elif keys[pygame.K_2]:
                settings_mute = not settings_mute
                if settings_mute: stop_music()
                else: play_music()
                time.sleep(0.2)
            elif keys[pygame.K_3]:
                stop_music()
                return

            continue

        if game_over:
            draw_starry_bg(0.1)
            pygame.draw.rect(screen, (20, 10, 10, 220), (80, 150, 440, 500))
            draw_text("GAME OVER", font_large, COLOR_RED, WIDTH//2, 200)

            lvl_bonus = level * 10 * settings_difficulty
            final_fs = score + lvl_bonus

            draw_text(f"Raw Score: {score}", font_med, COLOR_WHITE, WIDTH//2, 280)
            draw_text(f"Level Bonus: +{lvl_bonus}", font_med, COLOR_WHITE, WIDTH//2, 330)
            draw_text(f"Final Score: {final_fs}", font_large, COLOR_GREEN, WIDTH//2, 390)

            draw_text("Enter your 3 initials:", font_med, COLOR_YELLOW, WIDTH//2, 460)

            if "name_str" not in locals():
                name_str = ""

            draw_text(f"{name_str if name_str else '___'}", font_large, COLOR_WHITE, WIDTH//2, 520)
            draw_text("[Press letters A-Z to type, Enter to Save]", font_small, COLOR_GREY, WIDTH//2, 580)

            pygame.display.flip()

            for event in pygame.event.get(pygame.KEYDOWN):
                if event.key == pygame.K_RETURN and len(name_str) == 3:
                    save_local_score(name_str, final_fs, score, lvl_bonus, level, settings_difficulty, gems_count, damage_taken)
                    running = False
                elif event.key == pygame.K_BACKSPACE:
                    name_str = name_str[:-1]
                elif len(name_str) < 3 and event.unicode.isalpha():
                    name_str += event.unicode.upper()
            continue

        if move_cooldown > 0:
            move_cooldown -= 1

        keys = pygame.key.get_pressed()
        if move_cooldown == 0:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                if player_col > 0:
                    player_col -= 1
                    move_cooldown = 2
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                if player_col < cols - 1:
                    player_col += 1
                    move_cooldown = 2

        level_scroll_count += 1
        score += 1

        # Dynamic difficulty speed scaling
        if score % 200 == 0:
            current_fps = min(40, current_fps + 1)

        # Scroll Map downwards
        map_rows.pop(0)
        new_row = [" " for _ in range(cols)]

        # Level Mode completion generation
        if settings_gmode == 1:
            if level_scroll_count == level_goal_row:
                for c in range(cols):
                    new_row[c] = "═"
                new_row[cols // 2] = " "
            elif level_scroll_count > level_goal_row - 10 and level_scroll_count <= level_goal_row + 5:
                pass
            else:
                for c in range(cols):
                    num = random.randint(0, 999)
                    if num < 8: new_row[c] = "S" # Shield
                    elif num >= 100 and num <= 108: new_row[c] = "H" # Heart
                    elif num >= 200 and num <= 215: new_row[c] = "G" # Gem
                    elif num >= 50 and num <= 60 + settings_difficulty * 10:
                        new_row[c] = "M" # Meteor
        else:
            for c in range(cols):
                num = random.randint(0, 999)
                if num < 8: new_row[c] = "S"
                elif num >= 100 and num <= 108: new_row[c] = "H"
                elif num >= 200 and num <= 215: new_row[c] = "G"
                elif num >= 50 and num <= 60 + settings_difficulty * 10:
                    new_row[c] = "M"

        map_rows.append(new_row)

        # Verify Landing Strip reaching (Level Mode)
        if settings_gmode == 1 and level_scroll_count >= level_goal_row:
            if player_row == len(map_rows) - 4 or level_scroll_count == level_goal_row + 5:
                if player_col == cols // 2:
                    play_sfx("heart.wav")
                    add_explosion(WIDTH//2, HEIGHT//2, COLOR_GREEN)
                    score += level * 500
                    level += 1
                    level_scroll_count = 0
                    map_rows = [[" " for _ in range(cols)] for _ in range(22)]
                    player_bullets = []
                    enemy_bullets = []
                    bullets_left = 10
                    continue
                else:
                    lives -= 1
                    damage_taken += 1
                    play_sfx("damage.wav")
                    level_scroll_count = level_goal_row - 12

        # Update Player Lasers (moving DOWN screen, +y relative)
        active_pbullets = []
        for b in player_bullets:
            bc, br = b
            hit = False
            for step in range(3):
                test_r = br + step
                if test_r < len(map_rows):
                    cell = map_rows[test_r][bc]
                    if cell != " " and cell != "P" and cell != "O" and cell != "▲" and cell != "•" and cell != "↑":
                        hit = True
                        map_rows[test_r][bc] = " "
                        cell_cx = map_x_offset + bc * cell_w + cell_w//2
                        cell_cy = test_r * cell_h + cell_h//2
                        if cell == "G":
                            gems_count += 1
                            score += 5 * settings_difficulty + 5
                            play_sfx("gem.wav")
                            add_explosion(cell_cx, cell_cy, COLOR_GREEN)
                        elif cell == "H":
                            lives = min(10, lives + 1)
                            play_sfx("heart.wav")
                            add_explosion(cell_cx, cell_cy, COLOR_RED)
                        elif cell == "S":
                            special_shields = min(5, special_shields + 1)
                            play_sfx("boom.wav")
                            add_explosion(cell_cx, cell_cy, COLOR_CYAN)
                        else:
                            # Hit Meteor
                            map_rows[test_r][bc] = "."
                            play_sfx("damage.wav")
                            add_explosion(cell_cx, cell_cy, COLOR_GREY)
                        break
                    elif cell == "▲":
                        # Hit enemy ship directly!
                        hit = True
                        map_rows[test_r][bc] = " "
                        score += 1000
                        play_sfx("boom.wav")
                        add_explosion(map_x_offset + bc * cell_w + cell_w//2, test_r * cell_h + cell_h//2, COLOR_YELLOW)
                        break
            if not hit:
                new_br = br + 3
                if new_br < len(map_rows):
                    active_pbullets.append([bc, new_br])
        player_bullets = active_pbullets

        # Update Enemy Lasers (moving UP screen, -y relative)
        active_ebullets = []
        for eb in enemy_bullets:
            ebc, ebr = eb
            hit = False
            for step in range(2):
                test_r = ebr - step
                if test_r >= 0:
                    if test_r == player_row and ebc == player_col:
                        hit = True
                        lives -= 1
                        damage_taken += 1
                        play_sfx("damage.wav")
                        add_explosion(map_x_offset + player_col * cell_w + cell_w//2, player_row * cell_h + cell_h//2, COLOR_RED)
                        break
            if not hit:
                new_ebr = ebr - 2
                if new_ebr >= 0:
                    active_ebullets.append([ebc, new_ebr])
        enemy_bullets = active_ebullets

        # Update Enemies on map (scrolling up naturally, moving side-to-side, and shooting UP)
        if settings_gmode == 1:
            for r in range(len(map_rows) - 1, -1, -1):
                for c in range(cols):
                    if map_rows[r][c] == "▲":
                        map_rows[r][c] = " "
                        move = random.choice([-1, 0, 1])
                        new_c = max(0, min(cols - 1, c + move))
                        # Fire bullet upwards (-y)
                        if random.randint(0, 5) == 0:
                            enemy_bullets.append([new_c, r - 1])
                        if r < len(map_rows):
                            map_rows[r][new_c] = "▲"

            # Spawn active enemies
            if level_scroll_count % 15 == 0 and level_scroll_count < level_goal_row - 10:
                spawn_c = random.randint(0, cols - 1)
                if map_rows[len(map_rows) - 1][spawn_c] == " ":
                    map_rows[len(map_rows) - 1][spawn_c] = "▲"

        # Resolve player direct collisions
        player_cell = map_rows[player_row][player_col]
        if player_cell != " ":
            map_rows[player_row][player_col] = " "
            cell_cx = map_x_offset + player_col * cell_w + cell_w//2
            cell_cy = player_row * cell_h + cell_h//2
            if player_cell == "G":
                gems_count += 1
                score += 5 * settings_difficulty + 5
                play_sfx("gem.wav")
                add_explosion(cell_cx, cell_cy, COLOR_GREEN)
            elif player_cell == "H":
                lives = min(10, lives + 1)
                play_sfx("heart.wav")
                add_explosion(cell_cx, cell_cy, COLOR_RED)
            elif player_cell == "S":
                special_shields = min(5, special_shields + 1)
                play_sfx("boom.wav")
                add_explosion(cell_cx, cell_cy, COLOR_CYAN)
            elif player_cell in ("▲", "•", "↑"):
                lives -= 1
                damage_taken += 1
                play_sfx("damage.wav")
                add_explosion(cell_cx, cell_cy, COLOR_RED)
            else:
                damage_taken += 1
                play_sfx("damage.wav")
                add_explosion(cell_cx, cell_cy, COLOR_GREY)
                if special_shields > 0:
                    special_shields -= 1
                    lives -= 1
                else:
                    lives -= 3

        if lives <= 0:
            stop_music()
            game_over = True

        # DRAW ACTIVE FRAME
        draw_starry_bg(1.5)

        # Draw Side Borders
        pygame.draw.line(screen, COLOR_WHITE, (map_x_offset, 0), (map_x_offset, HEIGHT), 2)
        pygame.draw.line(screen, COLOR_WHITE, (map_x_offset + cols * cell_w, 0), (map_x_offset + cols * cell_w, HEIGHT), 2)

        # Draw Map cells
        for r in range(len(map_rows)):
            for c in range(cols):
                cell = map_rows[r][c]
                rx = map_x_offset + c * cell_w
                ry = r * cell_h

                is_bullet = any(b[0] == c and b[1] == r for b in player_bullets)
                is_ebullet = any(eb[0] == c and eb[1] == r for eb in enemy_bullets)

                if r == player_row and c == player_col:
                    ship_color = COLOR_CYAN
                    points = [
                        (rx + cell_w//2, ry + cell_h), # Nose pointing down
                        (rx, ry), # Wing left
                        (rx + cell_w//2, ry + 8), # Center groove
                        (rx + cell_w, ry) # Wing right
                    ]
                    pygame.draw.polygon(screen, ship_color, points)
                    pygame.draw.polygon(screen, COLOR_WHITE, points, 1)
                elif is_bullet:
                    # Player bullet fires down (Green plasma ball)
                    pygame.draw.circle(screen, COLOR_GREEN, (rx + cell_w//2, ry + cell_h//2), 6)
                elif is_ebullet:
                    # Enemy bullet fires up (Red laser beam)
                    pygame.draw.line(screen, COLOR_RED, (rx + cell_w//2, ry), (rx + cell_w//2, ry + cell_h), 4)
                elif cell == "▲":
                    # Red enemy ship
                    pygame.draw.ellipse(screen, COLOR_RED, (rx + 2, ry + 4, cell_w - 4, cell_h - 8))
                    pygame.draw.circle(screen, COLOR_YELLOW, (rx + cell_w//2, ry + cell_h//2), 4)
                elif cell == "G":
                    pts = [
                        (rx + cell_w//2, ry),
                        (rx + cell_w, ry + cell_h//2),
                        (rx + cell_w//2, ry + cell_h),
                        (rx, ry + cell_h//2)
                    ]
                    pygame.draw.polygon(screen, COLOR_GREEN, pts)
                elif cell == "H":
                    pygame.draw.circle(screen, COLOR_RED, (rx + cell_w//4, ry + cell_h//3), cell_w//4)
                    pygame.draw.circle(screen, COLOR_RED, (rx + 3 * cell_w//4, ry + cell_h//3), cell_w//4)
                    pts = [
                        (rx, ry + cell_h//3 + 2),
                        (rx + cell_w//2, ry + cell_h),
                        (rx + cell_w, ry + cell_h//3 + 2)
                    ]
                    pygame.draw.polygon(screen, COLOR_RED, pts)
                elif cell == "S":
                    pygame.draw.circle(screen, COLOR_BLUE, (rx + cell_w//2, ry + cell_h//2), cell_w//2 - 2, 2)
                    pygame.draw.circle(screen, COLOR_CYAN, (rx + cell_w//2, ry + cell_h//2), 6)
                elif cell == ".":
                    pygame.draw.circle(screen, COLOR_GREY, (rx + cell_w//2, ry + cell_h//2), 3)
                elif cell == "═":
                    pygame.draw.rect(screen, COLOR_YELLOW, (rx, ry + cell_h//3, cell_w, cell_h//3))
                elif cell != " ":
                    pygame.draw.rect(screen, (80, 50, 40), (rx + 1, ry + 1, cell_w - 2, cell_h - 2))
                    pygame.draw.rect(screen, (150, 110, 80), (rx + 3, ry + 3, cell_w - 6, cell_h - 6), 1)

        # Render particles
        active_parts = []
        for p in particles:
            p[0] += p[2]
            p[1] += p[3]
            p[6] -= 1
            if p[6] > 0:
                pygame.draw.circle(screen, p[4], (int(p[0]), int(p[1])), p[5])
                active_parts.append(p)
        particles = active_parts

        # Draw HUD interface
        pygame.draw.rect(screen, (15, 15, 30), (0, 0, WIDTH, 80))
        pygame.draw.line(screen, COLOR_CYAN, (0, 80), (WIDTH, 80), 2)

        # Lives Bar
        draw_text("Lives: ", font_med, COLOR_WHITE, 50, 25)
        for heart_i in range(lives):
            pygame.draw.circle(screen, COLOR_RED, (110 + heart_i * 22, 20), 8)
            pygame.draw.circle(screen, COLOR_RED, (120 + heart_i * 22, 20), 8)
            pygame.draw.polygon(screen, COLOR_RED, [(101 + heart_i * 22, 21), (115 + heart_i * 22, 34), (129 + heart_i * 22, 21)])

        # Shield Bar
        draw_text("Shields: ", font_med, COLOR_WHITE, 50, 55)
        for s_i in range(special_shields):
            pygame.draw.circle(screen, COLOR_CYAN, (115 + s_i * 22, 55), 8, 2)
            pygame.draw.circle(screen, COLOR_CYAN, (115 + s_i * 22, 55), 4)

        # Stats Texts
        draw_text(f"Score: {score}", font_med, COLOR_GREEN, 400, 25, center=False)
        draw_text(f"Level: {level}", font_med, COLOR_WHITE, 400, 50, center=False)
        if settings_gmode == 1:
            draw_text(f"Laser Ammo: {bullets_left}", font_small, COLOR_YELLOW, 220, 50)

        pygame.display.flip()

        clock.tick(current_fps)

def main_menu():
    global settings_gmode, settings_difficulty, settings_sym_idx, settings_mute
    sel = 1
    total_opts = 7

    font_title = pygame.font.Font(None, 64)
    font_med = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 24)

    while True:
        draw_starry_bg(0.8)

        draw_text("GEMS AND METEORS", font_title, COLOR_CYAN, WIDTH//2, 120)
        draw_text("GRAPHICAL EDITION", font_med, COLOR_WHITE, WIDTH//2, 180)

        mode_str = "Levels Mode" if settings_gmode == 1 else "Endless Mode"
        mute_str = "Sound OFF (Muted)" if settings_mute else "Sound ON"

        options = [
            "Start GaM",
            f"Game Mode: {mode_str}",
            f"Difficulty: {settings_difficulty}",
            f"Sound: {mute_str}",
            "High Scores",
            "Controls & Help",
            "Quit"
        ]

        for i, opt in enumerate(options, 1):
            color = COLOR_GREEN if i == sel else COLOR_WHITE
            prefix = " ► " if i == sel else "   "
            draw_text(f"{prefix}{opt}", font_med, color, WIDTH//2, 280 + i * 55)

        draw_text("Use UP/DOWN Arrows to Select, SPACE/ENTER to Confirm", font_small, COLOR_GREY, WIDTH//2, 750)

        pygame.display.flip()

        while True:
            event = pygame.event.wait()
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    sel = sel - 1 if sel > 1 else total_opts
                    break
                elif event.key == pygame.K_DOWN:
                    sel = sel + 1 if sel < total_opts else 1
                    break
                elif event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                    if sel == 1:
                        run_game()
                        break
                    elif sel == 2:
                        settings_gmode = 1 - settings_gmode
                        break
                    elif sel == 3:
                        settings_difficulty = settings_difficulty + 1 if settings_difficulty < 4 else 1
                        break
                    elif sel == 4:
                        settings_mute = not settings_mute
                        break
                    elif sel == 5:
                        show_high_scores()
                        break
                    elif sel == 6:
                        show_help()
                        break
                    elif sel == 7:
                        pygame.quit()
                        sys.exit()

def show_help():
    font_title = pygame.font.Font(None, 48)
    font_med = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 24)

    while True:
        draw_starry_bg(0.3)
        pygame.draw.rect(screen, (15, 15, 30, 210), (50, 100, 500, 600))
        draw_text("CONTROLS & HELP", font_title, COLOR_YELLOW, WIDTH//2, 150)

        instructions = [
            "A / LEFT Arrow    : Move Left",
            "D / RIGHT Arrow   : Move Right",
            "SPACE / ENTER     : Fire Laser Beam (Downwards)",
            "ESC               : Pause / In-game settings",
            "",
            "Objective:",
            "- Shoot/dodge enemies coming from the bottom",
            "- Collect Gems, Hearts, and gun-reloading Shields",
            "- Avoid meteor clusters and projectile bullets",
            "- Land in the middle column on the yellow Landing",
            "  Strip at the bottom to save your progress!"
        ]

        for i, line in enumerate(instructions):
            draw_text(line, font_small, COLOR_WHITE, 80, 240 + i * 32, center=False)

        draw_text("[Press any key to return to main menu]", font_small, COLOR_GREEN, WIDTH//2, 650)
        pygame.display.flip()

        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            return

def show_high_scores():
    load_scores()
    font_title = pygame.font.Font(None, 48)
    font_med = pygame.font.Font(None, 32)
    font_small = pygame.font.Font(None, 24)

    while True:
        draw_starry_bg(0.3)
        pygame.draw.rect(screen, (15, 15, 30, 210), (50, 100, 500, 600))
        draw_text("LOCAL LEADERBOARD", font_title, COLOR_YELLOW, WIDTH//2, 150)

        headers = f"{'Rank':<6}{'Name':<10}{'Score':<12}{'Level':<8}{'Diff':<8}"
        draw_text(headers, font_med, COLOR_CYAN, 80, 220, center=False)
        pygame.draw.line(screen, COLOR_CYAN, (80, 250), (520, 250), 2)

        for idx, s in enumerate(local_scores[:10]):
            line = f"#{idx+1:<5}{s['name']:<10}{s['fs']:<12}{s['level']:<8}{s['difficulty']:<8}"
            draw_text(line, font_med, COLOR_WHITE, 80, 270 + idx * 35, center=False)

        draw_text("[Press any key to return to main menu]", font_small, COLOR_GREEN, WIDTH//2, 650)
        pygame.display.flip()

        event = pygame.event.wait()
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            return

if __name__ == "__main__":
    main_menu()

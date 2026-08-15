# -*- coding: utf-8 -*-
"""
Gems and Meteors - Python Graphical (Tkinter) Version
Created by Jules
Utilizes Python's native standard library Tkinter for a 100% zero-dependency,
zero-compile graphical arcade game that runs flawlessly on any python version (including 3.14+).
"""

import os
import sys
import time
import random
import tkinter as tk
from tkinter import messagebox
import threading

# Ensure data and cache folders exist
os.makedirs("cache", exist_ok=True)
os.makedirs("data", exist_ok=True)

# Color Definitions
COLOR_BG = "#0A0A19"
COLOR_WHITE = "#FFFFFF"
COLOR_GREY = "#787878"
COLOR_RED = "#F03232"
COLOR_GREEN = "#32F032"
COLOR_BLUE = "#3296FF"
COLOR_YELLOW = "#F0DC32"
COLOR_CYAN = "#32F0F0"

# Settings
gmode = 1 # 1: Levels, 0: Endless
difficulty = 1 # 1-4
settings_mute = False

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

def play_sfx(filename):
    if settings_mute or os.name != 'nt':
        return
    import winsound
    filepath = os.path.join("cache", filename)
    if os.path.exists(filepath):
        threading.Thread(target=winsound.PlaySound, args=(filepath, winsound.SND_FILENAME | winsound.SND_ASYNC), daemon=True).start()

class GameApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Gems and Meteors - Graphical Edition")
        self.geometry("600x800")
        self.resizable(False, False)
        self.configure(bg=COLOR_BG)

        # Star Background Setup
        self.stars = [[random.randint(0, 600), random.randint(0, 800), random.uniform(1, 3.5)] for _ in range(80)]

        self.show_main_menu()

    def show_main_menu(self):
        self.clear_screen()

        # Canvas for Title and starry background
        self.canvas = tk.Canvas(self, width=600, height=800, bg=COLOR_BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.draw_stars_on_canvas()

        # Render Title Text
        self.canvas.create_text(300, 120, text="GEMS AND METEORS", font=("Courier New", 36, "bold"), fill=COLOR_CYAN)
        self.canvas.create_text(300, 170, text="Graphical Edition (Tkinter)", font=("Courier New", 18), fill=COLOR_WHITE)

        # Add buttons using Tkinter labels with elegant styles
        self.create_menu_button("Start Game", 280, self.start_game)
        self.create_menu_button(f"Game Mode: {'Levels' if gmode == 1 else 'Endless'}", 340, self.toggle_gmode)
        self.create_menu_button(f"Difficulty: {difficulty}", 400, self.toggle_difficulty)
        self.create_menu_button(f"Sound: {'Muted' if settings_mute else 'ON'}", 460, self.toggle_sound)
        self.create_menu_button("Leaderboard", 520, self.show_leaderboard)
        self.create_menu_button("Controls & Help", 580, self.show_help)
        self.create_menu_button("Quit Game", 640, self.quit)

        self.menu_running = True
        self.animate_menu()

    def create_menu_button(self, text, y, callback):
        btn = tk.Label(self.canvas, text=text, font=("Courier New", 18, "bold"), fg=COLOR_WHITE, bg=COLOR_BG, cursor="hand2")
        btn.bind("<Enter>", lambda e: btn.configure(fg=COLOR_GREEN))
        btn.bind("<Leave>", lambda e: btn.configure(fg=COLOR_WHITE))
        btn.bind("<Button-1>", lambda e: callback())
        self.canvas.create_window(300, y, window=btn)

    def draw_stars_on_canvas(self):
        self.canvas.delete("star")
        for s in self.stars:
            s[1] += s[2] * 0.5
            if s[1] > 800:
                s[1] = 0
                s[0] = random.randint(0, 600)
            col = int(s[2] * 70)
            rgb = f"#{col:02x}{col:02x}{min(255, col+30):02x}"
            sz = int(s[2])
            self.canvas.create_oval(s[0], s[1], s[0]+sz, s[1]+sz, fill=rgb, outline="", tags="star")

    def animate_menu(self):
        if hasattr(self, "menu_running") and self.menu_running:
            self.draw_stars_on_canvas()
            # Bring text/buttons to top
            self.canvas.tag_raise("star")
            self.canvas.tag_lower("star")
            self.after(50, self.animate_menu)

    def clear_screen(self):
        self.menu_running = False
        for widget in self.winfo_children():
            widget.destroy()

    def toggle_gmode(self):
        global gmode
        gmode = 1 - gmode
        self.show_main_menu()

    def toggle_difficulty(self):
        global difficulty
        difficulty = difficulty + 1 if difficulty < 4 else 1
        self.show_main_menu()

    def toggle_sound(self):
        global settings_mute
        settings_mute = not settings_mute
        self.show_main_menu()

    def show_leaderboard(self):
        load_scores()
        self.clear_screen()

        self.canvas = tk.Canvas(self, width=600, height=800, bg=COLOR_BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.canvas.create_text(300, 100, text="LOCAL LEADERBOARD", font=("Courier New", 28, "bold"), fill=COLOR_YELLOW)

        headers = f"{'Rank':<6}{'Name':<10}{'Score':<12}{'Level':<8}{'Diff':<8}"
        self.canvas.create_text(300, 180, text=headers, font=("Courier New", 16, "bold"), fill=COLOR_CYAN)

        for idx, s in enumerate(local_scores[:10]):
            line = f"#{idx+1:<5}{s['name']:<10}{s['fs']:<12}{s['level']:<8}{s['difficulty']:<8}"
            self.canvas.create_text(300, 220 + idx * 35, text=line, font=("Courier New", 14), fill=COLOR_WHITE)

        self.create_menu_button("Return to Menu", 680, self.show_main_menu)
        self.menu_running = True
        self.animate_menu()

    def show_help(self):
        self.clear_screen()
        self.canvas = tk.Canvas(self, width=600, height=800, bg=COLOR_BG, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.canvas.create_text(300, 100, text="CONTROLS & HELP", font=("Courier New", 28, "bold"), fill=COLOR_YELLOW)

        help_lines = [
            "A / LEFT Arrow    : Move Left",
            "D / RIGHT Arrow   : Move Right",
            "SPACE / ENTER     : Fire Laser (Downwards)",
            "ESC               : Pause Settings",
            "",
            "Objective:",
            "- Shoot/dodge enemies coming from the bottom",
            "- Collect Gems, Hearts, and gun Shields",
            "- Avoid meteor clusters and projectile bullets",
            "- Land in the middle column on the yellow Landing",
            "  Strip at the bottom to save your progress!"
        ]

        for i, line in enumerate(help_lines):
            self.canvas.create_text(100, 180 + i * 35, text=line, font=("Courier New", 14), fill=COLOR_WHITE, anchor="w")

        self.create_menu_button("Return to Menu", 680, self.show_main_menu)
        self.menu_running = True
        self.animate_menu()

    def start_game(self):
        self.clear_screen()

        # Setup Grid Mapping based on difficulty
        self.cols = 13 if difficulty == 1 else (11 if difficulty == 2 else (9 if difficulty == 3 else 7))
        self.cell_w = 400 // self.cols
        self.cell_h = 32
        self.map_x_offset = (600 - 400) // 2

        self.map_rows = [[" " for _ in range(self.cols)] for _ in range(22)]
        self.player_col = self.cols // 2
        self.player_row = 3

        # Game statistics
        self.game_score = 0
        self.gems_count = 0
        self.lives = 3
        self.special_shields = 0
        self.bullets_left = 10
        self.game_level = 1
        self.damage_taken = 0

        self.player_bullets = []
        self.enemy_bullets = []

        self.level_goal_row = 150
        self.level_scroll_count = 0

        # Delay mapping (ms)
        speed_delays = {1: 150, 2: 80, 3: 40, 4: 20}
        self.tick_delay = speed_delays[difficulty]

        # Particles list
        self.particles = []

        # Create interactive canvas
        self.game_canvas = tk.Canvas(self, width=600, height=800, bg=COLOR_BG, highlightthickness=0)
        self.game_canvas.pack(fill="both", expand=True)

        self.bind_keys()
        self.game_paused = False
        self.game_over = False

        self.game_tick()

    def bind_keys(self):
        self.bind_all("<Key>", self.handle_keydown)

    def handle_keydown(self, event):
        if self.game_over:
            return

        key = event.keysym.lower()
        if key == "escape":
            self.game_paused = not self.game_paused
            if self.game_paused:
                self.show_pause_overlay()
            else:
                self.game_canvas.delete("pause_ov")
                self.game_tick()
        elif not self.game_paused:
            if key in ("left", "a"):
                if self.player_col > 0:
                    self.player_col -= 1
            elif key in ("right", "d"):
                if self.player_col < self.cols - 1:
                    self.player_col += 1
            elif key in ("space", "return"):
                # Fire Laser downwards in Levels mode
                if gmode == 1:
                    if self.bullets_left > 0:
                        self.bullets_left -= 1
                        self.player_bullets.append([self.player_col, self.player_row + 1])
                        play_sfx("damage.wav")
                    elif self.special_shields > 0:
                        self.special_shields -= 1
                        self.bullets_left = 9
                        self.player_bullets.append([self.player_col, self.player_row + 1])
                        play_sfx("boom.wav")
                else:
                    # Endless clear explosion
                    if self.special_shields > 0:
                        self.special_shields -= 1
                        play_sfx("boom.wav")
                        for r in range(len(self.map_rows)):
                            for c in range(self.cols):
                                if self.map_rows[r][c] not in (" ", "G", "H", "S"):
                                    self.map_rows[r][c] = "."

    def show_pause_overlay(self):
        self.game_canvas.create_rectangle(100, 200, 500, 550, fill="#141428", outline=COLOR_CYAN, width=2, tags="pause_ov")
        self.game_canvas.create_text(300, 250, text="GAME PAUSED", font=("Courier New", 24, "bold"), fill=COLOR_RED, tags="pause_ov")

        self.game_canvas.create_text(300, 320, text="[ESC] Resume Game", font=("Courier New", 14), fill=COLOR_WHITE, tags="pause_ov")
        self.game_canvas.create_text(300, 380, text=f"[S] Sound Setting: {'OFF' if settings_mute else 'ON'}", font=("Courier New", 14), fill=COLOR_WHITE, tags="pause_ov")
        self.game_canvas.create_text(300, 440, text="[Q] Quit to Menu", font=("Courier New", 14), fill=COLOR_WHITE, tags="pause_ov")

        # Listen to pause commands directly
        def pause_input(event):
            key = event.keysym.lower()
            if key == "s":
                global settings_mute
                settings_mute = not settings_mute
                self.show_pause_overlay()
            elif key == "q":
                self.unbind_all("<Key>")
                self.show_main_menu()

        self.bind_all("<Key>", pause_input)

    def add_explosion(self, x, y, color):
        for _ in range(12):
            self.particles.append([
                x, y,
                random.uniform(-4, 4), random.uniform(-4, 4),
                color,
                random.randint(2, 5),
                15
            ])

    def game_tick(self):
        if self.game_paused or self.game_over:
            return

        self.level_scroll_count += 1
        self.game_score += 1

        # Dynamic delay decrease
        if self.game_score % 200 == 0:
            min_delay = 50 if difficulty == 1 else (25 if difficulty == 2 else (12 if difficulty == 3 else 5))
            if self.tick_delay > min_delay:
                self.tick_delay = max(min_delay, self.tick_delay - 2)

        # Scroll Map downwards
        self.map_rows.pop(0)
        new_row = [" " for _ in range(self.cols)]

        if gmode == 1:
            if self.level_scroll_count == self.level_goal_row:
                for c in range(self.cols):
                    new_row[c] = "═"
                new_row[self.cols // 2] = " "
            elif self.level_scroll_count > self.level_goal_row - 10 and self.level_scroll_count <= self.level_goal_row + 5:
                pass
            else:
                for c in range(self.cols):
                    num = random.randint(0, 999)
                    if num < 8: new_row[c] = "S" # Shield
                    elif num >= 100 and num <= 108: new_row[c] = "H" # Heart
                    elif num >= 200 and num <= 215: new_row[c] = "G" # Gem
                    elif num >= 50 and num <= 60 + difficulty * 10:
                        new_row[c] = "M" # Meteor
        else:
            for c in range(self.cols):
                num = random.randint(0, 999)
                if num < 8: new_row[c] = "S"
                elif num >= 100 and num <= 108: new_row[c] = "H"
                elif num >= 200 and num <= 215: new_row[c] = "G"
                elif num >= 50 and num <= 60 + difficulty * 10:
                    new_row[c] = "M"

        self.map_rows.append(new_row)

        # Level mode landing strip reaching check
        if gmode == 1 and self.level_scroll_count >= self.level_goal_row:
            if self.player_row == len(self.map_rows) - 4 or self.level_scroll_count == self.level_goal_row + 5:
                if self.player_col == self.cols // 2:
                    # Successfully completed level!
                    play_sfx("heart.wav")
                    self.game_score += self.game_level * 500
                    self.game_level += 1
                    self.level_scroll_count = 0
                    self.map_rows = [[" " for _ in range(self.cols)] for _ in range(22)]
                    self.player_bullets = []
                    self.enemy_bullets = []
                    self.bullets_left = 10
                else:
                    self.lives -= 1
                    self.damage_taken += 1
                    play_sfx("damage.wav")
                    self.level_scroll_count = self.level_goal_row - 12

        # Update Player Lasers (moving DOWN screen, +y relative)
        active_pbullets = []
        for b in self.player_bullets:
            bc, br = b
            hit = False
            for step in range(3):
                test_r = br + step
                if test_r < len(self.map_rows):
                    cell = self.map_rows[test_r][bc]
                    if cell != " " and cell != "▲" and cell != "•" and cell != "↑":
                        hit = True
                        self.map_rows[test_r][bc] = " "
                        cx = self.map_x_offset + bc * self.cell_w + self.cell_w//2
                        cy = test_r * self.cell_h + self.cell_h//2
                        if cell == "G":
                            self.gems_count += 1
                            self.game_score += 5 * difficulty + 5
                            play_sfx("gem.wav")
                            self.add_explosion(cx, cy, COLOR_GREEN)
                        elif cell == "H":
                            self.lives = min(10, self.lives + 1)
                            play_sfx("heart.wav")
                            self.add_explosion(cx, cy, COLOR_RED)
                        elif cell == "S":
                            self.special_shields = min(5, self.special_shields + 1)
                            play_sfx("boom.wav")
                            self.add_explosion(cx, cy, COLOR_CYAN)
                        else:
                            self.map_rows[test_r][bc] = "."
                            play_sfx("damage.wav")
                            self.add_explosion(cx, cy, COLOR_GREY)
                        break
                    elif cell == "▲":
                        hit = True
                        self.map_rows[test_r][bc] = " "
                        self.game_score += 1000
                        play_sfx("boom.wav")
                        self.add_explosion(self.map_x_offset + bc * self.cell_w + self.cell_w//2, test_r * self.cell_h + self.cell_h//2, COLOR_YELLOW)
                        break
            if not hit:
                new_br = br + 3
                if new_br < len(self.map_rows):
                    active_pbullets.append([bc, new_br])
        self.player_bullets = active_pbullets

        # Update Enemy Lasers (moving UP screen, -y relative)
        active_ebullets = []
        for eb in self.enemy_bullets:
            ebc, ebr = eb
            hit = False
            for step in range(2):
                test_r = ebr - step
                if test_r >= 0:
                    if test_r == self.player_row and ebc == self.player_col:
                        hit = True
                        self.lives -= 1
                        self.damage_taken += 1
                        play_sfx("damage.wav")
                        self.add_explosion(self.map_x_offset + self.player_col * self.cell_w + self.cell_w//2, self.player_row * self.cell_h + self.cell_h//2, COLOR_RED)
                        break
            if not hit:
                new_ebr = ebr - 2
                if new_ebr >= 0:
                    active_ebullets.append([ebc, new_ebr])
        self.enemy_bullets = active_ebullets

        # Update Enemies on map (moving side-to-side every 2 ticks towards player_col with difficulty-scaled accuracy)
        if gmode == 1:
            if not hasattr(self, "tick_count"):
                self.tick_count = 0
            self.tick_count += 1

            acc_thresholds = {1: 30, 2: 50, 3: 70, 4: 90}
            thresh = acc_thresholds[difficulty]

            for r in range(len(self.map_rows) - 1, -1, -1):
                for c in range(self.cols):
                    if self.map_rows[r][c] == "▲":
                        self.map_rows[r][c] = " "
                        new_c = c
                        if self.tick_count % 2 == 0:
                            if random.randint(0, 99) < thresh:
                                if c < self.player_col:
                                    new_c = min(self.cols - 1, c + 1)
                                elif c > self.player_col:
                                    new_c = max(0, c - 1)
                            else:
                                move = random.choice([-1, 0, 1])
                                new_c = max(0, min(self.cols - 1, c + move))
                        if random.randint(0, 5) == 0:
                            self.enemy_bullets.append([new_c, r - 1])
                        if r < len(self.map_rows):
                            self.map_rows[r][new_c] = "▲"

            if self.level_scroll_count % 15 == 0 and self.level_scroll_count < self.level_goal_row - 10:
                spawn_c = random.randint(0, self.cols - 1)
                if self.map_rows[len(self.map_rows) - 1][spawn_c] == " ":
                    self.map_rows[len(self.map_rows) - 1][spawn_c] = "▲"

        # Direct player collisions
        player_cell = self.map_rows[self.player_row][self.player_col]
        if player_cell != " ":
            self.map_rows[self.player_row][self.player_col] = " "
            cx = self.map_x_offset + self.player_col * self.cell_w + self.cell_w//2
            cy = self.player_row * self.cell_h + self.cell_h//2
            if player_cell == "G":
                self.gems_count += 1
                self.game_score += 5 * difficulty + 5
                play_sfx("gem.wav")
                self.add_explosion(cx, cy, COLOR_GREEN)
            elif player_cell == "H":
                self.lives = min(10, self.lives + 1)
                play_sfx("heart.wav")
                self.add_explosion(cx, cy, COLOR_RED)
            elif player_cell == "S":
                self.special_shields = min(5, self.special_shields + 1)
                play_sfx("boom.wav")
                self.add_explosion(cx, cy, COLOR_CYAN)
            elif player_cell in ("▲", "•", "↑"):
                self.lives -= 1
                self.damage_taken += 1
                play_sfx("damage.wav")
                self.add_explosion(cx, cy, COLOR_RED)
            else:
                self.damage_taken += 1
                play_sfx("damage.wav")
                self.add_explosion(cx, cy, COLOR_GREY)
                if self.special_shields > 0:
                    self.special_shields -= 1
                    self.lives -= 1
                else:
                    self.lives -= 3

        if self.lives <= 0:
            self.game_over = True
            self.show_game_over_screen()
            return

        self.render_game_frame()

        self.after(self.tick_delay, self.game_tick)

    def render_game_frame(self):
        self.game_canvas.delete("all")

        # Draw Star background
        for s in self.stars:
            s[1] += s[2] * 0.5
            if s[1] > 800:
                s[1] = 0
                s[0] = random.randint(0, 600)
            col = int(s[2] * 70)
            rgb = f"#{col:02x}{col:02x}{min(255, col+30):02x}"
            sz = int(s[2])
            self.game_canvas.create_oval(s[0], s[1], s[0]+sz, s[1]+sz, fill=rgb, outline="")

        # Draw Borders
        self.game_canvas.create_line(self.map_x_offset, 0, self.map_x_offset, 800, fill=COLOR_WHITE, width=2)
        self.game_canvas.create_line(self.map_x_offset + self.cols * self.cell_w, 0, self.map_x_offset + self.cols * self.cell_w, 800, fill=COLOR_WHITE, width=2)

        # Draw Map Elements
        for r in range(len(self.map_rows)):
            for c in range(self.cols):
                cell = self.map_rows[r][c]
                rx = self.map_x_offset + c * self.cell_w
                ry = r * self.cell_h

                is_bullet = any(b[0] == c and b[1] == r for b in self.player_bullets)
                is_ebullet = any(eb[0] == c and eb[1] == r for eb in self.enemy_bullets)

                if r == self.player_row and c == self.player_col:
                    # Beautiful, cool space-shippy player spaceship facing down
                    # Thruster Flame at the top/rear of the ship
                    self.game_canvas.create_polygon(
                        rx + self.cell_w//2 - 5, ry + 4,
                        rx + self.cell_w//2 + 5, ry + 4,
                        rx + self.cell_w//2, ry,
                        fill=COLOR_YELLOW, outline=COLOR_RED
                    )
                    # Swept Wings
                    self.game_canvas.create_polygon(
                        rx + 2, ry + 4,
                        rx + self.cell_w//2 - 5, ry + 12,
                        rx + self.cell_w//2 - 2, ry + 20,
                        fill=COLOR_BLUE, outline=COLOR_WHITE
                    )
                    self.game_canvas.create_polygon(
                        rx + self.cell_w - 2, ry + 4,
                        rx + self.cell_w//2 + 5, ry + 12,
                        rx + self.cell_w//2 + 2, ry + 20,
                        fill=COLOR_BLUE, outline=COLOR_WHITE
                    )
                    # Main Central Hull pointing down
                    self.game_canvas.create_polygon(
                        rx + self.cell_w//2, ry + self.cell_h, # Nose tip
                        rx + self.cell_w//2 - 6, ry + 8,        # Left rear corner
                        rx + self.cell_w//2, ry + 14,          # Notch in rear
                        rx + self.cell_w//2 + 6, ry + 8,        # Right rear corner
                        fill=COLOR_CYAN, outline=COLOR_WHITE
                    )
                elif is_bullet:
                    # Player bullet fires down screen (Green plasma circle)
                    self.game_canvas.create_oval(rx + self.cell_w//2 - 6, ry + self.cell_h//2 - 6, rx + self.cell_w//2 + 6, ry + self.cell_h//2 + 6, fill=COLOR_GREEN, outline="")
                elif is_ebullet:
                    # Enemy bullet fires up screen (Red laser beam)
                    self.game_canvas.create_line(rx + self.cell_w//2, ry, rx + self.cell_w//2, ry + self.cell_h, fill=COLOR_RED, width=4)
                elif cell == "▲":
                    # Pointy alien space-shippy enemy pointing UPWARDS
                    self.game_canvas.create_polygon(
                        rx + self.cell_w//2, ry + 2,                  # Pointy nose tip pointing UP
                        rx + 2, ry + self.cell_h - 6,                 # Left wing tip
                        rx + self.cell_w//2 - 4, ry + self.cell_h - 10,# Left inner indent
                        rx + self.cell_w//2, ry + self.cell_h - 4,    # Rear notch
                        rx + self.cell_w//2 + 4, ry + self.cell_h - 10,# Right inner indent
                        rx + self.cell_w - 2, ry + self.cell_h - 6,   # Right wing tip
                        fill=COLOR_RED, outline=COLOR_YELLOW
                    )
                    # Central power core cockpit
                    self.game_canvas.create_oval(
                        rx + self.cell_w//2 - 4, ry + self.cell_h//2 - 4,
                        rx + self.cell_w//2 + 4, ry + self.cell_h//2 + 4,
                        fill=COLOR_YELLOW, outline=""
                    )
                elif cell == "G":
                    # Gem diamond
                    self.game_canvas.create_polygon(
                        rx + self.cell_w//2, ry,
                        rx + self.cell_w, ry + self.cell_h//2,
                        rx + self.cell_w//2, ry + self.cell_h,
                        rx, ry + self.cell_h//2,
                        fill=COLOR_GREEN, outline=""
                    )
                elif cell == "H":
                    # Beautiful custom polygon Heart shape
                    self.game_canvas.create_polygon(
                        rx + self.cell_w//2, ry + self.cell_h - 4,    # Bottom tip
                        rx + 2, ry + self.cell_h//2 - 2,              # Left waist
                        rx + 4, ry + 4,                               # Top left outer hump
                        rx + self.cell_w//2 - 1, ry + 6,              # Top center cleavage left
                        rx + self.cell_w//2, ry + 10,                 # Top center plunge
                        rx + self.cell_w//2 + 1, ry + 6,              # Top center cleavage right
                        rx + self.cell_w - 4, ry + 4,                 # Top right outer hump
                        rx + self.cell_w - 2, ry + self.cell_h//2 - 2,# Right waist
                        fill=COLOR_RED, outline=""
                    )
                elif cell == "S":
                    # Shield circle
                    self.game_canvas.create_oval(rx + 2, ry + 2, rx + self.cell_w - 2, ry + self.cell_h - 2, outline=COLOR_BLUE, width=2)
                    self.game_canvas.create_oval(rx + self.cell_w//2 - 4, ry + self.cell_h//2 - 4, rx + self.cell_w//2 + 4, ry + self.cell_h//2 + 4, fill=COLOR_CYAN, outline="")
                elif cell == ".":
                    self.game_canvas.create_oval(rx + self.cell_w//2 - 2, ry + self.cell_h//2 - 2, rx + self.cell_w//2 + 2, ry + self.cell_h//2 + 2, fill=COLOR_GREY, outline="")
                elif cell == "═":
                    self.game_canvas.create_rectangle(rx, ry + self.cell_h//3, rx + self.cell_w, ry + 2*self.cell_h//3, fill=COLOR_YELLOW, outline="")
                elif cell != " ":
                    # Meteor brown block
                    self.game_canvas.create_rectangle(rx + 2, ry + 2, rx + self.cell_w - 2, ry + self.cell_h - 2, fill="#503228", outline="#966E50")

        # Update and Render Particles
        active_parts = []
        for p in self.particles:
            p[0] += p[2]
            p[1] += p[3]
            p[6] -= 1
            if p[6] > 0:
                self.game_canvas.create_oval(p[0] - p[5], p[1] - p[5], p[0] + p[5], p[1] + p[5], fill=p[4], outline="")
                active_parts.append(p)
        self.particles = active_parts

        # Draw HUD interface at top
        self.game_canvas.create_rectangle(0, 0, 600, 80, fill="#0F0F1E", outline=COLOR_CYAN, width=2)

        # Lives text
        self.game_canvas.create_text(80, 25, text=f"Lives: {self.lives}/10", font=("Courier New", 14, "bold"), fill=COLOR_RED, anchor="w")
        # Shields text
        self.game_canvas.create_text(80, 55, text=f"Shields: {self.special_shields}/5", font=("Courier New", 14, "bold"), fill=COLOR_CYAN, anchor="w")

        # Scores text
        self.game_canvas.create_text(350, 25, text=f"Score: {self.game_score}", font=("Courier New", 14, "bold"), fill=COLOR_GREEN, anchor="w")
        self.game_canvas.create_text(350, 55, text=f"Level: {self.game_level}", font=("Courier New", 14, "bold"), fill=COLOR_WHITE, anchor="w")

        if gmode == 1:
            self.game_canvas.create_text(220, 55, text=f"Ammo: {self.bullets_left}", font=("Courier New", 12, "bold"), fill=COLOR_YELLOW)

    def show_game_over_screen(self):
        self.unbind_all("<Key>")
        self.game_canvas.delete("all")

        # Background
        self.game_canvas.create_text(300, 200, text="GAME OVER", font=("Courier New", 36, "bold"), fill=COLOR_RED)

        lvl_bonus = self.game_level * 10 * difficulty
        final_fs = self.game_score + lvl_bonus

        self.game_canvas.create_text(300, 280, text=f"Score: {self.game_score}", font=("Courier New", 18), fill=COLOR_WHITE)
        self.game_canvas.create_text(300, 330, text=f"Level Bonus: +{lvl_bonus}", font=("Courier New", 18), fill=COLOR_WHITE)
        self.game_canvas.create_text(300, 390, text=f"FINAL SCORE: {final_fs}", font=("Courier New", 24, "bold"), fill=COLOR_GREEN)

        self.game_canvas.create_text(300, 460, text="Enter your initials (3 Letters):", font=("Courier New", 14, "bold"), fill=COLOR_YELLOW)

        # We create an entry widget for initials typing
        entry = tk.Entry(self, font=("Courier New", 24, "bold"), width=5, justify="center")
        self.game_canvas.create_window(300, 520, window=entry)
        entry.focus_set()

        def save_and_return():
            name = entry.get().strip().upper()
            if len(name) != 3:
                messagebox.showwarning("Initials", "Please enter exactly 3 letters!")
                return
            save_local_score(name, final_fs, self.game_score, lvl_bonus, self.game_level, difficulty, self.gems_count, self.damage_taken)
            self.show_main_menu()

        # Save Button
        save_btn = tk.Button(self, text="Save Score", font=("Courier New", 14, "bold"), command=save_and_return)
        self.game_canvas.create_window(300, 600, window=save_btn)

if __name__ == "__main__":
    app = GameApp()
    app.mainloop()

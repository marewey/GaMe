# Gems and Meteors (GaM)
An action-packed arcade scrolling game of skill and reflexes! Avoid the cascading meteors, collect precious gems, hearts, and shields, and survive as long as possible.

We have optimized the original **Windows Batch Edition** and created **two brand-new Python Editions** (a retro Terminal CLI version and a stunning Pygame Graphical Edition) for you to test and play!

---

## Game Features Included Across All Editions
1. **Configurable Spaceship Customization**: Select your favorite downward-pointing spaceship (defaulting to a cool retro `🛸` or various other retro icons like `▼`, `v`, `∇`, `⛛`, `⧩`).
2. **Two Game Modes**:
   - **Endless Mode**: Classic survival scrolling getting progressively faster over time.
   - **Levels Mode**: Dodge cascading obstacles, shoot down active enemy ships (▲), and successfully land in the middle column on the yellow **Landing Strip** at the bottom of the map to save progress and advance to the next level!
3. **Dynamic Difficulty & Scaling**: Adjust starting difficulty (Easy, Medium, Hard, Expert). Column widths scale with difficulty, and scroll speed increases dynamically as your score grows!
4. **Interactive Combat (Levels Mode)**:
   - Since the world scrolls UPWARDS relative to the player at the top, **Player's bullets are fired DOWNWARDS** (`+y` direction) to destroy meteors and enemies, and to retrieve items instantly with visual flashes.
   - **Enemies are spawned at the bottom** and fire bullets/lasers **UPWARDS** (`-y` direction) towards the player.
   - Shields (`☼` or circles) function as weapon reloads. Fire lasers to obliterate meteors and enemy craft.
5. **Enhanced Pause Menus**: Smooth in-game pause screens with sound toggles (Mute/Unmute) and Quit options.
6. **Local Leaderboard**: Keeps track of your best runs offline, saving scores locally and merging them seamlessly with online score caching.

---

## How to Test and Run the 3 Editions on your Windows PC

### 1. Windows Batch Edition (`GaMe.bat`)
*This is your updated, optimized original Batch file!*

* **Prerequisites**: No dependencies required. Natively runs on Windows.
* **How to Run**:
  1. Simply double-click **`GaMe.bat`** in your file explorer.
  2. Alternatively, open a Command Prompt (cmd) window, navigate to the folder, and type:
     ```cmd
     GaMe.bat
     ```
  3. Ensure your console codepage supports UTF-8 (the batch file will automatically configure this to use symbols like `🛸` and `♦`).

---

### 2. Python Terminal CLI Edition (`game_cli.py`)
*A silky-smooth, flicker-free command-line interface with native double-buffered rendering and Windows MCI audio! Fully standalone with Base64 audio embedded in-memory.*

* **Prerequisites**: Python 3 must be installed. No third-party modules are required!
* **How to Run**:
  1. Open a Command Prompt or PowerShell window in the game directory.
  2. Launch the script using python:
     ```cmd
     python game_cli.py
     ```
  3. Customize your spaceship in the settings menu, toggle sound options, and enjoy!

---

### 3. Pygame Graphical Edition (`game_gui.py`)
*A gorgeous, modern arcade-style graphical edition with scrolling starfields, custom animations, pop-up text, particle burst explosions, and native Pygame mixer music!*

* **Prerequisites**: Python 3 must be installed. Pygame is used for graphics, and the script **automatically installs pygame on startup** if you don't have it!
* **How to Run**:
  1. Open a Command Prompt or PowerShell window in the game directory.
  2. Launch the script using python:
     ```cmd
     python game_gui.py
     ```
  3. The script will check for the Pygame library, automatically download the sound files (gem, heart, damage, explosion, music) from the remote server if they are missing in your local `cache/` folder, and launch the graphical game window.
  4. Use **Arrow keys / WASD** to move smoothly, **Space/Enter** to shoot, and **ESC** to pause.

---

### File Hierarchy
- `GaMe.bat` - Optimized Windows Batch version.
- `game_cli.py` - Standalone Terminal CLI Python edition.
- `game_gui.py` - Smooth, graphical Pygame window edition.
- `cache/` - Sound effect resources (mp3 and wav files).
- `data/` - High score registries and settings data.

Have fun testing all three editions! Let us know which one you like best!

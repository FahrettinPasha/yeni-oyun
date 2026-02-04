# Fragmentia: Truth & Betrayal (Neon Runner)

![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)
![Pygame](https://img.shields.io/badge/Pygame-CE-green)
![Gemini AI](https://img.shields.io/badge/AI-Google%20Gemini-orange)
![Status](https://img.shields.io/badge/Status-Experimental-yellow)

**Fragmentia** is an experimental narrative-driven runner built with Pygame. 

The core idea was to push the limits of what a standard Python game loop can do by integrating a Large Language Model (Google Gemini) not just as a chatbot, but as a "Dungeon Master" that has write-access to the game's physics engine.

There are no sprite sheets in this repo. Every visual and sound effect is generated procedurally via code.

## 🚀 Why This Project Exists

I built this to explore three specific technical challenges:

1.  **Real-Time AI Control:** Can an LLM change the game difficulty on the fly?
    *   *Solution:* The `StoryManager` class sends game state data to Gemini. The AI responds with text for dialogue, but also injects hidden **JSON commands**. The game parses these to alter gravity, speed, or trigger visual glitches in real-time.
    
2.  **Procedural Asset Generation:** Can we make a game look good without external assets?
    *   *Solution:* All entities are drawn using math and `pygame.draw`.
    *   *Audio:* If `.wav` files are missing, the game uses `numpy` to generate sine-wave sound effects and ambient drones instantly. The game never crashes due to missing assets.

3.  **Dynamic Narrative (Karma System):**
    *   The game tracks behavioral data (kills vs. saves).
    *   **Low Karma:** Triggers "Genocide Mode." Bosses mutate (e.g., Ares), visual themes turn red/corrupted.
    *   **High Karma:** Unlocks "Redemption Mode" and the "Talisman" mechanic, allowing you to save enemies instead of destroying them.

## 🛠️ Tech Stack & Architecture

*   **Engine:** Pygame CE (Community Edition).
*   **AI:** `google.generativeai` (Gemini 2.5 Flash).
*   **Physics:** Custom AABB collision with "Squash & Stretch" procedural animation logic (`CharacterAnimator` class).
*   **VFX:** Custom particle system for explosions, trails, and CRT monitor effects.

### File Structure Highlight
*   `main.py`: The central State Machine (Menu, Game, Cutscene loops).
*   `story_system.py`: Handles the async API calls and JSON command parsing.
*   `boss_manager.py`: Logic for the 3 distinct boss types (Nexus, Ares, Vasil) and their phase transitions.
*   `vfx.py` & `cutscene.py`: Handles the matrix rain, glitches, and particle rendering.

## 📸 Screenshots

*(Eklenecek!)*

## ⚙️ Installation

1.  **Clone the repo:**
    ```bash
    git clone https://github.com/FahrettinPasha/fragmentia.git
    cd fragmentia
    ```

2.  **Install dependencies:**
    ```bash
    pip install pygame google-generativeai numpy
    ```

3.  **API Key Setup (Optional but Recommended):**
    *   Get a free API key from [Google AI Studio](https://aistudio.google.com/).
    *   Open `settings.py` (or the relevant config file).
    *   Set `GENAI_API_KEY = "YOUR_KEY_HERE"`.
    *   *Note: The game runs fine without a key, but the AI dialogue and dynamic world events will be disabled.*

4.  **Run:**
    ```bash
    python main.py
    ```

## 🎮 Controls

| Key | Action | Context |
| :--- | :--- | :--- |
| **W / Space** | Jump / Double Jump | Movement |
| **A / D** | Move Left / Right | Movement |
| **Space** | Dash Attack | While on ground |
| **S** | Slam Attack | While in air |
| **E** | Interact | Talk to NPCs in Rest Areas |
| **R** | Redemption Mode | Trigger in Limbo (Level 99) |
| **G** | Genocide Mode | Trigger in Limbo (Level 99) |
| **P** | Pause | System |

## 📄 License

**MIT License**

I built this for fun and to experiment with code. You are free to use, modify, distribute, or sell this code however you want. No strings attached.

I only ask that you don't blame me if it bugs out on your machine. Enjoy!

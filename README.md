FRAGMENTIA: Truth and Betrayal - Complete Technical Documentation
📋 Table of Contents
Project Overview
Architecture Overview
System Components
Data Structures and Flow
Game Physics
Visual Effects System
AI and Story System
Boss Management System
Setup and Configuration
Performance Optimization
Debugging and Development
Project Overview
📖 Concept
Fragmentia: Truth and Betrayal - A 2D platformer game written in Pygame with a cyberpunk theme. Players progress through layers of a dystopian digital city, making philosophical choices through a karma system that shapes the narrative.

🎮 Core Mechanics
Platform Running: Movement through dynamically generated platforms moving left-to-right
Karma System: Values ranging from -1000 (Genocide Mode) to +1000 (Redemption Mode) determining story outcomes
Three Endings: Different conclusions based on final karma value (Limbo-Vasil, Limbo-Ares, or Normal End)
Level Progression: 15 levels + hidden chapters (11-14), each with unique theme and difficulty
AI Integration: Google Gemini 2.5 Flash API for dynamic dialogue and world manipulation
🔧 Technical Stack
Engine: Pygame 2.x
Language: Python 3.8+
AI: Google Generative AI (Gemini 2.5 Flash Preview)
Audio: Pygame mixer + NumPy
Resolution: 1920x1080 (logical) - scalable
FPS Target: 60 FPS
Platforms: Windows/Linux (Fullscreen + VSYNC)
Architecture Overview
Code
FRAGMENTIA ARCHITECTURE
├── 📊 CORE ENGINE
│   ├── main.py (Game Loop & State Machine)
│   ├── settings.py (Configuration & Constants)
│   └── save_system.py (Persistence Layer)
│
├── 🎮 GAMEPLAY SYSTEMS
│   ├── entities.py (Player, Enemies, NPCs, Platforms)
│   ├── animations.py (Character & VFX Animation)
│   ├── boss_manager.py (Boss Attack Patterns)
│   └── boss_entities.py (Boss & Attack Objects)
│
├── 📚 STORY & WORLD
│   ├── story_system.py (Narrative & AI Chat)
│   ├── cutscene.py (Cutscene Rendering)
│   ├── auxiliary_systems.py (World Systems Stubs)
│   └── game_config.py (Level & Theme Data)
│
├── 🎨 GRAPHICS & VFX
│   ├── drawing_utils.py (Cinematic Rendering)
│   ├── ui_system.py (UI Elements)
│   ├── vfx.py (Particle & Effects)
│   └── animations.py (Character States)
│
└── 🛠️ UTILITIES
    ├── utils.py (Audio Loading & Text Wrapping)
    └── lexical-code-search (Semantic Search)
State Machine (Main State Machine)
Code
GAME_STATE Transitions:

┌─────────────────────────────────────────────┐
│                                             │
│         MENU → LEVEL_SELECT                 │
│              ↓                              │
│         LOADING → PLAYING                   │
│              ↓                              │
│    PLAYING ←→ PAUSED                        │
│         ↓                                   │
│    LEVEL_COMPLETE/GAME_OVER                 │
│         ↓                                   │
│    MENU (Restart)                           │
│                                             │
│    Special States:                          │
│    - CUTSCENE (Story)                       │
│    - REST_AREA (Safe Zone)                  │
│    - NPC_CHAT (Dialog)                      │
│    - SETTINGS (Config)                      │
└─────────────────────────────────────────────┘
System Components
1. main.py - Game Loop and Main Controller
Core Structure
Python
class GameLoop:
    - clock: pygame.time.Clock()
    - screen: pygame.display.Surface (LOGICAL_WIDTH x LOGICAL_HEIGHT)
    - game_canvas: pygame.Surface (offscreen rendering)
    - vfx_surface: pygame.Surface (for alpha blending)
    
    Core Methods:
    ├── init_game()          # Initialize level & objects
    ├── run_game_loop()      # Main loop (60 FPS)
    ├── handle_input()       # Process events
    ├── update_physics()     # Physics calculations
    ├── render()             # Draw frame
    └── cleanup()            # Resource deallocation
Key Features
VSYNC Enabled: Smooth 60 FPS guarantee
Double Buffering: pygame.HWSURFACE
Scaled Display: Logical 1920x1080 → Physical resolution
Frame Multiplier: frame_mul = actual_dt / (1/60) (physics consistency)
Main Loop Pseudocode
Code
while GAME_STATE != 'EXIT':
    dt = clock.tick(60) / 1000.0  # Seconds
    frame_mul = dt * 60.0          # Physics scaling
    
    HANDLE EVENTS
    ├── Process Input
    ├── Update State Machine
    └── Handle UI Clicks
    
    UPDATE (if PLAYING):
    ├── Player Physics
    │   ├── Gravity & Velocity
    │   ├── Jump/Dash/Slam Logic
    │   └── Platform Collision
    ├── Camera Movement
    ├── Enemy AI & Collision
    ├── Boss Manager Updates
    ├── Animation Manager
    └── Particle Systems
    
    RENDER:
    ├── Clear Buffers
    ├── Draw Background & Grid
    ├── Draw Platforms
    ├── Draw Player (Animated)
    ├── Draw Enemies & Effects
    ├── Draw VFX Layers
    ├── Draw UI/HUD
    └── Flip Display
2. settings.py - Configuration and Constants
Critical Variables
Python
# 🖥️ DISPLAY
LOGICAL_WIDTH = 1920
LOGICAL_HEIGHT = 1080
FPS = 60
AVAILABLE_RESOLUTIONS = [(3840,2160), (1920,1080), ...]

# 🎮 PHYSICS
GRAVITY = 1.0                    # Pixels/frame²
JUMP_POWER = 28                  # Pixels/frame
PLAYER_SPEED = 10                # Pixels/frame (horizontal)
MAX_JUMPS = 2                    # Double-jump
SLAM_GRAVITY = 5.0               # Increased gravity during slam

# ⚡ DASH MECHANICS
DASH_SPEED = 90                  # Pixels/frame
DASH_DURATION = 18               # Frames (0.3 seconds @ 60 FPS)
DASH_COOLDOWN = 60               # Frames (1 second)

# 💥 SLAM MECHANICS
SLAM_COOLDOWN_BASE = 100         # Frames (1.67 seconds)
SLAM_STALL_TIME = 8              # Hang time at peak
SLAM_COLLISION_CHECK = 3         # Frames to check collision

# 📷 CAMERA
INITIAL_CAMERA_SPEED = 5         # Pixels/frame
MAX_CAMERA_SPEED = 18
SPEED_INCREMENT_RATE = 0.001     # Per frame
PLATFORM_MIN_WIDTH = 100
PLATFORM_MAX_WIDTH = 300
GAP_MIN = 120
GAP_MAX = 250
VERTICAL_GAP = 180

# 🎨 THEMES
THEMES = [
    {
        "name": "NEON MARKET",
        "bg_color": (5, 5, 10),
        "platform_color": (10, 10, 15),
        "border_color": (0, 255, 255),
        ...
    },
    # 4 more themes...
]

# 🎵 AUDIO
VOLUME_SETTINGS = {
    "master_volume": 0.7,
    "music_volume": 0.5,
    "effects_volume": 0.8
}

# 🤖 AI
GENAI_API_KEY = ""  # INSERT YOUR OWN KEY HERE
AI_MODEL_NAME = 'gemini-2.5-flash-preview-09-2025'
FRAGMENTIA_SYSTEM_PROMPT = """..."""

# 📊 LEVEL DATA
EASY_MODE_LEVELS = {
    1: {...},   # Level 1-9: Normal
    10: {...},  # Boss Fight (Scrolling Boss)
    11-14: {...}, # Hidden chapters
    15: {...}   # Final Challenge
}
Theme System
Python
# Each theme defines:
Theme = {
    "name": str,
    "bg_color": (R, G, B),
    "platform_color": (R, G, B),
    "border_color": (R, G, B),
    "player_color": (R, G, B),
    "grid_color": (R, G, B)
}

# 5 Themes:
0: NEON MARKET          (Cyan/Dark Blue)
1: SOVEREIGNS' TOWER    (Red/Orange)
2: MEMORY DUMP          (Gray/White)
3: THE GUTTER           (Green/Dark)
4: SAFE ZONE            (Light Blue)
3. entities.py - Game Objects
Player Object Model
Python
# Player State
player_state = 'idle' | 'running' | 'jumping' | 'falling' | 'dashing' | 'slamming'

# Player Physics
player_x: float                 # X position
player_y: float                 # Y position
y_velocity: float               # Vertical speed (pixels/frame)
is_jumping: bool                # Currently in jump?
is_dashing: bool                # Currently dashing?
is_slamming: bool               # Currently slam-attacking?
is_grounded: bool               # On platform?
jumps_left: int                 # Remaining jumps (0-2)
dash_timer: float               # Frames into dash
dash_cooldown_timer: float      # Frames until dash ready
slam_stall_timer: float         # Hang time
slam_cooldown_timer: float      # Frames until slam ready
dash_angle: float               # Dash direction (radians)

# Map Objects
class Platform(pygame.sprite.Sprite):
    """Platform Object"""
    x, y: int                   # Position
    width, height: int          # Dimensions
    theme_index: int            # Visual style (0-4)
    rect: pygame.Rect          # Collision rect
    
    Methods:
    ├── draw()          # Render with theme
    ├── update()         # Camera panning
    └── activate_hover() # Hover effect

class Star(pygame.sprite.Sprite):
    """Background parallax star"""
    x, y: float
    speed: float               # Parallax depth
    Methods: update(), draw()

class EnemyBase:
    """Base class for all enemies"""
    health: int
    x, y: float
    rect: pygame.Rect
    Methods:
    ├── update()              # AI & physics
    ├── draw()                # Render
    ├── take_damage()         # Damage logic
    └── update_speech()       # Dialog

class CursedEnemy(EnemyBase):
    """Haunted entity"""
    spawn_platform: Platform
    animation_state: 'idle' | 'attacking' | 'damaged'
    color: (R,G,B) = (150, 0, 255)

class DroneEnemy(EnemyBase):
    """Flying drone"""
    x, y: float               # Free position
    flight_pattern: 'sine' | 'random'
    target_player: bool

class TankEnemy(EnemyBase):
    """Heavy armored tank"""
    armor_level: int
    jump_height: float
    charging: bool

class NPC:
    """Non-player character for rest areas"""
    name: str
    color: (R,G,B)
    personality_type: 'philosopher' | 'warrior' | 'mystic' | 'guide'
    x, y: float
    
    Methods:
    ├── update()                    # Movement & animation
    ├── draw()                      # Render with eyes
    ├── generate_greeting()         # AI greeting
    ├── start_conversation()        # Init dialog
    ├── send_message()              # Process player input
    └── end_conversation()          # Clean up
Enemy AI Patterns
Python
# CursedEnemy: Platform-bound patrol
├── State: IDLE
│   └── Wander left-right on platform
├── State: ATTACKING
│   ├── Fire projectile at player
│   └── If player in range: charge
└── State: DAMAGED
    └── Brief stun & knockback

# DroneEnemy: Airborne predator
├── Sine wave flight pattern (height ±50px)
├── Targets player if distance < 400px
├── Fires homing projectile every 1.5s
└── Patrol randomly if player not visible

# TankEnemy: Slow but powerful
├── Stationary on platform
├── Every 2s: charges towards player
├── Jump attack if player above
└── High health (200 HP)
4. animations.py - Animation System
CharacterAnimator
Python
class CharacterAnimator:
    def __init__(self):
        self.state = 'idle'
        self.frame_index = 0
        self.animation_timer = 0
        
        # Frame data per state
        self.frame_data = {
            'idle': {
                'frames': 4,
                'speed': 0.15,      # Animation speed multiplier
                'colors': [base, pulse1, pulse2, pulse3]
            },
            'running': {
                'frames': 6,
                'speed': 0.25,
                'offset_y': [-2, -4, -2, 0, 2, 0]  # Bounce effect
            },
            'jumping': {
                'frames': 3,
                'speed': 0.3,
                'scale': [0.9, 1.0, 1.1]  # Squash/stretch
            },
            'dashing': {
                'frames': 5,
                'speed': 0.4,
                'glow_intensity': [0.5, 1.0, 0.8, 0.6, 0.4]
            },
            'slamming': {
                'frames': 2,
                'speed': 0.3,
                'rotation': [0, 45, 90, 135, 180]
            }
        }
        
    Methods:
    ├── update()                    # Process frame animation
    ├── _update_idle()              # Idle state logic
    ├── _update_running()           # Running state logic
    ├── _update_jumping()           # Jump animation
    ├── _update_falling()           # Fall animation
    ├── _update_dashing()           # Dash animation
    ├── _update_slamming()          # Slam animation
    ├── _update_frame_animation()   # Frame ticker
    ├── _update_extra_effects()     # Glow, trails, etc.
    ├── get_draw_params()           # Color, scale, rotation
    ├── get_modified_color()        # Karma-based coloring
    ├── get_glow_color()            # Glow effect color
    └── trigger_impact()            # Slam impact particles
Trail Effects
Python
class TrailEffect:
    """Motion blur trail left by player"""
    x, y: float
    color: (R,G,B)
    size: float
    life: int                       # Frames remaining
    
    Animation:
    ├── Fade out (life decay)
    ├── Shrink (size → 0)
    └── Glitch offset (jitter)

# Trail Pool Management:
MAX_TRAIL_PARTICLES = 120
trail_effects: List[TrailEffect]    # Pool allocated at start
TRAIL_INTERVAL = 3                  # Frames between trails
Particle System
Python
class ElectricParticle(pygame.sprite.Sprite):
    """Electrical charge particle (slam impact)"""
    x, y: float
    color: (R,G,B)
    life: int
    Methods:
    ├── _generate_arc()    # Lightning arc path
    ├── update()           # Physics & decay
    └── draw()             # Render arc

class ParticleExplosion:
    """Multi-particle burst (damage, collision)"""
    particles: List[{
        x, y, vx, vy,
        size, initial_size,
        life, initial_life,
        color, rotation, rot_speed
    }]
    
    Spawning: count (default 20)
    Distribution: uniform 0-360°
    Speed: 4-12 px/frame
    
# Pools:
AFTERIMAGE_POOL_SIZE = 6
MAX_IMPACT_PARTICLES = 300
5. story_system.py - Story and AI System
StoryManager
Python
class StoryManager:
    def __init__(self):
        self.current_text: str              # Current dialog text
        self.display_text: str              # Animated text
        self.char_index: float              # Writing progress (0 → len)
        self.state: 'IDLE'|'TYPING'|'WAITING_INPUT'|'THINKING'|'FINISHED'
        self.speaker: str                   # Speaking character name
        self.text_speed: float = 0.5        # Characters/frame
        
        # AI Integration
        self.ai_active: bool                # Gemini connection active?
        self.chat_session                   # Ongoing conversation
        self.model: genai.GenerativeModel   # Gemini instance
        self.ai_thinking: bool
        self.conversation_history: List     # Chat logs
        
        # Chapter System
        self.current_chapter: int
        self.dialogue_index: int
        self.chapter_data: Dict
        self.dialogue_queue: List
        
        # World Modifiers (changed by AI)
        self.world_modifiers = {
            "gravity_mult": 1.0,
            "speed_mult": 1.0,
            "glitch_mode": False
        }

    Methods:
    ├── setup_ai()                          # Initialize Gemini API
    ├── load_chapter()                      # Load story chapter
    ├── next_line()                         # Advance dialog
    ├── set_dialogue()                      # Direct dialog set
    ├── send_ai_message()                   # Player message → AI
    ├── generate_npc_response()             # Stateless NPC response
    ├── extract_commands()                  # Parse JSON from AI
    ├── apply_world_modifiers()             # Apply physics changes
    └── update()                            # Animation tick
AI Integration Flow
Code
Player Input (Chat/Dialog)
        ↓
send_ai_message(text, game_context)
        ↓
context_str = "[SYSTEM DATA: Score=X, Deaths=Y]"
full_prompt = context_str + user_text
        ↓
chat_session.send_message(full_prompt)
        ↓
Gemini Response (Text + Optional JSON)
        ↓
extract_commands()
├── Find ```json { ... } ```
├── Parse JSON
└── Remove from display text
        ↓
apply_world_modifiers()
├── Adjust gravity_mult
├── Adjust speed_mult
└── Enable glitch_mode
        ↓
Display Response to Player
Story Chapter Structure
Python
STORY_CHAPTERS = {
    0: {
        "title": "THE GUTTER: AWAKENING",
        "background_theme": 2,      # Dump Theme
        "dialogues": [
            {
                "speaker": "SYSTEM",
                "text": "PATCH PROCESS FAILED...",
                "type": "cutscene"
            },
            {
                "speaker": "???",
                "text": "Open your eyes...",
                "type": "chat"
            },
            # ... more dialogs
        ],
        "next_state": "PLAYING",
        "next_level": 1
    }
}
NPC AI Prompt System
Python
NPC_PERSONALITIES = [
    "philosopher", "warrior", "mystic", "guide", "merchant"
]

NPC_PROMPTS = {
    "philosopher": "Welcome 'Nameless'...",
    "warrior": "Your score is rising...",
    "mystic": "In my dreams, glass towers...",
    "guide": "There's a way out...",
    "merchant": "SYSTEM ERROR: MERCHANT PROTOCOL DISABLED."
}

# NPC-specific system prompt (generate_npc_response):
system_prompt = f"""
Role-Playing Game Mode:
Your Name: {npc.name}
Your Personality Type: {npc.personality_type}
Your Role/Task: "{npc.prompt}"

Your Universe: Fragmentia (Cyberpunk, dystopian)

Rule: You are speaking with the player. NEVER break character.
Give short, concise, character-appropriate responses (Max 2-3 sentences).

Conversation so far:
{history_text}

The player just said: "{user_text}"

{npc.name}'s response:
"""
Data Structures and Flow
Player Data Model
Python
# Save File (save_data.json)
{
    "karma": int,                   # -1000 to +1000
    "saved_souls": int,             # Count of redeemed enemies
    "easy_mode": {
        "unlocked_levels": int,     # Max level available
        "completed_levels": [1, 2, 5, ...],
        "high_scores": {
            "1": 5000,
            "2": 12000,
            ...
        }
    },
    "settings": {
        "sound_volume": 0.7,
        "music_volume": 0.5,
        "effects_volume": 0.8
    }
}
Enemy Data Model
Python
class Enemy {
    id: unique_id
    type: 'cursed' | 'drone' | 'tank'
    health: int                     # 10-200
    x, y: float
    rect: pygame.Rect
    velocity: (vx, vy)
    state: 'idle' | 'attacking' | 'damaged' | 'dead'
    
    # Behavior
    ai_timer: float
    target_player: bool
    damage_value: int               # Dealt to player
    speech_bubble: str
    speech_timer: float
}
Platform Data Model
Python
class Platform {
    id: unique_id
    x, y: int                       # Left, Top
    width, height: int              # Dimensions
    theme_index: int                # 0-4 (visual style)
    rect: pygame.Rect
    active: bool
    hover_effect_active: bool
}
Camera and Viewport
Code
Viewport (Screen Space):
┌─────────────────────────────────────────────────────────────┐
│                   LOGICAL_WIDTH = 1920                      │
│   ┌───────────────────────────────────────────────────────┐ │
│   │              LOGICAL_HEIGHT = 1080                     │ │
│   │  (0,0)                                    (1920,1080)  │ │
│   │   └──────────────────────────────────────────────┘    │ │
│   │                                                        │ │
│   │  Render everything here (game_canvas)                 │ │
│   │                                                        │ │
│   └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘

World Space:
Infinite scroll → right
Platforms spawn dynamically at camera_x + 1920
Platforms despawn when camera_x > platform.x + platform.width

camera_offset = camera_x (horizontal panning)
Game Physics
Gravity and Velocity System
Python
# Gravity (Constant acceleration)
GRAVITY = 1.0                       # pixels/frame² 
y_velocity += GRAVITY * frame_mul   # Add each frame

# Max fall speed (terminal velocity)
MAX_FALL_SPEED = 30                 # pixels/frame
y_velocity = min(y_velocity, MAX_FALL_SPEED)

# Collision Detection
def check_platform_collision(player_rect, platforms):
    for platform in platforms:
        if player_rect.colliderect(platform.rect):
            if y_velocity > 0:      # Falling onto platform
                player_y = platform.rect.top - player_rect.height
                y_velocity = 0
                is_grounded = True
                jumps_left = MAX_JUMPS  # Reset jumps
                return True
    return False
Jump Mechanics
Python
# Input: SPACE key pressed
if not is_jumping and jumps_left > 0:
    y_velocity = -JUMP_POWER        # Upward velocity
    jumps_left -= 1
    is_jumping = True
    jump_timer = 0
    play_sound(JUMP_SOUND)

# Update during jump
jump_timer += frame_mul
if jump_timer > JUMP_DURATION:
    is_jumping = False              # Can't continue holding

# Variable jump height (holding longer = higher)
if is_jumping and SPACE_HELD:
    y_velocity *= 0.98              # Slight sustained lift
else:
    # Gravity pulls down harder when released
    y_velocity += GRAVITY * 2 * frame_mul
Dash Mechanics
Code
STATE: DASHING

Initial:
├── dash_angle = angle to movement input
├── dash_velocity_x = cos(angle) * DASH_SPEED
├── dash_velocity_y = sin(angle) * DASH_SPEED
└── dash_timer = 0

Per Frame:
├── x += dash_velocity_x * frame_mul
├── y += dash_velocity_y * frame_mul
├── dash_timer += frame_mul
└── Spawn trail particles every 2 frames

End (dash_timer > DASH_DURATION):
├── dash_timer = 0
├── dash_cooldown_timer = DASH_COOLDOWN
├── y_velocity = 0 (reset gravity)
└── state = 'falling'

VFX:
├── SpeedLine particles (motion blur)
├── GhostTrail (afterimage)
└── ScreenShake (intensity 2)
Slam Attack Mechanics
Code
STATE: SLAMMING

Phase 1: STARTUP (0-8 frames)
├── Gravity = SLAM_GRAVITY (5.0)
├── Animation: rotate 90°
├── VFX: Aura glow
└── Can't change direction

Phase 2: STALL (8-16 frames)
├── y_velocity = 0 (hang time)
├── Animation: rotate 180°
└── Screen shake builds

Phase 3: FALL (16+ frames)
├── y_velocity += SLAM_GRAVITY
├── Lightning trails spawn
└── Check collision each frame

Collision:
├── If platform hit:
│   ├── Shockwave VFX
│   ├── Screen flash
│   ├── Damage all enemies in radius (100px)
│   ├── Knockback enemies (velocity.y = -15)
│   └── Reset slam cooldown
└── If fall off screen:
    └── Reset to last platform
Platform Collision Detail
Python
def update_player_collision(player_rect, platforms, camera_speed):
    # Update player position with camera
    player_rect.x -= camera_speed * frame_mul
    
    # Check against all visible platforms
    for platform in platforms:
        if player_rect.colliderect(platform.rect):
            # Only collide if falling (y_velocity > 0)
            if y_velocity > 0:
                # Landing
                player_y = platform.rect.top - player_rect.height
                y_velocity = 0
                is_grounded = True
                jumps_left = MAX_JUMPS
                return platform
            
            # Hitting from below (ceiling)
            elif y_velocity < 0 and player_rect.bottom >= platform.rect.top:
                y_velocity = 0
    
    is_grounded = False
    return None
Visual Effects System
VFX Architecture
Python
# VFX Manager (Central)
all_vfx = pygame.sprite.Group()

# Main VFX Classes
├── LightningBolt
│   ├── Jagged segments
│   ├── Multi-layer rendering (glow, core, white)
│   └── Life-based fade
│
├── FlameSpark
│   ├── Particle burst (explosion)
│   ├── Physics: gravity + drag
│   └── Size shrinking + alpha fade
│
├── Shockwave
│   ├── Expanding rings
│   ├── Multiple layers with offset
│   └── Perlin noise ripple (optional)
│
├── SpeedLine
│   ├── Dash motion blur
│   ├── Direction-based angle
│   └── Quick decay
│
├── GhostTrail
│   ├── Afterimage duplicate
│   ├── Scanline hologram effect
│   └── Jitter/glitch displacement
│
├── EnergyOrb
│   ├── Floating pickup visual
│   ├── Concentric circles
│   └── Pulse animation
│
└── ParticleExplosion
    ├── 20+ particles per explosion
    ├── Radial distribution
    ├── Rotatable squares
    └── Life-based color shift
LightningBolt Generation
Python
def create_bolt(x1, y1, x2, y2, displace=15):
    """Jagged lightning path (recursive subdivision)"""
    segments = [(x1, y1)]
    
    dx, dy = x2 - x1, y2 - y1
    length = sqrt(dx² + dy²)
    
    if length < 0.01:
        segments.append((x2, y2))
        return segments
    
    # Perpendicular offset
    perp_x = -dy / length
    perp_y = dx / length
    
    # Midpoint displacement
    num_points = max(3, int(length / 8))
    for i in range(1, num_points):
        t = i / num_points
        mid_x = x1 + t * dx
        mid_y = y1 + t * dy
        
        # Random offset perpendicular to line
        offset = random(-displace, displace) * (1 - |t - 0.5| * 2)
        
        jagged_x = mid_x + offset * perp_x
        jagged_y = mid_y + offset * perp_y
        segments.append((jagged_x, jagged_y))
    
    segments.append((x2, y2))
    return segments
Rendering Pipeline
Code
Frame Render Order:
1. Clear game_canvas (fill BG color)
2. Draw stars (parallax layer)
3. Draw platforms (base layer)
4. Draw particles (mid layer)
   - Trails
   - Particles
5. Draw player (character layer)
6. Draw enemies (character layer)
7. Draw VFX (top layer)
   - Lightning
   - Shockwaves
   - Explosions
8. Draw UI (HUD layer)
   - Health/Score
   - Karma bar
9. Screen shake offset applied to all
10. Flip display
Screen Shake
Python
class ScreenShakeLite:
    def __init__(self):
        self.intensity = 0
        self.duration = 0
        self.timer = 0
        self.current_offset = (0, 0)
    
    def shake(self, intensity, duration):
        self.intensity = intensity
        self.duration = duration
        self.timer = 0
    
    def update(self, dt):
        if self.timer < self.duration:
            self.timer += dt
            progress = self.timer / self.duration
            current_intensity = self.intensity * (1 - progress)
            
            offset_x = random(-current_intensity, current_intensity)
            offset_y = random(-current_intensity, current_intensity)
            self.current_offset = (offset_x, offset_y)
    
    def get_offset(self):
        return self.current_offset
Glow and Color Effects
Python
def get_modified_color(base_color, state):
    """Modify color based on player state"""
    r, g, b = base_color
    
    if state == 'dashing':
        # Red dash
        return (255, min(50, g//2), min(50, b//2))
    elif state == 'slamming':
        # Purple slam
        return (max(200, r), 0, 200)
    elif state == 'falling':
        # Dim falling
        return (r//2, g//2, b//2)
    else:
        # Normal
        return base_color

def get_glow_color(base_color):
    """Glow color (brighter version)"""
    r, g, b = base_color
    return (min(255, r + 100), min(255, g + 100), min(255, b + 100))
AI and Story System
Google Gemini Integration
Python
# Initialization
genai.configure(api_key=GENAI_API_KEY)

model = genai.GenerativeModel(
    'gemini-2.5-flash-preview-09-2025',
    system_instruction=FRAGMENTIA_SYSTEM_PROMPT
)

chat_session = model.start_chat(history=[])

# Sending Messages
response = chat_session.send_message(full_prompt)
raw_text = response.text
AI Response Format
Code
Expected Response Format:

Text Response:
"[NPC Dialog in English]"

Optional JSON Commands:
```json
{
    "gravity": 0.5,      // Gravity multiplier (0.1 - 2.0)
    "speed": 1.5,        // Camera speed multiplier
    "glitch": true       // Enable glitch visual mode
}
Example: "Gravity has started decreasing! Watch out!

JSON
{
    "gravity": 2.0,
    "glitch": true
}
"

Processing:

Extract text before JSON
Parse JSON with regex: r'json\s*(\{.*?\})\s*'
Apply modifications to world_modifiers
Display only text portion to player
Code

### Story Branching

Current Implementation: Linear (16 chapters) ├── Chapter 0: Awakening ├── Chapters 1-9: Main story ├── Chapter 10: Boss fight └── Chapters 11-14: Hidden/post-game

Potential Branching Points: ├── Early game: Mercy vs. Kill choice (Karma ±50) ├── Chapter 8: Redemption vs. Revenge (Karma ±100) └── Chapter 15: AI offers three endings based on final karma value

Final Endings: ├── Karma > 500: "Redemption" (Good) ├── Karma -500 < x < 500: "Equilibrium" (Neutral) └── Karma < -500: "Genocide" (Evil - Limbo Vasil)

Code

### NPC Conversation Flow

Player approaches NPC ├── Trigger npc_conversation_active = True └── Open chat interface

Player types message ├── Add to chat_history └── If AI enabled: send to generate_npc_response()

generate_npc_response(): ├── Build context (NPC name, personality, role, history) ├── Call model.generate_content(system_prompt) ├── Extract response text └── Return to player

NPC Response displayed ├── Add to chat_history ├── Update NPC state (mood, suspicion, etc.) └── Trigger visual feedback (color change, animation)

Player can: ├── Continue conversation ├── Press TAB to toggle AI mode └── Press ESC to exit

Code

---

## Boss Management System

### Boss Manager Architecture

```python
class BossManager:
    def __init__(self):
        self.spikes = pygame.sprite.Group()        # Platform spikes
        self.lightning = pygame.sprite.Group()     # Lightning columns
        self.giant_arrows = pygame.sprite.Group()  # Descending arrows
        self.orbitals = pygame.sprite.Group()      # Orbital strikes
        
        self.timers = {
            'spike': 0,
            'lightning': 0,
            'difficulty': 0
        }
    
    def update_logic(self, level_idx, platforms, player_x, player_karma, camera_speed, frame_mul, is_weakened=False):
        """Main boss attack pattern generator"""
        
        if level_idx not in [10, 15]:
            return  # Only active on boss levels
        
        # Difficulty scaling
        if self.timers['difficulty'] > 300:
            current_difficulty = 2
        if self.timers['difficulty'] > 900:
            current_difficulty = 3
        else:
            current_difficulty = 1
        
        # Weakening multipliers
        time_mult = 0.25 if is_weakened else 1.0
        spawn_mult = 0.25 if is_weakened else 1.0
        
        # Attack patterns (see detail below)
        self._spawn_spikes(platforms, player_karma, is_weakened)
        self._spawn_lightning(player_x, current_difficulty, spawn_mult, is_weakened)
        self._spawn_giant_arrows(player_x, current_difficulty, is_weakened)
        self._spawn_orbital_strikes(current_difficulty, is_weakened)
Boss Attack Patterns
1. Platform Spikes
Code
Spawn Rate: Every 10 frames (if timer threshold met)

Pattern:
├── Select 1-3 visible platforms randomly
├── Spawn BossSpike on each
└── Each spike has two phases:

Phase 1: WARNING (25 frames)
├─�� Visual: Flashing outline at platform edge
├── Animation: Up arrow indicators
├── Color: Cyan (Karma < 0) or Magenta (Karma > 0)

Phase 2: ACTIVE (30 frames)
├── Grow spike from platform surface
├── Animation: 4-frame growth sequence
├── Collision: Damage player if touched
└── Disappear after duration

Collision Damage:
├── Karma loss: ±5
├── Effect: Screen flash + particle burst
└── Knockback: 5 pixels upward

Code:
```python
if self.timers['spike'] > 10:
    self.timers['spike'] = 0
    visible_platforms = [p for p in platforms 
                        if 0 < p.rect.centerx < 1920]
    
    max_targets = 1 if is_weakened else 3
    target_count = min(len(visible_platforms), 
                      random.randint(1, max_targets))
    
    for p in random.sample(visible_platforms, target_count):
        if not any(s.platform == p for s in self.spikes):
            self.spikes.add(BossSpike(p, player_karma))
Code

#### 2. Lightning Columns

Spawn Rate: Every 40 frames

Pattern: ├── 1-2 strikes per spawn (difficulty dependent) ├── Targeting: 70% near player, 30% random

Phase 1: WARNING (30 frames) ├── Visual: Thin vertical line ├── Animation: Blinking outline ├── SFX: Warning beep └── Color: Based on karma

Phase 2: ACTIVE (10 frames) ├── Full-width lightning bolt ├── Jagged line animation ├── Bright core glow ├── Collision check every frame

Collision Radius: ±30 pixels horizontal

Code:

Python
self.timers['lightning'] += 1 * time_mult
if self.timers['lightning'] > 40:
    self.timers['lightning'] = 0
    count = int(current_difficulty * 2 * spawn_mult)
    
    for _ in range(max(1, count)):
        if random.random() < 0.7:
            # Near player
            tx = player_x + random.randint(-100, 300)
        else:
            # Random
            tx = random.randint(50, 1800)
        
        self.lightning.add(BossLightning(tx, player_karma))
Code

#### 3. Giant Arrows

Spawn Rate: Every 60 frames (Difficulty 2+)

Pattern: ├── 2-4 arrows per spawn (weakening reduces) ├── Spawn: Bottom of screen ├── Fall time: 5 seconds to ground

Phase 1: WARNING (45 frames) ├── Semi-transparent warning zone ├── Flashing border ├── Skull emoji (☠) └── Color flash animation

Phase 2: ACTIVE (20 frames) ├── Solid arrow descending ├── Light trail effect ├── Grows to fill screen width └── Collision check per frame

Collision: Full width from x-75 to x+75

Code:

Python
if current_difficulty >= 2 and int(self.timers['difficulty']) % 60 == 0:
    arrow_count = 1 if is_weakened else random.randint(2, 4)
    
    for _ in range(arrow_count):
        gx = max(50, min(1800, 
                player_x + random.randint(-200, 800)))
        self.giant_arrows.add(BossGiantArrow(gx, player_karma))
Code

#### 4. Orbital Strikes

Spawn Rate: Every 120 frames (Difficulty 3)

Pattern: ├── 2-3 orbitals per spawn ├── Spawn height: 50-150 pixels

Phase 1: CHARGING (60 frames) ├── Expanding circular charge-up ├── Center glow intensifies ├── Target zone marked at bottom ├── Audio: Charging hum

Phase 2: BLAST (20 frames) ├── Multiple beams rain down ├── Beams: 5-8 per strike ├── Distribution: ±300 pixels from center └── Collision: 40-pixel radius per beam

Code:

Python
if current_difficulty >= 3 and int(self.timers['difficulty']) % 120 == 0:
    orb_count = 1 if is_weakened else random.randint(2, 3)
    
    for _ in range(orb_count):
        orb_x = random.randint(100, 1800)
        orb_y = random.randint(50, 150)
        self.orbitals.add(
            BossOrbitalStrike(orb_x, orb_y, player_karma)
        )
Code

### Boss Collision Detection

```python
def check_collisions(self, player_rect, player_obj, all_vfx, save_manager):
    hit_occurred = False
    
    # 1. Spikes
    for spike in self.spikes:
        if spike.state == 'ACTIVE':
            if player_rect.colliderect(spike.rect):
                spike.kill()
                hit_occurred = True
    
    # 2. Lightning
    for bolt in self.lightning:
        if bolt.state == 'ACTIVE':
            if player_rect.colliderect(bolt.rect):
                bolt.kill()
                hit_occurred = True
    
    # 3. Giant Arrows
    for arrow in self.giant_arrows:
        if arrow.state == 'ACTIVE':
            if arrow.rect.colliderect(player_rect):
                hit_occurred = True
    
    # 4. Orbitals
    for orb in self.orbitals:
        if orb.check_collision(player_rect):
            orb.kill()
            hit_occurred = True
    
    # Apply Damage
    if hit_occurred:
        all_vfx.add(ScreenFlash((255, 255, 255), 150, 5))
        all_vfx.add(ParticleExplosion(
            player_obj['x'] + 15, 
            player_obj['y'] + 15, 
            (255, 0, 0), 
            15
        ))
        
        current_k = save_manager.get_karma()
        damage = 5
        
        if current_k > 0:
            save_manager.update_karma(-damage)
        elif current_k < 0:
            save_manager.update_karma(damage)
    
    return hit_occurred
Setup and Configuration
System Requirements
Code
Minimum:
├── Python 3.8+
├── pygame 2.0+
├── numpy (for audio generation)
├── google-generativeai (for AI features)
└── 2GB RAM, 500MB Disk

Recommended:
├── Python 3.10+
├── pygame 2.2+
├── Dedicated GPU (better performance)
└── 4GB+ RAM

Operating Systems:
├── Windows 10/11
├── Linux (Ubuntu 20.04+)
├── macOS 10.14+ (partially tested)
Installation Steps
bash
# 1. Clone repository
git clone https://github.com/FahrettinPasha/Fragmentia.git
cd Fragmentia

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate      # Linux/Mac
venv\Scripts\activate          # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure API Key
# Open settings.py
# Find: GENAI_API_KEY = ""
# Insert your Gemini API key:
GENAI_API_KEY = "YOUR_ACTUAL_KEY_HERE"

# 5. Run game
python main.py
requirements.txt
Code
pygame==2.2.1
numpy>=1.21.0
google-generativeai>=0.5.0
Configuration Files
settings.py - Primary Config
Python
# Display
LOGICAL_WIDTH = 1920
LOGICAL_HEIGHT = 1080
FPS = 60

# Physics (tune for difficulty)
GRAVITY = 1.0               # ↑ = harder to jump
JUMP_POWER = 28             # ↑ = higher jumps
PLAYER_SPEED = 10           # ↑ = faster horizontal movement
DASH_SPEED = 90             # ↑ = faster dashes
DASH_COOLDOWN = 60          # ↓ = more frequent dashing

# Camera
INITIAL_CAMERA_SPEED = 5    # ↑ = starts faster
MAX_CAMERA_SPEED = 18       # ↑ = harder final levels
SPEED_INCREMENT_RATE = 0.001 # ↑ = accelerates faster

# Level Goals (tune length)
EASY_MODE_LEVELS[1]['goal_score'] = 500  # ↑ = longer level

# Theme selection
CURRENT_THEME = THEMES[0]   # 0-4
Audio Configuration
Python
# In settings.py
VOLUME_SETTINGS = {
    "master_volume": 0.7,      # 0.0 - 1.0
    "music_volume": 0.5,       # Background music
    "effects_volume": 0.8      # Sounds, particles
}

# In main.py
FX_VOLUME = 0.7 * VOLUME_SETTINGS["effects_volume"]
Save System
Python
# Auto-saves after every level
save_manager.save_data()

# Loads on startup
save_manager.load_data()

# Reset to defaults
save_manager.reset_progress()

# Save location: ./save_data.json
Performance Optimization
Profiling Checklist
Python
# FPS Monitoring
print(f"FPS: {clock.get_fps():.1f}")  # Should be ~60

# Memory Usage
import tracemalloc
tracemalloc.start()
current, peak = tracemalloc.get_traced_memory()
print(f"Memory: {current / 1024 / 1024:.1f} MB")

# Frame Time Breakdown
update_time = 0
render_time = 0
t1 = time.time()
# ... update code ...
update_time = time.time() - t1

t2 = time.time()
# ... render code ...
render_time = time.time() - t2
print(f"Update: {update_time*1000:.2f}ms, Render: {render_time*1000:.2f}ms")
Optimization Techniques
1. Sprite Pooling
Python
# Pre-allocate reusable objects
trail_pool = [TrailEffect(0, 0) for _ in range(MAX_TRAIL_PARTICLES)]
active_trails = []

def spawn_trail(x, y, color, size):
    if trail_pool:
        trail = trail_pool.pop()
        trail.reset(x, y, color, size)
        active_trails.append(trail)
    else:
        # Create new if pool exhausted
        active_trails.append(TrailEffect(x, y, color, size))

def update_trails():
    for trail in active_trails[:]:
        trail.update(camera_speed)
        if trail.life <= 0:
            trail_pool.append(trail)
            active_trails.remove(trail)
2. Dirty Rectangle Optimization
Python
# Only update changed regions
dirty_rects = []

# When object moves:
old_rect = player.rect.copy()
player.update()
new_rect = player.rect.copy()

if old_rect != new_rect:
    dirty_rects.append(old_rect.inflate(10, 10))
    dirty_rects.append(new_rect.inflate(10, 10))

# Render only dirty regions
for rect in dirty_rects:
    if rect.colliderect(screen.get_rect()):
        # Draw to this rect only
        pass
3. Culling
Python
# Only process visible entities
RENDER_MARGIN = 200  # Extra pixels for smooth scrolling

def should_render(entity, camera_x):
    return (camera_x - RENDER_MARGIN < entity.x 
            < camera_x + LOGICAL_WIDTH + RENDER_MARGIN)

for enemy in all_enemies:
    if should_render(enemy, camera_x):
        enemy.update(camera_speed, dt)
        enemy.draw(surface)
4. Batch Rendering
Python
# Group similar objects and render together
def render_layer(surface, sprites, layer_type):
    for sprite in sprites:
        if sprite.layer == layer_type:
            surface.blit(sprite.image, sprite.rect)

# Call in order:
render_layer(surface, all_sprites, 'background')
render_layer(surface, all_sprites, 'platforms')
render_layer(surface, all_sprites, 'characters')
render_layer(surface, all_sprites, 'vfx')
5. AI Caching
Python
# Cache Gemini responses to reduce API calls
response_cache = {}

def get_npc_response(npc_name, user_text):
    cache_key = f"{npc_name}_{hash(user_text)}"
    
    if cache_key in response_cache:
        return response_cache[cache_key]
    
    response = generate_npc_response(npc_name, user_text)
    response_cache[cache_key] = response
    
    # Limit cache size
    if len(response_cache) > 100:
        response_cache.popitem()
    
    return response
Frame Budgets
Code
Target Frame Time: 16.67 ms (60 FPS)

Ideal Breakdown:
├── Input Processing: 0.5 ms
├── Physics Update: 4.0 ms
│   ├── Player movement: 1 ms
│   ├── Enemy AI: 2 ms
│   └── Collision detection: 1 ms
├── Animation: 1.0 ms
├── Particle Systems: 1.5 ms
├── Render: 9.0 ms
│   ├── Clear: 1 ms
│   ├── Draw world: 4 ms
│   ├── Draw UI: 2 ms
│   └── Flip: 2 ms
└── Audio: 0.67 ms

Red Flags:
├── Physics > 5 ms: Optimize collision
├── Render > 10 ms: Reduce draw calls
├── Audio > 1 ms: Check mixer settings
└── Total > 16.67 ms: Profile and find bottleneck
Debugging and Development
Debug Mode Enabling
Python
# In main.py, at top
DEBUG_MODE = True

if DEBUG_MODE:
    # Show hitboxes
    def draw_debug(surface):
        for platform in all_platforms:
            pygame.draw.rect(surface, (255, 0, 0), platform.rect, 1)
        pygame.draw.rect(surface, (0, 255, 0), player_rect, 2)
        for enemy in all_enemies:
            pygame.draw.rect(surface, (255, 255, 0), enemy.rect, 1)
    
    # Show stats overlay
    font = pygame.font.Font(None, 24)
    fps_text = font.render(f"FPS: {int(clock.get_fps())}", True, (255,255,255))
    score_text = font.render(f"Score: {int(score)}", True, (255,255,255))
    karma_text = font.render(f"Karma: {save_manager.get_karma()}", True, (255,255,255))
    
    # Draw all
    draw_debug(game_canvas)
    game_canvas.blit(fps_text, (10, 10))
    game_canvas.blit(score_text, (10, 40))
    game_canvas.blit(karma_text, (10, 70))
Common Issues & Solutions
Issue 1: API Key Not Working
Code
Error: "Unrecognized API key"

Solution:
1. Check settings.py has correct key (no spaces)
2. Verify key has Gemini API enabled
3. Check API quota limits
4. Fallback: Set AI_ENABLED = False
Issue 2: Low FPS (<60)
Code
Debug Steps:
1. Enable frame time profiling
2. Check which system is slow:
   ├── Physics? Reduce MAX_ENEMIES
   ├── Render? Reduce particle count (MAX_VFX_COUNT)
   ├── Audio? Check mixer load
3. Profile with cProfile:

import cProfile
cProfile.run('main()', 'stats')

import pstats
p = pstats.Stats('stats')
p.sort_stats('cumulative')
p.print_stats(10)
Issue 3: Audio Crackling
Code
Solution:
1. Reduce FX_VOLUME
2. Check mixer initialization:
   pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
3. Lower sample rate:
   pygame.mixer.init(frequency=22050)
4. Increase buffer size (less responsive but more stable)
Issue 4: Collision Issues
Code
Debug:
1. Draw collision boxes (DEBUG_MODE)
2. Print collision events:
   
   if should_collide(player_rect, platform.rect):
       print(f"Collision: player={player_rect}, platform={platform.rect}")

3. Check rect dimensions are correct
4. Verify camera offset is applied correctly:
   
   player_rect.x = player_x - camera_offset
Unit Testing Template
Python
import unittest

class TestPhysics(unittest.TestCase):
    def setUp(self):
        self.player = Player(100, 100)
        self.platform = Platform(50, 200, 300, 20)
    
    def test_gravity_application(self):
        initial_velocity = self.player.y_velocity
        self.player.apply_gravity(1.0)
        self.assertEqual(self.player.y_velocity, initial_velocity + GRAVITY)
    
    def test_jump_increases_velocity(self):
        self.player.jump()
        self.assertEqual(self.player.y_velocity, -JUMP_POWER)
    
    def test_platform_collision(self):
        self.player.y = 180
        self.player.y_velocity = 5
        collided = self.player.check_collision(self.platform)
        self.assertTrue(collided)

if __name__ == '__main__':
    unittest.main()
Git Workflow
bash
# Feature branch
git checkout -b feature/new-enemy-type
git add entities.py
git commit -m "feat: add drone enemy with homing bullets"

# Testing branch
git checkout -b test/boss-balance
git add boss_manager.py
git commit -m "test: adjust boss attack frequencies"

# Hotfix
git checkout -b hotfix/crash-on-level-10
git add main.py
git commit -m "fix: null pointer in boss initialization"

# Merge
git checkout main
git merge feature/new-enemy-type
Console Commands (Cheat Terminal)
Python
# In main.py game loop
if GAME_STATE == 'CHEAT_TERMINAL':
    # Available commands:
    commands = {
        "skip_level": lambda: init_game(current_level_idx + 1),
        "set_karma": lambda v: save_manager.update_karma(int(v)),
        "set_score": lambda v: score = float(v),
        "spawn_enemy": lambda: spawn_test_enemy(),
        "god_mode": lambda: toggle_invincibility(),
        "infinite_dash": lambda: dash_cooldown = 0,
        "slow_motion": lambda v: time_scale = float(v),
        "spawn_boss": lambda: spawn_boss(),
    }
Additional Resources
File Structure
Code
Fragmentia/
├── main.py                      # Game loop & state machine
├── settings.py                  # Constants & configuration
├── save_system.py               # Persistence layer
├── entities.py                  # Game objects
├── animations.py                # Character & VFX animation
├── story_system.py              # AI & narrative
├── cutscene.py                  # Cinematic rendering
├── boss_manager.py              # Boss attack patterns
├── boss_entities.py             # Boss objects
├── auxiliary_systems.py         # World systems (stubs)
├── game_config.py               # Level & theme data
├── drawing_utils.py             # Cinematic rendering utils
├── ui_system.py                 # UI elements
├── vfx.py                       # Visual effects
├── utils.py                     # Utility functions
├── assets/
│   ├── sfx/
│   │   ├── jump.wav
│   │   ├── dash.wav
│   │   ├── slam.wav
│   │   └── ...
│   ├── music/
│   │   ├── ara1.mp3
│   │   ├── ara2.mp3
│   │   ├── boss1.mp3
│   │   ├── boss2.mp3
│   │   └── ...
│   └── sprites/
│       └── (placeholder)
├── save_data.json               # Game progress
├── README.md                    # This file
└── requirements.txt             # Dependencies
API Reference
Player Methods
Python
player.jump()               # Initiate jump
player.dash(angle)         # Initiate dash
player.slam()              # Initiate slam attack
player.apply_gravity(dt)   # Apply gravity
player.check_collision()   # Collision detection
player.take_damage()       # Receive damage
Enemy Methods
Python
enemy.update(camera_speed, dt, player_pos)
enemy.draw(surface, camera_offset, theme)
enemy.take_damage(amount, vfx_group)
enemy.fire_projectile()
SaveManager Methods
Python
save_manager.save_data()
save_manager.load_data()
save_manager.update_karma(amount)
save_manager.get_karma()
save_manager.add_saved_soul()
save_manager.unlock_next_level(mode, level_idx)
save_manager.update_high_score(mode, level_idx, score)
StoryManager Methods
Python
story_manager.setup_ai()
story_manager.load_chapter(chapter_id)
story_manager.send_ai_message(user_text, game_context)
story_manager.generate_npc_response(npc, user_text, history)
story_manager.extract_commands(text)
story_manager.apply_world_modifiers(commands)
Troubleshooting Guide
Problem	Cause	Solution
Game won't start	Missing API key	Add GENAI_API_KEY to settings.py
Low FPS (<60)	Too many particles	Reduce MAX_VFX_COUNT
Crash on level 10	Uninitialized boss	Check boss_manager initialization
Weird collision	Camera offset not applied	Verify rect.x -= camera_speed
Audio cuts out	Mixer uninitialized	Call pygame.mixer.init()
AI unresponsive	Network timeout	Check internet & API quota
Save file corrupted	Invalid JSON	Delete save_data.json, restart
Version History
v1.0.0 (February 2025)

Initial release with 15 levels
AI integration with Gemini API
Karma system with branching endings
4 enemy types + Boss battles
Full VFX system
v0.9.0 (January 2025)

Beta testing phase
Boss fight mechanics
Story system implementation
v0.5.0 (December 2024)

Core game loop & physics
Platform generation
Basic enemies
License and Attribution
Project released under MIT License.

Library Attribution
Pygame: https://www.pygame.org
NumPy: https://numpy.org
Google Generative AI: https://ai.google.dev
Contact and Contribution
Bug Reporting
Report bugs on GitHub Issues page: https://github.com/FahrettinPasha/Fragmentia/issues

Contributing
Fork repository
Create feature branch (git checkout -b feature/amazing-feature)
Commit changes (git commit -m 'Add amazing feature')
Push to branch (git push origin feature/amazing-feature)
Open Pull Request
Contact
Discord: [Link]
Twitter: @FahrettinPasha
Email: contact@fragmentia-game.com
Acknowledgments
Thanks to all contributors who made the Fragmentia: Truth and Betrayal project possible.

Last Updated: February 12, 2026 Build: Python 3.8+, Pygame 2.2+, Gemini 2.5 Flash Status: Active Development

# main.py
from boss_entities import NexusBoss, AresBoss, VasilBoss, EnemyBullet, VasilCompanion, BossSpike, BossLightning
from boss_manager import BossManager
import pygame
import sys
import random
import math
import os
import json
import warnings
import numpy as np 
# Gereksiz uyarıları gizle
warnings.filterwarnings("ignore", category=UserWarning, module='pygame.pkgdata')

from settings import *

# --- BU FONKSİYONLARI MAIN.PY'NİN EN ÜSTÜNE EKLE ---

def rotate_point(point, angle, origin):
    """Bir noktayı orijin etrafında döndürür."""
    ox, oy = origin
    px, py = point
    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy

def draw_legendary_revolver(surface, x, y, angle, shoot_timer):
    """Detaylı, dönen ve geri tepme efekti olan Altıpatlar çizer."""
    # Geri Tepme
    recoil_angle = 0
    recoil_offset = 0
    if shoot_timer < 0.15:
        recoil_value = (0.15 - shoot_timer) / 0.15 
        recoil_angle = -0.5 * recoil_value 
        recoil_offset = -10 * recoil_value 

    final_angle = angle + recoil_angle
    pivot_x = x + math.cos(angle) * recoil_offset
    pivot_y = y + math.sin(angle) * recoil_offset

    # Renkler
    GUN_METAL = (40, 40, 50)
    NEON_CYAN = (0, 255, 255)
    GRIP_BROWN = (139, 69, 19)
    BARREL_GREY = (80, 80, 90)

    # Poligonlar
    grip_poly = [(pivot_x - 10, pivot_y - 5), (pivot_x + 10, pivot_y - 5), (pivot_x + 5, pivot_y + 20), (pivot_x - 15, pivot_y + 20)]
    body_poly = [(pivot_x + 5, pivot_y - 15), (pivot_x + 45, pivot_y - 15), (pivot_x + 45, pivot_y + 5), (pivot_x + 5, pivot_y + 5)]
    barrel_poly = [(pivot_x + 45, pivot_y - 12), (pivot_x + 90, pivot_y - 12), (pivot_x + 90, pivot_y + 2), (pivot_x + 45, pivot_y + 2)]
    
    # Silindir
    cyl_center_x = pivot_x + 25
    cyl_center_y = pivot_y - 5
    cylinder_poly = []
    for i in range(6):
        deg = i * 60
        rad = math.radians(deg)
        cylinder_poly.append((cyl_center_x + math.cos(rad) * 12, cyl_center_y + math.sin(rad) * 12))

    # Çizim Yardımcısı
    def draw_rotated_poly(surface, color, points, angle, pivot):
        rotated_points = [rotate_point(p, angle, pivot) for p in points]
        pygame.draw.polygon(surface, color, rotated_points)
        pygame.draw.polygon(surface, (0, 0, 0), rotated_points, 1)

    draw_rotated_poly(surface, GRIP_BROWN, grip_poly, final_angle, (pivot_x, pivot_y))
    draw_rotated_poly(surface, BARREL_GREY, barrel_poly, final_angle, (pivot_x, pivot_y))
    draw_rotated_poly(surface, GUN_METAL, body_poly, final_angle, (pivot_x, pivot_y))
    draw_rotated_poly(surface, (60, 60, 70), cylinder_poly, final_angle, (pivot_x, pivot_y))
    
    # Neon Çizgi
    start_neon = rotate_point((pivot_x + 10, pivot_y - 5), final_angle, (pivot_x, pivot_y))
    end_neon = rotate_point((pivot_x + 40, pivot_y - 5), final_angle, (pivot_x, pivot_y))
    pygame.draw.line(surface, NEON_CYAN, start_neon, end_neon, 2)

    return rotate_point((pivot_x + 90, pivot_y - 5), final_angle, (pivot_x, pivot_y))

# Gizli bölümleri ekle (11-15)
EASY_MODE_LEVELS.update({
    11: {'name': 'Karanlık Diriliş Yolu', 'goal_score': 60000, 'speed_mult': 1.6, 'theme_index': 0, 'type': 'normal', 'music_file': 'cyber_chase.mp3'},
    12: {'name': 'Vasi\'nin İzinde', 'goal_score': 75000, 'speed_mult': 1.7, 'theme_index': 1, 'type': 'normal', 'music_file': 'final_ascension.mp3'},
    13: {'name': 'Felsefi Geçit', 'goal_score': 90000, 'speed_mult': 1.8, 'theme_index': 2, 'type': 'normal', 'music_file': 'dark_ambient.mp3'},
    14: {'name': 'Gerçeklik Çatlağı', 'goal_score': 110000, 'speed_mult': 1.9, 'theme_index': 3, 'type': 'normal', 'music_file': 'synthwave.mp3'},
    15: {'name': 'SON KOŞU', 'goal_score': 150000, 'speed_mult': 2.5, 'theme_index': 1, 'type': 'normal', 'music_file': 'final_boss.mp3'}
})

# --- BÖLÜM 10 AYARI ---
EASY_MODE_LEVELS[10] = {
    'name': 'YARGI GÜNÜ (Bölüm 10)',
    'goal_score': 100000, 
    'speed_mult': 0.0,    # Kamera durur (Boss fight)
    'theme_index': 1,     # Kırmızı Kule teması
    'type': 'boss_fight',
    'music_file': 'final_boss.mp3'
}

# Boss sabitleri
BULLET_SPEED = 8
BOSS_HEALTH = 1000
BOSS_DAMAGE = 10
BOSS_FIRE_RATE = 60
BOSS_INVULNERABILITY_TIME = 30

# Limbo sabitleri (YENİ EKLENDİ)
LIMBO_VASIL_PROMPT = "Sen... buradasın. İraden kırıldı, ama sistem seni tamamen silmedi. Neden? Belki de hâlâ bir şansın var. Ya da belki bu, daha büyük bir planın parçası. Bu siyah boşluk, senin için bir ceza mı yoksa bir fırsat mı?"
LIMBO_ARES_PROMPT = "Ölümün bile seni kurtaramadı. Ama buradayız. Bu limbo, gerçekliğin çatlaklarından biri. Belki de burada, gerçek gücün ne olduğunu anlayacaksın. Hazır mısın?"

# Renkler (eğer settings.py'de yoksa)
CURSED_PURPLE = (128, 0, 128)
GLITCH_BLACK = (20, 20, 30)
CURSED_RED = (200, 0, 0)  # Eksik tanım eklendi

from utils import generate_sound_effect, generate_ambient_fallback, generate_calm_ambient, load_sound_asset, draw_text, draw_animated_player, wrap_text, draw_text_with_shadow
from vfx import LightningBolt, FlameSpark, GhostTrail, SpeedLine, Shockwave, EnergyOrb, ParticleExplosion, ScreenFlash, SavedSoul
# GÜNCELLEME: Yeni düşman sınıfları eklendi
from entities import Platform, Star, CursedEnemy, NPC, DroneEnemy, TankEnemy
from ui_system import render_ui
from animations import CharacterAnimator, TrailEffect
from save_system import SaveManager
from story_system import StoryManager

# --- EKSİK DOSYA YERİNE GEÇEN KODLAR BAŞLANGICI ---
class RestAreaManager:
    def __init__(self): self.active_area = None
    def update(self, pos): pass

class NexusHub: pass
class PhilosophicalCore: pass

class RealityShiftSystem:
    def __init__(self): self.current_reality = 0
    def get_current_effects(self): return {}
    def get_visual_effect(self): return {}

class TimeLayerSystem:
    def __init__(self): 
        self.current_era = 'present'
        self.eras = {'present': {}}

class CombatPhilosophySystem:
    def create_philosophical_combo(self, seq): return None

class LivingSoundtrack: pass
class EndlessFragmentia:
    def __init__(self): self.current_mode = 'default'

class ReactiveFragmentia:
    def update_world_based_on_player(self, ctx, hist): pass

class LivingNPC:
    def __init__(self, id, variant):
        self.x, self.y = 0, 0
    def daily_update(self, t, d): pass
    def draw(self, s, o): pass

class FragmentiaDistrict:
    def __init__(self, id, size): pass

class PhilosophicalTitan:
    def __init__(self, name, type, diff): pass
# --- EKSİK DOSYA YERİNE GEÇEN KODLAR BİTİŞİ ---

# --- YENİ: AI CUTSCENE IMPORT ---
from cutscene import AICutscene

# --- Asset Paths Tanımı ---
asset_paths = {
    'font': 'assets/fonts/VCR_OSD_MONO.ttf',
    'sfx_bip': 'assets/sounds/bip.wav',
    'sfx_glitch': 'assets/sounds/glitch.wav',
    'sfx_awake': 'assets/sounds/awake.wav',
    'npc_image': 'assets/images/npc_silhouette.png'
}

# --- YENİ: BOSS MANAGER SİSTEMİ ---
boss_manager_system = BossManager()

def trigger_guardian_interruption():
    """Karma sıfırlandığında Vasi'nin araya girip savaşı durdurması."""
    global GAME_STATE, story_manager, all_enemies
    
    # 1. Tüm saldırıları temizle (Ekranı rahatlat)
    boss_manager_system.clear_all_attacks()
    all_enemies.empty()  # Boss'ları da temizle
    
    # 2. Hikaye Moduna Geçiş
    GAME_STATE = 'CHAT'
    
    # 3. Vasi'nin Diyaloğunu Ayarla
    # "Yeterli. İraden kırıldı." gibi bir mesaj
    story_manager.set_dialogue("VASI", "SİSTEM UYARISI: İrade bütünlüğü kritik seviyenin altında... Müdahale ediliyor.", is_cutscene=True)
    
    # 4. Sonraki Adım
    # Diyalog bitince ne olacak? Şimdilik oyunu bitirebilir veya menüye atabiliriz.
    # story_manager'a bir sonraki state'i bildirmek gerekebilir ama şimdilik manuel yöneteceğiz.

# --- 1. SİSTEM VE EKRAN AYARLARI ---
pygame.init()
pygame.mixer.pre_init(44100, -16, 2, 512)

# Global Ekran (Pencere)
current_display_w, current_display_h = LOGICAL_WIDTH, LOGICAL_HEIGHT
screen = pygame.display.set_mode((current_display_w, current_display_h),
                                pygame.SCALED | pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE, vsync=1)
pygame.display.set_caption("FRAGMENTIA: Hakikat ve İhanet")
clock = pygame.time.Clock()

# Sanal Canvas (Oyun Mantığı için 1920x1080 Sabit)
game_canvas = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT))

# VFX için yardımcı yüzey
vfx_surface = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)

# --- 2. SES AYARLARI ---
FX_VOLUME = 0.7
AMBIENT_CHANNEL = pygame.mixer.Channel(0)
FX_CHANNEL = pygame.mixer.Channel(1)

# SES EFEKTLERİ
JUMP_SOUND = load_sound_asset("assets/sfx/jump.wav", lambda: generate_sound_effect(350, 90), FX_VOLUME * 0.9)
DASH_SOUND = load_sound_asset("assets/sfx/dash.wav", lambda: generate_sound_effect(700, 60), FX_VOLUME * 1.1)
SLAM_SOUND = load_sound_asset("assets/sfx/slam.wav", lambda: generate_sound_effect(100, 150, 0.7), FX_VOLUME * 1.5)
EXPLOSION_SOUND = load_sound_asset("assets/sfx/explosion.wav", lambda: generate_sound_effect(50, 300, 0.5), FX_VOLUME * 1.2)

current_level_music = None

MAX_VFX_COUNT = 200
MAX_DASH_VFX_PER_FRAME = 5
METEOR_CORE = (255, 255, 200)
METEOR_FIRE = (255, 80, 0)

class WarpLine(pygame.sprite.Sprite):
    def __init__(self, x, y, angle, color, theme_color=None):
        super().__init__()
        self.x, self.y = x, y
        self.vx, self.vy = math.cos(angle) * 15, math.sin(angle) * 15
        self.color = color
        self.theme_color = theme_color
        self.width = random.randint(2, 4)
        self.length_multiplier = random.uniform(10.0, 18.0)
        self.life = 8
        self.alpha = 255

    def update(self, *args):
        camera_speed = args[0] if args else 0
        self.x -= camera_speed
        self.x += self.vx * 0.8
        self.y += self.vy * 0.8
        self.life -= 1
        self.alpha = int(255 * (self.life / 8))
        if self.life <= 0:
            self.kill()

    def draw(self, surface):
        draw_color = self.theme_color if self.theme_color else self.color
        if self.alpha > 10:
            end_x = self.x - (self.vx * self.length_multiplier * 1.5)
            end_y = self.y - (self.vy * self.length_multiplier * 1.5)
            pygame.draw.line(surface, (*draw_color, self.alpha // 3),
                            (int(self.x), int(self.y)), (int(end_x), int(end_y)), self.width + 4)
            pygame.draw.line(surface, (*draw_color, self.alpha),
                            (int(self.x), int(self.y)), (int(end_x), int(end_y)), self.width)

# --- BOSS SINIFLARI ---
class NexusBoss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.health = BOSS_HEALTH
        self.max_health = BOSS_HEALTH
        self.fire_timer = 0
        self.invulnerable_timer = 0
        self.spawn_queue = []
        self.phase = 1

    def update(self, camera_speed, dt, player_pos):
        if not hasattr(self, 'ignore_camera_speed') or not self.ignore_camera_speed:
            self.x -= camera_speed
        self.fire_timer += 1
        if self.fire_timer >= BOSS_FIRE_RATE:
            self.fire_timer = 0
            self.shoot(player_pos)
        if self.health <= self.max_health * 0.5 and self.phase == 1:
            self.phase = 2
            self.enter_phase2()

    def shoot(self, player_pos):
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        dist = max(0.1, math.sqrt(dx*dx + dy*dy))
        dx /= dist
        dy /= dist
        bullet = EnemyBullet(self.x, self.y, dx * BULLET_SPEED, dy * BULLET_SPEED, BOSS_DAMAGE)
        self.spawn_queue.append(bullet)

    def enter_phase2(self):
        global BOSS_FIRE_RATE
        BOSS_FIRE_RATE = max(20, BOSS_FIRE_RATE - 20)

    def draw(self, surface, theme):
        # Can çubuğu
        bar_width = 200
        bar_height = 20
        bar_x = self.x - bar_width // 2
        bar_y = self.y - 60
        pygame.draw.rect(surface, (255,0,0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, (0,255,0), (bar_x, bar_y, bar_width * (self.health / self.max_health), bar_height))

        # Boss gövdesi
        color = (255, 0, 0) if self.invulnerable_timer > 0 else (255, 100, 100)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), 40)
        pygame.draw.circle(surface, (255, 200, 200), (int(self.x), int(self.y)), 40, 4)

        # Gözler
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x - 15), int(self.y - 10)), 10)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + 15), int(self.y - 10)), 10)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x - 15), int(self.y - 10)), 5)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + 15), int(self.y - 10)), 5)

    def take_damage(self, damage):
        if self.invulnerable_timer <= 0:
            self.health -= damage
            self.invulnerable_timer = BOSS_INVULNERABILITY_TIME
            # Hasar efekti
            all_vfx.add(Shockwave(self.x, self.y, (255,0,0), max_radius=60, width=3, speed=10))
            if self.health <= 0:
                self.kill()

class AresBoss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.health = BOSS_HEALTH
        self.max_health = BOSS_HEALTH
        self.fire_timer = 0
        self.invulnerable_timer = 0
        self.spawn_queue = []
        self.phase = 1

    def update(self, camera_speed, dt, player_pos):
        if not hasattr(self, 'ignore_camera_speed') or not self.ignore_camera_speed:
            self.x -= camera_speed
        self.fire_timer += 1
        if self.fire_timer >= BOSS_FIRE_RATE:
            self.fire_timer = 0
            self.shoot(player_pos)
        if self.health <= self.max_health * 0.5 and self.phase == 1:
            self.phase = 2
            self.enter_phase2()

    def shoot(self, player_pos):
        for angle in [-0.2, 0, 0.2]:
            dx = player_pos[0] - self.x
            dy = player_pos[1] - self.y
            dist = max(0.1, math.sqrt(dx*dx + dy*dy))
            dx /= dist
            dy /= dist
            new_dx = dx * math.cos(angle) - dy * math.sin(angle)
            new_dy = dx * math.sin(angle) + dy * math.cos(angle)
            bullet = EnemyBullet(self.x, self.y, new_dx * BULLET_SPEED, new_dy * BULLET_SPEED, BOSS_DAMAGE)
            self.spawn_queue.append(bullet)

    def enter_phase2(self):
        global BOSS_FIRE_RATE
        BOSS_FIRE_RATE = max(15, BOSS_FIRE_RATE - 25)

    def draw(self, surface, theme):
        # Can çubuğu
        bar_width = 200
        bar_height = 20
        bar_x = self.x - bar_width // 2
        bar_y = self.y - 60
        pygame.draw.rect(surface, (255,0,0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, (0,255,0), (bar_x, bar_y, bar_width * (self.health / self.max_health), bar_height))

        # Boss gövdesi (kare)
        color = (255, 0, 0) if self.invulnerable_timer > 0 else (200, 50, 50)
        pygame.draw.rect(surface, color, (int(self.x-50), int(self.y-50), 100, 100))
        pygame.draw.rect(surface, (255, 200, 200), (int(self.x-50), int(self.y-50), 100, 100), 4)

    def take_damage(self, damage):
        if self.invulnerable_timer <= 0:
            self.health -= damage
            self.invulnerable_timer = BOSS_INVULNERABILITY_TIME
            all_vfx.add(Shockwave(self.x, self.y, (255,0,0), max_radius=60, width=3, speed=10))
            if self.health <= 0:
                self.kill()

class VasilBoss(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.health = BOSS_HEALTH
        self.max_health = BOSS_HEALTH
        self.fire_timer = 0
        self.invulnerable_timer = 0
        self.spawn_queue = []
        self.phase = 1

    def update(self, camera_speed, dt, player_pos):
        if not hasattr(self, 'ignore_camera_speed') or not self.ignore_camera_speed:
            self.x -= camera_speed
        self.fire_timer += 1
        if self.fire_timer >= BOSS_FIRE_RATE:
            self.fire_timer = 0
            self.shoot(player_pos)
        if self.health <= self.max_health * 0.5 and self.phase == 1:
            self.phase = 2
            self.enter_phase2()

    def shoot(self, player_pos):
        angle = self.fire_timer * 0.1
        dx = math.cos(angle)
        dy = math.sin(angle)
        bullet = EnemyBullet(self.x, self.y, dx * BULLET_SPEED, dy * BULLET_SPEED, BOSS_DAMAGE)
        self.spawn_queue.append(bullet)

    def enter_phase2(self):
        global BOSS_FIRE_RATE
        BOSS_FIRE_RATE = max(10, BOSS_FIRE_RATE - 30)

    def draw(self, surface, theme):
        # Can çubuğu
        bar_width = 200
        bar_height = 20
        bar_x = self.x - bar_width // 2
        bar_y = self.y - 60
        pygame.draw.rect(surface, (255,0,0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, (0,255,0), (bar_x, bar_y, bar_width * (self.health / self.max_health), bar_height))

        # Boss gövdesi (üçgen)
        color = (255, 0, 0) if self.invulnerable_timer > 0 else (100, 50, 255)
        points = [(self.x, self.y-50), (self.x-50, self.y+50), (self.x+50, self.y+50)]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, (200, 200, 255), points, 4)

    def take_damage(self, damage):
        if self.invulnerable_timer <= 0:
            self.health -= damage
            self.invulnerable_timer = BOSS_INVULNERABILITY_TIME
            all_vfx.add(Shockwave(self.x, self.y, (255,0,0), max_radius=60, width=3, speed=10))
            if self.health <= 0:
                self.kill()

class EnemyBullet(pygame.sprite.Sprite):
    def __init__(self, x, y, vx, vy, damage):
        super().__init__()
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.damage = damage
        self.radius = 8

    def update(self, camera_speed, dt, player_pos=None):
        self.x += self.vx
        self.y += self.vy
        self.x -= camera_speed

        # Ekrandan çıkınca sil
        if self.x < -100 or self.x > LOGICAL_WIDTH + 100 or self.y < -100 or self.y > LOGICAL_HEIGHT + 100:
            self.kill()

    def draw(self, surface, theme):
        pygame.draw.circle(surface, (255, 0, 0), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (255, 255, 0), (int(self.x), int(self.y)), self.radius - 3)

# --- SİNEMATİK FONKSİYONU ---
def draw_cinematic_overlay(surface, manager, time_ms, mouse_pos):
    """Oyun dünyasının üzerine çizilen sinematik katman"""
    w, h = surface.get_width(), surface.get_height()
    active_buttons = {}
    
    # 1. Arka Planı Hafif Karart (Vignette etkisi)
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150)) # Şeffaflık değeri (0-255)
    surface.blit(overlay, (0, 0))
    
    # 2. Sinematik Barlar (Letterbox - Üst ve Alt Siyah Bantlar)
    bar_height = 130
    pygame.draw.rect(surface, (0, 0, 0), (0, 0, w, bar_height)) # Üst
    pygame.draw.rect(surface, (0, 0, 0), (0, h - bar_height, w, bar_height)) # Alt
    
    # 3. Konuşmacıya Göre Renk Teması
    line_color = (0, 255, 255) # Varsayılan Neon Mavi
    if manager.speaker == "SİSTEM" or manager.speaker == "MUHAFIZ" or "MAKİNE" in manager.speaker or "YARGIÇ" in manager.speaker:
        line_color = (255, 50, 50) # Kırmızı (Tehdit)
    elif manager.speaker == "VASI" or manager.speaker == "KURYE":
        line_color = (0, 255, 100) # Yeşil (Dost)
    elif "OYUNCU" in manager.speaker or "İÇ SES" in manager.speaker:
        line_color = (255, 200, 50) # Sarı (İçsel)

    # İnce neon çizgiler
    pygame.draw.line(surface, line_color, (0, bar_height), (w, bar_height), 2)
    pygame.draw.line(surface, line_color, (0, h - bar_height), (w, h - bar_height), 2)
    
    # 4. Üst Bar: Konuşmacı İsmi
    if manager.speaker:
        font_title = pygame.font.Font(None, 55)
        # İsmin yanında küçük bir ikon kutusu
        icon_rect = pygame.Rect(50, bar_height // 2 - 20, 40, 40)
        pygame.draw.rect(surface, line_color, icon_rect, 2)
        pygame.draw.rect(surface, (*line_color, 100), icon_rect.inflate(-4,-4)) # İç dolgu
        
        draw_text_with_shadow(surface, manager.speaker, font_title, (110, bar_height // 2), line_color, align="midleft")

    # 5. Alt Bar: Diyalog Metni
    font_text = pygame.font.Font(None, 36)
    text_area_rect = pygame.Rect(60, h - bar_height + 30, w - 120, bar_height - 60)
    
    if manager.is_cutscene:
        # Cutscene ise metin ekranın tam ortasında belirir (daha dramatik)
        center_overlay = pygame.Surface((w, 200), pygame.SRCALPHA)
        center_overlay.fill((0, 0, 0, 180))
        surface.blit(center_overlay, (0, h//2 - 100))
        
        lines = wrap_text(manager.display_text, font_text, w - 400)
        total_h = len(lines) * 45
        start_y = h//2 - total_h // 2
        
        for i, line in enumerate(lines):
            col = (255, 255, 255)
            if "HATA" in line or "UYARI" in line or "DİKKAT" in line: col = (255, 50, 50)
            draw_text_with_shadow(surface, line, font_text, (w//2, start_y + i * 45), col, align="center")
    else:
        # Normal diyalog ise alt barda akar
        lines = wrap_text(manager.display_text, font_text, text_area_rect.width)
        for i, line in enumerate(lines):
            draw_text_with_shadow(surface, line, font_text, (text_area_rect.x, text_area_rect.y + i * 35), (220, 220, 220), align="topleft")

    # 6. Devam Göstergesi
    if manager.waiting_for_click and manager.state != "WAITING_CHOICE":
        blink = (time_ms // 500) % 2 == 0
        if blink:
            draw_text_with_shadow(surface, "DEVAM ETMEK İÇİN TIKLA >", pygame.font.Font(None, 24), 
                                 (w - 50, h - 30), line_color, align="bottomright")

    # 7. Seçim Ekranı (Oyun dünyasının üzerinde)
    if manager.state == "WAITING_CHOICE":
        btn_height = 80
        btn_width = 800
        start_y = h // 2 - (len(manager.current_choices) * 110) // 2 + 30
        
        draw_text_with_shadow(surface, "BİR SEÇİM YAP", pygame.font.Font(None, 60), (w//2, start_y - 70), (255, 255, 0), align="center")
        
        for i, choice in enumerate(manager.current_choices):
            rect = pygame.Rect(w//2 - btn_width//2, start_y + i * 110, btn_width, btn_height)
            is_hover = rect.collidepoint(mouse_pos)
            
            # Yarı saydam buton arka planı
            s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            bg_col = (0, 40, 60, 230) if is_hover else (0, 20, 30, 200)
            s.fill(bg_col)
            surface.blit(s, rect.topleft)
            
            # Çerçeve
            border_col = (0, 255, 255) if is_hover else (0, 100, 150)
            pygame.draw.rect(surface, border_col, rect, 3, border_radius=0)
            
            text_col = (255, 255, 255) if is_hover else (200, 200, 200)
            draw_text_with_shadow(surface, f"> {choice['text']}", font_text, rect.center, text_col, align="center")
            
            active_buttons[f'choice_{i}'] = rect
            
    return active_buttons

# --- ARKA PLAN KAHRAMAN SİLÜETİ FONKSİYONU ---
def draw_background_hero(surface, x, y, size=150):
    """
    Arka planda devasa kahraman silüetini çizer.
    Cutscene.py'deki 'draw_warrior' fonksiyonundan uyarlandı.
    """
    GOLD = (255, 215, 0)
    HERO_BLUE = (0, 191, 255)
    
    # Yarı saydam bir yüzey oluştur (Ghost etkisi için)
    # Surface boyutunu çizim alanına göre ayarlıyoruz
    ghost_surf = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
    
    cx, cy = size * 1.5, size * 1.5  # Yüzeyin merkezi
    
    # 1. Kutsal Hare (Aura)
    t = pygame.time.get_ticks() / 1000.0
    for i in range(2):
        radius = size * (1.2 + i * 0.2) + math.sin(t * 2) * 10
        alpha = int(80 / (i + 1))  # Daha silik olsun
        pygame.draw.circle(ghost_surf, (*GOLD, alpha), (cx, cy), int(radius), 2)

    # 2. Miğfer / Gövde Formu
    points = [
        (cx, cy - size * 1.2),  # Tepe
        (cx - size * 0.8, cy - size * 0.2), # Sol Kulak
        (cx - size * 0.6, cy + size), # Sol Alt Çene
        (cx, cy + size * 1.4), # Çene Ucu
        (cx + size * 0.6, cy + size), # Sağ Alt Çene
        (cx + size * 0.8, cy - size * 0.2)  # Sağ Kulak
    ]
    
    # İçi hafif dolu, kenarları parlak
    pygame.draw.polygon(ghost_surf, (*GOLD, 30), points) 
    pygame.draw.polygon(ghost_surf, (*GOLD, 100), points, 5)
    
    # 3. Göz/Vizör (Parlak Mavi Umut Işığı)
    visor_rect = pygame.Rect(cx - size * 0.4, cy - 10, size * 0.8, 25)
    pygame.draw.rect(ghost_surf, (*HERO_BLUE, 150), visor_rect, border_radius=5)

    # Ekrana çiz (Oyuncunun arkasında kalması için pozisyonu ayarla)
    # x ve y koordinatlarını merkeze oturtmak için offset çıkarıyoruz
    surface.blit(ghost_surf, (x - cx, y - cy))

def draw_background_boss_silhouette(surface, karma, width, height):
    """
    Arka planda Boss silüetini çizer.
    - KÖTÜ SON (Karma < 0): SAVAŞÇI (Altın Miğfer)
    - İYİ SON (Karma >= 0): VASİ (Dijital Göz)
    """
    t = pygame.time.get_ticks() / 1000.0
    float_y = math.sin(t) * 15
    cx, cy = width // 2, height // 2 + float_y
    size = 200 
    ghost_surf = pygame.Surface((width, height), pygame.SRCALPHA)

    # ---------------------------------------------------------
    # DURUM 1: KÖTÜ SON (SAVAŞÇI - ALTIN MİĞFER)
    # ---------------------------------------------------------
    if karma < 0:
        GOLD = (255, 215, 0)
        HERO_BLUE = (0, 191, 255)
        WHITE = (255, 255, 255)
        
        # Hareler
        for i in range(2):
            radius = size * (1.3 + i * 0.25)
            pygame.draw.circle(ghost_surf, (*GOLD, 60), (cx, cy), int(radius), 3)

        # Miğfer
        points = [
            (cx, cy - size * 1.2), (cx - size * 0.8, cy - size * 0.2), 
            (cx - size * 0.6, cy + size), (cx, cy + size * 1.4), 
            (cx + size * 0.6, cy + size), (cx + size * 0.8, cy - size * 0.2)
        ]
        pygame.draw.polygon(ghost_surf, (*GOLD, 50), points) 
        pygame.draw.polygon(ghost_surf, (*GOLD, 255), points, 6)
        
        # Vizör
        visor_rect = pygame.Rect(cx - size*0.4, cy - 15, size*0.8, 30)
        pygame.draw.rect(ghost_surf, (*HERO_BLUE, 200), visor_rect, border_radius=8)
        
        # Cross Işığı
        pygame.draw.line(ghost_surf, (*WHITE, 200), (cx - size*1.5, cy), (cx + size*1.5, cy), 3)
        pygame.draw.line(ghost_surf, (*WHITE, 150), (cx, cy - size*1.5), (cx, cy + size*1.5), 10)

    # ---------------------------------------------------------
    # DURUM 2: İYİ SON (VASİ - DİJİTAL GÖZ) -> CUTSCENE'DEKİ TASARIM
    # ---------------------------------------------------------
    else: 
        CYBER_GREEN = (0, 255, 100)
        DARK_GREEN = (0, 50, 20)
        WHITE = (255, 255, 255)
        
        # 1. Karmaşık HUD Çerçeveleri (Dönen Kareler)
        rect_size = size * 2.2
        rect = pygame.Rect(0, 0, rect_size, rect_size)
        rect.center = (cx, cy)
        
        # Dönme efekti (Hafif sallanma)
        rot_offset = math.sin(t) * 10
        
        # Dış Çerçeve Köşeleri
        corner_len = 40
        # Sol Üst
        pygame.draw.line(ghost_surf, (*CYBER_GREEN, 200), (rect.left - rot_offset, rect.top), (rect.left + corner_len, rect.top), 4)
        pygame.draw.line(ghost_surf, (*CYBER_GREEN, 200), (rect.left - rot_offset, rect.top), (rect.left - rot_offset, rect.top + corner_len), 4)
        # Sağ Alt
        pygame.draw.line(ghost_surf, (*CYBER_GREEN, 200), (rect.right + rot_offset, rect.bottom), (rect.right - corner_len, rect.bottom), 4)
        pygame.draw.line(ghost_surf, (*CYBER_GREEN, 200), (rect.right + rot_offset, rect.bottom), (rect.right + rot_offset, rect.bottom - corner_len), 4)

        # 2. İris (Ana Göz)
        pygame.draw.circle(ghost_surf, (*DARK_GREEN, 100), (cx, cy), size) 
        pygame.draw.circle(ghost_surf, (*CYBER_GREEN, 255), (cx, cy), size, 3) # Dış halka
        
        # İç halkalar (Teknoloji hissi)
        pygame.draw.circle(ghost_surf, (*CYBER_GREEN, 100), (cx, cy), int(size * 0.7), 1)
        pygame.draw.circle(ghost_surf, (*CYBER_GREEN, 150), (cx, cy), int(size * 0.4), 2)
        
        # 3. Göz Bebeği (Elmas Şekli)
        pupil_size = 20
        # Göz bebeği oyuncuya baksın (Hafif hareket)
        pupil_x = cx + math.cos(t * 2) * 10
        pupil_y = cy + math.sin(t * 3) * 5
        
        pupil_points = [
            (pupil_x, pupil_y - 20),
            (pupil_x + 15, pupil_y),
            (pupil_x, pupil_y + 20),
            (pupil_x - 15, pupil_y)
        ]
        pygame.draw.polygon(ghost_surf, (*CYBER_GREEN, 255), pupil_points)
        pygame.draw.circle(ghost_surf, (*WHITE, 255), (pupil_x, pupil_y), 5) # Parlama

        # 4. Tarama Çizgisi (Scanline)
        scan_y = cy + math.sin(t * 4) * size
        pygame.draw.line(ghost_surf, (*CYBER_GREEN, 80), (cx - size, scan_y), (cx + size, scan_y), 2)

    # Ekrana çiz
    surface.blit(ghost_surf, (0, 0))

# --- 3. DURUM DEĞİŞKENLERİ ---
GAME_STATE = 'MENU' 
vasil_companion = None  # YENİ EKLENDİ: Vasi yoldaşı için global değişken

game_settings = {
    'fullscreen': True,
    'quality': 'HIGH',
    'res_index': 1,
    'fps_limit': 60,
    'fps_index': 1
}
current_fps = 60

save_manager = SaveManager()
story_manager = StoryManager()
philosophical_core = PhilosophicalCore()
reality_shifter = RealityShiftSystem()
time_layer = TimeLayerSystem()
combat_philosophy = CombatPhilosophySystem()
soundtrack = LivingSoundtrack()
endless_modes = EndlessFragmentia()
world_reactor = ReactiveFragmentia()

current_level_idx = 15

# YENİ: Level seçim sayfası değişkeni
level_select_page = 0

loading_progress = 0.0
loading_logs = []
loading_timer = 0
loading_stage = 0
target_state_after_load = 'PLAYING'
fake_log_messages = [
    "Yapay Zeka Çekirdeği Başlatılıyor...",
    "NEXUS Protokolü Aktif...",
    "VRAM Tahsisi Yapılıyor...",
    "Bölüm Varlıkları Yükleniyor...",
    "Felsefi Matris Yükleniyor...",
    "Gerçeklik Stabilizasyonu...",
    "Zaman Katmanları Senkronize Ediliyor...",
    "NPC Bellek Bankası Hazırlanıyor...",
    "Dünya Tepki Sistemi Aktif...",
    "Sistem Hazır."
]

CURRENT_THEME = THEMES[0]
CURRENT_SHAPE = 'circle'
score = 0.0
high_score = 0
camera_speed = INITIAL_CAMERA_SPEED
player_x, player_y = 150.0, float(LOGICAL_HEIGHT - 300)
y_velocity = 0.0
is_jumping = is_dashing = is_slamming = False
slam_stall_timer = 0
slam_cooldown = 0
jumps_left = MAX_JUMPS
dash_timer = 0
dash_cooldown_timer = 0
screen_shake = 0
dash_particles_timer = 0
dash_angle = 0.0
dash_frame_counter = 0.0
character_state = 'idle'
slam_collision_check_frames = 0
active_damage_waves = [] 

# STAT DEĞİŞKENLERİ
active_player_speed = PLAYER_SPEED
active_dash_cd = DASH_COOLDOWN
active_slam_cd = SLAM_COOLDOWN_BASE

# YENİ: Dirilme Hakkı Kontrolü
has_revived_this_run = False

# YENİ: Tılsım Kontrolü (Kurtuluş Modu için)
has_talisman = False

# YENİ: Level 15 için yeni değişkenler
level_15_timer = 0.0
finisher_active = False
finisher_state_timer = 0.0
finisher_type = None
level_15_cutscene_played = False

character_animator = CharacterAnimator()
trail_effects = []
last_trail_time = 0.0
TRAIL_INTERVAL = 3

all_platforms = pygame.sprite.Group()
all_enemies = pygame.sprite.Group()
all_vfx = pygame.sprite.Group()
stars = [Star(LOGICAL_WIDTH, LOGICAL_HEIGHT) for _ in range(120)]

# --- NPC SİSTEMİ DEĞİŞKENLERİ ---
npcs = []  # Dinlenme alanı NPC'leri
current_npc = None
npc_conversation_active = False
npc_chat_input = ""
npc_chat_history = []
npc_show_cursor = True
npc_cursor_timer = 0
npc_typing_timer = 0

# --- KARMA SİSTEMİ DEĞİŞKENLERİ ---
player_karma = 0
enemies_killed_current_level = 0
karma_notification_timer = 0
karma_notification_text = ""

# Dinlenme alanı yöneticisi
rest_area_manager = RestAreaManager()

# NPC ekosistemi (200 NPC)
npc_ecosystem = []
if game_settings['quality'] != 'LOW':
    for i in range(50): # Performans için düşürüldü
        npc = LivingNPC(i, random.randint(1, 5))
        npc_ecosystem.append(npc)

# Bölgeler (12 devasa bölge)
districts = []
for i in range(12):
    district = FragmentiaDistrict(i, random.choice(['small', 'medium', 'large']))
    districts.append(district)

# Boss arenası
boss_arenas = [
    PhilosophicalTitan('Plato Reborn', 'platonist', 8),
    PhilosophicalTitan('Nietzsche Incarnate', 'nietzschean', 9),
    PhilosophicalTitan('Camus Manifest', 'existentialist', 7),
    PhilosophicalTitan('Buddha Digital', 'buddhist', 10)
]

# --- YARDIMCI FONKSİYONLAR ---
def apply_display_settings():
    global screen, current_display_w, current_display_h
    target_res = AVAILABLE_RESOLUTIONS[game_settings['res_index']]
    
    if game_settings['fullscreen']:
        current_display_w, current_display_h = LOGICAL_WIDTH, LOGICAL_HEIGHT
        flags = pygame.SCALED | pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE
    else:
        current_display_w, current_display_h = target_res
        flags = pygame.DOUBLEBUF | pygame.HWSURFACE
    screen = pygame.display.set_mode((current_display_w, current_display_h), flags, vsync=1)

def add_new_platform(start_x=None):
    """Yeni platform ekler. Eğer platformda düşman varsa, hemen peşine GÜVENLİ bir platform ekler."""
    if start_x is None:
        if len(all_platforms) > 0:
            rightmost = max(all_platforms, key=lambda p: p.rect.right)
            gap = random.randint(GAP_MIN, GAP_MAX)
            start_x = rightmost.rect.right + gap
        else:
            start_x = LOGICAL_WIDTH
            
    width = random.randint(PLATFORM_MIN_WIDTH, PLATFORM_MAX_WIDTH)
    y = random.choice(PLATFORM_HEIGHTS)
    
    new_plat = Platform(start_x, y, width, 50)
    all_platforms.add(new_plat)
    if current_level_idx in [10, 15]:
        return 

    
    has_enemy = False
    
    # GÜNCELLEME: Yeni düşman tiplerini çağırma mantığı
    # Ayarları kontrol et, eğer "no_enemies" varsa düşman koyma
    lvl_props = EASY_MODE_LEVELS.get(current_level_idx, {})
    
    if not lvl_props.get("no_enemies") and width > 120 and random.random() < 0.4:
        # Bölüm zorluğuna göre düşman çeşitliliği
        enemy_roll = random.random()
        
        # Level 7 ve üzeri: Tank Düşman ihtimali
        if current_level_idx >= 7 and enemy_roll < 0.15:
            enemy = TankEnemy(new_plat)
        # Level 4 ve üzeri: Drone Düşman ihtimali
        elif current_level_idx >= 4 and enemy_roll < 0.35:
            # Drone havada olur, platformun biraz üstüne koy
            drone_y = y - random.randint(50, 150)
            enemy = DroneEnemy(new_plat.rect.centerx, drone_y)
        # Diğer durumlarda: Cursed Enemy (Standart)
        else:
            enemy = CursedEnemy(new_plat)
            
        all_enemies.add(enemy)
        has_enemy = True

    # --- YENİ ÖZELLİK: DÜŞMAN VARSA GÜVENLİ PLATFORM EKLE ---
    if has_enemy:
        # Hemen arkasına (biraz daha kısa bir boşlukla) güvenli platform ekle
        safe_gap = random.randint(150, 250) # Oyuncunun rahat atlayabileceği mesafe
        safe_start_x = new_plat.rect.right + safe_gap
        safe_width = random.randint(PLATFORM_MIN_WIDTH, PLATFORM_MAX_WIDTH)
        # Yükseklik değişimi çok olmasın ki kaçabilsin
        possible_heights = [h for h in PLATFORM_HEIGHTS if abs(h - y) <= VERTICAL_GAP]
        if not possible_heights: possible_heights = PLATFORM_HEIGHTS
        safe_y = random.choice(possible_heights)
        
        safe_plat = Platform(safe_start_x, safe_y, safe_width, 50)
        # İşaretle: Bu platformda asla düşman olamaz
        safe_plat.theme_index = CURRENT_THEME # Tema bozulmasın
        all_platforms.add(safe_plat)
        # Burada düşman ekleme kodu YOK, böylece güvenli alan garantilenir.

def start_loading_sequence(next_state_override=None):
    global GAME_STATE, loading_progress, loading_logs, loading_timer, loading_stage, target_state_after_load
    GAME_STATE = 'LOADING'
    loading_progress = 0.0
    loading_logs = []
    loading_timer = 0
    loading_stage = 0
    target_state_after_load = next_state_override if next_state_override else 'PLAYING'
    
    if game_settings['quality'] == 'LOW':
        global MAX_VFX_COUNT, MAX_DASH_VFX_PER_FRAME
        MAX_VFX_COUNT = 50
        MAX_DASH_VFX_PER_FRAME = 2

def start_story_chapter(chapter_id):
    global GAME_STATE, current_level_idx, player_x, player_y, camera_speed, CURRENT_THEME, y_velocity
    
    story_manager.load_chapter(chapter_id)
    GAME_STATE = 'CHAT'
    
    if chapter_id == 0:
        # Geri Dönüşüm Merkezi Sahnesi Kurulumu
        all_platforms.empty()
        all_enemies.empty()
        all_vfx.empty()
        
        # 1. Taban Platformu
        base_plat = Platform(0, LOGICAL_HEIGHT - 100, LOGICAL_WIDTH, 100, theme_index=2)
        all_platforms.add(base_plat)
        
        # 2. Arka Plan Sedyeleri (Dekoratif Platformlar)
        bed1 = Platform(400, LOGICAL_HEIGHT - 180, 200, 30, theme_index=2)
        bed2 = Platform(800, LOGICAL_HEIGHT - 180, 200, 30, theme_index=2)
        all_platforms.add(bed1)
        all_platforms.add(bed2)
        
        # 3. Oyuncu Pozisyonu
        player_x, player_y = 200.0, float(LOGICAL_HEIGHT - 250)
        y_velocity = 0
        camera_speed = 0 # Sinematikte kamera durur
        CURRENT_THEME = THEMES[2] # Çöplük teması

def init_rest_area():
    """Dinlenme alanını başlat"""
    global npcs, camera_speed, CURRENT_THEME, player_karma
    
    # Kamera durdur
    camera_speed = 0
    
    # Dinlenme alanı teması
    CURRENT_THEME = THEMES[4]
    
    # Platformları temizle
    all_platforms.empty()
    
    # Platform ve NPC ayarları
    platform_width = 400
    gap = 200
    
    # NPC oluşturma sayacı
    npc_spawn_index = 0
    
    # --- YENİ NPC MANTIĞI ---
    # Toplam 5 potansiyel NPC var, döngüyle kontrol edip yerleştiriyoruz
    for i in range(len(NPC_PERSONALITIES)):
        
        personality = NPC_PERSONALITIES[i]
        name = NPC_NAMES[i]
        color = NPC_COLORS[i]
        
        # 1. KURAL: Merchant (Tüccar) kaldırıldı
        if personality == "merchant":
            continue
            
        # 2. KURAL: Savaşçı (Ares) sadece Karma pozitifse (+) görünür
        # Eğer karma <= 0 ise Savaşçı orada olmayacak.
        if personality == "warrior" and player_karma <= 0:
            continue

        # 3. KURAL: Vasi tamamen kaldırıldı (Onun yerine Sokrat zaten listede var)
        
        # Platform oluştur
        x = npc_spawn_index * (platform_width + gap) + 200
        y = LOGICAL_HEIGHT - 100
        platform = Platform(x, y, platform_width, 50, theme_index=4)
        all_platforms.add(platform)
        
        # NPC Yerleştir
        npc_x = x + platform_width // 2
        npc_y = y - 80
        
        prompt = NPC_PROMPTS.get(personality, "...")
        
        npc = NPC(npc_x, npc_y, name, color, personality, prompt)
        
        # Sokrat için özel ayar (İstersen onu biraz daha farklı yapabilirsin)
        if personality == "philosopher":
            npc.talk_radius = 250 # Sokrat daha uzaktan konuşabilsin
            
        npcs.append(npc)
        npc_spawn_index += 1
    
    # Boş kalan alanlar için dekoratif orta platform
    center_x = (npc_spawn_index * (platform_width + gap)) + 200
    center_platform = Platform(center_x, LOGICAL_HEIGHT - 150, 600, 60, theme_index=4)
    all_platforms.add(center_platform)
    
    print(f"Dinlenme alanı başlatıldı. {len(npcs)} NPC oluşturuldu. (Karma: {player_karma})")

def init_limbo():
    """Oyuncu Level 10'da öldüğünde çağrılır. Araf modu."""
    global player_x, player_y, y_velocity, camera_speed, CURRENT_THEME
    global all_platforms, all_enemies, all_vfx, npcs, game_canvas
    global current_level_idx, boss_manager_system
    
    # 1. BOSS SAVAŞINI DURDUR
    boss_manager_system.reset()
    current_level_idx = 99      # Limbo ID
    
    # 2. Ortamı Temizle
    all_platforms.empty()
    all_enemies.empty()
    all_vfx.empty()
    npcs.clear()
    
    # 3. Ayarlar
    camera_speed = 0
    y_velocity = 0
    CURRENT_THEME = THEMES[2] # Karanlık Void Teması
    
    # 4. Platform
    center_plat = Platform(LOGICAL_WIDTH//2 - 400, LOGICAL_HEIGHT - 150, 800, 50, theme_index=4)
    all_platforms.add(center_plat)
    player_x = LOGICAL_WIDTH // 2 - 100
    player_y = LOGICAL_HEIGHT - 250
    
    # 5. NPC Seçimi (SENARYO DEĞİŞİKLİĞİ BURADA)
    karma = save_manager.get_karma()
    
    npc_name = ""
    npc_prompt = ""
    npc_color = (255, 255, 255)
    personality = "guide"
    
    # --- YENİ MANTIK ---
    if karma >= 0: # İYİ SONA GİDERKEN ÖLDÜN -> SAVAŞÇI GELİR
        npc_name = "SAVAŞÇI ARES"
        # Ares pasifist oyuncuya saygı duyar ama güçsüzlüğünü eleştirir ve Tılsımı verir.
        npc_prompt = """
        Sen ARES'sin. İyi niyetli ama gücü yetmeyen bu oyuncuyu (İsimsiz) izledin.
        Ona şöyle de: "Merhametin takdire şayan ama kılıcın kör. Bu Tılsımı al.
        Onunla düşmanlarına dokunduğunda onları yok etmeyeceksin, onları azad edeceksin.
        Kalk ve 'R' tuşuna basarak Kurtuluşunu tamamla."
        """
        npc_color = (255, 50, 50) # Kırmızı (Savaşçı Rengi)
        personality = "warrior"
        
    else: # KÖTÜ SONA GİDERKEN ÖLDÜN -> VASİ GELİR (Seni yargılar)
        npc_name = "VASİ"
        npc_prompt = """
        Sen VASİ'sin. Oyuncu her şeyi yok ederek buraya geldi ve başarısız oldu.
        Ona soğuk bir şekilde: "Yıkım getirdin ve yine de düştün. 
        Eğer gerçekten kaos istiyorsan 'G' tuşuna bas ve gerçek soykırımı gör."
        """
        npc_color = (0, 255, 100) # Yeşil (Sistem Rengi)
        personality = "philosopher"

    # NPC'yi Oluştur
    limbo_npc = NPC(
        x=LOGICAL_WIDTH // 2 + 100, 
        y=LOGICAL_HEIGHT - 230,
        name=npc_name,
        color=npc_color,
        personality_type=personality,
        prompt=npc_prompt
    )
    
    limbo_npc.ai_active = True 
    npcs.append(limbo_npc)
    
    print(f"LİMBO: {npc_name} oyuncuyu karşıladı. Karma: {karma}")
    
    try:
        AMBIENT_CHANNEL.stop()
    except:
        pass

# --- YENİ: KURTULUŞ MODU FONKSİYONU ---
def init_redemption_mode():
    """Savaşçı'nın verdiği Tılsım ile kurtuluş modu."""
    global player_x, player_y, y_velocity, camera_speed, CURRENT_THEME
    global all_platforms, all_enemies, all_vfx, npcs, current_level_idx
    global has_talisman, boss_manager_system
    
    # 1. Level ID'sini değiştir (11: Gizli Yol - Kurtuluş Modu)
    current_level_idx = 11
    
    # 2. Tılsımı Ver
    has_talisman = True
    
    # 3. Ortamı Hazırla
    all_platforms.empty()
    all_enemies.empty()
    all_vfx.empty()
    npcs.clear()
    boss_manager_system.reset() # Boss saldırısı olmasın
    
    # 4. Tema: Umutlu bir tema (Mesela Neon Pazarı veya Güvenli Bölge karışımı)
    CURRENT_THEME = THEMES[0] # Mavi/Mor Neon
    
    # 5. Başlangıç Platformu
    start_plat = Platform(0, LOGICAL_HEIGHT - 100, 600, 50)
    all_platforms.add(start_plat)
    
    player_x = 100
    player_y = LOGICAL_HEIGHT - 250
    camera_speed = INITIAL_CAMERA_SPEED * 1.5 # Hızlı aksiyon
    y_velocity = 0
    
    # Müzik: Coşkulu bir şey
    try:
        # Varsa cyber_chase, yoksa ambient
        sound = load_sound_asset("assets/music/cyber_chase.mp3", generate_ambient_fallback, 0.8)
        AMBIENT_CHANNEL.play(sound, loops=-1)
    except:
        pass
        
    print("KURTULUŞ MODU AKTİF! Tılsım alındı. Temas artık öldürmez, kurtarır.")

# --- YENİ: SOYKIRIM MODU FONKSİYONU ---
def init_genocide_mode():
    """Vasi ile anlaşma sonrası Kanlı Yol modu."""
    global player_x, player_y, y_velocity, camera_speed, CURRENT_THEME
    global all_platforms, all_enemies, all_vfx, npcs, current_level_idx
    global vasil_companion, boss_manager_system
    
    # 1. Level ID'sini değiştir (11: Gizli Yol - Soykırım Modu)
    current_level_idx = 11
    
    # 2. Ortamı Hazırla
    all_platforms.empty()
    all_enemies.empty()
    all_vfx.empty()
    npcs.clear()
    boss_manager_system.reset()
    
    # 3. Tema: Kırmızı/Siyah (Vasi'nin Kötücül Hali)
    CURRENT_THEME = THEMES[1] # Kule Teması (Kırmızı ağırlıklı)
    
    # 4. Başlangıç Platformu
    start_plat = Platform(0, LOGICAL_HEIGHT - 100, 600, 50)
    all_platforms.add(start_plat)
    
    player_x = 100
    player_y = LOGICAL_HEIGHT - 250
    camera_speed = INITIAL_CAMERA_SPEED * 1.6 # Çok hızlı
    y_velocity = 0
    
    # 5. Vasi Yoldaşını Başlat (Başlangıçta pasif veya yok olabilir, sonra gelecek)
    # Hikayeye göre: Önce kanıtla (-100 karma), sonra gelirim dedi.
    # O yüzden şimdilik companion YOK.
    vasil_companion = None 
    
    # Müzik: Agresif
    try:
        sound = load_sound_asset("assets/music/final_ascension.mp3", generate_ambient_fallback, 0.8)
        AMBIENT_CHANNEL.play(sound, loops=-1)
    except:
        pass
        
    print("SOYKIRIM MODU AKTİF! Gizli Yol: Bölüm 11. Hedef: -250 Karma")

def start_npc_conversation(npc):
    """NPC ile konuşmaya başla"""
    global current_npc, npc_conversation_active, npc_chat_history, GAME_STATE
    
    current_npc = npc
    npc_conversation_active = True
    npc_chat_input = ""
    npc_chat_history = []
    
    # NPC'nin ilk mesajı
    greeting = npc.start_conversation()
    npc_chat_history.append({"speaker": npc.name, "text": greeting})
    
    GAME_STATE = 'NPC_CHAT'
    print(f"NPC {npc.name} ile konuşma başlatıldı.")

def draw_npc_chat(surface):
    """NPC sohbet ekranını çiz"""
    if not current_npc:
        return
        
    # Koyu arka plan
    overlay = pygame.Surface((LOGICAL_WIDTH, LOGICAL_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))
    
    # Sohbet kutusu
    chat_width = 800
    chat_height = 600
    chat_x = (LOGICAL_WIDTH - chat_width) // 2
    chat_y = (LOGICAL_HEIGHT - chat_height) // 2
    
    # Ana kutu
    pygame.draw.rect(surface, (20, 20, 30), (chat_x, chat_y, chat_width, chat_height), border_radius=15)
    pygame.draw.rect(surface, current_npc.color, (chat_x, chat_y, chat_width, chat_height), 3, border_radius=15)
    
    # Başlık
    title_font = pygame.font.Font(None, 40)
    title = title_font.render(f"KONUŞUYOR: {current_npc.name}", True, current_npc.color)
    surface.blit(title, (chat_x + 20, chat_y + 20))
    
    # Kişilik etiketi
    type_font = pygame.font.Font(None, 24)
    status_text = "AI AKTİF" if current_npc.ai_active else "MANUEL MOD"
    status_color = (0, 255, 100) if current_npc.ai_active else (200, 200, 200)
    
    type_text = type_font.render(f"Kişilik: {current_npc.personality_type} | {status_text}", True, status_color)
    surface.blit(type_text, (chat_x + chat_width - 300, chat_y + 30))
    
    # Sohbet geçmişi alanı
    history_height = 400
    history_rect = pygame.Rect(chat_x + 20, chat_y + 80, chat_width - 40, history_height)
    pygame.draw.rect(surface, (10, 10, 15), history_rect, border_radius=10)
    
    # Sohbet mesajları
    font = pygame.font.Font(None, 28)
    y_offset = history_rect.y + 20
    
    for msg in npc_chat_history[-8:]:  # Son 8 mesajı göster
        if msg["speaker"] == "Oyuncu":
            text_color = (200, 255, 200)
            speaker = "Siz: "
        elif msg["speaker"] == "SİSTEM":
            text_color = (255, 100, 100)
            speaker = "SİSTEM: "
        else:
            text_color = current_npc.color
            speaker = f"{msg['speaker']}: "
        
        lines = wrap_text(msg["text"], font, history_rect.width - 40)
        for line in lines:
            text_surf = font.render(speaker + line, True, text_color)
            surface.blit(text_surf, (history_rect.x + 20, y_offset))
            y_offset += 35
        y_offset += 10
    
    # Giriş kutusu
    input_y = chat_y + history_height + 100
    input_rect = pygame.Rect(chat_x + 20, input_y, chat_width - 40, 50)
    pygame.draw.rect(surface, (30, 30, 40), input_rect, border_radius=8)
    pygame.draw.rect(surface, (100, 100, 150), input_rect, 2, border_radius=8)
    
    # Giriş metni
    input_font = pygame.font.Font(None, 32)
    display_text = npc_chat_input
    if npc_show_cursor:
        display_text += "|"
    
    input_text = input_font.render(display_text, True, (220, 220, 220))
    surface.blit(input_text, (input_rect.x + 15, input_rect.centery - 10))
    
    # Talimatlar
    instruct_font = pygame.font.Font(None, 24)
    instruct1 = instruct_font.render("ENTER: Gönder | ESC: Çık | TAB: AI Modu Aç/Kapa", True, (150, 150, 150))
    
    # AI Durumuna göre talimat
    if current_npc.ai_active:
        instruct2 = instruct_font.render("AI BAĞLANTISI KURULDU: Herhangi bir şey sorabilirsin!", True, (0, 255, 100))
    else:
        instruct2 = instruct_font.render("MANUEL MOD: Sadece ön tanımlı cevaplar.", True, (255, 200, 100))
    
    surface.blit(instruct1, (chat_x + 20, chat_y + chat_height - 40))
    surface.blit(instruct2, (chat_x + chat_width//2 - instruct2.get_width()//2, chat_y + chat_height - 70))
    
    # NPC avatarı (sağ üst)
    avatar_size = 80
    avatar_x = chat_x + chat_width - avatar_size - 30
    avatar_y = chat_y + 30
    
    # Avatar arka planı
    pygame.draw.circle(surface, (40, 40, 60), (avatar_x + avatar_size//2, avatar_y + avatar_size//2), avatar_size//2)
    pygame.draw.circle(surface, current_npc.color, (avatar_x + avatar_size//2, avatar_y + avatar_size//2), avatar_size//2, 3)
    
    # Avatar gözleri
    eye_y = avatar_y + avatar_size//2 - 10
    pygame.draw.circle(surface, (255, 255, 255), (avatar_x + avatar_size//2 - 15, eye_y), 8)
    pygame.draw.circle(surface, (255, 255, 255), (avatar_x + avatar_size//2 + 15, eye_y), 8)
    pygame.draw.circle(surface, (0, 100, 200), (avatar_x + avatar_size//2 - 15, eye_y), 4)
    pygame.draw.circle(surface, (0, 100, 200), (avatar_x + avatar_size//2 + 15, eye_y), 4)

def init_game():
    global player_x, player_y, y_velocity, score, camera_speed, jumps_left
    global is_jumping, is_dashing, is_slamming, dash_timer, dash_cooldown_timer, slam_stall_timer, slam_cooldown
    global CURRENT_THEME, CURRENT_SHAPE, screen_shake, dash_particles_timer, dash_angle, dash_frame_counter
    global character_state, trail_effects, last_trail_time, slam_collision_check_frames, active_damage_waves
    global CURRENT_THEME, current_level_music, npcs, current_npc, npc_conversation_active
    global player_karma, enemies_killed_current_level, karma_notification_text, karma_notification_timer
    global active_player_speed, active_dash_cd, active_slam_cd
    global has_revived_this_run, has_talisman
    global boss_manager_system, vasil_companion
    # --- YENİ: Level 15 için yeni değişkenler ---
    global level_15_timer, finisher_active, finisher_state_timer, finisher_type, level_15_cutscene_played

    # --- DÜZELTME: DEĞİŞKENLERİ SADECE GEREKİRSE SIFIRLA ---
    
    # Eğer normal bölümlerdeysek (1-10), her şeyi sıfırla.
    # Ama Gizli Yola (11+) girdiysek, Tılsım veya Vasi bizde kalmalı!
    if current_level_idx < 11:
        has_talisman = False
        vasil_companion = None
        has_revived_this_run = False
    
    # YENİ: Level 15 değişkenlerini sıfırla
    if current_level_idx == 15:
        level_15_timer = 0.0
        finisher_active = False
        finisher_state_timer = 0.0
        finisher_type = None
        level_15_cutscene_played = False

    lvl_config = EASY_MODE_LEVELS.get(current_level_idx, EASY_MODE_LEVELS[1])
    
    # Varsayılan değerler
    active_player_speed = PLAYER_SPEED
    active_dash_cd = DASH_COOLDOWN
    active_slam_cd = SLAM_COOLDOWN_BASE

    # YENİ: Boss yöneticisini sıfırla
    boss_manager_system.reset()

    # NPC'leri temizle
    npcs.clear()
    current_npc = None
    npc_conversation_active = False
    npc_chat_input = ""
    npc_chat_history = []
    
    # Bölüm tipine göre başlat
    if lvl_config.get('type') == 'rest_area':
        # Dinlenme alanı
        camera_speed = 0
        CURRENT_THEME = THEMES[4]
        init_rest_area()
        
        # Oyuncuyu platform üzerine yerleştir (NPC'lere yakın)
        player_x, player_y = 200.0, float(LOGICAL_HEIGHT - 180)
        y_velocity = 0
        
        # Dinlenme müziği
        music_file = random.choice(REST_AREA_MUSIC) if REST_AREA_MUSIC else "calm_ambient.mp3"
        try:
            current_level_music = load_sound_asset(f"assets/music/{music_file}", generate_calm_ambient, 0.6)
            AMBIENT_CHANNEL.play(current_level_music, loops=-1)
        except:
            current_level_music = generate_calm_ambient()
            AMBIENT_CHANNEL.play(current_level_music, loops=-1)
            
    elif lvl_config.get('type') == 'boss_fight':
        camera_speed = 0
        CURRENT_THEME = THEMES[lvl_config['theme_index']]
        all_platforms.empty()
        # Full zemin
        all_platforms.add(Platform(0, LOGICAL_HEIGHT - 50, LOGICAL_WIDTH, 50, theme_index=lvl_config['theme_index']))
        player_x, player_y = 200.0, float(LOGICAL_HEIGHT - 180)
        
        # --- KARMA BOSS SEÇİMİ (Hem Level 10 Hem Level 15 İçin Geçerli) ---
        karma = save_manager.get_karma()
        boss = None
        if karma <= -20:
            print(f"BOSS: ARES (LOW KARMA) - Level {current_level_idx}")
            boss = AresBoss(LOGICAL_WIDTH - 300, LOGICAL_HEIGHT - 200)
        elif karma >= 20:
            print(f"BOSS: VASIL (HIGH KARMA) - Level {current_level_idx}")
            boss = VasilBoss(LOGICAL_WIDTH // 2, 100)
        else:
            print(f"BOSS: NEXUS (NEUTRAL KARMA) - Level {current_level_idx}")
            boss = NexusBoss(LOGICAL_WIDTH - 300, LOGICAL_HEIGHT - 400)
        
        if boss: all_enemies.add(boss)
        
        # Müzik
        try:
            m = load_sound_asset(f"assets/music/{lvl_config.get('music_file')}", generate_ambient_fallback, 1.0)
            AMBIENT_CHANNEL.play(m, loops=-1)
        except: pass
            
    else:
        # Normal bölüm
        # BASE HIZ ARTIŞI: %25
        camera_speed = (INITIAL_CAMERA_SPEED * 1.25) * lvl_config['speed_mult']
        theme_idx = lvl_config['theme_index']
        CURRENT_THEME = THEMES[theme_idx]
        
        # Oyuncu pozisyonu
        player_x, player_y = 150.0, float(LOGICAL_HEIGHT - 300)
        
        # Normal müziği - eğer özel müzik tanımlıysa onu kullan
        music_file = lvl_config.get('music_file', 'dark_ambient.mp3')
        # (Level 1 kontrolü silindi, artık settings.py'dan ara1.mp3'ü alacak)
            
        try:
            current_level_music = load_sound_asset(f"assets/music/{music_file}", generate_ambient_fallback, 1.0)
            AMBIENT_CHANNEL.play(current_level_music, loops=-1)
        except:
            current_level_music = generate_ambient_fallback()
            AMBIENT_CHANNEL.play(current_level_music, loops=-1)
        
        # Normal platformlar
        all_platforms.empty()
        start_plat = Platform(0, LOGICAL_HEIGHT - 50, 400, 50)
        all_platforms.add(start_plat)
        current_right = 400
        while current_right < LOGICAL_WIDTH + 200:
            add_new_platform()
            current_right = max(p.rect.right for p in all_platforms)

        # 15. BÖLÜM İÇİN BOSS EKLE
        if current_level_idx == 15:
            karma = save_manager.get_karma()
            boss = None
            if karma <= -20:
                boss = AresBoss(LOGICAL_WIDTH - 300, LOGICAL_HEIGHT - 200)
            elif karma >= 20:
                boss = VasilBoss(LOGICAL_WIDTH // 2, 100)
            else:
                boss = NexusBoss(LOGICAL_WIDTH - 300, LOGICAL_HEIGHT - 400)
            if boss:
                boss.ignore_camera_speed = True  # Boss kamera ile hareket etmesin
                all_enemies.add(boss)
    
    # Boss HP Artır (Level 15 için)
    if current_level_idx == 15:
        for e in all_enemies:
            if hasattr(e, 'health'): 
                e.max_health = 50000
                e.health = 50000
    
    # Oyuncu değişkenleri
    y_velocity = score = dash_timer = dash_cooldown_timer = screen_shake = slam_stall_timer = slam_cooldown = 0
    is_jumping = is_dashing = is_slamming = False
    jumps_left = MAX_JUMPS
    dash_particles_timer = 0
    dash_angle = 0.0
    dash_frame_counter = 0.0
    character_state = 'idle'
    slam_collision_check_frames = 0
    active_damage_waves.clear()
    trail_effects.clear()
    last_trail_time = 0.0
    
    # Karma Sistemi Sıfırlama (Seviye Bazlı)
    player_karma = save_manager.get_karma() # Kayıttan yükle
    enemies_killed_current_level = 0
    karma_notification_timer = 0
    
    CURRENT_SHAPE = random.choice(PLAYER_SHAPES)
    all_enemies.empty()
    all_vfx.empty()
    
    character_animator.__init__()
    
    print(f"Bölüm {current_level_idx} başlatıldı: {lvl_config['name']}")

# --- YENİ: ANA PROGRAM BAŞLANGICI ---
def main():
    # 1. ANA OYUN DÖNGÜSÜ
    global GAME_STATE
    # Oyunu doğrudan MENÜ modunda başlat (Cutscene'i atla)
    GAME_STATE = 'MENU'
    
    # Mevcut oyun döngüsünü çalıştır
    run_game_loop()

def run_game_loop():
    # Değiştirilecek tüm global değişkenleri burada bildirin.
    global GAME_STATE, loading_timer, loading_logs, loading_stage, target_state_after_load
    global score, camera_speed, player_x, player_y, y_velocity, is_jumping, is_dashing, is_slamming
    global slam_stall_timer, slam_cooldown, jumps_left, dash_timer, dash_cooldown_timer
    global screen_shake, character_state, current_level_idx, high_score
    global dash_vx, dash_vy, dash_particles_timer, dash_angle, dash_frame_counter
    global slam_collision_check_frames, active_damage_waves, trail_effects, last_trail_time
    global CURRENT_THEME, CURRENT_SHAPE, loading_progress, frame_count
    global current_npc, npc_conversation_active, npc_chat_input, npc_chat_history
    global npc_show_cursor, npc_cursor_timer, npc_typing_timer, npcs
    global active_ui_elements
    global player_karma, enemies_killed_current_level, karma_notification_timer, karma_notification_text
    global active_player_speed, active_dash_cd, active_slam_cd
    global has_revived_this_run, has_talisman
    global level_select_page, vasil_companion
    global boss_manager_system
    # --- YENİ: Level 15 değişkenleri ---
    global level_15_timer, finisher_active, finisher_state_timer, finisher_type, level_15_cutscene_played
    
    # YENİ: Hile Modu Değişkenleri
    is_super_mode = False
    terminal_input = ""
    terminal_status = "KOMUT BEKLENİYOR..."
    
    # active_ui_elements'i boş bir sözlük olarak başlatın.
    active_ui_elements = {}

    running = True
    last_time = pygame.time.get_ticks()
    frame_count = 0
    
    current_level_idx = 15
    
    # Oyun değişkenlerini sıfırla
    CURRENT_THEME = THEMES[0]
    CURRENT_SHAPE = 'circle'
    score = 0.0
    high_score = 0
    camera_speed = INITIAL_CAMERA_SPEED
    player_x, player_y = 150.0, float(LOGICAL_HEIGHT - 300)
    y_velocity = 0.0
    is_jumping = is_dashing = is_slamming = False
    jumps_left = MAX_JUMPS
    dash_timer = dash_cooldown_timer = 0
    screen_shake = 0
    dash_particles_timer = 0
    dash_angle = 0.0
    dash_frame_counter = 0.0
    character_state = 'idle'
    slam_collision_check_frames = 0
    active_damage_waves.clear()
    trail_effects.clear()
    last_trail_time = 0.0
    
    # YENİ: Level 15 değişkenlerini sıfırla
    level_15_timer = 0.0
    finisher_active = False
    finisher_state_timer = 0.0
    finisher_type = None
    level_15_cutscene_played = False
    
    # YENİ: Boss sistemini sıfırla
    boss_manager_system.reset()
    vasil_companion = None  # Vasi yoldaşı sıfırla
    
    # Mevcut oyun döngüsünü çalıştır
    while running:
        current_time = pygame.time.get_ticks()
        dt = (current_time - last_time) / 1000.0
        last_time = current_time
        time_ms = current_time
        frame_count += 1
        frame_mul = max(0.001, dt) * 60.0

        raw_mouse_pos = pygame.mouse.get_pos()
        scale_x = LOGICAL_WIDTH / screen.get_width()
        scale_y = LOGICAL_HEIGHT / screen.get_height()
        mouse_pos = (raw_mouse_pos[0] * scale_x, raw_mouse_pos[1] * scale_y)

        if frame_count % 30 == 0:
            if len(all_vfx) > MAX_VFX_COUNT:
                 sprites = list(all_vfx.sprites())
                 for sprite in sprites[:20]:
                     sprite.kill()

        # Olay kontrol döngüsü
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # BU SATIR ARTIK HATA VERMEYECEK
                if GAME_STATE == 'MENU':
                    if 'story_mode' in active_ui_elements and active_ui_elements['story_mode'].collidepoint(mouse_pos):
                        # YENİ MANTIK: MENÜ -> CUTSCENE -> OYUN
                        print("Hikaye modu seçildi, ara sahne oynatılıyor...")
                        
                        # Müzik varsa durdur (sinematik kendi seslerini kullanıyor olabilir)
                        if AMBIENT_CHANNEL.get_busy():
                            AMBIENT_CHANNEL.stop()

                        # Ara sahneyi oynat (Blocking loop - Oyun döngüsünü geçici olarak bekletir)
                        # Bu, basit bir state machine için kabul edilebilir bir çözümdür.
                        ai_awakening_scene = AICutscene(screen, clock, asset_paths)
                        cutscene_finished = ai_awakening_scene.run()
                        
                        if cutscene_finished:
                            # Ara sahne bitti, oyunu yükle
                            current_level_idx = 1
                            start_loading_sequence('PLAYING')
                        else:
                            # Ara sahnede çıkış yapıldıysa
                            running = False
                            
                    elif 'level_select' in active_ui_elements and active_ui_elements['level_select'].collidepoint(mouse_pos):
                        GAME_STATE = 'LEVEL_SELECT'
                        level_select_page = 0 # Sayfayı sıfırla

                    elif 'settings' in active_ui_elements and active_ui_elements['settings'].collidepoint(mouse_pos):
                        GAME_STATE = 'SETTINGS'
                    elif 'cheat_terminal' in active_ui_elements and active_ui_elements['cheat_terminal'].collidepoint(mouse_pos):
                        GAME_STATE = 'TERMINAL'
                        terminal_input = ""
                        terminal_status = "KOMUT BEKLENİYOR..."
                    elif 'endless' in active_ui_elements and active_ui_elements['endless'].collidepoint(mouse_pos):
                        GAME_STATE = 'ENDLESS_SELECT'
                    elif 'exit' in active_ui_elements and active_ui_elements['exit'].collidepoint(mouse_pos):
                        running = False
                
                elif GAME_STATE == 'LEVEL_SELECT':
                    if 'back' in active_ui_elements and active_ui_elements['back'].collidepoint(mouse_pos):
                        GAME_STATE = 'MENU'
                    
                    # GÜNCELLEME: Sayfalama Kontrolleri
                    elif 'next_page' in active_ui_elements and active_ui_elements['next_page'].collidepoint(mouse_pos):
                        level_select_page += 1
                    elif 'prev_page' in active_ui_elements and active_ui_elements['prev_page'].collidepoint(mouse_pos):
                        level_select_page = max(0, level_select_page - 1)
                        
                    else:
                        for key, rect in active_ui_elements.items():
                            if key.startswith('level_') and rect.collidepoint(mouse_pos):
                                level_num = int(key.split('_')[1])
                                current_level_idx = level_num
                                current_level_idx = level_num
                                start_loading_sequence('PLAYING')
                                break

                elif GAME_STATE == 'ENDLESS_SELECT':
                    if 'back' in active_ui_elements and active_ui_elements['back'].collidepoint(mouse_pos):
                        GAME_STATE = 'MENU'
                    else:
                        for key, rect in active_ui_elements.items():
                            if key.startswith('mode_') and rect.collidepoint(mouse_pos):
                                mode_name = key.split('_')[1]
                                endless_modes.current_mode = mode_name
                                start_loading_sequence('ENDLESS_PLAY')
                                break

                elif GAME_STATE == 'SETTINGS':
                    if 'toggle_fullscreen' in active_ui_elements and active_ui_elements['toggle_fullscreen'].collidepoint(mouse_pos):
                        game_settings['fullscreen'] = not game_settings['fullscreen']
                    elif 'toggle_quality' in active_ui_elements and active_ui_elements['toggle_quality'].collidepoint(mouse_pos):
                        game_settings['quality'] = 'LOW' if game_settings['quality'] == 'HIGH' else 'HIGH'
                    elif 'change_resolution' in active_ui_elements and active_ui_elements['change_resolution'].collidepoint(mouse_pos):
                        game_settings['res_index'] = (game_settings['res_index'] + 1) % len(AVAILABLE_RESOLUTIONS)
                    elif 'apply_changes' in active_ui_elements and active_ui_elements['apply_changes'].collidepoint(mouse_pos):
                        apply_display_settings()
                    elif 'back' in active_ui_elements and active_ui_elements['back'].collidepoint(mouse_pos):
                        GAME_STATE = 'MENU'
                    elif 'reset_progress' in active_ui_elements and active_ui_elements['reset_progress'].collidepoint(mouse_pos):
                        save_manager.reset_progress()

                elif GAME_STATE == 'LEVEL_COMPLETE':
                    if 'continue' in active_ui_elements and active_ui_elements['continue'].collidepoint(mouse_pos):
                        next_level = current_level_idx + 1
                        
                        # --- YENİ SİSTEM: FİNAL ÖNCESİ SİNEMATİK ---
                        if next_level == 10:
                            # 1. Karmayı kontrol et
                            karma = save_manager.get_karma()
                            scenario = "BETRAYAL" if karma >= 0 else "JUDGMENT"
                            
                            print(f"Sinematik Başlatılıyor: {scenario}")
                            
                            # 2. Sinematik sınıfına senaryoyu gönder
                            # asset_paths sözlüğüne 'scenario' anahtarını ekleyerek gönderiyoruz
                            cinematic_assets = asset_paths.copy()
                            cinematic_assets['scenario'] = scenario
                            
                            # 3. Müziği durdur ve sahneyi oynat
                            if AMBIENT_CHANNEL.get_busy(): AMBIENT_CHANNEL.stop()
                            
                            scene = AICutscene(screen, clock, cinematic_assets)
                            scene.run() # Bu işlem bitene kadar kod burada bekler
                            
                            # 4. Sahne bitti, 10. Bölümü başlat
                            current_level_idx = 10
                            start_loading_sequence('PLAYING')
                            continue  # Döngüye devam et, return yerine continue kullanıyoruz
                        # ---------------------------------------------

                        # GİZLİ BÖLÜMLERDE (11-14) NORMAL DEVAM ET
                        if 11 <= current_level_idx <= 14:
                            current_level_idx = next_level
                            init_game()
                            GAME_STATE = 'PLAYING'
                            continue
                        
                        # SON BÖLÜM (15) BİTTİYSE OYUN BİTER
                        elif current_level_idx == 15:
                            GAME_STATE = 'GAME_COMPLETE'
                        elif next_level in EASY_MODE_LEVELS:
                            current_level_idx = next_level
                            init_game()
                            GAME_STATE = 'PLAYING'
                        else:
                            GAME_STATE = 'GAME_COMPLETE'
                    elif 'return_menu' in active_ui_elements and active_ui_elements['return_menu'].collidepoint(mouse_pos):
                        GAME_STATE = 'MENU'
                
                elif GAME_STATE in ['CHAT', 'CUTSCENE']:
                    # SEÇİM YAPMA EKRANI
                    if story_manager.state == "WAITING_CHOICE":
                        for key, rect in active_ui_elements.items():
                            if key.startswith('choice_') and rect.collidepoint(mouse_pos):
                                choice_idx = int(key.split('_')[1])
                                story_manager.select_choice(choice_idx)
                                break
                    
                    # NORMAL İLERLEME
                    elif story_manager.waiting_for_click:
                        story_manager.next_line()
                        if story_manager.state == "FINISHED":
                            # Diyalog bitti, oyuna dön
                            if story_manager.current_chapter == 0: 
                                # Giriş bölümü bitti, Bölüm 1'i başlat
                                current_level_idx = 1
                                start_loading_sequence('PLAYING')
                            else:
                                start_loading_sequence('PLAYING')

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if GAME_STATE == 'PLAYING':
                        GAME_STATE = 'MENU' 
                        AMBIENT_CHANNEL.stop()
                    elif GAME_STATE == 'NPC_CHAT':
                        # Sohbetten çık
                        GAME_STATE = 'PLAYING'
                        if current_npc:
                            current_npc.end_conversation()
                            current_npc = None
                    elif GAME_STATE == 'TERMINAL':
                        GAME_STATE = 'MENU'
                    elif GAME_STATE in ['MENU', 'SETTINGS', 'LEVEL_SELECT', 'ENDLESS_SELECT']:
                        running = False

                if event.key == pygame.K_p:
                    if GAME_STATE == 'PLAYING':
                        GAME_STATE = 'PAUSED'
                        AMBIENT_CHANNEL.pause()
                    elif GAME_STATE == 'PAUSED':
                        GAME_STATE = 'PLAYING'
                        AMBIENT_CHANNEL.unpause()

                if GAME_STATE == 'GAME_OVER' and event.key == pygame.K_r:
                    init_game()
                    GAME_STATE = 'PLAYING'
                    
                # --- YENİ: Limbo'da R tuşuna basınca Kurtuluş Modu başlat ---
                if current_level_idx == 99 and event.key == pygame.K_r:
                    init_redemption_mode()
                    
                # --- YENİ: Limbo'da G tuşuna basınca Soykırım Modu başlat ---
                if current_level_idx == 99 and event.key == pygame.K_g:
                    # Test için karmayı düşür
                    save_manager.update_karma(-80) # Hemen gelmesin, biraz oynayalım
                    init_genocide_mode()
                    
                if GAME_STATE == 'PLAYING' and event.key == pygame.K_e:
                    # NPC ile konuşma
                    closest_npc = None
                    min_dist = float('inf')
                    
                    for npc in npcs:
                        dist = math.sqrt((player_x - npc.x)**2 + (player_y - npc.y)**2)
                        if dist < npc.talk_radius and dist < min_dist:
                            min_dist = dist
                            closest_npc = npc
                    
                    if closest_npc:
                        start_npc_conversation(closest_npc)
                
                # --- TERMİNAL İŞLEMLERİ ---
                elif GAME_STATE == 'TERMINAL':
                    if event.key == pygame.K_RETURN:
                        # Şifre Kontrolü
                        if terminal_input.upper() == "SUPER_MODE_ON":
                            is_super_mode = not is_super_mode # Toggle
                            status = "AKTİF" if is_super_mode else "PASİF"
                            terminal_status = f"SÜPER MOD: {status}!"
                            terminal_input = ""
                        else:
                            terminal_status = "HATA: GEÇERSİZ KOD"
                            terminal_input = ""
                    elif event.key == pygame.K_BACKSPACE:
                        terminal_input = terminal_input[:-1]
                    else:
                        if len(terminal_input) < 20:
                            terminal_input += event.unicode.upper()

                elif GAME_STATE == 'NPC_CHAT':
                    if event.key == pygame.K_RETURN:
                        # Mesaj gönder
                        if npc_chat_input.strip():
                            # Oyuncu mesajını geçmişe ekle
                            npc_chat_history.append({"speaker": "Oyuncu", "text": npc_chat_input})
                            
                            # NPC'den yanıt al
                            npc_response = "..."
                            
                            if current_npc:
                                if current_npc.ai_active:
                                    # --- YENİ: AI SİSTEMİNİ KULLAN ---
                                    # Geçmiş konuşmayı AI'ya bağlam olarak veriyoruz
                                    npc_response = story_manager.generate_npc_response(current_npc, npc_chat_input, npc_chat_history[:-1])
                                else:
                                    # --- ESKİ: MANUEL YANIT ---
                                    game_context = f"Skor: {int(score)}, Bölüm: {current_level_idx}"
                                    npc_response = current_npc.send_message(npc_chat_input, game_context)
                                
                                npc_chat_history.append({"speaker": current_npc.name, "text": npc_response})
                            
                            # Girişi temizle
                            npc_chat_input = ""
                    
                    elif event.key == pygame.K_BACKSPACE:
                        # Karakter sil
                        npc_chat_input = npc_chat_input[:-1]
                    
                    elif event.key == pygame.K_TAB:
                        # AI modunu aç/kapa
                        if current_npc:
                            current_npc.ai_active = not current_npc.ai_active
                            # Durum değişikliğini sohbet geçmişine ekle
                            status = "AKTİF" if current_npc.ai_active else "PASİF"
                            color = (0, 255, 100) if current_npc.ai_active else (255, 200, 100)
                            # Kullanıcıya bilgi ver
                            # Not: Bu sadece görsel bir log
                            # UI çiziminde üst köşede de gösteriyoruz
                    
                    elif event.key == pygame.K_ESCAPE:
                        # Sohbetten çık
                        GAME_STATE = 'PLAYING'
                        if current_npc:
                            current_npc.end_conversation()
                            current_npc = None
                    
                    else:
                        # Karakter ekle
                        if len(npc_chat_input) < 100:  # Maksimum uzunluk
                            npc_chat_input += event.unicode
                
                # DİNLENME BÖLGESİNDEN ÇIKIŞ İÇİN T TUŞU
                if GAME_STATE == 'PLAYING' and event.key == pygame.K_t:
                    lvl_config = EASY_MODE_LEVELS.get(current_level_idx, EASY_MODE_LEVELS[1])
                    if lvl_config.get('type') == 'rest_area':
                        # Bir sonraki bölüme geç
                        next_level = current_level_idx + 1
                        if next_level in EASY_MODE_LEVELS:
                            current_level_idx = next_level
                            init_game()
                            print(f"Bölüm {current_level_idx}'e geçildi: {EASY_MODE_LEVELS[current_level_idx]['name']}")
                        else:
                            # Oyun bitti
                            GAME_STATE = 'GAME_COMPLETE'

                if GAME_STATE == 'PLAYING':
                    px, py = int(player_x + 15), int(player_y + 15)
                    if event.key == pygame.K_w and jumps_left > 0 and not is_dashing:
                        jumps_left -= 1
                        is_jumping = True
                        is_slamming = False
                        y_velocity = -JUMP_POWER
                        character_state = 'jumping'
                        if JUMP_SOUND:
                            FX_CHANNEL.play(JUMP_SOUND)
                        all_vfx.add(ParticleExplosion(px, py, CURRENT_THEME["player_color"], 6))
                        for _ in range(2):
                            all_vfx.add(EnergyOrb(px + random.randint(-10, 10),
                                                    py + random.randint(-10, 10),
                                                    CURRENT_THEME["border_color"], 4, 15))

                    if event.key == pygame.K_s and is_jumping and not is_dashing and not is_slamming and slam_cooldown <= 0:
                        is_slamming = True
                        slam_stall_timer = 15
                        # Slam Cooldown: Karma ve level buff'ları etkiler
                        slam_cooldown = active_slam_cd
                        y_velocity = 0
                        character_state = 'slamming'
                        slam_collision_check_frames = 0
                        if SLAM_SOUND:
                            FX_CHANNEL.play(SLAM_SOUND)
                        all_vfx.add(ScreenFlash(PLAYER_SLAM, 80, 8))
                        all_vfx.add(Shockwave(px, py, PLAYER_SLAM, max_radius=200, rings=3, speed=25))
                        
                        for _ in range(3):
                            all_vfx.add(LightningBolt(px, py,
                                                        px + random.randint(-60, 60),
                                                        py + random.randint(-60, 60),
                                                        PLAYER_SLAM, 12))

                    if event.key == pygame.K_SPACE and dash_cooldown_timer <= 0 and not is_dashing:
                        is_dashing = True
                        dash_timer = DASH_DURATION
                        # Dash Cooldown: Karma ve level buff'ları etkiler
                        dash_cooldown_timer = active_dash_cd
                        screen_shake = 8
                        dash_particles_timer = 0
                        dash_frame_counter = 0.0
                        character_state = 'dashing'
                        if DASH_SOUND:
                            FX_CHANNEL.play(DASH_SOUND)
                        all_vfx.add(ScreenFlash(METEOR_CORE, 80, 6))
                        all_vfx.add(Shockwave(px, py, METEOR_FIRE, max_radius=120, rings=2, speed=15))
                        
                        keys = pygame.key.get_pressed()
                        dx = (keys[pygame.K_d] - keys[pygame.K_a])
                        dy = (keys[pygame.K_s] - keys[pygame.K_w])
                        if dx == 0 and dy == 0:
                            dx = 1
                        mag = math.sqrt(dx*dx + dy*dy)
                        dash_vx, dash_vy = (dx/mag)*DASH_SPEED, (dy/mag)*DASH_SPEED
                        is_jumping = True
                        y_velocity = 0
                        dash_angle = math.atan2(dash_vy, dash_vx)

        # --- OYUN LOJİĞİ ---
        if GAME_STATE == 'LOADING':
            loading_timer += 1 
            # DÜZELTME: Random yerine sabit modülo kullanarak daha kararlı bir yükleme süreci
            if loading_timer % 10 == 0 and loading_stage < len(fake_log_messages):
                loading_logs.append(fake_log_messages[loading_stage])
                loading_stage += 1
                loading_progress = min(0.95, loading_stage / len(fake_log_messages))
            
            if loading_stage >= len(fake_log_messages):
                loading_progress += 0.02 # Biraz daha hızlı
                if loading_progress >= 1.0:
                    init_game()
                    GAME_STATE = target_state_after_load

        elif GAME_STATE == 'CHAT' or GAME_STATE == 'CUTSCENE':
            story_manager.update(dt)
            if story_manager.is_cutscene:
                GAME_STATE = 'CUTSCENE'
            else:
                GAME_STATE = 'CHAT'
                
        elif GAME_STATE == 'NPC_CHAT':
            # İmleç animasyonu
            npc_cursor_timer += 1
            if npc_cursor_timer >= 30:
                npc_show_cursor = not npc_show_cursor
                npc_cursor_timer = 0

        elif GAME_STATE in ['PLAYING', 'ENDLESS_PLAY']:
            # --- KARMA GÜÇLENMESİ (YENİ) ---
            # Negatif karma oyuncuyu güçlendirir
            current_karma = player_karma
            
            # Level Buff'ı (Varsayılan)
            buff_stacks = (current_level_idx - 1) // 3
            if buff_stacks > 2: buff_stacks = 2
            
            base_speed_mult = 1.0 + (0.25 * buff_stacks)
            base_cd_mult = 0.5 ** buff_stacks
            
            # Karma Buff'ı (Karma Ful ise %25 bonus)
            # Karma -100 veya 100 olduğunda: Hız +%25, CD -%25
            karma_bonus = 0.0
            if abs(current_karma) >= 100:
                # Maksimum bonuslar (Ful Karma)
                karma_speed_bonus = 0.25
                karma_cd_reduction = 0.25
                
                # Çarpanları güncelle
                base_speed_mult += karma_speed_bonus
                base_cd_mult -= karma_cd_reduction
            
            # Değerleri uygula
            active_player_speed = PLAYER_SPEED * base_speed_mult
            active_dash_cd = DASH_COOLDOWN * max(0.2, base_cd_mult) # Minimum %20 CD sınırı
            if vasil_companion:
                active_player_speed = PLAYER_SPEED * 1.5  # %50 Hız Artışı
                active_dash_cd = 0  # Bekleme süresi YOK
                active_slam_cd = 0  # Bekleme süresi YOK
            active_slam_cd = SLAM_COOLDOWN_BASE * max(0.2, base_cd_mult)
            if vasil_companion:
                active_player_speed = PLAYER_SPEED * 1.5  # %50 Hız Artışı
                active_dash_cd = 0  # Bekleme süresi YOK
                active_slam_cd = 0  # Bekleme süresi YOK

            # DİNLENME BÖLGESİNDEN OTOMATİK ÇIKIŞ: Ekranın sağına gidince
            lvl_config = EASY_MODE_LEVELS.get(current_level_idx, EASY_MODE_LEVELS[1])
            if lvl_config.get('type') == 'rest_area':
                if player_x > LOGICAL_WIDTH + 100:
                    # Sonraki bölüme geç
                    next_level = current_level_idx + 1
                    if next_level in EASY_MODE_LEVELS:
                        current_level_idx = next_level
                        init_game()
                        print(f"Bölüm {current_level_idx}'e otomatik geçildi: {EASY_MODE_LEVELS[current_level_idx]['name']}")
                    else:
                        GAME_STATE = 'GAME_COMPLETE'
            else:
                # Normal bölümde kamera hızı artar (Limbo hariç)
                if current_level_idx != 99:  # <-- BU KONTROLÜ EKLE
                    camera_speed = min(MAX_CAMERA_SPEED, camera_speed + SPEED_INCREMENT_RATE * frame_mul)
                    # Skoru sadece normal oyunda arttır
                    score_gain = 0.1 * camera_speed * frame_mul
                    if is_super_mode: score_gain *= 40
                    score += score_gain

            old_x, old_y = player_x, player_y
            keys = pygame.key.get_pressed()
            horizontal_move = keys[pygame.K_d] - keys[pygame.K_a]
            if horizontal_move != 0 and not is_dashing and not is_slamming:
                character_state = 'running'
            elif not is_jumping and not is_dashing and not is_slamming:
                character_state = 'idle'

            is_grounded = not is_jumping and not is_slamming and not is_dashing
            character_animator.update(dt, character_state, is_grounded, y_velocity, is_dashing, is_slamming)

            last_trail_time += frame_mul
            if last_trail_time >= TRAIL_INTERVAL and (is_dashing or is_slamming):
                last_trail_time = 0.0
                trail_color = CURRENT_THEME["player_color"]
                if is_dashing:
                    trail_color = METEOR_FIRE
                    trail_size = random.randint(8, 14)
                elif is_slamming:
                    trail_color = PLAYER_SLAM
                    trail_size = random.randint(8, 12)
                trail_effects.append(TrailEffect(player_x + 15, player_y + 15, trail_color, trail_size, life=12))

            for wave in active_damage_waves[:]:
                wave['r'] += wave['speed'] * frame_mul
                wave['x'] -= camera_speed * frame_mul
                for enemy in all_enemies:
                    dist = math.sqrt((enemy.rect.centerx - wave['x'])**2 + (enemy.rect.centery - wave['y'])**2)
                    if dist < wave['r'] + 20 and dist > wave['r'] - 40:
                        enemy.kill()
                        score += 500
                        # KARMA CEZASI (SLAM WAVE)
                        save_manager.update_karma(-10)
                        player_karma = save_manager.get_karma()
                        enemies_killed_current_level += 1
                        karma_notification_text = "KARMA DÜŞTÜ!"
                        karma_notification_timer = 60
                        
                        all_vfx.add(ParticleExplosion(enemy.rect.centerx, enemy.rect.centery, CURSED_PURPLE, 20))
                        all_vfx.add(ScreenFlash(CURSED_PURPLE, 30, 2))
                if wave['r'] > wave['max_r']:
                    active_damage_waves.remove(wave)

            if is_dashing:
                px, py = int(player_x + 15), int(player_y + 15)
                dash_frame_counter += frame_mul
                for _ in range(4):
                    inv_angle = dash_angle + math.pi + random.uniform(-0.5, 0.5)
                    spark_speed = random.uniform(5, 15)
                    color = random.choice([(255, 50, 0), (255, 150, 0), (255, 255, 100)])
                    all_vfx.add(FlameSpark(px, py, inv_angle, spark_speed, color, life=20, size=random.randint(4, 8)))

                if int(dash_frame_counter) % 5 == 0:
                    all_vfx.add(Shockwave(px, py, (255, 200, 100), max_radius=70, width=2, speed=10))

                meteor_hit_radius = 120
                enemy_hits_aoe = [e for e in all_enemies if math.sqrt((e.rect.centerx - px)**2 + (e.rect.centery - py)**2) < meteor_hit_radius]
                for enemy in enemy_hits_aoe:
                    enemy.kill()
                    score += 500
                        # KARMA CEZASI (DASH KILL)
                    save_manager.update_karma(-10)
                    player_karma = save_manager.get_karma()
                    enemies_killed_current_level += 1
                    
                    karma_notification_text = "KARMA DÜŞTÜ!"
                    karma_notification_timer = 60
                    
                    screen_shake = 10
                    if EXPLOSION_SOUND:
                        FX_CHANNEL.play(EXPLOSION_SOUND)
                    all_vfx.add(ParticleExplosion(enemy.rect.centerx, enemy.rect.centery, METEOR_FIRE, 25))
                    all_vfx.add(Shockwave(enemy.rect.centerx, enemy.rect.centery, (255, 100, 0), max_radius=90, width=4))

                if dash_particles_timer > 0:
                    dash_particles_timer -= frame_mul
                else:
                    dash_particles_timer = 4
                    offset_x = random.randint(-5, 5)
                    offset_y = random.randint(-5, 5)
                    all_vfx.add(WarpLine(px + offset_x, py + offset_y, dash_angle + random.uniform(-0.15, 0.15), METEOR_CORE, METEOR_FIRE))

                player_x += dash_vx * frame_mul
                player_y += dash_vy * frame_mul
                player_x -= camera_speed * frame_mul
                dash_timer -= frame_mul
                if not vasil_companion:
                    dash_timer -= frame_mul
                else:
                    # Vasi varken timer azalmaz, hatta fullenir
                    dash_timer = DASH_DURATION 

                if dash_timer <= 0:
                    is_dashing = False
            elif is_slamming and slam_stall_timer > 0:
                slam_stall_timer -= frame_mul
                slam_collision_check_frames += 1
                if int(slam_stall_timer) % 3 == 0:
                    for _ in range(2):
                        angle = random.uniform(0, math.pi * 2)
                        dist = random.randint(20, 40)
                        ex = player_x + 15 + math.cos(angle) * dist
                        ey = player_y + 15 + math.sin(angle) * dist
                        all_vfx.add(FlameSpark(ex, ey, angle + math.pi, dist/10, PLAYER_SLAM, life=15))

                vibration = random.randint(-1, 1) if slam_stall_timer > 7 else 0
                player_x += vibration
                if slam_stall_timer <= 0:
                    y_velocity = 30
                    screen_shake = 12
                    all_vfx.add(ParticleExplosion(player_x+15, player_y+15, PLAYER_SLAM, 12))

            else:
                # Normal hareket
                if lvl_config.get('type') != 'rest_area':
                    player_x -= camera_speed * frame_mul
                if keys[pygame.K_a]:
                    # YENİ: Hız buff'ını kullan
                    player_x -= active_player_speed * frame_mul
                if keys[pygame.K_d]:
                    # YENİ: Hız buff'ını kullan
                    player_x += active_player_speed * frame_mul
                
                # --- YENİ: SÜPER MOD UÇUŞ MANTIĞI ---
                if is_super_mode:
                    # Yerçekimi yok, W/S ile uçuş
                    y_velocity = 0
                    fly_speed = 15
                    if keys[pygame.K_w]:
                        player_y -= fly_speed * frame_mul
                    if keys[pygame.K_s]:
                        player_y += fly_speed * frame_mul
                else:
                    player_y += y_velocity * frame_mul
                    if is_slamming:
                        y_velocity += SLAM_GRAVITY * 1.8 * frame_mul
                    else:
                        y_velocity += GRAVITY * frame_mul

            attack_sequence = []
            if attack_sequence:
                philosophical_combo = combat_philosophy.create_philosophical_combo(attack_sequence)
                if philosophical_combo:
                    score *= philosophical_combo['power_multiplier']

            if reality_shifter.current_reality != 0:
                reality_effects = reality_shifter.get_current_effects()
                if 'physics' in reality_effects:
                    physics = reality_effects['physics']
                    if 'gravity' in physics:
                        y_velocity += (GRAVITY * physics['gravity'] - GRAVITY) * frame_mul
                    if 'player_speed' in physics:
                        player_x += (PLAYER_SPEED * physics['player_speed'] - PLAYER_SPEED) * frame_mul

            if dash_cooldown_timer > 0:
                dash_cooldown_timer -= frame_mul
            if slam_cooldown > 0:
                slam_cooldown -= frame_mul
            if screen_shake > 0:
                screen_shake -= 1
            if karma_notification_timer > 0:
                karma_notification_timer -= 1

            PLAYER_W, PLAYER_H = 30, 30
            player_rect = pygame.Rect(int(player_x), int(player_y), PLAYER_W, PLAYER_H)
            
            dummy_player = type('',(object,),{'rect':player_rect})()
            enemy_hits = pygame.sprite.spritecollide(dummy_player, all_enemies, False)
            
            for enemy in enemy_hits:
                
                # --- ÇARPIŞMA DÖNGÜSÜ ---
                PLAYER_W, PLAYER_H = 30, 30
                player_rect = pygame.Rect(int(player_x), int(player_y), PLAYER_W, PLAYER_H)
                
                dummy_player = type('',(object,),{'rect':player_rect})()
                enemy_hits = pygame.sprite.spritecollide(dummy_player, all_enemies, False)
                
                for enemy in enemy_hits:
                    
                    # --- SENARYO 1: KURTULUŞ MODU (TILSIM VARSA) ---
                    if has_talisman:
                        # Dash atıyor olsan, Slam vuruyor olsan bile burası çalışır.
                        # Düşmanı öldürme kodu yerine "Kurtarma" kodu çalışır.
                        
                        enemy.kill() # Fiziksel olarak sil
                        
                        # Görsel Efekt: Ruh Yükselişi
                        saved_soul = SavedSoul(enemy.rect.centerx, enemy.rect.centery)
                        all_vfx.add(saved_soul)
                        
                        # Altın Patlama
                        all_vfx.add(ParticleExplosion(enemy.rect.centerx, enemy.rect.centery, (255, 215, 0), 20))
                        all_vfx.add(Shockwave(enemy.rect.centerx, enemy.rect.centery, (255, 255, 200), max_radius=120, width=5))
                        
                        # --- KARMA VE SKOR ARTIŞI ---
                        save_manager.update_karma(25) # HER KURTARIŞ KARMAYI ARTIRIR
                        save_manager.add_saved_soul(1)  # <-- BU SATIRI EKLE
                        score += 1000
                        
                        # Sayaç: Burada "killed" değişkenini artırıyoruz ama UI'da bunu "Kurtarılan" olarak göstereceğiz
                        enemies_killed_current_level += 1 
                        
                        # Bildirim
                        karma_notification_text = "RUH KURTARILDI! (+25)"
                        karma_notification_timer = 40
                        
                        # Ses
                        if JUMP_SOUND: JUMP_SOUND.play()
                        
                        # ÖNEMLİ: Döngünün altına inme, Dash/Slam hasarını pas geç
                        continue 

                    # --- SENARYO 2: NORMAL OYNANIŞ (TILSIM YOKSA) ---
                    
                    # Boss mermisi her türlü öldürür (Tılsım mermiye işlemiyorsa)
                    if isinstance(enemy, EnemyBullet):
                        GAME_STATE = 'GAME_OVER'
                        enemy.kill()
                        continue

                    # Dash veya Slam ile Saldırı
                    if is_dashing or is_slamming or is_super_mode:
                        enemy.kill()
                        score += 500
                            
                        if not is_super_mode: 
                            # Öldürdüğün için Karma Cezası
                            save_manager.update_karma(-10)
                            enemies_killed_current_level += 1
                            karma_notification_text = "KARMA DÜŞTÜ!"
                            karma_notification_timer = 60
                        
                        screen_shake = 15
                        if EXPLOSION_SOUND: FX_CHANNEL.play(EXPLOSION_SOUND)
                        all_vfx.add(ParticleExplosion(enemy.rect.centerx, enemy.rect.centery, CURSED_PURPLE, 20))
                        all_vfx.add(Shockwave(enemy.rect.centerx, enemy.rect.centery, GLITCH_BLACK, max_radius=80, width=5))
                        pygame.time.delay(30)
                        
                    else:
                        # --- YENİ: KARMA DİRİLİŞİ (DIRILME HAKKI) ---
                        if player_karma <= -90 and not has_revived_this_run:
                            has_revived_this_run = True # Hakkı tüket
                            karma_notification_text = "KARANLIK DİRİLİŞ AKTİF!"
                            karma_notification_timer = 120
                            
                            # Ekranı temizle (Şok Dalgası)
                            screen_shake = 30
                            all_vfx.add(ScreenFlash((0, 0, 0), 150, 20)) # Siyah flaş
                            
                            # Tüm düşmanları yok et
                            for e in all_enemies:
                                e.kill()
                                all_vfx.add(ParticleExplosion(e.rect.centerx, e.rect.centery, CURSED_RED, 20))
                            
                            # Düşmanları geriye it (Dalga oluştur)
                            active_damage_waves.append({'x': player_x + 15, 'y': player_y + 15, 'r': 10, 'max_r': 500, 'speed': 40})
                            
                            # Oyuncuyu biraz yukarı at
                            y_velocity = -15
                            is_jumping = True
                            
                            print("Karanlık Diriliş Aktifleşti!")
                        else:
                            # Normal ölüm
                            # YENİ: Level 10'da ölürse Limbo'ya gönder
                            if current_level_idx == 10:
                                init_limbo()
                                GAME_STATE = 'PLAYING'
                                if npcs:
                                    start_npc_conversation(npcs[0])
                            else:
                                GAME_STATE = 'GAME_OVER'
                                high_score = max(high_score, int(score))
                                AMBIENT_CHANNEL.stop()
                                all_vfx.add(ParticleExplosion(player_x, player_y, CURSED_RED, 30))
            
            move_rect = pygame.Rect(int(player_x), int(min(old_y, player_y)), PLAYER_W, int(abs(player_y - old_y)) + PLAYER_H)
            collided_platforms = pygame.sprite.spritecollide(type('',(object,),{'rect':move_rect})(), all_platforms, False)
            
            for p in collided_platforms:
                platform_top = p.rect.top
                if (old_y + PLAYER_H <= platform_top + 15) and (player_y + PLAYER_H >= platform_top):
                    player_y = platform_top - PLAYER_H
                    if is_slamming:
                        y_velocity = -15
                        screen_shake = 30
                        active_damage_waves.append({'x': player_x + 15, 'y': platform_top, 'r': 10, 'max_r': 250, 'speed': 25})
                        for i in range(2):
                            wave = Shockwave(player_x+15, p.rect.top, (255, 180, 80), speed=25)
                            wave.radius = 30 + i*30
                            wave.max_radius = 200 + i*60
                            all_vfx.add(wave)
                        all_vfx.add(ParticleExplosion(player_x+15, p.rect.top, PLAYER_SLAM, 25))
                        is_slamming = False
                        is_jumping = True
                        jumps_left = MAX_JUMPS - 1
                        character_state = 'jumping'
                    else:
                        y_velocity = 0
                        is_jumping = is_slamming = False
                        jumps_left = MAX_JUMPS
                        character_state = 'idle'
                        all_vfx.add(ParticleExplosion(player_x+15, player_y+30, CURRENT_THEME["player_color"], 8))
                    break

            # NPC'leri güncelle
            for npc in npcs:
                npc.update(player_x, player_y, dt)

            # --- VASİ YOLDAŞI MANTIĞI ---
            if vasil_companion:
                # Vasi'yi güncelle
                action = vasil_companion.update(player_x, player_y, all_enemies, boss_manager_system, camera_speed)
                
                # Vasi bir saldırı yapmak istiyor mu?
                if action:
                    act_type, target = action
                    
                    if act_type == "LASER":
                        # Lazer Efekti
                        pygame.draw.line(game_canvas, (0, 255, 100), (vasil_companion.x, vasil_companion.y), target.rect.center, 3)
                        # Düşmanı Yok Et
                        target.kill()
                        
                        # Görsel
                        all_vfx.add(ParticleExplosion(target.rect.centerx, target.rect.centery, (0, 255, 100), 15))
                        
                        # Skoru ve Karmayı Güncelle (Vasi öldürse bile bizim suçumuz)
                        save_manager.update_karma(-5) # Ekstra kötü karma
                        score += 1000
                
                # --- EKSTRA GÜÇLER (-250 Karma Altında) ---
                if save_manager.get_karma() <= -250:
                    # 1. Otomatik Kazık Saldırısı (Her 2 saniyede bir)
                    vasil_companion.spike_timer += 1
                    if vasil_companion.spike_timer > 120:
                        vasil_companion.spike_timer = 0
                        # Ekranda görünen rastgele bir platforma kazık at
                        vis_plats = [p for p in all_platforms if 0 < p.rect.centerx < LOGICAL_WIDTH]
                        if vis_plats:
                            p = random.choice(vis_plats)
                            # DİKKAT: BossSpike oyuncuya zarar verir!
                            # Ama bu modda Vasi bizim dostumuz. 
                            # O yüzden BossSpike sınıfını modifiye etmemiz veya sadece görsel kullanmamız lazım.
                            # Şimdilik "Dost Kazık" (Friendly Fire Off) yapalım:
                            
                            # YENİ BİR EFEKT: Düşmanları öldüren devasa bir şok dalgası
                            all_vfx.add(Shockwave(p.rect.centerx, p.rect.top, (0, 255, 100), max_radius=100, speed=15, rings=2))
                            # O platformdaki düşmanları temizle
                            for e in all_enemies:
                                if e.rect.colliderect(p.rect.inflate(0, -50)): # Platformun üstündekiler
                                    e.kill()
                                    all_vfx.add(ParticleExplosion(e.rect.centerx, e.rect.centery, (0, 255, 100), 20))

            # --- KARMA KONTROLÜ VE VASİ'NİN GELİŞİ ---
            # Eğer Gizli Bölümlerde (11-15) ve karma -100'ü aştıysa Vasi gelir
            if current_level_idx in [11, 12, 13, 14, 15] and save_manager.get_karma() <= -100 and vasil_companion is None:
                vasil_companion = VasilCompanion(player_x, player_y - 100)
                karma_notification_text = "VASİ KATILDI! (-100 KARMA)"
                karma_notification_timer = 120
                
                # Efekt
                all_vfx.add(ScreenFlash((0, 255, 100), 100, 10))
                print("Vasi Yoldaşı oluşturuldu.")
            
            # -250 Karma Bonusu Bildirimi
            if current_level_idx in [11, 12, 13, 14, 15] and save_manager.get_karma() == -250 and karma_notification_timer == 0:
                 karma_notification_text = "VASİ TAM GÜÇ! (-250 KARMA)"
                 karma_notification_timer = 120

            # --- LEVEL 15: SON HAKİKAT (YENİ 2 DAKİKALIK HAYATTA KALMA) ---
            if current_level_idx == 15:
                # 1. SİNEMATİK
                if not level_15_cutscene_played:
                    level_15_cutscene_played = True
                    if AMBIENT_CHANNEL.get_busy(): AMBIENT_CHANNEL.stop()
                    cinematic_assets = asset_paths.copy()
                    cinematic_assets['scenario'] = 'FINAL_MEMORY'
                    AICutscene(screen, clock, cinematic_assets).run()
                    level_15_timer = 0
                    try: AMBIENT_CHANNEL.play(load_sound_asset("assets/music/final_boss.mp3", generate_ambient_fallback, 1.0), loops=-1)
                    except: pass

                # 2. 2 DAKİKALIK HAYATTA KALMA
                if not finisher_active:
                    level_15_timer += dt
                    # Boss'un canını çok yüksek tut (ölmesin)
                    for enemy in all_enemies:
                        if isinstance(enemy, (NexusBoss, AresBoss, VasilBoss)):
                            enemy.health = max(enemy.health, 1000)

                    # 2 dakika doldu mu?
                    if level_15_timer >= 120.0:
                        finisher_active = True
                        finisher_state_timer = 0.0
                        finisher_type = 'GOOD' if player_karma >= 0 else 'BAD'
                        if AMBIENT_CHANNEL.get_busy(): AMBIENT_CHANNEL.stop()
                        screen_shake = 50
                        print(f"FİNAL SEKANS BAŞLADI: {finisher_type}")

                # 3. FİNAL SEKANS (ANIMASYON)
                if finisher_active:
                    finisher_state_timer += dt

                    boss_target = None
                    for e in all_enemies:
                        if isinstance(e, (NexusBoss, AresBoss, VasilBoss)):
                            boss_target = e
                            break

                    if boss_target:
                        if finisher_type == 'GOOD':
                            # İlk 6 saniye: dost saldırıları
                            if finisher_state_timer < 6.0:
                                if frame_count % 2 == 0:
                                    start_x = random.choice([-100, LOGICAL_WIDTH + 100, random.randint(0, LOGICAL_WIDTH)])
                                    start_y = -100 if start_x > 0 and start_x < LOGICAL_WIDTH else random.randint(0, LOGICAL_HEIGHT)

                                    soul = SavedSoul(start_x, start_y)
                                    dx = boss_target.x - start_x
                                    dy = boss_target.y - start_y
                                    dist = math.sqrt(dx*dx + dy*dy)
                                    soul.vy = (dy / dist) * 25
                                    soul.x += (dx / dist) * 25

                                    all_vfx.add(soul)

                                    bx = boss_target.x + random.randint(-50, 50)
                                    by = boss_target.y + random.randint(-50, 50)
                                    all_vfx.add(ParticleExplosion(bx, by, (0, 255, 255), 15))
                                    all_vfx.add(Shockwave(bx, by, (255, 255, 100), max_radius=50, speed=10))

                                karma_notification_text = "TÜM DOSTLAR SALDIRIYOR!"
                                karma_notification_timer = 2

                            # 6. saniyede boss ölür
                            elif finisher_state_timer > 6.0:
                                boss_target.health = 0

                        elif finisher_type == 'BAD':
                            center_x = player_x
                            center_y = player_y
                            if vasil_companion:
                                center_x = vasil_companion.x
                                center_y = vasil_companion.y

                            if finisher_state_timer < 3.0:
                                if frame_count % 2 == 0:
                                    angle = random.uniform(0, math.pi*2)
                                    dist = 300 - (finisher_state_timer * 100)
                                    px = center_x + math.cos(angle) * dist
                                    py = center_y + math.sin(angle) * dist
                                    pygame.draw.line(vfx_surface, (255, 0, 0), (px, py), (center_x, center_y), 2)
                                    all_vfx.add(EnergyOrb(px, py, (255, 50, 50), 4, 10))

                                karma_notification_text = "VASİ: KIYAMET PROTOKOLÜ..."
                                karma_notification_timer = 2

                            elif 3.0 <= finisher_state_timer < 5.0:
                                if int(finisher_state_timer * 10) % 5 == 0:
                                    screen_shake = 100
                                    all_vfx.add(ScreenFlash((255, 255, 255), 255, 60))
                                    all_vfx.add(Shockwave(center_x, center_y, (255, 0, 0), max_radius=2000, width=50, speed=100))
                                    for _ in range(20):
                                        rx = random.randint(0, LOGICAL_WIDTH)
                                        ry = random.randint(0, LOGICAL_HEIGHT)
                                        all_vfx.add(ParticleExplosion(rx, ry, (255, 0, 0), 40))

                            elif finisher_state_timer > 5.0:
                                boss_target.health = 0
            
            # --- BOSS SİSTEMİNİ GÜNCELLE (BÖLÜM 10 VE 15 İÇİN) ---
            if current_level_idx in [10, 15]: 
                # Boss mantığını güncelle
                boss_manager_system.update_logic(
                    current_level_idx, 
                    all_platforms,
                    player_x, 
                    player_karma, 
                    camera_speed, 
                    frame_mul,
                    is_weakened=False  # Artık zayıflatma yok
                )
                
                # Çarpışma kontrolü
                player_hitbox = pygame.Rect(player_x + 5, player_y + 5, 20, 20)
                player_obj_data = {'x': player_x, 'y': player_y}
        
                is_hit = boss_manager_system.check_collisions(
                    player_hitbox,    
                    player_obj_data,  
                    all_vfx,          
                    save_manager      
                )
                
                if is_hit:
                    # 1. Görsel ve Fiziksel Efektler
                    screen_shake = 20
                    all_vfx.add(ScreenFlash((255, 0, 0), 150, 5)) # Kırmızı flaş
                    all_vfx.add(ParticleExplosion(player_x + 15, player_y + 15, (200, 0, 0), 25))
                    
                    # Geri tepme (Knockback)
                    player_x -= 40
                    y_velocity = -10
                    
                    # 2. KARMA HASARI (DÜZELTİLEN KISIM)
                    current_k = save_manager.get_karma()
                    
                    # Hasar miktarını artırdık (Daha ölümcül)
                    damage = 75 
                    
                    # Mantık: Karman ne olursa olsun, darbe seni "Sıfıra" (Yok oluşa) iter.
                    if current_k > 0:
                        save_manager.update_karma(-damage) # İyiyken hasar alırsan düşersin
                    elif current_k < 0:
                        save_manager.update_karma(damage)  # Kötüyken hasar alırsan yükselirsin (Nötre çekilirsin)
                    
                    # 3. ÖLÜM KONTROLÜ (İRADE KIRILMASI)
                    new_k = save_manager.get_karma()
                    
                    # Eğer karma işaret değiştirdiyse (örn: 50'den -25'e düştüysen)
                    # Veya kritik seviyeye (örn: -50 ile +50 arasına) geldiysen ÖLÜRSÜN.
                    if abs(new_k) < 50: 
                        print(">>> İRADE KIRILDI! LİMBO BAŞLATILIYOR <<<")
                        
                        # Karma'yı tam 0 yapalım ki sistem öldüğünü anlasın
                        save_manager.data["karma"] = 0 
                        save_manager.save_data()
                        
                        # Level 10'da olduğumuz için Limbo'ya gönder
                        if current_level_idx == 10:
                            init_limbo()
                            GAME_STATE = 'PLAYING'
                            if npcs:
                                start_npc_conversation(npcs[0])
                        else:
                            GAME_STATE = 'GAME_OVER'
                            save_manager.update_high_score('easy_mode', current_level_idx, score)
                            AMBIENT_CHANNEL.stop()
                    else:
                        # Ölmediysek bildirim göster
                        karma_notification_text = "İRADE HASAR ALDI!"
                        karma_notification_timer = 40
            # --- BÖLÜM HEDEFİ KONTROLÜ ---
            if GAME_STATE == 'PLAYING' and lvl_config.get('type') != 'rest_area':
                base_goal = EASY_MODE_LEVELS.get(current_level_idx, EASY_MODE_LEVELS[1])['goal_score']
                # HEDEF SKOR %25 DÜŞÜRÜLDÜ
                lvl_goal = base_goal * 0.75
                
                # NORMAL VE GİZLİ BÖLÜMLER İÇİN (1-15)
                if current_level_idx <= 15 and score >= lvl_goal:
                    # BÖLÜM BİTİŞİNDE KARMA KONTROLÜ
                    if enemies_killed_current_level == 0:
                        save_manager.update_karma(50) # Pasifist Bonus
                        karma_notification_text = "PASİFİST BONUSU! (+50 KARMA)"
                    else:
                        save_manager.update_karma(5) # Küçük bir hayatta kalma bonusu
                        
                    GAME_STATE = 'LEVEL_COMPLETE'
                    save_manager.unlock_next_level('easy_mode', current_level_idx)
                    save_manager.update_high_score('easy_mode', current_level_idx, score)

            all_platforms.update(camera_speed * frame_mul)
            # FIX: Oyuncu pozisyonunu düşmanlara gönder
            all_enemies.update(camera_speed * frame_mul, dt, (player_x, player_y))

            if current_level_idx in [10, 15]:
                for e in all_enemies:
                    if isinstance(e, (NexusBoss, AresBoss, VasilBoss)):w
            
            # --- MERMİ KUYRUĞU İŞLEME (Spawn Queue) ---
            for enemy in all_enemies:
                if hasattr(enemy, 'spawn_queue') and enemy.spawn_queue:
                    for projectile in enemy.spawn_queue:
                        all_enemies.add(projectile)
                    enemy.spawn_queue = [] # Kuyruğu temizle
            
            # --- BOSS ÖLÜM KONTROLÜ ---
            if lvl_config.get('type') == 'boss_fight' or current_level_idx == 15:
                boss_alive = False
                boss_obj = None
                for e in all_enemies:
                    if isinstance(e, (NexusBoss, AresBoss, VasilBoss)):
                        boss_alive = True
                        boss_obj = e
                        break
                
                if not boss_alive and current_level_idx == 15:
                    # Cutscene Başlatma Kodları
                    score += 150000
                    
                    if AMBIENT_CHANNEL.get_busy(): AMBIENT_CHANNEL.stop()
                    
                    final_karma = save_manager.get_karma()
                    ending_scenario = "GOOD_ENDING" if final_karma >= 0 else "BAD_ENDING"
                    
                    print(f"FİNAL TETİKLENDİ: {ending_scenario}")
                    
                    ending_assets = asset_paths.copy()
                    ending_assets['scenario'] = ending_scenario
                    
                    final_cutscene = AICutscene(screen, clock, ending_assets)
                    final_cutscene.run()
                    
                    GAME_STATE = 'GAME_COMPLETE'
                    save_manager.update_high_score('easy_mode', current_level_idx, score)
            
            for s in stars:
                s.update(camera_speed * frame_mul)
            all_vfx.update(camera_speed * frame_mul)
            
            for trail in trail_effects[:]:
                try:
                    trail.update(camera_speed * frame_mul)
                except:
                    trail.update(camera_speed * frame_mul, dt)
                if trail.life <= 0:
                    trail_effects.remove(trail)

            # Platform Üretimi - Normal ve Gizli Bölümler (1-15) için
            if lvl_config.get('type') != 'rest_area' and current_level_idx != 99:
                # NORMAL VE GİZLİ BÖLÜMLER + BOSS BÖLÜMLERİ İÇİN PLATFORM ÜRET
                if current_level_idx <= 15:
                    if len(all_platforms) > 0 and max(p.rect.right for p in all_platforms) < LOGICAL_WIDTH + 100:
                        add_new_platform()
            # ##############################
            # ÖLÜM KONTROLÜ - EN ÖNEMLİ KISIM
            # ##############################
            # Bu kısım BAĞIMSIZ olmalı, herhangi bir if bloğunun içinde OLMAMALI
            
            # EKRANIN ALTINA DÜŞME
            if player_y > LOGICAL_HEIGHT + 100:
                print(f"ÖLÜM: Ekranın altına düştü! X:{player_x}, Y:{player_y}")
                
                if current_level_idx == 10:  # Boss bölümü
                    init_limbo()
                    GAME_STATE = 'PLAYING'
                    if npcs: 
                        start_npc_conversation(npcs[0])
                elif current_level_idx == 99:  # Limbo
                    # Limbo'da ölme, geri dön
                    player_y = LOGICAL_HEIGHT - 300
                    player_x = 100
                    y_velocity = 0
                    print("Limbo'da düştün, geri döndürüldü!")
                else:
                    # NORMAL ÖLÜM
                    GAME_STATE = 'GAME_OVER'
                    high_score = max(high_score, int(score))
                    save_manager.update_high_score('easy_mode', current_level_idx, score)
                    AMBIENT_CHANNEL.stop()
                    all_vfx.add(ParticleExplosion(player_x, player_y, (255, 0, 0), 30))
                    print(f"Oyun bitti! Skor: {score}")

            # EKRANIN SOLUNA ÇIKMA
            if player_x < -50:
                print(f"Ölüm: Ekranın soluna çıktı! X:{player_x}, Y:{player_y}")
                
                if current_level_idx == 10:  # Boss bölümü
                    init_limbo()
                    GAME_STATE = 'PLAYING'
                    if npcs: 
                        start_npc_conversation(npcs[0])
                elif current_level_idx == 99:  # Limbo
                    # Limbo'da geri dön
                    player_x = 50
                    print("Limbo'da sola çıktın, geri döndürüldü!")
                else:
                    # NORMAL ÖLÜM
                    GAME_STATE = 'GAME_OVER'
                    high_score = max(high_score, int(score))
                    save_manager.update_high_score('easy_mode', current_level_idx, score)
                    AMBIENT_CHANNEL.stop()
                    all_vfx.add(ParticleExplosion(player_x, player_y, (255, 0, 0), 30))
                    print(f"Oyun bitti! Skor: {score}")

            rest_area_manager.update((player_x, player_y))

            if game_settings['quality'] != 'LOW' and frame_count % 10 == 0:
                for npc in npc_ecosystem:
                    if abs(npc.x - player_x) < 500 and abs(npc.y - player_y) < 400:
                        npc.draw(game_canvas, render_offset)

        # --- ÇİZİM ---
        
        # UI Verisi Hazırlama (Her durum için ortak)
        ui_data = {
            'theme': CURRENT_THEME, 
            'score': score, 
            'high_score': high_score,
            'dash_cd': dash_cooldown_timer, 
            'slam_cd': slam_cooldown, 
            'time_ms': time_ms,
            'settings': game_settings,
            'progress': loading_progress,
            'logs': loading_logs,
            'save_data': save_manager.data,
            'level_idx': current_level_idx,
            'level_data': EASY_MODE_LEVELS.get(current_level_idx, EASY_MODE_LEVELS[1]),
            'story_manager': story_manager,
            'philosophical_core': philosophical_core,
            'reality_shifter': reality_shifter,
            'time_layer': time_layer,
            'combat_philosophy': combat_philosophy,
            'endless_modes': endless_modes,
            'current_mode': endless_modes.current_mode if GAME_STATE == 'ENDLESS_PLAY' else None,
            'world_reactor': world_reactor,
            'npcs': npcs,
            'current_npc': current_npc,
            'npc_conversation_active': npc_conversation_active,
            'npc_chat_input': npc_chat_input,
            'npc_chat_history': npc_chat_history,
            'karma': player_karma,
            'kills': enemies_killed_current_level,
            # YENİ: UI'da CD hesaplamak için sabit değerler yerine aktif değerleri gönder
            'active_dash_max': active_dash_cd,
            'active_slam_max': active_slam_cd,
            # YENİ: Terminal Verileri
            'term_input': terminal_input,
            'term_status': terminal_status,
            # YENİ: Level Seçim Sayfalama
            'level_select_page': level_select_page,
            # YENİ: Tılsım bilgisi
            'has_talisman': has_talisman
        }

        if GAME_STATE in ['MENU', 'SETTINGS', 'LOADING', 'LEVEL_SELECT', 'ENDLESS_SELECT', 'TERMINAL']:
            game_canvas.fill(DARK_BLUE)
            for s in stars:
                s.draw(game_canvas)
                s.update(0.5)
            
            # Menü UI'ını çiz
            active_ui_elements = render_ui(game_canvas, GAME_STATE, ui_data, mouse_pos)
                
        # ANA OYUN ÇİZİMİ (CHAT ve CUTSCENE dahil)
        else: 
            try:
                anim_params = character_animator.get_draw_params()
            except:
                anim_params = {}
                
            anim_offset = anim_params.get('screen_shake_offset', (0,0))
            global_offset = (random.randint(-screen_shake, screen_shake), random.randint(-screen_shake, screen_shake)) if screen_shake > 0 else (0,0)
            render_offset = (global_offset[0] + int(anim_offset[0]), global_offset[1] + int(anim_offset[1]))

            if reality_shifter.current_reality != 0:
                reality_effect = reality_shifter.get_visual_effect()
                game_canvas.fill(reality_effect.get('bg_color', CURRENT_THEME["bg_color"]))
            elif time_layer.current_era != 'present':
                era_data = time_layer.eras[time_layer.current_era]
                game_canvas.fill(era_data.get('bg_color', CURRENT_THEME["bg_color"]))
            else:
                game_canvas.fill(CURRENT_THEME["bg_color"])
                
            for s in stars:
                s.draw(game_canvas)
            
            # --- BOSS FIGHT ARKA PLANI ---
            # 10 ve 15. Bölümde Boss silüeti çizilsin
            if current_level_idx in [10, 15]:
                # Mevcut karmayı al
                current_k = save_manager.get_karma()
                
                # Fonksiyona karmayı da gönderiyoruz!
                draw_background_boss_silhouette(game_canvas, current_k, LOGICAL_WIDTH, LOGICAL_HEIGHT)
            # -----------------------------

            vfx_surface.fill((0, 0, 0, 0))
            
            for p in all_platforms:
                p.draw(game_canvas, CURRENT_THEME)
            
            # --- BOSS SALDIRILARINI ÇİZ ---
            boss_manager_system.draw(game_canvas)
            
            for e in all_enemies:
                e.draw(game_canvas, theme=CURRENT_THEME)
            for v in all_vfx:
                v.draw(vfx_surface)
            for trail in trail_effects:
                trail.draw(vfx_surface)
                
            # NPC'leri çiz
            for npc in npcs:
                npc.draw(game_canvas, render_offset)

            if GAME_STATE in ('PLAYING', 'PAUSED', 'GAME_OVER', 'LEVEL_COMPLETE', 'ENDLESS_PLAY', 'CHAT', 'CUTSCENE') and GAME_STATE != 'GAME_OVER':
                p_color = CURRENT_THEME["player_color"]
                if is_dashing:
                    p_color = METEOR_CORE
                elif is_slamming:
                    p_color = PLAYER_SLAM
                elif is_super_mode: # Süper modda parlak altın rengi
                    p_color = (255, 215, 0)
                
                try:
                    modified_color = character_animator.get_modified_color(p_color)
                except:
                    modified_color = p_color
                
                # TILSIM AURASI ÇİZİMİ (YENİ EKLEME)
                if has_talisman:
                    # Altın rengi dönen bir kalkan/aura
                    t = pygame.time.get_ticks() * 0.005
                    px, py = int(player_x + 15) + render_offset[0], int(player_y + 15) + render_offset[1]
                    
                    # Dış Halka
                    radius = 35 + math.sin(t) * 5
                    pygame.draw.circle(game_canvas, (255, 215, 0), (px, py), int(radius), 2)
                    
                    # Dönen parçacıklar
                    for i in range(3):
                        angle = t + (i * 2.09) # 120 derece farkla
                        ox = math.cos(angle) * radius
                        oy = math.sin(angle) * radius
                        pygame.draw.circle(game_canvas, (255, 255, 200), (int(px + ox), int(py + oy)), 4)

                draw_animated_player(
                    game_canvas, CURRENT_SHAPE,
                    int(player_x + 15) + render_offset[0], int(player_y + 15) + render_offset[1], 15,
                    modified_color, anim_params
                )

               
            if vasil_companion:
                vasil_companion.draw(game_canvas)
                
                # Lazer çizimi anlık olduğu için update içinde yapıldı ama 
                # kalıcı bir lazer (beam) istiyorsan buraya eklemelisin.
            
            # KARMA BİLDİRİM EFEKTİ (Ekran ortasında kısa süreli yazı)
            if karma_notification_timer > 0:
                font = pygame.font.Font(None, 40)
                color = (255, 50, 50) if "DÜŞTÜ" in karma_notification_text else (0, 255, 100)
                # Özel durum: Diriliş
                if "DİRİLİŞ" in karma_notification_text: color = (200, 50, 200)
                
                draw_text_with_shadow(game_canvas, karma_notification_text, font, 
                                     (LOGICAL_WIDTH//2, LOGICAL_HEIGHT//2 - 100), color, align="center")
            
            # LEVEL 15 GERİ SAYIM GÖSTERGESİ
            if current_level_idx == 15 and not finisher_active:
                remaining = max(0, 120 - level_15_timer)
                mins = int(remaining // 60)
                secs = int(remaining % 60)
                time_str = f"HAYATTA KAL: {mins:02}:{secs:02}"
                
                # Yanıp sönen kırmızı/beyaz yazı
                text_color = (255, 50, 50) if frame_count % 60 < 30 else (255, 255, 255)
                font_timer = pygame.font.Font(None, 60)
                
                draw_text_with_shadow(game_canvas, time_str, font_timer, 
                                     (LOGICAL_WIDTH//2, 80), text_color, align="center")

            game_canvas.blit(vfx_surface, render_offset)

            # NPC sohbet ekranı (Oyun içi NPC etkileşimi için)
            if GAME_STATE == 'NPC_CHAT':
                draw_npc_chat(game_canvas)

            # SİNEMATİK / HİKAYE MODE OVERLAY
            if GAME_STATE in ['CHAT', 'CUTSCENE']:
                active_ui_elements = draw_cinematic_overlay(game_canvas, story_manager, time_ms, mouse_pos)

            # Dinlenme bölgesi talimatları
            if GAME_STATE == 'PLAYING':
                lvl_config = EASY_MODE_LEVELS.get(current_level_idx, EASY_MODE_LEVELS[1])
                if lvl_config.get('type') == 'rest_area':
                    font = pygame.font.Font(None, 24)
                    instructions = [
                        "E: NPC ile konuş",
                        "T: Sonraki bölüme geç",
                        "WASD: Hareket et",
                        "Sağa git → Otomatik geçiş"
                    ]
                    
                    y_offset = LOGICAL_HEIGHT - 120
                    for instruction in instructions:
                        text_surf = font.render(instruction, True, (200, 255, 200))
                        game_canvas.blit(text_surf, (40, y_offset))
                        y_offset += 25

            if hasattr(rest_area_manager, 'active_area') and rest_area_manager.active_area:
                 pass 

            if game_settings['quality'] != 'LOW':
                for npc in npc_ecosystem:
                    if abs(npc.x - player_x) < 500 and abs(npc.y - player_y) < 400:
                        npc.draw(game_canvas, render_offset)

            # UI ÇİZİMİ (Sadece normal oyun modunda)
            if GAME_STATE not in ['CHAT', 'CUTSCENE']:
                active_ui_elements = render_ui(game_canvas, GAME_STATE, ui_data, mouse_pos)

        # Ekran ölçeklendirme ve gösterim
        target_res = AVAILABLE_RESOLUTIONS[game_settings['res_index']]

        if game_settings['fullscreen']:
            if target_res != (LOGICAL_WIDTH, LOGICAL_HEIGHT):
                scaled_small = pygame.transform.scale(game_canvas, target_res)
                final_game_image = pygame.transform.scale(scaled_small, screen.get_size())
            else:
                final_game_image = pygame.transform.scale(game_canvas, screen.get_size())
        else:
            final_game_image = pygame.transform.scale(game_canvas, screen.get_size())

        screen.blit(final_game_image, (0, 0))

        pygame.display.flip()
        clock.tick(current_fps)

# --- ANA PROGRAM BAŞLANGICI ---
if __name__ == '__main__':
    main()
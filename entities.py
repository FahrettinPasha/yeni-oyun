import pygame
import random
import math
from settings import *

# KONUŞMA SİSTEMİ İÇİN KELİME LİSTESİ
ALIEN_SPEECH = [
    "ZGRR!", "0xDEAD", "##!!", "HATA", "KZZT...", 
    "¥€$?", "NO_SIGNAL", "GÖRDÜM!", "∆∆∆", "SİLİN!"
]

# --- YENİ RENKLER VE ÇİZİM FONKSİYONLARI ---
VOID_PURPLE = (20, 0, 30)
TOXIC_GREEN = (0, 255, 50)
CORRUPT_NEON = (0, 255, 200)

def draw_corrupted_sprite(surface, rect, main_color=VOID_PURPLE):
    """Boss gövdeleri için temiz glitch efekti"""
    x, y, w, h = rect
    pygame.draw.rect(surface, main_color, rect)
    pygame.draw.rect(surface, (10, 5, 10), (x+2, y+2, w-4, h-4))
    if random.random() < 0.3:
        offset = random.randint(-2, 2)
        pygame.draw.rect(surface, CORRUPT_NEON, (x+offset, y, w, h), 1)
    else:
        pygame.draw.rect(surface, (100, 0, 200), rect, 1)
    if random.random() < 0.1:
        line_y = random.randint(y, y + h)
        pygame.draw.line(surface, CORRUPT_NEON, (x, line_y), (x + w, line_y), 1)

def draw_themed_glitch(surface, rect, body_color, neon_color):
    """Düşmanı harita temasına uygun renklerle çizer.
    body_color: O anki temanın platform rengi
    neon_color: O anki temanın kenar/neon rengi
    """
    x, y, w, h = rect
    
    # 1. Ana Gövde (Temanın platform rengi)
    pygame.draw.rect(surface, body_color, rect)
    
    # 2. İç Dolgu (Biraz daha koyuluk kat)
    pygame.draw.rect(surface, (0, 0, 0, 50), (x+2, y+2, w-4, h-4))
    
    # 3. Wireframe / Glitch Çerçevesi (Temanın neon rengi)
    if random.random() < 0.2:
        # Glitch: Çerçeve kayar
        offset = random.randint(-3, 3)
        pygame.draw.rect(surface, neon_color, (x+offset, y, w, h), 1)
    else:
        # Normal: Stabil çerçeve
        pygame.draw.rect(surface, neon_color, rect, 1)

    # 4. Veri Çizgileri
    if random.random() < 0.1:
        line_y = random.randint(y, y + h)
        pygame.draw.line(surface, neon_color, (x, line_y), (x + w, line_y), 1)

# --- ENEMY BASE GÜNCELLEMESİ ---
class EnemyBase(pygame.sprite.Sprite):
    """Tüm düşmanlar için temel sınıf - Konuşma özelliği eklendi"""
    def __init__(self):
        super().__init__()
        self.health = 100
        self.is_active = True
        
        # KONUŞMA SİSTEMİ
        self.speech_text = ""
        self.speech_timer = 0
        self.speech_duration = 0
        self.speech_font = pygame.font.Font(None, 24)
        self.spawn_queue = [] # YENİ: Mermi kuyruğu

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.is_active = False
            return True
        return False

    def update_speech(self, dt):
        """Rastgele konuşma mantığı"""
        # Mevcut yazının süresini azalt
        if self.speech_duration > 0:
            self.speech_duration -= dt
            if self.speech_duration <= 0:
                self.speech_text = ""
        
        # Rastgele yeni konuşma başlat (%0.5 şans her karede)
        if self.speech_text == "" and random.random() < 0.005:
            self.speech_text = random.choice(ALIEN_SPEECH)
            self.speech_duration = 2.0 # 2 saniye ekranda kalsın

    def draw_speech(self, surface, x, y):
        """Konuşma balonunu çizer"""
        if self.speech_text:
            text_surf = self.speech_font.render(self.speech_text, True, (255, 50, 50))
            # Yazıyı düşmanın biraz yukarısına ortala
            text_rect = text_surf.get_rect(center=(x, y - 30))
            
            # Arkaplan kutusu (daha okunaklı olsun diye)
            bg_rect = text_rect.inflate(10, 5)
            pygame.draw.rect(surface, (0, 0, 0, 200), bg_rect)
            pygame.draw.rect(surface, (255, 0, 0), bg_rect, 1)
            
            surface.blit(text_surf, text_rect)

class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, theme_index=0):
        super().__init__()
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, y, width, height)
        self.theme_index = theme_index
        self.hover_effect = 0.0
        self.pulse_direction = 1

    def draw(self, surface, theme=None, camera_offset=(0, 0)):
        offset_x, offset_y = camera_offset
        draw_rect = pygame.Rect(
            self.rect.x + offset_x,
            self.rect.y + offset_y,
            self.width,
            self.height
        )
        
        # Varsayılan renkler
        fill_c = (10, 30, 10)
        border_c = (50, 255, 50)
        
        if theme:
            fill_c = theme["platform_color"]
            border_c = theme["border_color"]
        
        # Hover efekti için renk parlaklığı
        hover_factor = 1.0 + self.hover_effect * 0.2
        fill_c = (
            min(255, int(fill_c[0] * hover_factor)),
            min(255, int(fill_c[1] * hover_factor)),
            min(255, int(fill_c[2] * hover_factor))
        )
        
        pygame.draw.rect(surface, fill_c, draw_rect, border_radius=5)
        
        border_width = 2 + int(self.hover_effect * 3)
        pygame.draw.rect(surface, border_c, draw_rect, border_width, border_radius=5)
        
        top_line_color = (
            min(255, border_c[0] + 50),
            min(255, border_c[1] + 50),
            min(255, border_c[2] + 50)
        )
        pygame.draw.line(surface, top_line_color, 
                        (draw_rect.left, draw_rect.top), 
                        (draw_rect.right, draw_rect.top), 
                        3)
        
        shadow_rect = pygame.Rect(draw_rect.x, draw_rect.bottom, draw_rect.width, 3)
        shadow_color = (max(0, fill_c[0] - 30), max(0, fill_c[1] - 30), max(0, fill_c[2] - 30))
        pygame.draw.rect(surface, shadow_color, shadow_rect)

    def update(self, camera_speed, dt=0.016):
        self.rect.x -= camera_speed
        
        self.hover_effect += self.pulse_direction * dt * 3
        if self.hover_effect >= 1.0:
            self.hover_effect = 1.0
            self.pulse_direction = -1
        elif self.hover_effect <= 0.0:
            self.hover_effect = 0.0
            self.pulse_direction = 1
        
        if self.rect.right < 0:
            self.kill()
            
    def activate_hover(self):
        self.hover_effect = 1.0
        self.pulse_direction = -1

class Star:
    def __init__(self, screen_width, screen_height):
        self.x = random.randrange(0, screen_width)
        self.y = random.randrange(0, screen_height)
        self.size = random.randint(1, 3)
        self.speed = random.uniform(0.5, 1.5)
        self.brightness = random.randint(150, 255)
        self.twinkle_speed = random.uniform(0.5, 2.0)
        self.twinkle_offset = random.uniform(0, math.pi * 2)
        self.screen_width = screen_width
        self.screen_height = screen_height

    def update(self, camera_speed, dt=0.016):
        self.x -= self.speed * camera_speed / 3
        
        time = pygame.time.get_ticks() * 0.001
        twinkle = (math.sin(time * self.twinkle_speed + self.twinkle_offset) + 1) / 2
        self.brightness = int(150 + twinkle * 105)
        
        if self.x < 0:
            self.x = self.screen_width
            self.y = random.randrange(0, self.screen_height)
            self.brightness = random.randint(150, 255)

    def draw(self, surface):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), self.size)
        
        if self.size >= 2:
            glow_radius = self.size + 1
            for i in range(3, 0, -1):
                glow_alpha = int(self.brightness * 0.3 * (i / 3))
                glow_color = (color[0], color[1], color[2], glow_alpha)
                temp_surface = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(temp_surface, glow_color, (glow_radius, glow_radius), glow_radius)
                surface.blit(temp_surface, (int(self.x) - glow_radius, int(self.y) - glow_radius))

# --- DÜŞMAN SINIFLARI ---

# YENİ: Gelişmiş Düşman Mermisi (Nişan alabilen)
class EnemyProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x=None, target_y=None, speed=10):
        super().__init__()
        self.rect = pygame.Rect(x, y, 15, 15) 
        
        # Nişan alma mantığı
        if target_x is not None and target_y is not None:
            dx = target_x - x
            dy = target_y - y
            angle = math.atan2(dy, dx)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
        else:
            # Hedef yoksa sola düz git
            self.vx = -speed
            self.vy = 0
            
        self.color = (255, 0, 0) 
        self.timer = 0

    def update(self, camera_speed, dt=0.016, player_pos=None):
        self.rect.x -= camera_speed
        self.rect.x += self.vx
        self.rect.y += self.vy
        
        self.timer += dt
        # Yanıp sönme efekti
        if int(self.timer * 20) % 2 == 0:
            self.color = (255, 255, 0)
        else:
            self.color = (255, 0, 0)

        if self.rect.right < 0 or self.rect.y > LOGICAL_HEIGHT or self.rect.y < 0:
            self.kill()

    def draw(self, surface, camera_offset=(0, 0), theme=None):  # theme parametresi eklendi
        offset_x, offset_y = camera_offset
        draw_rect = pygame.Rect(
            self.rect.x + offset_x,
            self.rect.y + offset_y,
            self.rect.width,
            self.rect.height
        )
        pygame.draw.circle(surface, self.color, draw_rect.center, 7)
        pygame.draw.circle(surface, (255, 255, 255), draw_rect.center, 3)

class CursedEnemy(EnemyBase):
    def __init__(self, platform, theme_index=0):
        super().__init__()
        self.platform = platform
        self.width = 40
        self.height = 40
        self.theme_index = theme_index
        
        safe_x = random.randint(platform.rect.left, max(platform.rect.left, platform.rect.right - self.width))
        self.rect = pygame.Rect(safe_x, platform.rect.top - self.height, self.width, self.height)
        
        self.speed = 2
        self.direction = random.choice([-1, 1])
        self.timer = 0
        self.face_id = random.choice([0, 1]) # Farklı yüz tipleri

    def update(self, camera_speed, dt=0.016, player_pos=None):
        if not self.is_active: return
        self.update_speech(dt)

        self.rect.x -= camera_speed
        self.rect.x += self.speed * self.direction
        
        if self.rect.right > self.platform.rect.right:
            self.direction = -1
        elif self.rect.left < self.platform.rect.left:
            self.direction = 1
        
        self.timer += dt
        if self.rect.right < 0: self.kill()
        if not self.platform.alive(): self.kill()

    def draw(self, surface, camera_offset=(0, 0), theme=None): # theme parametresi eklendi
        if not self.is_active: return
        ox, oy = camera_offset
        
        # Tema renklerini belirle (Yoksa varsayılan mor/yeşil kullan)
        if theme:
            body_col = theme['platform_color']
            neon_col = theme['border_color']
        else:
            body_col = (40, 30, 50)
            neon_col = (0, 255, 100)

        # Hafif zıplama
        hover = math.sin(self.timer * 5) * 3
        draw_rect = pygame.Rect(self.rect.x + ox, self.rect.y + oy + hover, self.width, self.height)
        
        # 1. Temalı Gövde
        draw_themed_glitch(surface, draw_rect, body_col, neon_col)
        
        # 2. Yüz İfadesi (Neon renginde)
        # Gözler
        pygame.draw.rect(surface, neon_col, (draw_rect.x + 8, draw_rect.y + 10, 6, 6))
        pygame.draw.rect(surface, neon_col, (draw_rect.right - 14, draw_rect.y + 10, 6, 6))
        
        # Ağız (Dikdörtgen, ara sıra genişleyen)
        mouth_w = 20
        if random.random() < 0.05: mouth_w = 24
        pygame.draw.rect(surface, neon_col, (draw_rect.x + 10, draw_rect.y + 25, mouth_w, 4))
        
        # Konuşma balonu
        self.draw_speech(surface, self.rect.centerx + ox, self.rect.top + oy + hover)

class DroneEnemy(EnemyBase):
    """Uçan Drone - Rastgele hareket ve oyuncuya nişan alma"""
    def __init__(self, x, y):
        super().__init__()
        self.width = 40
        self.height = 40
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.timer = random.uniform(0, 100)
        self.shoot_timer = 0
        
        # Hareket hedefleri
        self.target_x = x
        self.target_y = y
        self.move_timer = 0
        self.recoil_x = 0
        
    def update(self, camera_speed, dt=0.016, player_pos=None):
        if not self.is_active: return
        
        # Konuşma güncellemesi
        self.update_speech(dt)
        
        self.rect.x -= camera_speed
        self.target_x -= camera_speed # Hedefi de kaydır
        
        # Rastgele uçuş rotası belirle
        self.move_timer -= dt
        if self.move_timer <= 0:
            self.move_timer = random.uniform(1.0, 2.5)
            self.target_x = self.rect.x + random.uniform(-100, 100)
            self.target_y = max(50, min(LOGICAL_HEIGHT - 150, self.rect.y + random.uniform(-80, 80)))

        # Hedefe yumuşak geçiş (Lerp)
        self.rect.x += (self.target_x - self.rect.x) * 2 * dt
        self.rect.y += (self.target_y - self.rect.y) * 2 * dt
        
        # Geri tepme iyileşmesi
        self.recoil_x *= 0.9
        
        # ATEŞ ETME MANTIĞI GÜNCELLEMESİ
        self.shoot_timer += dt
        
        # ESKİ KOD: if self.shoot_timer > 2.5: 
        # YENİ KOD: Süreyi 2.5'ten 0.8'e düşürdük (Yaklaşık 3 kat hızlı ateş eder)
        if self.shoot_timer > 0.8: 
            self.shoot_timer = 0
            self.recoil_x = 10 
            
            # OYUNCUYA KİLİTLENME (Lock-On)
            px, py = None, None
            if player_pos:
                # player_pos'un formatını güvenli şekilde al
                if hasattr(player_pos, 'center'):
                    px, py = player_pos.center
                elif isinstance(player_pos, (tuple, list)):
                    px, py = player_pos[0], player_pos[1]
            
            # Eğer oyuncu bulunduysa TAM ÜZERİNE nişan al
            if px is not None and py is not None:
                # Mermi hızını (speed) da artırabilirsin, örn: 12 -> 15
                projectile = EnemyProjectile(self.rect.centerx, self.rect.centery, px, py, speed=15)
                for group in self.groups():
                    group.add(projectile)
            else:
                # Oyuncu bulunamazsa düz sola ateş et
                projectile = EnemyProjectile(self.rect.centerx, self.rect.centery, target_x=self.rect.x - 100, target_y=self.rect.y, speed=15)
                for group in self.groups():
                    group.add(projectile)
        
        if self.rect.right < 0: self.kill()

    def draw(self, surface, camera_offset=(0, 0), theme=None):
        if not self.is_active: return
        ox, oy = camera_offset
        
        # Tema renkleri
        if theme:
            body_col = theme['bg_color'] # Drone havada olduğu için arkaplan rengine yakın olsun
            neon_col = theme['border_color']
        else:
            body_col = (20, 20, 30)
            neon_col = (0, 255, 200)

        cx = self.rect.centerx + ox + self.recoil_x
        cy = self.rect.centery + oy
        
        # Süzülme
        cy += math.sin(pygame.time.get_ticks() * 0.005) * 5

        # 1. Elmas Gövde
        points = [(cx, cy - 20), (cx + 20, cy), (cx, cy + 20), (cx - 20, cy)]
        pygame.draw.polygon(surface, body_col, points)
        
        # Çerçeve (Bazen beyazlayarak parlar)
        border_c = neon_col if random.random() > 0.1 else (255, 255, 255)
        pygame.draw.polygon(surface, border_c, points, 2)
        
        # 2. Merkez Göz (Kırmızı kalmalı, tehlikeyi belirtir)
        charge = min(1, self.shoot_timer / 0.8)
        eye_color = (255, int(255 * charge), 0)
        pygame.draw.circle(surface, eye_color, (int(cx), int(cy)), int(4 + charge * 6))
        
        # 3. Yörünge Parçaları (Neon Renginde)
        angle = pygame.time.get_ticks() * 0.01
        orbit_x = cx + math.cos(angle) * 35
        orbit_y = cy + math.sin(angle) * 10
        pygame.draw.rect(surface, neon_col, (orbit_x, orbit_y, 4, 4))

        self.draw_speech(surface, cx, self.rect.top + oy - 20)

class TankEnemy(EnemyBase):
    """Devasa Zırhlı Tank - Zıplayan ve Nişan Alan"""
    def __init__(self, platform):
        super().__init__()
        self.platform = platform
        self.width = 160 # 2 Kat arttırıldı (Önceki 40 -> 80 -> Şimdi 160)
        self.height = 140
        self.health = 500 
        
        self.rect = pygame.Rect(
            platform.rect.centerx - 80, 
            platform.rect.top - self.height, 
            self.width, 
            self.height
        )
        self.vx = 2
        self.vy = 0
        self.on_ground = True
        self.move_timer = 0
        self.barrel_angle = 0
        self.shoot_timer = 0
        self.muzzle_flash = 0
        
    def update(self, camera_speed, dt=0.016, player_pos=None):
        if not self.is_active: return
        self.update_speech(dt) # Konuşma özelliği kalsın

        # Kamera kayması
        self.rect.x -= camera_speed
        self.move_timer += dt
        
        # --- AĞIR HAREKET FİZİĞİ (ZIPLAMA YOK) ---
        
        # 1. Yerçekimi (Her zaman uygulanır ki boşluğa düşerse süzülmesin)
        self.vy += 0.8 
        self.rect.y += self.vy
        
        # 2. Zemin Kontrolü (Platformun üstünde mi?)
        # Basit çarpışma kontrolü
        if self.rect.bottom >= self.platform.rect.top and self.vy > 0:
            # Platformun içine girdiyse yukarı taşı
            if self.rect.bottom - self.vy <= self.platform.rect.top + 10: 
                self.rect.bottom = self.platform.rect.top
                self.vy = 0
                self.on_ground = True
        else:
            self.on_ground = False

        # 3. Yatay Hareket (Sadece yerdeyken)
        if self.on_ground:
            self.rect.x += self.vx
            
            # Palet animasyonu için timer
            self.move_timer += dt

            # --- KENAR KONTROLÜ: Zıplamak yerine geri dön ---
            # Platformun sağına geldiyse
            if self.rect.right > self.platform.rect.right:
                self.rect.right = self.platform.rect.right
                self.vx *= -1 # Yönü tersine çevir
            
            # Platformun soluna geldiyse
            elif self.rect.left < self.platform.rect.left:
                self.rect.left = self.platform.rect.left
                self.vx *= -1 # Yönü tersine çevir

        # --- NİŞAN ALMA VE ATEŞ ETME (Aynı kalıyor) ---
        target_x, target_y = self.rect.x - 200, self.rect.centery
        
        if player_pos:
            if hasattr(player_pos, 'center'):
                target_x, target_y = player_pos.center
            elif isinstance(player_pos, (tuple, list)):
                target_x, target_y = player_pos[0], player_pos[1]

        dx = target_x - self.rect.centerx
        dy = target_y - (self.rect.y + 30)
        target_angle = math.atan2(dy, dx)
        
        self.barrel_angle += (target_angle - self.barrel_angle) * 0.1
        
        self.shoot_timer += dt
        self.muzzle_flash = max(0, self.muzzle_flash - 1)
        
        angle_diff = abs(target_angle - self.barrel_angle)
        if self.shoot_timer > 1.5 and angle_diff < 0.2:
            self.shoot_timer = 0
            self.muzzle_flash = 5
            
            barrel_len = 80
            bx = self.rect.centerx + math.cos(self.barrel_angle) * barrel_len
            by = (self.rect.y + 30) + math.sin(self.barrel_angle) * barrel_len
            
            # Mermi oluştur
            projectile = EnemyProjectile(bx, by, target_x, target_y, speed=15)
            projectile.rect.width = 25
            projectile.rect.height = 25
            for group in self.groups():
                group.add(projectile)

        if self.rect.right < 0: self.kill()
        if not self.platform.alive(): self.kill()
        
    def draw(self, surface, camera_offset=(0, 0), theme=None):
        if not self.is_active: return
        ox, oy = camera_offset
        
        # Tema renkleri
        if theme:
            body_col = theme['platform_color']
            neon_col = theme['border_color']
        else:
            body_col = (50, 50, 50)
            neon_col = (255, 100, 0)

        draw_rect = pygame.Rect(self.rect.x + ox, self.rect.y + oy, self.width, self.height)
        
        # 1. Paletler (Standart Koyu Gri)
        track_h = 25
        pygame.draw.rect(surface, (15, 15, 15), (draw_rect.x, draw_rect.bottom - track_h, self.width, track_h))
        
        # 2. Ana Gövde (Tema Rengi)
        body_rect = pygame.Rect(draw_rect.x + 5, draw_rect.y + 40, self.width - 10, self.height - 65)
        draw_themed_glitch(surface, body_rect, body_col, neon_col)
        
        # 3. Kule (Tema Rengi + Neon Çerçeve)
        turret_rect = pygame.Rect(draw_rect.centerx - 30, body_rect.top - 30, 60, 40)
        pygame.draw.rect(surface, body_col, turret_rect)
        pygame.draw.rect(surface, neon_col, turret_rect, 2)
        
        # 4. Namlu
        end_x = draw_rect.centerx + math.cos(self.barrel_angle) * 70
        end_y = (body_rect.top + 10) + math.sin(self.barrel_angle) * 70
        
        pygame.draw.line(surface, (80, 80, 80), (draw_rect.centerx, body_rect.top + 10), (end_x, end_y), 12)
        # Şarj oldukça neon rengi parlasın
        charge = min(1, self.shoot_timer / 1.5)
        if charge > 0.5:
             pygame.draw.line(surface, neon_col, (draw_rect.centerx, body_rect.top + 10), (end_x, end_y), 4)

        self.draw_speech(surface, self.rect.centerx + ox, self.rect.top + oy - 20)


class NPC:
    """Dinlenme alanında bulunan NPC"""
    def __init__(self, x, y, name, color, personality_type="philosopher", prompt=None):
        self.x = x
        self.y = y
        self.name = name
        self.color = color
        self.personality_type = personality_type
        self.prompt = prompt
        self.ai_active = False 
        
        self.width = 70
        self.height = 90
        self.rect = pygame.Rect(x - self.width//2, y - self.height//2, self.width, self.height)
        
        self.talk_radius = 200
        self.can_talk = False
        self.talking = False
        
        self.idle_timer = random.uniform(0, 10)
        self.float_offset = 0
        self.float_speed = random.uniform(0.03, 0.07)
        self.float_amplitude = random.uniform(2, 4)
        
        self.glow_intensity = 0.0
        self.glow_direction = 1
        self.energy_pulse = 0.0
        self.eye_phase = random.uniform(0, math.pi*2)
        self.blink_timer = random.uniform(0, 5)
        
        self.personality_colors = {
            "philosopher": (100, 200, 255),
            "warrior": (255, 100, 100),
            "merchant": (255, 200, 100),
            "mystic": (200, 100, 255),
            "guide": (100, 255, 150)
        }
        
    def update(self, player_x, player_y, dt=0.016):
        self.idle_timer += dt
        self.float_offset = math.sin(self.idle_timer * self.float_speed) * self.float_amplitude
        self.blink_timer -= dt
        if self.blink_timer <= 0:
            self.blink_timer = random.uniform(2, 4)
            
        self.glow_intensity += self.glow_direction * dt * 1.5
        if self.glow_intensity >= 1.0:
            self.glow_intensity = 1.0
            self.glow_direction = -1
        elif self.glow_intensity <= 0.0:
            self.glow_intensity = 0.0
            self.glow_direction = 1
            
        self.energy_pulse = (math.sin(self.idle_timer * 2) + 1) / 2
        
        dist = math.sqrt((player_x - self.x)**2 + (player_y - self.y)**2)
        self.can_talk = dist < self.talk_radius
        
        if self.can_talk:
            self.glow_intensity = min(1.0, self.glow_intensity + dt * 3)

    def draw(self, surface, camera_offset=(0,0)):
        offset_x, offset_y = camera_offset
        draw_x = self.x + offset_x
        draw_y = self.y + offset_y + self.float_offset
        
        hologram_alpha = int(100 + 50 * self.energy_pulse)
        for i in range(3):
            offset = (i+1) * 2
            ghost_rect = pygame.Rect(draw_x - 30 + offset, draw_y - 40 + offset, 60, 80)
            pygame.draw.rect(surface, (*self.color, hologram_alpha//(i+1)), ghost_rect, border_radius=10)
        
        body_color = (
            min(255, self.color[0] + int(50 * self.glow_intensity)),
            min(255, self.color[1] + int(50 * self.glow_intensity)),
            min(255, self.color[2] + int(50 * self.glow_intensity))
        )
        body_rect = pygame.Rect(draw_x - 30, draw_y - 40, 60, 80)
        pygame.draw.rect(surface, body_color, body_rect, border_radius=10)
        
        border_color = (
            min(255, body_color[0] + 50),
            min(255, body_color[1] + 50),
            min(255, body_color[2] + 50)
        )
        pygame.draw.rect(surface, border_color, body_rect, 3, border_radius=10)
        
        eye_y = draw_y - 15
        eye_offset = math.sin(self.idle_timer * 3) * 2
        
        pygame.draw.circle(surface, (255, 255, 255), (draw_x - 15 + eye_offset, eye_y), 10)
        pygame.draw.circle(surface, (255, 255, 255), (draw_x + 15 - eye_offset, eye_y), 10)
        
        pupil_offset_x = math.sin(self.eye_phase) * 3
        pupil_offset_y = math.cos(self.eye_phase) * 2
        
        pygame.draw.circle(surface, (0, 100, 200), (draw_x - 15 + eye_offset + pupil_offset_x, eye_y + pupil_offset_y), 5)
        pygame.draw.circle(surface, (0, 100, 200), (draw_x + 15 - eye_offset + pupil_offset_x, eye_y + pupil_offset_y), 5)
        
        if self.blink_timer < 0.3:
            blink_height = int(10 * (0.3 - self.blink_timer) * 3)
            pygame.draw.rect(surface, body_color, (draw_x - 25, eye_y - 10, 50, blink_height))
        
        mouth_y = draw_y + 20
        mouth_width = 30
        
        if self.can_talk and not self.talking:
            mouth_rect = pygame.Rect(draw_x - mouth_width//2, mouth_y, mouth_width, 5)
            pygame.draw.rect(surface, (50, 50, 50), mouth_rect, border_radius=2)
        else:
            pygame.draw.line(surface, (50, 50, 50), (draw_x - mouth_width//2, mouth_y), (draw_x + mouth_width//2, mouth_y), 3)
        
        font = pygame.font.Font(None, 26)
        name_surf = font.render(self.name, True, (255, 255, 255))
        name_shadow = font.render(self.name, True, (0, 0, 0))
        name_rect = name_surf.get_rect(center=(draw_x, draw_y + 70))
        
        surface.blit(name_shadow, (name_rect.x + 2, name_rect.y + 2))
        surface.blit(name_surf, name_rect)
        
        type_font = pygame.font.Font(None, 20)
        type_text = type_font.render(f"[{self.personality_type}]", True, self.personality_colors.get(self.personality_type, (200, 200, 200)))
        type_rect = type_text.get_rect(center=(draw_x, draw_y + 90))
        surface.blit(type_text, type_rect)
        
        if self.can_talk and not self.talking:
            bubble_x = draw_x
            bubble_y = draw_y - 100
            pygame.draw.circle(surface, (255, 255, 255), (bubble_x, bubble_y), 25)
            pygame.draw.circle(surface, (0, 150, 150), (bubble_x, bubble_y), 25, 2)
            font = pygame.font.Font(None, 32)
            e_text = font.render("E", True, (0, 100, 100))
            e_rect = e_text.get_rect(center=(bubble_x, bubble_y))
            surface.blit(e_text, e_rect)
            points = [(bubble_x, bubble_y + 20), (bubble_x - 10, bubble_y + 40), (bubble_x + 10, bubble_y + 40)]
            pygame.draw.polygon(surface, (255, 255, 255), points)
            pygame.draw.polygon(surface, (0, 150, 150), points, 2)
            
    def generate_greeting(self):
        greetings = {
            "philosopher": ["Mağaradaki gölgelerden korkma, onlar sadece birer yansıma.", "Cebindeki kimlik boş olabilir ama zihnin dolu olmalı İsimsiz."],
            "warrior": ["Gözlerinde bir savaşçının ateşi var. Egemenler bundan korkacak.", "Skorun yüksek ama kılıcın keskin mi?"],
            "mystic": ["Gelecekte cam kırıkları görüyorum... Çok fazla cam kırığı.", "Ruhun Fragmentia'nın titreşimleriyle uyumsuz. Bu bir lütuf."],
            "guide": ["Bu yol tehlikeli. Mide'den çıkmak herkesin harcı değil.", "Haritalar yalan söyler, içgüdülerine güven."],
            "merchant": ["..."]
        }
        import random
        return random.choice(greetings.get(self.personality_type, ["Merhaba."]))
        
    def start_conversation(self):
        self.talking = True
        if self.prompt: return self.prompt
        return self.generate_greeting()
            
    def send_message(self, player_message, game_context=None):
        responses = {
            "philosopher": ["Hakikat acıdır ama iyileştirir.", "20 Egemen sadece kendi korkularının esiri.", "Özgürlük, puanlarla satın alınamaz."],
            "warrior": ["Daha sert vurmalısın. Tereddüt edersen ölürsün.", "Düşmanlarına merhamet etme. Onlar sana etmeyecek."],
            "mystic": ["Kaderin ipleri düğümlenmiş.", "Bir seçim yapacaksın ve bu tüm şehri yakacak.", "Görüyorum... Dört farklı son görüyorum."],
            "guide": ["Sağdaki tünel tuzahtı, iyi ki oradan gitmedin.", "Skorunu koru ama ruhunu satma."]
        }
        import random
        return random.choice(responses.get(self.personality_type, ["Anladım."]))
            
    def end_conversation(self):
        self.talking = False
        return ""

# --- YENİ BOSS SINIFLARI ---

class AresBoss(EnemyBase):
    """LOW KARMA BOSS: Glitch Samurai"""
    def __init__(self, x, y):
        super().__init__()
        self.width, self.height = 100, 140
        self.x, self.y = x, y
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.health = 2500
        self.max_health = 2500
        self.state = "IDLE" 
        self.timer = 0
        self.target_x = x
        self.vy = 0

    def update(self, camera_speed, dt=0.016, player_pos=None):
        if not self.is_active: return
        self.update_speech(dt)
        px, py = 0, 0
        if player_pos:
            if isinstance(player_pos, tuple): px, py = player_pos
            else: px, py = player_pos.center
        self.timer += dt
        
        # Attack Logic
        if self.state == "IDLE":
            direction = 1 if px > self.rect.centerx else -1
            self.rect.x += direction * 2
            if self.timer > 2.0:
                self.timer = 0
                r = random.random()
                if r < 0.4: self.state = "PREP_DASH"; self.speech_text = "KAÇAMAZSIN!"
                elif r < 0.7: self.state = "PREP_SMASH"; self.speech_text = "EZİLECEKSİN!"
                else: self.state = "PREP_BEAM"; self.speech_text = "KESİP ATACAĞIM!"
                self.speech_duration = 1.0

        elif self.state == "PREP_DASH":
            if self.timer > 0.5: self.state = "DASH"; self.timer = 0; self.target_x = px
        elif self.state == "DASH":
            self.rect.x += (1 if self.target_x > self.rect.centerx else -1) * 25
            if self.timer > 0.8: self.state = "IDLE"; self.timer = 0
        
        elif self.state == "PREP_SMASH":
            if self.timer < 0.02: self.vy = -20
            self.vy += 1
            self.rect.y += self.vy
            if self.rect.bottom >= LOGICAL_HEIGHT - 50:
                self.rect.bottom = LOGICAL_HEIGHT - 50
                self.state = "IDLE"; self.timer = 0
                wave = EnemyProjectile(self.rect.centerx, self.rect.bottom-20, self.rect.centerx-500, self.rect.bottom-20, speed=15)
                wave.rect.width, wave.rect.height, wave.color = 40, 20, (255, 100, 0)
                self.spawn_queue.append(wave)

        elif self.state == "PREP_BEAM":
            if self.timer > 0.8:
                self.state = "IDLE"; self.timer = 0
                beam = EnemyProjectile(self.rect.centerx, self.rect.centery, px, py, speed=20)
                beam.rect.width, beam.rect.height, beam.color = 10, 100, (200, 200, 255)
                self.spawn_queue.append(beam)

        if self.state != "PREP_SMASH":
             self.rect.bottom = min(self.rect.bottom, LOGICAL_HEIGHT - 50)

    def draw(self, surface, camera_offset=(0, 0), theme=None):
        if not self.is_active: return
        ox, oy = camera_offset
        x, y = self.rect.x + ox + random.randint(-2,2), self.rect.y + oy + random.randint(-2,2)
        armor_col, neon_col, blade_col = (40, 10, 10), (255, 60, 0), (255, 200, 200)
        
        # Cape
        for i in range(5):
            sx, sy = x+20, y+20
            ex = sx-60-(i*10)+math.sin(pygame.time.get_ticks()*0.01+i)*20
            ey = sy-20+(i*15)
            pygame.draw.line(surface, (200, 50, 50), (sx, sy), (ex, ey), 3)
        # Body
        pygame.draw.polygon(surface, armor_col, [(x,y), (x+100,y), (x+80,y+80), (x+20,y+80)])
        draw_corrupted_sprite(surface, pygame.Rect(x+20, y+10, 60, 60), armor_col)
        # Shoulders
        pygame.draw.polygon(surface, neon_col, [(x-10,y), (x+20,y), (x+20,y+30)], 2)
        pygame.draw.polygon(surface, neon_col, [(x+80,y), (x+110,y), (x+80,y+30)], 2)
        # Sword
        sx, sy = x+80, y+20
        pygame.draw.line(surface, (50,50,50), (sx,sy), (sx,sy+40), 5)
        pts = [(sx-5,sy), (sx+5,sy), (sx+15,sy-120), (sx-15,sy-120)]
        if random.random()<0.2: pts[2] = (sx+20, sy-130)
        pygame.draw.polygon(surface, blade_col, pts)
        pygame.draw.polygon(surface, neon_col, pts, 2)
        
        # Health
        pygame.draw.rect(surface, (50,0,0), (x, y+self.height+10, self.width, 6))
        pygame.draw.rect(surface, neon_col, (x, y+self.height+10, self.width*(self.health/self.max_health), 6))
        self.draw_speech(surface, self.rect.centerx+ox, self.rect.top+oy-50)

class VasilBoss(EnemyBase):
    """HIGH KARMA BOSS: Biblically Accurate Admin"""
    def __init__(self, x, y):
        super().__init__()
        self.width, self.height = 180, 180
        self.x, self.y = x, y
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.health = 3000
        self.max_health = 3000
        self.state = "IDLE"; self.timer = 0; self.angle_cnt = 0

    def update(self, camera_speed, dt=0.016, player_pos=None):
        if not self.is_active: return
        self.update_speech(dt)
        self.rect.y = self.y + math.sin(pygame.time.get_ticks()*0.002)*30
        px, py = 0, 0
        if player_pos: px, py = (player_pos if isinstance(player_pos, tuple) else player_pos.center)
        self.timer += dt

        if self.state == "IDLE":
            if self.timer > 2.0:
                self.timer = 0; r = random.random()
                if r < 0.4: self.state = "SPIRAL"
                elif r < 0.7: self.state = "WALL"
                else: self.state = "SNIPER"
                self.speech_text = "VERİ TEMİZLİĞİ."
                self.speech_duration = 1.0
        
        elif self.state == "SPIRAL":
            self.angle_cnt += 0.5
            if self.timer % 0.1 < 0.02:
                for i in range(4):
                    angle = self.angle_cnt + (i*(math.pi/2))
                    tx, ty = self.rect.centerx+math.cos(angle)*1000, self.rect.centery+math.sin(angle)*1000
                    p = EnemyProjectile(self.rect.centerx, self.rect.centery, tx, ty, speed=8)
                    p.color = (0, 255, 255)
                    self.spawn_queue.append(p)
            if self.timer > 3.0: self.state = "IDLE"; self.timer = 0

        elif self.state == "WALL":
            if self.timer < 0.1:
                for i in range(5):
                    p = EnemyProjectile(self.rect.left-50, self.rect.top+(i*40), -1000, self.rect.top+(i*40), speed=10)
                    p.color = (255, 255, 255)
                    self.spawn_queue.append(p)
            if self.timer > 1.0: self.state = "IDLE"; self.timer = 0

        elif self.state == "SNIPER":
            if (0.5 < self.timer < 0.6) or (0.8 < self.timer < 0.9):
                p = EnemyProjectile(self.rect.centerx, self.rect.centery, px, py, speed=20)
                p.color = (255, 0, 0)
                self.spawn_queue.append(p)
            if self.timer > 1.1: self.state = "IDLE"; self.timer = 0

    def draw(self, surface, camera_offset=(0, 0), theme=None):
        if not self.is_active: return
        ox, oy = camera_offset
        cx, cy = self.rect.centerx+ox, self.rect.centery+oy
        t = pygame.time.get_ticks()*0.002
        
        # Aura
        pygame.draw.circle(surface, (0, 20, 50), (int(cx), int(cy)), int(100+math.sin(t*2)*10))
        # Outer Rings
        for i in range(8):
            angle = t + (i*(math.pi/4))
            px, py = cx+math.cos(angle)*90, cy+math.sin(angle)*90
            pygame.draw.rect(surface, (0,100,255), (px-10, py-10, 20, 20), 2)
            if i%2==0: pygame.draw.line(surface, (0,50,100), (cx,cy), (px,py), 1)
        # Inner Rings
        for i in range(4):
            angle = -t*2 + (i*(math.pi/2))
            px, py = cx+math.cos(angle)*50, cy+math.sin(angle)*50
            pygame.draw.polygon(surface, (0,200,200), [(px,py-10), (px+8,py+8), (px-8,py+8)])
        # Core
        pygame.draw.circle(surface, (255,255,255), (int(cx),int(cy)), 30)
        pygame.draw.circle(surface, (0,100,255), (int(cx),int(cy)), 30, 3)
        pygame.draw.circle(surface, (0,0,0), (int(cx), int(cy-5)), 8)
        
        # Health
        pygame.draw.rect(surface, (0,50,100), (cx-100, cy-120, 200, 10))
        pygame.draw.rect(surface, (0,255,255), (cx-100, cy-120, 200*(self.health/self.max_health), 10))
        self.draw_speech(surface, cx, cy-150)

class NexusBoss(EnemyBase):
    """NEUTRAL BOSS: The Monolith"""
    def __init__(self, x, y):
        super().__init__()
        self.width, self.height = 200, 300
        self.x, self.y = x, y
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.health = 2000
        self.max_health = 2000
        self.state = "IDLE"; self.timer = 0; self.float_offset = 0

    def update(self, camera_speed, dt=0.016, player_pos=None):
        if not self.is_active: return
        self.update_speech(dt)
        self.timer += dt
        self.float_offset = math.sin(pygame.time.get_ticks()*0.001)*20
        self.rect.y = self.y + self.float_offset
        px, py = 0, 0
        if player_pos: px, py = (player_pos if isinstance(player_pos, tuple) else player_pos.center)

        if self.state == "IDLE":
            if self.timer > 2.5:
                self.timer = 0; r = random.random()
                if r < 0.4: self.state = "SCATTER"
                elif r < 0.7: self.state = "HOMING"
                else: self.state = "SWEEP"
                self.speech_text = "HEDEF KİLİTLENDİ."
                self.speech_duration = 1.0

        elif self.state == "SCATTER":
            if self.timer < 0.1:
                for i in range(-2, 3):
                    p = EnemyProjectile(self.rect.centerx, self.rect.centery, px, py+(i*100), speed=12)
                    p.color = (255, 0, 255)
                    self.spawn_queue.append(p)
            if self.timer > 1.0: self.state = "IDLE"; self.timer = 0

        elif self.state == "HOMING":
            if self.timer < 0.1:
                p = EnemyProjectile(self.rect.centerx, self.rect.top+50, px, py, speed=10)
                p.rect.inflate_ip(10, 10); p.color = (255, 50, 50)
                self.spawn_queue.append(p)
            if self.timer > 1.5: self.state = "IDLE"; self.timer = 0

        elif self.state == "SWEEP":
            cnt = int(self.timer / 0.2)
            if cnt < 5 and (self.timer % 0.2 < 0.05):
                yp = self.rect.bottom - (cnt*60)
                p = EnemyProjectile(self.rect.left, yp, -1000, yp, speed=15)
                p.color = (255, 255, 0); p.rect.height = 10; p.rect.width = 40
                self.spawn_queue.append(p)
            if self.timer > 2.0: self.state = "IDLE"; self.timer = 0

    def draw(self, surface, camera_offset=(0, 0), theme=None):
        if not self.is_active: return
        ox, oy = camera_offset
        x, y = self.rect.x + ox, self.rect.y + oy
        neon_col = (255, 0, 100)
        
        # Tower
        pts = [(x+20,y), (x+self.width-20,y), (x+self.width,y+self.height), (x,y+self.height)]
        pygame.draw.polygon(surface, (30, 20, 40), pts)
        pygame.draw.polygon(surface, neon_col, pts, 3)
        # Plates
        for i in range(4):
            pr = pygame.Rect(x+10, y+40+(i*60), self.width-20, 40)
            draw_corrupted_sprite(surface, pr, (50, 40, 60))
        # Eye
        ecx, ecy = x+self.width//2, y+80
        pygame.draw.circle(surface, (10,10,10), (int(ecx),int(ecy)), 50)
        pygame.draw.circle(surface, neon_col, (int(ecx),int(ecy)), 50, 4)
        blink = math.sin(pygame.time.get_ticks()*0.005)*5
        pygame.draw.ellipse(surface, (255,50,50), (ecx-(10+blink), ecy-30, (10+blink)*2, 60))
        # Cables
        for i in range(3):
            cx = x+50+(i*50)
            pygame.draw.line(surface, (20,20,20), (cx,y), (cx,y-500), 5)
            dy = y-(pygame.time.get_ticks()*0.2+(i*50))%500
            pygame.draw.circle(surface, neon_col, (int(cx),int(dy)), 4)
        
        # Health
        pygame.draw.rect(surface, (50,0,0), (x-20, y, 10, self.height))
        fh = self.height * (self.health/self.max_health)
        pygame.draw.rect(surface, neon_col, (x-20, y+self.height-fh, 10, fh))
        self.draw_speech(surface, x+self.width//2, y-40)

def create_starfield(num_stars, screen_width, screen_height):
    stars = []
    for _ in range(num_stars):
        stars.append(Star(screen_width, screen_height))
    return stars

def update_starfield(stars, camera_speed, dt=0.016):
    for star in stars:
        star.update(camera_speed, dt)

def draw_starfield(surface, stars):
    for star in stars:
        star.draw(surface)
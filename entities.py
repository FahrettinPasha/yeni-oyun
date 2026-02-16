import pygame
import random
import math
from settings import *

# --- KONUŞMA SİSTEMİ İÇİN KELİME LİSTESİ ---
ALIEN_SPEECH = [
    "ZGRR!", "0xDEAD", "##!!", "HATA", "KZZT...", 
    "¥€$?", "NO_SIGNAL", "GÖRDÜM!", "∆∆∆", "SİLİN!"
]

# --- RENKLER ---
VOID_PURPLE = (20, 0, 30)
TOXIC_GREEN = (0, 255, 50)
CORRUPT_NEON = (0, 255, 200)

# YENİ PLATFORM TEMA RENKLERİ
COLOR_SYSTEM_RED = (200, 20, 20)    # İtaat / Askeri / Sanayi
COLOR_GLITCH_PURPLE = (150, 0, 255) # İsyan / Anomali / Gutter
COLOR_DIVINE_GOLD = (255, 215, 0)   # Kutsal / Yönetim / Core
COLOR_DIVINE_WHITE = (240, 240, 255)

# --- ÇİZİM YARDIMCI FONKSİYONLARI ---

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
    """Düşmanı harita temasına uygun renklerle çizer."""
    x, y, w, h = rect
    
    # 1. Ana Gövde
    pygame.draw.rect(surface, body_color, rect)
    
    # 2. İç Dolgu
    pygame.draw.rect(surface, (0, 0, 0, 50), (x+2, y+2, w-4, h-4))
    
    # 3. Wireframe / Glitch Çerçevesi
    if random.random() < 0.2:
        offset = random.randint(-3, 3)
        pygame.draw.rect(surface, neon_color, (x+offset, y, w, h), 1)
    else:
        pygame.draw.rect(surface, neon_color, rect, 1)

    # 4. Veri Çizgileri
    if random.random() < 0.1:
        line_y = random.randint(y, y + h)
        pygame.draw.line(surface, neon_color, (x, line_y), (x + w, line_y), 1)

# --- ENEMY BASE ---
class EnemyBase(pygame.sprite.Sprite):
    """Tüm düşmanlar için temel sınıf"""
    def __init__(self):
        super().__init__()
        self.health = 100
        self.is_active = True
        
        # KONUŞMA SİSTEMİ
        self.speech_text = ""
        self.speech_timer = 0
        self.speech_duration = 0
        self.speech_font = pygame.font.Font(None, 24)
        self.spawn_queue = [] 

    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.is_active = False
            return True
        return False

    def update_speech(self, dt):
        if self.speech_duration > 0:
            self.speech_duration -= dt
            if self.speech_duration <= 0:
                self.speech_text = ""
        
        if self.speech_text == "" and random.random() < 0.005:
            self.speech_text = random.choice(ALIEN_SPEECH)
            self.speech_duration = 2.0 

    def draw_speech(self, surface, x, y):
        if self.speech_text:
            text_surf = self.speech_font.render(self.speech_text, True, (255, 50, 50))
            text_rect = text_surf.get_rect(center=(x, y - 30))
            bg_rect = text_rect.inflate(10, 5)
            pygame.draw.rect(surface, (0, 0, 0, 200), bg_rect)
            pygame.draw.rect(surface, (255, 0, 0), bg_rect, 1)
            surface.blit(text_surf, text_rect)

# --- YENİ OPTİMİZE EDİLMİŞ PLATFORM ENGINE ---
class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, theme_index=0):
        super().__init__()
        self.width = width
        self.height = height
        self.theme_index = theme_index
        
        # Fiziksel dikdörtgen (Çarpışma için)
        self.rect = pygame.Rect(x, y, width, height)
        
        # Görsel yüzey (Ekrana çizilecek resim)
        # Yüksekliği artırıyoruz ki altından sarkan detaylar kesilmesin
        self.image = pygame.Surface((width, height + 60), pygame.SRCALPHA)
        
        self.generate_texture()

    def generate_texture(self):
        """Temaya göre platformun görünümünü kodla çizer (PNG kullanmaz)"""
        w, h = self.width, self.height
        
        # Temayı belirle (settings.py'daki indexlere göre kabaca grupluyoruz)
        # THEME 0 (Neon Market), THEME 2 (Gutter) -> PURPLE/GLITCH (Asi Bölgeler)
        # THEME 1 (Core) -> DIVINE (Kutsal)
        # THEME 3 (Industrial) -> SYSTEM RED (Askeri/Sanayi)
        
        mode = "GLITCH"
        if self.theme_index == 1: mode = "DIVINE"
        elif self.theme_index == 3: mode = "SYSTEM"
        elif self.theme_index == 4: mode = "NEUTRAL" # Rest Area

        if mode == "SYSTEM": 
            self._draw_system_style(w, h)
        elif mode == "DIVINE":
            self._draw_divine_style(w, h)
        elif mode == "GLITCH":
            self._draw_glitch_style(w, h)
        else:
            self._draw_neutral_style(w, h)

    def _draw_system_style(self, w, h):
        """SİSTEM (KIRMIZI): Sert, Endüstriyel, Düzenli"""
        # Ana Blok (Koyu Metal)
        pygame.draw.rect(self.image, (20, 10, 10), (0, 0, w, h))
        
        # Çerçeve (Sert Kırmızı)
        pygame.draw.rect(self.image, COLOR_SYSTEM_RED, (0, 0, w, h), 2)
        
        # Uyarı Şeritleri (Warning Stripes)
        for i in range(0, w, 40):
            # p1 = (i, h), p2 = (i + 20, 0) mantığıyla çizgi
            if i + 20 < w:
                pygame.draw.line(self.image, (100, 0, 0), (i, h), (i+20, 0), 10)
        
        # Perçinler
        for ix in [5, w-10]:
            for iy in [5, h-10]:
                pygame.draw.circle(self.image, (150, 50, 50), (ix, iy), 3)

        # Alt Detay (Sert Borular)
        pipes = random.randint(1, 3)
        for _ in range(pipes):
            px = random.randint(10, w-10)
            ph = random.randint(10, 40)
            pygame.draw.rect(self.image, (50, 20, 20), (px, h, 6, ph))
            pygame.draw.circle(self.image, COLOR_SYSTEM_RED, (px+3, h+ph), 3) # Ucunda kırmızı ışık

    def _draw_glitch_style(self, w, h):
        """ASİ (MOR): Bozuk, Titrek, Düzensiz"""
        # Ana Blok (Kirli Siyah/Mor)
        pygame.draw.rect(self.image, (10, 0, 15), (0, 0, w, h))
        
        # Glitch Çerçeve (Rastgele kaymalar)
        points = []
        for x in range(0, w, 10):
            offset = random.randint(-2, 2)
            points.append((x, 0 + offset))
        points.append((w, 0))
        points.append((w, h))
        for x in range(w, 0, -10):
            offset = random.randint(-2, 2)
            points.append((x, h + offset))
        points.append((0, h))
        
        if len(points) > 2:
            pygame.draw.lines(self.image, COLOR_GLITCH_PURPLE, True, points, 2)

        # Matrix / Veri Akışı
        for _ in range(10):
            rx = random.randint(0, w)
            ry = random.randint(0, h)
            rw = random.randint(2, 10)
            pygame.draw.rect(self.image, (50, 0, 100), (rx, ry, rw, 2))

        # Alt Detay (Veri Sızıntısı / Sarkan Kablolar)
        cables = random.randint(2, 5)
        for _ in range(cables):
            cx = random.randint(0, w)
            cl = random.randint(10, 50)
            # Kablo titrek olsun
            start = (cx, h)
            mid = (cx + random.randint(-5, 5), h + cl//2)
            end = (cx + random.randint(-10, 10), h + cl)
            pygame.draw.lines(self.image, (100, 0, 200), False, [start, mid, end], 2)

    def _draw_divine_style(self, w, h):
        """KUTSAL (ALTIN/BEYAZ): Pürüzsüz, Temiz, Yüce"""
        # Ana Blok (Mermer Beyazı)
        pygame.draw.rect(self.image, (240, 240, 245), (0, 0, w, h), border_radius=10)
        
        # Altın İşlemeler
        pygame.draw.rect(self.image, COLOR_DIVINE_GOLD, (0, 0, w, h), 2, border_radius=10)
        
        # İç Desen (Halkalar / Geometri)
        pygame.draw.circle(self.image, (*COLOR_DIVINE_GOLD, 50), (w//2, h//2), h-5, 1)
        pygame.draw.line(self.image, (*COLOR_DIVINE_GOLD, 100), (0, h//2), (w, h//2), 1)

        # Alt Detay (Süzülen Işık/Hale)
        # Sadece temiz bir parlama, kablo veya boru yok.
        s = pygame.Surface((w, 20), pygame.SRCALPHA)
        pygame.draw.ellipse(s, (255, 215, 0, 100), (0, 0, w, 20))
        self.image.blit(s, (0, h))

    def _draw_neutral_style(self, w, h):
        # Basit güvenli bölge
        pygame.draw.rect(self.image, (30, 30, 40), (0, 0, w, h), border_radius=5)
        pygame.draw.rect(self.image, (100, 200, 255), (0, 0, w, h), 1, border_radius=5)

    def update(self, camera_speed, dt=0.016):
        self.rect.x -= camera_speed
        if self.rect.right < 0:
            self.kill()

    def draw(self, surface, theme=None, camera_offset=(0, 0)):
        # Hazır texture'ı bas
        offset_x, offset_y = camera_offset
        surface.blit(self.image, (self.rect.x + offset_x, self.rect.y + offset_y))


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
            # Basit glow efekti
            s = pygame.Surface((glow_radius*2, glow_radius*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (color[0], color[1], color[2], 50), (glow_radius, glow_radius), glow_radius)
            surface.blit(s, (int(self.x) - glow_radius, int(self.y) - glow_radius))

# --- DÜŞMAN SINIFLARI ---

class EnemyProjectile(pygame.sprite.Sprite):
    def __init__(self, x, y, target_x=None, target_y=None, speed=10):
        super().__init__()
        self.rect = pygame.Rect(x, y, 15, 15) 
        
        if target_x is not None and target_y is not None:
            dx = target_x - x
            dy = target_y - y
            angle = math.atan2(dy, dx)
            self.vx = math.cos(angle) * speed
            self.vy = math.sin(angle) * speed
        else:
            self.vx = -speed
            self.vy = 0
            
        self.color = (255, 0, 0) 
        self.timer = 0

    def update(self, camera_speed, dt=0.016, player_pos=None):
        self.rect.x -= camera_speed
        self.rect.x += self.vx
        self.rect.y += self.vy
        
        self.timer += dt
        if int(self.timer * 20) % 2 == 0:
            self.color = (255, 255, 0)
        else:
            self.color = (255, 0, 0)

        if self.rect.right < 0 or self.rect.y > LOGICAL_HEIGHT or self.rect.y < 0:
            self.kill()

    def draw(self, surface, camera_offset=(0, 0), theme=None):
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

    def draw(self, surface, camera_offset=(0, 0), theme=None):
        if not self.is_active: return
        ox, oy = camera_offset
        
        if theme:
            body_col = theme['platform_color']
            neon_col = theme['border_color']
        else:
            body_col = (40, 30, 50)
            neon_col = (0, 255, 100)

        hover = math.sin(self.timer * 5) * 3
        draw_rect = pygame.Rect(self.rect.x + ox, self.rect.y + oy + hover, self.width, self.height)
        
        draw_themed_glitch(surface, draw_rect, body_col, neon_col)
        
        pygame.draw.rect(surface, neon_col, (draw_rect.x + 8, draw_rect.y + 10, 6, 6))
        pygame.draw.rect(surface, neon_col, (draw_rect.right - 14, draw_rect.y + 10, 6, 6))
        
        mouth_w = 20
        if random.random() < 0.05: mouth_w = 24
        pygame.draw.rect(surface, neon_col, (draw_rect.x + 10, draw_rect.y + 25, mouth_w, 4))
        
        self.draw_speech(surface, self.rect.centerx + ox, self.rect.top + oy + hover)

class DroneEnemy(EnemyBase):
    def __init__(self, x, y):
        super().__init__()
        self.width = 40
        self.height = 40
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.timer = random.uniform(0, 100)
        self.shoot_timer = 0
        self.target_x = x
        self.target_y = y
        self.move_timer = 0
        self.recoil_x = 0
        
    def update(self, camera_speed, dt=0.016, player_pos=None):
        if not self.is_active: return
        self.update_speech(dt)
        
        self.rect.x -= camera_speed
        self.target_x -= camera_speed 
        
        self.move_timer -= dt
        if self.move_timer <= 0:
            self.move_timer = random.uniform(1.0, 2.5)
            self.target_x = self.rect.x + random.uniform(-100, 100)
            self.target_y = max(50, min(LOGICAL_HEIGHT - 150, self.rect.y + random.uniform(-80, 80)))

        self.rect.x += (self.target_x - self.rect.x) * 2 * dt
        self.rect.y += (self.target_y - self.rect.y) * 2 * dt
        self.recoil_x *= 0.9
        
        self.shoot_timer += dt
        if self.shoot_timer > 0.8: 
            self.shoot_timer = 0
            self.recoil_x = 10 
            
            px, py = None, None
            if player_pos:
                if hasattr(player_pos, 'center'):
                    px, py = player_pos.center
                elif isinstance(player_pos, (tuple, list)):
                    px, py = player_pos[0], player_pos[1]
            
            if px is not None and py is not None:
                projectile = EnemyProjectile(self.rect.centerx, self.rect.centery, px, py, speed=15)
                for group in self.groups():
                    group.add(projectile)
            else:
                projectile = EnemyProjectile(self.rect.centerx, self.rect.centery, target_x=self.rect.x - 100, target_y=self.rect.y, speed=15)
                for group in self.groups():
                    group.add(projectile)
        
        if self.rect.right < 0: self.kill()

    def draw(self, surface, camera_offset=(0, 0), theme=None):
        if not self.is_active: return
        ox, oy = camera_offset
        
        if theme:
            body_col = theme['bg_color']
            neon_col = theme['border_color']
        else:
            body_col = (20, 20, 30)
            neon_col = (0, 255, 200)

        cx = self.rect.centerx + ox + self.recoil_x
        cy = self.rect.centery + oy
        cy += math.sin(pygame.time.get_ticks() * 0.005) * 5

        points = [(cx, cy - 20), (cx + 20, cy), (cx, cy + 20), (cx - 20, cy)]
        pygame.draw.polygon(surface, body_col, points)
        
        border_c = neon_col if random.random() > 0.1 else (255, 255, 255)
        pygame.draw.polygon(surface, border_c, points, 2)
        
        charge = min(1, self.shoot_timer / 0.8)
        eye_color = (255, int(255 * charge), 0)
        pygame.draw.circle(surface, eye_color, (int(cx), int(cy)), int(4 + charge * 6))
        
        angle = pygame.time.get_ticks() * 0.01
        orbit_x = cx + math.cos(angle) * 35
        orbit_y = cy + math.sin(angle) * 10
        pygame.draw.rect(surface, neon_col, (orbit_x, orbit_y, 4, 4))

        self.draw_speech(surface, cx, self.rect.top + oy - 20)

class TankEnemy(EnemyBase):
    def __init__(self, platform):
        super().__init__()
        self.platform = platform
        self.width = 160
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
        self.update_speech(dt)

        self.rect.x -= camera_speed
        self.move_timer += dt
        
        self.vy += 0.8 
        self.rect.y += self.vy
        
        if self.rect.bottom >= self.platform.rect.top and self.vy > 0:
            if self.rect.bottom - self.vy <= self.platform.rect.top + 10: 
                self.rect.bottom = self.platform.rect.top
                self.vy = 0
                self.on_ground = True
        else:
            self.on_ground = False

        if self.on_ground:
            self.rect.x += self.vx
            self.move_timer += dt

            if self.rect.right > self.platform.rect.right:
                self.rect.right = self.platform.rect.right
                self.vx *= -1
            elif self.rect.left < self.platform.rect.left:
                self.rect.left = self.platform.rect.left
                self.vx *= -1

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
        
        if theme:
            body_col = theme['platform_color']
            neon_col = theme['border_color']
        else:
            body_col = (50, 50, 50)
            neon_col = (255, 100, 0)

        draw_rect = pygame.Rect(self.rect.x + ox, self.rect.y + oy, self.width, self.height)
        
        track_h = 25
        pygame.draw.rect(surface, (15, 15, 15), (draw_rect.x, draw_rect.bottom - track_h, self.width, track_h))
        
        body_rect = pygame.Rect(draw_rect.x + 5, draw_rect.y + 40, self.width - 10, self.height - 65)
        draw_themed_glitch(surface, body_rect, body_col, neon_col)
        
        turret_rect = pygame.Rect(draw_rect.centerx - 30, body_rect.top - 30, 60, 40)
        pygame.draw.rect(surface, body_col, turret_rect)
        pygame.draw.rect(surface, neon_col, turret_rect, 2)
        
        end_x = draw_rect.centerx + math.cos(self.barrel_angle) * 70
        end_y = (body_rect.top + 10) + math.sin(self.barrel_angle) * 70
        
        pygame.draw.line(surface, (80, 80, 80), (draw_rect.centerx, body_rect.top + 10), (end_x, end_y), 12)
        charge = min(1, self.shoot_timer / 1.5)
        if charge > 0.5:
             pygame.draw.line(surface, neon_col, (draw_rect.centerx, body_rect.top + 10), (end_x, end_y), 4)

        self.draw_speech(surface, self.rect.centerx + ox, self.rect.top + oy - 20)

# --- NPC SINIFI ---
class NPC:
    def __init__(self, x, y, name, color, personality_type="philosopher", prompt=None):
        self.x = x
        self.y = y
        self.name = name
        self.color = color
        self.personality_type = personality_type
        self.prompt = prompt
        self.ai_active = False 
        
        self.width = 40
        self.height = 60
        self.rect = pygame.Rect(x - 20, y - 60, 40, 60)
        
        self.talk_radius = 200
        self.can_talk = False
        self.talking = False
        
        # Animasyon Değişkenleri
        self.float_timer = random.uniform(0, 100)
        self.glitch_timer = 0
        self.eye_offset_x = 0
        self.eye_offset_y = 0

    def update(self, player_x, player_y, dt=0.016):
        # 1. Nefes Alma / Süzülme Hareketi
        self.float_timer += dt * 2
        
        # 2. Oyuncuya Bakma (Eye Tracking)
        dx = player_x - self.x
        dy = (player_y - 40) - (self.y - 40) # Kafa hizası
        dist = math.sqrt(dx*dx + dy*dy)
        if dist > 0:
            self.eye_offset_x = (dx / dist) * 3 # Gözbebeği en fazla 3 piksel kaysın
            self.eye_offset_y = (dy / dist) * 2
            
        # 3. Glitch Efekti (Rastgele titreme)
        if random.random() < 0.01:
            self.glitch_timer = 5 # 5 kare boyunca bozul
        if self.glitch_timer > 0:
            self.glitch_timer -= 1

        # Etkileşim Mesafesi
        self.can_talk = dist < self.talk_radius

    def draw(self, surface, camera_offset=(0,0)):
        ox, oy = camera_offset
        
        # Glitch varsa konumu hafifçe saptır
        gx = random.randint(-3, 3) if self.glitch_timer > 0 else 0
        gy = random.randint(-3, 3) if self.glitch_timer > 0 else 0
        
        draw_x = self.x + ox + gx
        draw_y = self.y + oy + math.sin(self.float_timer) * 5 + gy # Süzülme eklendi
        
        # --- GÖVDE ÇİZİMİ (Pelerinli Figür / Robot) ---
        
        # 1. Aura (Hale)
        if self.can_talk:
            pygame.draw.circle(surface, (*self.color, 50), (int(draw_x), int(draw_y - 30)), 40, 2)

        # 2. Gövde (Üçgenimsi Pelerin)
        points = [
            (draw_x, draw_y - 60),      # Baş
            (draw_x - 20, draw_y),      # Sol Alt
            (draw_x + 20, draw_y)       # Sağ Alt
        ]
        pygame.draw.polygon(surface, (20, 20, 30), points)
        pygame.draw.polygon(surface, self.color, points, 2)
        
        # 3. Kafa / Göz
        head_pos = (int(draw_x), int(draw_y - 50))
        pygame.draw.circle(surface, (0, 0, 0), head_pos, 12) # Kafa arkaplanı
        pygame.draw.circle(surface, self.color, head_pos, 12, 1) # Kafa çerçevesi
        
        # Göz Bebeği (Oyuncuyu takip eder)
        eye_pos = (int(draw_x + self.eye_offset_x), int(draw_y - 50 + self.eye_offset_y))
        
        # NPC Tipine göre göz şekli
        if self.personality_type == "warrior":
            # Kırmızı, agresif tek göz
            pygame.draw.circle(surface, (255, 0, 0), eye_pos, 4)
        elif self.personality_type == "philosopher":
            # Mavi, sakin göz
            pygame.draw.rect(surface, (0, 255, 255), (eye_pos[0]-4, eye_pos[1]-2, 8, 4))
        else:
            # Standart beyaz göz
            pygame.draw.circle(surface, (255, 255, 255), eye_pos, 3)

        # 4. İsim ve Durum
        if self.can_talk:
            # Konuşma balonu ikonu
            bubble_rect = pygame.Rect(draw_x + 15, draw_y - 80, 20, 15)
            pygame.draw.rect(surface, (255, 255, 255), bubble_rect, border_radius=5)
            pygame.draw.polygon(surface, (255, 255, 255), [(draw_x + 15, draw_y - 65), (draw_x + 25, draw_y - 65), (draw_x + 15, draw_y - 60)])
            
            # Tuş bilgisi
            font = pygame.font.Font(None, 20)
            text = font.render("E", True, (0, 0, 0))
            surface.blit(text, (bubble_rect.x + 6, bubble_rect.y + 1))

    def start_conversation(self):
        self.talking = True
        if self.prompt: return self.prompt
        return "..."
    
    def send_message(self, player_message, game_context=None):
        return "Sistem verisi analiz ediliyor..."
            
    def end_conversation(self):
        self.talking = False
        return ""

# --- BOSS SINIFLARI ---

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
        
        for i in range(5):
            sx, sy = x+20, y+20
            ex = sx-60-(i*10)+math.sin(pygame.time.get_ticks()*0.01+i)*20
            ey = sy-20+(i*15)
            pygame.draw.line(surface, (200, 50, 50), (sx, sy), (ex, ey), 3)
        pygame.draw.polygon(surface, armor_col, [(x,y), (x+100,y), (x+80,y+80), (x+20,y+80)])
        draw_corrupted_sprite(surface, pygame.Rect(x+20, y+10, 60, 60), armor_col)
        pygame.draw.polygon(surface, neon_col, [(x-10,y), (x+20,y), (x+20,y+30)], 2)
        pygame.draw.polygon(surface, neon_col, [(x+80,y), (x+110,y), (x+80,y+30)], 2)
        sx, sy = x+80, y+20
        pygame.draw.line(surface, (50,50,50), (sx,sy), (sx,sy+40), 5)
        pts = [(sx-5,sy), (sx+5,sy), (sx+15,sy-120), (sx-15,sy-120)]
        if random.random()<0.2: pts[2] = (sx+20, sy-130)
        pygame.draw.polygon(surface, blade_col, pts)
        pygame.draw.polygon(surface, neon_col, pts, 2)
        
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
        
        pygame.draw.circle(surface, (0, 20, 50), (int(cx), int(cy)), int(100+math.sin(t*2)*10))
        for i in range(8):
            angle = t + (i*(math.pi/4))
            px, py = cx+math.cos(angle)*90, cy+math.sin(angle)*90
            pygame.draw.rect(surface, (0,100,255), (px-10, py-10, 20, 20), 2)
            if i%2==0: pygame.draw.line(surface, (0,50,100), (cx,cy), (px,py), 1)
        for i in range(4):
            angle = -t*2 + (i*(math.pi/2))
            px, py = cx+math.cos(angle)*50, cy+math.sin(angle)*50
            pygame.draw.polygon(surface, (0,200,200), [(px,py-10), (px+8,py+8), (px-8,py+8)])
        pygame.draw.circle(surface, (255,255,255), (int(cx),int(cy)), 30)
        pygame.draw.circle(surface, (0,100,255), (int(cx),int(cy)), 30, 3)
        pygame.draw.circle(surface, (0,0,0), (int(cx), int(cy-5)), 8)
        
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
        
        pts = [(x+20,y), (x+self.width-20,y), (x+self.width,y+self.height), (x,y+self.height)]
        pygame.draw.polygon(surface, (30, 20, 40), pts)
        pygame.draw.polygon(surface, neon_col, pts, 3)
        for i in range(4):
            pr = pygame.Rect(x+10, y+40+(i*60), self.width-20, 40)
            draw_corrupted_sprite(surface, pr, (50, 40, 60))
        ecx, ecy = x+self.width//2, y+80
        pygame.draw.circle(surface, (10,10,10), (int(ecx),int(ecy)), 50)
        pygame.draw.circle(surface, neon_col, (int(ecx),int(ecy)), 50, 4)
        blink = math.sin(pygame.time.get_ticks()*0.005)*5
        pygame.draw.ellipse(surface, (255,50,50), (ecx-(10+blink), ecy-30, (10+blink)*2, 60))
        for i in range(3):
            cx = x+50+(i*50)
            pygame.draw.line(surface, (20,20,20), (cx,y), (cx,y-500), 5)
            dy = y-(pygame.time.get_ticks()*0.2+(i*50))%500
            pygame.draw.circle(surface, neon_col, (int(cx),int(dy)), 4)
        
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

# --- YENİ PARALLAX ŞEHİR ARKA PLANI ---
class CityBackground:
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.layers = []
        self.create_layers()

    def create_layers(self):
        # Katman Ayarları
        layer_configs = [
            # Katman 1: En arkada, devasa silüetler (Gökdelenler)
            {'speed': 0.05, 'color': (5, 5, 8), 'count': 10, 'w_range': (150, 400), 'h_range': (400, 900), 'windows': False, 'neon': False},
            # Katman 2: Orta mesafe, detaylı binalar
            {'speed': 0.2, 'color': (15, 15, 25), 'count': 20, 'w_range': (100, 250), 'h_range': (200, 600), 'windows': True, 'neon': False},
            # Katman 3: Yakın, hızlı, neonlu ve detaylı
            {'speed': 0.6, 'color': (25, 25, 40), 'count': 30, 'w_range': (60, 180), 'h_range': (100, 400), 'windows': True, 'neon': True}
        ]

        for config in layer_configs:
            # Sonsuz döngü için ekranın biraz fazlasını oluştur
            surface_width = self.width + 400
            layer_surface = pygame.Surface((surface_width, self.height)).convert_alpha()
            layer_surface.fill((0,0,0,0))

            current_x = 0
            while current_x < surface_width:
                w = random.randint(*config['w_range'])
                h = random.randint(*config['h_range'])
                
                rect = pygame.Rect(current_x, self.height - h, w, h)
                pygame.draw.rect(layer_surface, config['color'], rect)
                
                # Pencereler
                if config['windows']:
                    win_cols = random.randint(2, 5)
                    win_rows = random.randint(5, 15)
                    win_w = max(1, w // (win_cols + 2))
                    win_h = max(1, h // (win_rows + 2))
                    win_gap_x = max(1, (w - (win_cols * win_w)) // (win_cols + 1))
                    win_gap_y = max(1, (h - (win_rows * win_h)) // (win_rows + 1))
                    
                    win_color = random.choice([(50, 50, 80), (80, 80, 100), (100, 100, 50)])
                    lit_chance = 0.3
                    
                    for row in range(win_rows):
                        for col in range(win_cols):
                            if random.random() < lit_chance:
                                wx = current_x + win_gap_x + (col * (win_w + win_gap_x))
                                wy = (self.height - h) + win_gap_y + (row * (win_h + win_gap_y))
                                pygame.draw.rect(layer_surface, win_color, (wx, wy, win_w, win_h))

                # Neonlar
                if config['neon'] and random.random() < 0.3:
                    neon_color = random.choice([(0, 255, 255), (255, 0, 100), (50, 255, 50)])
                    if random.random() < 0.5:
                        pygame.draw.rect(layer_surface, neon_color, (current_x + 10, self.height - h + 20, 5, h - 40))
                    else:
                        sign_h = 40
                        safe_max_y = h - 60
                        if safe_max_y > 20:
                            sign_y_offset = random.randint(20, safe_max_y)
                            sign_y = self.height - h + sign_y_offset
                            
                            pygame.draw.rect(layer_surface, (0, 0, 0), (current_x - 10, sign_y, w + 20, sign_h))
                            pygame.draw.rect(layer_surface, neon_color, (current_x - 10, sign_y, w + 20, sign_h), 2)
                            for i in range(3):
                                ly = sign_y + 10 + (i * 8)
                                pygame.draw.line(layer_surface, neon_color, (current_x, ly), (current_x + w - 10, ly), 2)

                # Antenler
                if random.random() < 0.4:
                    ant_h = random.randint(20, 80)
                    pygame.draw.line(layer_surface, (50, 50, 50), (current_x + w//2, self.height - h), (current_x + w//2, self.height - h - ant_h), 2)
                    if random.random() < 0.5:
                        pygame.draw.circle(layer_surface, (200, 0, 0), (current_x + w//2, self.height - h - ant_h), 2)

                current_x += w + random.randint(-5, 5)

            # Twin Surface Tekniği (x1, x2)
            self.layers.append({
                'surface': layer_surface,
                'speed': config['speed'],
                'x1': 0,
                'x2': surface_width,
                'width': surface_width
            })
            
        # Uçan Arabalar
        self.cars = []
        for _ in range(10):
            self.cars.append({
                'x': random.randint(0, self.width),
                'y': random.randint(100, 600),
                'speed': random.uniform(2, 5),
                'color': random.choice([(255, 200, 200), (200, 200, 255), (255, 255, 200)])
            })

    def update(self, camera_speed):
        # Katmanları kaydır (Sonsuz Döngü)
        for layer in self.layers:
            move = layer['speed'] * (camera_speed * 0.8)
            layer['x1'] -= move
            layer['x2'] -= move
            
            if layer['x1'] <= -layer['width']:
                layer['x1'] = layer['x2'] + layer['width']
            
            if layer['x2'] <= -layer['width']:
                layer['x2'] = layer['x1'] + layer['width']
                
        # Arabaları hareket ettir
        for car in self.cars:
            car['x'] -= car['speed'] + (camera_speed * 0.1)
            if car['x'] < -50:
                car['x'] = self.width + random.randint(50, 200)
                car['y'] = random.randint(100, 600)

    def draw(self, surface):
        # Katmanları çiz
        for layer in self.layers:
            if layer['x1'] < self.width:
                surface.blit(layer['surface'], (int(layer['x1']), 0))
            if layer['x2'] < self.width:
                surface.blit(layer['surface'], (int(layer['x2']), 0))
                
        # Arabaları çiz
        for car in self.cars:
            pygame.draw.circle(surface, car['color'], (int(car['x']), int(car['y'])), 2)
            pygame.draw.line(surface, (*car['color'], 100), 
                             (int(car['x']), int(car['y'])), (int(car['x'] + 20), int(car['y'])), 1)
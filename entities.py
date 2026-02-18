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

class GutterBackground:
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.scroll_x = 0        # Far background scroll
        self.scroll_mid = 0      # Mid layer scroll (parallax)
        self.scroll_fg = 0       # Foreground debris scroll
        self.frame_count = 0

        # --- COLOR PALETTE: DIGITAL DECAY ---
        self.VOID_BLACK    = (2, 2, 5)           # The abyss
        self.ROTTING_GREEN = (8, 28, 12)          # Mold-circuit green
        self.TOXIC_ACID    = (20, 80, 10)         # Corroded acid green
        self.RUST_DATA     = (50, 22, 14)         # Oxidized data-iron
        self.GHOST_GREY    = (22, 22, 28)         # Ghost memory
        self.CRITICAL_RED  = (90, 5, 5)           # Fatal error
        self.DEAD_BLUE     = (5, 10, 35)          # Cold dead process
        self.SLUDGE        = (15, 18, 10)         # Ground sludge
        self.DRIP_GREEN    = (0, 160, 40)         # Acid drip color
        self.EMBER_ORANGE  = (120, 40, 5)         # Dying ember

        # Fonts
        try:
            self.font       = pygame.font.SysFont("consolas", 14)
            self.font_sm    = pygame.font.SysFont("consolas", 10)
            self.big_font   = pygame.font.SysFont("consolas", 96)
            self.tomb_font  = pygame.font.SysFont("consolas", 11)
        except:
            self.font       = pygame.font.Font(None, 14)
            self.font_sm    = pygame.font.Font(None, 10)
            self.big_font   = pygame.font.Font(None, 96)
            self.tomb_font  = pygame.font.Font(None, 11)

        # Pre-baked surfaces (generated once, drawn every frame)
        self.far_bg      = self._generate_far_background()
        self.junk_piles  = self._generate_junk_piles()
        self.mid_layer   = self._generate_mid_layer()
        self.fg_debris   = self._generate_fg_debris()

        # Pre-baked scanline overlay
        self.scanlines   = self._generate_scanlines()

        # Pre-baked vignette
        self.vignette    = self._generate_vignette()

        # Animated particles: data ash (rising)
        self.ashes = [self._create_ash() for _ in range(80)]

        # Animated particles: toxic drips (falling)
        self.drips = [self._create_drip() for _ in range(30)]

        # Memory tombstones (static objects on mid layer — error logs, dead processes)
        self.tombstones = self._generate_tombstones()

        # Ambient ghost text (VOID/NULL/EOF floating in far BG)
        self.ghost_texts = []
        ghost_labels = ["NULL", "EOF", "VOID", "0x00", "DEAD", "∅", "SEGFAULT",
                        "0xDEAD", "ERR", "LOST", "CORRUPT", "NaN"]
        for _ in range(8):
            self.ghost_texts.append({
                'x':     random.randint(0, self.width),
                'y':     random.randint(20, self.height - 20),
                'text':  random.choice(ghost_labels),
                'alpha': random.randint(6, 22),       # Very faint
                'flicker_speed': random.uniform(0.01, 0.04),
                'flicker_offset': random.uniform(0, math.pi * 2),
            })

        # Glitch strip state — rare, ominous, brief
        self._glitch_strip_timer = random.randint(180, 400)  # Start with a long silence
        self._glitch_strips      = []   # List of active strip effects
        self._glitch_event_alpha = 0    # Full-screen dark flash on glitch trigger

        # Toxic fog pulse
        self.fog_alpha = 0
        self.fog_surface = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    # ------------------------------------------------------------------ #
    #  SURFACE GENERATORS (called once at init)
    # ------------------------------------------------------------------ #

    def _generate_far_background(self):
        """Deep background: ruined cityscape silhouette, hex data rain, dead circuit grid."""
        w = self.width + 400
        surf = pygame.Surface((w, self.height), pygame.SRCALPHA)

        # ── Vertical gradient: pure void at top → sickly dark sludge green at bottom ──
        for y in range(self.height):
            t = y / self.height
            r = int(2  + t * 8)
            g = int(2  + t * 16)
            b = int(5  + t * 6)
            pygame.draw.line(surf, (r, g, b), (0, y), (w, y))

        # ── Distant ruined city skyline — jagged silhouette of dead skyscrapers ──
        sky_surf = pygame.Surface((w, self.height), pygame.SRCALPHA)
        bx = 0
        while bx < w:
            bw  = random.randint(18, 80)
            bh  = random.randint(60, 320)
            by  = self.height - bh
            col = random.choice([(6, 8, 6), (8, 6, 5), (5, 6, 10), (7, 7, 7)])
            # Main building body
            pygame.draw.rect(sky_surf, col, (bx, by, bw, bh))
            # Antenna / spire on top
            if random.random() < 0.5:
                spire_h = random.randint(15, 60)
                spire_x = bx + bw // 2 + random.randint(-5, 5)
                pygame.draw.line(sky_surf, (col[0]+3, col[1]+3, col[2]+3),
                                 (spire_x, by), (spire_x, by - spire_h), 1)
                # Dead beacon (occasional dim blink-baked-in dot)
                if random.random() < 0.3:
                    pygame.draw.circle(sky_surf, (60, 0, 0), (spire_x, by - spire_h), 2)
            # Window grid (mostly dark, occasional faint light)
            win_w, win_h = 4, 5
            for wx in range(bx + 3, bx + bw - 3, win_w + 2):
                for wy in range(by + 4, by + bh - 4, win_h + 3):
                    if random.random() < 0.08:   # Most windows are dead
                        wc = random.choice([(0, 40, 8), (40, 10, 0), (8, 8, 50)])
                        pygame.draw.rect(sky_surf, wc, (wx, wy, win_w, win_h))
                    else:
                        pygame.draw.rect(sky_surf, (3, 3, 3), (wx, wy, win_w, win_h))
            bx += bw + random.randint(2, 20)
        sky_surf.set_alpha(60)
        surf.blit(sky_surf, (0, 0))

        # ── Dead circuit board grid — faint PCB traces across the whole BG ──
        grid_surf = pygame.Surface((w, self.height), pygame.SRCALPHA)
        # Horizontal traces
        for _ in range(40):
            y1  = random.randint(0, self.height)
            x1  = random.randint(0, w)
            seg = random.randint(30, 200)
            col = random.choice([(0, 35, 8, 20), (30, 10, 5, 15), (5, 5, 35, 18)])
            pygame.draw.line(grid_surf, col, (x1, y1), (x1 + seg, y1), 1)
            # 90-degree turn
            turn_len = random.randint(10, 80)
            dir_y    = random.choice([-1, 1])
            pygame.draw.line(grid_surf, col,
                             (x1 + seg, y1),
                             (x1 + seg, y1 + dir_y * turn_len), 1)
            # Via (solder dot)
            pygame.draw.circle(grid_surf, col[:3], (x1 + seg, y1), 2)
        # Vertical traces
        for _ in range(30):
            x1  = random.randint(0, w)
            y1  = random.randint(0, self.height)
            seg = random.randint(20, 150)
            col = random.choice([(0, 28, 6, 14), (22, 8, 4, 12)])
            pygame.draw.line(grid_surf, col, (x1, y1), (x1, y1 + seg), 1)
        surf.blit(grid_surf, (0, 0))

        # ── Hex / binary rain columns — static snapshot baked into BG ──
        # These give the "data torrent" feel without the Matrix cliché
        hex_chars = list("0123456789ABCDEF∅§¬░▒")
        try:
            hf = pygame.font.SysFont("consolas", 11)
        except:
            hf = pygame.font.Font(None, 11)
        for col_x in range(0, w, random.randint(18, 40)):
            col_len  = random.randint(4, 22)
            start_y  = random.randint(-100, self.height - col_len * 13)
            col_alpha = random.randint(12, 45)
            bright_idx = random.randint(0, col_len - 1)  # One "bright" char per column
            for i in range(col_len):
                ch  = random.choice(hex_chars)
                cy  = start_y + i * 13
                if cy < 0 or cy > self.height:
                    continue
                # Brightest at the "head" of the column
                a = col_alpha + (25 if i == bright_idx else 0)
                c = (0, min(255, 30 + a * 2), 8)
                t = hf.render(ch, True, c)
                t.set_alpha(a)
                surf.blit(t, (col_x, cy))

        # ── Horizontal "dead bandwidth" streaks ──
        for _ in range(50):
            sx     = random.randint(0, w)
            sy     = random.randint(0, self.height)
            sw     = random.randint(30, 280)
            sh_px  = random.randint(1, 2)
            alpha  = random.randint(8, 35)
            c      = random.choice([(0, 50, 8), (28, 8, 4), (4, 4, 28)])
            streak = pygame.Surface((sw, sh_px), pygame.SRCALPHA)
            streak.fill((*c, alpha))
            surf.blit(streak, (sx, sy))

        # ── Large ghostly ERROR / MEMORY ADDRESS overlays ──
        addr_labels = [
            "0xDEAD_BEEF", "0xCAFE_BABE", "0x0000_0000",
            "STACK OVERFLOW", "ACCESS DENIED", "MEMORY FAULT",
            "KERNEL PANIC", "NULL PTR", "UNRESOLVED SYMBOL",
        ]
        try:
            af = pygame.font.SysFont("consolas", random.randint(28, 72))
        except:
            af = pygame.font.Font(None, 48)
        for _ in range(6):
            lbl   = random.choice(addr_labels)
            ax    = random.randint(0, w - 300)
            ay    = random.randint(0, self.height - 80)
            angle = random.choice([0, 90, -90, 45, -45])
            col   = random.choice([(0, 40, 8), (40, 5, 5), (5, 5, 40)])
            t     = af.render(lbl, True, col)
            t     = pygame.transform.rotate(t, angle)
            t.set_alpha(random.randint(8, 22))
            surf.blit(t, (ax, ay))

        return surf

    def _generate_junk_piles(self):
        """Background junk mountains — layered corrupted data heaps."""
        surface_w = self.width + 400
        surf = pygame.Surface((surface_w, self.height), pygame.SRCALPHA)

        current_x = 0
        while current_x < surface_w:
            w = random.randint(80, 280)
            h = random.randint(80, 380)

            # Base polygon (irregular heap silhouette)
            jagged_top = []
            steps = random.randint(4, 9)
            for i in range(steps + 1):
                fx = current_x + (w * i / steps)
                fy = (self.height - h) + random.randint(-40, 40)
                jagged_top.append((fx, fy))

            points = (
                [(current_x, self.height)]
                + jagged_top
                + [(current_x + w, self.height)]
            )

            # Pick a dark, decayed color
            base_color = random.choice([
                self.ROTTING_GREEN,
                self.RUST_DATA,
                self.GHOST_GREY,
                self.DEAD_BLUE,
                self.SLUDGE,
            ])
            pygame.draw.polygon(surf, base_color, points)

            # Interior "pixel debris" — small rectangles of dead data
            for _ in range(random.randint(8, 20)):
                rx = random.randint(current_x, current_x + w - 5)
                ry = random.randint(self.height - h, self.height - 4)
                rw = random.randint(2, 18)
                rh = random.randint(2, 10)
                shade = (
                    max(0, base_color[0] + random.randint(-8, 20)),
                    max(0, base_color[1] + random.randint(-8, 20)),
                    max(0, base_color[2] + random.randint(-8, 20)),
                )
                pygame.draw.rect(surf, shade, (rx, ry, rw, rh))

            # Exposed "wire" lines sticking out of the heap top
            for _ in range(random.randint(1, 4)):
                wx = current_x + random.randint(5, w - 5)
                wy_base = self.height - h + random.randint(-30, 10)
                wy_tip  = wy_base - random.randint(10, 50)
                wire_color = random.choice([(0, 120, 20), (100, 20, 5), (20, 20, 60)])
                pygame.draw.line(surf, wire_color, (wx, wy_base), (wx + random.randint(-8, 8), wy_tip), 1)

            # Horizontal "error bar" stripes inside the heap
            if random.random() < 0.4:
                bar_y = random.randint(self.height - h + 10, self.height - 10)
                bar_color = random.choice([(60, 5, 5), (5, 50, 5), (5, 5, 50)])
                pygame.draw.line(surf, bar_color, (current_x + 5, bar_y), (current_x + w - 5, bar_y), 2)

            current_x += w - random.randint(0, 60)

        return surf

    def _generate_mid_layer(self):
        """Mid-distance layer: server ruins, broken pipes, dead terminals, collapsed walls."""
        surface_w = self.width + 400
        surf = pygame.Surface((surface_w, self.height), pygame.SRCALPHA)

        # ── Broken horizontal pipe network running across the mid ground ──
        pipe_y_levels = [
            self.height - random.randint(120, 180),
            self.height - random.randint(200, 280),
        ]
        for pipe_y in pipe_y_levels:
            px = 0
            while px < surface_w:
                seg_len = random.randint(60, 250)
                pipe_col = random.choice([(28, 18, 12), (14, 22, 12), (12, 14, 24)])
                pipe_h   = random.randint(6, 14)
                # Pipe body
                pygame.draw.rect(surf, pipe_col,
                                 (px, pipe_y - pipe_h // 2, seg_len, pipe_h))
                # Highlight top edge
                pygame.draw.line(surf, (pipe_col[0]+10, pipe_col[1]+10, pipe_col[2]+10),
                                 (px, pipe_y - pipe_h // 2),
                                 (px + seg_len, pipe_y - pipe_h // 2), 1)
                # Joint flanges at segment ends
                flange_col = (pipe_col[0]+15, pipe_col[1]+15, pipe_col[2]+15)
                pygame.draw.rect(surf, flange_col,
                                 (px + seg_len - 5, pipe_y - pipe_h, 7, pipe_h * 2))
                # Occasional vertical drop pipe
                if random.random() < 0.35:
                    drop_x = px + random.randint(20, max(21, seg_len - 20))
                    drop_h = random.randint(20, 80)
                    pygame.draw.rect(surf, pipe_col,
                                     (drop_x - 3, pipe_y, 6, drop_h))
                    # Drip stain below
                    for ds in range(0, 20, 4):
                        stain_a = max(0, 40 - ds * 4)
                        stain_s = pygame.Surface((4, 2), pygame.SRCALPHA)
                        stain_s.fill((0, 100, 10, stain_a))
                        surf.blit(stain_s, (drop_x - 2, pipe_y + drop_h + ds))
                px += seg_len + random.randint(0, 30)

        # ── Server racks / dead machinery at intervals ──
        x = 0
        while x < surface_w:
            gap = random.randint(150, 420)
            x  += gap
            structure_type = random.choice(['rack', 'wall_slab', 'terminal', 'pillar'])

            if structure_type == 'rack':
                rack_w = random.randint(28, 65)
                rack_h = random.randint(100, 260)
                rack_y = self.height - rack_h - random.randint(0, 30)
                rack_col = random.choice([(16, 16, 18), (18, 9, 7), (9, 16, 9)])
                # Body
                pygame.draw.rect(surf, rack_col, (x, rack_y, rack_w, rack_h))
                # Trim lines
                pygame.draw.rect(surf, (rack_col[0]+20, rack_col[1]+20, rack_col[2]+22),
                                 (x, rack_y, rack_w, rack_h), 1)
                pygame.draw.line(surf, (rack_col[0]+12, rack_col[1]+12, rack_col[2]+14),
                                 (x+2, rack_y+2), (x+rack_w-2, rack_y+2), 1)
                # Drive bays
                slot_h = 7
                for sy in range(rack_y + 6, rack_y + rack_h - 6, slot_h + 4):
                    s_col = random.choice([(4,4,4),(6,14,4),(14,4,4),(4,4,14)])
                    pygame.draw.rect(surf, s_col, (x+3, sy, rack_w-6, slot_h))
                    # Slot label (tiny)
                    if random.random() < 0.3:
                        label_col = random.choice([(0,50,8),(50,8,0),(8,8,50)])
                        pygame.draw.rect(surf, label_col, (x+3, sy+1, random.randint(4,10), 2))
                    # LED indicator
                    led = (0, 0, 0)
                    if random.random() < 0.12:
                        led = random.choice([(0,70,8),(70,0,0),(4,4,70)])
                    pygame.draw.rect(surf, led, (x+rack_w-6, sy+2, 3, 3))
                # Hanging cables
                for _ in range(random.randint(2, 5)):
                    cx   = x + random.randint(4, rack_w - 4)
                    cl   = random.randint(20, 70)
                    cc   = random.choice([(25,25,25),(0,50,8),(50,8,4),(4,4,50)])
                    for seg in range(0, cl, 5):
                        sway = int(math.sin(seg * 0.45 + cx * 0.1) * 4)
                        pygame.draw.line(surf, cc,
                                         (cx + sway, rack_y + rack_h + seg),
                                         (cx + sway, rack_y + rack_h + seg + 4), 1)
                    # Spark/fray at the end
                    if random.random() < 0.25:
                        for _ in range(3):
                            sx2 = cx + random.randint(-4, 4)
                            pygame.draw.line(surf, (80, 60, 0),
                                             (cx, rack_y + rack_h + cl),
                                             (sx2, rack_y + rack_h + cl + random.randint(2, 6)), 1)

            elif structure_type == 'wall_slab':
                sw2  = random.randint(40, 130)
                sh2  = random.randint(80, 200)
                sy2  = self.height - sh2 - random.randint(0, 20)
                scol = random.choice([(18, 14, 10), (10, 16, 10), (10, 10, 20)])
                # Crumbling slab body
                pts = [
                    (x, self.height),
                    (x + random.randint(-4, 4), sy2 + random.randint(-8, 8)),
                    (x + sw2 // 3 + random.randint(-6, 6), sy2 + random.randint(-15, 5)),
                    (x + sw2 + random.randint(-4, 4), sy2 + random.randint(-8, 8)),
                    (x + sw2, self.height),
                ]
                pygame.draw.polygon(surf, scol, pts)
                pygame.draw.lines(surf, (scol[0]+18, scol[1]+18, scol[2]+18), False, pts, 1)
                # Crack pattern
                for _ in range(random.randint(2, 5)):
                    cx1 = x + random.randint(4, sw2 - 4)
                    cy1 = sy2 + random.randint(10, sh2 - 10)
                    pygame.draw.line(surf, (4, 4, 4),
                                     (cx1, cy1),
                                     (cx1 + random.randint(-12, 12),
                                      cy1 + random.randint(8, 28)), 1)
                # Graffiti-style data tag
                if random.random() < 0.4:
                    tag = random.choice(["0xFF", "DEAD", "NULL", "ERR", "∅"])
                    try:
                        tf2 = pygame.font.SysFont("consolas", 10)
                    except:
                        tf2 = pygame.font.Font(None, 10)
                    tsurf = tf2.render(tag, True, (0, 55, 10))
                    tsurf.set_alpha(60)
                    surf.blit(tsurf, (x + 5, sy2 + sh2 // 2))

            elif structure_type == 'terminal':
                tw  = random.randint(35, 55)
                th  = random.randint(55, 100)
                ty  = self.height - th - random.randint(5, 25)
                # Stand / pedestal
                pygame.draw.rect(surf, (14, 14, 16),
                                 (x + tw // 2 - 5, ty + th, 10, 25))
                # Monitor body
                pygame.draw.rect(surf, (18, 18, 22), (x, ty, tw, th))
                pygame.draw.rect(surf, (35, 35, 40), (x, ty, tw, th), 1)
                # Screen (dead green / dead blue / static)
                screen_col = random.choice([(0, 20, 5), (0, 5, 18), (12, 12, 8)])
                pygame.draw.rect(surf, screen_col, (x+3, ty+4, tw-6, th-12))
                # Screen content — dead data lines or static
                if random.random() < 0.5:
                    try:
                        sf2 = pygame.font.SysFont("consolas", 7)
                    except:
                        sf2 = pygame.font.Font(None, 7)
                    lines_t = ["FATAL ERR", "0x000000", "NO INPUT", "HALTED", "> _"]
                    for li, ln in enumerate(random.sample(lines_t, min(3, len(lines_t)))):
                        lt = sf2.render(ln, True, (0, 80, 12))
                        lt.set_alpha(90)
                        surf.blit(lt, (x + 4, ty + 5 + li * 9))
                else:
                    # Static noise pattern
                    for _ in range(30):
                        nx = x + 3 + random.randint(0, tw - 8)
                        ny = ty + 4 + random.randint(0, th - 14)
                        nc = random.choice([(0,60,8),(60,0,0),(0,0,60),(40,40,10)])
                        pygame.draw.rect(surf, nc, (nx, ny, random.randint(1,4), 1))

            elif structure_type == 'pillar':
                pw  = random.randint(14, 30)
                ph  = random.randint(100, 300)
                py  = self.height - ph
                pcol = random.choice([(16,12,10),(10,16,10),(10,10,18)])
                pygame.draw.rect(surf, pcol, (x, py, pw, ph))
                # Vertical scoring marks
                for _ in range(random.randint(2, 6)):
                    mark_y = py + random.randint(10, ph - 10)
                    pygame.draw.line(surf, (4,4,4),
                                     (x + 2, mark_y),
                                     (x + pw - 2, mark_y + random.randint(-2, 2)), 1)
                # Cap at top
                pygame.draw.rect(surf, (pcol[0]+14, pcol[1]+14, pcol[2]+14),
                                 (x - 3, py, pw + 6, 8))

        # ── Distant power/data cable catenary spans between structures ──
        for _ in range(12):
            cx1 = random.randint(0, surface_w - 100)
            cx2 = cx1 + random.randint(80, 300)
            cy1 = random.randint(int(self.height * 0.2), int(self.height * 0.6))
            cy2 = cy1 + random.randint(-30, 30)
            sag = random.randint(15, 50)
            cc  = random.choice([(20,20,20),(0,35,6),(35,6,0)])
            # Approximate catenary as quadratic arc
            steps = 20
            prev  = (cx1, cy1)
            for i in range(1, steps + 1):
                t_c  = i / steps
                mid_y = cy1 + (cy2 - cy1) * t_c + sag * math.sin(math.pi * t_c)
                cur  = (int(cx1 + (cx2 - cx1) * t_c), int(mid_y))
                pygame.draw.line(surf, cc, prev, cur, 1)
                prev = cur

        return surf

    def _generate_fg_debris(self):
        """Foreground debris strip: broken chips, glass shards, pooled corrosion, rubble."""
        surface_w = self.width + 400
        ground_band = 80   # Taller strip for richer ground detail
        surf = pygame.Surface((surface_w, ground_band), pygame.SRCALPHA)

        # ── Base ground: dark stained slab ──
        for y in range(ground_band):
            t = y / ground_band
            r = int(4 + t * 6)
            g = int(6 + t * 10)
            b = int(4 + t * 5)
            pygame.draw.line(surf, (r, g, b), (0, y), (surface_w, y))

        # ── Corrosion / acid pools on the ground ──
        for _ in range(25):
            px  = random.randint(0, surface_w - 40)
            py  = random.randint(ground_band // 2, ground_band - 8)
            pw  = random.randint(10, 60)
            ph  = random.randint(3, 12)
            col = random.choice([(0, 80, 10), (0, 60, 5), (30, 50, 0), (0, 40, 40)])
            pool = pygame.Surface((pw, ph), pygame.SRCALPHA)
            pool.fill((*col, random.randint(40, 100)))
            surf.blit(pool, (px, py))
            # Highlight edge
            pygame.draw.line(surf, (*col[:2], min(255, col[2]+30), 60),
                             (px + 1, py), (px + pw - 1, py), 1)

        # ── Scattered circuit board fragments ──
        for _ in range(80):
            fx  = random.randint(0, surface_w - 20)
            fy  = random.randint(2, ground_band - 6)
            fw  = random.randint(5, 20)
            fh  = random.randint(3, 10)
            fc  = random.choice([(8, 22, 8), (20, 10, 6), (8, 8, 22), (18, 18, 10)])
            pygame.draw.rect(surf, fc, (fx, fy, fw, fh))
            # Trace lines on chip
            if fw > 10:
                pygame.draw.line(surf, (fc[0]+15, fc[1]+15, fc[2]+15),
                                 (fx+2, fy+fh//2), (fx+fw-2, fy+fh//2), 1)

        # ── Broken glass / metal shards ──
        for _ in range(120):
            gx  = random.randint(0, surface_w - 10)
            gy  = random.randint(0, ground_band - 4)
            gsz = random.randint(2, 14)
            gc  = random.choice([
                (20, 10, 6), (6, 20, 8), (6, 6, 22),
                (30, 16, 6), (8, 28, 8), (4, 4, 30),
                (22, 22, 14)
            ])
            if random.random() < 0.6:
                # Triangle shard
                pts = [
                    (gx, gy + gsz),
                    (gx + gsz // 2 + random.randint(-2, 2), gy),
                    (gx + gsz, gy + gsz // 2 + random.randint(-2, 2)),
                ]
                pygame.draw.polygon(surf, gc, pts)
            else:
                # Rect chip
                pygame.draw.rect(surf, gc, (gx, gy, gsz, max(1, gsz // 2)))

        # ── Larger rubble blocks scattered on ground surface ──
        for _ in range(30):
            rx  = random.randint(0, surface_w - 30)
            ry  = random.randint(ground_band // 3, ground_band - 12)
            rw  = random.randint(8, 35)
            rh  = random.randint(5, 16)
            rc  = random.choice([(18, 12, 10), (12, 18, 10), (10, 10, 20), (20, 16, 8)])
            # Irregular polygon (not just a box)
            pts = [
                (rx, ry + rh),
                (rx + random.randint(-2, 2), ry),
                (rx + rw + random.randint(-3, 3), ry + random.randint(-3, 3)),
                (rx + rw, ry + rh),
            ]
            pygame.draw.polygon(surf, rc, pts)
            pygame.draw.lines(surf, (rc[0]+20, rc[1]+20, rc[2]+20), True, pts, 1)

        # ── Dust / scatter noise ──
        for _ in range(200):
            nx = random.randint(0, surface_w - 1)
            ny = random.randint(0, ground_band - 1)
            nc = random.choice([(20,20,14),(10,24,10),(24,10,6)])
            surf.set_at((nx, ny), (*nc, random.randint(20, 60)))

        return surf

    def _generate_scanlines(self):
        """Static scanline overlay for CRT effect."""
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        for y in range(0, self.height, 3):
            pygame.draw.line(surf, (0, 0, 0, 35), (0, y), (self.width, y))
        return surf

    def _generate_vignette(self):
        """Heavy radial vignette — crushes corners into void."""
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        cx, cy = self.width // 2, self.height // 2
        max_r = math.sqrt(cx**2 + cy**2)

        # Draw concentric ellipses from outside in, decreasing alpha
        steps = 60
        for i in range(steps, 0, -1):
            t     = i / steps                          # 1.0 = edge, 0.0 = center
            alpha = int(t ** 1.6 * 200)                # Power curve: dark edges
            scale = t
            w     = int(self.width  * scale)
            h     = int(self.height * scale)
            x     = (self.width  - w) // 2
            y     = (self.height - h) // 2
            pygame.draw.ellipse(surf, (0, 0, 0, alpha), (x, y, w, h), 4)

        # Extra crush on bottom (ground) and top (ceiling)
        for dy in range(80):
            alpha = int((1 - dy / 80) ** 2 * 220)
            pygame.draw.line(surf, (0, 0, 0, alpha), (0, self.height - dy), (self.width, self.height - dy))
        for dy in range(50):
            alpha = int((1 - dy / 50) ** 1.5 * 160)
            pygame.draw.line(surf, (0, 0, 0, alpha), (0, dy), (self.width, dy))

        return surf

    def _generate_tombstones(self):
        """Dead process tombstones — small crumbling monuments with error codes."""
        tombstones = []
        epitaphs = [
            ["PROCESS 4721", "SEGFAULT", "CORE DUMPED"],
            ["SVC: NULL_IO", "UNHANDLED EXC", "0xC000005"],
            ["MEM: 0x00000", "READ FAULT", "R.I.P"],
            ["THREAD_POOL", "DEADLOCK", "TIMED OUT"],
            ["SYS_DAEMON", "KILLED -9", "NO TRACE"],
            ["DATA STREAM", "CORRUPTED", "UNRECOVERABLE"],
        ]
        surface_w = self.width + 400
        x = random.randint(80, 220)
        while x < surface_w:
            w  = random.randint(36, 60)
            h  = random.randint(50, 90)
            gy = self.height - h - random.randint(0, 20)  # Sits on "ground"

            surf = pygame.Surface((w, h + 20), pygame.SRCALPHA)

            # Stone body (slightly skewed)
            body_pts = [
                (2, h),
                (random.randint(0, 4), random.randint(10, 20)),          # top-left
                (w // 2 + random.randint(-3, 3), random.randint(0, 8)),  # arch tip
                (w - random.randint(0, 4), random.randint(10, 20)),      # top-right
                (w - 2, h),
            ]
            stone_color = random.choice([(22, 14, 10), (12, 18, 12), (15, 12, 20)])
            pygame.draw.polygon(surf, stone_color, body_pts)
            pygame.draw.lines(surf, (45, 40, 35), True, body_pts, 1)

            # Crack lines
            for _ in range(random.randint(1, 3)):
                cx1 = random.randint(3, w - 3)
                cy1 = random.randint(15, h - 15)
                pygame.draw.line(surf, (5, 5, 5),
                                 (cx1, cy1),
                                 (cx1 + random.randint(-8, 8), cy1 + random.randint(5, 20)), 1)

            # Epitaph text
            lines = random.choice(epitaphs)
            try:
                tf = pygame.font.SysFont("consolas", 8)
            except:
                tf = pygame.font.Font(None, 8)
            for li, line in enumerate(lines):
                col = (0, 100, 10) if li < len(lines) - 1 else (80, 0, 0)
                t = tf.render(line, True, col)
                surf.blit(t, (2, 18 + li * 11))

            tombstones.append({'x': x, 'y': gy, 'surf': surf, 'w': w, 'h': h})
            x += random.randint(160, 450)

        return tombstones

    # ------------------------------------------------------------------ #
    #  PARTICLE FACTORIES
    # ------------------------------------------------------------------ #

    def _create_ash(self):
        """Upward-floating dead data particle."""
        return {
            'x':     random.randint(0, self.width),
            'y':     random.randint(self.height, int(self.height * 1.5)),
            'speed': random.uniform(0.3, 1.8),
            'char':  random.choice(['0', '1', 'X', '?', '§', 'µ', '∅', '¬', '░', '▒']),
            'alpha': random.randint(40, 180),
            'phase': random.uniform(0, math.pi * 2),
            'color': random.choice([(60, 120, 60), (80, 40, 20), (40, 40, 80), (100, 60, 0)]),
        }

    def _create_drip(self):
        """Toxic acid drip falling from the ceiling."""
        return {
            'x':      random.randint(0, self.width),
            'y':      random.randint(-60, 0),
            'speed':  random.uniform(0.8, 3.0),
            'length': random.randint(4, 20),
            'alpha':  random.randint(60, 200),
            'color':  random.choice([(0, 160, 30), (0, 180, 10), (10, 200, 50), (0, 120, 20)]),
            'pooled': False,
            'pool_x': 0,
            'pool_y': 0,
            'pool_r': 0,
            'pool_life': 0,
        }

    # ------------------------------------------------------------------ #
    #  UPDATE
    # ------------------------------------------------------------------ #

    def update(self, camera_speed):
        self.frame_count += 1

        # Parallax scrolls at different speeds
        self.scroll_x   -= camera_speed * 0.08   # Far BG — slowest
        self.scroll_mid -= camera_speed * 0.25   # Mid layer
        self.scroll_fg  -= camera_speed * 0.55   # Foreground debris

        # Wrap each layer
        for attr, w in [('scroll_x', self.width + 400),
                        ('scroll_mid', self.width + 400),
                        ('scroll_fg', self.width + 400)]:
            if getattr(self, attr) <= -(w):
                setattr(self, attr, 0)

        # --- Ash particles ---
        for ash in self.ashes:
            ash['y'] -= ash['speed']
            ash['x'] += math.sin(self.frame_count * 0.04 + ash['phase']) * 0.4
            if ash['y'] < -20:
                new_ash = self._create_ash()
                ash.clear()
                ash.update(new_ash)
                ash['y'] = self.height + random.randint(0, 80)

        # --- Drip particles ---
        for drip in self.drips:
            if drip['pooled']:
                drip['pool_r']   += 0.3
                drip['pool_life'] -= 1
                if drip['pool_life'] <= 0:
                    new_drip = self._create_drip()
                    drip.clear()
                    drip.update(new_drip)
            else:
                drip['y'] += drip['speed']
                if drip['y'] > self.height - 55:
                    # Splat into pool
                    drip['pooled']    = True
                    drip['pool_x']    = drip['x']
                    drip['pool_y']    = self.height - 55
                    drip['pool_r']    = 2
                    drip['pool_life'] = random.randint(40, 120)

        # --- Glitch strips: rare, ominous events ---
        self._glitch_strip_timer -= 1
        if self._glitch_strip_timer <= 0:
            # Only 1–2 strips, very short life, subtle dark-green tint not red
            count = random.randint(1, 2)
            self._glitch_strips = []
            for _ in range(count):
                sh = random.randint(2, 18)
                sy = random.randint(0, self.height - sh)
                self._glitch_strips.append({
                    'y':      sy,
                    'h':      sh,
                    'offset': random.randint(-5, 5),
                    'life':   random.randint(1, 4),   # Very brief
                })
            self._glitch_event_alpha = 30             # Subtle dark flash
            # Long silence between glitch events (3–8 seconds at 60fps)
            self._glitch_strip_timer = random.randint(180, 480)
        else:
            for s in self._glitch_strips:
                s['life'] -= 1
            self._glitch_strips = [s for s in self._glitch_strips if s['life'] > 0]

        # Decay the glitch flash quickly
        if self._glitch_event_alpha > 0:
            self._glitch_event_alpha = max(0, self._glitch_event_alpha - 6)

        # --- Ghost text alpha flicker ---
        for gt in self.ghost_texts:
            flicker = math.sin(self.frame_count * gt['flicker_speed'] + gt['flicker_offset'])
            gt['_alpha'] = max(4, int(gt['alpha'] + flicker * 8))

        # --- Tombstone scroll (they move with mid layer) ---
        for tomb in self.tombstones:
            tomb['x'] -= camera_speed * 0.25

        # --- Toxic fog pulse ---
        self.fog_alpha = int(10 + math.sin(self.frame_count * 0.015) * 8)

    # ------------------------------------------------------------------ #
    #  DRAW
    # ------------------------------------------------------------------ #

    def draw(self, surface):

        # ── 1. VOID FILL ──────────────────────────────────────────────
        surface.fill(self.VOID_BLACK)

        # ── 2. FAR BACKGROUND (parallax — slowest) ────────────────────
        x0 = int(self.scroll_x)
        surface.blit(self.far_bg, (x0, 0))
        surface.blit(self.far_bg, (x0 + self.width + 400, 0))

        # ── 3. GHOST TEXTS (enormous, nearly invisible NULL/VOID labels) ─
        for gt in self.ghost_texts:
            alpha = gt.get('_alpha', gt['alpha'])
            txt = self.big_font.render(gt['text'], True, (0, 80, 10))
            txt.set_alpha(alpha)
            txt_rot = pygame.transform.rotate(txt, random.choice([0, 90, -90]) if random.random() < 0.02 else 0)
            surface.blit(txt_rot, (int(gt['x'] + x0 * 0.05) % self.width, gt['y']))

        # ── 4. JUNK PILE MOUNTAINS ────────────────────────────────────
        x1 = int(self.scroll_x * 1.3)  # slightly faster than far BG
        surface.blit(self.junk_piles, (x1, 0))
        surface.blit(self.junk_piles, (x1 + self.width + 400, 0))

        # ── 5. MID LAYER (server racks, ruins) ───────────────────────
        xm = int(self.scroll_mid)
        surface.blit(self.mid_layer, (xm, 0))
        surface.blit(self.mid_layer, (xm + self.width + 400, 0))

        # ── 6. MEMORY TOMBSTONES ─────────────────────────────────────
        for tomb in self.tombstones:
            tx = int(tomb['x'])
            if -tomb['w'] < tx < self.width + 10:
                surface.blit(tomb['surf'], (tx, tomb['y']))

        # ── 7. TOXIC DRIPS (falling from ceiling) ─────────────────────
        for drip in self.drips:
            if drip['pooled']:
                r = int(drip['pool_r'])
                if r > 0:
                    a = max(0, int(drip['alpha'] * (drip['pool_life'] / 100)))
                    pool_surf = pygame.Surface((r * 2 + 2, r + 2), pygame.SRCALPHA)
                    pygame.draw.ellipse(pool_surf, (*drip['color'], a),
                                        (0, 0, r * 2, max(1, r // 2)))
                    surface.blit(pool_surf, (drip['pool_x'] - r, drip['pool_y']))
            else:
                # Draw the drip as a tapered line
                x_d = int(drip['x'])
                y_d = int(drip['y'])
                length = drip['length']
                col = drip['color']
                a = drip['alpha']
                # Body
                drip_surf = pygame.Surface((3, length + 6), pygame.SRCALPHA)
                pygame.draw.line(drip_surf, (*col, a),        (1, 0),      (1, length))
                pygame.draw.line(drip_surf, (*col, a // 2),   (1, length), (1, length + 3))
                # Bead at tip
                pygame.draw.circle(drip_surf, (*col, a), (1, length + 4), 2)
                surface.blit(drip_surf, (x_d - 1, y_d))

        # ── 8. ASH PARTICLES (rising dead data) ───────────────────────
        for ash in self.ashes:
            txt = self.font.render(ash['char'], True, ash['color'])
            txt.set_alpha(ash['alpha'])
            surface.blit(txt, (int(ash['x']), int(ash['y'])))

        # ── 9. FOREGROUND GROUND DEBRIS ──────────────────────────────
        xf = int(self.scroll_fg)
        ground_y = self.height - 80
        surface.blit(self.fg_debris, (xf, ground_y))
        surface.blit(self.fg_debris, (xf + self.width + 400, ground_y))

        # ── 10. TOXIC FOG LAYER (ground-hugging) ──────────────────────
        fog_h = 90
        self.fog_surface.fill((0, 0, 0, 0))
        for fy in range(fog_h):
            t     = 1.0 - (fy / fog_h)
            alpha = int(t ** 2 * (self.fog_alpha + 5))
            pygame.draw.line(self.fog_surface,
                             (0, 30, 5, alpha),
                             (0, self.height - fog_h + fy),
                             (self.width, self.height - fog_h + fy))
        surface.blit(self.fog_surface, (0, 0))

        # ── 11. GLITCH STRIPS (rare, ominous — dark green tint, not red) ──
        for s in self._glitch_strips:
            sy, sh, offset = s['y'], s['h'], s['offset']
            if sh > 0 and sy >= 0 and sy + sh <= self.height:
                try:
                    strip = surface.subsurface((0, sy, self.width, sh)).copy()
                    surface.blit(strip, (offset, sy))
                    # Dark green desaturating tint — feels like a dying CRT
                    tint = pygame.Surface((self.width, sh), pygame.SRCALPHA)
                    tint.fill((0, 20, 5, 18))
                    surface.blit(tint, (0, sy), special_flags=pygame.BLEND_RGBA_ADD)
                except ValueError:
                    pass

        # Glitch event: brief whole-screen dark pulse
        if self._glitch_event_alpha > 0:
            flash = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            flash.fill((0, 8, 2, self._glitch_event_alpha))
            surface.blit(flash, (0, 0))

        # ── 12. SCANLINES ─────────────────────────────────────────────
        surface.blit(self.scanlines, (0, 0))

        # ── 13. VIGNETTE ──────────────────────────────────────────────
        surface.blit(self.vignette, (0, 0))

class IndustrialBackground:
    """
    THE FORGE — a visceral heavy-industry environment.

    Layer stack (back to front):
      1. Sky — burnt gradient, pulsing furnace glow rising from below
      2. Far factory silhouettes — massive structures with chimneys, catwalks, cranes
      3. Smoke columns — thick billowing plumes anchored to chimney positions
      4. Mid machinery — gear assemblies in housings, piston rigs, pipe networks
      5. Catwalk / scaffolding — horizontal walkways crossing the mid-ground
      6. Molten glow sources — bright slag/furnace openings with animated light halos
      7. Sparks — welding bursts anchored to specific forge points
      8. Heat haze — scanline-distortion effect at ground level
      9. Soot vignette — crushes edges in dirty brown-black
    """

    def __init__(self, screen_width, screen_height):
        self.width  = screen_width
        self.height = screen_height
        self.frame_count = 0

        # Parallax scroll offsets (three independent speeds)
        self.scroll_far = 0.0   # Far factory silhouettes
        self.scroll_mid = 0.0   # Mid machinery layer
        self.scroll_fg  = 0.0   # Foreground catwalk / sparks

        # ── COLOR PALETTE ────────────────────────────────────────────
        # Wide value contrast: shadows truly dark (5-15), lit surfaces punch (100-180)
        self.C_SKY_TOP     = (5,   2,   2)    # True near-black zenith
        self.C_SKY_BOT     = (45,  14,  4)    # Hot rust-orange horizon
        self.C_METAL_DARK  = (12,  9,   6)    # Cast shadow on iron
        self.C_METAL_MID   = (52,  40,  25)   # Lit steel face
        self.C_METAL_LIGHT = (110, 85,  50)   # Specular highlight
        self.C_METAL_RIM   = (160, 110, 55)   # Hot-lit rim near heat source
        self.C_RUST        = (110, 42,  10)   # Surface rust
        self.C_RUST_DARK   = (65,  22,   5)   # Deep rust in recesses
        self.C_SOOT        = (8,   6,   5)    # Soot black
        self.C_SOOT_STREAK = (18,  14,  10)   # Soot deposit
        self.C_SMOKE_CORE  = (28,  24,  20)   # Dense smoke belly
        self.C_SMOKE_MID   = (55,  48,  38)   # Billowing mid-tone
        self.C_SMOKE_EDGE  = (80,  70,  55)   # Thin wispy edge
        self.C_MOLTEN_CORE = (255, 220,  80)  # White-yellow molten centre
        self.C_MOLTEN_MID  = (255, 100,  10)  # Deep orange furnace throat
        self.C_MOLTEN_EDGE = (180,  30,   4)  # Dying crust at edge
        self.C_EMBER       = (240,  80,   5)  # Live ember
        self.C_SPARK_HOT   = (255, 255, 200)  # White-hot spark tip
        self.C_SPARK_WARM  = (255, 180,  40)  # Warm spark body
        self.C_SPARK_COOL  = (220,  60,   8)  # Cooling tail

        # ── PRE-BAKED SURFACES ───────────────────────────────────────
        self.sky_surf        = self._bake_sky()
        self.far_factories   = self._bake_far_factories()
        self.mid_machinery   = self._bake_mid_machinery()
        self.catwalk_layer   = self._bake_catwalks()
        self.vignette        = self._bake_vignette()
        self.heat_haze_strip = self._bake_heat_haze_strip()

        # ── DUMAN SÜTUNLARI — İLLÜZYON SİSTEMİ ─────────────────────
        #
        #  ESKİ: baca başına 14-22 parçacık × N baca = yüzlerce parçacık.
        #        Her frame sorted() + per-parçacık SRCALPHA Surface yaratma.
        #
        #  İLLÜZYON TEKNİKLERİ:
        #   1. SCROLLING COLUMN TEXTURE — baca başına bir kez pre-bake edilmiş
        #      yüksek duman sütunu dokusu. Gerçek parçacık yok; dikey twin-scroll
        #      ile "yükselen duman" yanılsaması yaratılır. Parallax katmanlarıyla
        #      TAMAMEN AYNI numara, sadece yatay değil dikey.
        #   2. SEAMLESSLİK — dokunun üst ve alt kenarları alpha=0'a söner;
        #      twin-buffer döngüsünde hiç kesinti olmaz.
        #   3. FLIPBOOK PUFF — baca ağzında 4 pre-bake edilmiş "çıkış bulutu"
        #      sprite'ı döngüsel olarak gösterilir; yeni parçacık üretimi yok.
        #
        #  Sonuç: N×22 parçacık update+draw → N×2 blit (baca sayısı ne olursa)
        #
        self.smoke_columns = []
        for chimney_x in self._chimney_positions:
            col_surf = self._bake_smoke_column(chimney_x)
            col_h    = col_surf.get_height()
            self.smoke_columns.append({
                'x':     chimney_x,
                'surf':  col_surf,
                'col_h': col_h,
                # İki kopya: biri diğerinin hemen üzerinde → seamless döngü
                'y1': float(self.height - col_h),   # alt kopya (aktif)
                'y2': float(self.height - col_h * 2),  # üst kopya (bekleyen)
                'speed': random.uniform(0.55, 1.1),
            })
        # Baca ağzı efekti için 8 pre-bake puff sprite (küçük→büyük)
        self._puff_sprites = self._bake_puff_sprites()
        self._puff_frame   = 0   # ortak flipbook sayacı

        # ── GEAR ASSEMBLIES (mid layer, animated) ────────────────────
        # Each gear lives inside a housing and meshes with neighbours
        self.gear_assemblies = self._init_gear_assemblies()

        # ── PISTONS (mid layer, animated) ────────────────────────────
        self.pistons = self._init_pistons()

        # ── MOLTEN SOURCES (furnace openings, forge vents) ───────────
        self.molten_sources = []
        for _ in range(random.randint(3, 6)):
            self.molten_sources.append({
                'x':         random.randint(80, self.width - 80),
                'y':         self.height - random.randint(20, 80),
                'base_r':    random.randint(18, 45),
                'pulse':     random.uniform(0, math.pi * 2),
                'pulse_spd': random.uniform(0.04, 0.10),
            })

        # ── SPARK EMITTERS anchored to forge/weld points ─────────────
        self.spark_emitters = []
        for ms in self.molten_sources:
            self.spark_emitters.append({
                'x': ms['x'] + random.randint(-20, 20),
                'y': ms['y'],
                'burst_timer':    random.randint(0, 80),
                'burst_interval': random.randint(40, 120),
            })
        self.sparks = []  # Active spark particles

        # ── HEAT HAZE STATE ──────────────────────────────────────────
        self._haze_offset   = 0.0   # Scrolls the wavy distortion pattern
        self._haze_surf     = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

        # ── FURNACE GLOW PULSE ───────────────────────────────────────
        self._glow_pulse    = 0.0
        self._glow_surf     = pygame.Surface((self.width, self.height), pygame.SRCALPHA)

    # ================================================================ #
    #  SURFACE BAKERS
    # ================================================================ #

    def _bake_sky(self):
        """
        Multi-stop gradient sky:
          - Pure near-black at zenith
          - Deep brown-red in mid sky (smoke-stained atmosphere)
          - Saturated rust-orange near horizon (furnace light from below)
        Also bakes in a subtle atmospheric haze band and distant heat shimmer.
        """
        surf = pygame.Surface((self.width, self.height))

        # Four gradient stops
        stops = [
            (0.00, (5,  2,  2)),    # zenith: true black
            (0.35, (14, 5,  3)),    # upper atmosphere: smoke brown
            (0.70, (35, 12, 4)),    # lower atmosphere: rust-red
            (1.00, (60, 18, 5)),    # horizon: hot orange glow
        ]

        for y in range(self.height):
            t = y / self.height
            # Find which two stops we're between
            for i in range(len(stops) - 1):
                t0, c0 = stops[i]
                t1, c1 = stops[i + 1]
                if t0 <= t <= t1:
                    f = (t - t0) / (t1 - t0)
                    r = int(c0[0] + (c1[0] - c0[0]) * f)
                    g = int(c0[1] + (c1[1] - c0[1]) * f)
                    b = int(c0[2] + (c1[2] - c0[2]) * f)
                    break
            pygame.draw.line(surf, (r, g, b), (0, y), (self.width, y))

        # Bake in some faint horizontal soot/haze streaks in the upper sky
        for _ in range(30):
            sy  = random.randint(0, int(self.height * 0.6))
            sx  = random.randint(0, self.width)
            sw2 = random.randint(60, 400)
            sh2 = random.randint(1, 3)
            a   = random.randint(6, 20)
            streak = pygame.Surface((sw2, sh2), pygame.SRCALPHA)
            streak.fill((20, 8, 4, a))
            surf.blit(streak, (sx, sy))

        return surf

    def _bake_far_factories(self):
        """
        Distant factory silhouettes with:
        - Strong furnace top-lighting (orange rim on top edges)
        - Vertical rust/soot streaks flowing DOWN from joints
        - Side face darker than front face (3/4 lighting)
        - Far buildings warmer/hazier (atmospheric perspective from heat)
        - Chimneys with proper taper and warning banding
        - Gantry cranes, connecting bridges, roof plant
        """
        surface_w = self.width + 600
        surf = pygame.Surface((surface_w, self.height), pygame.SRCALPHA)
        self._chimney_positions = []

        x = 0
        building_idx = 0
        while x < surface_w:
            bw = random.randint(100, 320)
            bh = random.randint(160, 450)
            by = self.height - bh

            # Atmospheric depth: far buildings (large x) get a warm haze tint
            depth_t = min(1.0, x / surface_w)
            base_r  = int(random.randint(10, 20) + depth_t * 18)
            base_g  = int(random.randint(7,  14) + depth_t * 8)
            base_b  = int(random.randint(5,  10) + depth_t * 4)
            bc      = (base_r, base_g, base_b)

            # ── Front face (main body) ──────────────────────────────
            pygame.draw.rect(surf, bc, (x, by, bw, bh))

            # ── Side face (right side, darker — 3/4 lighting) ───────
            side_w = random.randint(8, 22)
            side_c = (max(0, bc[0]-6), max(0, bc[1]-5), max(0, bc[2]-4))
            pygame.draw.rect(surf, side_c, (x + bw, by + side_w, side_w, bh - side_w))
            # Top slant of side face
            pygame.draw.polygon(surf, side_c, [
                (x + bw,          by),
                (x + bw + side_w, by + side_w),
                (x + bw + side_w, by + bh),
                (x + bw,          by + bh),
            ])

            # ── Furnace rim lighting on top edge ────────────────────
            # Orange glow hits the top of every structure from below
            rim_intensity = random.randint(120, 180)
            rim_c = (rim_intensity, rim_intensity // 3, rim_intensity // 12)
            pygame.draw.line(surf, rim_c, (x, by), (x + bw, by), 2)
            # Soft gradient below the rim (baked in as semi-transparent lines)
            for rim_y in range(1, 6):
                a = max(0, 50 - rim_y * 10)
                rim_s = pygame.Surface((bw, 1), pygame.SRCALPHA)
                rim_s.fill((*rim_c, a))
                surf.blit(rim_s, (x, by + rim_y))

            # ── Horizontal floor bands ────────────────────────────
            floor_h = random.randint(28, 50)
            for fy in range(by + floor_h, by + bh, floor_h):
                pygame.draw.line(surf, (bc[0]+10, bc[1]+8, bc[2]+5),
                                 (x + 2, fy), (x + bw - 2, fy), 1)

            # ── Window grid ──────────────────────────────────────
            win_cols = max(2, bw // 26)
            win_rows = max(2, bh // 32)
            for wc2 in range(win_cols):
                for wr in range(win_rows):
                    wx = x + 8 + wc2 * (bw // win_cols)
                    wy = by + 10 + wr  * (bh // win_rows)
                    ww2 = random.randint(7, 16)
                    wh2 = random.randint(10, 20)
                    if random.random() < 0.25:
                        # Lit — orange/amber, varies in warmth
                        wglow = random.choice([
                            (200, 120, 30), (220, 90, 15), (180, 140, 40), (240, 80, 10)
                        ])
                        pygame.draw.rect(surf, wglow, (wx, wy, ww2, wh2))
                        # Bloom bleed
                        bloom = pygame.Surface((ww2 + 8, wh2 + 8), pygame.SRCALPHA)
                        bloom.fill((*wglow, 28))
                        surf.blit(bloom, (wx - 4, wy - 4))
                    else:
                        pygame.draw.rect(surf, (5, 4, 3), (wx, wy, ww2, wh2))
                        # Window frame
                        pygame.draw.rect(surf, (bc[0]+5, bc[1]+4, bc[2]+3),
                                         (wx, wy, ww2, wh2), 1)

            # ── Rust streaks flowing DOWN from horizontal joints ────
            for fy in range(by + floor_h, by + bh, floor_h):
                for _ in range(random.randint(0, 4)):
                    rx2 = x + random.randint(4, bw - 4)
                    streak_len = random.randint(10, 55)
                    streak_w2  = random.choice([1, 1, 2])
                    rust_c = random.choice([self.C_RUST, self.C_RUST_DARK,
                                            self.C_SOOT_STREAK])
                    pygame.draw.line(surf, rust_c,
                                     (rx2, fy),
                                     (rx2 + random.randint(-3, 3), fy + streak_len),
                                     streak_w2)

            # ── Soot staining on lower wall surfaces ─────────────
            for _ in range(random.randint(2, 6)):
                sx2  = x + random.randint(0, bw - 20)
                soot_h2 = random.randint(20, 80)
                soot_w2 = random.randint(8, 30)
                for si in range(soot_h2):
                    a = int((1 - si / soot_h2) * random.randint(20, 50))
                    ss = pygame.Surface((soot_w2, 1), pygame.SRCALPHA)
                    ss.fill((*self.C_SOOT_STREAK, a))
                    surf.blit(ss, (sx2, by + bh - soot_h2 + si))

            # ── Roof plant / penthouse boxes ─────────────────────
            for _ in range(random.randint(1, 4)):
                prx  = x + random.randint(10, max(11, bw - 40))
                prw  = random.randint(18, 65)
                prh  = random.randint(12, 45)
                pr_c = (bc[0] + random.randint(3, 8), bc[1] + 3, bc[2] + 2)
                pygame.draw.rect(surf, pr_c, (prx, by - prh, prw, prh))
                # Rim light on roof plant top
                pygame.draw.line(surf, rim_c,
                                 (prx, by - prh), (prx + prw, by - prh), 1)

            # ── Chimneys ─────────────────────────────────────────
            num_chimneys = random.randint(1, 3)
            for _ in range(num_chimneys):
                cw2 = random.randint(14, 35)
                ch2 = random.randint(90, 260)
                cx2 = x + random.randint(8, max(9, bw - cw2 - 8))
                cy2 = by - ch2
                taper = random.randint(2, 5)
                pts = [
                    (cx2,           by),
                    (cx2 + cw2,     by),
                    (cx2 + cw2 - taper, cy2),
                    (cx2 + taper,   cy2),
                ]
                ch_c = (random.randint(10, 16), random.randint(8, 12), random.randint(6, 10))
                pygame.draw.polygon(surf, ch_c, pts)
                # Rim light on chimney (it's always backlit by smoke glow)
                pygame.draw.line(surf, rim_c,
                                 (cx2 + taper, cy2),
                                 (cx2 + cw2 - taper, cy2), 2)
                # Banding rings (structural hoops)
                for band_y in range(cy2 + 18, by, random.randint(22, 40)):
                    progress = (by - band_y) / ch2
                    bw3 = cw2 - int(taper * 2 * progress)
                    bx3 = cx2 + int(taper * progress)
                    pygame.draw.line(surf, self.C_METAL_MID,
                                     (bx3, band_y), (bx3 + bw3, band_y), 2)
                # Rust streaks down chimney face
                for _ in range(random.randint(1, 3)):
                    srx = cx2 + taper + random.randint(2, max(3, cw2 - taper - 4))
                    pygame.draw.line(surf, self.C_RUST_DARK,
                                     (srx, cy2 + 20),
                                     (srx + random.randint(-2, 2), cy2 + 20 + random.randint(20, 80)), 1)
                self._chimney_positions.append(cx2 + cw2 // 2)

            # ── Gantry crane ─────────────────────────────────────
            if random.random() < 0.4:
                crane_y2  = by + random.randint(8, 35)
                arm_len2  = random.randint(55, 170)
                arm_dir2  = random.choice([-1, 1])
                arm_end2  = x + bw // 2 + arm_dir2 * arm_len2
                pygame.draw.line(surf, self.C_METAL_MID,
                                 (x + bw // 2, by), (x + bw // 2, crane_y2), 3)
                pygame.draw.line(surf, self.C_METAL_MID,
                                 (x + bw // 2, crane_y2), (arm_end2, crane_y2), 3)
                # Truss detail on horizontal beam
                for tx2 in range(min(x + bw // 2, arm_end2),
                                 max(x + bw // 2, arm_end2), 14):
                    pygame.draw.line(surf, self.C_METAL_DARK,
                                     (tx2, crane_y2 - 5),
                                     (tx2 + 7, crane_y2 + 5), 1)
                hoist_len = random.randint(25, 75)
                pygame.draw.line(surf, self.C_METAL_DARK,
                                 (arm_end2, crane_y2),
                                 (arm_end2, crane_y2 + hoist_len), 1)
                pygame.draw.circle(surf, self.C_METAL_MID, (arm_end2, crane_y2 + hoist_len), 4)

            # ── Connecting bridge ─────────────────────────────────
            if random.random() < 0.3:
                bridge_y2  = by + random.randint(bh // 4, bh * 3 // 4)
                bridge_len2 = random.randint(55, 150)
                bridge_h2   = random.randint(6, 16)
                pygame.draw.rect(surf, self.C_METAL_DARK,
                                 (x + bw, bridge_y2, bridge_len2, bridge_h2))
                pygame.draw.line(surf, rim_c,
                                 (x + bw, bridge_y2),
                                 (x + bw + bridge_len2, bridge_y2), 1)
                for rx3 in range(x + bw, x + bw + bridge_len2, 12):
                    pygame.draw.line(surf, self.C_METAL_MID,
                                     (rx3, bridge_y2), (rx3, bridge_y2 - 9), 1)
                pygame.draw.line(surf, self.C_METAL_MID,
                                 (x + bw, bridge_y2 - 9),
                                 (x + bw + bridge_len2, bridge_y2 - 9), 1)

            x += bw + side_w + random.randint(0, 50)
            building_idx += 1

        return surf

    def _bake_mid_machinery(self):
        """
        Mid-ground: massive gear housings bolted to walls, horizontal pipe
        runs with flanges and valves, vertical pressure vessels.
        """
        surface_w = self.width + 600
        surf = pygame.Surface((surface_w, self.height), pygame.SRCALPHA)

        # ── Horizontal pipe network at two heights ────────────────
        for pipe_y_frac in [0.55, 0.72]:
            pipe_y  = int(self.height * pipe_y_frac)
            ph      = random.randint(10, 20)
            px      = 0
            while px < surface_w:
                seg = random.randint(80, 300)
                pc  = random.choice([self.C_METAL_DARK, self.C_METAL_MID,
                                     (28, 18, 10), (20, 28, 16)])
                # Pipe body
                pygame.draw.rect(surf, pc, (px, pipe_y - ph // 2, seg, ph))
                # Top highlight / bottom shadow
                pygame.draw.line(surf, (pc[0]+18, pc[1]+14, pc[2]+8),
                                 (px, pipe_y - ph // 2), (px + seg, pipe_y - ph // 2), 1)
                pygame.draw.line(surf, (max(0,pc[0]-8), max(0,pc[1]-6), max(0,pc[2]-4)),
                                 (px, pipe_y + ph // 2), (px + seg, pipe_y + ph // 2), 1)
                # Flange joints
                fw = 8
                pygame.draw.rect(surf, self.C_METAL_LIGHT,
                                 (px + seg - fw//2, pipe_y - ph//2 - 3, fw, ph + 6))
                # Bolts on flange
                for boff in [3, ph - 3]:
                    pygame.draw.circle(surf, self.C_METAL_DARK,
                                       (px + seg, pipe_y - ph // 2 + boff), 2)
                # Valve wheel (occasional)
                if random.random() < 0.25:
                    vx = px + random.randint(20, max(21, seg - 20))
                    vy = pipe_y - ph // 2 - 14
                    pygame.draw.circle(surf, self.C_METAL_MID, (vx, vy), 10, 2)
                    pygame.draw.line(surf, self.C_METAL_MID,
                                     (vx - 10, vy), (vx + 10, vy), 2)
                    pygame.draw.line(surf, self.C_METAL_MID,
                                     (vx, vy - 10), (vx, vy + 10), 2)
                    pygame.draw.line(surf, self.C_METAL_DARK,
                                     (vx, vy + 10), (vx, pipe_y - ph // 2), 2)
                # Vertical drop pipe
                if random.random() < 0.3:
                    dx  = px + random.randint(30, max(31, seg - 30))
                    dph = random.randint(8, 14)
                    dl  = random.randint(30, 100)
                    pygame.draw.rect(surf, pc, (dx - dph//2, pipe_y, dph, dl))
                    # End cap
                    pygame.draw.rect(surf, self.C_METAL_LIGHT,
                                     (dx - dph//2 - 2, pipe_y + dl, dph + 4, 5))
                px += seg + random.randint(0, 20)

        # ── Pressure vessels / boiler tanks ──────────────────────
        for _ in range(random.randint(3, 7)):
            vx2  = random.randint(0, surface_w - 80)
            vw   = random.randint(35, 80)
            vh   = random.randint(60, 160)
            vy2  = self.height - vh - random.randint(20, 60)
            vc   = random.choice([(22, 16, 10), (16, 22, 14), (18, 14, 22)])
            # Body (rounded rect via ellipse caps)
            pygame.draw.rect(surf, vc, (vx2, vy2 + vw//2, vw, vh - vw))
            pygame.draw.ellipse(surf, vc, (vx2, vy2, vw, vw))
            pygame.draw.ellipse(surf, vc, (vx2, vy2 + vh - vw, vw, vw))
            # Seam weld line
            pygame.draw.line(surf, self.C_METAL_LIGHT,
                             (vx2 + 2, vy2 + vh // 2), (vx2 + vw - 2, vy2 + vh // 2), 1)
            # Pressure gauge
            gx = vx2 + vw // 2
            gy = vy2 + 12
            pygame.draw.circle(surf, self.C_METAL_MID, (gx, gy), 7, 1)
            pygame.draw.circle(surf, (4, 4, 4), (gx, gy), 5)
            # Gauge needle (random angle)
            nangle = random.uniform(-math.pi * 0.8, math.pi * 0.1)
            pygame.draw.line(surf, (200, 50, 10),
                             (gx, gy),
                             (gx + int(math.cos(nangle) * 4),
                              gy + int(math.sin(nangle) * 4)), 1)
            # Support legs
            for lx2 in [vx2 + 8, vx2 + vw - 8]:
                pygame.draw.line(surf, self.C_METAL_DARK,
                                 (lx2, vy2 + vh), (lx2, self.height), 3)

        # ── Gear housing silhouettes (gears themselves are drawn animated) ─
        self._gear_housing_positions = []
        for _ in range(random.randint(4, 7)):
            ghx = random.randint(30, surface_w - 100)
            ghy = self.height - random.randint(60, 200)
            ghr = random.randint(55, 130)
            # Hexagonal housing
            pts = []
            for i in range(6):
                ang = i * math.pi / 3
                pts.append((ghx + int(math.cos(ang) * (ghr + 12)),
                             ghy + int(math.sin(ang) * (ghr + 12))))
            pygame.draw.polygon(surf, self.C_METAL_DARK, pts)
            pygame.draw.polygon(surf, self.C_METAL_MID, pts, 2)
            # Bolt holes at each hex corner
            for pt in pts:
                pygame.draw.circle(surf, self.C_METAL_LIGHT, pt, 3)
                pygame.draw.circle(surf, self.C_SOOT, pt, 2)
            # Store for animated gear drawing
            self._gear_housing_positions.append((ghx, ghy, ghr))

        return surf

    def _bake_catwalks(self):
        """
        Foreground catwalks and scaffolding: horizontal grated walkways
        with vertical support struts, handrails, safety chains.
        """
        surface_w = self.width + 600
        surf = pygame.Surface((surface_w, self.height), pygame.SRCALPHA)

        for _ in range(random.randint(3, 6)):
            cwy   = random.randint(int(self.height * 0.35), int(self.height * 0.65))
            cwx   = random.randint(0, surface_w // 2)
            cwlen = random.randint(150, 500)
            cwh   = 10

            # Grated floor plate (alternating solid/gap pattern)
            for gx in range(cwx, cwx + cwlen, 6):
                if (gx // 6) % 2 == 0:
                    pygame.draw.rect(surf, self.C_METAL_DARK, (gx, cwy, 5, cwh))
                else:
                    pygame.draw.rect(surf, self.C_SOOT, (gx, cwy, 5, cwh))
            # Top and bottom rails
            pygame.draw.line(surf, self.C_METAL_MID,
                             (cwx, cwy), (cwx + cwlen, cwy), 2)
            pygame.draw.line(surf, self.C_METAL_DARK,
                             (cwx, cwy + cwh), (cwx + cwlen, cwy + cwh), 1)

            # Handrail posts
            for px3 in range(cwx, cwx + cwlen, random.randint(25, 45)):
                post_h = random.randint(18, 30)
                pygame.draw.line(surf, self.C_METAL_MID,
                                 (px3, cwy), (px3, cwy - post_h), 2)
                # Horizontal rail
            pygame.draw.line(surf, self.C_METAL_LIGHT,
                             (cwx, cwy - 20), (cwx + cwlen, cwy - 20), 1)

            # Vertical support struts down to ground
            for sx3 in range(cwx + 20, cwx + cwlen, random.randint(60, 120)):
                pygame.draw.line(surf, self.C_METAL_DARK,
                                 (sx3, cwy + cwh), (sx3 + random.randint(-10, 10), self.height), 2)
                # Cross-brace
                pygame.draw.line(surf, self.C_SOOT,
                                 (sx3 - 15, cwy + cwh + 20),
                                 (sx3 + 15, cwy + cwh + 60), 1)

            # Hanging safety chain (lazy catenary)
            for ci in range(cwx, cwx + cwlen - 30, 30):
                sag_pts = []
                for t in range(11):
                    tc = t / 10
                    cx4 = ci + tc * 30
                    cy4 = cwy - 12 + math.sin(math.pi * tc) * 6
                    sag_pts.append((cx4, cy4))
                if len(sag_pts) > 1:
                    pygame.draw.lines(surf, (50, 42, 30), False, sag_pts, 1)

        return surf

    def _bake_vignette(self):
        """Heavy soot-brown vignette — industrial claustrophobia."""
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        steps = 70
        for i in range(steps, 0, -1):
            t  = i / steps
            a  = int(t ** 1.8 * 210)
            w2 = int(self.width  * t)
            h2 = int(self.height * t)
            x2 = (self.width  - w2) // 2
            y2 = (self.height - h2) // 2
            pygame.draw.ellipse(surf, (10, 6, 4, a), (x2, y2, w2, h2), 5)
        # Extra bottom crush — ground is darker
        for dy in range(100):
            a = int((1 - dy / 100) ** 2.2 * 230)
            pygame.draw.line(surf, (8, 4, 2, a),
                             (0, self.height - dy), (self.width, self.height - dy))
        return surf

    def _bake_smoke_column(self, anchor_x):
        """
        İLLÜZYON 1: Dikey Kayan Sütun Dokusu
        ─────────────────────────────────────
        Baca başına TEK BİR SEFERLE çizilen yüksek doku.
        Runtime'da sadece dikey twin-scroll ile kaydırılır.
        Gerçek parçacık simülasyonu yok — göz kandırma sanatı.

        Doku mantığı:
          • Alt %15 → baca ağzı: dar, yoğun, koyu
          • Orta %60 → açılan sütun: sallanarak genişler
          • Üst %25 → dağılma: giderek şeffaflaşır, alpha→0
          Üst ve alt kenar alpha=0 → twin-scroll döngüsünde
          hiç görünür kesinti olmaz.
        """
        col_w  = 180          # sütun doku genişliği
        col_h  = self.height + 600   # ekrandan taşacak kadar uzun
        surf   = pygame.Surface((col_w, col_h), pygame.SRCALPHA)
        rng    = random.Random(anchor_x)   # tekrarlanabilir rastgelelik

        cx = col_w // 2   # sütun merkezi

        # Katman renkleri (3 duman tonu)
        layers = [
            (self.C_SMOKE_CORE,  0.55),   # koyu çekirdek
            (self.C_SMOKE_MID,   0.35),   # orta ton
            (self.C_SMOKE_EDGE,  0.20),   # açık kenar
        ]

        # Dokuyu aşağıdan yukarıya bloklara böl ve her blokta
        # kalabalık overlap'li daireler çiz (noise benzeri)
        block_size = 40
        for block_y in range(0, col_h, block_size // 2):
            # Yükseklik ilerledikçe duman genişler
            progress  = block_y / col_h          # 0=alt, 1=üst
            spread    = 8 + int(progress * 70)   # piksel cinsinden yatay yayılma
            density   = int(4 + progress * 3)    # bu blokta kaç daire

            # Kenar sönümleme: alt %8 ve üst %20'de alpha azalır
            if progress < 0.08:
                edge_fade = progress / 0.08
            elif progress > 0.80:
                edge_fade = (1.0 - progress) / 0.20
            else:
                edge_fade = 1.0

            for _ in range(density):
                bx  = cx + rng.randint(-spread, spread)
                by  = block_y + rng.randint(-block_size // 2, block_size // 2)
                r   = rng.randint(12 + int(progress * 40), 30 + int(progress * 60))
                col, base_alpha = rng.choice(layers)
                a   = int(base_alpha * edge_fade * rng.uniform(0.5, 1.0) * 255)
                a   = max(0, min(255, a))
                if a > 0:
                    pygame.draw.circle(surf, (*col, a), (bx, by), r)

        return surf

    def _bake_puff_sprites(self, n_frames=8):
        """
        İLLÜZYON 2: Baca Ağzı Flipbook
        ────────────────────────────────
        8 kare pre-bake edilmiş "baca çıkış bulutu" sprite'ı.
        Küçükten büyüğe sıralanır; frame sayacı döngüsel ilerler.
        Runtime'da sıfır yeni Surface — sadece blit.
        """
        sprites = []
        for i in range(n_frames):
            t  = i / (n_frames - 1)        # 0→1 (küçük→büyük/şeffaf)
            r  = int(8 + t * 36)           # yarıçap büyür
            a  = int(200 * (1 - t * 0.7))  # alpha azalır
            s  = pygame.Surface((r * 2 + 4, r * 2 + 4), pygame.SRCALPHA)
            # Üç halkalı yumuşak puff
            pygame.draw.circle(s, (*self.C_SMOKE_EDGE, a // 3),
                               (r+2, r+2), r)
            pygame.draw.circle(s, (*self.C_SMOKE_MID,  a * 2 // 3),
                               (r+2, r+2), max(1, r * 3 // 4))
            pygame.draw.circle(s, (*self.C_SMOKE_CORE, a),
                               (r+2, r+2), max(1, r // 2))
            sprites.append(s)
        return sprites

    def _bake_heat_haze_strip(self):
        """
        A pre-baked wavy alpha mask used to simulate ground-level heat distortion.
        We'll scroll this horizontally each frame and use it to tint.
        """
        w = self.width * 2   # wider so we can scroll it
        h = 80
        surf = pygame.Surface((w, h), pygame.SRCALPHA)
        for x in range(w):
            for y in range(h):
                wave = math.sin(x * 0.06 + y * 0.15) * 0.5 + 0.5
                t    = (1 - y / h) ** 2
                a    = int(wave * t * 22)
                if a > 0:
                    surf.set_at((x, y), (255, 90, 10, a))
        return surf

    # ================================================================ #
    #  RUNTIME OBJECT FACTORIES
    # ================================================================ #

    def _init_gear_assemblies(self):
        """
        Create animated gears positioned inside the pre-baked housings.
        Each assembly can have 1–3 meshing gears.
        """
        assemblies = []
        for (ghx, ghy, ghr) in self._gear_housing_positions:
            n_gears = random.randint(1, 3)
            gears   = []
            base_spd = random.uniform(0.008, 0.025) * random.choice([-1, 1])
            for gi in range(n_gears):
                r2    = ghr - gi * 18 - 10
                if r2 < 12:
                    break
                # Offset center for meshing
                ox = 0 if gi == 0 else int(math.cos(gi * 2.1) * (ghr - 10))
                oy = 0 if gi == 0 else int(math.sin(gi * 2.1) * (ghr - 10))
                gears.append({
                    'cx':     ghx + ox,
                    'cy':     ghy + oy,
                    'r':      r2,
                    'teeth':  max(6, r2 // 8),
                    'angle':  random.uniform(0, math.pi * 2),
                    # Alternate rotation direction for meshing pairs
                    'speed':  base_spd * (1 if gi % 2 == 0 else -1),
                })
            assemblies.append(gears)
        return assemblies

    def _init_pistons(self):
        """Create piston rigs at random ground positions."""
        pistons = []
        for _ in range(random.randint(3, 6)):
            px3 = random.randint(50, self.width - 50)
            py3 = self.height - random.randint(40, 100)
            pistons.append({
                'x':        px3,
                'y':        py3,
                'stroke':   random.randint(20, 60),  # Travel distance
                'phase':    random.uniform(0, math.pi * 2),
                'speed':    random.uniform(0.04, 0.10),
                'cyl_w':    random.randint(12, 24),
                'cyl_h':    random.randint(50, 100),
                'rod_w':    random.randint(5, 9),
            })
        return pistons

    def _new_smoke(self, anchor_x):
        """Dense smoke particle rising from a chimney — starts tight, billows outward."""
        return {
            'x':       float(anchor_x + random.randint(-5, 5)),
            'y':       float(self.height - random.randint(180, 320)),
            'r':       float(random.randint(8, 20)),    # Starts tight at chimney mouth
            'max_r':   float(random.randint(60, 140)),  # Billows large as it rises
            'speed':   random.uniform(0.5, 1.4),
            'drift':   random.uniform(-0.5, 0.5),
            'alpha':   float(random.randint(120, 200)), # Starts dense
            'phase':   random.uniform(0, math.pi * 2),
            'anchor':  anchor_x,
            # Which smoke layer: 0=dark core, 1=mid, 2=edge
            'layer':   random.choice([0, 0, 1, 1, 2]),
        }

    def _new_spark(self, ex, ey):
        """Single welding spark launched from emitter position."""
        angle = random.uniform(-math.pi, -math.pi * 0.1)  # Mostly upward arc
        speed = random.uniform(3.0, 9.0)
        return {
            'x':    float(ex),
            'y':    float(ey),
            'vx':   math.cos(angle) * speed,
            'vy':   math.sin(angle) * speed,
            'life': random.randint(25, 70),
            'max_life': 70,
            'size': random.uniform(1.0, 3.0),
        }

    # ================================================================ #
    #  UPDATE
    # ================================================================ #

    def update(self, camera_speed):
        self.frame_count += 1

        self.scroll_far -= camera_speed * 0.06
        self.scroll_mid -= camera_speed * 0.22
        self.scroll_fg  -= camera_speed * 0.50

        sw = self.width + 600
        if self.scroll_far <= -sw: self.scroll_far = 0
        if self.scroll_mid <= -sw: self.scroll_mid = 0
        if self.scroll_fg  <= -sw: self.scroll_fg  = 0

        # ── Furnace glow pulse ────────────────────────────────────
        self._glow_pulse += 0.022

        # ── Heat haze scroll ──────────────────────────────────────
        self._haze_offset = (self._haze_offset + 0.6) % self.width

        # ── DUMAN SÜTUNLARI — twin-scroll ────────────────────────
        # Her frame sadece y offset güncellenir.
        # Bir kopya üstten çıkınca diğerinin altına eklenir.
        for col in self.smoke_columns:
            col['y1'] -= col['speed']
            col['y2'] -= col['speed']
            # Üstten çıkan kopya diğerinin altına geçer
            if col['y1'] < -col['col_h']:
                col['y1'] = col['y2'] + col['col_h']
            if col['y2'] < -col['col_h']:
                col['y2'] = col['y1'] + col['col_h']

        # Flipbook sayacı (baca ağzı puff animasyonu)
        self._puff_frame = (self._puff_frame + 1) % (len(self._puff_sprites) * 4)

        # ── Gears ─────────────────────────────────────────────────
        for assembly in self.gear_assemblies:
            for g in assembly:
                g['angle'] += g['speed']

        # ── Pistons ───────────────────────────────────────────────
        for p in self.pistons:
            p['phase'] += p['speed']

        # ── Molten sources ────────────────────────────────────────
        for ms in self.molten_sources:
            ms['pulse'] += ms['pulse_spd']

        # ── Spark emitters ────────────────────────────────────────
        for em in self.spark_emitters:
            em['burst_timer'] -= 1
            if em['burst_timer'] <= 0:
                count = random.randint(8, 25)
                for _ in range(count):
                    self.sparks.append(self._new_spark(em['x'], em['y']))
                em['burst_timer'] = em['burst_interval'] + random.randint(-20, 20)

        # ── Spark physics ─────────────────────────────────────────
        alive = []
        for sp in self.sparks:
            sp['x']   += sp['vx']
            sp['y']   += sp['vy']
            sp['vy']  += 0.28          # Gravity
            sp['vx']  *= 0.985         # Air drag
            sp['life'] -= 1
            if sp['life'] > 0:
                alive.append(sp)
        self.sparks = alive

    # ================================================================ #
    #  DRAW HELPERS
    # ================================================================ #

    def _draw_gear(self, surface, cx, cy, r, teeth, angle, color_body, color_tooth):
        """Draw a proper gear: trapezoidal teeth, inner ring, spoke arms, hub."""
        if r < 8:
            return

        # ── Teeth ─────────────────────────────────────────────────
        tooth_h    = max(5, r // 5)
        tooth_w_in = max(3, int(2 * math.pi * r / teeth * 0.45))  # Inner arc width
        for i in range(teeth):
            mid_angle = angle + i * (2 * math.pi / teeth)
            half_gap  = math.pi / teeth * 0.5

            # Four corners of each trapezoidal tooth
            a1 = mid_angle - half_gap * 0.8
            a2 = mid_angle + half_gap * 0.8
            pts = [
                (cx + math.cos(a1) * r,           cy + math.sin(a1) * r),
                (cx + math.cos(a1) * (r+tooth_h), cy + math.sin(a1) * (r+tooth_h)),
                (cx + math.cos(a2) * (r+tooth_h), cy + math.sin(a2) * (r+tooth_h)),
                (cx + math.cos(a2) * r,           cy + math.sin(a2) * r),
            ]
            pygame.draw.polygon(surface, color_tooth, [(int(p[0]), int(p[1])) for p in pts])

        # ── Outer ring (body) ─────────────────────────────────────
        pygame.draw.circle(surface, color_body, (cx, cy), r)

        # ── Inner decorative ring ──────────────────────────────────
        inner_r = max(4, r - r // 4)
        pygame.draw.circle(surface, (color_body[0]+8, color_body[1]+6, color_body[2]+4),
                           (cx, cy), inner_r, 2)

        # ── Spoke arms ────────────────────────────────────────────
        n_spokes = max(3, min(6, teeth // 3))
        spoke_r  = inner_r - 4
        hub_r    = max(4, r // 6)
        for i in range(n_spokes):
            a = angle + i * (2 * math.pi / n_spokes)
            sx2 = cx + int(math.cos(a) * spoke_r)
            sy2 = cy + int(math.sin(a) * spoke_r)
            pygame.draw.line(surface, self.C_METAL_LIGHT, (cx, cy), (sx2, sy2),
                             max(2, r // 14))
            # Lightening hole along spoke
            hole_x = cx + int(math.cos(a) * spoke_r * 0.55)
            hole_y = cy + int(math.sin(a) * spoke_r * 0.55)
            pygame.draw.circle(surface, self.C_SOOT, (hole_x, hole_y), max(2, r // 10))

        # ── Hub ───────────────────────────────────────────────────
        pygame.draw.circle(surface, self.C_METAL_LIGHT, (cx, cy), hub_r)
        pygame.draw.circle(surface, self.C_SOOT,       (cx, cy), hub_r - 2)
        # Keyway slot
        kx = cx + int(math.cos(angle) * (hub_r - 1))
        ky = cy + int(math.sin(angle) * (hub_r - 1))
        pygame.draw.line(surface, self.C_METAL_MID, (cx, cy), (kx, ky), 2)

    def _draw_piston(self, surface, p):
        """Draw a piston rig: cylinder block, rod, connecting arm, crank pin."""
        travel  = math.sin(p['phase']) * p['stroke']
        rod_top = int(p['y'] - p['cyl_h'] + travel)
        cx2     = p['x']
        cyl_w   = p['cyl_w']
        rod_w   = p['rod_w']

        # ── Cylinder block ────────────────────────────────────────
        pygame.draw.rect(surface, self.C_METAL_DARK,
                         (cx2 - cyl_w // 2, p['y'] - p['cyl_h'],
                          cyl_w, p['cyl_h']))
        pygame.draw.rect(surface, self.C_METAL_MID,
                         (cx2 - cyl_w // 2, p['y'] - p['cyl_h'],
                          cyl_w, p['cyl_h']), 1)
        # Port holes on cylinder
        for ph_y in range(p['y'] - p['cyl_h'] + 8, p['y'] - 8, 14):
            pygame.draw.circle(surface, self.C_SOOT, (cx2 + cyl_w // 2 + 2, ph_y), 3)
            pygame.draw.circle(surface, self.C_METAL_LIGHT, (cx2 + cyl_w // 2 + 2, ph_y), 3, 1)

        # ── Piston rod ────────────────────────────────────────────
        pygame.draw.rect(surface, self.C_METAL_LIGHT,
                         (cx2 - rod_w // 2, rod_top, rod_w, p['y'] - rod_top))
        pygame.draw.line(surface, self.C_SOOT,
                         (cx2, rod_top), (cx2, p['y']), 1)  # Centreline scratch

        # ── Piston head ───────────────────────────────────────────
        head_h = cyl_w // 2
        pygame.draw.rect(surface, self.C_METAL_MID,
                         (cx2 - cyl_w // 2 + 2, rod_top - head_h, cyl_w - 4, head_h))
        pygame.draw.line(surface, self.C_MOLTEN_EDGE,
                         (cx2 - cyl_w // 2 + 2, rod_top - head_h + 1),
                         (cx2 + cyl_w // 2 - 2, rod_top - head_h + 1), 1)

        # ── Connecting rod and crank ──────────────────────────────
        crank_r  = p['stroke']
        crank_cy = p['y'] + crank_r // 2
        crank_angle = p['phase']
        pin_x = cx2 + int(math.cos(crank_angle) * crank_r * 0.5)
        pin_y = crank_cy + int(math.sin(crank_angle) * crank_r * 0.5)
        pygame.draw.line(surface, self.C_METAL_MID,
                         (cx2, rod_top), (pin_x, pin_y), rod_w - 1)
        pygame.draw.circle(surface, self.C_METAL_LIGHT, (pin_x, pin_y), 4)
        pygame.draw.circle(surface, self.C_SOOT, (pin_x, pin_y), 2)

    # ================================================================ #
    #  DRAW
    # ================================================================ #

    def draw(self, surface):

        # ── 1. SKY ────────────────────────────────────────────────
        surface.blit(self.sky_surf, (0, 0))

        # ── 2. FURNACE GLOW — pulsing light bloom rising from below ─
        # Multiple glow sources across the bottom, not just one centered circle
        glow_alpha = int(55 + math.sin(self._glow_pulse) * 22)
        self._glow_surf.fill((0, 0, 0, 0))
        for ms in self.molten_sources:
            pulse_offset = math.sin(self._glow_pulse + ms['pulse']) * 15
            for radius, a_mult, col in [
                (int(ms['base_r'] * 14), 0.45, (100, 22,  3)),
                (int(ms['base_r'] *  8), 0.70, (180, 50,  6)),
                (int(ms['base_r'] *  4), 0.90, (230, 90, 10)),
            ]:
                ga = min(255, int((glow_alpha + pulse_offset) * a_mult))
                if radius > 0:
                    pygame.draw.circle(self._glow_surf, (*col, ga),
                                       (ms['x'], self.height + 40), radius)
        surface.blit(self._glow_surf, (0, 0))

        # ── 3. FAR FACTORIES (slowest parallax) ───────────────────
        xf = int(self.scroll_far)
        surface.blit(self.far_factories, (xf, 0))
        surface.blit(self.far_factories, (xf + self.width + 600, 0))

        # ── 4. DUMAN SÜTUNLARI — illüzyon twin-scroll ────────────
        #
        #  İLLÜZYON 1: Kaydırılan doku.
        #    Baca başına 2 blit (twin kopya). Toplam: N_baca × 2 blit.
        #    Parçacık update yok, sorted() yok, Surface yaratma yok.
        #    Göz "yükselen duman" görür; gerçekte tek bir doku kayıyor.
        #
        #  İLLÜZYON 2: Flipbook puff.
        #    Baca ağzında 8 pre-bake sprite döngüsel gösterilir.
        #    "Taze duman çıkıyor" yanılsaması → sıfır yeni Surface.
        #
        puff_idx = (self._puff_frame // 4) % len(self._puff_sprites)
        puff_spr = self._puff_sprites[puff_idx]
        pr       = puff_spr.get_width() // 2

        for col in self.smoke_columns:
            # Ana sütun: iki twin kopya
            cx_draw = col['x'] - col['surf'].get_width() // 2
            if col['y1'] < self.height:
                surface.blit(col['surf'], (cx_draw, int(col['y1'])))
            if col['y2'] < self.height:
                surface.blit(col['surf'], (cx_draw, int(col['y2'])))

            # Baca ağzı puff (baca yüksekliği bilinmiyor; zeminden ~200px yukarıda)
            puff_y = self.height - 220
            surface.blit(puff_spr, (col['x'] - pr, puff_y - pr))

        # ── 5. MID MACHINERY (pipes, vessels, housing silhouettes) ─
        xm = int(self.scroll_mid)
        surface.blit(self.mid_machinery, (xm, 0))
        surface.blit(self.mid_machinery, (xm + self.width + 600, 0))

        # ── 6. ANIMATED GEARS (drawn over housing silhouettes) ────
        for assembly in self.gear_assemblies:
            for g in assembly:
                self._draw_gear(
                    surface,
                    g['cx'], g['cy'], g['r'],
                    g['teeth'], g['angle'],
                    self.C_METAL_DARK, self.C_METAL_MID
                )
                # Furnace-glow rim: if a molten source is nearby, tint the gear warm
                for ms in self.molten_sources:
                    dist = math.hypot(g['cx'] - ms['x'], g['cy'] - ms['y'])
                    if dist < 200:
                        glow_r = g['r'] + g['teeth'] // 5 + 6
                        intensity = int(max(0, (1 - dist / 200) ** 2 * 35))
                        if intensity > 0 and glow_r > 0:
                            rim_surf = pygame.Surface((glow_r * 2, glow_r * 2), pygame.SRCALPHA)
                            pygame.draw.circle(rim_surf, (255, 100, 10, intensity),
                                               (glow_r, glow_r), glow_r, 2)
                            surface.blit(rim_surf, (g['cx'] - glow_r, g['cy'] - glow_r))

        # ── 7. ANIMATED PISTONS ────────────────────────────────────
        for p in self.pistons:
            self._draw_piston(surface, p)

        # ── 8. CATWALKS / SCAFFOLDING (foreground) ─────────────────
        xcw = int(self.scroll_fg)
        surface.blit(self.catwalk_layer, (xcw, 0))
        surface.blit(self.catwalk_layer, (xcw + self.width + 600, 0))

        # ── 9. MOLTEN SOURCES ──────────────────────────────────────
        for ms in self.molten_sources:
            pulse_r = ms['base_r'] + math.sin(ms['pulse']) * ms['base_r'] * 0.18
            cx3, cy3 = int(ms['x']), int(ms['y'])
            # Outer glow halo
            halo_r = int(pulse_r * 3.5)
            if halo_r > 2:
                halo = pygame.Surface((halo_r * 2, halo_r * 2), pygame.SRCALPHA)
                pygame.draw.circle(halo, (*self.C_MOLTEN_EDGE, 40), (halo_r, halo_r), halo_r)
                surface.blit(halo, (cx3 - halo_r, cy3 - halo_r))
            # Mid glow
            mid_r = int(pulse_r * 1.8)
            if mid_r > 2:
                mid_s = pygame.Surface((mid_r * 2, mid_r * 2), pygame.SRCALPHA)
                pygame.draw.circle(mid_s, (*self.C_MOLTEN_MID, 80), (mid_r, mid_r), mid_r)
                surface.blit(mid_s, (cx3 - mid_r, cy3 - mid_r))
            # Bright core
            core_r = max(3, int(pulse_r))
            pygame.draw.circle(surface, self.C_MOLTEN_CORE, (cx3, cy3), core_r)
            # White-hot centre pinpoint
            if core_r > 4:
                pygame.draw.circle(surface, (255, 255, 220), (cx3, cy3), core_r // 3)

        # ── 10. SPARKS ──────────────────────────────────────────────
        for sp in self.sparks:
            life_frac = sp['life'] / sp['max_life']
            # Colour transitions: white-hot → warm orange → cooling red
            if life_frac > 0.6:
                col = self.C_SPARK_HOT
            elif life_frac > 0.3:
                col = self.C_SPARK_WARM
            else:
                col = self.C_SPARK_COOL
            sz = max(1, int(sp['size'] * life_frac))
            ix, iy = int(sp['x']), int(sp['y'])
            if sz >= 2:
                pygame.draw.circle(surface, col, (ix, iy), sz)
            else:
                surface.set_at((ix, iy), col)
            # Motion tail — short line back along velocity
            tail_x = int(sp['x'] - sp['vx'] * 2.5)
            tail_y = int(sp['y'] - sp['vy'] * 2.5)
            tail_col = (col[0] // 2, col[1] // 3, col[2] // 4)
            pygame.draw.line(surface, tail_col, (ix, iy), (tail_x, tail_y), 1)

        # ── 11. HEAT HAZE — actual scanline displacement near ground ─
        # Warp rows of the already-drawn scene upward by a sine offset.
        # Only the bottom 100px are distorted — that's where heat rises from.
        haze_band_top = self.height - 100
        haze_band_h   = 100
        distort_phase = self._haze_offset * 0.05   # Slowly evolving wave

        for row in range(haze_band_h):
            # Intensity: strongest at ground (row=haze_band_h), zero at top
            t      = row / haze_band_h
            mag    = int((1 - t) ** 1.8 * 5)       # Max 5px displacement
            if mag == 0:
                continue
            sy = haze_band_top + row
            if sy < 0 or sy >= self.height:
                continue
            wave   = math.sin(row * 0.25 + distort_phase + self.frame_count * 0.03)
            offset = int(wave * mag)
            if offset == 0:
                continue
            # Read original row and write it shifted
            try:
                row_strip = surface.subsurface((0, sy, self.width, 1)).copy()
                surface.blit(row_strip, (offset, sy))
            except (ValueError, pygame.error):
                pass

        # Colour tint over haze zone — orange heat shimmer
        shimmer_a = int(14 + math.sin(self._glow_pulse * 1.3) * 8)
        for row in range(haze_band_h):
            t = row / haze_band_h
            a = int((1 - t) ** 2 * shimmer_a)
            if a > 0:
                shimmer_line = pygame.Surface((self.width, 1), pygame.SRCALPHA)
                shimmer_line.fill((200, 70, 5, a))
                surface.blit(shimmer_line, (0, haze_band_top + row))

        # ── 12. VIGNETTE ────────────────────────────────────────────
        surface.blit(self.vignette, (0, 0))

class SlumsBackground:
    """
    THE SLUMS (VAROŞLAR)
    Atmosfer: Klostrofobik, Yağmurlu, Neon, Kaotik Kablolar.
    Katmanlar:
      1. Gökyüzü: Şehir ışıklarından kaynaklı kirli mor/lacivert gradient.
      2. Uzak Binalar: Devasa, pencere dolu "Mega-Blok" silüetleri.
      3. Orta Katman: Detaylı gecekondular, klima üniteleri, sarkan kablolar, neon tabelalar.
      4. Yağmur: Sürekli yağan asit yağmuru efekti.
      5. Metro: Arada sırada geçen fütüristik tren.
    """
    def __init__(self, screen_width, screen_height):
        self.width = screen_width
        self.height = screen_height
        self.frame_count = 0
        
        # Parallax Scroll Değerleri
        self.scroll_far = 0.0
        self.scroll_mid = 0.0
        
        # Renk Paleti (Cyberpunk Noir)
        self.C_SKY_TOP = (5, 5, 10)       # Gece Siyahı
        self.C_SKY_BOT = (20, 10, 30)     # Kirli Mor (Işık Kirliliği)
        self.C_BUILDING_FAR = (10, 10, 15)
        self.C_BUILDING_MID = (20, 20, 25)
        self.C_WINDOW_LIT = (200, 200, 150) # Soluk Sarı
        self.C_WINDOW_OFF = (15, 15, 20)
        self.C_NEON_PINK = (255, 0, 128)
        self.C_NEON_CYAN = (0, 255, 255)
        self.C_CABLE = (10, 10, 10)
        self.C_RAIN = (100, 150, 255)

        # Pre-Bake (Önceden Çizilmiş) Katmanlar
        self.sky_surf = self._bake_sky()
        self.far_layer = self._bake_far_layer()
        self.mid_layer = self._bake_mid_layer()
        
        # Dinamik Efektler
        self.rain_drops = []
        for _ in range(150): # Yağmur yoğunluğu
            self.rain_drops.append(self._create_drop())
            
        self.train_x = -2000
        self.train_timer = random.randint(200, 600)

    def _bake_sky(self):
        surf = pygame.Surface((self.width, self.height))
        for y in range(self.height):
            t = y / self.height
            r = int(self.C_SKY_TOP[0] + (self.C_SKY_BOT[0] - self.C_SKY_TOP[0]) * t)
            g = int(self.C_SKY_TOP[1] + (self.C_SKY_BOT[1] - self.C_SKY_TOP[1]) * t)
            b = int(self.C_SKY_TOP[2] + (self.C_SKY_BOT[2] - self.C_SKY_TOP[2]) * t)
            pygame.draw.line(surf, (r, g, b), (0, y), (self.width, y))
        return surf

    def _bake_far_layer(self):
        """Ufuktaki devasa 'Mega-Blok' apartmanlar."""
        w = self.width + 600 # Scroll için geniş alan
        surf = pygame.Surface((w, self.height), pygame.SRCALPHA)
        
        current_x = 0
        while current_x < w:
            bw = random.randint(80, 200)
            bh = random.randint(400, 700) # Çok yüksek binalar
            by = self.height - bh + 50 # Aşağıdan başlasın
            
            # Bina Gövdesi
            pygame.draw.rect(surf, self.C_BUILDING_FAR, (current_x, by, bw, bh))
            
            # Pencereler (Izgara şeklinde)
            rows = bh // 15
            cols = bw // 10
            for r in range(rows):
                for c in range(cols):
                    if random.random() < 0.2: # %20 ışıklar açık
                        wx = current_x + c * 10 + 2
                        wy = by + r * 15 + 2
                        pygame.draw.rect(surf, (*self.C_WINDOW_LIT, 100), (wx, wy, 4, 8))
            
            # Bina tepesindeki kırmızı uyarı ışıkları
            if random.random() < 0.5:
                pygame.draw.line(surf, (200, 0, 0), (current_x + bw//2, by), (current_x + bw//2, by-20), 2)
            
            current_x += bw + random.randint(5, 20)
            
        return surf

    def _bake_mid_layer(self):
        """Yakın binalar, kablolar, tabelalar."""
        w = self.width + 600
        surf = pygame.Surface((w, self.height), pygame.SRCALPHA)
        
        current_x = 0
        prev_roof_right = (0, 0) # Kablo bağlantısı için
        
        while current_x < w:
            bw = random.randint(150, 300)
            bh = random.randint(200, 500)
            by = self.height - bh
            
            # Bina
            pygame.draw.rect(surf, self.C_BUILDING_MID, (current_x, by, bw, bh))
            pygame.draw.rect(surf, (30, 30, 40), (current_x, by, bw, bh), 2) # Çerçeve
            
            # Detaylar: Klima Üniteleri
            for _ in range(random.randint(2, 5)):
                ac_x = current_x - 10 if random.random() < 0.5 else current_x + bw
                ac_y = by + random.randint(20, bh - 50)
                pygame.draw.rect(surf, (40, 40, 50), (ac_x, ac_y, 10, 15))
            
            # Detaylar: Neon Tabelalar (Japonca/Hacker tarzı dikey tabelalar)
            if random.random() < 0.6:
                sign_w = 20
                sign_h = random.randint(60, 120)
                sign_x = current_x + 20
                sign_y = by + 30
                color = random.choice([self.C_NEON_PINK, self.C_NEON_CYAN, (255, 255, 0)])
                
                # Neon Glow
                s_glow = pygame.Surface((sign_w + 20, sign_h + 20), pygame.SRCALPHA)
                pygame.draw.rect(s_glow, (*color, 50), (10, 10, sign_w, sign_h))
                surf.blit(s_glow, (sign_x - 10, sign_y - 10))
                
                # Tabela içi
                pygame.draw.rect(surf, (0,0,0), (sign_x, sign_y, sign_w, sign_h))
                pygame.draw.rect(surf, color, (sign_x, sign_y, sign_w, sign_h), 2)
                # Rastgele çizgiler (Yazı taklidi)
                for i in range(5):
                    ly = sign_y + 10 + i * 15
                    if ly < sign_y + sign_h - 5:
                        pygame.draw.line(surf, color, (sign_x+4, ly), (sign_x+sign_w-4, ly), 2)

            # Detaylar: Kablolar (Binalar arası)
            if current_x > 0:
                start_pos = prev_roof_right
                end_pos = (current_x + 10, by + random.randint(10, 100))
                
                # Bezier/Sarkma efekti (Basit parabol)
                mid_x = (start_pos[0] + end_pos[0]) / 2
                sag = random.randint(20, 60)
                mid_y = (start_pos[1] + end_pos[1]) / 2 + sag
                
                pygame.draw.lines(surf, self.C_CABLE, False, [start_pos, (mid_x, mid_y), end_pos], 2)

            prev_roof_right = (current_x + bw - 10, by + random.randint(10, 50))
            current_x += bw + random.randint(50, 150) # Binalar arası boşluk (sokak)

        return surf

    def _create_drop(self):
        return {
            'x': random.randint(0, self.width),
            'y': random.randint(-100, self.height),
            'speed': random.uniform(15, 25),
            'len': random.randint(10, 30),
            'alpha': random.randint(50, 150)
        }

    def update(self, camera_speed):
        self.frame_count += 1
        
        # Parallax Update
        self.scroll_far -= camera_speed * 0.1
        self.scroll_mid -= camera_speed * 0.5
        
        # Sonsuz Döngü Reset
        bg_w = self.width + 600
        if self.scroll_far <= -bg_w: self.scroll_far += bg_w
        if self.scroll_mid <= -bg_w: self.scroll_mid += bg_w
        
        # Yağmur Update
        for drop in self.rain_drops:
            drop['y'] += drop['speed']
            drop['x'] -= (camera_speed * 0.5) + 2 # Hafif rüzgar etkisi (sola)
            
            if drop['y'] > self.height:
                drop['y'] = random.randint(-50, -10)
                drop['x'] = random.randint(0, self.width + 200)

        # Metro Treni Mantığı (Arkaplanda geçen)
        self.train_timer -= 1
        if self.train_timer <= 0:
            self.train_x = self.width + 100 # Sağdan başla
            self.train_timer = random.randint(600, 1200) # Tekrar gelmesi uzun sürsün
            
        if self.train_x > -1000: # Tren ekrandaysa veya geçiyorsa
            self.train_x -= (camera_speed * 0.2) + 15 # Kameradan hızlı gitsin

    def draw(self, surface):
        # 1. Gökyüzü
        surface.blit(self.sky_surf, (0, 0))
        
        # 2. Uzak Binalar (Mega-Bloklar)
        x_far = int(self.scroll_far)
        surface.blit(self.far_layer, (x_far, 0))
        surface.blit(self.far_layer, (x_far + self.width + 600, 0))
        
        # 3. Metro Treni (Binaların arkasından/arasından geçsin)
        if self.train_x > -1000 and self.train_x < self.width + 200:
            train_y = self.height - 350
            # Tren Gövdesi
            pygame.draw.rect(surface, (10, 10, 20), (self.train_x, train_y, 800, 40))
            # Tren Pencereleri (Hızlı hareket flu etkisi için uzun çizgiler)
            for i in range(10):
                wx = self.train_x + 50 + i * 70
                pygame.draw.rect(surface, (200, 255, 255), (wx, train_y + 10, 50, 15))
            # Tren Işığı (Ön)
            pygame.draw.circle(surface, (255, 255, 200), (int(self.train_x), train_y + 20), 15)
            # Işık hüzmesi
            s_light = pygame.Surface((300, 100), pygame.SRCALPHA)
            pygame.draw.polygon(s_light, (255, 255, 200, 30), [(300, 50), (0, 0), (0, 100)])
            surface.blit(s_light, (self.train_x - 300, train_y - 30))

        # 4. Orta Katman (Gecekondular)
        x_mid = int(self.scroll_mid)
        surface.blit(self.mid_layer, (x_mid, 0))
        surface.blit(self.mid_layer, (x_mid + self.width + 600, 0))
        
        # 5. Yağmur Efekti
        for drop in self.rain_drops:
            start_pos = (drop['x'], drop['y'])
            end_pos = (drop['x'] - 2, drop['y'] + drop['len'])
            
            if drop['x'] > 0 and drop['x'] < self.width:
                pygame.draw.line(surface, (150, 180, 255), start_pos, end_pos, 1)

        # 6. Alt Sis (Yer seviyesi kirliliği)
        s_fog = pygame.Surface((self.width, 150), pygame.SRCALPHA)
        pygame.draw.rect(s_fog, (10, 5, 20, 100), s_fog.get_rect())
        surface.blit(s_fog, (0, self.height - 150))
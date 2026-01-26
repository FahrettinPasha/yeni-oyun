import pygame
import random
import math
from settings import LOGICAL_HEIGHT, LOGICAL_WIDTH

# Boss Sabitleri
BULLET_SPEED = 8
BOSS_HEALTH = 1000
BOSS_DAMAGE = 10
BOSS_FIRE_RATE = 60
BOSS_INVULNERABILITY_TIME = 30

# --- BOSS SALDIRI NESNELERİ ---

class BossSpike(pygame.sprite.Sprite):
    def __init__(self, platform, karma):
        super().__init__()
        self.platform = platform
        self.karma = karma
        
        margin = 5
        self.width = platform.width - (margin * 2)
        self.height = 130 
        
        self.x = platform.rect.left + margin
        self.y = platform.rect.top - self.height
        
        self.rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        self.timer = 0
        self.warning_duration = 25
        self.active_duration = 30
        self.state = 'WARNING' 
        
    def update(self, camera_speed):
        self.rect.x -= camera_speed
        self.x -= camera_speed
        
        self.timer += 1
        
        if self.state == 'WARNING':
            if self.timer >= self.warning_duration:
                self.state = 'ACTIVE'
                self.timer = 0 
        elif self.state == 'ACTIVE':
            if self.timer >= self.active_duration:
                self.state = 'DONE'
                self.kill() 
    
    def draw(self, surface):
        if self.state == 'WARNING':
            if (self.timer // 4) % 2 == 0:
                warn_color = (0, 255, 255) if self.karma < 0 else (200, 0, 255)
                pygame.draw.rect(surface, warn_color, (self.rect.x, self.rect.bottom - 5, self.width, 5))
                arrow_count = max(1, self.width // 50)
                for i in range(arrow_count):
                    ax = self.rect.x + (i * 50) + 25
                    ay = self.rect.bottom - 15
                    points = [(ax, ay - 10), (ax - 5, ay), (ax + 5, ay)]
                    pygame.draw.polygon(surface, warn_color, points)

        elif self.state == 'ACTIVE':
            progress = min(1.0, self.timer / 4.0)
            current_h = int(self.height * progress)
            base_y = self.rect.bottom 
            top_y = base_y - current_h
            
            arrow_spacing = 30
            num_arrows = int(self.width // arrow_spacing)
            
            for i in range(num_arrows):
                arrow_x = self.rect.x + (i * arrow_spacing) + (arrow_spacing // 2)
                
                if self.karma < 0:
                    COLOR_SHAFT = (0, 100, 150)
                    COLOR_HEAD = (0, 255, 255)
                    COLOR_GLOW = (200, 255, 255)
                    pygame.draw.line(surface, COLOR_SHAFT, (arrow_x, base_y), (arrow_x, top_y + 15), 3)
                    head_points = [(arrow_x, top_y), (arrow_x - 6, top_y + 20), (arrow_x, top_y + 15), (arrow_x + 6, top_y + 20)]
                    pygame.draw.polygon(surface, COLOR_HEAD, head_points)
                    pygame.draw.polygon(surface, COLOR_GLOW, head_points, 1)
                else:
                    COLOR_SHAFT = (50, 0, 50)
                    COLOR_HEAD = (180, 0, 255)
                    COLOR_GLITCH = (255, 0, 255)
                    off_x = random.randint(-2, 2)
                    pygame.draw.line(surface, COLOR_SHAFT, (arrow_x + off_x, base_y), (arrow_x + off_x, top_y + 15), 4)
                    head_points = [(arrow_x + off_x, top_y), (arrow_x - 7 + off_x, top_y + 25), (arrow_x + 7 + off_x, top_y + 25)]
                    pygame.draw.polygon(surface, COLOR_HEAD, head_points)
                    if random.random() < 0.3:
                        gy = random.randint(top_y, base_y)
                        pygame.draw.line(surface, COLOR_GLITCH, (arrow_x - 10, gy), (arrow_x + 10, gy), 1)

class BossLightning(pygame.sprite.Sprite):
    def __init__(self, x, karma):
        super().__init__()
        self.x = x
        self.karma = karma
        self.width = 60
        self.height = LOGICAL_HEIGHT
        self.rect = pygame.Rect(self.x - self.width//2, 0, self.width, self.height)
        self.timer = 0
        self.warning_duration = 30
        self.active_duration = 10
        self.state = 'WARNING'
        
    def update(self, camera_speed):
        self.x -= camera_speed
        self.rect.x -= camera_speed
        self.timer += 1
        
        if self.state == 'WARNING':
            if self.timer >= self.warning_duration:
                self.state = 'ACTIVE'
                self.timer = 0
        elif self.state == 'ACTIVE':
            if self.timer >= self.active_duration:
                self.state = 'DONE'
                self.kill()
                
    def draw(self, surface):
        if self.state == 'WARNING':
            if (self.timer // 5) % 2 == 0:
                warn_col = (0, 255, 255) if self.karma < 0 else (200, 0, 255)
                pygame.draw.line(surface, (*warn_col, 100), (self.x, 0), (self.x, LOGICAL_HEIGHT), 1)
                target_rect = pygame.Rect(self.x - 20, LOGICAL_HEIGHT - 60, 40, 20)
                pygame.draw.ellipse(surface, warn_col, target_rect, 2)
                font = pygame.font.Font(None, 30)
                txt = font.render("!", True, warn_col)
                surface.blit(txt, (self.x - 5, 50))
        elif self.state == 'ACTIVE':
            if self.karma < 0:
                core_col = (200, 255, 255)
                outer_col = (0, 200, 255)
                points = []
                segments = 10
                for i in range(segments + 1):
                    px = self.x + random.randint(-20, 20)
                    py = (LOGICAL_HEIGHT / segments) * i
                    points.append((px, py))
                if len(points) > 1:
                    pygame.draw.lines(surface, outer_col, False, points, 15)
                    pygame.draw.lines(surface, core_col, False, points, 5)
            else:
                core_col = (255, 200, 255)
                outer_col = (150, 0, 255)
                for i in range(0, LOGICAL_HEIGHT, 40):
                    off_x = random.randint(-30, 30)
                    rect_w = random.randint(10, 40)
                    rect_h = random.randint(40, 80)
                    r = pygame.Rect(self.x + off_x - rect_w//2, i, rect_w, rect_h)
                    pygame.draw.rect(surface, outer_col, r)
                    pygame.draw.rect(surface, core_col, r.inflate(-10, -10))

class BossGiantArrow(pygame.sprite.Sprite):
    def __init__(self, x, karma):
        super().__init__()
        self.x = x
        self.karma = karma
        self.width = 150
        self.height = 400
        self.rect = pygame.Rect(x, LOGICAL_HEIGHT, self.width, self.height)
        self.timer = 0
        self.warning_duration = 45
        self.active_duration = 20
        self.state = 'WARNING'
        
    def update(self, camera_speed):
        self.x -= camera_speed
        self.rect.x -= camera_speed
        self.timer += 1
        
        if self.state == 'WARNING':
            if self.timer >= self.warning_duration:
                self.state = 'ACTIVE'
                self.timer = 0
        elif self.state == 'ACTIVE':
            if self.timer >= self.active_duration:
                self.state = 'DONE'
                self.kill()

    def draw(self, surface):
        if self.state == 'WARNING':
            if (self.timer // 10) % 2 == 0:
                col = (255, 0, 0) if self.karma < 0 else (150, 0, 255)
                s = pygame.Surface((self.width, LOGICAL_HEIGHT), pygame.SRCALPHA)
                s.fill((*col, 50))
                surface.blit(s, (self.rect.x, 0))
                pygame.draw.rect(surface, col, (self.rect.x, LOGICAL_HEIGHT - 20, self.width, 20))
                font = pygame.font.Font(None, 60)
                txt = font.render("☠", True, col)
                surface.blit(txt, (self.rect.centerx - 15, LOGICAL_HEIGHT - 80))
        elif self.state == 'ACTIVE':
            progress = min(1.0, self.timer / 5.0)
            h = int(LOGICAL_HEIGHT * progress)
            draw_rect = pygame.Rect(self.rect.x, LOGICAL_HEIGHT - h, self.width, h)
            if self.karma < 0: 
                color = (0, 255, 255)
                pygame.draw.polygon(surface, color, [(draw_rect.left, draw_rect.bottom), (draw_rect.centerx, draw_rect.top), (draw_rect.right, draw_rect.bottom)])
                pygame.draw.line(surface, (255, 255, 255), (draw_rect.centerx, draw_rect.bottom), (draw_rect.centerx, draw_rect.top), 10)
            else:
                color = (180, 0, 255)
                pygame.draw.rect(surface, color, draw_rect)
                for _ in range(5):
                    bx = random.randint(draw_rect.left, draw_rect.right)
                    by = random.randint(draw_rect.top, draw_rect.bottom)
                    pygame.draw.rect(surface, (0,0,0), (bx, by, 20, 20))

class BossOrbitalStrike(pygame.sprite.Sprite):
    def __init__(self, x, y, karma):
        super().__init__()
        self.x = x
        self.y = y
        self.karma = karma
        self.timer = 0
        self.radius = 0
        self.max_radius = 300
        self.state = 'CHARGING'
        self.beams = []
        
    def update(self, camera_speed):
        self.x -= camera_speed
        self.timer += 1
        
        if self.state == 'CHARGING':
            if self.timer < 60:
                self.radius = (self.timer / 60) * 40
            else:
                self.state = 'BLAST'
                self.timer = 0
                for _ in range(random.randint(5, 8)):
                    offset = random.randint(-self.max_radius, self.max_radius)
                    self.beams.append(self.x + offset)
        elif self.state == 'BLAST':
            if self.timer > 20:
                self.kill()
                
    def draw(self, surface):
        col = (0, 255, 255) if self.karma < 0 else (255, 0, 255)
        if self.state == 'CHARGING':
            pygame.draw.circle(surface, col, (int(self.x), int(self.y)), int(self.radius))
            pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), int(self.radius * 0.5))
            target_rect = pygame.Rect(self.x - self.max_radius, LOGICAL_HEIGHT - 20, self.max_radius*2, 20)
            pygame.draw.ellipse(surface, (*col, 100), target_rect, 2)
        elif self.state == 'BLAST':
            pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), 60)
            for bx in self.beams:
                pygame.draw.line(surface, col, (self.x, self.y), (bx, LOGICAL_HEIGHT), 5)
                pygame.draw.circle(surface, col, (bx, LOGICAL_HEIGHT), 30)

    def check_collision(self, player_rect):
        if self.state == 'BLAST':
            for bx in self.beams:
                beam_rect = pygame.Rect(bx - 20, 0, 40, LOGICAL_HEIGHT)
                if beam_rect.colliderect(player_rect):
                    return True
        return False

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
        bar_width = 200
        bar_height = 20
        bar_x = self.x - bar_width // 2
        bar_y = self.y - 60
        pygame.draw.rect(surface, (255,0,0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, (0,255,0), (bar_x, bar_y, bar_width * (self.health / self.max_health), bar_height))
        color = (255, 0, 0) if self.invulnerable_timer > 0 else (255, 100, 100)
        pygame.draw.circle(surface, color, (int(self.x), int(self.y)), 40)
        pygame.draw.circle(surface, (255, 200, 200), (int(self.x), int(self.y)), 40, 4)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x - 15), int(self.y - 10)), 10)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x + 15), int(self.y - 10)), 10)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x - 15), int(self.y - 10)), 5)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x + 15), int(self.y - 10)), 5)

    def take_damage(self, damage):
        if self.invulnerable_timer <= 0:
            self.health -= damage
            self.invulnerable_timer = BOSS_INVULNERABILITY_TIME
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
        bar_width = 200
        bar_height = 20
        bar_x = self.x - bar_width // 2
        bar_y = self.y - 60
        pygame.draw.rect(surface, (255,0,0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, (0,255,0), (bar_x, bar_y, bar_width * (self.health / self.max_health), bar_height))
        color = (255, 0, 0) if self.invulnerable_timer > 0 else (200, 50, 50)
        pygame.draw.rect(surface, color, (int(self.x-50), int(self.y-50), 100, 100))
        pygame.draw.rect(surface, (255, 200, 200), (int(self.x-50), int(self.y-50), 100, 100), 4)

    def take_damage(self, damage):
        if self.invulnerable_timer <= 0:
            self.health -= damage
            self.invulnerable_timer = BOSS_INVULNERABILITY_TIME
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
        bar_width = 200
        bar_height = 20
        bar_x = self.x - bar_width // 2
        bar_y = self.y - 60
        pygame.draw.rect(surface, (255,0,0), (bar_x, bar_y, bar_width, bar_height))
        pygame.draw.rect(surface, (0,255,0), (bar_x, bar_y, bar_width * (self.health / self.max_health), bar_height))
        color = (255, 0, 0) if self.invulnerable_timer > 0 else (100, 50, 255)
        points = [(self.x, self.y-50), (self.x-50, self.y+50), (self.x+50, self.y+50)]
        pygame.draw.polygon(surface, color, points)
        pygame.draw.polygon(surface, (200, 200, 255), points, 4)

    def take_damage(self, damage):
        if self.invulnerable_timer <= 0:
            self.health -= damage
            self.invulnerable_timer = BOSS_INVULNERABILITY_TIME
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
        if self.x < -100 or self.x > LOGICAL_WIDTH + 100 or self.y < -100 or self.y > LOGICAL_HEIGHT + 100:
            self.kill()

    def draw(self, surface, theme):
        pygame.draw.circle(surface, (255, 0, 0), (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (255, 255, 0), (int(self.x), int(self.y)), self.radius - 3)
class VasilCompanion(pygame.sprite.Sprite):
    """Oyuncuyu takip eden ve düşmanları yok eden Mini-Vasi"""
    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.target_x = x
        self.target_y = y
        self.float_offset = 0.0
        
        # Saldırı Zamanlayıcıları
        self.laser_timer = 0
        self.spike_timer = 0
        self.shield_timer = 0
        
        # Görsel
        self.size = 20 # Oyuncuyla aynı boyutta (biraz küçük)
        self.color = (0, 255, 100) # Matrix Yeşili
        self.eye_color = (255, 0, 0) # Kırmızı Göz (Kötücül mod)

    def update(self, player_x, player_y, all_enemies, boss_manager_system, camera_speed):
        # 1. Takip Hareketi (Süzülerek)
        # Oyuncunun sol üstünde duracak
        target_dest_x = player_x - 40
        target_dest_y = player_y - 40
        
        # Yumuşak geçiş (Lerp)
        self.x += (target_dest_x - self.x) * 0.1
        self.y += (target_dest_y - self.y) * 0.1
        
        # Süzülme efekti
        self.float_offset += 0.1
        draw_y = self.y + math.sin(self.float_offset) * 5
        
        # 2. Lazer Saldırısı (Sık sık)
        self.laser_timer += 1
        if self.laser_timer > 30: # Saniyede 2 kez
            # En yakın düşmanı bul
            nearest_enemy = None
            min_dist = 400 # Menzil
            
            for enemy in all_enemies:
                # Mermileri hedef alma
                if isinstance(enemy, EnemyBullet): continue
                
                dist = math.sqrt((enemy.rect.centerx - self.x)**2 + (enemy.rect.centery - draw_y)**2)
                if dist < min_dist:
                    min_dist = dist
                    nearest_enemy = enemy
            
            if nearest_enemy:
                self.laser_timer = 0
                return ("LASER", nearest_enemy) # Main.py'de işlenecek

        # 3. Kazık Saldırısı (Nadir - Karma -250 altındaysa)
        # Bunu main.py içinde karma kontrolüyle tetikleyeceğiz
        
        return None

    def draw(self, surface):
        # Süzülme hareketi
        draw_y = self.y + math.sin(self.float_offset) * 5
        cx, cy = int(self.x), int(draw_y)
        
        # --- CUTSCENE TARZI DİJİTAL GÖZ EFEKTİ ---
        
        # Renkler (Soykırım Modu olduğu için Kırmızı/Siyah ağırlıklı olabilir veya Vasi yeşili)
        # Vasi normalde Yeşil ama "Soykırım" modunda oyuncuya yardım ederken Kırmızılaşabilir.
        # İsteğine göre: Yeşil (0, 255, 100) veya Kırmızı (255, 50, 50)
        MAIN_COLOR = (0, 255, 100) 
        DARK_COLOR = (0, 50, 20)
        WHITE = (255, 255, 255)
        
        size = 15 # Küçültülmüş boyut
        
        # 1. Dönen Kare Çerçeveler (HUD Efekti)
        t = pygame.time.get_ticks() * 0.002
        rect_size = size * 3.5
        rect = pygame.Rect(0, 0, rect_size, rect_size)
        rect.center = (cx, cy)
        
        rot_offset = math.sin(t) * 5
        
        # Çerçeve Köşeleri
        corner_len = 10
        # Sol Üst
        pygame.draw.line(surface, MAIN_COLOR, (rect.left - rot_offset, rect.top), (rect.left + corner_len, rect.top), 2)
        pygame.draw.line(surface, MAIN_COLOR, (rect.left - rot_offset, rect.top), (rect.left - rot_offset, rect.top + corner_len), 2)
        # Sağ Alt
        pygame.draw.line(surface, MAIN_COLOR, (rect.right + rot_offset, rect.bottom), (rect.right - corner_len, rect.bottom), 2)
        pygame.draw.line(surface, MAIN_COLOR, (rect.right + rot_offset, rect.bottom), (rect.right + rot_offset, rect.bottom - corner_len), 2)

        # 2. İris (Ana Göz)
        pygame.draw.circle(surface, DARK_COLOR, (cx, cy), size + 2) 
        pygame.draw.circle(surface, MAIN_COLOR, (cx, cy), size + 2, 2) # Dış halka
        
        # İç halkalar (Teknoloji hissi)
        pygame.draw.circle(surface, (*MAIN_COLOR, 150), (cx, cy), int(size * 0.6), 1)
        
        # 3. Göz Bebeği (Elmas Şekli) - Oyuncunun baktığı yöne baksın
        # Basitçe sürekli dönsün veya sağa baksın
        pupil_x = cx + math.cos(t * 2) * 3
        pupil_y = cy + math.sin(t * 3) * 2
        
        pupil_points = [
            (pupil_x, pupil_y - 6),
            (pupil_x + 4, pupil_y),
            (pupil_x, pupil_y + 6),
            (pupil_x - 4, pupil_y)
        ]
        pygame.draw.polygon(surface, MAIN_COLOR, pupil_points)
        pygame.draw.circle(surface, WHITE, (pupil_x, pupil_y), 2) # Parlama

        # 4. Tarama Çizgisi (Scanline)
        scan_y = cy + math.sin(t * 5) * size
        pygame.draw.line(surface, (*MAIN_COLOR, 100), (cx - size, scan_y), (cx + size, scan_y), 1)
               
        # Dış Halka (Dönen)
        t = pygame.time.get_ticks() * 0.005
        for i in range(3):
            angle = t + (i * 2.09)
            ox = math.cos(angle) * 25
            oy = math.sin(angle) * 25
            pygame.draw.circle(surface, self.color, (int(cx + ox), int(cy + oy)), 3)
            # Bağlantı çizgileri
            pygame.draw.line(surface, (*self.color, 100), (cx, cy), (int(cx+ox), int(cy+oy)), 1)

        # Ana Gövde (Üçgen Piramit)
        points = [
            (cx, cy - 15),
            (cx - 12, cy + 10),
            (cx + 12, cy + 10)
        ]
        pygame.draw.polygon(surface, (20, 30, 20), points) # İç renk
        pygame.draw.polygon(surface, self.color, points, 2) # Çerçeve
        
        # Göz (Kırmızı)
        pygame.draw.circle(surface, self.eye_color, (cx, cy), 5)        
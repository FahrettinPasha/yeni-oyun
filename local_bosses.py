import pygame
import math
from settings import LOGICAL_WIDTH, LOGICAL_HEIGHT
from game_config import BULLET_SPEED, BOSS_HEALTH, BOSS_DAMAGE, BOSS_FIRE_RATE, BOSS_INVULNERABILITY_TIME
from vfx import Shockwave

# --- YEREL BOSS SINIFLARI ---

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
        if not getattr(self, 'ignore_camera_speed', False):
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
        # Burada global değişkeni değiştirmek yerine instance değişkeni kullanmak daha iyi olurdu ama
        # orijinal mantığı bozmamak adına şimdilik pas geçiyoruz.
        # Not: Bu sadece main.py'deki global'i etkilemez, bu modüldeki sabiti etkiler.
        pass

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

    def take_damage(self, damage, vfx_group=None):
        """
        Hasar alma fonksiyonu.
        vfx_group: Efektlerin ekleneceği grup (main.py'den all_vfx gönderilmeli).
        """
        if self.invulnerable_timer <= 0:
            self.health -= damage
            self.invulnerable_timer = BOSS_INVULNERABILITY_TIME
            if vfx_group is not None:
                vfx_group.add(Shockwave(self.x, self.y, (255,0,0), max_radius=60, width=3, speed=10))
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
        if not getattr(self, 'ignore_camera_speed', False):
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
        pass

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

    def take_damage(self, damage, vfx_group=None):
        if self.invulnerable_timer <= 0:
            self.health -= damage
            self.invulnerable_timer = BOSS_INVULNERABILITY_TIME
            if vfx_group is not None:
                vfx_group.add(Shockwave(self.x, self.y, (255,0,0), max_radius=60, width=3, speed=10))
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
        if not getattr(self, 'ignore_camera_speed', False):
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
        pass

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

    def take_damage(self, damage, vfx_group=None):
        if self.invulnerable_timer <= 0:
            self.health -= damage
            self.invulnerable_timer = BOSS_INVULNERABILITY_TIME
            if vfx_group is not None:
                vfx_group.add(Shockwave(self.x, self.y, (255,0,0), max_radius=60, width=3, speed=10))
            if self.health <= 0:
                self.kill()
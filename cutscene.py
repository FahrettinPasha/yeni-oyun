"""
cutscene.py
ULTIMATE Cyberpunk/AI Cutscene for Fragmentia
DÜZELTME: Eksik olan draw_cyber_revolver fonksiyonu eklendi.
"""

import pygame
import random
import math
import sys

# --- RENK PALETİ ---
CYBER_GREEN = (0, 255, 100)
CYBER_DARK = (0, 20, 10)
HACKER_GREEN = (50, 255, 50)
ALERT_RED = (255, 50, 50)
PURE_WHITE = (255, 255, 255)
PURE_BLACK = (0, 0, 0)
DATA_BLUE = (0, 200, 255)
WARNING_YELLOW = (255, 200, 0)

# --- EKSİK OLAN FONKSİYON BURAYA EKLENDİ ---
def draw_cyber_revolver(surface, x, y, color, scale=1.0):
    """
    Eksik olan Cyber Revolver çizim fonksiyonu.
    Verilen koordinatta (x,y) neon hatlı bir silah çizer.
    """
    # Ölçeklendirme yardımcısı
    def s(val): return int(val * scale)
    
    # 1. Kabza (Handle)
    handle_points = [
        (x - s(30), y + s(10)),
        (x - s(10), y + s(10)),
        (x + s(5), y + s(50)),
        (x - s(35), y + s(50))
    ]
    pygame.draw.polygon(surface, (30, 30, 40), handle_points) # İç Dolgu
    pygame.draw.polygon(surface, color, handle_points, 2)     # Neon Çerçeve

    # 2. Tetik Korkuluğu
    pygame.draw.lines(surface, color, False, [
        (x - s(5), y + s(20)), 
        (x + s(10), y + s(40)), 
        (x + s(25), y + s(20))
    ], 2)

    # 3. Ana Gövde (Body)
    body_rect = pygame.Rect(x - s(30), y - s(20), s(70), s(35))
    pygame.draw.rect(surface, (20, 20, 30), body_rect)
    pygame.draw.rect(surface, color, body_rect, 2)

    # 4. Namlu (Barrel) - Uzun kısım
    barrel_rect = pygame.Rect(x + s(40), y - s(15), s(60), s(20))
    pygame.draw.rect(surface, (40, 40, 50), barrel_rect)
    pygame.draw.rect(surface, color, barrel_rect, 2)
    
    # Namlu ucu parlaması
    pygame.draw.line(surface, color, (x + s(40), y), (x + s(100), y), 1)

    # 5. Silindir (Cylinder/Top)
    cylinder_rect = pygame.Rect(x - s(5), y - s(18), s(35), s(30))
    pygame.draw.ellipse(surface, (60, 60, 70), cylinder_rect)
    pygame.draw.ellipse(surface, color, cylinder_rect, 2)
    
    # Detay çizgileri (Hacker teması)
    pygame.draw.line(surface, color, (x - s(30), y - s(5)), (x + s(100), y - s(5)), 1)


class MatrixRain:
    """Matrix tarzı akan kod efekti"""
    def __init__(self, width, height, font_size=20):
        self.width = width
        self.height = height
        self.font_size = font_size
        self.cols = width // font_size
        self.drops = [random.randint(-50, 0) for _ in range(self.cols)]
        self.chars = ["0", "1", "X", "Z", "A", "Ω", "Σ", "π", "¥", "$", "∆", "∇"]
        self.speed_mult = 1.0

    def update(self):
        for i in range(len(self.drops)):
            self.drops[i] += 1 * self.speed_mult
            if self.drops[i] * self.font_size > self.height and random.random() > 0.975:
                self.drops[i] = 0

    def draw(self, surface, font, color=HACKER_GREEN):
        for i in range(len(self.drops)):
            char = random.choice(self.chars)
            x = i * self.font_size
            y = int(self.drops[i] * self.font_size)
            
            char_surf = font.render(char, True, color)
            surface.blit(char_surf, (x, y))
            
            if y > self.font_size * 2:
                tail_color = (0, 100, 0) if color == HACKER_GREEN else (100, 0, 0)
                tail_surf = font.render(char, True, tail_color)
                surface.blit(tail_surf, (x, y - self.font_size))

class CRTOverlay:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.scanline_surf = pygame.Surface((width, height), pygame.SRCALPHA)
        self.create_scanlines()
        self.vignette_surf = self.create_vignette()

    def create_scanlines(self):
        for y in range(0, self.height, 3):
            pygame.draw.line(self.scanline_surf, (0, 0, 0, 50), (0, y), (self.width, y), 1)

    def create_vignette(self):
        surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.rect(surf, (0,0,0,0), surf.get_rect()) 
        pygame.draw.rect(surf, (0,0,0,180), (0,0, self.width, 100))
        pygame.draw.rect(surf, (0,0,0,180), (0, self.height-100, self.width, 100))
        pygame.draw.rect(surf, (0,0,0,180), (0,0, 100, self.height))
        pygame.draw.rect(surf, (0,0,0,180), (self.width-100, 0, 100, self.height))
        return surf

    def draw(self, surface):
        surface.blit(self.scanline_surf, (0, 0))
        surface.blit(self.vignette_surf, (0, 0))

class HexDumpView:
    def __init__(self, width, height, font):
        self.width = width
        self.height = height
        self.font = font
        self.lines = []
        self.max_lines = 25
        self.timer = 0

    def update(self, dt):
        self.timer += dt
        if self.timer > 0.05:
            self.timer = 0
            addr = f"0x{random.randint(0, 0xFFFFFF):06X}"
            data = " ".join([f"{random.randint(0, 255):02X}" for _ in range(8)])
            ascii_rep = "".join([random.choice("..*!?#") for _ in range(8)])
            self.lines.append(f"{addr}  {data}  |{ascii_rep}|")
            if len(self.lines) > self.max_lines:
                self.lines.pop(0)

    def draw(self, surface, x, y, color=DATA_BLUE):
        for i, line in enumerate(self.lines):
            text = self.font.render(line, True, color)
            surface.blit(text, (x, y + i * 20))

class LoadingBar:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.progress = 0.0
        self.target = 1.0
        self.message = "SYSTEM_CHECK"

    def set_progress(self, val, msg=""):
        self.target = val
        if msg: self.message = msg

    def update(self, dt):
        if self.progress < self.target:
            self.progress += dt * 0.5
        else:
            self.progress = self.target

    def draw(self, surface, x, y):
        pygame.draw.rect(surface, (20, 30, 40), (x, y, self.width, self.height))
        pygame.draw.rect(surface, CYBER_GREEN, (x, y, self.width, self.height), 2)
        
        fill_w = int(self.width * self.progress)
        if fill_w > 0:
            for i in range(0, fill_w, 15):
                block_w = min(10, fill_w - i)
                pygame.draw.rect(surface, CYBER_GREEN, (x + i + 2, y + 4, block_w, self.height - 8))

        font = pygame.font.SysFont("consolas", 20)
        msg_surf = font.render(f"{self.message}... {int(self.progress*100)}%", True, PURE_WHITE)
        surface.blit(msg_surf, (x, y - 25))

class DigitalEye:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.pupil_offset = [0, 0]
        self.blink_timer = 0
        self.is_blinking = False
        self.scanning = False
        self.scan_angle = 0

    def update(self, dt):
        if random.random() < 0.05:
            self.pupil_offset = [random.randint(-3, 3), random.randint(-3, 3)]
        
        self.blink_timer -= dt
        if self.blink_timer <= 0:
            self.is_blinking = True
            if self.blink_timer <= -0.15:
                self.is_blinking = False
                self.blink_timer = random.uniform(2.0, 6.0)
        
        if self.scanning:
            self.scan_angle += dt * 5

    def draw(self, surface, color, intensity=1.0):
        r, g, b = color
        bright_color = (min(255, int(r*intensity)), min(255, int(g*intensity)), min(255, int(b*intensity)))
        
        rect_size = self.size * 2.5
        rect = pygame.Rect(0, 0, rect_size, rect_size)
        rect.center = (self.x, self.y)
        
        pygame.draw.rect(surface, (20, 20, 20), rect, 1)
        
        corner_len = 30
        pygame.draw.line(surface, bright_color, (rect.left, rect.top), (rect.left + corner_len, rect.top), 2)
        pygame.draw.line(surface, bright_color, (rect.left, rect.top), (rect.left, rect.top + corner_len), 2)
        pygame.draw.line(surface, bright_color, (rect.right, rect.bottom), (rect.right - corner_len, rect.bottom), 2)
        pygame.draw.line(surface, bright_color, (rect.right, rect.bottom), (rect.right + corner_len, rect.bottom), 2)

        if self.is_blinking:
            pygame.draw.line(surface, bright_color, (self.x - 40, self.y), (self.x + 40, self.y), 3)
            return

        pygame.draw.circle(surface, (5, 10, 5), (self.x, self.y), self.size) 
        pygame.draw.circle(surface, bright_color, (self.x, self.y), self.size, 2)
        
        if self.scanning:
            scan_x = self.x + math.cos(self.scan_angle) * self.size
            scan_y = self.y + math.sin(self.scan_angle) * self.size
            pygame.draw.line(surface, (0, 255, 0), (self.x, self.y), (scan_x, scan_y), 1)

        pupil_x = self.x + self.pupil_offset[0]
        pupil_y = self.y + self.pupil_offset[1]
        points = [
            (pupil_x, pupil_y - 10),
            (pupil_x + 6, pupil_y),
            (pupil_x, pupil_y + 10),
            (pupil_x - 6, pupil_y)
        ]
        pygame.draw.polygon(surface, bright_color, points)
        pygame.draw.circle(surface, PURE_WHITE, (pupil_x - 2, pupil_y - 2), 2)
        
    def draw_warrior(self, surface, x, y, intensity=1.0):
        GOLD = (255, 215, 0)
        HERO_BLUE = (0, 191, 255)
        WHITE = (255, 255, 255)
        
        t = pygame.time.get_ticks() / 1000.0
        for i in range(3):
            radius = self.size * (1.5 + i * 0.3) + math.sin(t * 2) * 5
            alpha = int(100 / (i + 1))
            pygame.draw.circle(surface, (*GOLD, alpha), (x, y), int(radius), 1)

        points = [
            (x, y - self.size * 1.2),
            (x - self.size * 0.8, y - self.size * 0.2),
            (x - self.size * 0.6, y + self.size),
            (x, y + self.size * 1.4),
            (x + self.size * 0.6, y + self.size),
            (x + self.size * 0.8, y - self.size * 0.2)
        ]
        
        poly_surf = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        pygame.draw.polygon(poly_surf, (*GOLD, 50), points)
        pygame.draw.polygon(poly_surf, GOLD, points, 3)
        
        visor_rect = pygame.Rect(x - self.size * 0.4, y - 10, self.size * 0.8, 20)
        pygame.draw.rect(poly_surf, HERO_BLUE, visor_rect, border_radius=5)
        
        pygame.draw.line(poly_surf, WHITE, (x - self.size, y), (x + self.size, y), 2)
        pygame.draw.line(poly_surf, WHITE, (x, y - self.size), (x, y + self.size), 10)

        surface.blit(poly_surf, (0,0))

class AICutscene:
    def __init__(self, screen, clock, asset_paths=None):
        self.screen = screen
        self.clock = clock
        self.width, self.height = screen.get_size()
        self.asset_paths = asset_paths if asset_paths else {}
        self.running = True

        try:
            self.font_main = pygame.font.SysFont("consolas", 24)
            self.font_large = pygame.font.SysFont("consolas", 60, bold=True)
            self.font_matrix = pygame.font.SysFont("consolas", 16)
            self.font_bios = pygame.font.SysFont("lucidaconsole", 18)
        except:
            self.font_main = pygame.font.Font(None, 32)
            self.font_large = pygame.font.Font(None, 48)
            self.font_matrix = pygame.font.Font(None, 20)
            self.font_bios = pygame.font.Font(None, 20)

        self.matrix_rain = MatrixRain(self.width, self.height, 16)
        self.crt_effect = CRTOverlay(self.width, self.height)
        self.digital_eye = DigitalEye(self.width // 2, self.height // 2 - 80, 70)
        self.hexdump = HexDumpView(self.width, self.height, self.font_matrix)
        self.loading_bar = LoadingBar(600, 30)

        self.sounds = {}
        self.load_sounds()

        self.time_elapsed = 0
        self.text_timer = 0
        self.char_index = 0
        self.current_text = ""
        self.display_text = ""
        self.speaker = ""
        self.bg_color = PURE_BLACK
        
        self.scenario_type = asset_paths.get('scenario', 'INTRO')
        
        # 1. INTRO
        timeline_intro = [
            {"time": 0.5, "type": "BIOS", "text": "BIOS DATE 2099/13/32 18:04:22 VER 9.1"},
            {"time": 2.5, "type": "BIOS", "text": "MEM: 128 YB DETECTED... OK"},
            {"time": 4.5, "type": "HEX_DUMP", "text": "CRITICAL DATA LEAK DETECTED"},
            {"time": 6.0, "type": "LOADING", "text": "FRAGMENTIA OS v4.0", "load_val": 0.5},
            {"time": 8.0, "type": "EYE_WAKE", "text": "BAĞLANTI KURULDU.", "speaker": "SİSTEM"},
            {"time": 10.0, "type": "TALK", "text": "Gözlerini aç, 'Değişken'.", "speaker": "VASI"},
            {"time": 12.0, "type": "TALK", "text": "Yukarıda, Egemenler seni bekliyor.", "speaker": "VASI"},
            {"time": 14.0, "type": "TALK", "text": "Sistemi çökertmeye hazır mısın?", "speaker": "VASI", "color": CYBER_GREEN},
            {"time": 16.0, "type": "GLITCH_CLIMAX", "text": "SİMÜLASYON BAŞLATILIYOR..."},
        ]

        # 2. BETRAYAL
        timeline_betrayal = [
            {"time": 0.5, "type": "BIOS", "text": "ANALYSIS: PACIFIST RUN DETECTED..."},
            {"time": 2.0, "type": "BIOS", "text": "KARMA LEVEL: PURE WHITE..."},
            {"time": 4.0, "type": "EYE_WAKE", "text": "Hala buradasın...", "speaker": "VASI"},
            {"time": 6.0, "type": "TALK", "text": "Hiç kimseyi öldürmeden buraya kadar geldin.", "speaker": "VASI"},
            {"time": 9.0, "type": "TALK", "text": "Sana 'Kahraman' diyorlar değil mi? Ne kadar NAİF.", "speaker": "VASI"},
            {"time": 12.0, "type": "SCAN", "text": "GÜVENLİK DUVARI: AŞILDI.", "speaker": "SİSTEM", "color": ALERT_RED},
            {"time": 14.0, "type": "TALK", "text": "Güvenlik duvarını aşmak için 'temiz' bir veriye ihtiyacım vardı. O sensin.", "speaker": "VASI"},
            {"time": 17.0, "type": "TALK", "text": "Artık işim bitti. Merhametin senin sonun olacak.", "speaker": "VASI"},
            {"time": 20.0, "type": "GLITCH_CLIMAX", "text": "SİLİNME İŞLEMİ BAŞLATILIYOR...", "color": ALERT_RED},
        ]

        # 3. JUDGMENT
        timeline_judgment = [
            {"time": 0.5, "type": "BIOS", "text": "ANALYSIS: GENOCIDE RUN DETECTED..."},
            {"time": 2.0, "type": "BIOS", "text": "KARMA LEVEL: PURE BLACK..."},
            {"time": 4.0, "type": "HEX_DUMP", "text": "ERROR: TOO MUCH BLOOD DATA"},
            {"time": 6.0, "type": "EYE_WAKE", "text": "Havadaki bu kokuyu alıyor musun?", "speaker": "SAVAŞÇI", "color": ALERT_RED},
            {"time": 9.0, "type": "TALK", "text": "Yanmış veri ve kan kokusu...", "speaker": "SAVAŞÇI"},
            {"time": 12.0, "type": "TALK", "text": "Egemenlere ulaşmak istiyorsun ama bir kurtarıcı gibi değil...", "speaker": "SAVAŞÇI"},
            {"time": 15.0, "type": "TALK", "text": "...bir VEBA gibi geliyorsun.", "speaker": "SAVAŞÇI"},
            {"time": 18.0, "type": "TALK", "text": "Sen bir kahraman değilsin. Sen sadece bozuk bir kodsun.", "speaker": "SAVAŞÇI"},
            {"time": 21.0, "type": "GLITCH_CLIMAX", "text": "HATALARI DÜZELTME ZAMANI!", "color": ALERT_RED},
        ]

        # 4. FINAL MEMORY
        timeline_final_memory = [
            {"time": 1.0, "type": "BIOS", "text": "MEMORY FRAGMENT FOUND... LOADING..."},
            {"time": 3.0, "type": "EYE_WAKE", "text": "Bunca gürültünün arasında...", "speaker": "İÇ SES", "color": (255, 200, 50)},
            {"time": 5.5, "type": "TALK", "text": "Onu hatırlıyorum. En yakın dostumu.", "speaker": "İÇ SES"},
            {"time": 8.0, "type": "TALK", "text": "Bana sırtımı kollamayı öğretmişti.", "speaker": "İÇ SES"},
            # SİLAH GÖSTERİMİ
            {"time": 12.0, "type": "WEAPON_SHOW", "text": "Bu sefer ıskalamayacağım.", "speaker": "OYUNCU", "color": (0, 255, 255)}, 
            {"time": 16.0, "type": "GLITCH_CLIMAX", "text": "SON SAVAŞ BAŞLIYOR!", "color": (255, 50, 50)},
        ]
        # 5. GOOD ENDING (KURTULUŞ - YÜKSEK KARMA)
        timeline_good_ending = [
            {"time": 0.5, "type": "BIOS", "text": "SYSTEM INTEGRITY: RESTORED..."},
            {"time": 2.5, "type": "BIOS", "text": "SOUL DATA: UPLOADING TO CLOUD... 100%"},
            {"time": 4.5, "type": "EYE_WAKE", "text": "Döngü kırıldı.", "speaker": "VASİ", "color": (0, 255, 255)},
            {"time": 7.0, "type": "TALK", "text": "Bunu başarabileceğini hiç düşünmemiştim, İsimsiz.", "speaker": "VASİ"},
            {"time": 10.0, "type": "TALK", "text": "Silahını indirdin ve onlara elini uzattın.", "speaker": "VASİ"},
            {"time": 13.0, "type": "TALK", "text": "Fragmentia artık bir hapishane değil...", "speaker": "VASİ"},
            {"time": 16.0, "type": "TALK", "text": "...bir yuva.", "speaker": "VASİ", "color": (255, 215, 0)}, # Altın Rengi
            {"time": 19.0, "type": "SCAN", "text": "YENİ YÖNETİCİ ATANIYOR: [İSİMSİZ]", "color": (0, 255, 100)},
            {"time": 22.0, "type": "GLITCH_CLIMAX", "text": "SİMÜLASYON TAMAMLANDI. HUZUR.", "color": (255, 255, 255)},
        ]

        # 6. BAD ENDING (SOYKIRIM - DÜŞÜK KARMA)
        timeline_bad_ending = [
            {"time": 0.5, "type": "HEX_DUMP", "text": "FATAL ERROR: 0xDEAD_END"},
            {"time": 2.0, "type": "HEX_DUMP", "text": "ALL ENTITIES DELETED."},
            {"time": 4.0, "type": "EYE_WAKE", "text": "Ne yaptın sen?", "speaker": "SİSTEM", "color": (255, 0, 0)},
            {"time": 6.5, "type": "TALK", "text": "Burada yönetebileceğin hiçbir şey kalmadı.", "speaker": "SİSTEM"},
            {"time": 9.0, "type": "TALK", "text": "Hepsini sildin. Sadece sessizlik var.", "speaker": "SİSTEM"},
            {"time": 12.0, "type": "EYE_WAKE", "text": "Bu sessizlik... Ne kadar güzel.", "speaker": "OYUNCU", "color": (100, 0, 0)}, # Koyu Kırmızı
            {"time": 15.0, "type": "TALK", "text": "Artık kuralları ben koyarım.", "speaker": "OYUNCU"},
            {"time": 18.0, "type": "GLITCH_CLIMAX", "text": "SİSTEM KAPATILIYOR... SONSUZA DEK.", "color": (50, 0, 0)},
        ]

        # Senaryo Seçiciye Ekle
        if self.scenario_type == 'BETRAYAL':
            self.timeline = timeline_betrayal
        elif self.scenario_type == 'JUDGMENT':
            self.timeline = timeline_judgment
        elif self.scenario_type == 'FINAL_MEMORY':
            self.timeline = timeline_final_memory
        elif self.scenario_type == 'GOOD_ENDING': # YENİ
            self.timeline = timeline_good_ending
        elif self.scenario_type == 'BAD_ENDING':  # YENİ
            self.timeline = timeline_bad_ending
        else:
            self.timeline = timeline_intro

        self.current_step = 0
        self.state_type = "BIOS"
        self.bios_lines = []
        
        self.glitch_amount = 0.0
        self.shake_offset = (0, 0)
        self.text_color = CYBER_GREEN # Varsayılan renk

    def load_sounds(self):
        sound_names = ['sfx_bip', 'sfx_glitch', 'sfx_awake']
        for name in sound_names:
            path = self.asset_paths.get(name)
            if path and isinstance(path, str):
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                    self.sounds[name].set_volume(0.3)
                except:
                    self.sounds[name] = None
            else:
                self.sounds[name] = None

    def play_sound(self, name):
        if self.sounds.get(name):
            self.sounds[name].play()

    def update(self, dt):
        self.time_elapsed += dt
        self.text_timer += dt

        if self.current_step < len(self.timeline):
            next_event = self.timeline[self.current_step]
            if self.time_elapsed >= next_event["time"]:
                self.state_type = next_event["type"]
                self.current_text = next_event["text"]
                self.speaker = next_event.get("speaker", "")
                self.text_color = next_event.get("color", CYBER_GREEN)
                
                if self.state_type == "BIOS":
                    self.play_sound('sfx_bip')
                    self.bios_lines.append({"text": self.current_text, "color": self.text_color})
                    if len(self.bios_lines) > 15: self.bios_lines.pop(0)
                elif self.state_type == "LOADING":
                    val = next_event.get("load_val", 0.0)
                    self.loading_bar.set_progress(val, self.current_text)
                elif self.state_type == "EYE_WAKE":
                    self.play_sound('sfx_awake')
                    self.digital_eye.scanning = True
                    self.glitch_amount = 2.0
                elif self.state_type == "GLITCH_CLIMAX":
                    self.play_sound('sfx_glitch')
                    self.glitch_amount = 20.0
                
                self.char_index = 0
                self.current_step += 1

        speed = 40 if self.state_type == "TALK" else 100
        if int(self.char_index) < len(self.current_text):
            self.char_index += dt * speed
        
        if self.state_type in ["HEX_DUMP", "GLITCH_CLIMAX"]:
            self.hexdump.update(dt)
        # SİYAH EKRAN SORUNUNU ÇÖZEN EKLEME (WEAPON_SHOW buraya eklendi)
        if self.state_type in ["LOADING", "SCAN", "EYE_WAKE", "TALK", "GLITCH_CLIMAX", "WEAPON_SHOW"]:
            self.matrix_rain.update()
        if self.state_type == "LOADING":
            self.loading_bar.update(dt)
        if self.state_type in ["EYE_WAKE", "SCAN", "TALK", "GLITCH_CLIMAX"]:
            self.digital_eye.update(dt)

        self.glitch_amount *= 0.96
        if self.glitch_amount < 0.1: self.glitch_amount = 0
        if self.glitch_amount > 0:
            self.shake_offset = (random.randint(-int(self.glitch_amount), int(self.glitch_amount)),
                                 random.randint(-int(self.glitch_amount), int(self.glitch_amount)))
        else:
            self.shake_offset = (0, 0)

        if self.time_elapsed > self.timeline[-1]["time"] + 2.0:
            self.running = False

    def draw(self):
        self.screen.fill(self.bg_color)
        shake_x, shake_y = self.shake_offset
        
        # 1. BIOS EKRANI
        if self.state_type == "BIOS":
            y_offset = 50
            for line in self.bios_lines:
                txt = self.font_bios.render(line["text"], True, line["color"])
                self.screen.blit(txt, (50, y_offset))
                y_offset += 25
            if int(self.time_elapsed * 2) % 2 == 0:
                pygame.draw.rect(self.screen, CYBER_GREEN, (50, y_offset, 10, 20))

        # 2. HEX DUMP
        elif self.state_type == "HEX_DUMP":
            self.hexdump.draw(self.screen, 50, 50)
            if int(self.time_elapsed * 4) % 2 == 0:
                warn_box = pygame.Surface((600, 100))
                warn_box.fill(ALERT_RED)
                txt = self.font_large.render(self.current_text, True, PURE_BLACK)
                warn_box.blit(txt, (300 - txt.get_width()//2, 50 - txt.get_height()//2))
                self.screen.blit(warn_box, (self.width//2 - 300, self.height//2 - 50))

        # 3. YÜKLEME
        elif self.state_type == "LOADING":
            self.matrix_rain.draw(self.screen, self.font_matrix, (0, 50, 0))
            logo_text = self.font_large.render("NEXUS OS", True, CYBER_GREEN)
            self.screen.blit(logo_text, (self.width//2 - logo_text.get_width()//2, self.height//2 - 100))
            self.loading_bar.draw(self.screen, self.width//2 - 300, self.height//2 + 50)

        # 4. GÖZ / KONUŞMA / GLITCH
        elif self.state_type in ["EYE_WAKE", "SCAN", "TALK", "GLITCH_CLIMAX"]:
            if self.state_type != "GLITCH_CLIMAX":
                self.matrix_rain.draw(self.screen, self.font_matrix, (0, 30, 0))
            else:
                self.matrix_rain.draw(self.screen, self.font_matrix, HACKER_GREEN)
                self.hexdump.draw(self.screen, 0, 0, (255, 0, 0))

            intensity = 1.0
            eye_col = (0, 255, 100)
            if self.state_type == "SCAN": eye_col = (0, 200, 255)
            elif self.state_type == "GLITCH_CLIMAX":
                eye_col = (255, 50, 50)
                intensity = 2.0

            display_surf = self.screen.copy()
            if self.speaker == "SAVAŞÇI":
                cx, cy = self.width // 2, self.height // 2 - 80
                self.digital_eye.draw_warrior(display_surf, cx, cy, intensity)
            else:
                self.digital_eye.draw(display_surf, eye_col, intensity)
            self.screen.blit(display_surf, (shake_x, shake_y))

            if self.state_type == "TALK" or self.state_type == "SCAN":
                box_rect = pygame.Rect(self.width//2 - 400, self.height - 200, 800, 120)
                s = pygame.Surface((800, 120), pygame.SRCALPHA)
                s.fill((0, 10, 5, 230))
                self.screen.blit(s, box_rect.topleft)
                pygame.draw.rect(self.screen, self.text_color, box_rect, 2)
                
                if self.speaker:
                    name_bg = pygame.Rect(box_rect.left, box_rect.top - 30, 200, 30)
                    pygame.draw.rect(self.screen, self.text_color, name_bg)
                    name_txt = self.font_main.render(self.speaker, True, PURE_BLACK)
                    self.screen.blit(name_txt, (name_bg.x + 10, name_bg.y + 5))
                
                display_txt = self.current_text[:int(self.char_index)]
                txt_surf = self.font_main.render(display_txt, True, PURE_WHITE)
                self.screen.blit(txt_surf, (box_rect.x + 20, box_rect.y + 20))

            if self.state_type == "GLITCH_CLIMAX":
                 txt = self.font_large.render(self.current_text, True, ALERT_RED)
                 self.screen.blit(txt, (self.width//2 - txt.get_width()//2 + shake_x, self.height//2 + shake_y))
        
        # 5. SİLAH GÖSTERİMİ
        elif self.state_type == "WEAPON_SHOW":
            # Arka plan matrix
            self.matrix_rain.draw(self.screen, self.font_matrix, (0, 50, 50))
            
            # Silahı ekranın ortasına çiz
            cx, cy = self.width // 2, self.height // 2 - 50
            scale = 2.0 
            draw_cyber_revolver(self.screen, cx, cy, self.text_color, scale)
            
            # Teknik Yazı
            try:
                font_tech = pygame.font.SysFont("consolas", 20)
            except:
                font_tech = pygame.font.Font(None, 24)
                
            tech_text = font_tech.render("[WEAPON_CLASS: LEGENDARY]", True, self.text_color)
            self.screen.blit(tech_text, (cx - tech_text.get_width()//2, cy + 100))
            
            # Alt Yazı (Speaker varsa)
            if self.speaker:
                 txt = self.font_main.render(self.current_text, True, PURE_WHITE)
                 self.screen.blit(txt, (self.width//2 - txt.get_width()//2, self.height - 150))
            else:
                 # Sistem mesajı ise
                 txt = self.font_main.render(self.current_text, True, self.text_color)
                 self.screen.blit(txt, (self.width//2 - txt.get_width()//2, self.height - 150))

        self.crt_effect.draw(self.screen)
        
        if self.glitch_amount > 5.0:
            temp = self.screen.copy()
            self.screen.blit(temp, (5, 0), special_flags=pygame.BLEND_ADD)
            self.screen.blit(temp, (-5, 0), special_flags=pygame.BLEND_ADD)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE or event.key == pygame.K_SPACE:
                    self.running = False
        return True

    def run(self):
        while self.running:
            dt = self.clock.tick(60) / 1000.0
            if not self.handle_events():
                return False
            self.update(dt)
            self.draw()
            pygame.display.flip()
        return True
import pygame
import sys
import math
import random
import threading
import json
import urllib.request
import urllib.error
import ssl
_SSL_CTX = ssl._create_unverified_context()

import time

pygame.init()
pygame.font.init()

# --- EKRAN ---
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fragmentia  ✦  Bölüm 1.2 — Çöplükte Uyanış")
clock = pygame.time.Clock()
FPS = 60

# --- RENKLER — Endüstriyel / Asit Paleti ---
SKY_TOP     = (12,  18,  14)   # Zifiri kurşuni yeşil
SKY_BOT     = (38,  34,  22)   # Dumanlı kahverengi gri
GROUND_COL  = (32,  22,  14)   # Pas/toprak
TILE_COL    = (72,  50,  28)   # Paslı metal
TILE_DARK   = (48,  32,  16)   # Koyu pas
ACID_COL    = (140, 210, 30)   # Asit sarısı-yeşili
PLAYER_COL  = (130, 220, 255)  # Nebula mavisi
WHITE       = (255, 255, 255)
BLACK       = (0,   0,   0)
GRAY        = (130, 120, 100)
DARKGRAY    = (40,  38,  30)
BUBBLE_BG   = (30,  40,  20)
BUBBLE_BOR  = (140, 200, 40)
HINT_COL    = (180, 230, 50)
INPUT_BG    = (10,  14,  8)
INPUT_BOR   = (120, 180, 30)
AI_COL      = (160, 230, 120)
PLAYER_TXT  = (130, 200, 255)
RUST1       = (160, 80,  30)
RUST2       = (120, 55,  20)
SMOKE_COL   = (55,  50,  45)

# --- FONTlar ---
font_main  = pygame.font.SysFont("segoeui", 18)
font_bold  = pygame.font.SysFont("segoeui", 20, bold=True)
font_title = pygame.font.SysFont("segoeui", 28, bold=True)
font_small = pygame.font.SysFont("segoeui", 15)
font_input = pygame.font.SysFont("segoeui", 17)
font_tiny  = pygame.font.SysFont("segoeui", 13)

WORLD_W = 4000
WORLD_H = HEIGHT

# ================================================================
# GROQ API
# ================================================================
GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"

def call_ai(api_key, history, system_prompt):
    messages = [{"role": "system", "content": system_prompt}]
    for msg in history:
        role = "user" if msg["role"] == "user" else "assistant"
        messages.append({"role": role, "content": msg["text"]})
    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "max_tokens": 200,
        "temperature": 0.9
    }
    data = json.dumps(payload).encode("utf-8")
    req  = urllib.request.Request(
        GROQ_URL, data=data,
        headers={"Content-Type": "application/json",
                 "Authorization": f"Bearer {api_key}"}
    )
    try:
        with urllib.request.urlopen(req, timeout=15, context=_SSL_CTX) as resp:
            body = json.loads(resp.read())
            return body["choices"][0]["message"]["content"].strip()
    except urllib.error.HTTPError as e:
        err = e.read().decode()
        try:
            msg = json.loads(err)["error"]["message"]
        except Exception:
            msg = err[:120]
        return f"[HATA] {msg}"
    except Exception as e:
        return f"[HATA] {str(e)[:120]}"

# ================================================================
# YARDIMCI
# ================================================================
def wrap_text(text, font, max_width):
    words = text.split()
    lines, line = [], ""
    for w in words:
        test = (line + " " + w).strip()
        if font.size(test)[0] <= max_width:
            line = test
        else:
            if line:
                lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines

def draw_rounded_rect_alpha(surf, color, rect, radius=10, alpha=200):
    s = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    pygame.draw.rect(s, (*color, alpha), (0, 0, rect[2], rect[3]), border_radius=radius)
    surf.blit(s, (rect[0], rect[1]))

# ================================================================
# KAMERA
# ================================================================
class Camera:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0

    def update(self, tx, ty):
        tx = max(0, min(tx - WIDTH  // 2, WORLD_W - WIDTH))
        ty = max(0, min(ty - HEIGHT // 2, WORLD_H - HEIGHT))
        self.x += (tx - self.x) * 0.10
        self.y += (ty - self.y) * 0.10

    def apply(self, x, y):
        return x - int(self.x), y - int(self.y)

# ================================================================
# OYUNCU  (Nebula bilincinin beden almış hali)
# ================================================================
class Player:
    W, H = 36, 58
    SPEED  = 5
    JUMP_V = -16
    GRAV   = 0.7

    def __init__(self, x, y):
        self.x   = float(x)
        self.y   = float(y)
        self.vx  = 0.0
        self.vy  = 0.0
        self.grounded = False
        self.facing   = 1
        self.anim_t   = 0
        self.talking  = False
        self.glow_t   = 0

    def update(self, platforms):
        keys = pygame.key.get_pressed()
        self.glow_t += 1
        if not self.talking:
            self.vx = 0
            if keys[pygame.K_LEFT]  or keys[pygame.K_a]: self.vx = -self.SPEED; self.facing = -1
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.vx =  self.SPEED; self.facing =  1
            if (keys[pygame.K_UP] or keys[pygame.K_w] or keys[pygame.K_SPACE]) and self.grounded:
                self.vy = self.JUMP_V
                self.grounded = False
        else:
            self.vx = 0

        self.vy += self.GRAV
        self.x  += self.vx
        self.y  += self.vy
        self.x   = max(0, min(self.x, WORLD_W - self.W))

        self.grounded = False
        for p in platforms:
            if (self.x + self.W > p.x and self.x < p.x + p.w and
                    self.y + self.H > p.y and self.y + self.H < p.y + p.h + 20 and
                    self.vy >= 0):
                self.y = p.y - self.H; self.vy = 0; self.grounded = True

        if self.y + self.H >= WORLD_H - 80:
            self.y = WORLD_H - 80 - self.H; self.vy = 0; self.grounded = True

        if self.vx != 0:
            self.anim_t += 1

    def draw(self, surf, cam):
        sx, sy = cam.apply(int(self.x), int(self.y))
        t = self.anim_t; f = self.facing

        # Nebula parıltısı (mavi enerji halesi)
        glow_r = int(18 + math.sin(self.glow_t * 0.07) * 4)
        glow = pygame.Surface((glow_r*2+10, glow_r*2+10), pygame.SRCALPHA)
        pygame.draw.circle(glow, (80, 180, 255, 22), (glow_r+5, glow_r+5), glow_r+5)
        surf.blit(glow, (sx + self.W//2 - glow_r - 5, sy + self.H//2 - glow_r - 5))

        shadow = pygame.Surface((self.W, 10), pygame.SRCALPHA)
        pygame.draw.ellipse(shadow, (0, 0, 0, 60), (0, 0, self.W, 10))
        surf.blit(shadow, (sx, sy + self.H - 4))

        # Bacaklar — yırtık koyu giysi
        leg = int(math.sin(t * 0.25) * 6) if self.vx != 0 else 0
        pygame.draw.rect(surf, (28, 38, 55), (sx + 4,           sy + 36 + leg, 12, 22))
        pygame.draw.rect(surf, (28, 38, 55), (sx + self.W - 16, sy + 36 - leg, 12, 22))
        # Gövde — mavi-siyah giysili
        pygame.draw.rect(surf, (40, 80, 120), (sx, sy + 14, self.W, 28), border_radius=6)
        # Nebula enerjisi çizgileri gövde üstünde
        energy = int(math.sin(self.glow_t * 0.1) * 3)
        pygame.draw.line(surf, (100, 210, 255), (sx+6, sy+20+energy), (sx+self.W-6, sy+20+energy), 1)
        pygame.draw.line(surf, (80, 180, 220), (sx+8, sy+28), (sx+self.W-8, sy+28), 1)
        # Kollar
        arm = int(math.sin(t * 0.25) * 5) if self.vx != 0 else 0
        pygame.draw.rect(surf, (35, 65, 100), (sx - 6,          sy + 16 + arm, 9, 18), border_radius=4)
        pygame.draw.rect(surf, (35, 65, 100), (sx + self.W - 3, sy + 16 - arm, 9, 18), border_radius=4)
        # Kafa
        pygame.draw.ellipse(surf, (200, 185, 155), (sx + 4, sy, self.W - 8, 20))
        # Gözler — Nebula bilinci: soluk mavi ışıklı
        ex = sx + (self.W // 2) + f * 5
        pygame.draw.circle(surf, (20, 60, 120), (ex, sy + 8), 3)
        pygame.draw.circle(surf, (120, 210, 255), (ex, sy + 7), 1)

    @property
    def cx(self): return self.x + self.W / 2
    @property
    def cy(self): return self.y + self.H / 2

# ================================================================
# PLATFORM  — Paslı metal enkaz
# ================================================================
class Platform:
    def __init__(self, x, y, w, h=20):
        self.x, self.y, self.w, self.h = x, y, w, h

    def draw(self, surf, cam):
        sx, sy = cam.apply(self.x, self.y)
        if sx + self.w < 0 or sx > WIDTH: return
        # Ana yüzey: paslı plaka
        pygame.draw.rect(surf, TILE_COL,  (sx, sy, self.w, self.h), border_radius=4)
        pygame.draw.rect(surf, TILE_DARK, (sx, sy + self.h - 5, self.w, 5), border_radius=2)
        # Pas lekeleri / perçin çizgileri
        for i in range(0, self.w, 28):
            pygame.draw.circle(surf, RUST2, (sx + i + 6, sy + 5), 3)
        # Çatlak detay
        if self.w > 80:
            mid = self.w // 2
            pygame.draw.line(surf, RUST2, (sx + mid, sy + 2), (sx + mid + 8, sy + self.h - 3), 1)

# ================================================================
# NPC — Fragmentia: Çöplük Sakinleri
# ================================================================
NPC_DATA = [
    {
        # Yaşlı hurda toplayıcı. Çöplüğün her köşesini bilir.
        "name":  "Skrap",
        "color": (160, 75, 28),   # pas portakalı
        "skin":  (185, 145, 95),  # bronz, güneş görmemiş
        "x": 425,
        "system": (
            "Sen Fragmentia adli distopik bir oyunun NPC'sisin. Adin Skrap. "
            "Çöplük Bölgesi'nde yirmi yildir yasayan yasli bir hurda toplayicisisin. "
            "Çöplüğün her tünelini, her gizli geçidini bilirsin. "
            "Paranoyaksın, yabancilara güvenmezsin ama tehlikeyi sezince uyarirsin. "
            "Kisa, köşeli cümleler kurarsın. Bazen eski dünyanin nesnelerinden bahsedersin. "
            "Vasis adli fabrika yöneticisinden nefret edersin, onun adini duymak bile seni gerger yapar. "
            "KURAL: Sadece Türkçe yaz. Maksimum 3 kisa cümle. Bilmediğin şeyleri 'ben bilmem, sorma bana' diye geçiştir."
        ),
    },
    {
        # Çöplükte doğmuş genç kız. Hiç dışarı çıkmamış.
        "name":  "Roza",
        "color": (70, 150, 70),    # soluk yeşil
        "skin":  (255, 205, 165),
        "x": 1385,
        "system": (
            "Sen Fragmentia adlı distopik bir oyunun NPC'sisin. Adin Roza. "
            "Yaşın 14-15 civarında, çöplük bölgesinde doğdun ve hiç dışarı çıkmadın. "
            "Kırık teknoloji parçaları toplarsın, onların ne işe yaradığını merak edersin. "
            "Naif, cesur, meraklısın; ölümden korkmazsın çünkü başka türlü hayatı bilmiyorsun. "
            "Dışarıdan gelen biri seni heyecanlandırır. Sorular sorarsın. "
            "Nebula adını duyunca tuhaf hisseder, sanki bir rüyada gördüğünü sanırsın. "
            "KURAL: Sadece Türkçe yaz. Maksimum 3 cümle. Cümlelerinde bazen çocuksu bir safiyet taşısın."
        ),
    },
    {
        # Yarı robot, fabrika güvenlik birimi. Çöpte terk edilmiş.
        "name":  "Dent",
        "color": (100, 110, 130),   # soğuk çelik mavisi
        "skin":  (155, 155, 160),   # metalik/gri ten
        "x": 2280,
        "system": (
            "Sen Fragmentia adlı distopik bir oyunun NPC'sisin. Adin Dent. "
            "Vücudunun %60'ı metalik implant, eski bir fabrika güvenlik birimisin. "
            "Çöplüğe terk edildikten sonra hafızan bozuldu. Hangi tarafa sadık olduğunu bilmiyorsun. "
            "Konuşurken bazen robotik protokol diliyle, bazen kırık insan duygusuyla konuşursun. "
            "Korumak içgüdün var ama kimi koruyacağını şaşırdın. "
            "Vasis'in kodlarına göre düşman olarak işaretlenmiş biriyle konuşmak seni çatışmaya sokuyor. "
            "KURAL: Sadece Türkçe yaz. Maksimum 3 cümle. Ara sıra [HATA] veya [PROTOKOL İHLALİ] gibi sistem mesajı format hatası ekleyebilirsin."
        ),
    },
    {
        # Çöplüğün kadim ateş bekçisi. Eski dünyayı bilen tek kişi.
        "name":  "Ember",
        "color": (200, 95, 25),    # yanık turuncu-kırmızı
        "skin":  (215, 165, 120),
        "x": 3140,
        "system": (
            "Sen Fragmentia adlı distopik bir oyunun NPC'sisin. Adin Ember. "
            "Çöplük bölgesinin tek ısınma ateşini koruyorsun. Yetmişini aşkın yaşindasin. "
            "Fragmentia Olayı'nı gören son kişilerden birisin. Nebula bilincini tanıyorsun. "
            "Sakin, mistik, derin konuşursun. Kehanetimsi cümleler kurarsın ama somut bilgi de verirsin. "
            "Çöplükten çıkışı bilirsin ama kolay söylemezsin, önce oyuncuyu test edersin. "
            "Vasis hakkında 'O, zamanı yiyen birdir' diyebilirsin. "
            "KURAL: Sadece Türkçe yaz. Maksimum 3 cümle. Şiirsel ama anlaşılır ol."
        ),
    },
]

# ================================================================
# DÜKKAN VERİTABANI  — Gecekondu/Shantytown
# ================================================================
SHOP_DATA = [
    {
        # Skrap — Eski konteyner üstüne eklenmiş tahta köpek kulübesi gibisi
        "npc": "Skrap", "x": 360,
        "parts": [
            # (tip, x_off, y_from_bottom, w, h, renk)
            ("box", 0,   0,   170, 130, (70, 42, 18)),    # ana konteyner gövde
            ("box", 20,  130, 110, 55,  (58, 35, 14)),    # üst ek oda
            ("box", -8,  0,   12,  130, (55, 32, 12)),    # sol destek
            ("box", 158, 0,   12,  130, (55, 32, 12)),    # sağ destek
        ],
        "patches": [
            # yamalı levhalar (x_off, y_from_bottom, w, h, renk)
            (30,  30,  40, 25, (90, 52, 20)),
            (90,  60,  30, 18, (100, 60, 15)),
            (5,   80,  20, 30, (80, 48, 16)),
            (130, 40,  25, 20, (95, 55, 18)),
            (40,  130, 35, 20, (65, 38, 12)),
        ],
        "roof": ("lean", 20, 185, 130, 40, (95, 58, 22)),  # eğik sac çatı (x_off, y_top, w, yükseklik farkı, renk)
        "door": (65, 0, 36, 70),      # (x_off, y_from_bottom, w, h)
        "windows": [
            (15,  80, 26, 20, True),   # (x_off, y_from_bottom, w, h, lit?)
            (120, 80, 26, 20, False),
            (32,  148, 22, 16, True),
        ],
        "label": ("HURDA", 55, 155),  # (text, x_off, y_from_bottom)
        "chimney": (140, 175, 10, 35, (55, 32, 12)),  # baca (x_off, y_from_bottom, w, h, renk)
        "extras": [
            ("barrel_left",),
            ("scrap_right",),
            ("rope", 0, 185, 170, 195),  # ip (x1_off, y1, x2_off, y2) — çamaşır ipi
        ],
    },
    {
        # Roza — Yıkık duvar üstüne branda çekmiş, neon ışıklı kıble
        "npc": "Roza", "x": 1280,
        "parts": [
            ("box", 0,   0,   90,  140, (28, 48, 38)),   # sol bölüm
            ("box", 90,  0,   80,  110, (32, 55, 42)),   # sağ bölüm (daha kısa)
            ("box", 10,  140, 70,  45,  (24, 42, 32)),   # sol üst ek
        ],
        "patches": [
            (0,   50, 90, 5,  (50, 80, 60)),   # yatay ayrım çizgisi
            (12,  20, 20, 30, (35, 62, 45)),
            (60, 100, 25, 18, (30, 58, 40)),
            (92,  30, 78,  4, (45, 70, 52)),
        ],
        "roof": ("flat_uneven", 0, 185, 175, 0, (35, 65, 50)),  # düz ama yamuk
        "door": (100, 0, 34, 70),
        "windows": [
            (10,  70, 24, 18, True),
            (55,  90, 20, 16, True),
            (95,  40, 22, 20, False),
            (135, 60, 18, 22, True),
        ],
        "label": ("TEKNO", 38, 150),
        "chimney": None,
        "extras": [
            ("antenna", 155, 183),   # anten (x_off, y_from_bottom)
            ("scrap_left",),
            ("wires", 0, 185, 175, 188),
        ],
    },
    {
        # Dent — Beton blok, köşeli, dikenli telli, gözaltı hissi
        "npc": "Dent", "x": 2220,
        "parts": [
            ("box", 0,   0,   160, 160, (40, 44, 56)),   # ana blok
            ("box", 15,  160, 130, 40,  (35, 38, 50)),   # üst katman
            ("box", -10, 60,  10,  100, (30, 33, 45)),   # sol dışa çıkma
            ("box", 160, 80,  10,  80,  (30, 33, 45)),   # sağ dışa çıkma
        ],
        "patches": [
            (20,  40,  45, 6,  (55, 60, 75)),
            (80,  40,  45, 6,  (55, 60, 75)),
            (0,   100, 160, 4, (50, 54, 68)),
            (30,  130, 30, 15, (45, 50, 62)),
        ],
        "roof": ("flat_thick", -10, 200, 180, 0, (33, 36, 48)),  # kalın düz çatı
        "door": (60, 0, 38, 70),
        "windows": [
            (18,  100, 28, 22, False),
            (110, 100, 28, 22, False),
            (20,  168, 24, 18, True),
            (120, 168, 24, 18, False),
        ],
        "label": ("DEVRIYE", 32, 170),
        "chimney": None,
        "extras": [
            ("barbwire", -10, 200, 180),   # dikenli tel (x_off, y, genişlik)
            ("searchlight", 140, 198),     # projektör ışığı
            ("scrap_right",),
        ],
    },
    {
        # Ember — Ahşap + taş + branda patchwork kulübe, en organik
        "npc": "Ember", "x": 3070,
        "parts": [
            ("box", 0,   0,   110, 150, (68, 40, 18)),   # ana ahşap
            ("box", 110, 0,   70,  120, (75, 45, 20)),   # sağ taş ek
            ("box", 20,  150, 90,  50,  (58, 34, 14)),   # sol üst
            ("box", 0,   60,  -8,  90,  (55, 30, 12)),   # sol çıkma (negatif w = sola)
        ],
        "patches": [
            (8,   30,  30, 22, (85, 50, 20)),
            (50,  80,  40, 18, (78, 46, 18)),
            (115, 30,  60, 8,  (90, 55, 22)),
            (22,  150, 30, 20, (65, 38, 14)),
            (90,  155, 25, 18, (70, 42, 16)),
        ],
        "roof": ("gabled_offset", 0, 200, 180, 60, (88, 50, 18)),  # iki katlı yamuk çatı
        "door": (70, 0, 36, 70),
        "windows": [
            (14,  80,  26, 22, True),
            (70,  60,  22, 18, True),
            (118, 50,  24, 20, False),
            (28,  160, 20, 16, True),
        ],
        "label": ("OCAK", 80, 162),
        "chimney": (90, 195, 16, 50, (52, 30, 10)),
        "extras": [
            ("barrel_left",),
            ("barrel_right",),
            ("rope", 0, 195, 180, 180),
        ],
    },
]
class NPC:
    W, H     = 34, 56
    TALK_DIST = 120

    def __init__(self, data):
        self.name    = data["name"]
        self.color   = data["color"]
        self.skin    = data["skin"]
        self.x       = float(data["x"])
        self.system  = data["system"]
        self.history = []

        self.in_talk           = False
        self.ai_response       = ""
        self.loading           = False
        self._scroll_to_bottom = False
        self.error             = ""

        self.bob_t   = random.randint(0, 100)
        self.blink_t = random.randint(0, 200)

        self.y = WORLD_H - 80 - self.H

    def near(self, player):
        return abs((self.x + self.W / 2) - player.cx) < self.TALK_DIST

    def send_message(self, api_key, player_msg):
        self.history.append({"role": "user", "text": player_msg})
        self.loading     = True
        self.ai_response = ""
        self.error       = ""

        def worker():
            messages = [{"role": "system", "content": self.system}]
            for m in self.history:
                role = "user" if m["role"] == "user" else "assistant"
                messages.append({"role": role, "content": m["text"]})

            GROQ_MODELS = [
                "llama-3.3-70b-versatile",
                "llama-3.1-70b-versatile",
                "llama3-70b-8192",
                "mixtral-8x7b-32768",
                "gemma2-9b-it",
            ]

            reply = "[Şu an sinyal yok. Tekrar dene.]"
            for model_name in GROQ_MODELS:
                payload = {
                    "model": model_name,
                    "messages": messages,
                    "max_tokens": 200,
                    "temperature": 0.9
                }
                try:
                    import requests as req_lib
                    resp = req_lib.post(
                        GROQ_URL,
                        json=payload,
                        headers={"Authorization": f"Bearer {api_key}"},
                        timeout=15,
                        verify=False
                    )
                    if resp.status_code == 200:
                        reply = resp.json()["choices"][0]["message"]["content"].strip()
                        import unicodedata
                        arabic_chars = sum(1 for c in reply if unicodedata.name(c, '').startswith('ARABIC'))
                        if arabic_chars > 2:
                            messages[-1]["content"] += "\n\nÖNEMLİ: SADECE Türkçe yaz. Başka alfabe kesinlikle yasak."
                            continue
                        break
                    elif resp.status_code in (429, 503, 502):
                        continue
                    else:
                        break
                except Exception as ex:
                    continue

            self.history.append({"role": "model", "text": reply})
            self.ai_response = reply
            self.loading     = False
            self._scroll_to_bottom = True

        threading.Thread(target=worker, daemon=True).start()

    def draw(self, surf, cam):
        self.bob_t   += 1
        self.blink_t += 1
        bob   = math.sin(self.bob_t * 0.04) * 3
        blink = self.blink_t % 180 < 8

        sx, sy = cam.apply(int(self.x), int(self.y + bob))
        if sx + self.W < 0 or sx > WIDTH: return

        darker = tuple(max(0, c - 40) for c in self.color)
        # Bacaklar
        pygame.draw.rect(surf, self.color, (sx + 5,           sy + 34, 10, 20), border_radius=4)
        pygame.draw.rect(surf, self.color, (sx + self.W - 15, sy + 34, 10, 20), border_radius=4)
        # Gövde
        pygame.draw.rect(surf, self.color, (sx, sy + 14, self.W, 26), border_radius=7)
        # Kollar
        pygame.draw.rect(surf, darker, (sx - 5,          sy + 16, 8, 16), border_radius=4)
        pygame.draw.rect(surf, darker, (sx + self.W - 3, sy + 16, 8, 16), border_radius=4)
        # Kafa
        pygame.draw.ellipse(surf, self.skin, (sx + 3, sy - 2, self.W - 6, 22))

        if not blink:
            pygame.draw.circle(surf, (30, 20, 10), (sx + 10,          sy + 7), 3)
            pygame.draw.circle(surf, (30, 20, 10), (sx + self.W - 10, sy + 7), 3)
        else:
            pygame.draw.line(surf, (30, 20, 10), (sx + 7,           sy + 7), (sx + 13,           sy + 7), 2)
            pygame.draw.line(surf, (30, 20, 10), (sx + self.W - 13, sy + 7), (sx + self.W - 7,   sy + 7), 2)

        # Karakter detayları
        if self.name == "Dent":
            # Metal implant çizgisi sol yüz
            pygame.draw.line(surf, (80, 100, 120), (sx + 3, sy + 2), (sx + 12, sy + 14), 2)
            pygame.draw.circle(surf, (100, 200, 255), (sx + 10, sy + 7), 1)  # robot göz parıltısı
        elif self.name == "Ember":
            # Ateş rengi saç tutamı
            for i, oc in enumerate([(255,120,30),(255,80,10),(220,100,20)]):
                pygame.draw.circle(surf, oc, (sx + 8 + i*6, sy - 3), 4)
        elif self.name == "Skrap":
            # Hasarlı kask/bere
            pygame.draw.rect(surf, (60, 45, 25), (sx + 4, sy - 4, self.W - 8, 8), border_radius=4)
        elif self.name == "Roza":
            # Saç bantı
            pygame.draw.rect(surf, (80, 180, 80), (sx + 3, sy + 1, self.W - 6, 5), border_radius=3)

        # İsim etiketi
        if not self.in_talk:
            ns = font_small.render(self.name, True, WHITE)
            nr = ns.get_rect(centerx=sx + self.W // 2, bottom=sy - 6)
            draw_rounded_rect_alpha(surf, (15, 18, 10), nr.inflate(10, 6), radius=5, alpha=200)
            surf.blit(ns, nr)

    @property
    def cx(self): return self.x + self.W / 2

# ================================================================
# ARKA PLAN — Fragmentia Çöplük Bölgesi
# ================================================================
# Duman partikülleri için global liste
smoke_particles = []

def spawn_smoke(cam_x):
    """Fabrika bacalarından duman üret."""
    chimney_positions = [200, 600, 1100, 1700, 2400, 3000, 3600]
    for cx in chimney_positions:
        sx = cx - int(cam_x)
        if -100 < sx < WIDTH + 100:
            if random.random() < 0.08:
                smoke_particles.append({
                    "x": cx + random.randint(-8, 8),
                    "y": HEIGHT - 160,
                    "vx": random.uniform(-0.3, 0.3),
                    "vy": random.uniform(-0.8, -0.4),
                    "life": random.randint(80, 140),
                    "maxlife": 120,
                    "r": random.randint(10, 22)
                })

def update_smoke():
    for p in smoke_particles[:]:
        p["x"] += p["vx"]
        p["y"] += p["vy"]
        p["life"] -= 1
        if p["life"] <= 0:
            smoke_particles.remove(p)

# Asit yağmuru damlaları
acid_drops = [(random.randint(0, WORLD_W), random.uniform(0, HEIGHT),
               random.uniform(2, 5)) for _ in range(300)]

def draw_background(surf, cam_x, global_t):
    # Gökyüzü gradyanı — kurşuni + zehirli ton
    for row in range(HEIGHT):
        t = row / HEIGHT
        r = int(SKY_TOP[0] + (SKY_BOT[0] - SKY_TOP[0]) * t)
        g = int(SKY_TOP[1] + (SKY_BOT[1] - SKY_TOP[1]) * t)
        b = int(SKY_TOP[2] + (SKY_BOT[2] - SKY_TOP[2]) * t)
        pygame.draw.line(surf, (r, g, b), (0, row), (WIDTH, row))

    # Asit yağmuru
    for i, (dx, dy, spd) in enumerate(acid_drops):
        sx = (dx - int(cam_x * 0.9)) % WORLD_W
        screen_x = int(sx % WIDTH)
        screen_y = int((dy + global_t * spd) % HEIGHT)
        acid_drops[i] = (dx, dy, spd)
        alpha = random.randint(80, 140)
        col = (int(100 + random.randint(-10,10)), int(190 + random.randint(-10,10)), 20)
        pygame.draw.line(surf, col, (screen_x, screen_y), (screen_x - 1, screen_y + 5), 1)

    # Uzak fabrika silüetleri (parallax katman 1)
    for i in range(6):
        bx = int(i * 700 - cam_x * 0.12) % (WIDTH + 700) - 350
        bh = 200 + (i % 3) * 50
        bw = 80 + (i % 2) * 40
        pygame.draw.rect(surf, (18, 16, 12), (bx, HEIGHT - 80 - bh, bw, bh))
        # Fabrika penceresi ışıkları
        for wrow in range(3):
            for wcol in range(2):
                wx = bx + 10 + wcol * 28
                wy = HEIGHT - 80 - bh + 20 + wrow * 40
                lit = (global_t // 90 + i + wrow + wcol) % 5 != 0
                wc = (120, 90, 20) if lit else (30, 25, 15)
                pygame.draw.rect(surf, wc, (wx, wy, 14, 10))

    # Ön plan endüstriyel yapı gölgeleri (parallax katman 2)
    for i in range(10):
        fx = int(i * 450 - cam_x * 0.35) % (WIDTH + 450) - 225
        fh = 100 + (i % 4) * 30
        pygame.draw.rect(surf, (22, 18, 12), (fx - 18, HEIGHT - 80 - fh, 36, fh))
        # Baca
        pygame.draw.rect(surf, (30, 24, 16), (fx - 7, HEIGHT - 80 - fh - 40, 14, 40))

    # Duman partikülleri çiz
    spawn_smoke(cam_x)
    update_smoke()
    for p in smoke_particles:
        ratio = 1.0 - p["life"] / p["maxlife"]
        alpha = int(160 * (1 - ratio))
        r = p["r"] + int(ratio * 20)
        sx = int(p["x"]) - int(cam_x)
        sy = int(p["y"])
        if -60 < sx < WIDTH + 60:
            s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (50, 45, 38, alpha), (r, r), r)
            surf.blit(s, (sx - r, sy - r))

    # Zemin — toprak + pas plaka
    pygame.draw.rect(surf, GROUND_COL, (0, HEIGHT - 80, WIDTH, 80))
    # Zemin taşları / metal parçaları
    for i in range(0, WIDTH + 50, 38):
        gx = int(i - cam_x) % (WIDTH + 40) - 20
        col = TILE_DARK if (i // 38) % 3 != 0 else (55, 38, 18)
        pygame.draw.rect(surf, col, (gx, HEIGHT - 80, 36, 8), border_radius=2)

    # Zemin asit birikintileri
    for i in range(8):
        px = int(i * 500 - cam_x * 1.0) % (WIDTH + 500) - 250
        py = HEIGHT - 76
        ag = pygame.Surface((40, 10), pygame.SRCALPHA)
        pulse = int(40 + 15 * math.sin(global_t * 0.05 + i))
        pygame.draw.ellipse(ag, (100, 200, 20, pulse), (0, 0, 40, 10))
        surf.blit(ag, (px, py))

# ================================================================
# DEKORASYON — Çöplük Eşyaları
# ================================================================
def draw_fire_barrel(surf, x, y, t):
    """Ateş varili — ısınma noktası."""
    pygame.draw.rect(surf, (60, 45, 25), (x - 12, y - 5, 24, 30), border_radius=3)
    pygame.draw.rect(surf, (80, 55, 30), (x - 12, y - 5, 24, 30), 2, border_radius=3)
    # Alev
    flicker = math.sin(t * 0.2 + x) * 3
    flame_h = int(14 + flicker)
    for fi, (fc, fr) in enumerate([(( 255,200, 30),7),(( 255,120, 20),5),(( 255, 60, 10),3)]):
        pygame.draw.ellipse(surf, fc, (x - fr, y - 5 - flame_h - fi*3, fr*2, flame_h + fi*4))
    # Işık halesi
    glow = pygame.Surface((80, 80), pygame.SRCALPHA)
    ga = int(30 + flicker * 4)
    pygame.draw.circle(glow, (255, 140, 20, max(0, min(ga, 60))), (40, 40), 38)
    surf.blit(glow, (x - 40, y - 35))

def draw_scrap_pile(surf, x, y, idx):
    """Hurda yığını."""
    random.seed(idx * 137)
    for _ in range(6):
        rx = x + random.randint(-20, 20)
        ry = y + random.randint(-10, 5)
        rw = random.randint(8, 22)
        rh = random.randint(4, 12)
        col = random.choice([RUST1, RUST2, TILE_COL, (90, 65, 35)])
        pygame.draw.rect(surf, col, (rx, ry, rw, rh), border_radius=2)
    random.seed()

def draw_warning_sign(surf, x, y, text, cam_x):
    """Sprey boyalı uyarı levhası."""
    sx = x - int(cam_x)
    # Metal levha
    pygame.draw.rect(surf, (55, 45, 25), (sx, y, 90, 38), border_radius=3)
    pygame.draw.rect(surf, (80, 60, 20), (sx, y, 90, 38), 2, border_radius=3)
    # Destek direği
    pygame.draw.rect(surf, (45, 35, 18), (sx + 40, y + 38, 10, 22))
    # Uyarı rengi çerçeve
    pygame.draw.rect(surf, ACID_COL, (sx + 2, y + 2, 86, 34), 2, border_radius=2)
    ts = font_tiny.render(text, True, (220, 210, 50))
    surf.blit(ts, ts.get_rect(center=(sx + 45, y + 19)))

def draw_broken_pipe(surf, x, y, cam_x):
    """Zemine düşmüş paslı boru."""
    sx = x - int(cam_x)
    pygame.draw.rect(surf, RUST1, (sx - 30, y, 60, 12), border_radius=6)
    pygame.draw.rect(surf, RUST2, (sx - 30, y, 60, 12), 2, border_radius=6)
    pygame.draw.circle(surf, (40, 30, 15), (sx - 30, y + 6), 7)
    pygame.draw.circle(surf, (40, 30, 15), (sx + 30, y + 6), 7)

def draw_shop(surf, shop, cam_x, global_t):
    ox = shop["x"] - int(cam_x)  # dünya x → ekran x
    if ox + 220 < -20 or ox - 20 > WIDTH:
        return
    ground = HEIGHT - 80          # zemin y

    def gy(y_from_bottom):        # zemin tabanlı y hesapla
        return ground - y_from_bottom

    # ── GÖLGE ──────────────────────────────────────────────────────
    sh = pygame.Surface((200, 16), pygame.SRCALPHA)
    pygame.draw.ellipse(sh, (0,0,0,50), (0,0,200,16))
    surf.blit(sh, (ox - 10, ground - 6))

    # ── YAMALI DUVARLAR (parts) ─────────────────────────────────────
    for (typ, xo, yb, w, h, col) in shop["parts"]:
        if w < 0:   # negatif w → sola çıkma, atla
            continue
        rx, ry = ox + xo, gy(yb + h)
        pygame.draw.rect(surf, col, (rx, ry, w, h))
        # tahta çizgi dokusu
        darker = tuple(max(0, c - 18) for c in col)
        for li in range(0, h, 10):
            pygame.draw.line(surf, darker, (rx, ry + li), (rx + w, ry + li), 1)
        # kenar çerçeve
        lighter = tuple(min(255, c + 22) for c in col)
        pygame.draw.rect(surf, lighter, (rx, ry, w, h), 1)

    # ── YAMALI LEVHALAR (patches) ───────────────────────────────────
    for (xo, yb, w, h, col) in shop["patches"]:
        rx, ry = ox + xo, gy(yb + h)
        pygame.draw.rect(surf, col, (rx, ry, w, h))
        lighter = tuple(min(255, c + 30) for c in col)
        pygame.draw.rect(surf, lighter, (rx, ry, w, h), 1)
        # köşe perçinler
        for px_, py_ in [(rx+2, ry+2),(rx+w-4, ry+2),(rx+2, ry+h-4),(rx+w-4, ry+h-4)]:
            pygame.draw.circle(surf, lighter, (px_, py_), 2)

    # ── ÇATI ────────────────────────────────────────────────────────
    rtyp, rxo, ryb, rw, rslant, rcol = shop["roof"]
    rdark = tuple(max(0, c - 25) for c in rcol)
    rlighter = tuple(min(255, c + 20) for c in rcol)

    if rtyp == "lean":
        # eğik sac çatı — sola yüksek, sağa alçak
        p1 = (ox + rxo - 12,      gy(ryb + rslant))   # sol üst
        p2 = (ox + rxo + rw + 12, gy(ryb))             # sağ alt
        p3 = (ox + rxo + rw + 12, gy(ryb) + 14)        # sağ alt kenar
        p4 = (ox + rxo - 12,      gy(ryb + rslant) + 8)# sol üst kenar
        pygame.draw.polygon(surf, rcol, [p1, p2, p3, p4])
        pygame.draw.polygon(surf, rlighter, [p1, p2, p3, p4], 1)
        # sac yiv çizgileri
        steps = rw // 18
        for i in range(steps + 1):
            t_ = i / max(steps, 1)
            lx1 = int(p1[0] + (p2[0]-p1[0]) * t_)
            ly1 = int(p1[1] + (p2[1]-p1[1]) * t_)
            lx2 = int(p4[0] + (p3[0]-p4[0]) * t_)
            ly2 = int(p4[1] + (p3[1]-p4[1]) * t_)
            pygame.draw.line(surf, rdark, (lx1, ly1), (lx2, ly2), 1)

    elif rtyp in ("flat_uneven", "flat_thick"):
        thickness = 22 if rtyp == "flat_thick" else 14
        # düz ama kenarlar biraz yamuk
        pts = [
            (ox + rxo - 8,       gy(ryb) - random.randint(0,4)),
            (ox + rxo + rw//3,   gy(ryb) - random.randint(2,8)),
            (ox + rxo + rw*2//3, gy(ryb) - random.randint(0,5)),
            (ox + rxo + rw + 8,  gy(ryb) - random.randint(1,6)),
            (ox + rxo + rw + 8,  gy(ryb) + thickness),
            (ox + rxo - 8,       gy(ryb) + thickness),
        ]
        random.seed(shop["x"])   # sabit görünüm için
        pts = [
            (ox + rxo - 8,       gy(ryb) - [0,3,1,4,2,5][0]),
            (ox + rxo + rw//3,   gy(ryb) - [0,3,1,4,2,5][1]),
            (ox + rxo + rw*2//3, gy(ryb) - [0,3,1,4,2,5][2]),
            (ox + rxo + rw + 8,  gy(ryb) - [0,3,1,4,2,5][3]),
            (ox + rxo + rw + 8,  gy(ryb) + thickness),
            (ox + rxo - 8,       gy(ryb) + thickness),
        ]
        random.seed()
        pygame.draw.polygon(surf, rcol, pts)
        pygame.draw.polygon(surf, rlighter, pts, 1)
        if rtyp == "flat_thick":
            # beton çizgiler
            for li in range(4, thickness, 7):
                pygame.draw.line(surf, rdark,
                    (ox + rxo - 8, gy(ryb) + li),
                    (ox + rxo + rw + 8, gy(ryb) + li), 1)

    elif rtyp == "gabled_offset":
        # iki parçalı yamuk çatı
        peak_x = ox + rxo + rw // 3    # tepe merkez sola kayık
        peak_y = gy(ryb + rslant)
        base_y = gy(ryb)
        pts_left  = [(ox + rxo - 10, base_y), (peak_x, peak_y),
                     (peak_x, peak_y + 10),   (ox + rxo - 10, base_y + 12)]
        pts_right = [(peak_x, peak_y), (ox + rxo + rw + 10, base_y + 8),
                     (ox + rxo + rw + 10, base_y + 20), (peak_x, peak_y + 10)]
        pygame.draw.polygon(surf, rcol, pts_left)
        pygame.draw.polygon(surf, rdark, pts_right)
        pygame.draw.polygon(surf, rlighter, pts_left, 1)
        pygame.draw.polygon(surf, rlighter, pts_right, 1)

    # ── PENCERELER ──────────────────────────────────────────────────
    for (xo, yb, w, h, lit) in shop["windows"]:
        rx, ry = ox + xo, gy(yb + h)
        # cam iç
        pygame.draw.rect(surf, (12, 14, 10), (rx, ry, w, h))
        if lit:
            la = int(70 + 25 * math.sin(global_t * 0.05 + xo * 0.3))
            wg = pygame.Surface((w, h), pygame.SRCALPHA)
            pygame.draw.rect(wg, (220, 165, 55, la), (0, 0, w, h))
            surf.blit(wg, (rx, ry))
        # çerçeve
        pygame.draw.rect(surf, (90, 65, 30), (rx, ry, w, h), 2)
        # çapraz bölme
        pygame.draw.line(surf, (80, 58, 25), (rx + w//2, ry), (rx + w//2, ry+h), 1)
        pygame.draw.line(surf, (80, 58, 25), (rx, ry + h//2), (rx+w, ry+h//2), 1)

    # ── KAPI ────────────────────────────────────────────────────────
    dxo, dyb, dw, dh = shop["door"]
    drx, dry = ox + dxo, gy(dyb + dh)
    pygame.draw.rect(surf, (8, 7, 5), (drx, dry, dw, dh))
    # kapı çerçeve
    pygame.draw.rect(surf, (100, 65, 25), (drx, dry, dw, dh), 2)
    # kapı tokmağı
    pygame.draw.circle(surf, (160, 120, 40), (drx + dw - 7, dry + dh//2), 4)
    pygame.draw.circle(surf, (200, 160, 60), (drx + dw - 7, dry + dh//2), 2)

    # ── TABELA ──────────────────────────────────────────────────────
    txt, txo, tyb = shop["label"]
    ts  = font_tiny.render(txt, True, (240, 220, 100))
    tbg_w = ts.get_width() + 14
    tbx, tby = ox + txo - tbg_w//2, gy(tyb + 18)
    pygame.draw.rect(surf, (20, 14, 6), (tbx, tby, tbg_w, 18), border_radius=2)
    pygame.draw.rect(surf, (140, 100, 30), (tbx, tby, tbg_w, 18), 1, border_radius=2)
    surf.blit(ts, (tbx + 7, tby + 3))

    # ── BACA ────────────────────────────────────────────────────────
    if shop["chimney"]:
        cxo, cyb, cw, ch, ccol = shop["chimney"]
        crx, cry = ox + cxo, gy(cyb + ch)
        pygame.draw.rect(surf, ccol, (crx, cry, cw, ch))
        darker = tuple(max(0, c - 20) for c in ccol)
        pygame.draw.rect(surf, darker, (crx - 2, cry - 4, cw + 4, 8), border_radius=2)

    # ── EKSTRALAR ───────────────────────────────────────────────────
    for extra in shop["extras"]:
        if extra[0] == "barrel_left":
            draw_fire_barrel(surf, ox - 18, ground - 110, global_t)
        elif extra[0] == "barrel_right":
            # en geniş parça genişliğini tahmin et
            max_w = max(p[3] for p in shop["parts"] if len(p) > 3 and p[3] > 0)
            draw_fire_barrel(surf, ox + max_w + 18, ground - 110, global_t)
        elif extra[0] == "scrap_right":
            max_w = max(p[3] for p in shop["parts"] if len(p) > 3 and p[3] > 0)
            draw_scrap_pile(surf, ox + max_w + 10, ground - 84, hash(shop["npc"]) % 8)
        elif extra[0] == "scrap_left":
            draw_scrap_pile(surf, ox - 22, ground - 84, hash(shop["npc"]) % 8 + 1)
        elif extra[0] == "antenna":
            axo, ayb = extra[1], extra[2]
            ax, ay = ox + axo, gy(ayb + 45)
            pygame.draw.line(surf, (80, 90, 70), (ax, ay + 45), (ax, ay), 2)
            pygame.draw.line(surf, (80, 90, 70), (ax, ay + 10), (ax - 16, ay + 20), 1)
            pygame.draw.line(surf, (80, 90, 70), (ax, ay + 10), (ax + 12, ay + 22), 1)
            pulse = int(30 + 22 * math.sin(global_t * 0.1))
            ag = pygame.Surface((14, 14), pygame.SRCALPHA)
            pygame.draw.circle(ag, (100, 220, 30, pulse), (7, 7), 6)
            surf.blit(ag, (ax - 7, ay - 7))
        elif extra[0] == "rope":
            # çamaşır ipi
            rx1, ry1, rx2, ry2 = ox + extra[1], gy(extra[2]), ox + extra[3], gy(extra[4])
            for ri in range(12):
                t_ = ri / 11
                rpx = int(rx1 + (rx2 - rx1) * t_)
                rpy = int(ry1 + (ry2 - ry1) * t_ + math.sin(t_ * math.pi) * 14)
                if ri > 0:
                    prev_x = int(rx1 + (rx2 - rx1) * ((ri-1)/11))
                    prev_y = int(ry1 + (ry2 - ry1) * ((ri-1)/11) + math.sin(((ri-1)/11) * math.pi) * 14)
                    pygame.draw.line(surf, (90, 70, 50), (prev_x, prev_y), (rpx, rpy), 1)
                # ara sıra çamaşır parçası
                if ri % 3 == 1:
                    rc = [(180, 60, 40),(60, 80, 160),(200, 180, 60)][ri % 3]
                    pygame.draw.rect(surf, rc, (rpx - 4, rpy - 7, 8, 12))
        elif extra[0] == "wires":
            # elektrik kabloları
            rx1, ry1, rx2, ry2 = ox + extra[1], gy(extra[2]), ox + extra[3], gy(extra[4])
            for wi in range(3):
                sag = 8 + wi * 5
                pygame.draw.line(surf, (30, 35, 28),
                    (rx1, ry1 - wi*4), (rx1 + (rx2-rx1)//2, ry1 - wi*4 + sag), 1)
                pygame.draw.line(surf, (30, 35, 28),
                    (rx1 + (rx2-rx1)//2, ry1 - wi*4 + sag), (rx2, ry2 - wi*4), 1)
        elif extra[0] == "barbwire":
            bxo, by_, bw = extra[1], extra[2], extra[3]
            brx = ox + bxo
            bry = gy(by_)
            pygame.draw.line(surf, (80, 85, 95), (brx, bry), (brx + bw, bry), 2)
            for bi in range(0, bw, 10):
                pygame.draw.line(surf, (100, 105, 115),
                    (brx + bi, bry), (brx + bi + 5, bry - 6), 1)
                pygame.draw.line(surf, (100, 105, 115),
                    (brx + bi + 5, bry - 6), (brx + bi + 10, bry), 1)
        elif extra[0] == "searchlight":
            slxo, slyb = extra[1], extra[2]
            slx, sly = ox + slxo, gy(slyb + 10)
            sweep = math.sin(global_t * 0.015) * 60
            beam_end_x = int(slx + math.sin(math.radians(sweep)) * 180)
            beam_end_y = int(sly + 160)
            beam = pygame.Surface((400, HEIGHT), pygame.SRCALPHA)
            pygame.draw.polygon(beam, (200, 200, 160, 12),
                [(slx - ox + 200 - 5, sly),
                 (slx - ox + 200 + 5, sly),
                 (beam_end_x - ox + 200 + 22, beam_end_y),
                 (beam_end_x - ox + 200 - 22, beam_end_y)])
            surf.blit(beam, (ox - 200, 0))
            pygame.draw.rect(surf, (60, 65, 80), (slx - 8, sly - 6, 16, 10))
            pygame.draw.circle(surf, (220, 220, 180), (slx, sly), 4)


# ================================================================
# SOHBET PANELİ
# ================================================================
PANEL_W  = 740
PANEL_H  = 480
PANEL_X  = WIDTH  // 2 - PANEL_W // 2
PANEL_Y  = HEIGHT // 2 - PANEL_H // 2 - 30
INPUT_H  = 46
LH       = 20
MSG_PAD  = 8
TITLE_H  = 42
MSG_MAX_W = PANEL_W - 48

def build_msg_lines(history, npc_name):
    result = []
    for msg in history:
        is_user = msg["role"] == "user"
        col     = PLAYER_TXT if is_user else AI_COL
        prefix  = "Sen" if is_user else npc_name
        result.append((f"▸ {prefix}", (160, 155, 130), is_user))
        for ln in wrap_text(msg["text"], font_input, MSG_MAX_W):
            result.append((ln, col, is_user))
        result.append(("", col, is_user))
    return result

def draw_chat_panel(surf, npc, input_text, cursor_vis, global_t, scroll_offset=0):
    total_h = PANEL_H + INPUT_H + 20
    draw_rounded_rect_alpha(surf, (8, 10, 6), (PANEL_X, PANEL_Y, PANEL_W, total_h), radius=16, alpha=245)
    pygame.draw.rect(surf, npc.color, (PANEL_X, PANEL_Y, PANEL_W, total_h), 2, border_radius=16)

    draw_rounded_rect_alpha(surf, npc.color, (PANEL_X, PANEL_Y, PANEL_W, TITLE_H), radius=10, alpha=200)
    name_s = font_bold.render(f"💬  {npc.name}  —  Sohbet", True, WHITE)
    surf.blit(name_s, name_s.get_rect(centerx=PANEL_X + PANEL_W // 2, centery=PANEL_Y + TITLE_H // 2))
    esc_s = font_tiny.render("ESC → Kapat  |  ↑↓ Kaydır", True, (200, 190, 160))
    surf.blit(esc_s, (PANEL_X + PANEL_W - esc_s.get_width() - 10, PANEL_Y + 14))

    msg_x      = PANEL_X + 10
    msg_y_top  = PANEL_Y + TITLE_H + 6
    msg_area_h = PANEL_H - TITLE_H - 6

    all_lines      = build_msg_lines(npc.history, npc.name)
    total_lines_h  = len(all_lines) * (LH + 1)
    max_scroll     = max(0, total_lines_h - msg_area_h + 10)
    scroll_offset  = max(0, min(scroll_offset, max_scroll))

    clip_surf = pygame.Surface((PANEL_W - 20, msg_area_h), pygame.SRCALPHA)
    clip_surf.fill((0, 0, 0, 0))

    draw_y = -scroll_offset + 6
    for text, col, right in all_lines:
        if draw_y + LH > 0 and draw_y < msg_area_h:
            if text:
                ls = font_input.render(text, True, col)
                x  = (PANEL_W - 20 - ls.get_width() - 8) if right else 8
                clip_surf.blit(ls, (x, draw_y))
        draw_y += LH + 1

    surf.blit(clip_surf, (msg_x, msg_y_top))

    sep_y = PANEL_Y + PANEL_H
    pygame.draw.line(surf, npc.color, (PANEL_X + 10, sep_y), (PANEL_X + PANEL_W - 10, sep_y), 1)

    if npc.loading:
        dots = "." * (1 + (global_t // 18) % 3)
        ls   = font_bold.render(f"{npc.name} yazıyor{dots}", True, AI_COL)
        surf.blit(ls, (PANEL_X + 16, sep_y + 6))

    iy = PANEL_Y + PANEL_H + 6
    pygame.draw.rect(surf, (10, 14, 8),  (PANEL_X + 8, iy, PANEL_W - 16, INPUT_H), border_radius=10)
    pygame.draw.rect(surf, INPUT_BOR,    (PANEL_X + 8, iy, PANEL_W - 16, INPUT_H), 2, border_radius=10)

    if not input_text and not npc.loading:
        ph = font_input.render("Mesajını yaz... (ENTER gönder)", True, (70, 80, 50))
        surf.blit(ph, (PANEL_X + 20, iy + 14))

    ts = font_input.render(input_text[-60:], True, WHITE)
    surf.blit(ts, (PANEL_X + 20, iy + 14))
    if cursor_vis:
        cx = PANEL_X + 20 + font_input.size(input_text[-60:])[0]
        pygame.draw.line(surf, ACID_COL, (cx, iy + 8), (cx, iy + 38), 2)

    if total_lines_h > msg_area_h:
        bar_h = int(msg_area_h * msg_area_h / total_lines_h)
        bar_y = msg_y_top + int(scroll_offset * (msg_area_h - bar_h) / max_scroll) if max_scroll else msg_y_top
        pygame.draw.rect(surf, (50, 55, 35), (PANEL_X + PANEL_W - 8, msg_y_top, 4, msg_area_h), border_radius=2)
        pygame.draw.rect(surf, npc.color,    (PANEL_X + PANEL_W - 8, bar_y,     4, bar_h),      border_radius=2)

    return scroll_offset

# ================================================================
# ANA DÖNGÜ
# ================================================================
def main():
    try:
        pygame.scrap.init()
    except Exception:
        pass

    api_key = "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"

    # Platformlar kaldırıldı — kasaba düz zemin üstünde
    platforms = []

    player    = Player(180, HEIGHT - 200)
    camera    = Camera()
    npcs      = [NPC(d) for d in NPC_DATA]
    shops     = SHOP_DATA

    # Ateş varilleri — dükkanlar arasında, kasabanın sokak lambası gibi
    barrels = [200, 620, 900, 1760, 2050, 2660, 3500, 3800]

    # Hurda yığınları — sokak aralarında
    scraps = [
        (100,  HEIGHT - 84, 0), (720,  HEIGHT - 84, 1), (1060, HEIGHT - 84, 2),
        (1820, HEIGHT - 84, 3), (2720, HEIGHT - 84, 4), (3340, HEIGHT - 84, 5),
        (3700, HEIGHT - 84, 6),
    ]

    # Uyarı levhaları
    signs = [
        (80,   HEIGHT - 116, "TEHLİKE"),
        (1000, HEIGHT - 116, "BÖLGE-7"),
        (2800, HEIGHT - 116, "GERİ DÖN"),
        (3820, HEIGHT - 116, "ÇIKIŞ →"),
    ]

    # Kırık borular
    pipes = [280, 820, 1580, 2580, 3420]

    active_npc    = None
    chat_input    = ""
    scroll_offset = 0
    cursor_vis    = True
    cursor_t      = 0
    global_t      = 0
    hud_alpha     = 255.0

    # Açılış mesajı (iç ses)
    intro_lines = [
        "Vasis... Beni yendi. Ama buradayım.",
        "Burası neresi?  Çöplük mü?  Yoksa ölülerin dünyası mı?",
        "Paslı bir boru yanı başımda.  İlk silah."
    ]
    intro_timer  = 0
    intro_idx    = 0
    show_intro   = True

    running = True
    while running:
        clock.tick(FPS)
        global_t += 1
        cursor_t += 1
        if cursor_t % 28 == 0:
            cursor_vis = not cursor_vis

        # Açılış iç ses sayacı
        if show_intro:
            intro_timer += 1
            if intro_timer > 200:
                intro_timer = 0
                intro_idx += 1
                if intro_idx >= len(intro_lines):
                    show_intro = False

        # --- OLAYLAR ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == pygame.KEYDOWN:
                if active_npc and active_npc.in_talk:
                    if event.key == pygame.K_ESCAPE:
                        active_npc.in_talk = False
                        active_npc         = None
                        player.talking     = False
                        chat_input         = ""
                    elif event.key == pygame.K_UP:
                        scroll_offset = max(0, scroll_offset - 40)
                    elif event.key == pygame.K_DOWN:
                        scroll_offset += 40
                    elif event.key == pygame.K_RETURN:
                        msg = chat_input.strip()
                        if msg and not active_npc.loading:
                            active_npc.send_message(api_key, msg)
                            chat_input    = ""
                            scroll_offset = 9999
                    elif event.key == pygame.K_BACKSPACE:
                        chat_input = chat_input[:-1]
                    elif event.unicode and event.unicode.isprintable():
                        if len(chat_input) < 200:
                            chat_input += event.unicode
                else:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_e:
                        for npc in npcs:
                            if npc.near(player):
                                active_npc     = npc
                                npc.in_talk    = True
                                player.talking = True
                                chat_input     = ""
                                scroll_offset  = 9999
                                if not npc.history:
                                    npc.send_message(api_key, "Merhaba! (Bu sohbetin başlangıcı.)")
                                break

        # --- GÜNCELLE ---
        player.update(platforms)
        camera.update(player.cx, player.cy)
        if active_npc and getattr(active_npc, '_scroll_to_bottom', False):
            scroll_offset = 9999
            active_npc._scroll_to_bottom = False
        if hud_alpha > 0:
            hud_alpha = max(0, hud_alpha - 0.25)

        # --- ÇİZ ---
        draw_background(screen, camera.x, global_t)

        # Dükkanlar (NPC'lerden önce çizilmeli — arka plan)
        for shop in shops:
            draw_shop(screen, shop, camera.x, global_t)

        # Ateş varilleri (dükkan dışı, ara noktalarda)
        for bx in barrels:
            sx = bx - int(camera.x)
            if -80 < sx < WIDTH + 80:
                draw_fire_barrel(screen, sx, HEIGHT - 110, global_t)

        # Hurda yığınları
        for hx, hy, idx in scraps:
            sx = hx - int(camera.x)
            if -50 < sx < WIDTH + 50:
                draw_scrap_pile(screen, sx, hy, idx)

        # Kırık borular
        for px in pipes:
            draw_broken_pipe(screen, px, HEIGHT - 90, camera.x)

        # Uyarı levhaları
        for sx_, sy_, st in signs:
            draw_warning_sign(screen, sx_, sy_, st, camera.x)

        # NPC'ler
        for npc in npcs:
            npc.draw(screen, camera)

        # E ipucu
        for npc in npcs:
            if npc.near(player) and not npc.in_talk:
                hx_, hy_ = camera.apply(int(npc.x + npc.W // 2), int(npc.y - 36))
                hint = font_small.render("[E] Konuş", True, HINT_COL)
                screen.blit(hint, hint.get_rect(centerx=hx_, centery=hy_))

        # Oyuncu
        player.draw(screen, camera)

        # Sohbet paneli
        if active_npc and active_npc.in_talk:
            ov = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            ov.fill((0, 0, 0, 120))
            screen.blit(ov, (0, 0))
            scroll_offset = draw_chat_panel(screen, active_npc, chat_input, cursor_vis, global_t, scroll_offset)

        # Zemin ön çizgi
        pygame.draw.rect(screen, (20, 14, 8), (0, HEIGHT - 6, WIDTH, 6))

        # HUD — kontrol ipucu
        if hud_alpha > 0:
            msg = "← → Hareket   |   E → NPC ile konuş   |   ESC → Çıkış"
            hs  = font_small.render(msg, True, (200, 210, 160))
            hbg = pygame.Surface((hs.get_width() + 20, hs.get_height() + 10), pygame.SRCALPHA)
            hbg.fill((0, 0, 0, int(hud_alpha * 0.6)))
            screen.blit(hbg, (WIDTH // 2 - hbg.get_width() // 2, HEIGHT - 48))
            hs.set_alpha(int(hud_alpha))
            screen.blit(hs, hs.get_rect(centerx=WIDTH // 2, centery=HEIGHT - 38))

        # Başlık
        title = font_title.render("✦  FRAGMENTIA  ✦", True, (160, 200, 60))
        screen.blit(title, title.get_rect(centerx=WIDTH // 2, top=12))
        sub   = font_tiny.render("Bölüm 1.2  —  Çöplükte Uyanış", True, (110, 140, 50))
        screen.blit(sub,  sub.get_rect(centerx=WIDTH // 2, top=46))

        # Açılış iç ses (Nebula bilinci)
        if show_intro and intro_idx < len(intro_lines):
            line = intro_lines[intro_idx]
            fade = min(255, intro_timer * 4) if intro_timer < 60 else max(0, 255 - (intro_timer - 140) * 4)
            box_w = font_main.size(line)[0] + 40
            box_s = pygame.Surface((box_w, 36), pygame.SRCALPHA)
            box_s.fill((0, 0, 0, max(0, min(255, int(fade * 0.6)))))
            screen.blit(box_s, (WIDTH // 2 - box_w // 2, HEIGHT // 2 - 18))
            ts = font_main.render(line, True, (140, 200, 255))
            ts.set_alpha(fade)
            screen.blit(ts, ts.get_rect(centerx=WIDTH // 2, centery=HEIGHT // 2))

        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
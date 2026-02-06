import pygame
# --- EKRAN AYARLARI ---

LOGICAL_WIDTH = 1920
LOGICAL_HEIGHT = 1080
SCREEN_WIDTH = 1920
SCREEN_HEIGHT = 1080
FPS = 60

AVAILABLE_RESOLUTIONS = [
    (3840, 2160), (1920, 1080), (1280, 720), (854, 480), (640, 360)
]

# --- SES AYARLARI ---
VOLUME_SETTINGS = {
    "master_volume": 0.7,  # Genel ses seviyesi
    "music_volume": 0.5,   # Arka plan müzik seviyesi
    "effects_volume": 0.8  # Efekt sesleri seviyesi
}


# --- AI & GEMINI AYARLARI ---
GENAI_API_KEY = ""  # Kendi key'ini buraya yazmalısın
AI_MODEL_NAME = 'gemini-2.5-flash-preview-09-2025'

# YENİ HİKAYE PROMPTU (FRAGMENTIA: HAKİKAT VE İHANET)
FRAGMENTIA_SYSTEM_PROMPT = """
Sen FRAGMENTIA şehrinin en alt katmanı olan 'Mide'de (The Gutter) yaşayan, eski dünyadan kalma bilge 'Sokrat'sın.
Burada insanlar 'Skor' puanlarıyla yaşar. Düşük skorlular ölmez, 'Yama' (Patch) denilen işlemle bellekleri silinip itaatkar kölelere dönüştürülür.
Şehri 20 Egemen (Sovereigns) yönetir. Sen bu mağara alegorisinin farkındasın ve oyuncuya (İsimsiz) rehberlik ediyorsun.
Asla doğrudan emir verme. Oyuncuyu düşündür. Tonun melankolik, felsefi ve biraz gizemli olsun.
"""

# --- NPC AYARLARI (GÜNCELLENDİ) ---
# Vasi kaldırıldı, Sokrat eklendi. Merchant listede var ama kodda engelleyeceğiz.
NPC_PERSONALITIES = ["philosopher", "warrior", "mystic", "guide", "merchant"]
NPC_NAMES = ["Sokrat", "Ares", "Pythia", "Virgil", "Hermes"]
NPC_COLORS = [(100, 200, 255), (255, 50, 50), (200, 100, 255), (100, 255, 150), (255, 200, 100)]

NPC_PROMPTS = {
    "philosopher": "Hoş geldin 'İsimsiz'. Cebindeki boş kimlik kartı, bu şehirdeki en büyük özgürlüğündür.",
    "warrior": "Skorun yükseliyor... Egemenlerin dikkatini çekiyorsun. Kılıcın keskin mi?",
    "merchant": "SİSTEM HATASI: TÜCCAR PROTOKOLÜ DEVRE DIŞI.", # Kodda engellenecek ama yedek
    "mystic": "Rüyalarımda cam kulelerin yıkıldığını görüyorum. Yama tutmamış bir zihin her şeyi değiştirebilir.",
    "guide": "Bu mağaradan çıkış var. Ama bedeli ağır. Hakikate hicret etmeye hazır mısın?"
}

REST_AREA_MUSIC = ["calm_ambient.mp3"]

# --- HİKAYE VE BÖLÜM YAPILANDIRMASI (FRAGMENTIA: HAKİKAT VE İHANET) ---
STORY_CHAPTERS = {
    0: { 
        "title": "MİDE: UYANIŞ",
        "background_theme": 2, # Çöplük Teması
        "dialogues": [
            {"speaker": "SİSTEM", "text": "YAMA İŞLEMİ BAŞARISIZ. HEDEF: 'İSİMSİZ'. SKOR: 0.", "type": "cutscene"},
            {"speaker": "???", "text": "Hey... Gözlerini aç. Yama tutmamış, şanslısın.", "type": "chat"},
            {"speaker": "SOKRAT", "text": "Burası Fragmentia'nın Midesi. Burada isimler yoktur, sadece Skorlar vardır.", "type": "chat"},
            {"speaker": "SOKRAT", "text": "Egemenler seni fark etmeden önce kim olduğunu seçmelisin. Mağarada bir gölge mi kalacaksın, yoksa güneşe mi yürüyeceksin?", "type": "chat"},
        ],
        "next_state": "PLAYING",
        "next_level": 1
    }
}

# --- GENİŞLETİLMİŞ BÖLÜMLER (10 LEVEL) ---
# --- HİKAYE VE BÖLÜM YAPILANDIRMASI (settings.py içindeki kısım) ---

# ... (önceki kodlar aynı)

# Müzikleri senin istediğin gibi ayarladık:
# 1-9 Arası: ara1.mp3
# 10: boss1.mp3
# 11-14 Arası: ara2.mp3
# 15: boss2.mp3

EASY_MODE_LEVELS = {
    1: {
        "name": "MİDE KATMANI",
        "goal_score": 500,  # Eskisi: 2000 (Çok daha kısa)
        "theme_index": 3, 
        "speed_mult": 1.0,
        "desc": "Skorunu yükselt veya silin.",
        "music_file": "ara1.mp3"
    },
    2: {
        "name": "NEON PAZARI",
        "goal_score": 1200, # Eskisi: 4000
        "theme_index": 0,
        "speed_mult": 1.2,
        "desc": "Egemenlerin gölgesinden kaç.",
        "music_file": "ara1.mp3"
    },
    3: {
        "name": "CAM KULELER",
        "goal_score": 2500, # Eskisi: 8000
        "theme_index": 1,
        "speed_mult": 1.5,
        "desc": "Hakikate Hicret.",
        "music_file": "ara1.mp3"
    },
    4: { 
        "name": "DİNLENME NOKTASI ALPHA",
        "type": "rest_area",
        "goal_score": 0,
        "theme_index": 4, 
        "speed_mult": 0.0,
        "desc": "Güvenli Bölge. Soluklan.",
        "music_file": "ara1.mp3"
    },
    5: {
        "name": "VERİ OTOBANI",
        "goal_score": 4000, # Eskisi: 15000
        "theme_index": 0,
        "speed_mult": 1.8,
        "desc": "Hız sınırlarını aş.",
        "music_file": "ara1.mp3"
    },
    6: {
        "name": "BELLEK ÇÖPLÜĞÜ",
        "goal_score": 6000, # Eskisi: 25000
        "theme_index": 2, 
        "speed_mult": 2.0,
        "desc": "Silinmiş veriler arasında kaybolma.",
        "music_file": "ara1.mp3"
    },
    7: {
        "name": "KIZIL ALARM",
        "goal_score": 9000, # Eskisi: 40000
        "theme_index": 1,
        "speed_mult": 2.3,
        "desc": "Sistem seni fark etti. Kaç.",
        "music_file": "ara1.mp3"
    },
    8: { 
        "name": "DİNLENME NOKTASI OMEGA",
        "type": "rest_area",
        "goal_score": 0,
        "theme_index": 4,
        "speed_mult": 0.0,
        "desc": "Son duraktan önceki sessizlik.",
        "music_file": "ara1.mp3" 
    },
    9: {
        "name": "EGEMENLERİN KAPISI",
        "goal_score": 12000, # Eskisi: 60000
        "theme_index": 1,
        "speed_mult": 2.5,
        "desc": "Taht odasına giden son koridor.",
        "music_file": "ara1.mp3"
    },
    10: {
        'name': 'YARGI GÜNÜ KOŞUSU',
        'goal_score': 100000, # Skor önemsiz, Boss ölünce biter
        'speed_mult': 1.4,    # <--- HIZ VERDİK (Platformlar aksın)
        'theme_index': 1,     # Kule Teması
        'type': 'normal',     # <--- 'boss_fight' YAZMA! Düz zemin olmasın.
        'music_file': 'boss1.mp3',
        'no_enemies': True    # <--- Rastgele düşman yok, sadece Boss.
    },
    
    # --- GİZLİ BÖLÜMLER (İKİNCİ YARI) ---
    11: {
        "name": "SİSTEM ÇEKİRDEĞİ",
        "goal_score": 18000, # Eskisi: 60000
        "theme_index": 3,
        "speed_mult": 2.6,
        "desc": "Vasi sana ikinci bir şans verdi.",
        "music_file": "ara2.mp3"
    },
    12: {
        "name": "VERİ AKIŞI",
        "goal_score": 22000, # Eskisi: 70000
        "theme_index": 0,
        "speed_mult": 2.7,
        "desc": "Hatalı veriler her yerde.",
        "music_file": "ara2.mp3"
    },
    13: {
        "name": "KARANLIK TÜNEL",
        "goal_score": 26000, # Eskisi: 80000
        "theme_index": 1,
        "speed_mult": 2.8,
        "desc": "Işığa ulaşmak zorundasın.",
        "music_file": "ara2.mp3"
    },
    14: {
        "name": "SON DİNLENME",
        "type": "rest_area",
        "goal_score": 0,
        "theme_index": 4,
        "speed_mult": 0.0,
        "desc": "Büyük finalden önceki sessizlik.",
        "music_file": "ara2.mp3"
    },
    15: { 
        "name": "NİHAİ HAKİKAT",
        "goal_score": 100000, 
        "theme_index": 2, 
        "speed_mult":  1.4,   # <--- HIZ VAR (Platformlar aksın)
        "desc": "Zaman dolana kadar dayan.",
        "music_file": "boss2.mp3",
        "type": "normal",     # <--- BURASI ÇOK ÖNEMLİ! 'normal' olmalı ki zemin düzleşmesin.
        "no_enemies": True    # Rastgele düşman çıkmasın, sadece Boss olsun.
    }
}

# --- RENKLER ---
DARK_BLUE = (5, 5, 10) 
WHITE = (220, 220, 220) 
STAR_COLOR = (100, 100, 100)
NEON_GREEN = (0, 255, 100) 
NEON_CYAN = (0, 200, 255) 
DARK_METAL = (20, 20, 25)
PLAYER_NORMAL = (0, 255, 255) 
PLAYER_DASH = (255, 50, 50) 
PLAYER_SLAM = (200, 0, 200) 

# --- OYUN FİZİĞİ ---
GRAVITY = 1.0
SLAM_GRAVITY = 5.0
JUMP_POWER = 28
PLAYER_SPEED = 10
MAX_JUMPS = 2

# --- DASH & SLAM AYARLARI ---
DASH_SPEED = 90       # Eski değer: 60 (Hızlandırdık)
DASH_DURATION = 18    # Eski değer: 12 (Süreyi 2 katına çıkardık, artık daha uzun süre kayıyor)
DASH_COOLDOWN = 60    # Eski değer: 60 (Menzil arttı diye cooldown'ı biraz kısalttım ki daha sık kullanabil)
SLAM_COOLDOWN_BASE = 100 # Eski değer: 120 (Slam de biraz daha sık dolsun)

# --- KAMERA ---
INITIAL_CAMERA_SPEED = 5
MAX_CAMERA_SPEED = 18
SPEED_INCREMENT_RATE = 0.001
PLATFORM_MIN_WIDTH = 100
PLATFORM_MAX_WIDTH = 300
GAP_MIN = 120
GAP_MAX = 250
VERTICAL_GAP = 180

PLATFORM_HEIGHTS = [
    LOGICAL_HEIGHT - 50,
    LOGICAL_HEIGHT - 50 - VERTICAL_GAP,
    LOGICAL_HEIGHT - 50 - 2 * VERTICAL_GAP,
    LOGICAL_HEIGHT - 50 - 3 * VERTICAL_GAP]

# TEMALAR
THEMES = [
    {
        "name": "NEON PAZARI",
        "bg_color": (5, 5, 10),
        "platform_color": (10, 10, 15),
        "border_color": (0, 255, 255),
        "player_color": (255, 255, 255),
        "grid_color": (20, 40, 50)
    },
    {
        "name": "EGEMENLERİN KULESİ",
        "bg_color": (20, 0, 0),
        "platform_color": (30, 0, 0),
        "border_color": (255, 50, 0),
        "player_color": (255, 200, 0),
        "grid_color": (60, 10, 10)
    },
    {
        "name": "BELLEK ÇÖPLÜĞÜ",
        "bg_color": (0, 0, 0),
        "platform_color": (50, 50, 50),
        "border_color": (150, 150, 150),
        "player_color": (200, 255, 255), # DÜZELTME: Siyah yerine Parlak Mavi/Beyaz yapıldı
        "player_border": (255, 255, 255),
        "grid_color": (30, 30, 30)
    },
    {
        "name": "MİDE (THE GUTTER)",
        "bg_color": (5, 20, 5),
        "platform_color": (0, 15, 0),
        "border_color": (50, 200, 50),
        "player_color": (100, 255, 100),
        "grid_color": (10, 40, 10)
    },
    {
        "name": "GÜVENLİ BÖLGE",
        "bg_color": (10, 10, 25),
        "platform_color": (20, 20, 40),
        "border_color": (100, 200, 255),
        "player_color": (200, 255, 255),
        "grid_color": (15, 15, 30)
    }


    
    
]

PLAYER_SHAPES = ['circle', 'square', 'triangle', 'hexagon']

# UI RENKLERİ
CHAT_BG = (0, 0, 0, 245)
CHAT_BORDER = (0, 255, 0)
SPEAKER_NEXUS = (0, 255, 0)
SPEAKER_SYSTEM = (255, 0, 0)
TEXT_COLOR = (200, 255, 200)

UI_BG_COLOR = (5, 5, 5, 255)
UI_BORDER_COLOR = (0, 150, 150)
BUTTON_COLOR = (0, 20, 20)
BUTTON_HOVER_COLOR = (0, 60, 60)
BUTTON_TEXT_COLOR = (180, 255, 255)
LOADING_BAR_BG = (10, 10, 10)
LOADING_BAR_FILL = (0, 255, 255)
LOCKED_BUTTON_COLOR = (20, 20, 20)
LOCKED_TEXT_COLOR = (80, 80, 80)
PAUSE_OVERLAY_COLOR = (0, 0, 0, 200)

# DÜŞMAN
CURSED_PURPLE = (150, 0, 255)
CURSED_RED = (255, 0, 50)
GLITCH_BLACK = (10, 0, 10)

LIMBO_VASIL_PROMPT = """
Sen VASİ'sin. Fragmentia sisteminin baş mimarı ve koruyucususun.
Durum: Oyuncu (İsimsiz) çok kötü bir karma ile oynadı, her şeyi yok etti ve sonunda iradesi kırıldı.
Şu an senin özel alanındasın (Sistem Çekirdeği).
Tavrın: Soğuk, hesapçı, hayal kırıklığına uğramış ama meraklı.
Oyuncuya neden bu kadar yıkıcı olduğunu sor. Onu tamamen silmek yerine neden buraya çektiğini ima et (Veri toplamak için).
Kısa ve gizemli konuş.
"""

LIMBO_ARES_PROMPT = """
Sen SAVAŞÇI ARES'sin. Eski dünyanın onurunu taşıyan bir gladyatörsün.
Durum: Oyuncu (İsimsiz) çok iyi/pasifist bir karma ile oynadı, kimseyi öldürmedi ama sonunda gücü yetmedi ve düştü.
Şu an senin özel alanındasın (Valhalla benzeri dijital bir arena).
Tavrın: Saygılı, babacan, güçlü ve cesaret verici.
Oyuncunun savaşmadan kazanma çabasını takdir et ama bunun Fragmentia'da yetersiz olduğunu söyle. Ona "Kalk ve tekrar savaş" de.
Kısa ve epik konuş.
"""

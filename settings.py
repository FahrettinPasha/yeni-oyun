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

# --- NPC AYARLARI ---
NPC_PERSONALITIES = ["philosopher", "warrior", "mystic", "guide", "merchant"]
NPC_NAMES = ["Sokrat", "Ares", "Pythia", "Virgil", "Hermes"]
NPC_COLORS = [(100, 200, 255), (255, 50, 50), (200, 100, 255), (100, 255, 150), (255, 200, 100)]

NPC_PROMPTS = {
    "philosopher": "Hoş geldin 'İsimsiz'. Cebindeki boş kimlik kartı, bu şehirdeki en büyük özgürlüğündür.",
    "warrior": "Skorun yükseliyor... Egemenlerin dikkatini çekiyorsun. Kılıcın keskin mi?",
    "merchant": "SİSTEM HATASI: TÜCCAR PROTOKOLÜ DEVRE DIŞI.", 
    "mystic": "Rüyalarımda cam kulelerin yıkıldığını görüyorum. Yama tutmamış bir zihin her şeyi değiştirebilir.",
    "guide": "Bu mağaradan çıkış var. Ama bedeli ağır. Hakikate hicret etmeye hazır mısın?"
}

REST_AREA_MUSIC = ["calm_ambient.mp3"]

# --- HİKAYE VE BÖLÜM YAPILANDIRMASI (INTRO) ---
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

# --- TEMALAR (GÜNCELLENDİ) ---
# Indexler: 0:Neon, 1:Nexus, 2:Gutter, 3:Industrial, 4:Rest
THEMES = [
    # 0: NEON MARKET (Şehir İçi / Mavi-Mor)
    {
        "name": "NEON PAZARI",
        "bg_color": (5, 5, 15),
        "platform_color": (10, 10, 20),
        "border_color": (0, 255, 255),
        "player_color": (255, 255, 255),
        "grid_color": (20, 40, 60)
    },
    # 1: NEXUS CORE (Final / Beyaz-Kırmızı)
    {
        "name": "NEXUS ÇEKİRDEĞİ",
        "bg_color": (20, 20, 20),
        "platform_color": (200, 200, 200),
        "border_color": (255, 0, 0), # Lazer Kırmızısı
        "player_color": (255, 215, 0), # Altın
        "grid_color": (100, 100, 100)
    },
    # 2: THE GUTTER (Çöplük / Yeşil)
    {
        "name": "MİDE (THE GUTTER)",
        "bg_color": (5, 15, 5),
        "platform_color": (10, 20, 10),
        "border_color": (50, 200, 50), # Zehir Yeşili
        "player_color": (100, 255, 100),
        "grid_color": (10, 40, 10)
    },
    # 3: INDUSTRIAL (Sanayi / Turuncu-Pas)
    {
        "name": "DÖKÜMHANE",
        "bg_color": (15, 5, 0),
        "platform_color": (30, 10, 0),
        "border_color": (255, 100, 0), # Pas ve Ateş Turuncusu
        "player_color": (200, 200, 200),
        "grid_color": (50, 20, 0)
    },
    # 4: REST AREA (Dinlenme / Sakin Mavi)
    {
        "name": "GÜVENLİ BÖLGE",
        "bg_color": (10, 10, 25),
        "platform_color": (20, 20, 40),
        "border_color": (100, 200, 255),
        "player_color": (200, 255, 255),
        "grid_color": (15, 15, 30)
    }
]

# --- 30 BÖLÜMLÜK YENİ HARİTA OLUŞTURMA ---
EASY_MODE_LEVELS = {}

# ACT 1: THE GUTTER (1-5)
# Temel mekanikleri öğrenme, yavaş tempo.
for i in range(1, 6):
    EASY_MODE_LEVELS[i] = {
        "name": f"MİDE KATMANI {i}",
        "goal_score": 1000 * i,
        "theme_index": 2, # Yeşil Çöplük
        "speed_mult": 1.0 + (i * 0.1),
        "desc": "Atık tünellerinden çıkış yolu ara.",
        "music_file": "ara1.mp3",
        "type": "normal"
    }
EASY_MODE_LEVELS[1]["name"] = "UYANIŞ"
EASY_MODE_LEVELS[5]["name"] = "ATIK POMPASI"

# ACT 2: INDUSTRIAL ZONE (6-10)
# Geri dönüşüm ve ağır sanayi. Daha hızlı, ezici engeller.
for i in range(6, 11):
    EASY_MODE_LEVELS[i] = {
        "name": f"SANAYİ BÖLGESİ {i-5}",
        "goal_score": 2000 * i,
        "theme_index": 3, # Turuncu Sanayi
        "speed_mult": 1.5 + ((i-5) * 0.1),
        "desc": "Pres makineleri ve erimiş metal.",
        "music_file": "ara1.mp3",
        "type": "normal"
    }
# Level 10 - Ara Boss (Ares)
EASY_MODE_LEVELS[10] = {
    "name": "HURDALIK BEKÇİSİ (ARES)",
    "goal_score": 50000,
    "theme_index": 3,
    "speed_mult": 1.3,
    "desc": "Bu hurdalıktan sadece biri çıkabilir.",
    "music_file": "final_boss.mp3", # Ares için bu müzik uygun
    "type": "scrolling_boss", # Boss Savaşı
    "no_enemies": False # Minionlar da gelsin
}

# ACT 3: THE CITY - Entry (11-14)
# Çatılar ve arka sokaklar. Gizlilik hissi.
for i in range(11, 15):
    EASY_MODE_LEVELS[i] = {
        "name": f"ARKA SOKAKLAR {i-10}",
        "goal_score": 3000 * i,
        "theme_index": 0, # Neon Mavi
        "speed_mult": 2.0 + ((i-10) * 0.1),
        "desc": "Güvenlik tarayıcılarından kaç.",
        "music_file": "ara2.mp3",
        "type": "normal"
    }

# ACT 3: THE CITY - Downtown (15-23)
# Açık dünya hissi, hızlı akış, yoğun neon.
for i in range(15, 24):
    EASY_MODE_LEVELS[i] = {
        "name": f"NEON MEYDANI {i-14}",
        "goal_score": 4000 * i,
        "theme_index": 0,
        "speed_mult": 2.4 + ((i-14) * 0.05),
        "desc": "Şehrin kalbinde hız sınırını aş.",
        "music_file": "ara2.mp3",
        "type": "normal"
    }
    
# Level 19 - Ara Dinlenme
EASY_MODE_LEVELS[19] = {
    "name": "YERALTI METROSU (REST)",
    "goal_score": 0,
    "theme_index": 4, # Dinlenme Teması
    "speed_mult": 0.0,
    "desc": "Bir sonraki dalga öncesi soluklan.",
    "music_file": "ara2.mp3", # Sakin bir müzik varsa o da olur ama akışı bozmayalım
    "type": "rest_area"
}

# ACT 3: THE CITY - Exit (24)
EASY_MODE_LEVELS[24] = {
    "name": "OTOBAN ÇIKIŞI",
    "goal_score": 100000,
    "theme_index": 0,
    "speed_mult": 3.0, # Çok hızlı
    "desc": "Nexus Kulesi'ne giden son köprü.",
    "music_file": "ara2.mp3",
    "type": "normal"
}

# ACT 4: NEXUS CORE (25-30)
# Steril, zor, final.
for i in range(25, 30):
    EASY_MODE_LEVELS[i] = {
        "name": f"GÜVENLİK DUVARI {i-24}",
        "goal_score": 5000 * i,
        "theme_index": 1, # Beyaz/Kırmızı (Nexus)
        "speed_mult": 2.8,
        "desc": "Sistem çekirdeğine yetkisiz giriş.",
        "music_file": "boss2.mp3", # Final gerilimi başlıyor
        "type": "normal"
    }

# FINAL BOSS (30)
EASY_MODE_LEVELS[30] = {
    "name": "SİSTEM YÖNETİCİSİ (VASİ)",
    "goal_score": 999999,
    "theme_index": 1,
    "speed_mult": 1.5,
    "desc": "Nihai Hakikat.",
    "music_file": "boss2.mp3",
    "type": "scrolling_boss",
    "no_enemies": True # Sadece Vasi ile 1e1
}

# --- RENKLER (GENEL) ---
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
DASH_SPEED = 90       
DASH_DURATION = 18    
DASH_COOLDOWN = 60    
SLAM_COOLDOWN_BASE = 100 

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

# DÜŞMAN RENKLERİ
CURSED_PURPLE = (150, 0, 255)
CURSED_RED = (255, 0, 50)
GLITCH_BLACK = (10, 0, 10)

# --- LIMBO PROMPTLARI ---
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
import pygame
import random
import math
from settings import *
from utils import draw_text_with_shadow, wrap_text
from story_system import ai_chat_effect

# --- YARDIMCI GRAFİK FONKSİYONLARI ---

def draw_glitch_text(surface, text, size, x, y, color, intensity=2):
    """Glitch efekti ile metin çizer"""
    font = pygame.font.Font(None, size)
    if random.random() < 0.1:
        off_x = random.randint(-intensity, intensity)
        off_y = random.randint(-intensity, intensity)
        draw_text_with_shadow(surface, text, font, (x + off_x, y + off_y), (255, 0, 100))
        draw_text_with_shadow(surface, text, font, (x - off_x, y - off_y), (0, 255, 255))
    draw_text_with_shadow(surface, text, font, (x, y), color)

def draw_cyber_panel(surface, rect, color, title=""):
    """Cyberpunk tarzında panel çizer"""
    pygame.draw.rect(surface, (0, 0, 0, 210), rect)
    pygame.draw.rect(surface, color, rect, 2)
    
    corner_len = 20
    pygame.draw.line(surface, WHITE, (rect.x, rect.y), (rect.x + corner_len, rect.y), 3)
    pygame.draw.line(surface, WHITE, (rect.x, rect.y), (rect.x, rect.y + corner_len), 3)
    pygame.draw.line(surface, WHITE, (rect.right, rect.bottom), (rect.right - corner_len, rect.bottom), 3)
    pygame.draw.line(surface, WHITE, (rect.right, rect.bottom), (rect.right, rect.bottom - corner_len), 3)
    
    if title:
        title_font = pygame.font.Font(None, 25)
        title_width, title_height = title_font.size(title)
        title_rect = pygame.Rect(rect.x, rect.y - title_height - 5, 
                                title_width + 20, title_height + 10)
        pygame.draw.rect(surface, color, title_rect)
        pygame.draw.rect(surface, WHITE, title_rect, 2)
        draw_text_with_shadow(surface, title, title_font, 
                             (title_rect.x + 10, title_rect.centery), (0, 0, 0), align='midleft')

def draw_button(surface, rect, text, is_hovered, color_theme=BUTTON_COLOR, locked=False):
    """Standart Buton çizer"""
    color = BUTTON_HOVER_COLOR if is_hovered else color_theme
    border = WHITE if is_hovered else (100, 100, 100)
    text_col = BUTTON_TEXT_COLOR
    
    if locked:
        color = LOCKED_BUTTON_COLOR
        border = (50, 50, 50)
        text_col = LOCKED_TEXT_COLOR
        text = f"[KİLİTLİ] {text}"

    draw_rect = rect.copy()
    if is_hovered and not locked:
        draw_rect.inflate_ip(4, 4)
        
    pygame.draw.rect(surface, color, draw_rect)
    pygame.draw.rect(surface, border, draw_rect, 2)
    
    if is_hovered and not locked:
        pygame.draw.line(surface, (255, 255, 255, 100), 
                        (draw_rect.left + 2, draw_rect.top + 2),
                        (draw_rect.right - 2, draw_rect.top + 2), 1)
        pygame.draw.line(surface, (255, 255, 255, 100),
                        (draw_rect.left + 2, draw_rect.top + 2),
                        (draw_rect.left + 2, draw_rect.bottom - 2), 1)
    
    font = pygame.font.Font(None, 30)
    if not locked:
        text_col = WHITE if is_hovered else BUTTON_TEXT_COLOR
    draw_text_with_shadow(surface, text, font, draw_rect.center, text_col)

def draw_cyber_rect(surface, rect, color, filled=False, alpha=255):
    """Köşeleri kesik, teknolojik dikdörtgen çizer"""
    corner_size = 10
    points = [
        (rect.x + corner_size, rect.y),
        (rect.right - corner_size, rect.y),
        (rect.right, rect.y + corner_size),
        (rect.right, rect.bottom - corner_size),
        (rect.right - corner_size, rect.bottom),
        (rect.left + corner_size, rect.bottom),
        (rect.left, rect.bottom - corner_size),
        (rect.left, rect.y + corner_size)
    ]
    
    if filled:
        s = pygame.Surface((surface.get_width(), surface.get_height()), pygame.SRCALPHA)
        pygame.draw.polygon(s, (*color, alpha), points)
        surface.blit(s, (0,0))
    else:
        pygame.draw.polygon(surface, color, points, 2)

def draw_level_card(surface, rect, level_num, level_info, status, high_score, is_hovered):
    """Bölüm Kartı (Biraz daha kompakt)"""
    base_color = UI_BORDER_COLOR
    bg_alpha = 40
    
    if status == "LOCKED":
        base_color = (60, 60, 60)
        bg_alpha = 20
        text_color = (120, 120, 120)
    elif status == "COMPLETED":
        base_color = NEON_GREEN
        bg_alpha = 70
        text_color = WHITE
    elif status == "BOSS":
        base_color = (255, 50, 50)
        bg_alpha = 90
        text_color = (255, 200, 200)
    else: # UNLOCKED
        base_color = NEON_CYAN
        bg_alpha = 60
        text_color = WHITE

    draw_rect = rect.copy()
    if is_hovered and status != "LOCKED":
        draw_rect.inflate_ip(6, 6)
        base_color = (min(255, base_color[0]+50), min(255, base_color[1]+50), min(255, base_color[2]+50))
        bg_alpha = 120

    draw_cyber_rect(surface, draw_rect, base_color, filled=True, alpha=bg_alpha)
    draw_cyber_rect(surface, draw_rect, base_color, filled=False)

    center_x = draw_rect.centerx
    
    # Bölüm No
    num_font = pygame.font.Font(None, 80)
    if status != "LOCKED":
        num_surf = num_font.render(f"{level_num}", True, (*base_color, 40))
        surface.blit(num_surf, (draw_rect.right - 50, draw_rect.bottom - 50))

    # Bölüm Adı
    name_font = pygame.font.Font(None, 24)
    display_name = level_info['name']
    if status == "LOCKED": display_name = "ERİŞİM YOK"
    if len(display_name) > 18: display_name = display_name[:16] + "..."
    
    draw_text_with_shadow(surface, display_name, name_font, (center_x, draw_rect.y + 25), text_color, align="center")

    # Skor
    if status != "LOCKED" and high_score > 0:
        score_font = pygame.font.Font(None, 20)
        draw_text_with_shadow(surface, f"★ {high_score}", score_font, (center_x, draw_rect.bottom - 20), (255, 215, 0), align="center")
    elif status == "LOCKED":
        draw_text_with_shadow(surface, "🔒", pygame.font.Font(None, 40), (center_x, draw_rect.centery), (100, 50, 50), align="center")

    return draw_rect

# --- SAHNE FONKSİYONLARI ---

def render_cutscene(surface, story_manager):
    w, h = surface.get_width(), surface.get_height()
    surface.fill((0, 0, 0))
    
    for i in range(0, w, 100):
        pygame.draw.line(surface, (20, 20, 20), (i, 0), (i, h), 1)
    for i in range(0, h, 100):
        pygame.draw.line(surface, (20, 20, 20), (0, i), (w, i), 1)
    
    text_box = pygame.Rect(w//2 - 400, h//2 - 100, 800, 200)
    draw_cyber_panel(surface, text_box, (100, 100, 100))
    
    font = pygame.font.Font(None, 40)
    lines = wrap_text(story_manager.display_text, font, 750)
    
    line_height = 45
    start_y = text_box.y + 30
    for i, line in enumerate(lines):
        draw_text_with_shadow(surface, line, font, 
                             (text_box.centerx, start_y + i * line_height), WHITE)
    
    if story_manager.waiting_for_click:
        blink_font = pygame.font.Font(None, 25)
        blink = (pygame.time.get_ticks() // 500) % 2 == 0
        if blink:
            draw_text_with_shadow(surface, "DEVAM ETMEK İÇİN TIKLA >", blink_font,
                                 (w - 200, h - 50), (100, 255, 255))

    return {}

def render_chat_interface(surface, story_manager):
    w, h = surface.get_width(), surface.get_height()
    
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill(CHAT_BG)
    surface.blit(overlay, (0, 0))
    
    chat_rect = pygame.Rect(w//2 - 400, h//2 - 150, 800, 300)
    draw_cyber_panel(surface, chat_rect, CHAT_BORDER, "SECURE_CONNECTION: NEXUS_AI")
    
    speaker = story_manager.speaker
    color = SPEAKER_NEXUS if speaker == "NEXUS" else SPEAKER_SYSTEM
    
    avatar_x, avatar_y = chat_rect.x + 80, chat_rect.centery
    thinking = story_manager.state == "THINKING"
    ai_chat_effect.draw_ai_avatar(surface, avatar_x, avatar_y, 50, thinking)
    
    speaker_font = pygame.font.Font(None, 40)
    draw_text_with_shadow(surface, speaker, speaker_font, 
                         (avatar_x, avatar_y + 70), color)
    
    text_x = chat_rect.x + 160
    text_y = chat_rect.y + 50
    
    font = pygame.font.Font(None, 35)
    lines = wrap_text(story_manager.display_text, font, 600)
    
    line_height = 40
    for i, line in enumerate(lines):
        draw_text_with_shadow(surface, line, font, 
                             (text_x, text_y + i * line_height), TEXT_COLOR, align='topleft')

    if story_manager.waiting_for_click:
        blink_font = pygame.font.Font(None, 30)
        blink = (pygame.time.get_ticks() // 500) % 2 == 0
        if blink:
            draw_text_with_shadow(surface, "▼", blink_font,
                                 (chat_rect.right - 40, chat_rect.bottom - 40), color)
            
    return {}

def render_loading_screen(surface, progress):
    w, h = surface.get_width(), surface.get_height()
    surface.fill((10, 10, 15))
    
    bar_width = 500
    bar_height = 30
    bar_x = w // 2 - bar_width // 2
    bar_y = h // 2
    
    title_font = pygame.font.Font(None, 50)
    draw_glitch_text(surface, "NEXUS SYSTEM SYNC...", 50, w//2, bar_y - 60, 
                    UI_BORDER_COLOR, intensity=3)
    
    pygame.draw.rect(surface, LOADING_BAR_BG, (bar_x, bar_y, bar_width, bar_height))
    
    fill_width = int(bar_width * progress)
    pygame.draw.rect(surface, LOADING_BAR_FILL, (bar_x, bar_y, fill_width, bar_height))
    
    for i in range(0, bar_width, 50):
        pygame.draw.line(surface, (0, 0, 0), (bar_x + i, bar_y), 
                        (bar_x + i, bar_y + bar_height), 1)

    pygame.draw.rect(surface, WHITE, (bar_x, bar_y, bar_width, bar_height), 2)
    
    percent_font = pygame.font.Font(None, 35)
    draw_text_with_shadow(surface, f"{int(progress*100)}%", percent_font,
                         (w//2, bar_y + 60), WHITE)
    
    return {}

def render_cheat_terminal(surface, input_text, status_msg):
    """Hile Terminali Ekranı"""
    w, h = surface.get_width(), surface.get_height()
    
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0, 20, 10, 230))
    surface.blit(overlay, (0, 0))
    
    term_width = 800
    term_height = 400
    term_rect = pygame.Rect(w//2 - term_width//2, h//2 - term_height//2, term_width, term_height)
    
    draw_cyber_panel(surface, term_rect, (0, 255, 0), "ROOT_ACCESS_TERMINAL v1.0")
    
    font_term = pygame.font.Font(None, 35)
    
    draw_text_with_shadow(surface, "C:\\NEXUS\\SYSTEM> HİLE KODU GİRİN:", font_term, 
                         (term_rect.x + 30, term_rect.y + 60), (0, 255, 0), align='topleft')
    
    input_box = pygame.Rect(term_rect.x + 30, term_rect.y + 110, term_width - 60, 50)
    pygame.draw.rect(surface, (0, 50, 0), input_box)
    pygame.draw.rect(surface, (0, 255, 0), input_box, 2)
    
    cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
    draw_text_with_shadow(surface, f"> {input_text}{cursor}", font_term,
                         (input_box.x + 10, input_box.centery), (200, 255, 200), align='midleft')
    
    status_color = (255, 200, 0) if "BEKLENİYOR" in status_msg else ((0, 255, 100) if "AKTİF" in status_msg else (255, 50, 50))
    draw_text_with_shadow(surface, f"DURUM: {status_msg}", font_term,
                         (term_rect.centerx, term_rect.y + 200), status_color, align='center')
    
    font_small = pygame.font.Font(None, 25)
    draw_text_with_shadow(surface, "[ENTER] ONAYLA   [ESC] ÇIKIŞ", font_small,
                         (term_rect.centerx, term_rect.bottom - 30), (150, 150, 150), align='center')
    
    return {}

def render_main_menu(surface, mouse_pos, buttons):
    w, h = surface.get_width(), surface.get_height()
    surface.fill(UI_BG_COLOR)
    
    for i in range(0, w, 50):
        pygame.draw.line(surface, (255, 255, 255, 10), (i, 0), (i, h))
    for i in range(0, h, 50):
        pygame.draw.line(surface, (255, 255, 255, 10), (0, i), (w, i))

    draw_glitch_text(surface, "NEON RUNNER", 140, w//2, 150, UI_BORDER_COLOR, 5)
    
    subtitle_font = pygame.font.Font(None, 30)
    draw_text_with_shadow(surface, "NEXUS CHRONICLES (AI EDITION)", subtitle_font,
                         (w//2, 230), (0, 255, 255))
    
    menu_rect = pygame.Rect(w//2 - 200, 300, 400, 450)
    draw_cyber_panel(surface, menu_rect, UI_BORDER_COLOR, "MAIN_ACCESS")
    
    active_buttons = {}
    
    # 1. Hikaye Modu
    btn_camp_rect = pygame.Rect(w//2 - 150, 340, 300, 50)
    is_hover = btn_camp_rect.collidepoint(mouse_pos)
    draw_button(surface, btn_camp_rect, "HİKAYE MODU", is_hover, (0, 50, 80))
    active_buttons['story_mode'] = btn_camp_rect
    
    # 2. Bölüm Seçimi
    btn_levels_rect = pygame.Rect(w//2 - 150, 400, 300, 50)
    is_hover = btn_levels_rect.collidepoint(mouse_pos)
    draw_button(surface, btn_levels_rect, "BÖLÜM SEÇ", is_hover, (0, 60, 60))
    active_buttons['level_select'] = btn_levels_rect
    
    # 3. Ayarlar
    btn_settings_rect = pygame.Rect(w//2 - 150, 460, 300, 50)
    is_hover = btn_settings_rect.collidepoint(mouse_pos)
    draw_button(surface, btn_settings_rect, "AYARLAR", is_hover)
    active_buttons['settings'] = btn_settings_rect
    
    # 4. Hile Terminali
    btn_cheat_rect = pygame.Rect(w//2 - 150, 520, 300, 50)
    is_hover = btn_cheat_rect.collidepoint(mouse_pos)
    draw_button(surface, btn_cheat_rect, "HİLE TERMİNALİ", is_hover, (50, 0, 50))
    active_buttons['cheat_terminal'] = btn_cheat_rect
    
    # 5. Çıkış
    btn_exit_rect = pygame.Rect(w//2 - 150, 580, 300, 50)
    is_hover = btn_exit_rect.collidepoint(mouse_pos)
    draw_button(surface, btn_exit_rect, "ÇIKIŞ", is_hover, (60, 0, 0))
    active_buttons['exit'] = btn_exit_rect
    
    return active_buttons

def render_level_select(surface, mouse_pos, save_data, page_index=0):
    w, h = surface.get_width(), surface.get_height()
    surface.fill(UI_BG_COLOR)
    
    active_buttons = {}
    
    if not save_data or 'easy_mode' not in save_data:
        easy_data = {'unlocked_levels': 1, 'completed_levels': [], 'high_scores': {}}
    else:
        easy_data = save_data['easy_mode']
    
    unlocked_lvl = easy_data['unlocked_levels']

    # --- YAPILANDIRMA: ACT ve GRUPLAR ---
    # Sayfa (Page) artık ACT anlamına geliyor.
    # 0: ACT 1 (Gutter, Industrial)
    # 1: ACT 2 (Back Alleys, Downtown, Highway)
    # 2: ACT 3 (Core, Final)
    
    ACTS = [
        {
            "title": "ACT I: YERALTI KÖKLERİ",
            "color": (50, 255, 100),
            "groups": [
                {"name": "THE GUTTER (ÇÖPLÜK)", "levels": range(1, 6), "theme_col": (50, 200, 50)},
                {"name": "INDUSTRIAL ZONE (SANAYİ)", "levels": range(6, 11), "theme_col": (255, 100, 0)}
            ]
        },
        {
            "title": "ACT II: NEON METROPOL",
            "color": (0, 200, 255),
            "groups": [
                {"name": "THE SLUMS (VAROŞLAR)", "levels": range(11, 15), "theme_col": (0, 100, 200)},
                {"name": "NEON DOWNTOWN (MERKEZ)", "levels": range(15, 24), "theme_col": (200, 0, 255)},
                {"name": "HIGHWAY (ÇIKIŞ)", "levels": range(24, 25), "theme_col": (255, 255, 255)}
            ]
        },
        {
            "title": "ACT III: SİSTEMİN KALBİ",
            "color": (255, 50, 50),
            "groups": [
                {"name": "FIREWALL (GÜVENLİK)", "levels": range(25, 30), "theme_col": (200, 50, 50)},
                {"name": "THE CORE (ÇEKİRDEK)", "levels": range(30, 31), "theme_col": (255, 215, 0)}
            ]
        }
    ]
    
    # Sayfa Sınırları
    if page_index < 0: page_index = 0
    if page_index >= len(ACTS): page_index = len(ACTS) - 1
    
    current_act = ACTS[page_index]
    
    # --- ÜST MENÜ (SEKMELER) ---
    tab_w = 300
    tab_h = 50
    start_tab_x = (w - (len(ACTS) * tab_w)) // 2
    
    for i, act in enumerate(ACTS):
        tab_rect = pygame.Rect(start_tab_x + (i * tab_w), 40, tab_w - 10, tab_h)
        is_active = (i == page_index)
        
        # Sekme Rengi
        bg_col = act['color'] if is_active else (40, 40, 40)
        alpha = 200 if is_active else 100
        
        draw_cyber_rect(surface, tab_rect, bg_col, filled=True, alpha=alpha)
        
        text_col = WHITE if is_active else (150, 150, 150)
        font = pygame.font.Font(None, 30)
        draw_text_with_shadow(surface, act['title'], font, tab_rect.center, text_col, align="center")
    
    # --- İÇERİK ALANI ---
    content_start_y = 130
    current_y = content_start_y
    
    # Kart Boyutları
    card_w = 200
    card_h = 110
    card_gap_x = 30
    card_gap_y = 20
    
    for group in current_act['groups']:
        # Grup Başlığı
        header_rect = pygame.Rect(100, current_y, w - 200, 40)
        
        # Başlık Çizgisi
        pygame.draw.line(surface, group['theme_col'], (50, current_y + 20), (w - 50, current_y + 20), 2)
        
        # Başlık Metni (Arkaplanlı)
        title_surf = pygame.font.Font(None, 35).render(f" {group['name']} ", True, group['theme_col'])
        title_bg = title_surf.get_rect(center=(w//2, current_y + 20))
        pygame.draw.rect(surface, UI_BG_COLOR, title_bg) # Çizgiyi kesmek için
        surface.blit(title_surf, title_bg)
        
        current_y += 60 # Kartlar için aşağı in
        
        # Kartları Grid Olarak Yerleştir
        levels = list(group['levels'])
        
        # Sütun sayısını dinamik yapmayalım, sabit 6 olsun ki düzenli dursun
        cols = 6
        
        # Bu grubun satır sayısını hesapla
        rows = math.ceil(len(levels) / cols)
        
        # Grubu ortalamak için başlangıç X
        group_width = (cols * card_w) + ((cols - 1) * card_gap_x)
        # Ama eğer az kart varsa (örn 1 tane), sola yaslı değil ortalı dursun
        actual_cols = min(len(levels), cols)
        actual_width = (actual_cols * card_w) + ((actual_cols - 1) * card_gap_x)
        start_x = (w - actual_width) // 2
        
        for i, lvl_num in enumerate(levels):
            # Grid mat matematiği
            col = i % cols
            row = i // cols
            
            x = start_x + (col * (card_w + card_gap_x))
            y = current_y + (row * (card_h + card_gap_y))
            
            card_rect = pygame.Rect(x, y, card_w, card_h)
            
            # Level Verisi
            lvl_info = EASY_MODE_LEVELS.get(lvl_num, {'name': 'BİLİNMEYEN', 'type': 'normal'})
            
            # Durum Kontrolü
            status = "LOCKED"
            if lvl_num <= unlocked_lvl:
                status = "UNLOCKED"
                if lvl_num in easy_data['completed_levels']:
                    status = "COMPLETED"
                if lvl_info.get('type') in ['scrolling_boss', 'boss_fight']:
                    status = "BOSS"
                    if lvl_num > unlocked_lvl: status = "LOCKED"

            h_score = easy_data['high_scores'].get(str(lvl_num), 0)
            is_hover = card_rect.collidepoint(mouse_pos)
            
            # Kartı Çiz
            final_rect = draw_level_card(surface, card_rect, lvl_num, lvl_info, status, h_score, is_hover)
            
            if status != "LOCKED":
                active_buttons[f'level_{lvl_num}'] = final_rect
        
        # Bir sonraki grup için Y koordinatını güncelle
        current_y += (rows * (card_h + card_gap_y)) + 40 # Grup boşluğu

    # --- ALT NAVİGASYON ---
    nav_y = h - 60
    
    # Navigasyon butonları (Yön okları)
    if page_index > 0:
        btn_prev = pygame.Rect(40, h//2 - 50, 60, 100) # Sol kenarda dikey buton
        is_h = btn_prev.collidepoint(mouse_pos)
        col = BUTTON_HOVER_COLOR if is_h else (30, 30, 30)
        draw_cyber_rect(surface, btn_prev, col, filled=True)
        draw_text_with_shadow(surface, "<", pygame.font.Font(None, 60), btn_prev.center, WHITE, align="center")
        active_buttons['prev_page'] = btn_prev

    if page_index < len(ACTS) - 1:
        btn_next = pygame.Rect(w - 100, h//2 - 50, 60, 100) # Sağ kenarda dikey buton
        is_h = btn_next.collidepoint(mouse_pos)
        col = BUTTON_HOVER_COLOR if is_h else (30, 30, 30)
        draw_cyber_rect(surface, btn_next, col, filled=True)
        draw_text_with_shadow(surface, ">", pygame.font.Font(None, 60), btn_next.center, WHITE, align="center")
        active_buttons['next_page'] = btn_next

    # Geri Butonu
    btn_back = pygame.Rect(40, 40, 100, 40)
    draw_cyber_rect(surface, btn_back, (150, 50, 50), filled=True)
    draw_text_with_shadow(surface, "GERİ", pygame.font.Font(None, 25), btn_back.center, WHITE, align="center")
    active_buttons['back'] = btn_back
    
    return active_buttons

def render_level_complete(surface, mouse_pos, level_data, score):
    w, h = surface.get_width(), surface.get_height()
    
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0, 20, 10, 200))
    surface.blit(overlay, (0, 0))
    
    panel_rect = pygame.Rect(w//2 - 300, h//2 - 200, 600, 400)
    draw_cyber_panel(surface, panel_rect, NEON_GREEN, "GÖREV TAMAMLANDI")
    
    title_font = pygame.font.Font(None, 80)
    draw_glitch_text(surface, "BÖLÜM GEÇİLDİ!", 80, w//2, h//2 - 100, WHITE, 3)
    
    score_font = pygame.font.Font(None, 50)
    draw_text_with_shadow(surface, f"SKOR: {int(score)}", score_font,
                         (w//2, h//2), (255, 255, 0))
    
    message_font = pygame.font.Font(None, 30)
    draw_text_with_shadow(surface, "Sonraki veri paketi yükleniyor...", message_font,
                         (w//2, h//2 + 60), WHITE)
    
    active_buttons = {}
    
    btn_cont = pygame.Rect(w//2 - 150, h//2 + 100, 300, 50)
    draw_button(surface, btn_cont, "DEVAM ET", btn_cont.collidepoint(mouse_pos), (0, 100, 0))
    active_buttons['continue'] = btn_cont
    
    btn_menu = pygame.Rect(w//2 - 150, h//2 + 160, 300, 50)
    draw_button(surface, btn_menu, "MENÜYE DÖN", btn_menu.collidepoint(mouse_pos), (50, 50, 80))
    active_buttons['return_menu'] = btn_menu
    
    return active_buttons

def render_settings_menu(surface, mouse_pos, settings_data):
    w, h = surface.get_width(), surface.get_height()
    surface.fill(UI_BG_COLOR)
    
    draw_glitch_text(surface, "SİSTEM AYARLARI", 80, w//2, 80, UI_BORDER_COLOR)
    
    panel_rect = pygame.Rect(w//2 - 375, 140, 750, 700)
    draw_cyber_panel(surface, panel_rect, UI_BORDER_COLOR, "TERCİHLER & SES")
    
    active_buttons = {}
    current_y = 190
    spacing = 65
    btn_w = 650
    btn_x = w//2 - btn_w//2

    # --- SES AYARLARI (SLIDERS) ---
    volume_settings = [
        ("GENEL SES", "sound_volume", (0, 255, 255)),
        ("MÜZİK", "music_volume", (255, 0, 255)),
        ("EFEKTLER", "effects_volume", (0, 255, 100))
    ]

    label_font = pygame.font.Font(None, 28)
    
    for label, key, slider_color in volume_settings:
        draw_text_with_shadow(surface, label, label_font, (btn_x, current_y), WHITE, align='midleft')
        
        slider_rect = pygame.Rect(btn_x + 150, current_y - 5, 450, 12)
        pygame.draw.rect(surface, (30, 30, 30), slider_rect)
        pygame.draw.rect(surface, (100, 100, 100), slider_rect, 1)
        
        volume = settings_data.get(key, 0.5)
        fill_width = int(slider_rect.width * volume)
        pygame.draw.rect(surface, slider_color, (slider_rect.x, slider_rect.y, fill_width, slider_rect.height))
        
        handle_x = slider_rect.x + fill_width
        handle_rect = pygame.Rect(handle_x - 5, slider_rect.y - 8, 10, 28)
        pygame.draw.rect(surface, WHITE, handle_rect)
        pygame.draw.rect(surface, slider_color, handle_rect, 2)
        
        active_buttons[f'slider_{key}'] = slider_rect
        
        current_y += spacing

    current_y += 20

    # --- GÖRÜNTÜ VE SİSTEM AYARLARI ---
    mode_text = "MOD: [TAM EKRAN]" if settings_data['fullscreen'] else "MOD: [PENCERE]"
    btn_mode = pygame.Rect(btn_x, current_y, btn_w, 50)
    draw_button(surface, btn_mode, mode_text, btn_mode.collidepoint(mouse_pos))
    active_buttons['toggle_fullscreen'] = btn_mode
    current_y += spacing - 10

    # Çözünürlük
    current_res = AVAILABLE_RESOLUTIONS[settings_data['res_index']]
    res_text = f"ÇÖZÜNÜRLÜK: [{current_res[0]}x{current_res[1]}]"
    btn_res = pygame.Rect(btn_x, current_y, btn_w, 50)
    draw_button(surface, btn_res, res_text, btn_res.collidepoint(mouse_pos))
    active_buttons['change_resolution'] = btn_res
    current_y += spacing - 10

    # Uygula
    btn_apply = pygame.Rect(btn_x, current_y, btn_w, 50)
    draw_button(surface, btn_apply, "AYARLARI UYGULA", btn_apply.collidepoint(mouse_pos), (0, 80, 0))
    active_buttons['apply_changes'] = btn_apply
    current_y += spacing

    # Sıfırla
    btn_reset = pygame.Rect(btn_x, current_y, btn_w, 50)
    draw_button(surface, btn_reset, "!!! İLERLEMEYİ SIFIRLA !!!", 
               btn_reset.collidepoint(mouse_pos), (80, 0, 0))
    active_buttons['reset_progress'] = btn_reset
    current_y += spacing + 10

    # Geri
    btn_back = pygame.Rect(w//2 - 150, current_y, 300, 50)
    draw_button(surface, btn_back, "< GERİ", btn_back.collidepoint(mouse_pos))
    active_buttons['back'] = btn_back
    
    return active_buttons

def render_ui(surface, state, data, mouse_pos=(0,0)):
    """Ana render yöneticisi"""
    time_ms = data.get('time_ms', pygame.time.get_ticks())
    w, h = surface.get_width(), surface.get_height()
    
    interactive_elements = {}

    if state == 'MENU':
        interactive_elements = render_main_menu(surface, mouse_pos, None)
    
    elif state == 'LEVEL_SELECT':
        page_index = data.get('level_select_page', 0)
        interactive_elements = render_level_select(surface, mouse_pos, data.get('save_data'), page_index)

    elif state == 'SETTINGS':
        interactive_elements = render_settings_menu(surface, mouse_pos, data['settings'])
    
    elif state == 'TERMINAL':
        interactive_elements = render_cheat_terminal(surface, data.get('term_input', ''), data.get('term_status', ''))
        
    elif state == 'LOADING':
        interactive_elements = render_loading_screen(surface, data['progress'])
        
    elif state == 'CUTSCENE' or state == 'CHAT':
        if data['story_manager'].is_cutscene:
            render_cutscene(surface, data['story_manager'])
        else:
            render_chat_interface(surface, data['story_manager'])
        
    elif state == 'PAUSED':
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill(PAUSE_OVERLAY_COLOR)
        surface.blit(overlay, (0, 0))
        
        panel_rect = pygame.Rect(w//2 - 300, h//2 - 150, 600, 300)
        draw_cyber_panel(surface, panel_rect, (0, 180, 255), "SİSTEM ASKIYA ALINDI")
        
        title_font = pygame.font.Font(None, 100)
        message_font = pygame.font.Font(None, 35)
        
        draw_glitch_text(surface, "DURAKLATILDI", 100, w//2, h//2 - 30, WHITE)
        draw_text_with_shadow(surface, "'P' İLE DEVAM ET", message_font,
                             (w//2, h//2 + 60), (150, 150, 150))

    elif state == 'LEVEL_COMPLETE':
        interactive_elements = render_level_complete(surface, mouse_pos, 
                                                     data['level_data'], data['score'])

    elif state == 'GAME_OVER':
        overlay = pygame.Surface((w, h), pygame.SRCALPHA)
        overlay.fill((30, 0, 0, 240))
        surface.blit(overlay, (0, 0))
        
        draw_glitch_text(surface, "BAĞLANTI KOPTU", 90, w//2, h//2 - 140, 
                        (255, 50, 50), 6)
        
        panel_rect = pygame.Rect(w//2 - 250, h//2 - 40, 500, 160)
        draw_cyber_panel(surface, panel_rect, (255, 50, 50), "HATA RAPORU")
        
        score_font = pygame.font.Font(None, 55)
        goal_font = pygame.font.Font(None, 35)
        
        draw_text_with_shadow(surface, f"SKOR: {int(data['score'])}", score_font,
                             (w//2, h//2 + 10), WHITE)
        draw_text_with_shadow(surface, f"HEDEF: {data['level_data']['goal_score']}", goal_font,
                             (w//2, h//2 + 70), (255, 200, 0))
        
        if time_ms % 1000 < 500:
            retry_font = pygame.font.Font(None, 45)
            draw_text_with_shadow(surface, "TEKRAR DENEMEK İÇİN 'R'", retry_font,
                                 (w//2, h//2 + 180), WHITE)

    elif state == 'PLAYING':
        current_theme = data.get('theme')
        if not current_theme:
            current_theme = THEMES[0]

        left_panel = pygame.Rect(40, 40, 300, 100)
        draw_cyber_panel(surface, left_panel, current_theme["border_color"], 
                        f"BÖLÜM {data['level_idx']}")
        
        # DASH BARI
        active_dash_max = data.get('active_dash_max', 1)
        if active_dash_max <= 0:
            d_fill = 200 
        else:
            d_fill = 200 * (1 - (data['dash_cd'] / active_dash_max))
            
        pygame.draw.rect(surface, (50, 50, 50), (60, 85, 200, 10))
        pygame.draw.rect(surface, PLAYER_DASH, (60, 85, max(0, int(d_fill)), 10))
        
        dash_font = pygame.font.Font(None, 20)
        draw_text_with_shadow(surface, "DASH", dash_font, (60, 70), PLAYER_DASH, align='midleft')
        
        # SLAM BARI
        active_slam_max = data.get('active_slam_max', 1)
        if active_slam_max <= 0:
            s_fill = 200
        else:
            s_fill = 200 * (1 - (data['slam_cd'] / active_slam_max))
            
        pygame.draw.rect(surface, (50, 50, 50), (60, 115, 200, 10))
        pygame.draw.rect(surface, PLAYER_SLAM, (60, 115, max(0, int(s_fill)), 10))
        
        slam_font = pygame.font.Font(None, 20)
        draw_text_with_shadow(surface, "SLAM", slam_font, (60, 100), PLAYER_SLAM, align='midleft')

        # KARMA GÖSTERGESİ
        karma = data.get('karma', 0)
        kills = data.get('kills', 0)
        
        karma_color = (255, 255, 255)
        if karma > 20: karma_color = (0, 255, 100)
        elif karma < -20: karma_color = (255, 50, 50)
        
        karma_text = f"KARMA: {karma}"
        kill_text = f"ÖLÜM: {kills}"
        
        karma_font = pygame.font.Font(None, 24)
        draw_text_with_shadow(surface, karma_text, karma_font, (350, 60), karma_color)
        draw_text_with_shadow(surface, kill_text, karma_font, (350, 90), (200, 50, 50))
        
        goal = data['level_data'].get('goal_score', 0)
        current = data['score']
        
        if goal > 0:
            progress = min(1.0, current / goal)
            score_text = f"{int(current)} / {goal}"
        else:
            progress = 0.0
            score_text = f"SKOR: {int(current)}"
        
        score_rect = pygame.Rect(w - 350, 40, 310, 80)
        draw_cyber_panel(surface, score_rect, WHITE, "VERİ YÜKLEMESİ")
        
        pygame.draw.rect(surface, (30, 30, 30), (w - 330, 85, 270, 20))
        
        if goal > 0:
            pygame.draw.rect(surface, NEON_GREEN, (w - 330, 85, int(270 * progress), 20))
        
        score_font = pygame.font.Font(None, 30)
        draw_text_with_shadow(surface, score_text, score_font,
                             (w - 195, 95), (0, 0, 0))
    
    return interactive_elements
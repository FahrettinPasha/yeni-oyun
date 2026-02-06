import pygame
import random
import math
from settings import *
from utils import draw_text_with_shadow, wrap_text
from story_system import ai_chat_effect

def draw_glitch_text(surface, text, size, x, y, color, intensity=2):
    """Glitch efekti ile metin çizer (Varsayılan: Center)"""
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
        # Başlık için MidLeft hizalama kullan
        draw_text_with_shadow(surface, title, title_font, 
                             (title_rect.x + 10, title_rect.centery), (0, 0, 0), align='midleft')

def draw_button(surface, rect, text, is_hovered, color_theme=BUTTON_COLOR, locked=False):
    """Buton çizer"""
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
    # Buton metni ortalanır
    draw_text_with_shadow(surface, text, font, draw_rect.center, text_col)

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
        # Sohbet metni sola yaslanmalı
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
    
    # Arkaplan Karartma
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0, 20, 10, 230))
    surface.blit(overlay, (0, 0))
    
    # Terminal Kutusu
    term_width = 800
    term_height = 400
    term_rect = pygame.Rect(w//2 - term_width//2, h//2 - term_height//2, term_width, term_height)
    
    draw_cyber_panel(surface, term_rect, (0, 255, 0), "ROOT_ACCESS_TERMINAL v1.0")
    
    # Terminal İçeriği
    font_term = pygame.font.Font(None, 35)
    
    # Prompt
    draw_text_with_shadow(surface, "C:\\NEXUS\\SYSTEM> HİLE KODU GİRİN:", font_term, 
                         (term_rect.x + 30, term_rect.y + 60), (0, 255, 0), align='topleft')
    
    # Girilen Metin
    input_box = pygame.Rect(term_rect.x + 30, term_rect.y + 110, term_width - 60, 50)
    pygame.draw.rect(surface, (0, 50, 0), input_box)
    pygame.draw.rect(surface, (0, 255, 0), input_box, 2)
    
    cursor = "_" if (pygame.time.get_ticks() // 500) % 2 == 0 else ""
    draw_text_with_shadow(surface, f"> {input_text}{cursor}", font_term,
                         (input_box.x + 10, input_box.centery), (200, 255, 200), align='midleft')
    
    # Durum Mesajı
    status_color = (255, 200, 0) if "BEKLENİYOR" in status_msg else ((0, 255, 100) if "AKTİF" in status_msg else (255, 50, 50))
    draw_text_with_shadow(surface, f"DURUM: {status_msg}", font_term,
                         (term_rect.centerx, term_rect.y + 200), status_color, align='center')
    
    # Talimat
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
    
    # Buton konumlarını düzenledim
    
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
    
    # 4. Hile Terminali (YENİ)
    btn_cheat_rect = pygame.Rect(w//2 - 150, 520, 300, 50)
    is_hover = btn_cheat_rect.collidepoint(mouse_pos)
    draw_button(surface, btn_cheat_rect, "HİLE TERMİNALİ", is_hover, (50, 0, 50)) # Mor renk
    active_buttons['cheat_terminal'] = btn_cheat_rect
    
    # 5. Çıkış
    btn_exit_rect = pygame.Rect(w//2 - 150, 580, 300, 50)
    is_hover = btn_exit_rect.collidepoint(mouse_pos)
    draw_button(surface, btn_exit_rect, "ÇIKIŞ", is_hover, (60, 0, 0))
    active_buttons['exit'] = btn_exit_rect
    
    return active_buttons

def render_level_select(surface, mouse_pos, save_data, page_index=0):
    """Bölüm Seçimi Ekranı - SAYFALAMA SİSTEMİ EKLENDİ"""
    w, h = surface.get_width(), surface.get_height()
    surface.fill(UI_BG_COLOR)
    
    draw_glitch_text(surface, "BÖLÜM SEÇİMİ", 100, w//2, 80, UI_BORDER_COLOR)
    
    active_buttons = {}
    
    if not save_data or 'easy_mode' not in save_data:
        easy_data = {'unlocked_levels': 1, 'completed_levels': [], 'high_scores': {}}
    else:
        easy_data = save_data['easy_mode']
        
    unlocked = easy_data['unlocked_levels']
    
    # --- SAYFALAMA MANTIĞI ---
    ITEMS_PER_PAGE = 4
    all_levels = list(EASY_MODE_LEVELS.items())
    total_pages = math.ceil(len(all_levels) / ITEMS_PER_PAGE)
    
    # Geçerli sayfa sınırları
    start_idx = page_index * ITEMS_PER_PAGE
    end_idx = min(start_idx + ITEMS_PER_PAGE, len(all_levels))
    current_page_levels = all_levels[start_idx:end_idx]
    
    start_y = 180
    
    for lvl_num, lvl_info in current_page_levels:
        is_locked = lvl_num > unlocked
        is_completed = lvl_num in easy_data['completed_levels']
        
        btn_rect = pygame.Rect(w//2 - 350, start_y, 700, 100)
        
        panel_col = UI_BORDER_COLOR
        if is_locked:
            panel_col = (50, 50, 50)
        elif is_completed:
            panel_col = NEON_GREEN
        
        draw_cyber_panel(surface, btn_rect, panel_col, f"BÖLÜM {lvl_num}")
        
        name_col = WHITE if not is_locked else LOCKED_TEXT_COLOR
        name_font = pygame.font.Font(None, 40)
        desc_font = pygame.font.Font(None, 25)
        
        draw_text_with_shadow(surface, lvl_info['name'], name_font,
                             (btn_rect.x + 40, btn_rect.centery - 15), name_col, align='midleft')
        draw_text_with_shadow(surface, lvl_info.get('desc', 'Açıklama Yok'), desc_font,
                     (btn_rect.x + 40, btn_rect.centery + 20), (150, 150, 150), align='midleft')
        play_btn_rect = pygame.Rect(btn_rect.right - 150, btn_rect.centery - 30, 120, 60)
        btn_text = "BAŞLA" if not is_locked else "KİLİTLİ"
        if is_completed:
            btn_text = "TEKRAR"
            
        draw_button(surface, play_btn_rect, btn_text, 
                   play_btn_rect.collidepoint(mouse_pos) and not is_locked, 
                   locked=is_locked)
        
        if not is_locked:
            active_buttons[f'level_{lvl_num}'] = play_btn_rect
            
        start_y += 120

    # --- NAVİGASYON BUTONLARI ---
    nav_y = h - 100
    
    # Önceki Sayfa
    if page_index > 0:
        btn_prev = pygame.Rect(w//2 - 250, nav_y, 200, 50)
        draw_button(surface, btn_prev, "<< ÖNCEKİ", btn_prev.collidepoint(mouse_pos))
        active_buttons['prev_page'] = btn_prev
        
    # Sayfa Göstergesi
    page_font = pygame.font.Font(None, 35)
    draw_text_with_shadow(surface, f"SAYFA {page_index + 1} / {total_pages}", page_font,
                         (w//2, nav_y + 25), WHITE, align='center')
        
    # Sonraki Sayfa
    if page_index < total_pages - 1:
        btn_next = pygame.Rect(w//2 + 50, nav_y, 200, 50)
        draw_button(surface, btn_next, "SONRAKİ >>", btn_next.collidepoint(mouse_pos))
        active_buttons['next_page'] = btn_next

    btn_back = pygame.Rect(40, 40, 150, 50)
    draw_button(surface, btn_back, "< GERİ", btn_back.collidepoint(mouse_pos))
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
    
    # Devam Et Butonu
    btn_cont = pygame.Rect(w//2 - 150, h//2 + 100, 300, 50)
    draw_button(surface, btn_cont, "DEVAM ET", btn_cont.collidepoint(mouse_pos), (0, 100, 0))
    active_buttons['continue'] = btn_cont
    
    # Menüye Dön Butonu (YENİ)
    btn_menu = pygame.Rect(w//2 - 150, h//2 + 160, 300, 50)
    draw_button(surface, btn_menu, "MENÜYE DÖN", btn_menu.collidepoint(mouse_pos), (50, 50, 80))
    active_buttons['return_menu'] = btn_menu
    
    return active_buttons

def render_settings_menu(surface, mouse_pos, settings_data):
    w, h = surface.get_width(), surface.get_height()
    surface.fill(UI_BG_COLOR)
    
    draw_glitch_text(surface, "SİSTEM AYARLARI", 80, w//2, 80, UI_BORDER_COLOR)
    
    # Paneli biraz daha genişlettim ki sliderlar rahat sığsın
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
        # Etiket
        draw_text_with_shadow(surface, label, label_font, (btn_x, current_y), WHITE, align='midleft')
        
        # Slider Arkaplan (Kanal)
        slider_rect = pygame.Rect(btn_x + 150, current_y - 5, 450, 12)
        pygame.draw.rect(surface, (30, 30, 30), slider_rect) # Koyu kanal
        pygame.draw.rect(surface, (100, 100, 100), slider_rect, 1) # İnce kenarlık
        
        # Doluluk Oranı
        volume = settings_data.get(key, 0.5)
        fill_width = int(slider_rect.width * volume)
        pygame.draw.rect(surface, slider_color, (slider_rect.x, slider_rect.y, fill_width, slider_rect.height))
        
        # Cyber Handle (Kaydırıcı Başlığı)
        handle_x = slider_rect.x + fill_width
        handle_rect = pygame.Rect(handle_x - 5, slider_rect.y - 8, 10, 28)
        pygame.draw.rect(surface, WHITE, handle_rect)
        pygame.draw.rect(surface, slider_color, handle_rect, 2)
        
        # Etkileşim için buton olarak kaydet (Tıklama kontrolü için)
        active_buttons[f'slider_{key}'] = slider_rect
        
        current_y += spacing

    current_y += 20 # Boşluk bırak

    # --- GÖRÜNTÜ VE SİSTEM AYARLARI ---
    # Tam Ekran
    mode_text = "MOD: [TAM EKRAN]" if settings_data['fullscreen'] else "MOD: [PENCERE]"
    btn_mode = pygame.Rect(btn_x, current_y, btn_w, 50)
    draw_button(surface, btn_mode, mode_text, btn_mode.collidepoint(mouse_pos))
    active_buttons['toggle_fullscreen'] = btn_mode
    current_y += spacing - 10

    # Kalite
    q_text = f"EFEKT KALİTESİ: [{settings_data['quality']}]"
    btn_q = pygame.Rect(btn_x, current_y, btn_w, 50)
    draw_button(surface, btn_q, q_text, btn_q.collidepoint(mouse_pos))
    active_buttons['toggle_quality'] = btn_q
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
        # Sayfalama bilgisini data'dan al
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
        # GÜVENLİK: Tema verisi yoksa varsayılanı kullan
        current_theme = data.get('theme')
        if not current_theme:
            current_theme = THEMES[0]

        left_panel = pygame.Rect(40, 40, 300, 100)
        draw_cyber_panel(surface, left_panel, current_theme["border_color"], 
                        f"BÖLÜM {data['level_idx']}")
        
        # --- UI SYSTEM DÜZELTMESİ BAŞLANGICI ---
        
        # DASH BARI
        active_dash_max = data.get('active_dash_max', 1)
        # Eğer max değer 0 veya daha küçükse (Sınırsız Dash), barı full göster
        if active_dash_max <= 0:
            d_fill = 200 
        else:
            d_fill = 200 * (1 - (data['dash_cd'] / active_dash_max))
            
        pygame.draw.rect(surface, (50, 50, 50), (60, 85, 200, 10))
        pygame.draw.rect(surface, PLAYER_DASH, (60, 85, max(0, d_fill), 10))
        
        dash_font = pygame.font.Font(None, 20)
        draw_text_with_shadow(surface, "DASH", dash_font, (60, 70), PLAYER_DASH, align='midleft')
        
        # SLAM BARI
        active_slam_max = data.get('active_slam_max', 1)
        # Eğer max değer 0 veya daha küçükse (Sınırsız Slam), barı full göster
        if active_slam_max <= 0:
            s_fill = 200
        else:
            s_fill = 200 * (1 - (data['slam_cd'] / active_slam_max))
            
        pygame.draw.rect(surface, (50, 50, 50), (60, 115, 200, 10))
        pygame.draw.rect(surface, PLAYER_SLAM, (60, 115, max(0, s_fill), 10))
        
        slam_font = pygame.font.Font(None, 20)
        draw_text_with_shadow(surface, "SLAM", slam_font, (60, 100), PLAYER_SLAM, align='midleft')

        # --- UI SYSTEM DÜZELTMESİ BİTİŞİ ---
        
        # --- KARMA GÖSTERGESİ (YENİ) ---
        karma = data.get('karma', 0)
        kills = data.get('kills', 0)
        
        # Karma Rengi
        karma_color = (255, 255, 255) # Nötr
        if karma > 20: karma_color = (0, 255, 100) # İyi
        elif karma < -20: karma_color = (255, 50, 50) # Kötü
        
        karma_text = f"KARMA: {karma}"
        kill_text = f"ÖLÜM: {kills}"
        
        karma_font = pygame.font.Font(None, 24)
        draw_text_with_shadow(surface, karma_text, karma_font, (350, 60), karma_color)
        draw_text_with_shadow(surface, kill_text, karma_font, (350, 90), (200, 50, 50))
        
        # --- FIX: Division by Zero Hatası Düzeltmesi ---
        goal = data['level_data'].get('goal_score', 0)
        current = data['score']
        
        if goal > 0:
            progress = min(1.0, current / goal)
            score_text = f"{int(current)} / {goal}"
        else:
            progress = 0.0 # Hedef yoksa (Dinlenme alanı) bar boş kalsın veya dolmasın
            score_text = f"SKOR: {int(current)}"
        
        score_rect = pygame.Rect(w - 350, 40, 310, 80)
        draw_cyber_panel(surface, score_rect, WHITE, "VERİ YÜKLEMESİ")
        
        pygame.draw.rect(surface, (30, 30, 30), (w - 330, 85, 270, 20))
        
        if goal > 0:
            pygame.draw.rect(surface, NEON_GREEN, (w - 330, 85, 270 * progress, 20))
        
        score_font = pygame.font.Font(None, 30)
        draw_text_with_shadow(surface, score_text, score_font,
                             (w - 195, 95), (0, 0, 0))
    
    return interactive_elements

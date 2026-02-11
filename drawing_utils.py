import pygame
import math
from utils import wrap_text, draw_text_with_shadow

def rotate_point(point, angle, origin):
    """Bir noktayı orijin etrafında döndürür."""
    ox, oy = origin
    px, py = point
    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy

def draw_legendary_revolver(surface, x, y, angle, shoot_timer):
    """Detaylı, dönen ve geri tepme efekti olan Altıpatlar çizer."""
    recoil_angle = 0
    recoil_offset = 0
    if shoot_timer < 0.15:
        recoil_value = (0.15 - shoot_timer) / 0.15 
        recoil_angle = -0.5 * recoil_value 
        recoil_offset = -10 * recoil_value 

    final_angle = angle + recoil_angle
    pivot_x = x + math.cos(angle) * recoil_offset
    pivot_y = y + math.sin(angle) * recoil_offset

    GUN_METAL = (40, 40, 50)
    NEON_CYAN = (0, 255, 255)
    GRIP_BROWN = (139, 69, 19)
    BARREL_GREY = (80, 80, 90)

    grip_poly = [(pivot_x - 10, pivot_y - 5), (pivot_x + 10, pivot_y - 5), (pivot_x + 5, pivot_y + 20), (pivot_x - 15, pivot_y + 20)]
    body_poly = [(pivot_x + 5, pivot_y - 15), (pivot_x + 45, pivot_y - 15), (pivot_x + 45, pivot_y + 5), (pivot_x + 5, pivot_y + 5)]
    barrel_poly = [(pivot_x + 45, pivot_y - 12), (pivot_x + 90, pivot_y - 12), (pivot_x + 90, pivot_y + 2), (pivot_x + 45, pivot_y + 2)]
    
    cyl_center_x = pivot_x + 25
    cyl_center_y = pivot_y - 5
    cylinder_poly = []
    for i in range(6):
        deg = i * 60
        rad = math.radians(deg)
        cylinder_poly.append((cyl_center_x + math.cos(rad) * 12, cyl_center_y + math.sin(rad) * 12))

    def draw_rotated_poly(surface, color, points, angle, pivot):
        rotated_points = [rotate_point(p, angle, pivot) for p in points]
        pygame.draw.polygon(surface, color, rotated_points)
        pygame.draw.polygon(surface, (0, 0, 0), rotated_points, 1)

    draw_rotated_poly(surface, GRIP_BROWN, grip_poly, final_angle, (pivot_x, pivot_y))
    draw_rotated_poly(surface, BARREL_GREY, barrel_poly, final_angle, (pivot_x, pivot_y))
    draw_rotated_poly(surface, GUN_METAL, body_poly, final_angle, (pivot_x, pivot_y))
    draw_rotated_poly(surface, (60, 60, 70), cylinder_poly, final_angle, (pivot_x, pivot_y))
    
    start_neon = rotate_point((pivot_x + 10, pivot_y - 5), final_angle, (pivot_x, pivot_y))
    end_neon = rotate_point((pivot_x + 40, pivot_y - 5), final_angle, (pivot_x, pivot_y))
    pygame.draw.line(surface, NEON_CYAN, start_neon, end_neon, 2)

    return rotate_point((pivot_x + 90, pivot_y - 5), final_angle, (pivot_x, pivot_y))

def draw_cinematic_overlay(surface, manager, time_ms, mouse_pos):
    """Oyun dünyasının üzerine çizilen sinematik katman"""
    w, h = surface.get_width(), surface.get_height()
    active_buttons = {}
    
    overlay = pygame.Surface((w, h), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    surface.blit(overlay, (0, 0))
    
    bar_height = 130
    pygame.draw.rect(surface, (0, 0, 0), (0, 0, w, bar_height))
    pygame.draw.rect(surface, (0, 0, 0), (0, h - bar_height, w, bar_height))
    
    line_color = (0, 255, 255)
    if manager.speaker == "SİSTEM" or manager.speaker == "MUHAFIZ" or "MAKİNE" in manager.speaker or "YARGIÇ" in manager.speaker:
        line_color = (255, 50, 50)
    elif manager.speaker == "VASI" or manager.speaker == "KURYE":
        line_color = (0, 255, 100)
    elif "OYUNCU" in manager.speaker or "İÇ SES" in manager.speaker:
        line_color = (255, 200, 50)

    pygame.draw.line(surface, line_color, (0, bar_height), (w, bar_height), 2)
    pygame.draw.line(surface, line_color, (0, h - bar_height), (w, h - bar_height), 2)
    
    if manager.speaker:
        font_title = pygame.font.Font(None, 55)
        icon_rect = pygame.Rect(50, bar_height // 2 - 20, 40, 40)
        pygame.draw.rect(surface, line_color, icon_rect, 2)
        pygame.draw.rect(surface, (*line_color, 100), icon_rect.inflate(-4,-4))
        draw_text_with_shadow(surface, manager.speaker, font_title, (110, bar_height // 2), line_color, align="midleft")

    font_text = pygame.font.Font(None, 36)
    text_area_rect = pygame.Rect(60, h - bar_height + 30, w - 120, bar_height - 60)
    
    if manager.is_cutscene:
        center_overlay = pygame.Surface((w, 200), pygame.SRCALPHA)
        center_overlay.fill((0, 0, 0, 180))
        surface.blit(center_overlay, (0, h//2 - 100))
        
        lines = wrap_text(manager.display_text, font_text, w - 400)
        total_h = len(lines) * 45
        start_y = h//2 - total_h // 2
        
        for i, line in enumerate(lines):
            col = (255, 255, 255)
            if "HATA" in line or "UYARI" in line or "DİKKAT" in line: col = (255, 50, 50)
            draw_text_with_shadow(surface, line, font_text, (w//2, start_y + i * 45), col, align="center")
    else:
        lines = wrap_text(manager.display_text, font_text, text_area_rect.width)
        for i, line in enumerate(lines):
            draw_text_with_shadow(surface, line, font_text, (text_area_rect.x, text_area_rect.y + i * 35), (220, 220, 220), align="topleft")

    if manager.waiting_for_click and manager.state != "WAITING_CHOICE":
        blink = (time_ms // 500) % 2 == 0
        if blink:
            draw_text_with_shadow(surface, "DEVAM ETMEK İÇİN TIKLA >", pygame.font.Font(None, 24), 
                                 (w - 50, h - 30), line_color, align="bottomright")

    if manager.state == "WAITING_CHOICE":
        btn_height = 80
        btn_width = 800
        start_y = h // 2 - (len(manager.current_choices) * 110) // 2 + 30
        
        draw_text_with_shadow(surface, "BİR SEÇİM YAP", pygame.font.Font(None, 60), (w//2, start_y - 70), (255, 255, 0), align="center")
        
        for i, choice in enumerate(manager.current_choices):
            rect = pygame.Rect(w//2 - btn_width//2, start_y + i * 110, btn_width, btn_height)
            is_hover = rect.collidepoint(mouse_pos)
            
            s = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
            bg_col = (0, 40, 60, 230) if is_hover else (0, 20, 30, 200)
            s.fill(bg_col)
            surface.blit(s, rect.topleft)
            
            border_col = (0, 255, 255) if is_hover else (0, 100, 150)
            pygame.draw.rect(surface, border_col, rect, 3, border_radius=0)
            
            text_col = (255, 255, 255) if is_hover else (200, 200, 200)
            draw_text_with_shadow(surface, f"> {choice['text']}", font_text, rect.center, text_col, align="center")
            active_buttons[f'choice_{i}'] = rect
            
    return active_buttons

def draw_background_hero(surface, x, y, size=150):
    GOLD = (255, 215, 0)
    HERO_BLUE = (0, 191, 255)
    ghost_surf = pygame.Surface((size * 3, size * 3), pygame.SRCALPHA)
    cx, cy = size * 1.5, size * 1.5 
    t = pygame.time.get_ticks() / 1000.0
    for i in range(2):
        radius = size * (1.2 + i * 0.2) + math.sin(t * 2) * 10
        alpha = int(80 / (i + 1))
        pygame.draw.circle(ghost_surf, (*GOLD, alpha), (cx, cy), int(radius), 2)

    points = [(cx, cy - size * 1.2), (cx - size * 0.8, cy - size * 0.2), (cx - size * 0.6, cy + size), (cx, cy + size * 1.4), (cx + size * 0.6, cy + size), (cx + size * 0.8, cy - size * 0.2)]
    pygame.draw.polygon(ghost_surf, (*GOLD, 30), points) 
    pygame.draw.polygon(ghost_surf, (*GOLD, 100), points, 5)
    visor_rect = pygame.Rect(cx - size * 0.4, cy - 10, size * 0.8, 25)
    pygame.draw.rect(ghost_surf, (*HERO_BLUE, 150), visor_rect, border_radius=5)
    surface.blit(ghost_surf, (x - cx, y - cy))

def draw_background_boss_silhouette(surface, karma, width, height):
    t = pygame.time.get_ticks() / 1000.0
    float_y = math.sin(t) * 15
    cx, cy = width // 2, height // 2 + float_y
    size = 200 
    ghost_surf = pygame.Surface((width, height), pygame.SRCALPHA)

    if karma < 0:
        GOLD = (255, 215, 0)
        HERO_BLUE = (0, 191, 255)
        WHITE = (255, 255, 255)
        for i in range(2):
            radius = size * (1.3 + i * 0.25)
            pygame.draw.circle(ghost_surf, (*GOLD, 60), (cx, cy), int(radius), 3)
        points = [(cx, cy - size * 1.2), (cx - size * 0.8, cy - size * 0.2), (cx - size * 0.6, cy + size), (cx, cy + size * 1.4), (cx + size * 0.6, cy + size), (cx + size * 0.8, cy - size * 0.2)]
        pygame.draw.polygon(ghost_surf, (*GOLD, 50), points) 
        pygame.draw.polygon(ghost_surf, (*GOLD, 255), points, 6)
        visor_rect = pygame.Rect(cx - size*0.4, cy - 15, size*0.8, 30)
        pygame.draw.rect(ghost_surf, (*HERO_BLUE, 200), visor_rect, border_radius=8)
        pygame.draw.line(ghost_surf, (*WHITE, 200), (cx - size*1.5, cy), (cx + size*1.5, cy), 3)
        pygame.draw.line(ghost_surf, (*WHITE, 150), (cx, cy - size*1.5), (cx, cy + size*1.5), 10)
    else: 
        CYBER_GREEN = (0, 255, 100)
        DARK_GREEN = (0, 50, 20)
        WHITE = (255, 255, 255)
        rect_size = size * 2.2
        rect = pygame.Rect(0, 0, rect_size, rect_size)
        rect.center = (cx, cy)
        rot_offset = math.sin(t) * 10
        corner_len = 40
        pygame.draw.line(ghost_surf, (*CYBER_GREEN, 200), (rect.left - rot_offset, rect.top), (rect.left + corner_len, rect.top), 4)
        pygame.draw.line(ghost_surf, (*CYBER_GREEN, 200), (rect.left - rot_offset, rect.top), (rect.left - rot_offset, rect.top + corner_len), 4)
        pygame.draw.line(ghost_surf, (*CYBER_GREEN, 200), (rect.right + rot_offset, rect.bottom), (rect.right - corner_len, rect.bottom), 4)
        pygame.draw.line(ghost_surf, (*CYBER_GREEN, 200), (rect.right + rot_offset, rect.bottom), (rect.right + rot_offset, rect.bottom - corner_len), 4)
        pygame.draw.circle(ghost_surf, (*DARK_GREEN, 100), (cx, cy), size) 
        pygame.draw.circle(ghost_surf, (*CYBER_GREEN, 255), (cx, cy), size, 3) 
        pygame.draw.circle(ghost_surf, (*CYBER_GREEN, 100), (cx, cy), int(size * 0.7), 1)
        pygame.draw.circle(ghost_surf, (*CYBER_GREEN, 150), (cx, cy), int(size * 0.4), 2)
        pupil_size = 20
        pupil_x = cx + math.cos(t * 2) * 10
        pupil_y = cy + math.sin(t * 3) * 5
        pupil_points = [(pupil_x, pupil_y - 20), (pupil_x + 15, pupil_y), (pupil_x, pupil_y + 20), (pupil_x - 15, pupil_y)]
        pygame.draw.polygon(ghost_surf, (*CYBER_GREEN, 255), pupil_points)
        pygame.draw.circle(ghost_surf, (*WHITE, 255), (pupil_x, pupil_y), 5) 
        scan_y = cy + math.sin(t * 4) * size
        pygame.draw.line(ghost_surf, (*CYBER_GREEN, 80), (cx - size, scan_y), (cx + size, scan_y), 2)

    surface.blit(ghost_surf, (0, 0))

def draw_npc_chat(surface, current_npc, chat_history, chat_input, show_cursor, logical_width, logical_height):
    """NPC sohbet ekranını çiz"""
    if not current_npc:
        return
    
    overlay = pygame.Surface((logical_width, logical_height), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 200))
    surface.blit(overlay, (0, 0))
    
    chat_width = 800
    chat_height = 600
    chat_x = (logical_width - chat_width) // 2
    chat_y = (logical_height - chat_height) // 2
    
    pygame.draw.rect(surface, (20, 20, 30), (chat_x, chat_y, chat_width, chat_height), border_radius=15)
    pygame.draw.rect(surface, current_npc.color, (chat_x, chat_y, chat_width, chat_height), 3, border_radius=15)
    
    title_font = pygame.font.Font(None, 40)
    title = title_font.render(f"KONUŞUYOR: {current_npc.name}", True, current_npc.color)
    surface.blit(title, (chat_x + 20, chat_y + 20))
    
    type_font = pygame.font.Font(None, 24)
    status_text = "AI AKTİF" if current_npc.ai_active else "MANUEL MOD"
    status_color = (0, 255, 100) if current_npc.ai_active else (200, 200, 200)
    type_text = type_font.render(f"Kişilik: {current_npc.personality_type} | {status_text}", True, status_color)
    surface.blit(type_text, (chat_x + chat_width - 300, chat_y + 30))
    
    history_height = 400
    history_rect = pygame.Rect(chat_x + 20, chat_y + 80, chat_width - 40, history_height)
    pygame.draw.rect(surface, (10, 10, 15), history_rect, border_radius=10)
    
    font = pygame.font.Font(None, 28)
    y_offset = history_rect.y + 20
    
    for msg in chat_history[-8:]:
        if msg["speaker"] == "Oyuncu":
            text_color = (200, 255, 200)
            speaker = "Siz: "
        elif msg["speaker"] == "SİSTEM":
            text_color = (255, 100, 100)
            speaker = "SİSTEM: "
        else:
            text_color = current_npc.color
            speaker = f"{msg['speaker']}: "
        
        lines = wrap_text(msg["text"], font, history_rect.width - 40)
        for line in lines:
            text_surf = font.render(speaker + line, True, text_color)
            surface.blit(text_surf, (history_rect.x + 20, y_offset))
            y_offset += 35
        y_offset += 10
    
    input_y = chat_y + history_height + 100
    input_rect = pygame.Rect(chat_x + 20, input_y, chat_width - 40, 50)
    pygame.draw.rect(surface, (30, 30, 40), input_rect, border_radius=8)
    pygame.draw.rect(surface, (100, 100, 150), input_rect, 2, border_radius=8)
    
    input_font = pygame.font.Font(None, 32)
    display_text = chat_input
    if show_cursor:
        display_text += "|"
    
    input_text = input_font.render(display_text, True, (220, 220, 220))
    surface.blit(input_text, (input_rect.x + 15, input_rect.centery - 10))
    
    instruct_font = pygame.font.Font(None, 24)
    instruct1 = instruct_font.render("ENTER: Gönder | ESC: Çık | TAB: AI Modu Aç/Kapa", True, (150, 150, 150))
    
    if current_npc.ai_active:
        instruct2 = instruct_font.render("AI BAĞLANTISI KURULDU: Herhangi bir şey sorabilirsin!", True, (0, 255, 100))
    else:
        instruct2 = instruct_font.render("MANUEL MOD: Sadece ön tanımlı cevaplar.", True, (255, 200, 100))
    
    surface.blit(instruct1, (chat_x + 20, chat_y + chat_height - 40))
    surface.blit(instruct2, (chat_x + chat_width//2 - instruct2.get_width()//2, chat_y + chat_height - 70))
    
    avatar_size = 80
    avatar_x = chat_x + chat_width - avatar_size - 30
    avatar_y = chat_y + 30
    
    pygame.draw.circle(surface, (40, 40, 60), (avatar_x + avatar_size//2, avatar_y + avatar_size//2), avatar_size//2)
    pygame.draw.circle(surface, current_npc.color, (avatar_x + avatar_size//2, avatar_y + avatar_size//2), avatar_size//2, 3)
    
    eye_y = avatar_y + avatar_size//2 - 10
    pygame.draw.circle(surface, (255, 255, 255), (avatar_x + avatar_size//2 - 15, eye_y), 8)
    pygame.draw.circle(surface, (255, 255, 255), (avatar_x + avatar_size//2 + 15, eye_y), 8)
    pygame.draw.circle(surface, (0, 100, 200), (avatar_x + avatar_size//2 - 15, eye_y), 4)
    pygame.draw.circle(surface, (0, 100, 200), (avatar_x + avatar_size//2 + 15, eye_y), 4)
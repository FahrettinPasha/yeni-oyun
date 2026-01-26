import pygame
import random
import math
import numpy as np

# --- SİSTEM FONKSİYONLARI ---

def generate_sound_effect(base_freq, duration, volume=1.0):
    try:
        sample_rate = 44100
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        wave = np.sin(2 * np.pi * base_freq * t)
        envelope = np.ones_like(t)
        attack_len = int(sample_rate * 0.01)
        decay_len = int(sample_rate * (duration * 0.8))
        if attack_len > 0:
            envelope[:attack_len] = np.linspace(0, 1, attack_len)
        if decay_len > 0:
            envelope[-decay_len:] = np.linspace(1, 0, decay_len)
        wave = wave * envelope
        if base_freq > 100:
            harmonic_1 = 0.3 * np.sin(2 * np.pi * base_freq * 2 * t)
            harmonic_2 = 0.15 * np.sin(2 * np.pi * base_freq * 0.5 * t)
            wave = wave + harmonic_1 + harmonic_2
        wave = wave / np.max(np.abs(wave)) if np.max(np.abs(wave)) > 0 else wave
        wave = (wave * 32767).astype(np.int16)
        wave = np.repeat(wave.reshape(-1, 1), 2, axis=1)
        sound = pygame.sndarray.make_sound(wave)
        sound.set_volume(volume * 0.7)
        return sound
    except Exception as e:
        print(f"Ses oluşturma hatası: {e}")
        silent = pygame.mixer.Sound(buffer=bytes([0, 0]))
        silent.set_volume(0)
        return silent

def generate_ambient_fallback():
    try:
        sample_rate = 44100
        duration = 10.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        base_freq = 55.0
        drone = 0.5 * np.sin(2 * np.pi * base_freq * t)
        wave = drone
        envelope = np.ones_like(t)
        fade = int(sample_rate * 2.0)
        if fade > 0:
            envelope[:fade] = np.linspace(0, 1, fade)
            envelope[-fade:] = np.linspace(1, 0, fade)
        wave = wave * envelope
        wave = (wave * 32767 * 0.3).astype(np.int16)
        wave = np.repeat(wave.reshape(-1, 1), 2, axis=1)
        sound = pygame.sndarray.make_sound(wave)
        sound.set_volume(0.4)
        return sound
    except Exception:
        silent = pygame.mixer.Sound(buffer=bytes([0, 0]))
        return silent

def generate_calm_ambient():
    """Dinlenme alanı için huzurlu müzik"""
    try:
        sample_rate = 44100
        duration = 15.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        
        # Sakin drone
        base_freq = 110.0
        wave = 0.3 * np.sin(2 * np.pi * base_freq * t)
        wave += 0.2 * np.sin(2 * np.pi * base_freq * 1.5 * t)
        
        # Zarf
        envelope = np.ones_like(t)
        fade = int(sample_rate * 3.0)
        if fade > 0:
            envelope[:fade] = np.linspace(0, 1, fade)
            envelope[-fade:] = np.linspace(1, 0, fade)
        
        wave = wave * envelope
        wave = (wave * 32767 * 0.25).astype(np.int16)
        wave = np.repeat(wave.reshape(-1, 1), 2, axis=1)
        
        sound = pygame.sndarray.make_sound(wave)
        sound.set_volume(0.4)
        return sound
    except:
        return generate_ambient_fallback()

def load_sound_asset(filepath, fallback_generator, volume=1.0):
    import os
    try:
        if os.path.exists(filepath):
            sound = pygame.mixer.Sound(filepath)
            sound.set_volume(volume)
            return sound
        else:
            return fallback_generator()
    except:
        return fallback_generator()

# --- ÇİZİM FONKSİYONLARI ---

def draw_text(surface, text, color, rect, font_size, aa=False, bkg=None):
    try:
        font = pygame.font.Font(None, font_size)
        text_surface = font.render(text, aa, color, bkg)
        text_rect = text_surface.get_rect()
        text_rect.center = (rect[0] + rect[2] // 2, rect[1] + rect[3] // 2)
        surface.blit(text_surface, text_rect)
    except:
        pygame.draw.rect(surface, color, rect, 1)

def draw_text_with_shadow(surface, text, font, pos, color, shadow_color=(0, 0, 0), offset=(2, 2), align='topleft'):
    """Metni gölgeli çizer"""
    try:
        text_surf = font.render(text, True, color)
        shadow_surf = font.render(text, True, shadow_color)
        
        # Hizalama işlemi
        text_rect = text_surf.get_rect()
        shadow_rect = shadow_surf.get_rect()
        
        # Align attribute'unu ayarla
        if hasattr(text_rect, align):
            setattr(text_rect, align, pos)
            shadow_pos = (getattr(text_rect, align)[0] + offset[0], 
                         getattr(text_rect, align)[1] + offset[1])
            setattr(shadow_rect, align, shadow_pos)
        else:
            # Varsayılan: topleft
            text_rect.topleft = pos
            shadow_rect.topleft = (pos[0] + offset[0], pos[1] + offset[1])
        
        surface.blit(shadow_surf, shadow_rect)
        surface.blit(text_surf, text_rect)
    except Exception as e:
        print(f"Shadow text error: {e}")

def wrap_text(text, font, max_width):
    """Metni satırlara böler"""
    words = text.split(' ')
    lines = []
    current_line = []
    for word in words:
        test_line = ' '.join(current_line + [word])
        w, h = font.size(test_line)
        if w < max_width:
            current_line.append(word)
        else:
            lines.append(' '.join(current_line))
            current_line = [word]
    lines.append(' '.join(current_line))
    return lines

def draw_animated_player(surface, shape, x, y, size, color, anim_params):
    try:
        scale = anim_params.get('scale', 1.0)
        rotation = anim_params.get('rotation', 0)
        pulse_alpha = anim_params.get('pulse_alpha', 1.0)
        shake_offset = anim_params.get('shake_offset', (0, 0))
        
        x += shake_offset[0]
        y += shake_offset[1]
        
        r, g, b = color
        pulse_factor = 0.5 + 0.5 * pulse_alpha
        anim_color = (min(255, int(r * pulse_factor)), min(255, int(g * pulse_factor)), min(255, int(b * pulse_factor)))
        
        scaled_size = int(size * scale)
        
        if shape == 'circle':
            pygame.draw.circle(surface, anim_color, (int(x), int(y)), scaled_size)
            inner_color = (min(255, anim_color[0] + 50), min(255, anim_color[1] + 50), min(255, anim_color[2] + 50))
            pygame.draw.circle(surface, inner_color, (int(x), int(y)), max(1, scaled_size // 2))
        elif shape == 'square':
            rect = pygame.Rect(x - scaled_size, y - scaled_size, scaled_size*2, scaled_size*2)
            pygame.draw.rect(surface, anim_color, rect)
        else:
            pygame.draw.circle(surface, anim_color, (int(x), int(y)), scaled_size)
            
    except Exception as e:
        pygame.draw.circle(surface, color, (int(x), int(y)), size)

def lerp(start, end, t):
    return start + (end - start) * t

def clamp(value, min_val, max_val):
    return max(min_val, min(value, max_val))
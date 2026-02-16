import pygame
import random
import math
import numpy as np
import os

# --- GELİŞMİŞ SES YÖNETİCİSİ (BU SINIF TÜM SESİ YÖNETECEK) ---
class AudioManager:
    def __init__(self):
        try:
            pygame.mixer.init(44100, -16, 2, 512)
            pygame.mixer.set_num_channels(32) # Efektler için bol kanal
        except:
            print("Ses kartı başlatılamadı.")

        # Kanalları ayır
        self.music_channel = pygame.mixer.Channel(0) # Müzik her zaman Kanal 0
        
        # Ses seviyeleri (Varsayılan)
        self.master_vol = 1.0
        self.music_vol = 0.5
        self.sfx_vol = 0.8

    def update_settings(self, settings_dict):
        """Ayarlar menüsünden gelen veriyi anında işler"""
        self.master_vol = settings_dict.get("sound_volume", 1.0)
        self.music_vol = settings_dict.get("music_volume", 0.5)
        self.sfx_vol = settings_dict.get("effects_volume", 0.8)
        self._apply_volumes()

    def _apply_volumes(self):
        """Matematiksel olarak sesleri uygular: Master * Özel Seviye"""
        # Müzik Kanalı Ses Ayarı
        final_music_vol = self.master_vol * self.music_vol
        self.music_channel.set_volume(final_music_vol)
        
        # Efektler için genel bir ayar yok, bu yüzden çalan/çalacak sesleri etkilemeliyiz
        # Ancak Pygame'de SFX kanalları dinamik olduğu için,
        # Sesi çalarken o anki volume ile çalacağız.

    def play_music(self, sound_obj, loops=-1):
        """Müziği güvenli şekilde çalar"""
        if not sound_obj: return
        
        # Eğer zaten aynı müzik çalıyorsa baştan başlatma (isteğe bağlı)
        # Ama burada basitçe kanalı durdurup yenisini çalıyoruz
        if self.music_channel.get_busy():
            self.music_channel.stop()
            
        self.music_channel.play(sound_obj, loops=loops)
        self._apply_volumes() # Sesi ayarla

    def play_sfx(self, sound_obj):
        """Efekt sesini boş bir kanalda çalar"""
        if not sound_obj: return
        
        # Boş bir kanal bul
        channel = pygame.mixer.find_channel(True) 
        if channel:
            # Kanal 0 Müzik için ayrıldı, onu kullanma
            if channel == self.music_channel:
                channel = pygame.mixer.find_channel(True) 

            # Ses seviyesini hesapla: Master * SFX
            final_sfx_vol = self.master_vol * self.sfx_vol
            channel.set_volume(final_sfx_vol)
            channel.play(sound_obj)

    def stop_music(self):
        self.music_channel.stop()

    def pause_all(self):
        pygame.mixer.pause()

    def unpause_all(self):
        pygame.mixer.unpause()

# Global Instance (Main.py buradan erişecek)
audio_manager = AudioManager()


# --- SİSTEM FONKSİYONLARI (GÜNCELLENDİ: ARTIK VOLUME HARDCODE EDİLMİYOR) ---

def generate_sound_effect(base_freq, duration, volume=1.0):
    # NOT: Volume parametresini artık dikkate almıyoruz, 
    # çünkü ses seviyesini AudioManager yönetecek. Ham sesi tam güçte üretiyoruz.
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
        return sound
    except Exception as e:
        return get_silent_sound()

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
        return sound
    except Exception:
        return get_silent_sound()

def generate_calm_ambient():
    try:
        sample_rate = 44100
        duration = 15.0
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        base_freq = 110.0
        wave = 0.3 * np.sin(2 * np.pi * base_freq * t)
        wave += 0.2 * np.sin(2 * np.pi * base_freq * 1.5 * t)
        envelope = np.ones_like(t)
        fade = int(sample_rate * 3.0)
        if fade > 0:
            envelope[:fade] = np.linspace(0, 1, fade)
            envelope[-fade:] = np.linspace(1, 0, fade)
        wave = wave * envelope
        wave = (wave * 32767 * 0.25).astype(np.int16)
        wave = np.repeat(wave.reshape(-1, 1), 2, axis=1)
        sound = pygame.sndarray.make_sound(wave)
        return sound
    except:
        return generate_ambient_fallback()

def get_silent_sound():
    try:
        buffer = bytearray([0] * 200) 
        return pygame.mixer.Sound(buffer=buffer)
    except:
        class MockSound:
            def play(self, *args, **kwargs): pass
            def set_volume(self, v): pass
            def stop(self): pass
        return MockSound()

def load_sound_asset(filepath, fallback_generator=None, volume=1.0):
    # NOT: Buradaki volume parametresi artık sadece 'dosya sesi çok yüksekse kısmak' için kullanılmalı.
    # Ana kontrol Audio Manager'da.
    if not os.path.exists(filepath):
        if fallback_generator: return fallback_generator()
        return get_silent_sound()
    try:
        sound = pygame.mixer.Sound(filepath)
        return sound
    except Exception:
        if fallback_generator: return fallback_generator()
        return get_silent_sound()

# --- ÇİZİM FONKSİYONLARI (DEĞİŞMEDİ) ---
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
    try:
        text_surf = font.render(text, True, color)
        shadow_surf = font.render(text, True, shadow_color)
        text_rect = text_surf.get_rect()
        shadow_rect = shadow_surf.get_rect()
        if hasattr(text_rect, align):
            setattr(text_rect, align, pos)
            shadow_pos = (getattr(text_rect, align)[0] + offset[0], 
                         getattr(text_rect, align)[1] + offset[1])
            setattr(shadow_rect, align, shadow_pos)
        else:
            text_rect.topleft = pos
            shadow_rect.topleft = (pos[0] + offset[0], pos[1] + offset[1])
        surface.blit(shadow_surf, shadow_rect)
        surface.blit(text_surf, text_rect)
    except Exception as e:
        print(f"Shadow text error: {e}")

def wrap_text(text, font, max_width):
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
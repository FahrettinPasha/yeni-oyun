import json
import os

SAVE_FILE = "save_data.json"

class SaveManager:
    def __init__(self):
        self.data = self.load_data()

    def load_data(self):
        """Kayıt dosyasını yükler, yoksa varsayılanı oluşturur."""
        if not os.path.exists(SAVE_FILE):
            return self.create_default_data()
        
        try:
            with open(SAVE_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            print(f"Kayıt dosyası bozuk, varsayılanlar yükleniyor. Hata: {e}")
            return self.create_default_data()

    def create_default_data(self):
        """Varsayılan oyun verilerini oluşturur."""
        default_data = {
            "karma": 0,  # YENİ: Başlangıç karması nötr (0)
            "easy_mode": {
                "unlocked_levels": 1,
                "completed_levels": [],
                "high_scores": {}
            },
            "settings": {
                "sound_volume": 0.7,
                "music_volume": 0.5
            }
        }
        self.save_data(default_data)
        return default_data

    def save_data(self, data=None):
        """Verileri diske yazar."""
        if data:
            self.data = data
        try:
            with open(SAVE_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except IOError as e:
            print(f"Kayıt Hatası: {e}")

    def update_karma(self, amount):
        """Karmayı günceller ve kaydeder."""
        if "karma" not in self.data:
            self.data["karma"] = 0
        
        self.data["karma"] += amount
        
        # ESKİ KOD (SİLİNECEK):
        # self.data["karma"] = max(-100, min(100, self.data["karma"]))
        
        # YENİ KOD (SINIRLARI GENİŞLET):
        # Soykırım Modu için -1000'e kadar izin verelim
        self.data["karma"] = max(-1000, min(1000, self.data["karma"]))
        
        self.save_data()

    def get_karma(self):
        """Mevcut karma değerini döndürür."""
        return self.data.get("karma", 0)

    def update_high_score(self, mode, level_idx, score):
        """Eğer yeni skor daha yüksekse günceller."""
        if mode not in self.data:
            self.data[mode] = {"unlocked_levels": 1, "completed_levels": [], "high_scores": {}}
        
        str_level = str(level_idx)
        current_high = self.data[mode]["high_scores"].get(str_level, 0)
        
        if score > current_high:
            self.data[mode]["high_scores"][str_level] = int(score)
            self.save_data()
            return True
        return False

    def unlock_next_level(self, mode, current_level_idx):
        """Bölüm tamamlandığında bir sonrakini açar."""
        if mode not in self.data:
            self.data[mode] = {"unlocked_levels": 1, "completed_levels": [], "high_scores": {}}
            
        if current_level_idx not in self.data[mode]["completed_levels"]:
            self.data[mode]["completed_levels"].append(current_level_idx)
            
        next_level = current_level_idx + 1
        if next_level > self.data[mode]["unlocked_levels"]:
            self.data[mode]["unlocked_levels"] = next_level
            
        self.save_data()
        return True

    def reset_progress(self):
        """Tüm ilerlemeyi siler."""
        self.data = self.create_default_data()
        return True

    def get_high_score(self, mode, level_idx):
        str_level = str(level_idx)
        if mode in self.data and "high_scores" in self.data[mode]:
            return self.data[mode]["high_scores"].get(str_level, 0)
        return 0

    def is_level_unlocked(self, mode, level_idx):
        if mode in self.data:
            return level_idx <= self.data[mode]["unlocked_levels"]
        return level_idx == 1

    def is_level_completed(self, mode, level_idx):
        if mode in self.data:
            return level_idx in self.data[mode]["completed_levels"]
        return False

    def update_settings(self, settings_dict):
        if "settings" not in self.data:
            self.data["settings"] = {}
        self.data["settings"].update(settings_dict)
        self.save_data()
        return True

    def get_settings(self):
        return self.data.get("settings", {
            "sound_volume": 0.7,
            "music_volume": 0.5
        })

# Global instance
save_manager = SaveManager()
def add_saved_soul(self, amount=1):
        """Kurtarılan ruh sayısını artırır."""
        if "saved_souls" not in self.data:
            self.data["saved_souls"] = 0
        self.data["saved_souls"] += amount
        self.save_data()

def get_saved_count(self):
        """Toplam kurtarılan ruh sayısını verir."""
        return self.data.get("saved_souls", 0)
import pygame
import math
import array


class AudioManager:
    def __init__(self, config: dict):
        pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
        
        self.master_volume = config.get("master_volume", 0.7)
        self.sfx_volume = config.get("sfx_volume", 0.8)
        self.music_volume = config.get("music_volume", 0.5)
        
        self.sounds = {}
        self._generate_sounds()
        
    def _generate_sounds(self):
        self.sounds["jump"] = self._create_tone(600, 0.1, 900, "sine")
        self.sounds["score"] = self._create_tone(880, 0.15, 1100, "sine")
        self.sounds["hit"] = self._create_tone(150, 0.2, 80, "square")
        self.sounds["click"] = self._create_tone(500, 0.05, None, "sine")
        
    def _create_tone(self, frequency: float, duration: float, 
                     freq_end: float = None, wave_type: str = "sine") -> pygame.mixer.Sound:
        sample_rate = 44100
        n_samples = int(sample_rate * duration)
        
        if freq_end is None:
            freq_end = frequency
            
        buf = array.array('h')
        
        for i in range(n_samples):
            t = i / sample_rate
            progress = i / n_samples
            freq = frequency + (freq_end - frequency) * progress
            
            if wave_type == "sine":
                value = math.sin(2 * math.pi * freq * t)
            elif wave_type == "square":
                value = 1 if math.sin(2 * math.pi * freq * t) > 0 else -1
            else:
                value = math.sin(2 * math.pi * freq * t)
            
            envelope = (1 - progress) ** 0.5
            sample = int(value * envelope * 32767 * 0.3)
            buf.append(sample)
            
        return pygame.mixer.Sound(buffer=buf)
    
    def play(self, sound_name: str):
        if sound_name in self.sounds:
            volume = self.master_volume * self.sfx_volume
            self.sounds[sound_name].set_volume(volume)
            self.sounds[sound_name].play()
            
    def set_master_volume(self, volume: float):
        self.master_volume = max(0, min(1, volume))
        
    def set_sfx_volume(self, volume: float):
        self.sfx_volume = max(0, min(1, volume))
        
    def set_music_volume(self, volume: float):
        self.music_volume = max(0, min(1, volume))
        pygame.mixer.music.set_volume(self.master_volume * self.music_volume)
        
    def get_volumes(self) -> dict:
        return {
            "master": self.master_volume,
            "sfx": self.sfx_volume,
            "music": self.music_volume
        }

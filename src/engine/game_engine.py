import pygame
import json
import os
from enum import Enum


class GameState(Enum):
    MENU = "menu"
    COUNTDOWN = "countdown"
    PLAYING = "playing"
    GAME_OVER = "game_over"
    PAUSED = "paused"


class GameEngine:
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.config = self._load_config()
        
        window_config = self.config["window"]
        self.width = window_config["width"]
        self.height = window_config["height"]
        self.fps = window_config["fps"]
        
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption(self.config["game"]["title"])
        
        self.clock = pygame.time.Clock()
        self.state = GameState.MENU
        self.running = True
        self.difficulty = "medium"
        
        self.score = 0
        self.high_score = self._load_high_score()
        
    def _load_config(self) -> dict:
        config_path = os.path.join(os.path.dirname(__file__), 
                                   "..", "config", "game_config.json")
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    def _load_high_score(self) -> int:
        try:
            save_path = os.path.join(os.path.dirname(__file__), 
                                     "..", "saves", "highscore.txt")
            with open(save_path, "r") as f:
                return int(f.read().strip())
        except:
            return 0
    
    def save_high_score(self):
        if self.score > self.high_score:
            self.high_score = self.score
            save_dir = os.path.join(os.path.dirname(__file__), "..", "saves")
            os.makedirs(save_dir, exist_ok=True)
            save_path = os.path.join(save_dir, "highscore.txt")
            with open(save_path, "w") as f:
                f.write(str(self.high_score))
    
    def get_difficulty_settings(self) -> dict:
        return self.config["difficulty"][self.difficulty]
    
    def set_state(self, state: GameState):
        self.state = state
        
    def reset_score(self):
        self.score = 0
        
    def add_score(self, points: int = 1):
        self.score += points
        
    def tick(self) -> float:
        return self.clock.tick(self.fps) / 1000.0
    
    def quit(self):
        self.save_high_score()
        pygame.quit()

import pygame
import random
from .game_object import MovingObject


class Pipe(MovingObject):
    def __init__(self, x: float, screen_height: int, ground_height: int,
                 config: dict, colors: dict):
        pipe_config = config["pipes"]
        super().__init__(x, 0, pipe_config["width"], screen_height, pipe_config["speed"])
        
        self.gap = pipe_config["gap"]
        self.min_height = pipe_config["min_height"]
        self.max_height = pipe_config["max_height"]
        self.ground_height = ground_height
        self.screen_height = screen_height
        
        self.colors = colors
        self.passed = False
        
        max_gap_top = screen_height - ground_height - self.gap - self.min_height
        self.gap_y = random.randint(self.min_height, min(self.max_height, max_gap_top))
        
        self._create_sprites()
        
    def set_colors(self, colors: dict):
        self.colors = colors
        self._create_sprites()
        
    def _create_sprites(self):
        cap_height = 26
        cap_overhang = 4
        
        pipe_color = tuple(self.colors.get("pipe", [34, 139, 34]))
        highlight_color = tuple(self.colors.get("pipe_highlight", [60, 179, 60]))
        border_color = tuple(self.colors.get("pipe_border", [0, 100, 0]))
        shadow_color = tuple(max(0, c - 30) for c in pipe_color)
        
        self.top_surface = pygame.Surface((self.width + cap_overhang * 2, self.gap_y), pygame.SRCALPHA)
        
        body_rect = pygame.Rect(cap_overhang, 0, self.width, self.gap_y - cap_height)
        pygame.draw.rect(self.top_surface, pipe_color, body_rect)
        
        highlight_rect = pygame.Rect(cap_overhang + 4, 0, 10, self.gap_y - cap_height)
        pygame.draw.rect(self.top_surface, highlight_color, highlight_rect)
        
        shadow_rect = pygame.Rect(cap_overhang + self.width - 10, 0, 10, self.gap_y - cap_height)
        pygame.draw.rect(self.top_surface, shadow_color, shadow_rect)
        pygame.draw.rect(self.top_surface, border_color, body_rect, 2)
        
        cap_rect = pygame.Rect(0, self.gap_y - cap_height, self.width + cap_overhang * 2, cap_height)
        pygame.draw.rect(self.top_surface, pipe_color, cap_rect, border_radius=3)
        
        cap_highlight = pygame.Rect(4, self.gap_y - cap_height + 4, self.width + cap_overhang * 2 - 8, 8)
        pygame.draw.rect(self.top_surface, highlight_color, cap_highlight, border_radius=2)
        pygame.draw.rect(self.top_surface, border_color, cap_rect, 2, border_radius=3)
        
        bottom_height = self.screen_height - self.ground_height - self.gap_y - self.gap
        self.bottom_surface = pygame.Surface((self.width + cap_overhang * 2, bottom_height), pygame.SRCALPHA)
        
        cap_rect = pygame.Rect(0, 0, self.width + cap_overhang * 2, cap_height)
        pygame.draw.rect(self.bottom_surface, pipe_color, cap_rect, border_radius=3)
        
        cap_highlight = pygame.Rect(4, 4, self.width + cap_overhang * 2 - 8, 8)
        pygame.draw.rect(self.bottom_surface, highlight_color, cap_highlight, border_radius=2)
        pygame.draw.rect(self.bottom_surface, border_color, cap_rect, 2, border_radius=3)
        
        body_rect = pygame.Rect(cap_overhang, cap_height, self.width, bottom_height - cap_height)
        pygame.draw.rect(self.bottom_surface, pipe_color, body_rect)
        
        highlight_rect = pygame.Rect(cap_overhang + 4, cap_height, 10, bottom_height - cap_height)
        pygame.draw.rect(self.bottom_surface, highlight_color, highlight_rect)
        
        shadow_rect = pygame.Rect(cap_overhang + self.width - 10, cap_height, 10, bottom_height - cap_height)
        pygame.draw.rect(self.bottom_surface, shadow_color, shadow_rect)
        pygame.draw.rect(self.bottom_surface, border_color, body_rect, 2)
        
    def update(self, dt: float):
        self.x -= self.speed
        
    def draw(self, surface: pygame.Surface):
        surface.blit(self.top_surface, (self.x - 4, 0))
        bottom_y = self.gap_y + self.gap
        surface.blit(self.bottom_surface, (self.x - 4, bottom_y))
        
    def get_top_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), 0, self.width, self.gap_y)
    
    def get_bottom_rect(self) -> pygame.Rect:
        bottom_y = self.gap_y + self.gap
        bottom_height = self.screen_height - self.ground_height - bottom_y
        return pygame.Rect(int(self.x), bottom_y, self.width, bottom_height)
    
    def is_off_screen(self) -> bool:
        return self.x + self.width < 0


class PipeManager:
    def __init__(self, screen_width: int, screen_height: int, 
                 ground_height: int, config: dict, colors: dict):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.ground_height = ground_height
        self.config = config
        self.colors = colors
        
        self.pipes = []
        self.spawn_timer = 0
        self.spawn_interval = config["pipes"]["spawn_interval"] / 1000.0
        
    def set_colors(self, colors: dict):
        self.colors = colors
        for pipe in self.pipes:
            pipe.set_colors(colors)
        
    def update(self, dt: float) -> int:
        self.spawn_timer += dt
        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0
            self.spawn_pipe()
        
        for pipe in self.pipes[:]:
            pipe.update(dt)
            if pipe.is_off_screen():
                self.pipes.remove(pipe)
        return 0
    
    def spawn_pipe(self):
        pipe = Pipe(self.screen_width, self.screen_height, 
                   self.ground_height, self.config, self.colors)
        self.pipes.append(pipe)
        
    def draw(self, surface: pygame.Surface):
        for pipe in self.pipes:
            pipe.draw(surface)
            
    def reset(self):
        self.pipes.clear()
        self.spawn_timer = 0
        
    def set_speed(self, speed: float):
        for pipe in self.pipes:
            pipe.speed = speed
        self.config["pipes"]["speed"] = speed
        
    def set_gap(self, gap: int):
        self.config["pipes"]["gap"] = gap

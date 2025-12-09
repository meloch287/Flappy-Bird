import pygame
import random
from .game_object import MovingObject


class Ground(MovingObject):
    def __init__(self, screen_width: int, screen_height: int, config: dict, colors: dict):
        ground_config = config["ground"]
        height = ground_config["height"]
        y = screen_height - height
        
        super().__init__(0, y, screen_width * 2, height, ground_config["speed"])
        
        self.screen_width = screen_width
        self.colors = colors
        self.scroll_x = 0
        
        self._create_surface()
        
    def set_colors(self, colors: dict):
        self.colors = colors
        self._create_surface()
        
    def _create_surface(self):
        self.surface = pygame.Surface((self.width, self.height))
        
        ground_color = tuple(self.colors.get("ground", [222, 184, 135]))
        ground_dark = tuple(self.colors.get("ground_dark", [180, 140, 100]))
        grass_color = tuple(self.colors.get("grass", [124, 252, 0]))
        
        self.surface.fill(ground_color)
        
        grass_height = 18
        for i in range(grass_height):
            factor = i / grass_height
            color = tuple(int(grass_color[j] * (1 - factor * 0.3)) for j in range(3))
            pygame.draw.line(self.surface, color, (0, i), (self.width, i))
        
        for x in range(0, self.width, 8):
            height_var = (x * 7) % 5 + 3
            points = [(x, grass_height), (x + 4, grass_height - height_var), (x + 8, grass_height)]
            pygame.draw.polygon(self.surface, grass_color, points)
        
        pygame.draw.line(self.surface, ground_dark, (0, grass_height), (self.width, grass_height), 3)
        
        stripe_color = tuple(min(255, c + 20) for c in ground_color)
        for i in range(0, self.width + self.height, 25):
            pygame.draw.line(self.surface, stripe_color, (i, grass_height + 5), (i - 30, self.height), 2)
        
        stone_color = tuple(max(0, c - 40) for c in ground_color)
        random.seed(42)
        for _ in range(30):
            x = random.randint(0, self.width)
            y = random.randint(grass_height + 10, self.height - 10)
            size = random.randint(2, 5)
            pygame.draw.ellipse(self.surface, stone_color, (x, y, size * 2, size))
        
    def update(self, dt: float):
        self.scroll_x -= self.speed
        if self.scroll_x <= -self.screen_width:
            self.scroll_x = 0
            
    def draw(self, surface: pygame.Surface):
        surface.blit(self.surface, (self.scroll_x, self.y))
        
    def reset(self):
        self.scroll_x = 0

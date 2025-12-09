import pygame
from abc import ABC, abstractmethod


class GameObject(ABC):
    def __init__(self, x: float, y: float, width: int, height: int):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.active = True
        
    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    
    @abstractmethod
    def update(self, dt: float):
        pass
    
    @abstractmethod
    def draw(self, surface: pygame.Surface):
        pass


class MovingObject(GameObject):
    def __init__(self, x: float, y: float, width: int, height: int, speed: float):
        super().__init__(x, y, width, height)
        self.speed = speed
        self.dx = 0
        self.dy = 0
        
    def move(self, dt: float):
        self.x += self.dx * self.speed * dt * 60
        self.y += self.dy * self.speed * dt * 60


class AnimatedObject(MovingObject):
    def __init__(self, x: float, y: float, width: int, height: int, speed: float):
        super().__init__(x, y, width, height, speed)
        self.animation_frames = []
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.1
        
    def update_animation(self, dt: float):
        self.animation_timer += dt
        if self.animation_timer >= self.animation_speed:
            self.animation_timer = 0
            self.current_frame = (self.current_frame + 1) % max(1, len(self.animation_frames))

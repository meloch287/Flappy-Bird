import pygame
from .game_object import AnimatedObject


class Bird(AnimatedObject):
    def __init__(self, x: float, y: float, config: dict, colors: dict):
        bird_config = config["bird"]
        super().__init__(x, y, bird_config["width"], bird_config["height"], 0)
        
        self.gravity = bird_config["gravity"]
        self.jump_strength = bird_config["jump_strength"]
        self.max_fall_speed = bird_config["max_fall_speed"]
        self.rotation_speed = bird_config["rotation_speed"]
        
        self.velocity = 0
        self.rotation = 0
        self.colors = colors
        
        self._create_sprites()
        self.animation_speed = 0.08
        
    def set_colors(self, colors: dict):
        self.colors = colors
        self._create_sprites()
        
    def _create_sprites(self):
        self.animation_frames = []
        
        body_color = tuple(self.colors.get("bird_body", [255, 220, 0]))
        wing_color = tuple(self.colors.get("bird_wing", [255, 165, 0]))
        beak_color = tuple(self.colors.get("bird_beak", [255, 69, 0]))
        eye_color = tuple(self.colors.get("bird_eye", [255, 255, 255]))
        
        for wing_offset in [0, -3, -6, -3]:
            frame = pygame.Surface((self.width + 8, self.height + 4), pygame.SRCALPHA)
            
            body_rect = pygame.Rect(4, 4, self.width - 4, self.height - 4)
            pygame.draw.ellipse(frame, body_color, body_rect)
            
            highlight_color = tuple(min(255, c + 40) for c in body_color)
            highlight_rect = pygame.Rect(body_rect.x + 4, body_rect.y + 2, 
                                        body_rect.width // 2, body_rect.height // 2)
            pygame.draw.ellipse(frame, highlight_color, highlight_rect)
            pygame.draw.ellipse(frame, (0, 0, 0), body_rect, 2)
            
            wing_rect = pygame.Rect(10, 12 + wing_offset, 14, 10)
            pygame.draw.ellipse(frame, wing_color, wing_rect)
            pygame.draw.ellipse(frame, (0, 0, 0), wing_rect, 1)
            
            eye_x, eye_y = self.width - 6, 8
            pygame.draw.circle(frame, eye_color, (eye_x, eye_y), 6)
            pygame.draw.circle(frame, (0, 0, 0), (eye_x, eye_y), 6, 1)
            pygame.draw.circle(frame, (0, 0, 0), (eye_x + 1, eye_y), 3)
            pygame.draw.circle(frame, (255, 255, 255), (eye_x + 2, eye_y - 1), 1)
            
            beak_points = [(self.width, 12), (self.width + 8, 15), (self.width, 18)]
            pygame.draw.polygon(frame, beak_color, beak_points)
            pygame.draw.polygon(frame, (0, 0, 0), beak_points, 1)
            pygame.draw.line(frame, (0, 0, 0), (self.width, 15), (self.width + 6, 15), 1)
            
            self.animation_frames.append(frame)
    
    def jump(self):
        self.velocity = self.jump_strength
        
    def update(self, dt: float):
        self.velocity += self.gravity
        self.velocity = min(self.velocity, self.max_fall_speed)
        self.y += self.velocity
        
        target_rotation = 25 if self.velocity < 0 else max(-90, -self.velocity * 6)
        self.rotation += (target_rotation - self.rotation) * 0.15
        
        self.animation_speed = 0.05 if self.velocity < 0 else 0.1
        self.update_animation(dt)
        
    def draw(self, surface: pygame.Surface):
        if self.animation_frames:
            frame = self.animation_frames[self.current_frame]
            rotated = pygame.transform.rotate(frame, self.rotation)
            rect = rotated.get_rect(center=(self.x + self.width // 2, 
                                            self.y + self.height // 2))
            surface.blit(rotated, rect)
    
    def get_rect(self) -> pygame.Rect:
        margin = 5
        return pygame.Rect(int(self.x) + margin, int(self.y) + margin,
                          self.width - margin * 2, self.height - margin * 2)
    
    def reset(self, y: float):
        self.y = y
        self.velocity = 0
        self.rotation = 0

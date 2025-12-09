import pygame


class PhysicsEngine:
    @staticmethod
    def check_collision(rect1: pygame.Rect, rect2: pygame.Rect) -> bool:
        return rect1.colliderect(rect2)
    
    @staticmethod
    def check_bounds(rect: pygame.Rect, screen_height: int, ground_height: int) -> bool:
        if rect.top < 0:
            return True
        if rect.bottom > screen_height - ground_height:
            return True
        return False
    
    @staticmethod
    def apply_gravity(velocity: float, gravity: float, max_speed: float) -> float:
        velocity += gravity
        return min(velocity, max_speed)
    
    @staticmethod
    def calculate_rotation(velocity: float, max_angle: float = 25) -> float:
        if velocity < 0:
            return min(-velocity * 3, max_angle)
        else:
            return max(-velocity * 3, -90)


class CollisionManager:
    def __init__(self, screen_height: int, ground_height: int):
        self.screen_height = screen_height
        self.ground_height = ground_height
        
    def check_bird_pipe_collision(self, bird_rect: pygame.Rect, pipes: list) -> bool:
        for pipe in pipes:
            if PhysicsEngine.check_collision(bird_rect, pipe.get_top_rect()):
                return True
            if PhysicsEngine.check_collision(bird_rect, pipe.get_bottom_rect()):
                return True
        return False
    
    def check_bird_bounds(self, bird_rect: pygame.Rect) -> bool:
        return PhysicsEngine.check_bounds(bird_rect, self.screen_height, self.ground_height)
    
    def check_pipe_passed(self, bird_x: float, pipe) -> bool:
        pipe_right = pipe.x + pipe.width
        return bird_x > pipe_right and not pipe.passed

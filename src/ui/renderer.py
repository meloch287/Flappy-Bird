import pygame


class Renderer:
    def __init__(self, screen: pygame.Surface, colors: dict):
        self.screen = screen
        self.width = screen.get_width()
        self.height = screen.get_height()
        self.colors = colors
        self.background = None
        self.particles = []
        
        self._create_background()
        
    def set_theme(self, colors: dict):
        self.colors = colors
        self._create_background()
        
    def _create_background(self):
        self.background = pygame.Surface((self.width, self.height))
        
        sky_top = self.colors.get("sky", [135, 206, 235])
        sky_bottom = self.colors.get("sky_bottom", [176, 224, 230])
        
        for y in range(self.height):
            factor = y / self.height
            r = int(sky_top[0] + (sky_bottom[0] - sky_top[0]) * factor)
            g = int(sky_top[1] + (sky_bottom[1] - sky_top[1]) * factor)
            b = int(sky_top[2] + (sky_bottom[2] - sky_top[2]) * factor)
            pygame.draw.line(self.background, (r, g, b), (0, y), (self.width, y))
        
        self._draw_clouds()
        
    def _draw_clouds(self):
        cloud_color = tuple(self.colors.get("cloud", [255, 255, 255]))
        cloud_positions = [
            (50, 80, 1.0), (200, 120, 0.8), (320, 60, 0.9), 
            (100, 200, 0.7), (280, 180, 0.85), (380, 100, 0.6)
        ]
        
        for x, y, scale in cloud_positions:
            self._draw_cloud(x, y, scale, cloud_color)
            
    def _draw_cloud(self, x: int, y: int, scale: float, color: tuple):
        cloud_surf = pygame.Surface((100, 60), pygame.SRCALPHA)
        
        circles = [(25, 35, 20), (45, 30, 28), (70, 35, 22), (50, 20, 18)]
        
        for cx, cy, r in circles:
            for i in range(r, 0, -2):
                alpha = int(180 * (i / r))
                pygame.draw.circle(cloud_surf, (*color[:3], alpha), 
                                 (int(cx * scale), int(cy * scale)), int(i * scale))
        
        self.background.blit(cloud_surf, (x, y))
            
    def draw_background(self):
        self.screen.blit(self.background, (0, 0))
        
    def draw_score(self, score: int, y: int = 50):
        font = pygame.font.Font(None, 72)
        
        text_color = tuple(self.colors.get("text", [255, 255, 255]))
        shadow_color = tuple(self.colors.get("text_shadow", [0, 0, 0]))
        
        for offset in [(3, 3), (2, 2)]:
            shadow = font.render(str(score), True, shadow_color)
            shadow.set_alpha(100)
            shadow_rect = shadow.get_rect(centerx=self.width // 2 + offset[0], y=y + offset[1])
            self.screen.blit(shadow, shadow_rect)
        
        text = font.render(str(score), True, text_color)
        text_rect = text.get_rect(centerx=self.width // 2, y=y)
        self.screen.blit(text, text_rect)
        
        highlight = font.render(str(score), True, (255, 255, 255))
        highlight.set_alpha(100)
        self.screen.blit(highlight, (text_rect.x, text_rect.y - 2))
        
    def draw_text(self, text: str, size: int, x: int, y: int, 
                  color: tuple = None, center: bool = True, shadow: bool = True):
        if color is None:
            color = tuple(self.colors.get("text", [255, 255, 255]))
            
        font = pygame.font.Font(None, size)
        
        if shadow:
            shadow_color = tuple(self.colors.get("text_shadow", [0, 0, 0]))
            shadow_surf = font.render(text, True, shadow_color)
            if center:
                shadow_rect = shadow_surf.get_rect(center=(x + 2, y + 2))
            else:
                shadow_rect = shadow_surf.get_rect(topleft=(x + 2, y + 2))
            self.screen.blit(shadow_surf, shadow_rect)
        
        surface = font.render(text, True, color)
        if center:
            rect = surface.get_rect(center=(x, y))
        else:
            rect = surface.get_rect(topleft=(x, y))
        self.screen.blit(surface, rect)
        
    def add_particle(self, x: int, y: int, color: tuple):
        self.particles.append({
            "x": x, "y": y,
            "vx": (pygame.time.get_ticks() % 10 - 5) * 0.5,
            "vy": -3,
            "life": 1.0,
            "color": color
        })
        
    def update_particles(self, dt: float):
        for p in self.particles[:]:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["vy"] += 0.1
            p["life"] -= dt * 2
            
            if p["life"] <= 0:
                self.particles.remove(p)
                
    def draw_particles(self):
        for p in self.particles:
            alpha = int(255 * p["life"])
            size = int(5 * p["life"])
            if size > 0:
                surf = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(surf, (*p["color"][:3], alpha), (size, size), size)
                self.screen.blit(surf, (p["x"] - size, p["y"] - size))

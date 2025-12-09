import pygame


class UIColors:
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (128, 128, 128)
    LIGHT_GRAY = (200, 200, 200)
    DARK_GRAY = (60, 60, 60)
    

class Button:
    def __init__(self, x: int, y: int, width: int, height: int, 
                 text: str, color: tuple, hover_color: tuple = None, icon: str = None):
        self.rect = pygame.Rect(x - width // 2, y - height // 2, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color or self._lighten(color, 30)
        self.icon = icon
        self.is_hovered = False
        self.press_scale = 1.0
        self.hover_offset = 0
        
    def _lighten(self, color: tuple, amount: int) -> tuple:
        return tuple(min(255, c + amount) for c in color)
    
    def _darken(self, color: tuple, amount: int) -> tuple:
        return tuple(max(0, c - amount) for c in color)
        
    def update(self, mouse_pos: tuple, dt: float = 0.016):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        target_offset = -3 if self.is_hovered else 0
        self.hover_offset += (target_offset - self.hover_offset) * 0.2
        
    def draw(self, surface: pygame.Surface):
        draw_rect = self.rect.copy()
        draw_rect.y += int(self.hover_offset)
        
        color = self.hover_color if self.is_hovered else self.color
        
        shadow_rect = draw_rect.copy()
        shadow_rect.y += 4
        pygame.draw.rect(surface, self._darken(color, 80), shadow_rect, border_radius=12)
        
        pygame.draw.rect(surface, color, draw_rect, border_radius=12)
        
        highlight_rect = pygame.Rect(draw_rect.x + 4, draw_rect.y + 4, 
                                     draw_rect.width - 8, draw_rect.height // 3)
        highlight_surf = pygame.Surface((highlight_rect.width, highlight_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(highlight_surf, (255, 255, 255, 60), 
                        (0, 0, highlight_rect.width, highlight_rect.height), border_radius=8)
        surface.blit(highlight_surf, highlight_rect)
        
        pygame.draw.rect(surface, self._darken(color, 40), draw_rect, 2, border_radius=12)
        
        font = pygame.font.Font(None, 32)
        text_surface = font.render(self.text, True, UIColors.WHITE)
        text_rect = text_surface.get_rect(center=draw_rect.center)
        
        shadow_surface = font.render(self.text, True, (0, 0, 0, 100))
        surface.blit(shadow_surface, (text_rect.x + 1, text_rect.y + 1))
        surface.blit(text_surface, text_rect)
        
    def is_clicked(self, mouse_pos: tuple, mouse_pressed: bool) -> bool:
        return self.rect.collidepoint(mouse_pos) and mouse_pressed


class Slider:
    def __init__(self, x: int, y: int, width: int, height: int,
                 min_val: float, max_val: float, value: float,
                 color: tuple, label: str = ""):
        self.x = x - width // 2
        self.y = y
        self.width = width
        self.height = height
        self.min_val = min_val
        self.max_val = max_val
        self.value = value
        self.color = color
        self.label = label
        
        self.track_rect = pygame.Rect(self.x, y, width, height)
        self.dragging = False
        self.handle_radius = height + 4
        
    def _get_handle_x(self) -> int:
        ratio = (self.value - self.min_val) / (self.max_val - self.min_val)
        return int(self.x + ratio * self.width)
    
    def _get_handle_rect(self) -> pygame.Rect:
        handle_x = self._get_handle_x()
        return pygame.Rect(handle_x - self.handle_radius, 
                          self.y - self.handle_radius // 2,
                          self.handle_radius * 2, 
                          self.handle_radius * 2)
    
    def update(self, mouse_pos: tuple, mouse_pressed: bool):
        handle_rect = self._get_handle_rect()
        
        if mouse_pressed:
            if handle_rect.collidepoint(mouse_pos) or self.dragging:
                self.dragging = True
                rel_x = mouse_pos[0] - self.x
                ratio = max(0, min(1, rel_x / self.width))
                self.value = self.min_val + ratio * (self.max_val - self.min_val)
        else:
            self.dragging = False
            
    def draw(self, surface: pygame.Surface):
        if self.label:
            font = pygame.font.Font(None, 24)
            label_surf = font.render(self.label, True, UIColors.WHITE)
            surface.blit(label_surf, (self.x, self.y - 25))
            
            percent = int(self.value * 100)
            val_surf = font.render(f"{percent}%", True, UIColors.WHITE)
            surface.blit(val_surf, (self.x + self.width - val_surf.get_width(), self.y - 25))
        
        track_bg = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, UIColors.DARK_GRAY, track_bg, border_radius=self.height // 2)
        
        fill_width = int((self.value - self.min_val) / (self.max_val - self.min_val) * self.width)
        if fill_width > 0:
            fill_rect = pygame.Rect(self.x, self.y, fill_width, self.height)
            pygame.draw.rect(surface, self.color, fill_rect, border_radius=self.height // 2)
        
        handle_x = self._get_handle_x()
        handle_y = self.y + self.height // 2
        
        pygame.draw.circle(surface, UIColors.DARK_GRAY, (handle_x + 2, handle_y + 2), self.handle_radius)
        pygame.draw.circle(surface, UIColors.WHITE, (handle_x, handle_y), self.handle_radius)
        pygame.draw.circle(surface, self.color, (handle_x, handle_y), self.handle_radius - 3)
        
    def get_value(self) -> float:
        return self.value


class ThemeSelector:
    def __init__(self, x: int, y: int, themes: dict, current_theme: str):
        self.x = x
        self.y = y
        self.themes = themes
        self.current_theme = current_theme
        self.theme_names = list(themes.keys())
        self.hovered = None
        
        self.button_size = 60
        self.spacing = 15
        self.buttons = []
        
        self._create_buttons()
        
    def _create_buttons(self):
        total_width = len(self.theme_names) * (self.button_size + self.spacing) - self.spacing
        start_x = self.x - total_width // 2
        
        self.buttons = []
        for i, name in enumerate(self.theme_names):
            btn_x = start_x + i * (self.button_size + self.spacing)
            self.buttons.append({
                "name": name,
                "rect": pygame.Rect(btn_x, self.y, self.button_size, self.button_size),
                "colors": self.themes[name]
            })
            
    def update(self, mouse_pos: tuple):
        self.hovered = None
        for btn in self.buttons:
            if btn["rect"].collidepoint(mouse_pos):
                self.hovered = btn["name"]
                
    def draw(self, surface: pygame.Surface):
        font = pygame.font.Font(None, 28)
        title = font.render("Тема:", True, UIColors.WHITE)
        surface.blit(title, (self.x - title.get_width() // 2, self.y - 35))
        
        for btn in self.buttons:
            rect = btn["rect"]
            colors = btn["colors"]
            is_selected = btn["name"] == self.current_theme
            
            shadow = rect.copy()
            shadow.y += 3
            pygame.draw.rect(surface, UIColors.DARK_GRAY, shadow, border_radius=10)
            
            pygame.draw.rect(surface, tuple(colors["sky"]), rect, border_radius=10)
            
            ground_rect = pygame.Rect(rect.x, rect.y + rect.height - 15, rect.width, 15)
            pygame.draw.rect(surface, tuple(colors["ground"]), ground_rect)
            
            pipe_rect = pygame.Rect(rect.x + rect.width - 18, rect.y + 10, 12, 25)
            pygame.draw.rect(surface, tuple(colors["pipe"]), pipe_rect)
            
            bird_pos = (rect.x + 20, rect.y + 25)
            pygame.draw.circle(surface, tuple(colors["bird_body"]), bird_pos, 8)
            
            border_color = (255, 215, 0) if is_selected else UIColors.WHITE
            border_width = 3 if is_selected else 1
            pygame.draw.rect(surface, border_color, rect, border_width, border_radius=10)
            
            name_font = pygame.font.Font(None, 18)
            name_text = {"day": "День", "night": "Ночь", 
                        "sunset": "Закат", "retro": "Ретро"}.get(btn["name"], btn["name"])
            name_surf = name_font.render(name_text, True, UIColors.WHITE)
            name_x = rect.centerx - name_surf.get_width() // 2
            surface.blit(name_surf, (name_x, rect.bottom + 5))
            
    def handle_click(self, mouse_pos: tuple) -> str:
        for btn in self.buttons:
            if btn["rect"].collidepoint(mouse_pos):
                self.current_theme = btn["name"]
                return btn["name"]
        return None


class Panel:
    def __init__(self, x: int, y: int, width: int, height: int, 
                 color: tuple = (40, 40, 40), alpha: int = 230):
        self.rect = pygame.Rect(x - width // 2, y, width, height)
        self.color = color
        self.alpha = alpha
        
    def draw(self, surface: pygame.Surface):
        panel_surf = pygame.Surface((self.rect.width, self.rect.height), pygame.SRCALPHA)
        
        shadow_rect = pygame.Rect(4, 4, self.rect.width, self.rect.height)
        pygame.draw.rect(panel_surf, (0, 0, 0, 100), shadow_rect, border_radius=20)
        
        main_rect = pygame.Rect(0, 0, self.rect.width, self.rect.height)
        pygame.draw.rect(panel_surf, (*self.color, self.alpha), main_rect, border_radius=20)
        pygame.draw.rect(panel_surf, (255, 255, 255, 50), main_rect, 2, border_radius=20)
        
        surface.blit(panel_surf, self.rect)


class IconButton:
    def __init__(self, x: int, y: int, radius: int, icon: str, color: tuple):
        self.x = x
        self.y = y
        self.radius = radius
        self.icon = icon
        self.color = color
        self.is_hovered = False
        
    def update(self, mouse_pos: tuple):
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        self.is_hovered = (dx * dx + dy * dy) <= self.radius * self.radius
        
    def draw(self, surface: pygame.Surface):
        pygame.draw.circle(surface, (0, 0, 0, 100), (self.x + 2, self.y + 2), self.radius)
        
        color = tuple(min(255, c + 30) for c in self.color) if self.is_hovered else self.color
        pygame.draw.circle(surface, color, (self.x, self.y), self.radius)
        pygame.draw.circle(surface, (255, 255, 255), (self.x, self.y), self.radius, 2)
        
        font = pygame.font.Font(None, 28)
        icon_surf = font.render(self.icon, True, UIColors.WHITE)
        icon_rect = icon_surf.get_rect(center=(self.x, self.y))
        surface.blit(icon_surf, icon_rect)
        
    def is_clicked(self, mouse_pos: tuple, mouse_pressed: bool) -> bool:
        if not mouse_pressed:
            return False
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        return (dx * dx + dy * dy) <= self.radius * self.radius

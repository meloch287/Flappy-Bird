import pygame
import math
from .components import Button, Slider, ThemeSelector, Panel, UIColors


class Menu:
    def __init__(self, screen_width: int, screen_height: int, themes: dict, current_theme: str):
        self.width = screen_width
        self.height = screen_height
        self.themes = themes
        
        center_x = screen_width // 2
        
        self.play_button = Button(center_x, 270, 220, 55, "ИГРАТЬ", (76, 175, 80))
        self.settings_button = Button(center_x, 340, 220, 55, "НАСТРОЙКИ", (33, 150, 243))
        
        self.difficulty_buttons = {
            "easy": Button(center_x - 100, 450, 90, 40, "Легко", (76, 175, 80)),
            "medium": Button(center_x, 450, 90, 40, "Средне", (255, 152, 0)),
            "hard": Button(center_x + 100, 450, 90, 40, "Сложно", (244, 67, 54))
        }
        self.selected_difficulty = "medium"
        
        self.title_offset = 0
        self.time = 0
        
    def update(self, mouse_pos: tuple, dt: float = 0.016):
        self.time += dt
        self.title_offset = math.sin(self.time * 2) * 5
        
        self.play_button.update(mouse_pos, dt)
        self.settings_button.update(mouse_pos, dt)
        for button in self.difficulty_buttons.values():
            button.update(mouse_pos, dt)
            
    def draw(self, surface: pygame.Surface, high_score: int, colors: dict):
        title_font = pygame.font.Font(None, 64)
        
        shadow_text = title_font.render("FLAPPY BIRD", True, tuple(colors.get("text_shadow", (0,0,0))))
        shadow_rect = shadow_text.get_rect(centerx=self.width // 2 + 3, y=80 + self.title_offset + 3)
        surface.blit(shadow_text, shadow_rect)
        
        title_text = title_font.render("FLAPPY BIRD", True, tuple(colors.get("text", (255,255,255))))
        title_rect = title_text.get_rect(centerx=self.width // 2, y=80 + self.title_offset)
        surface.blit(title_text, title_rect)
        
        line_y = 140 + self.title_offset
        pygame.draw.line(surface, tuple(colors.get("ui_accent", (255,200,0))),
                        (self.width // 2 - 100, line_y), (self.width // 2 + 100, line_y), 3)
        
        self._draw_score_panel(surface, high_score)
        
        self.play_button.draw(surface)
        self.settings_button.draw(surface)
        
        diff_font = pygame.font.Font(None, 26)
        diff_text = diff_font.render("Сложность:", True, UIColors.WHITE)
        diff_rect = diff_text.get_rect(centerx=self.width // 2, y=400)
        surface.blit(diff_text, diff_rect)
        
        for name, button in self.difficulty_buttons.items():
            if name == self.selected_difficulty:
                highlight = button.rect.inflate(8, 8)
                pygame.draw.rect(surface, (255, 215, 0), highlight, 3, border_radius=14)
            button.draw(surface)
            
        self._draw_instructions(surface)
        
    def _draw_score_panel(self, surface: pygame.Surface, high_score: int):
        panel_rect = pygame.Rect(self.width // 2 - 80, 170, 160, 50)
        
        panel_surf = pygame.Surface((panel_rect.width, panel_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(panel_surf, (0, 0, 0, 150), (0, 0, panel_rect.width, panel_rect.height), border_radius=15)
        pygame.draw.rect(panel_surf, (255, 215, 0, 200), (0, 0, panel_rect.width, panel_rect.height), 2, border_radius=15)
        surface.blit(panel_surf, panel_rect)
        
        font = pygame.font.Font(None, 24)
        label = font.render("РЕКОРД", True, (255, 215, 0))
        label_rect = label.get_rect(centerx=panel_rect.centerx, y=panel_rect.y + 8)
        surface.blit(label, label_rect)
        
        score_font = pygame.font.Font(None, 32)
        score_text = score_font.render(str(high_score), True, UIColors.WHITE)
        score_rect = score_text.get_rect(centerx=panel_rect.centerx, y=panel_rect.y + 28)
        surface.blit(score_text, score_rect)
        
    def _draw_instructions(self, surface: pygame.Surface):
        inst_font = pygame.font.Font(None, 20)
        
        inst_rect = pygame.Rect(self.width // 2 - 150, 535, 300, 50)
        inst_surf = pygame.Surface((inst_rect.width, inst_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(inst_surf, (0, 0, 0, 100), (0, 0, inst_rect.width, inst_rect.height), border_radius=10)
        surface.blit(inst_surf, inst_rect)
        
        lines = ["ПРОБЕЛ или ЛКМ - прыжок", "ESC - пауза / меню"]
        
        for i, line in enumerate(lines):
            text = inst_font.render(line, True, (200, 200, 200))
            text_rect = text.get_rect(centerx=self.width // 2, y=545 + i * 18)
            surface.blit(text, text_rect)
            
    def handle_click(self, mouse_pos: tuple) -> tuple:
        if self.play_button.is_clicked(mouse_pos, True):
            return "play", self.selected_difficulty
            
        if self.settings_button.is_clicked(mouse_pos, True):
            return "settings", None
            
        for name, button in self.difficulty_buttons.items():
            if button.is_clicked(mouse_pos, True):
                self.selected_difficulty = name
                return "difficulty", name
                
        return None, None


class SettingsMenu:
    def __init__(self, screen_width: int, screen_height: int, 
                 themes: dict, current_theme: str, audio_config: dict):
        self.width = screen_width
        self.height = screen_height
        
        center_x = screen_width // 2
        
        self.panel = Panel(center_x, 60, 350, 480)
        
        self.master_slider = Slider(center_x, 160, 280, 12, 0, 1, 
                                    audio_config.get("master_volume", 0.7),
                                    (76, 175, 80), "Общая громкость")
        self.sfx_slider = Slider(center_x, 230, 280, 12, 0, 1,
                                 audio_config.get("sfx_volume", 0.8),
                                 (33, 150, 243), "Звуковые эффекты")
        self.music_slider = Slider(center_x, 300, 280, 12, 0, 1,
                                   audio_config.get("music_volume", 0.5),
                                   (156, 39, 176), "Музыка")
        
        self.theme_selector = ThemeSelector(center_x, 380, themes, current_theme)
        self.back_button = Button(center_x, 510, 200, 45, "НАЗАД", (100, 100, 100))
        
    def update(self, mouse_pos: tuple, mouse_pressed: bool, dt: float = 0.016):
        self.master_slider.update(mouse_pos, mouse_pressed)
        self.sfx_slider.update(mouse_pos, mouse_pressed)
        self.music_slider.update(mouse_pos, mouse_pressed)
        self.theme_selector.update(mouse_pos)
        self.back_button.update(mouse_pos, dt)
        
    def draw(self, surface: pygame.Surface):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))
        
        self.panel.draw(surface)
        
        title_font = pygame.font.Font(None, 42)
        title = title_font.render("НАСТРОЙКИ", True, UIColors.WHITE)
        title_rect = title.get_rect(centerx=self.width // 2, y=85)
        surface.blit(title, title_rect)
        
        pygame.draw.line(surface, (100, 100, 100),
                        (self.width // 2 - 140, 120), (self.width // 2 + 140, 120), 2)
        
        self.master_slider.draw(surface)
        self.sfx_slider.draw(surface)
        self.music_slider.draw(surface)
        
        pygame.draw.line(surface, (100, 100, 100),
                        (self.width // 2 - 140, 340), (self.width // 2 + 140, 340), 2)
        
        self.theme_selector.draw(surface)
        self.back_button.draw(surface)
        
    def handle_click(self, mouse_pos: tuple) -> tuple:
        if self.back_button.is_clicked(mouse_pos, True):
            return "back", None
            
        theme = self.theme_selector.handle_click(mouse_pos)
        if theme:
            return "theme", theme
            
        return None, None
    
    def get_audio_settings(self) -> dict:
        return {
            "master_volume": self.master_slider.get_value(),
            "sfx_volume": self.sfx_slider.get_value(),
            "music_volume": self.music_slider.get_value()
        }


class GameOverScreen:
    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height
        
        center_x = screen_width // 2
        
        self.panel = Panel(center_x, 120, 300, 380)
        self.restart_button = Button(center_x, 400, 200, 50, "ЗАНОВО", (76, 175, 80))
        self.menu_button = Button(center_x, 460, 200, 50, "В МЕНЮ", (33, 150, 243))
        
        self.show_time = 0
        
    def update(self, mouse_pos: tuple, dt: float = 0.016):
        self.show_time += dt
        self.restart_button.update(mouse_pos, dt)
        self.menu_button.update(mouse_pos, dt)
        
    def draw(self, surface: pygame.Surface, score: int, high_score: int, is_new_record: bool):
        alpha = min(180, int(self.show_time * 500))
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, alpha))
        surface.blit(overlay, (0, 0))
        
        self.panel.draw(surface)
        
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("ИГРА ОКОНЧЕНА", True, (255, 100, 100))
        title_rect = title.get_rect(centerx=self.width // 2, y=150)
        surface.blit(title, title_rect)
        
        self._draw_score_display(surface, score, high_score, is_new_record)
        
        self.restart_button.draw(surface)
        self.menu_button.draw(surface)
        
    def _draw_score_display(self, surface: pygame.Surface, score: int, 
                            high_score: int, is_new_record: bool):
        center_x = self.width // 2
        
        score_label_font = pygame.font.Font(None, 28)
        score_label = score_label_font.render("СЧЕТ", True, (180, 180, 180))
        surface.blit(score_label, (center_x - score_label.get_width() // 2, 210))
        
        score_font = pygame.font.Font(None, 64)
        score_text = score_font.render(str(score), True, UIColors.WHITE)
        surface.blit(score_text, (center_x - score_text.get_width() // 2, 235))
        
        high_label = score_label_font.render("ЛУЧШИЙ", True, (180, 180, 180))
        surface.blit(high_label, (center_x - high_label.get_width() // 2, 300))
        
        high_color = (255, 215, 0) if is_new_record else UIColors.WHITE
        high_font = pygame.font.Font(None, 48)
        high_text = high_font.render(str(high_score), True, high_color)
        surface.blit(high_text, (center_x - high_text.get_width() // 2, 325))
        
        if is_new_record:
            pulse = abs(math.sin(self.show_time * 5)) * 0.3 + 0.7
            new_font = pygame.font.Font(None, 32)
            new_text = new_font.render("* НОВЫЙ РЕКОРД! *", True, 
                                       (int(255 * pulse), int(215 * pulse), 0))
            new_rect = new_text.get_rect(centerx=center_x, y=370)
            surface.blit(new_text, new_rect)
        
    def handle_click(self, mouse_pos: tuple) -> str:
        if self.restart_button.is_clicked(mouse_pos, True):
            return "restart"
        if self.menu_button.is_clicked(mouse_pos, True):
            return "menu"
        return None
    
    def reset(self):
        self.show_time = 0


class PauseMenu:
    def __init__(self, screen_width: int, screen_height: int):
        self.width = screen_width
        self.height = screen_height
        
        center_x = screen_width // 2
        
        self.panel = Panel(center_x, 180, 280, 250)
        self.resume_button = Button(center_x, 280, 200, 50, "ПРОДОЛЖИТЬ", (76, 175, 80))
        self.menu_button = Button(center_x, 350, 200, 50, "В МЕНЮ", (244, 67, 54))
        
    def update(self, mouse_pos: tuple, dt: float = 0.016):
        self.resume_button.update(mouse_pos, dt)
        self.menu_button.update(mouse_pos, dt)
        
    def draw(self, surface: pygame.Surface):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))
        
        self.panel.draw(surface)
        
        title_font = pygame.font.Font(None, 48)
        title = title_font.render("ПАУЗА", True, UIColors.WHITE)
        title_rect = title.get_rect(centerx=self.width // 2, y=210)
        surface.blit(title, title_rect)
        
        self.resume_button.draw(surface)
        self.menu_button.draw(surface)
        
    def handle_click(self, mouse_pos: tuple) -> str:
        if self.resume_button.is_clicked(mouse_pos, True):
            return "resume"
        if self.menu_button.is_clicked(mouse_pos, True):
            return "menu"
        return None

import pygame
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from engine.game_engine import GameEngine, GameState
from engine.physics import CollisionManager
from engine.audio_manager import AudioManager
from objects.bird import Bird
from objects.pipe import PipeManager
from objects.ground import Ground
from ui.renderer import Renderer
from ui.menu import Menu, SettingsMenu, GameOverScreen, PauseMenu


class FlappyBirdGame:
    def __init__(self):
        self.engine = GameEngine()
        self.config = self.engine.config
        
        self.themes = self.config["themes"]
        self.current_theme = "day"
        self.colors = {k: tuple(v) if isinstance(v, list) else v 
                      for k, v in self.themes[self.current_theme].items()}
        
        self.audio = AudioManager(self.config.get("audio", {}))
        
        self.renderer = Renderer(self.engine.screen, self.colors)
        self.menu = Menu(self.engine.width, self.engine.height, 
                        self.themes, self.current_theme)
        self.settings_menu = SettingsMenu(self.engine.width, self.engine.height,
                                          self.themes, self.current_theme,
                                          self.config.get("audio", {}))
        self.game_over_screen = GameOverScreen(self.engine.width, self.engine.height)
        self.pause_menu = PauseMenu(self.engine.width, self.engine.height)
        
        ground_height = self.config["ground"]["height"]
        self.collision_manager = CollisionManager(self.engine.height, ground_height)
        
        self._init_game_objects()
        
        self.is_new_record = False
        self.in_settings = False
        
        # Countdown
        self.countdown_timer = 0
        self.countdown_value = 3
        
    def _init_game_objects(self):
        bird_config = self.config["bird"]
        start_y = self.engine.height // 2 - bird_config["height"] // 2
        
        self.bird = Bird(bird_config["x_position"], start_y, self.config, self.colors)
        
        self.pipe_manager = PipeManager(
            self.engine.width, self.engine.height,
            self.config["ground"]["height"], self.config, self.colors
        )
        
        self.ground = Ground(
            self.engine.width, self.engine.height, 
            self.config, self.colors
        )
        
    def _apply_theme(self, theme_name: str):
        if theme_name in self.themes:
            self.current_theme = theme_name
            self.colors = {k: tuple(v) if isinstance(v, list) else v 
                          for k, v in self.themes[theme_name].items()}
            
            self.renderer.set_theme(self.colors)
            self.bird.set_colors(self.colors)
            self.pipe_manager.set_colors(self.colors)
            self.ground.set_colors(self.colors)
            self.settings_menu.theme_selector.current_theme = theme_name
            
            self.audio.play("click")
        
    def _apply_difficulty(self):
        settings = self.engine.get_difficulty_settings()
        self.bird.gravity = settings["gravity"]
        self.pipe_manager.set_speed(settings["pipe_speed"])
        self.pipe_manager.set_gap(settings["pipe_gap"])
        self.ground.speed = settings["pipe_speed"]
        
    def _reset_game(self):
        bird_config = self.config["bird"]
        start_y = self.engine.height // 2 - bird_config["height"] // 2
        
        self.bird.reset(start_y)
        self.pipe_manager.reset()
        self.ground.reset()
        self.engine.reset_score()
        self.is_new_record = False
        self.game_over_screen.reset()
        self._apply_difficulty()
        
    def _start_countdown(self):
        self._reset_game()
        self.countdown_value = 3
        self.countdown_timer = 0
        self.engine.set_state(GameState.COUNTDOWN)
        
    def _handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
                
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self._handle_escape()
                    
                if event.key == pygame.K_p and self.engine.state == GameState.PLAYING:
                    self.engine.set_state(GameState.PAUSED)
                    
                if event.key == pygame.K_SPACE:
                    self._handle_jump()
                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    self._handle_click(event.pos)
                    
        if pygame.mouse.get_pressed()[0] and self.in_settings:
            mouse_pos = pygame.mouse.get_pos()
            self.settings_menu.update(mouse_pos, True)
            self._apply_audio_settings()
                    
        return True
    
    def _handle_escape(self):
        if self.in_settings:
            self.in_settings = False
            self.audio.play("click")
        elif self.engine.state == GameState.PLAYING:
            self.engine.set_state(GameState.PAUSED)
        elif self.engine.state == GameState.PAUSED:
            self.engine.set_state(GameState.PLAYING)
        elif self.engine.state == GameState.GAME_OVER:
            self.engine.set_state(GameState.MENU)
    
    def _handle_jump(self):
        if self.engine.state == GameState.PLAYING:
            self.bird.jump()
            self.audio.play("jump")
        elif self.engine.state == GameState.MENU and not self.in_settings:
            self._start_countdown()
            
    def _handle_click(self, pos: tuple):
        if self.in_settings:
            action, value = self.settings_menu.handle_click(pos)
            if action == "back":
                self.in_settings = False
                self.audio.play("click")
            elif action == "theme":
                self._apply_theme(value)
            return
            
        if self.engine.state == GameState.MENU:
            action, value = self.menu.handle_click(pos)
            if action == "play":
                self._start_countdown()
                self.audio.play("click")
            elif action == "settings":
                self.in_settings = True
                self.audio.play("click")
            elif action == "difficulty":
                self.engine.difficulty = value
                self.audio.play("click")
                
        elif self.engine.state == GameState.PLAYING:
            self.bird.jump()
            self.audio.play("jump")
            
        elif self.engine.state == GameState.PAUSED:
            action = self.pause_menu.handle_click(pos)
            if action == "resume":
                self.engine.set_state(GameState.PLAYING)
                self.audio.play("click")
            elif action == "menu":
                self.engine.set_state(GameState.MENU)
                self._reset_game()
                self.audio.play("click")
            
        elif self.engine.state == GameState.GAME_OVER:
            action = self.game_over_screen.handle_click(pos)
            if action == "restart":
                self.engine.set_state(GameState.PLAYING)
                self._reset_game()
                self.audio.play("click")
            elif action == "menu":
                self.engine.set_state(GameState.MENU)
                self.audio.play("click")
                
    def _apply_audio_settings(self):
        settings = self.settings_menu.get_audio_settings()
        self.audio.set_master_volume(settings["master_volume"])
        self.audio.set_sfx_volume(settings["sfx_volume"])
        self.audio.set_music_volume(settings["music_volume"])
                
    def _update(self, dt: float):
        mouse_pos = pygame.mouse.get_pos()
        
        if self.in_settings:
            self.settings_menu.update(mouse_pos, False, dt)
            return
        
        if self.engine.state == GameState.COUNTDOWN:
            self.countdown_timer += dt
            if self.countdown_timer >= 1.0:
                self.countdown_timer = 0
                self.countdown_value -= 1
                if self.countdown_value <= 0:
                    self.engine.set_state(GameState.PLAYING)
            self.ground.update(dt)
            return
        
        if self.engine.state == GameState.MENU:
            self.menu.update(mouse_pos, dt)
            self.ground.update(dt)
            
        elif self.engine.state == GameState.PLAYING:
            self.bird.update(dt)
            self.pipe_manager.update(dt)
            self.ground.update(dt)
            self.renderer.update_particles(dt)
            
            if self._check_collisions():
                self._game_over()
                
            self._check_score()
            
        elif self.engine.state == GameState.PAUSED:
            self.pause_menu.update(mouse_pos, dt)
            
        elif self.engine.state == GameState.GAME_OVER:
            self.game_over_screen.update(mouse_pos, dt)
            
    def _check_collisions(self) -> bool:
        bird_rect = self.bird.get_rect()
        
        if self.collision_manager.check_bird_pipe_collision(bird_rect, 
                                                            self.pipe_manager.pipes):
            return True
            
        if self.collision_manager.check_bird_bounds(bird_rect):
            return True
            
        return False
    
    def _check_score(self):
        for pipe in self.pipe_manager.pipes:
            if self.collision_manager.check_pipe_passed(self.bird.x, pipe):
                pipe.passed = True
                self.engine.add_score()
                self.audio.play("score")
                
                for _ in range(5):
                    self.renderer.add_particle(
                        pipe.x + pipe.width // 2,
                        pipe.gap_y + pipe.gap // 2,
                        self.colors.get("ui_accent", (255, 215, 0))
                    )
                
    def _game_over(self):
        self.audio.play("hit")
        if self.engine.score > self.engine.high_score:
            self.is_new_record = True
        self.engine.save_high_score()
        self.engine.set_state(GameState.GAME_OVER)
        
    def _render(self):
        self.renderer.draw_background()
        
        if self.engine.state == GameState.MENU:
            self.ground.draw(self.engine.screen)
            self.menu.draw(self.engine.screen, self.engine.high_score, self.colors)
            
            if self.in_settings:
                self.settings_menu.draw(self.engine.screen)
            
        elif self.engine.state == GameState.COUNTDOWN:
            self.ground.draw(self.engine.screen)
            self.bird.draw(self.engine.screen)
            self._draw_countdown()
            
        elif self.engine.state == GameState.PLAYING:
            self.pipe_manager.draw(self.engine.screen)
            self.ground.draw(self.engine.screen)
            self.bird.draw(self.engine.screen)
            self.renderer.draw_particles()
            self.renderer.draw_score(self.engine.score)
            
        elif self.engine.state == GameState.PAUSED:
            self.pipe_manager.draw(self.engine.screen)
            self.ground.draw(self.engine.screen)
            self.bird.draw(self.engine.screen)
            self.renderer.draw_score(self.engine.score)
            self.pause_menu.draw(self.engine.screen)
            
        elif self.engine.state == GameState.GAME_OVER:
            self.pipe_manager.draw(self.engine.screen)
            self.ground.draw(self.engine.screen)
            self.bird.draw(self.engine.screen)
            self.game_over_screen.draw(self.engine.screen, self.engine.score,
                                       self.engine.high_score, self.is_new_record)
            
        pygame.display.flip()
    
    def _draw_countdown(self):
        font = pygame.font.Font(None, 150)
        text = str(self.countdown_value) if self.countdown_value > 0 else "GO!"
        
        # Тень
        shadow = font.render(text, True, (0, 0, 0))
        shadow_rect = shadow.get_rect(center=(self.engine.width // 2 + 3, 
                                               self.engine.height // 2 + 3))
        self.engine.screen.blit(shadow, shadow_rect)
        
        # Текст
        color = (255, 255, 255)
        rendered = font.render(text, True, color)
        rect = rendered.get_rect(center=(self.engine.width // 2, 
                                          self.engine.height // 2))
        self.engine.screen.blit(rendered, rect)
        
    def run(self):
        while self.engine.running:
            dt = self.engine.tick()
            
            if not self._handle_events():
                break
                
            self._update(dt)
            self._render()
            
        self.engine.quit()


def main():
    game = FlappyBirdGame()
    game.run()


if __name__ == "__main__":
    main()

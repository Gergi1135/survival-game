import pygame
from ui.buttons import Button

class SettingsScene:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.clock = game.clock
        self.font = pygame.font.SysFont(None, 64)
        self.small = pygame.font.SysFont(None, 32)
        self.buttons = []
        self._build_ui()

    def _build_ui(self):
        screen_w, screen_h = self.screen.get_size()
        btn_w, btn_h = 320, 64
        cx = (screen_w - btn_w)//2
        start_y = screen_h//2 - 100
        self.buttons = [
            Button('Toggle Fullscreen', (cx, start_y), (btn_w, btn_h), self._toggle_fullscreen),
            Button('Back', (cx, start_y + 100), (btn_w, btn_h), self._back)
        ]

    def _toggle_fullscreen(self):
        self.game.toggle_fullscreen()
        self._build_ui()

    def _back(self):
        self.game.switch_scene('menu')

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)

    def update(self):
        pass

    def draw(self):
        self.screen.fill((20,20,20))
        title = self.font.render('Settings', True, (230,230,230))
        self.screen.blit(title, ((self.screen.get_width()-title.get_width())//2, 120))
        for b in self.buttons:
            b.draw(self.screen)

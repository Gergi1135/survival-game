import pygame
import sys
from scenes.menu import MenuScene
from scenes.base import BaseScene
from scenes.raid import RaidScene
from scenes.saves import SavesScene
from scenes.settings import SettingsScene

class Game:
    def __init__(self):
        pygame.init()
        self.fullscreen = True
        self._apply_display_mode()
        pygame.display.set_caption("The Last Base")
        pygame.event.set_grab(True)
        self.clock = pygame.time.Clock()
        self.current_scene = MenuScene(self)
    def _apply_display_mode(self):
        if self.fullscreen:
            self.screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        else:
            self.screen = pygame.display.set_mode((1280, 720))
    def toggle_fullscreen(self):
        self.fullscreen = not self.fullscreen
        self._apply_display_mode()
        pygame.event.set_grab(True)
        if hasattr(self.current_scene, 'on_resize'):
            self.current_scene.on_resize()
    def switch_scene(self, scene_name):
        if scene_name == "menu":
            self.current_scene = MenuScene(self)
        elif scene_name == "base":
            self.current_scene = BaseScene(self)
        elif scene_name == "raid":
            self.current_scene = RaidScene(self)
        elif scene_name == "saves":
            self.current_scene = SavesScene(self)
        elif scene_name == "settings":
            self.current_scene = SettingsScene(self)
    def run(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit(); sys.exit()
                self.current_scene.handle_event(event)
            self.current_scene.update()
            self.current_scene.draw()
            pygame.display.flip()
            self.clock.tick(60)

if __name__ == "__main__":
    Game().run()

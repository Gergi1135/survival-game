import pygame
from systems import save_load
from ui.buttons import Button

class SavesScene:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.clock = game.clock
        self.font = pygame.font.SysFont(None, 48)
        self.small = pygame.font.SysFont(None, 28)
        self.buttons = []
        self._refresh()

    def _refresh(self):
        self.buttons = []
        slots = save_load.list_slots()
        screen_w, screen_h = self.screen.get_size()
        start_y = screen_h//2 - 140
        for idx, s in enumerate(slots, start=1):
            y = start_y + (idx-1)*80
            name = s['name'] if s['name'] else 'Empty'
            txt = f"Slot {s['index']}: {name}"
            def make_cb(i=s['index']):
                return lambda: self._start_slot(i)
            self.buttons.append(Button(txt, (screen_w//2 - 220, y), (300, 50), make_cb()))
            def make_del_cb(i=s['index']):
                return lambda: self._delete_slot(i)
            self.buttons.append(Button('Delete', (screen_w//2 + 100, y), (120, 50), make_del_cb()))
        self.buttons.append(Button('Back', (screen_w//2 - 160, start_y + 3*80 + 40), (200, 50), self._back))

    def _start_slot(self, slot_index):
        ok = save_load.set_active_slot(slot_index)
        if not ok:
            self.game.switch_scene('menu')
            self.game.current_scene.start_new_game(slot_index_preselect=slot_index)
        else:
            self.game.switch_scene('base')

    def _delete_slot(self, slot_index):
        save_load.delete_slot(slot_index)
        self._refresh()

    def _back(self):
        self.game.switch_scene('menu')

    def handle_event(self, event):
        for b in self.buttons:
            b.handle_event(event)

    def update(self):
        pass

    def draw(self):
        self.screen.fill((18, 22, 18))
        title = self.font.render('Saves', True, (230,230,230))
        self.screen.blit(title, ((self.screen.get_width()-title.get_width())//2, 100))
        hint = self.small.render('Click slot to load or Delete to remove.', True, (180,180,180))
        self.screen.blit(hint, ((self.screen.get_width()-hint.get_width())//2, 150))
        for b in self.buttons:
            b.draw(self.screen)

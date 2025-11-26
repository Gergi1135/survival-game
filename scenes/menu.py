import pygame
import os
from ui.buttons import Button
from ui.textbox import TextBox
from systems import save_load

class MenuScene:
    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.clock = game.clock
        self.font = pygame.font.SysFont(None, 72)
        self.small = pygame.font.SysFont(None, 32)
        self.bg = self._load_bg()
        self.buttons = []
        self._build_main_buttons()
        self.newgame_open = False
        self.slot_buttons = []
        self.name_box = TextBox((0, 0, 300, 50), placeholder='Save name...', maxlen=24)
        self.create_btn = Button('Create', (0, 0), (160, 50), self._confirm_newgame)
        self.cancel_btn = Button('Cancel', (0, 0), (160, 50), self._close_newgame)
        self.newgame_selected_slot = None
        self.message = None
        self.overwrite_confirm = False

    def on_resize(self):
        # re-scale background and rebuild layout
        self.bg = self._load_bg()
        self._build_main_buttons()
        if self.newgame_open:
            self._build_slot_buttons()

    def _load_bg(self):
        root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        assets = os.path.join(root, 'assets')
        path_user = os.path.join(assets, 'menu_bg.png')
        path_ph = os.path.join(assets, 'menu_bg_placeholder.png')
        img_path = path_user if os.path.exists(path_user) else path_ph
        try:
            img = pygame.image.load(img_path).convert()
            img = pygame.transform.smoothscale(img, self.screen.get_size())
            return img
        except Exception:
            surf = pygame.Surface(self.screen.get_size())
            surf.fill((20,25,20))
            return surf

    def _build_main_buttons(self):
        screen_w, screen_h = self.screen.get_size()
        btn_w, btn_h = 320, 64
        start_y = screen_h//2 - 160
        cx = (screen_w - btn_w)//2
        spacing = 80
        self.buttons = [
            Button('Continue', (cx, start_y), (btn_w, btn_h), self._continue),
            Button('New Game', (cx, start_y + spacing), (btn_w, btn_h), self._open_newgame),
            Button('Saves', (cx, start_y + spacing*2), (btn_w, btn_h), self._open_saves),
            Button('Settings', (cx, start_y + spacing*3), (btn_w, btn_h), self._settings),
            Button('Quit', (cx, start_y + spacing*4), (btn_w, btn_h), self._exit),
        ]

    def _open_saves(self):
        self.game.switch_scene('saves')

    def _continue(self):
        active = save_load.get_active_slot()
        if active is None:
            slots = save_load.list_slots()
            if any(s['exists'] for s in slots):
                self._open_saves()
            else:
                self._open_newgame()
        else:
            self.game.switch_scene('base')

    def _open_newgame(self):
        self.newgame_open = True
        self.message = None
        self.overwrite_confirm = False
        self._build_slot_buttons()
        self.name_box.text = ''
        self.newgame_selected_slot = None

    def start_new_game(self, slot_index_preselect=None):
        self._open_newgame()
        self.newgame_selected_slot = slot_index_preselect

    def _close_newgame(self):
        self.newgame_open = False
        self.overwrite_confirm = False

    def _build_slot_buttons(self):
        self.slot_buttons = []
        slots = save_load.list_slots()
        screen_w, screen_h = self.screen.get_size()
        panel_w, panel_h = 600, 420
        panel_x = (screen_w - panel_w)//2
        panel_y = (screen_h - panel_h)//2
        start_y = panel_y + 80
        for idx, s in enumerate(slots, start=1):
            y = start_y + (idx-1)*slot_spacing
            name = s['name'] if s['name'] else 'Empty'
            txt = f"Slot {s['index']} [{name}]"
            def make_cb(i=s['index']):
                return lambda: self._select_slot(i)
            self.slot_buttons.append(Button(txt, (panel_x+20, y), (panel_w-40, 50), make_cb()))
        # Name + buttons placement
        self.name_box.rect.topleft = (panel_x+20, panel_y+panel_h-120)
        self.name_box.rect.size = (panel_w-40, 50)
        self.create_btn.rect.topleft = (panel_x+20, panel_y+panel_h-60)
        self.cancel_btn.rect.topleft = (panel_x+220, panel_y+panel_h-60)
        self._panel_geo = (panel_x, panel_y, panel_w, panel_h)

    def _select_slot(self, slot_index):
        self.newgame_selected_slot = slot_index

    def _confirm_newgame(self):
        if not self.newgame_selected_slot:
            self.message = 'Válassz slotot!'
            return
        name = self.name_box.text.strip() or f'Slot {self.newgame_selected_slot}'
        ok = save_load.new_game(self.newgame_selected_slot, name)
        if not ok:
            self.overwrite_confirm = True
            self.message = 'Slot foglalt. Overwrite?'
            return
        self.newgame_open = False
        self.game.switch_scene('base')

    def _overwrite_yes(self):
        name = self.name_box.text.strip() or f'Slot {self.newgame_selected_slot}'
        save_load.new_game(self.newgame_selected_slot, name, overwrite=True)
        self.overwrite_confirm = False
        self.newgame_open = False
        self.game.switch_scene('base')

    def _overwrite_no(self):
        self.overwrite_confirm = False
        self.message = None

    def _settings(self):
        self.game.switch_scene('settings')

    def _exit(self):
        pygame.event.post(pygame.event.Event(pygame.QUIT))

    def handle_event(self, event):
        if self.newgame_open:
            for b in self.slot_buttons:
                b.handle_event(event)
            self.create_btn.handle_event(event)
            self.cancel_btn.handle_event(event)
            self.name_box.handle_event(event)
            if self.overwrite_confirm and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mx, my = event.pos
                yes_rect = pygame.Rect(self._panel_geo[0]+self._panel_geo[2]-220, self._panel_geo[1]+20, 90, 40)
                no_rect = pygame.Rect(self._panel_geo[0]+self._panel_geo[2]-120, self._panel_geo[1]+20, 90, 40)
                if yes_rect.collidepoint(mx, my):
                    self._overwrite_yes()
                elif no_rect.collidepoint(mx, my):
                    self._overwrite_no()
            return
        for b in self.buttons:
            b.handle_event(event)

    def update(self):
        if self.newgame_open:
            dt = self.clock.get_time()
            self.name_box.update(dt)

    def draw(self):
        self.screen.blit(self.bg, (0,0))
        screen_w, screen_h = self.screen.get_size()
        title = self.font.render('The Last Base', True, (230,230,230))
        self.screen.blit(title, ((screen_w - title.get_width())//2, 100))
        if self.newgame_open:
            panel_x, panel_y, panel_w, panel_h = self._panel_geo
            pygame.draw.rect(self.screen, (25,25,25), (panel_x, panel_y, panel_w, panel_h), border_radius=12)
            pygame.draw.rect(self.screen, (80,80,80), (panel_x, panel_y, panel_w, panel_h), 2, border_radius=12)
            cap = self.small.render('NEW GAME — válassz slotot és adj nevet', True, (200,200,200))
            self.screen.blit(cap, (panel_x+20, panel_y+20))
            for b in self.slot_buttons:
                b.draw(self.screen)
            self.name_box.draw(self.screen)
            self.create_btn.draw(self.screen)
            self.cancel_btn.draw(self.screen)
            if self.newgame_selected_slot:
                sel = self.small.render(f'Selected: Slot {self.newgame_selected_slot}', True, (220,220,220))
                self.screen.blit(sel, (panel_x+20, panel_y+panel_h-160))
            if self.message:
                self.screen.blit(self.small.render(self.message, True, (255,80,80)), (panel_x+20, panel_y+panel_h-70))
            if self.overwrite_confirm:
                yes_rect = pygame.Rect(panel_x+panel_w-220, panel_y+20, 90, 40)
                no_rect = pygame.Rect(panel_x+panel_w-120, panel_y+20, 90, 40)
                pygame.draw.rect(self.screen, (80,160,80), yes_rect)
                pygame.draw.rect(self.screen, (160,80,80), no_rect)
                self.screen.blit(self.small.render('YES', True, (255,255,255)), (yes_rect.x+20, yes_rect.y+8))
                self.screen.blit(self.small.render('NO', True, (255,255,255)), (no_rect.x+28, no_rect.y+8))
        else:
            for b in self.buttons:
                b.draw(self.screen)

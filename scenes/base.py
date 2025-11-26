import pygame
import random
import math
from systems import save_load

class NPC:
    def __init__(self, name, role, pos):
        self.name = name
        self.role = role
        self.pos = pos
        self.color = (200, 200, 50)
        self.rect = pygame.Rect(pos[0], pos[1], 30, 30)
    def move_idle(self):
        if random.random() < 0.02:
            self.pos[0] += random.choice([-1, 0, 1])
            self.pos[1] += random.choice([-1, 0, 1])
            self.rect.topleft = (self.pos[0], self.pos[1])

class BaseScene:
    MAX_SLOTS = 18
    MAX_STACK = 100

    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.clock = game.clock
        data = save_load.load_save()
        self.player_pos = list(data['base']['player_pos'])
        self.player_speed = 4
        self.attacking = False
        self.attack_timer = 0
        self.attack_applied = False
        self.attack_cooldown = 250
        self.last_attack_time = 0
        self.inventory_open = False
        self.inventory = self.load_inventory_stacks()
        self.font = pygame.font.SysFont(None, 24)
        self.crafts = [
            ("Workbench", {"Wood":5, "Metal":2}),
            ("Wall", {"Wood":10}),
            ("Door", {"Wood":8, "Metal":4}),
            ("FarmPlot", {"Wood":6, "Stone":4}),
        ]
        self.craft_buttons = []
        self.create_craft_buttons()
        self.hover_item_index = None
        self.drag_index = None
        self.drag_origin = None
        self.npcs = [NPC("Alex", "Builder", [200, 200]), NPC("Mia", "Medic", [300, 250])]
        self.hover_npc = None
        self.dialog_open = False
        self.dialog_npc = None
        self.dialog_text = []
        self.dialog_index = 0
        self.pause_menu_open = False
        self.item_icons = {
            "Wood": self.make_icon((139,69,19)),
            "Stone": self.make_icon((128,128,128)),
            "Metal": self.make_icon((192,192,192)),
            "Food": self.make_icon((34,139,34)),
            "Workbench": self.make_icon((160,100,50)),
            "Wall": self.make_icon((120,120,120)),
            "Door": self.make_icon((100,80,60)),
            "FarmPlot": self.make_icon((80,150,100)),
        }
        self.background = self.make_background()
        self.message = None
        self.split_open = False
        self.split_index = None
        self.split_value = 1
        self.split_max = 1
        self.split_bar = pygame.Rect(120, 420, 220, 12)
        self.split_handle_x = self.split_bar.x
        self.split_confirm = pygame.Rect(360, 410, 100, 32)
        self.split_cancel = pygame.Rect(360, 450, 100, 32)
        self.trash_rect = pygame.Rect(470, 370, 80, 80)
        self.targets = [{"rect": pygame.Rect(520, 260, 30, 30), "hp": 3, "type":"dummy"}]
        self.build_mode = False
        self.build_catalog = ["Wall", "Door", "Workbench", "FarmPlot"]
        self.build_selected = 0
        self.build_ghost_color = (180, 180, 180)
        self.placed_structures = []
        self._load_structures_from_save()
        self.farm_timers = {}

    def on_resize(self):
        self.background = self.make_background()

    def _load_structures_from_save(self):
        data = save_load.load_save()
        self.placed_structures = []
        for s in data['base']['placed_structures']:
            r = s['rect']
            rect = pygame.Rect(r['x'], r['y'], r.get('w', 40), r.get('h', 40))
            self.placed_structures.append({"type": s['type'], "rect": rect})

    def _persist_base(self):
        save_load.save_base_state(player_pos=self.player_pos, placed_structures=self.placed_structures)

    def load_inventory_stacks(self):
        items = save_load.load_save().get("inventory", [])
        stacks = []
        counts = {}
        for it in items:
            counts[it] = counts.get(it, 0) + 1
        for it, qty in counts.items():
            while qty > 0:
                take = min(qty, self.MAX_STACK)
                stacks.append({"item": it, "qty": take})
                qty -= take
        return stacks

    def save_inventory(self):
        flat = []
        for st in self.inventory:
            flat.extend([st["item"]] * st["qty"])
        save_load.save_inventory(flat)

    def add_item(self, item, amount=1):
        for st in self.inventory:
            if st["item"] == item and st["qty"] < self.MAX_STACK:
                can_add = min(amount, self.MAX_STACK - st["qty"])
                st["qty"] += can_add
                amount -= can_add
                if amount == 0:
                    self.save_inventory()
                    return True
        while amount > 0:
            if len(self.inventory) >= self.MAX_SLOTS:
                self.message = "not enough space"
                self.save_inventory()
                return False
            take = min(amount, self.MAX_STACK)
            self.inventory.append({"item": item, "qty": take})
            amount -= take
        self.save_inventory()
        return True

    def remove_items(self, item, qty):
        for st in self.inventory:
            if st["item"] == item and qty > 0:
                take = min(st["qty"], qty)
                st["qty"] -= take
                qty -= take
        self.inventory = [st for st in self.inventory if st["qty"] > 0]
        self.save_inventory()

    def count_item(self, item):
        return sum(st["qty"] for st in self.inventory if st["item"] == item)

    def make_icon(self, color):
        surf = pygame.Surface((32, 32), pygame.SRCALPHA)
        pygame.draw.rect(surf, color, (0,0,32,32), border_radius=6)
        pygame.draw.rect(surf, (0,0,0,60), (0,0,32,32), 2, border_radius=6)
        return surf

    def make_background(self):
        w, h = self.screen.get_size()
        bg = pygame.Surface((w, h))
        bg.fill((45, 55, 45))
        for x in range(0, w, 40):
            pygame.draw.line(bg, (50, 65, 50), (x,0), (x,h))
        for y in range(0, h, 40):
            pygame.draw.line(bg, (50, 65, 50), (0,y), (w,y))
        return bg

    def create_craft_buttons(self):
        self.craft_buttons = []
        y_offset = 90
        for name, req in self.crafts:
            rect = pygame.Rect(570, y_offset, 200, 40)
            self.craft_buttons.append((rect, name, req))
            y_offset += 60

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            # debounce toggles: ignore repeat
            is_repeat = getattr(event, 'repeat', False)
            if event.key == pygame.K_m and not self.pause_menu_open and not self.split_open:
                self._persist_base(); self.save_inventory(); self.game.switch_scene("raid")
            if event.key == pygame.K_TAB and not is_repeat:
                self.inventory_open = not self.inventory_open
            if event.key == pygame.K_ESCAPE and not is_repeat:
                self.pause_menu_open = not self.pause_menu_open
            if event.key == pygame.K_SPACE and self.dialog_open and not is_repeat:
                self.dialog_index += 1
                if self.dialog_index >= len(self.dialog_text): self.dialog_open = False
            if event.key == pygame.K_f and not self.pause_menu_open and not is_repeat:
                self.build_mode = not self.build_mode
            if event.key == pygame.K_q and self.build_mode and not is_repeat:
                self.build_selected = (self.build_selected - 1) % len(self.build_catalog)
            if event.key == pygame.K_e and self.build_mode and not is_repeat:
                self.build_selected = (self.build_selected + 1) % len(self.build_catalog)
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.pause_menu_open:
                return
            if event.button == 1 and not self.inventory_open and not self.dialog_open and not self.build_mode:
                if self.hover_npc is None:
                    now = pygame.time.get_ticks()
                    if now - self.last_attack_time >= self.attack_cooldown:
                        self.attacking = True; self.attack_timer = 120; self.attack_applied = False; self.last_attack_time = now
            if event.button == 1 and self.hover_npc and not self.dialog_open and not self.inventory_open:
                self.dialog_open = True; self.dialog_npc = self.hover_npc
                self.dialog_text = [f"Szia, {self.dialog_npc.name} vagyok.", "Erősítsük meg a bázist.", "Később folytatjuk."]
                self.dialog_index = 0
            if self.inventory_open:
                if event.button == 1 and not self.split_open:
                    slot = self.get_slot_under_mouse()
                    if slot is not None and slot < len(self.inventory):
                        self.drag_index = slot; self.drag_origin = slot
                if event.button == 3 and not self.split_open:
                    slot = self.get_slot_under_mouse()
                    if slot is not None and slot < len(self.inventory):
                        st = self.inventory[slot]
                        if st["qty"] > 1: self.open_split(slot)
                if event.button == 1:
                    mx, my = event.pos
                    for rect, name, req in self.craft_buttons:
                        if rect.collidepoint(mx, my):
                            if self.can_craft(req): self.craft_item(name, req)
                            else: self.message = "not enough materials"
            if event.button == 1 and self.build_mode and not self.inventory_open and not self.dialog_open:
                self.try_place_structure()
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                if self.drag_index is not None and not self.split_open:
                    if self.trash_rect.collidepoint(event.pos):
                        del self.inventory[self.drag_index]; self.save_inventory()
                    else:
                        target_slot = self.get_slot_under_mouse()
                        if target_slot is not None: self.move_stack(self.drag_origin, target_slot)
                    self.drag_index = None; self.drag_origin = None

    def move_stack(self, origin, target):
        if origin == target: return
        if origin < len(self.inventory) and target < self.MAX_SLOTS:
            if target >= len(self.inventory):
                st = self.inventory.pop(origin); self.inventory.append(st)
            else:
                self.inventory[origin], self.inventory[target] = self.inventory[target], self.inventory[origin]
            self.save_inventory()

    def open_split(self, slot_index):
        st = self.inventory[slot_index]
        self.split_open = True; self.split_index = slot_index
        self.split_max = st["qty"]; self.split_value = min(1, self.split_max - 1) or 1
        self.split_handle_x = self.split_bar.x
    def close_split(self):
        self.split_open = False; self.split_index = None
    def confirm_split(self):
        if self.split_index is None: return
        st = self.inventory[self.split_index]
        amount = self.split_value
        if amount <= 0 or amount >= st["qty"]: self.close_split(); return
        if len(self.inventory) >= self.MAX_SLOTS: self.message = "not enough space"; self.close_split(); return
        st["qty"] -= amount
        self.inventory.insert(self.split_index + 1, {"item": st["item"], "qty": amount})
        self.save_inventory(); self.close_split()

    def can_craft(self, requirements):
        for item, qty in requirements.items():
            if self.count_item(item) < qty: return False
        return True

    def craft_item(self, name, requirements):
        for item, qty in requirements.items(): self.remove_items(item, qty)
        self.add_item(name, 1); self.message = f"Crafted {name}"

    def consume_materials(self, requirements):
        for item, qty in requirements.items(): self.remove_items(item, qty)

    def get_build_cost(self, build_type):
        for name, req in self.crafts:
            if name == build_type: return req
        return {}

    def try_place_structure(self):
        build_type = self.build_catalog[self.build_selected]
        cost = self.get_build_cost(build_type)
        if not self.can_craft(cost): self.message = "not enough materials"; return
        mx, my = pygame.mouse.get_pos()
        gx = (mx // 40) * 40; gy = (my // 40) * 40
        rect = pygame.Rect(gx, gy, 40, 40)
        for s in self.placed_structures:
            if rect.colliderect(s['rect']): self.message = "occupied"; return
        for npc in self.npcs:
            if rect.colliderect(npc.rect): self.message = "occupied"; return
        self.consume_materials(cost)
        self.placed_structures.append({"type": build_type, "rect": rect})
        self.message = f"Placed {build_type}"; self._persist_base()

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_a]: self.player_pos[0] -= self.player_speed
        if keys[pygame.K_d]: self.player_pos[0] += self.player_speed
        if keys[pygame.K_w]: self.player_pos[1] -= self.player_speed
        if keys[pygame.K_s]: self.player_pos[1] += self.player_speed
        for npc in self.npcs: npc.move_idle()
        if self.attacking:
            dt = self.clock.get_time(); self.attack_timer -= dt
            if self.attack_timer <= 0: self.attacking = False; self.attack_timer = 0; self.attack_applied = False
        if self.attacking and not self.attack_applied:
            self.apply_attack_cone(); self.attack_applied = True
        mouse_pos = pygame.mouse.get_pos(); self.hover_npc = None
        for npc in self.npcs:
            npc.rect.topleft = (npc.pos[0], npc.pos[1])
            if npc.rect.collidepoint(mouse_pos): self.hover_npc = npc
        for idx, s in enumerate(self.placed_structures):
            if s['type'] == 'FarmPlot':
                t = self.farm_timers.get(idx, 0) + self.clock.get_time()
                if t >= 10000:
                    produced = self.add_item('Food', 1)
                    if produced: self.message = "Farm produced Food"
                    t = 0
                self.farm_timers[idx] = t

    def apply_attack_cone(self):
        origin = pygame.Vector2(self.player_pos[0]+20, self.player_pos[1]+20)
        mx,my = pygame.mouse.get_pos()
        dir_vec = pygame.Vector2(mx-origin.x, my-origin.y)
        angle = math.degrees(math.atan2(dir_vec.y, dir_vec.x))
        spread = 80; range_px = 60
        for t in self.targets:
            center = pygame.Vector2(t["rect"].center)
            to_target = center - origin; dist = to_target.length()
            if dist <= range_px:
                ang = math.degrees(math.atan2(to_target.y, to_target.x))
                if abs((ang - angle + 180) % 360 - 180) <= spread/2: t["hp"] -= 1
        self.targets = [t for t in self.targets if t["hp"] > 0]

    def get_slot_under_mouse(self):
        mouse_pos = pygame.mouse.get_pos()
        slot_width, slot_height = 60, 60; start_x, start_y = 60, 90
        for i in range(self.MAX_SLOTS):
            row = i // 6; col = i % 6
            x = start_x + col * slot_width; y = start_y + row * slot_height
            rect = pygame.Rect(x, y, slot_width-5, slot_height-5)
            if rect.collidepoint(mouse_pos): return i
        return None

    def draw_inventory(self):
        # inventory panel
        inv_rect = pygame.Rect(50, 50, 500, 400)
        pygame.draw.rect(self.screen, (60, 60, 60), inv_rect)
        slot_width, slot_height = 60, 60; start_x, start_y = 60, 90
        for i in range(self.MAX_SLOTS):
            row = i // 6; col = i % 6
            x = start_x + col * slot_width; y = start_y + row * slot_height
            rect = pygame.Rect(x, y, slot_width-5, slot_height-5)
            pygame.draw.rect(self.screen, (100, 100, 100), rect)
            if i < len(self.inventory):
                st = self.inventory[i]; icon = self.item_icons.get(st["item"]) 
                if icon: self.screen.blit(icon, (x+14, y+14))
                qty_text = self.font.render(f"{st['qty']}x", True, (255,255,255))
                self.screen.blit(qty_text, (x+30, y+40))
        pygame.draw.rect(self.screen, (150, 0, 0), self.trash_rect)
        self.screen.blit(self.font.render("Trash", True, (255,255,255)), (self.trash_rect.x+5, self.trash_rect.y+30))
        # craft panel
        craft_rect = pygame.Rect(560, 50, 220, 260)
        pygame.draw.rect(self.screen, (80, 80, 80), craft_rect)
        for rect, name, req in self.craft_buttons:
            pygame.draw.rect(self.screen, (120,120,120), rect)
            self.screen.blit(self.font.render(name, True, (255,255,255)), (rect.x+5, rect.y+5))
            req_txt = ', '.join([f"{k} x{v}" for k,v in req.items()])
            self.screen.blit(self.font.render(req_txt, True, (200,200,200)), (rect.x+5, rect.y+20))
        if self.message: self.screen.blit(self.font.render(self.message, True, (255,0,0)), (300, 60))

    def draw_dialog(self):
        pygame.draw.rect(self.screen, (50, 50, 50), (150, 380, 500, 180))
        if self.dialog_text:
            self.screen.blit(self.font.render(self.dialog_text[self.dialog_index], True, (255, 255, 255)), (170, 400))
        self.screen.blit(self.font.render("SPACE folytatás", True, (200,200,200)), (500, 530))

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        rect = pygame.Rect(self.player_pos[0], self.player_pos[1], 40, 40)
        pygame.draw.rect(self.screen, (0, 0, 255), rect)
        for npc in self.npcs: pygame.draw.rect(self.screen, npc.color, npc.rect)
        if self.hover_npc:
            mx,my = pygame.mouse.get_pos()
            self.screen.blit(self.font.render(f"{self.hover_npc.name} - {self.hover_npc.role}", True, (255,255,255)), (mx+10, my))
        for s in self.placed_structures:
            color = (120,120,120) if s['type']=="Wall" else (100,80,60) if s['type']=="Door" else (160,100,50) if s['type']=="Workbench" else (80,150,100)
            pygame.draw.rect(self.screen, color, s['rect'])
        if self.inventory_open: self.draw_inventory()
        if self.dialog_open: self.draw_dialog()

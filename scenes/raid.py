import pygame, random, math
from systems import save_load

class RaidScene:
    MAX_SLOTS = 18
    MAX_STACK = 100

    def __init__(self, game):
        self.horde_level = 0
        self.game = game
        self.screen = game.screen
        self.clock = game.clock
        self.font = pygame.font.SysFont(None, 24)
        self.player_pos = [400, 300]
        self.player_speed = 4
        self.attacking = False
        self.attack_timer = 0
        self.attack_applied = False
        self.attack_cooldown = 250
        self.last_attack_time = 0
        self.loot_items = []
        self.spawn_loot()
        self.enemies = []
        self.spawn_enemies()
        raid_data = save_load.load_save()['raid']
        self.noise = raid_data.get('noise', 0)
        self.noise_threshold = 100
        self.horde_level = 0
        self.weather = raid_data.get('weather', 'clear')
        self.weather_timer = 0
        self.weather_cycle_ms = 20000
        self.message = None
        self.pause_menu_open = False

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

    def add_item(self, item, amount=1):
        stacks = self.load_inventory_stacks()
        for st in stacks:
            if st["item"] == item and st["qty"] < self.MAX_STACK and amount>0:
                can_add = min(amount, self.MAX_STACK - st["qty"])
                st["qty"] += can_add
                amount -= can_add
        while amount>0:
            if len(stacks) >= self.MAX_SLOTS:
                self.message = "not enough space"; break
            take = min(amount, self.MAX_STACK)
            stacks.append({"item": item, "qty": take})
            amount -= take
        flat = []
        for st in stacks:
            flat.extend([st["item"]]*st["qty"])
        save_load.save_inventory(flat)
        return amount==0

    def spawn_loot(self):
        items = ["Wood", "Stone", "Metal", "Food"]
        self.loot_items.clear()
        for _ in range(6):
            x = random.randint(100, 700)
            y = random.randint(100, 500)
            item = random.choice(items)
            self.loot_items.append({"pos": [x, y], "item": item})

    def spawn_enemies(self):
        self.enemies.clear()
        base_count = 4 + self.horde_level * 2
        for _ in range(base_count):
            x = random.randint(100, 700)
            y = random.randint(100, 500)
            self.enemies.append({"rect": pygame.Rect(x, y, 30, 30), "hp": 2})

    def apply_attack_cone(self):
        origin = pygame.Vector2(self.player_pos[0]+20, self.player_pos[1]+20)
        mx,my = pygame.mouse.get_pos()
        dir_vec = pygame.Vector2(mx-origin.x, my-origin.y)
        angle = math.degrees(math.atan2(dir_vec.y, dir_vec.x))
        spread = 80
        range_px = 60
        for e in self.enemies:
            center = pygame.Vector2(e["rect"].center)
            to_target = center - origin
            dist = to_target.length()
            if dist <= range_px:
                ang = math.degrees(math.atan2(to_target.y, to_target.x))
                if abs((ang - angle + 180) % 360 - 180) <= spread/2:
                    e["hp"] -= 1
        self.enemies = [e for e in self.enemies if e["hp"]>0]

    def _update_weather(self, dt):
        self.weather_timer += dt
        if self.weather_timer >= self.weather_cycle_ms:
            self.weather_timer = 0
            import random
            self.weather = random.choice(['clear','rain','fog'])
        if self.weather == 'rain': self.player_speed = 3
        elif self.weather == 'fog': self.player_speed = 4
        else: self.player_speed = 4
        save_load.save_raid_state(weather=self.weather)

    def _add_noise(self, amount):
        self.noise = max(0, min(200, self.noise + amount))
        if self.noise >= self.noise_threshold:
            self.horde_level = min(5, self.horde_level + 1)
            self.spawn_enemies()
            self.noise = int(self.noise_threshold * 0.7)
        save_load.save_raid_state(noise=self.noise)

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_b: self.game.switch_scene("base")
            if event.key == pygame.K_ESCAPE: self.pause_menu_open = not self.pause_menu_open
            if event.key == pygame.K_e:
                for loot in list(self.loot_items):
                    if abs(self.player_pos[0]-loot["pos"][0])<50 and abs(self.player_pos[1]-loot["pos"][1])<50:
                        if self.add_item(loot['item'], 1): self.loot_items.remove(loot); self._add_noise(1)
                        else: self.message = "not enough space"
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.pause_menu_open: return
            if event.button == 1:
                now = pygame.time.get_ticks()
                if now - self.last_attack_time >= self.attack_cooldown:
                    self.attacking = True; self.attack_timer = 120; self.attack_applied = False; self.last_attack_time = now; self._add_noise(8)

    def update(self):
        if not self.pause_menu_open:
            keys = pygame.key.get_pressed(); moved = False
            if keys[pygame.K_a]: self.player_pos[0] -= self.player_speed; moved = True
            if keys[pygame.K_d]: self.player_pos[0] += self.player_speed; moved = True
            if keys[pygame.K_w]: self.player_pos[1] -= self.player_speed; moved = True
            if keys[pygame.K_s]: self.player_pos[1] += self.player_speed; moved = True
            if moved: self._add_noise(0.1)
        if self.attacking:
            dt = self.clock.get_time(); self.attack_timer -= dt
            if self.attack_timer <= 0: self.attacking = False; self.attack_timer = 0; self.attack_applied = False
        if self.attacking and not self.attack_applied:
            self.apply_attack_cone(); self.attack_applied = True
        self._update_weather(self.clock.get_time())

    def draw(self):
        if self.weather == 'clear': self.screen.fill((200, 100, 50))
        elif self.weather == 'rain': self.screen.fill((120, 120, 150))
        else: self.screen.fill((150, 150, 150))
        rect = pygame.Rect(self.player_pos[0], self.player_pos[1], 40, 40)
        pygame.draw.rect(self.screen, (0, 0, 255), rect)
        if self.attacking:
            origin = (self.player_pos[0]+20, self.player_pos[1]+20)
            mx,my = pygame.mouse.get_pos()
            angle_rad = math.atan2(my-origin[1], mx-origin[0])
            spread = math.radians(80); range_px = 60
            p1 = (origin[0] + math.cos(angle_rad-spread/2)*range_px, origin[1] + math.sin(angle_rad-spread/2)*range_px)
            p2 = (origin[0] + math.cos(angle_rad+spread/2)*range_px, origin[1] + math.sin(angle_rad+spread/2)*range_px)
            pygame.draw.polygon(self.screen, (255,0,0), [origin, p1, p2], 1)
        for e in self.enemies:
            pygame.draw.rect(self.screen, (50,200,50), e["rect"])
            self.screen.blit(self.font.render(f"HP:{e['hp']}", True, (255,255,255)), (e['rect'].x, e['rect'].y-18))
        for loot in self.loot_items:
            pygame.draw.rect(self.screen, (150, 0, 0), (*loot["pos"], 30, 30))
            self.screen.blit(self.font.render(loot["item"], True, (255,255,255)), (loot["pos"][0], loot["pos"][1]-20))
        pygame.draw.rect(self.screen, (30,30,30), (740, 40, 20, 200))
        h = int(min(1.0, self.noise / self.noise_threshold) * 200)
        pygame.draw.rect(self.screen, (200,40,40), (740, 240-h, 20, h))
        self.screen.blit(self.font.render("NOISE", True, (255,255,255)), (710, 20))
        self.screen.blit(self.font.render(f"{int(self.noise)}/{self.noise_threshold}", True, (255,255,255)), (690, 250))
        self.screen.blit(self.font.render(f"Weather: {self.weather}", True, (255,255,255)), (20, 20))
        if self.message: self.screen.blit(self.font.render(self.message, True, (255,0,0)), (320, 40))

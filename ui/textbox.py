import pygame

class TextBox:
    def __init__(self, rect, placeholder="", maxlen=20):
        self.rect = pygame.Rect(rect)
        self.font = pygame.font.SysFont(None, 28)
        self.text = ""
        self.placeholder = placeholder
        self.focus = False
        self.maxlen = maxlen
        self.cursor_visible = True
        self.cursor_timer = 0

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.focus = self.rect.collidepoint(event.pos)
        if self.focus and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pygame.K_RETURN:
                pass
            else:
                ch = event.unicode
                if ch and len(self.text) < self.maxlen and ch.isprintable():
                    self.text += ch

    def update(self, dt):
        self.cursor_timer += dt
        if self.cursor_timer > 500:
            self.cursor_timer = 0
            self.cursor_visible = not self.cursor_visible

    def draw(self, surface):
        pygame.draw.rect(surface, (60,60,60), self.rect, border_radius=8)
        pygame.draw.rect(surface, (30,30,30), self.rect, 2, border_radius=8)
        txt = self.text if self.text else self.placeholder
        color = (255,255,255) if self.text else (180,180,180)
        label = self.font.render(txt, True, color)
        surface.blit(label, (self.rect.x + 8, self.rect.y + (self.rect.height - label.get_height())//2))
        if self.focus and self.cursor_visible:
            cx = self.rect.x + 8 + label.get_width()
            cy = self.rect.y + 8
            pygame.draw.line(surface, (255,255,255), (cx, cy), (cx, cy + self.rect.height - 16), 2)

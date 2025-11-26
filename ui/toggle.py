import pygame

class Toggle:
    def __init__(self, label, pos, state=False, callback=None):
        self.label = label
        self.pos = pos
        self.state = state
        self.callback = callback
        self.font = pygame.font.SysFont(None, 28)
        self.rect = pygame.Rect(pos[0], pos[1], 180, 40)

    def draw(self, surface):
        pygame.draw.rect(surface, (60,60,60), self.rect, border_radius=10)
        knob_x = self.rect.x + (self.rect.width - 40 if self.state else 0)
        pygame.draw.rect(surface, (120,120,120), (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 2, border_radius=10)
        pygame.draw.rect(surface, (200,200,200), (knob_x, self.rect.y, 40, 40), border_radius=10)
        surface.blit(self.font.render(self.label, True, (255,255,255)), (self.rect.right + 12, self.rect.y + 8))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.state = not self.state
                if self.callback:
                    self.callback(self.state)

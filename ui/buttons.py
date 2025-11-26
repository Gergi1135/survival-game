import pygame

class Button:
    def __init__(self, text, pos, size, callback):
        self.text = text
        self.pos = pos
        self.size = size
        self.callback = callback
        self.font = pygame.font.SysFont(None, 36)
        self.rect = pygame.Rect(pos[0], pos[1], size[0], size[1])
        self.hover = False

    def draw(self, surface):
        color = (90, 90, 90) if not self.hover else (120, 120, 120)
        pygame.draw.rect(surface, color, self.rect, border_radius=10)
        pygame.draw.rect(surface, (30, 30, 30), self.rect, 2, border_radius=10)
        label = self.font.render(self.text, True, (255, 255, 255))
        surface.blit(label, (self.rect.x + 14, self.rect.y + (self.rect.height - label.get_height())//2))

    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            self.hover = self.rect.collidepoint(event.pos)
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                self.callback()

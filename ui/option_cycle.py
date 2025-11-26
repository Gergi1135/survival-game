import pygame

class OptionCycle:
    def __init__(self, label, pos, options, index=0, callback=None):
        self.label = label
        self.pos = pos
        self.options = options
        self.index = index
        self.callback = callback
        self.font = pygame.font.SysFont(None, 28)
        self.left_rect = pygame.Rect(pos[0], pos[1], 40, 40)
        self.right_rect = pygame.Rect(pos[0]+240, pos[1], 40, 40)
        self.value_rect = pygame.Rect(pos[0]+50, pos[1], 190, 40)

    def _text(self):
        return str(self.options[self.index])

    def draw(self, surface):
        pygame.draw.rect(surface, (80,80,80), self.left_rect, border_radius=8)
        pygame.draw.rect(surface, (80,80,80), self.right_rect, border_radius=8)
        surface.blit(self.font.render('<', True, (255,255,255)), (self.left_rect.x+12, self.left_rect.y+10))
        surface.blit(self.font.render('>', True, (255,255,255)), (self.right_rect.x+12, self.right_rect.y+10))
        pygame.draw.rect(surface, (60,60,60), self.value_rect, border_radius=8)
        pygame.draw.rect(surface, (30,30,30), self.value_rect, 2, border_radius=8)
        surface.blit(self.font.render(f'{self.label}: {self._text()}', True, (255,255,255)), (self.value_rect.x+8, self.value_rect.y+8))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.left_rect.collidepoint(event.pos):
                self.index = (self.index - 1) % len(self.options)
                if self.callback:
                    self.callback(self.options[self.index])
            elif self.right_rect.collidepoint(event.pos):
                self.index = (self.index + 1) % len(self.options)
                if self.callback:
                    self.callback(self.options[self.index])

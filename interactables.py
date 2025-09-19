import pygame

class Interactable:
    def __init__(self, rect=None, on_hover=None, on_click=None, is_active=True, hotkey=None, context=None):
        self.on_hover = on_hover
        self.on_click = on_click
        self.is_active = is_active
        self.rect = rect
        self.hotkey = hotkey
        self.context = context

        self.debounce = False
    
    def render(self, screen):
        pass

class Button(Interactable):
    def __init__(self, on_hover, on_click, is_active, rect, hotkey, text, font_size, font_color):
        super().__init__(on_hover, on_click, is_active, rect, hotkey)
        self.text = text
        self.font_size = font_size
        self.font_color = font_color

    def render(self, screen):
        if self.is_active:
            font = pygame.font.SysFont('monogram', self.font_size)
            display_text = font.render(self.text, False, self.font_color)
            screen.blit(display_text, self.rect)

def pause_game(game):
    if game.paused:
        game.paused = False
    else:
        game.paused = True
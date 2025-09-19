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
    # TO-DO: Flesh out button class with automatic text wrapping, center alignment, padding, background colors, etc.
    # Look at HTML / CSS buttons for inspiration
    def __init__(self, text, font_size, font_color, **kwargs):
        super().__init__(**kwargs)
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
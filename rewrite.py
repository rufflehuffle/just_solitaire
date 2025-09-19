import pygame
from abc import ABC, abstractmethod

class SolitaireGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 360))
        self.clock = pygame.time.Clock()
        self.cards = [Card('K', 'S')]

        self._setup_game()

    def _setup_game(self):
        pass

    def _draw_starting_piles(self):
        pass

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
            self._update()
            self._render()
            self.clock.tick(60)
        pygame.quit()

    def _render(self):
        self.screen.fill((81, 108, 58))
        for card in self.cards:
            card.graphic.render(self.screen)
        pygame.display.flip()
    
    def _update(self):
        for card in self.cards:
            card.update()

class GraphicComponent(ABC):
    @abstractmethod
    def render(self):
        pass

class InputComponent(ABC):
    # Handles click events and hotkey presses with debounce
    # TO-DO: Add hover enter and exit events instead of just on_hover
    def __init__(self, collision_rect=None, is_active=True, hotkey=None):
        self.is_active = is_active
        self.collision_rect = collision_rect
        self.hotkey = hotkey
        self.debounce = False
    
    @abstractmethod
    def on_hover(self):
        pass

    @abstractmethod
    def on_click(self):
        pass

    @property
    def is_hovering(self):
        return self.collision_rect.collidepoint(pygame.mouse.get_pos()) if self.collision_rect else False
    
    @property
    def is_clicked(self):
        return self.is_hovering and self._mb1_down()
    
    def update(self):
        if self.is_hovering:
            self.on_hover()

        # Check for debounce
        if not self.debounce:
            if (self.is_hovering and self._mb1_down()) or self._hotkey_down():
                self.on_click()
                self.debounce = True
        if not(self._mb1_down() or self._hotkey_down()):
            self.debounce = False

    def _mb1_down(self):
        return pygame.mouse.get_pressed()[0]
    
    def _hotkey_down(self):
        return pygame.key.get_pressed()[self.hotkey] if self.hotkey else False

class CardGraphicComponent(GraphicComponent):
    def __init__(self):
        self.rect = pygame.Rect(100, 100, 100, 100)

    def render(self, screen):
        pygame.draw.rect(screen, 'white', self.rect)

class CardInputComponent(InputComponent):
    # TO-DO: further decouple this
    def __init__(self, card, **kwargs):
        super().__init__(**kwargs)
        self.card = card

    def update(self):
        super().update()

    def on_click(self):
        print(self.card.value)

    def on_hover(self):
        pass

class Card():
    def __init__(self, value, suit):
        self.suit = suit
        self.value = value

        self.graphic = CardGraphicComponent()
        self.input = CardInputComponent(self, collision_rect=self.graphic.rect)

    def update(self):
        self.input.update()

if __name__ == "__main__":
    game = SolitaireGame()
    game.run()
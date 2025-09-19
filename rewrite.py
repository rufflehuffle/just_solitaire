import pygame
from abc import ABC, abstractmethod

class SolitaireGame:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((640, 360))
        self.clock = pygame.time.Clock()

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
            self._render()
            self.clock.tick(60)
        pygame.quit()

    def _render(self):
        self.screen.fill((81, 108, 58))
        pygame.display.flip()

class GraphicComponent(ABC):
    @abstractmethod
    def render(self):
        pass

class InputComponent(ABC):
    # Handles click events and hotkey presses with debounce
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
        # Check for debounce
        if not(self._mb1_down() or self._hotkey_down()):
            self.debounce = False
        if not self.debounce:
            if (self.is_hovering and self._mb1_down()) or self._hotkey_down():
                return self.on_click()

    def _mb1_down(self):
        return pygame.mouse_get_pressed()[0]
    
    def _hotkey_down(self):
        return pygame.key.get_pressed()[self.hotkey] if self.hotkey else False
        
class CardInputComponent(InputComponent):
    pass

class LogicComponent():
    pass

class GameObject():
    pass

# if __name__ == "__main__":
#     game = SolitaireGame()
#     game.run()

# card = Card('K', 'S')
# print(card.is_draggable)
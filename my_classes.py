import pygame
import random
from interactables import *
from enum import Enum
from dataclasses import dataclass, field
from typing import List

card_back = pygame.image.load("sprites/card-back.png")

@dataclass
class Player:
    lives: int = 3
    total_score: int = 0
    gold: int = 0
    items: List = field(default_factory=lambda: [])

class GameState(Enum):
    in_round = 1
    paused = 2
    round_over = 3
    round_win = 4
    in_shop = 5
    game_over = 6

class Game:
    def __init__(self):
        self.deck = Deck(context=self)
        self.piles = self.deck.draw_starting_piles()
        self.waste = Waste()
        self.foundations = [Foundation(suit=suit) for suit in ['H', 'D', 'C', 'S']]
        self.player = Player()
        self.game_state = GameState.in_round
        self.game_previous_state = None

    def reset(self):
        self.deck = Deck(context=self)
        self.piles = self.deck.draw_starting_piles()
        self.waste = Waste()
        self.foundations = [Foundation(suit=suit) for suit in ['H', 'D', 'C', 'S']]

    @property
    def score(self):
        pile_score_multiplier = 1
        foundation_score_multipler = 3
        return (self.num_cards_revealed - 7) * pile_score_multiplier + self.num_cards_in_foundation * foundation_score_multipler
    
    @property
    def num_cards_revealed(self):
        num_cards_revealed = 0
        for pile in self.piles:
            num_cards_revealed += sum([card.is_face_up for card in pile.cards])
        return num_cards_revealed
    
    @property
    def num_cards_in_foundation(self):
        return sum([len(foundation.cards) for foundation in self.foundations])
    
    @property
    def visible_cards(self):
        visible_cards = []
        for pile in self.piles:
            visible_cards.extend(pile.cards)
        visible_cards.extend(self.waste.cards)
        for foundation in self.foundations:
            visible_cards.extend(foundation.cards)
        return visible_cards

    def render_game_end(self, screen, pop_up_text):
        shadow_surf = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 128))
        screen.blit(shadow_surf, (0, 0))

        # Render game-end pop-up
        bg_rect = pygame.Rect(0, 0, 400, 300)
        bg_rect.center = (screen.get_width() / 2, screen.get_height() / 2)
        pygame.draw.rect(screen, (51, 45, 82), bg_rect)

        font = pygame.font.SysFont('monogram', 32)
        # Figure out how to deal with text wrapping / dynamic positioning
        text = font.render(pop_up_text, False, 'white')
        screen.blit(text, (355, 240))
        
        reset_text = font.render("Reset", False, 'black')
        reset_rect = pygame.Rect(0, 0, 100, 50)
        reset_rect.center = bg_rect.center
        pygame.draw.rect(screen, 'white', reset_rect)
        screen.blit(reset_text, (370, 285))

        score_text = font.render(f"Score: {self.score}", False, 'white')
        screen.blit(score_text, (345, 330))

        return reset_rect

class Card(Interactable):
    dimensions = (36, 54)

    def __init__(self, value, suit, location=None, **kwargs):
        super().__init__(**kwargs)
        
        self.value = value
        self.suit = suit
        self.int_value = self.card_value_to_int(value)

        self.rect = None
        self.is_face_up = True
        self.is_draggable = True
        self.location = location
        self.image = pygame.image.load(f"sprites/{self.value}{self.suit}.png")

        self.color = "red" if suit in ['H', 'D'] else "black"
    
    def render(self, screen):
        if self.is_face_up:
            screen.blit(self.image, (self.rect.x, self.rect.y))
        else:
            screen.blit(card_back, self.rect)

    def card_value_to_int(self, value):
        if value == 'A':
            return 1
        elif value == 'J':
            return 11
        elif value == 'Q':
            return 12
        elif value == 'K':
            return 13
        else:
            return int(value)
    
    @property
    def location_index(self): # Is this function actually necessary? Why not just call location.cards.index(card)...
        if self.location:
            return self.location.cards.index(self)
        return -1
    
    @property
    def collision_rect(self):
        if isinstance(self.location, Pile) and self.location.cards[-1] != self:
            return pygame.Rect(self.rect.x, self.rect.y, Card.dimensions[0], 30)
        else:
            return pygame.Rect(self.rect.x, self.rect.y, *Card.dimensions)

class Deck(Interactable):
    def __init__(self, **kwargs):
        super().__init__(on_click=self.on_click, **kwargs)
        self.cards = []
        self.rect = pygame.Rect(400, 50, *Card.dimensions)
        self.image = pygame.image.load("sprites/card-back.png")
        self.empty_image = pygame.image.load("sprites/card-placeholder.png")
        self.loops = 0
        self.max_loops = 1
        self.hotkey = pygame.K_SPACE
        suits = ['H', 'D', 'C', 'S']
        values = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']

        for suit in suits:
            for value in values:
                self.cards.append(Card(value, suit, location='deck'))
        random.shuffle(self.cards)

    def on_click(self, game):
        if self.cards:
            card_drawn = self.draw_card()
            game.waste.append(card_drawn)
        else:
            game.waste.loop(self)
            if self.loops == self.max_loops:
                game.player.lives -= 1
                game.player.total_score += game.score
                if game.player.lives == 0:
                    game.game_state = GameState.game_over
                else:
                    game.game_state = GameState.round_over

    def draw_card(self):
        if self.cards:
            return self.cards.pop()
        return None
    
    def draw_starting_piles(self):
        piles = []

        for i in range(7):
            pile_cards = [self.draw_card() for _ in range(i + 1)]
            pile = Pile(pile_cards, slot=i)
            piles.append(pile)
            for card in pile_cards:
                card.location = pile

        return piles

    def render(self, screen):
        if self.cards:
            screen.blit(self.image, self.rect)
        else:
            screen.blit(self.empty_image, self.rect)
        font = pygame.font.SysFont('monogram', 16)
        text = font.render(f'Loops: {self.loops}/{self.max_loops}', False, 'white')
        screen.blit(text, (self.rect.bottomleft[0] - 10, self.rect.bottomleft[1]))

class Pile:
    def __init__(self, cards=None, slot=None):
        self.cards = list(cards) if cards is not None else []
        self.slot = slot
        self.x = 50 + slot * 50
        self.y = 150
        self.card_offset = 30
        self.empty_image = pygame.image.load("sprites/card-placeholder.png")
        for card in self.cards[:-1]:
            card.is_face_up = False
            card.is_draggable = False
        if self.cards:
            self.cards[-1].is_face_up = True
            self.cards[-1].is_draggable = True
        for card in self.cards:
            card.rect = pygame.Rect(self.x, self.y + self.cards.index(card) * self.card_offset, *Card.dimensions)
            card.spot = self.slot
        self.collision_rect = pygame.Rect(self.x, self.y, *Card.dimensions)

    def flip(self):
        if self.cards:
            top_card = self.cards[-1]
            top_card.is_face_up = True
            top_card.is_draggable = True
            return top_card
        return None
    
    def render(self, screen):
        if self.cards:
            for card in self.cards:
                card.render(screen)
        else:  
            rect = pygame.Rect(self.x, self.y, *Card.dimensions)
            screen.blit(self.empty_image, rect)
    
    def validate_card_placement(self, card):
        if not self.cards:
            return card.value == 'K'  # Only Kings can be placed on empty piles
        top_card = self.cards[-1]
        if not top_card.is_face_up:
            return False
        # Check for alternating colors and descending order
        if card.color != top_card.color and card.int_value == top_card.int_value - 1:
            return True
        return False
    
    @property
    def collision_rect(self):
        if self.cards:
            top_card = self.cards[-1]
            return top_card.rect
        else:
            return pygame.Rect(self.x, self.y, *Card.dimensions)
        
    @collision_rect.setter
    def collision_rect(self, value):
        self._collision_rect = value
        
    def append(self, card):
        self.cards.append(card)
        card.rect = pygame.Rect(self.x, self.y + (len(self.cards) - 1) * self.card_offset, *Card.dimensions)
        return card
    
    def pop(self):
        if self.cards:
            card = self.cards.pop()
            return card
        return None

class Foundation:
    def __init__(self, suit=None, cards=None):
        self.cards = list(cards) if cards is not None else []
        self.suit = suit
        foundation_offset = 50
        self.x = 50 + ['H', 'D', 'C', 'S'].index(suit) * foundation_offset
        self.y = 50
        self.image = pygame.image.load(f"sprites/F{self.suit}.png")
        self.collision_rect = pygame.Rect(self.x, self.y, *Card.dimensions)

    def render(self, screen):
        rect = pygame.Rect(self.x, self.y, *Card.dimensions)
        if self.cards:
            top_card = self.cards[-1]
            top_card.rect = rect
            top_card.render(screen)
        else:
            screen.blit(self.image, rect)

    
    def validate_card_placement(self, card):
        if card.suit != self.suit:
            return False
        if not self.cards:
            return card.value == 'A'  # Only Aces can be placed on empty foundations
        top_card = self.cards[-1]
        if card.int_value == top_card.int_value + 1:
            return True
        return False
    
    def append(self, card):
        self.cards.append(card)
        card.location = self
        for cards in self.cards[:-1]:
            cards.is_draggable = False
        return card
    
    def pop(self):
        if self.cards:
            if len(self.cards) >= 2:
                self.cards[-2].is_draggable = True
            return self.cards.pop()
        return None

class Waste:
    def __init__(self, cards=None):
        self.cards = list(cards) if cards is not None else []
        self.x = 400
        self.y = 150

    def append(self, card):
        self.cards.append(card)
        card.location = self
        if self.cards:
            self.cards[-1].is_draggable = True
            for card in self.cards[:-1]:
                card.is_draggable = False
        return card

    def loop(self, deck):
        for card in self.cards:
            card.location = deck
        deck.cards.extend(reversed(self.cards))
        deck.loops += 1
        self.cards.clear()
    
    def render(self, screen, n=3):
        card_offset = 30
        if self.cards:
            for i, card in enumerate(self.cards[-n:]):
                card.rect = pygame.Rect(self.x, self.y + i * card_offset, *Card.dimensions)
                card.render(screen)

    def pop(self):
        if self.cards:
            if len(self.cards) >= 2:
                self.cards[-2].is_draggable = True
            return self.cards.pop()
        return None
    
class Shop:
    def __init__(self):
        self.items=[]

    def render(self, screen, player):
        screen.fill('darkgreen')
        for item in self.items:
            if item:
                item.render(screen)
        
        # Render next round button
        font = pygame.font.SysFont('monogram', 32)
        next_round_text = font.render('Next>', False, 'black')
        next_round_rect = pygame.Rect(screen.get_width() - 110, screen.get_height() - 60, 80, 50)
        
        pygame.draw.rect(screen, 'white', next_round_rect)
        screen.blit(next_round_text, (screen.get_width() - 100, screen.get_height() - 50))

        gold_text = font.render(f'Gold: {player.gold}', False, 'white')
        screen.blit(gold_text, (50, 50))

        return next_round_rect

    def refresh(self):
        pass

class Item(Interactable):
    def __init__(self, cost, name, image_filename, location=None):
        super().__init__()
        self.cost = cost
        self.name = name
        self.location = location
        self.image = pygame.image.load("sprites/" + image_filename + ".png")  
        self.rect = self.image.get_rect()
        self.on_click = self.buy
    
    @property
    def slot(self):
        return self.location.items.index(self)

    def render(self, screen):
        slot_offset = 100
        if isinstance(self.location, Shop):
            self.rect.center = (100 + slot_offset * self.slot, 100)

            font = pygame.font.SysFont('monogram', 16)
            text = font.render(f"{self.cost}g", None, 'white')
            text_rect = text.get_rect()
            text_rect.center = self.rect.midbottom
            text_rect.y += text_rect.h

            screen.blit(text, text_rect)
        else:
            self.rect.center = (100 + slot_offset * self.slot, 500)
        
        screen.blit(self.image, self.rect)            

        

    def buy(self, player):
        if self.cost <= player.gold:
            player.items.append(self)
            player.gold -= self.cost
            self.location = player
        else:
            pass
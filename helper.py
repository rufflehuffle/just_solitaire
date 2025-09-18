import pygame
from my_classes import *

def get_all_cards_on_screen(piles, waste, foundations):
    cards_on_screen = []
    for pile in piles:
        cards_on_screen.extend(pile.cards)
    cards_on_screen.extend(waste.cards)
    for foundation in foundations:
        cards_on_screen.extend(foundation.cards)
    return cards_on_screen

def calculate_score(piles, foundations):
    # Calculate score based on:
    #   - # of cards face up in piles > 7
    #   - # of cards in foundations
    n_face_up_in_piles = 0
    pile_score_multiplier = 1
    foundation_score_multipler = 3

    for pile in piles:
        n_face_up_in_piles += sum([card.is_face_up for card in pile.cards])

    n_cards_in_foundations = sum([len(foundation.cards) for foundation in foundations])

    score = (n_face_up_in_piles - 7) * pile_score_multiplier + n_cards_in_foundations * foundation_score_multipler
    return score

def render_game_end(screen, pop_up_text, piles, foundations):
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

    score_text = font.render(f"Score: {calculate_score(piles, foundations)}", False, 'white')
    screen.blit(score_text, (345, 330))

    return reset_rect
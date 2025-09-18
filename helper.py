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
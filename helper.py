import pygame
from my_classes import *

def move_card_command(card: Card, target_location):
    previous_location = None
    def execute():
        nonlocal previous_location
        previous_location = card.location
        card.location = target_location
    def undo():
        if previous_location:
            card.location = previous_location
    return [execute, undo]

def pause_game(game):
    if not game.game_state == GameState.paused:
        game.previous_state = game.game_state
        game.game_state = GameState.paused
    else:
        game.game_state = game.previous_state
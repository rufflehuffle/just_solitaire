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
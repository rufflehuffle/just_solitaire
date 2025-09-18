import pygame
from my_classes import Card, Deck, Pile, Foundation, Waste
from helper import *

pygame.init()
pygame.display.set_caption('Solitaire')
icon = pygame.image.load('sprites/KH.png')
pygame.display.set_icon(icon)

screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
running = True

cards_being_dragged = []
card_mouse_offset = 0
drag_card_original_pos = None
draw_clicked = False

deck = Deck()
piles = deck.draw_starting_piles()
waste = Waste()
foundations = [Foundation(suit=suit) for suit in ['H', 'D', 'C', 'S']]
# Debug win screen
# for foundation in foundations:
#     foundation.append(Card('K', foundation.suit))

pygame.mixer.init()
pygame.mixer.music.load("music/luigi.mp3")
pygame.mixer.music.play(-1)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((81, 108, 58))
    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
    if (deck.rect.collidepoint(pygame.mouse.get_pos())):
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)

    keystate = pygame.key.get_pressed()

    # Handle drawing
    # On click on deck or 'SPACE' press,
    if ((deck.rect.collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]) or (keystate[pygame.K_SPACE])) and not draw_clicked and not cards_being_dragged:
        draw_clicked = True

        if deck.cards:
            card_drawn = deck.draw_card()
            waste.append(card_drawn)
            if card_drawn:
                pygame.time.delay(100)
        else:
            waste.loop(deck)

    # Debounce for drawing
    if not (pygame.mouse.get_pressed()[0] or keystate[pygame.K_SPACE]):
        draw_clicked = False
        
    # Render all game elements
    for pile in piles:
        pile.render(screen)

    for foundation in foundations:
        foundation.render(screen)

    if drag_card_original_pos and isinstance(drag_card_original_pos, Waste):
        waste.render(screen, n=2)
    else:
        waste.render(screen, n=3)

    deck.render(screen)

    # Check for clicks on cards
    # BUG: If you're holding MB1 and drag your cursor over a card it'll scoop it up.
    for card in get_all_cards_on_screen(piles, waste, foundations):
        if card.collision_rect.collidepoint(pygame.mouse.get_pos()) and card.is_draggable:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            if pygame.mouse.get_pressed()[0] and not cards_being_dragged:
                cards_being_dragged.append(card)
                drag_card_original_pos = card.location

                # Handle stacks in piles
                if isinstance(card.location, Pile):
                    pile = card.location
                    cards_being_dragged = pile.cards[card.location_index:]

                # Remove card from original location
                for card in cards_being_dragged:
                    card.location.pop()
                    card.location = None
                
                # Keep track of offset for dragging
                card_mouse_offset = cards_being_dragged[0].rect.topleft - pygame.Vector2(pygame.mouse.get_pos())    

    # On MB1 release,
    # BUG: Moving a card to a pile from the waste feels weird because the waste shifts back after snapping to pile
    if cards_being_dragged and not pygame.mouse.get_pressed()[0]:
        cards = cards_being_dragged
        top_card = cards[0]
        cards_being_dragged = []
        valid_placement = False

        # Check if valid placement for foundation or pile, if so place the card there!
        for pile in piles:
            if pile.collision_rect.colliderect(top_card.rect):
                if pile.validate_card_placement(top_card):
                    valid_placement = True
                    for card in cards:
                        pile.append(card)
                        card.location = pile
                    break

        for foundation in foundations:
            if foundation.collision_rect.colliderect(top_card.rect) and foundation.validate_card_placement(top_card) and len(cards) == 1:
                foundation.append(top_card)
                top_card.location = foundation
                valid_placement = True
                break

        # Return card if placement not valid
        if not valid_placement:
            for card in cards:
                drag_card_original_pos.append(card)
                card.location = drag_card_original_pos
        
        # If card was originally in a pile, reveal the next card
        if drag_card_original_pos and isinstance(drag_card_original_pos, Pile):
            drag_card_original_pos.flip()

        drag_card_original_pos = None

        pygame.time.delay(100)
    
    # Handle cards being dragged around
    if cards_being_dragged:
        stack_offset = 30
        cards_being_dragged[0].rect.topleft = pygame.mouse.get_pos()[0] + card_mouse_offset.x, pygame.mouse.get_pos()[1] + card_mouse_offset.y
        for i, card in enumerate(cards_being_dragged[1:], start=1):
            card.rect.topleft = (cards_being_dragged[0].rect.x, cards_being_dragged[0].rect.y + i * stack_offset)

        for card in cards_being_dragged:
            card.render(screen)
    
    # Game win detection
    foundation_top_cards = [foundation.cards[-1].value for foundation in foundations if foundation.cards]
    if foundation_top_cards == ['K', 'K', 'K', 'K']:
        # Render game-end pop-up
        bg_rect = pygame.Rect(0, 0, 400, 300)
        bg_rect.center = (screen.get_width() / 2, screen.get_height() / 2)
        pygame.draw.rect(screen, (51, 45, 82), bg_rect)

        font = pygame.font.SysFont('monogram', 32)
        text = font.render('You won!', False, 'white')
        screen.blit(text, (355, 240))
        
        reset_text = font.render("Reset", False, 'black')
        reset_rect = pygame.Rect(0, 0, 100, 50)
        reset_rect.center = bg_rect.center
        pygame.draw.rect(screen, 'white', reset_rect)
        screen.blit(reset_text, (370, 285))

        score_text = font.render(f"Score: {calculate_score(piles, foundations)}", False, 'white')
        screen.blit(score_text, (345, 330))

        if reset_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            if pygame.mouse.get_pressed()[0]:
                deck = Deck()
                piles = deck.draw_starting_piles()
                waste = Waste()
                foundations = [Foundation(suit=suit) for suit in ['H', 'D', 'C', 'S']]

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
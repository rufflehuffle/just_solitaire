import pygame
from my_classes import Card, Deck, Pile, Foundation, Waste
from helper import *

pygame.init()
pygame.display.set_caption('Just Solitaire')
icon = pygame.image.load('sprites/KH.png')
pygame.display.set_icon(icon)

screen = pygame.display.set_mode((800, 600))
clock = pygame.time.Clock()
running = True

cards_being_dragged = []
card_mouse_offset = 0
drag_card_original_pos = None
draw_clicked = False
paused = False
pause_debounce = False
round_over = False

player = Player()
game = Game()
deck, piles, foundations, waste = game.deck, game.piles, game.foundations, game.waste

# Debug win screen
# for foundation in foundations:
#    foundation.append(Card('K', foundation.suit))

# Debug round end
# deck.loops = deck.max_loops - 1
# deck.cards = []

pygame.mixer.init()
pygame.mixer.music.load("music/luigi.mp3")
pygame.mixer.music.play(-1)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill((81, 108, 58))
    # BUG: Cursor flicks between 'ARROW' and 'HAND' ocassionally while hovering over a clickable object
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
            if deck.loops == deck.max_loops:
                player.lives -= 1
                # Add round end screen
                if player.lives == 1:
                    # End game when out of lives
                    print('Game over!')
                else:
                    print('Round over!')
                    round_over = True
        
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
    for card in game.visible_cards:
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
    
    if pygame.key.get_pressed()[pygame.K_ESCAPE] and not pause_debounce:
        pause_debounce = True
        if not paused:
            paused = True
        else:
            paused = False
    
    if not pygame.key.get_pressed()[pygame.K_ESCAPE]:
        pause_debounce = False

    if paused:
        shadow_surf = pygame.Surface((screen.get_width(), screen.get_height()), pygame.SRCALPHA)
        shadow_surf.fill((0, 0, 0, 128))
        screen.blit(shadow_surf, (0, 0))

        pop_up_rect = pygame.Rect(0, 0, 400, 300)
        pop_up_rect.center = (screen.get_width() / 2, screen.get_height() / 2)
        pygame.draw.rect(screen, (51, 45, 82), pop_up_rect)

        font = pygame.font.SysFont('monogram', 32)

        reset_text = font.render("Reset", False, 'black')
        reset_rect = pygame.Rect(0, 0, 100, 50)
        reset_rect.center = pop_up_rect.center
        pygame.draw.rect(screen, 'white', reset_rect)
        screen.blit(reset_text, (370, 285))

        if reset_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            if pygame.mouse.get_pressed()[0]:
                paused = False
                game = Game()
                deck, piles, foundations, waste = game.deck, game.piles, game.foundations, game.waste

    # Game win detection
    foundation_top_cards = [foundation.cards[-1].value for foundation in foundations if foundation.cards]
    if foundation_top_cards == ['K', 'K', 'K', 'K']:
        # Render game-end pop-up
        reset_rect = game.render_game_end(screen, 'You won!')

        if reset_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            if pygame.mouse.get_pressed()[0]:
                game = Game()
                deck, piles, foundations, waste = game.deck, game.piles, game.foundations, game.waste
    
    if round_over:
            # BUG: Need to turn off interacting with cards / deck while this screen is open
            reset_rect = game.render_game_end(screen, f'Round over! You have {player.lives} lives remaining')

            if reset_rect.collidepoint(pygame.mouse.get_pos()):
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
                if pygame.mouse.get_pressed()[0]:
                    game = Game()
                    deck, piles, foundations, waste = game.deck, game.piles, game.foundations, game.waste
                    round_over = False

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
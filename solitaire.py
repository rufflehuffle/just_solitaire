import pygame
from my_classes import *
from helper import *
from interactables import *
from items import *

pygame.init()
pygame.display.set_caption('Just Solitaire')
icon = pygame.image.load('sprites/KH.png')
pygame.display.set_icon(icon)

screen = pygame.display.set_mode([800, 600])
clock = pygame.time.Clock()
running = True

cards_being_dragged = []
card_mouse_offset = 0
drag_card_original_pos = None
shop_open = False

game = Game()
deck, piles, foundations, waste, player = game.deck, game.piles, game.foundations, game.waste, game.player

interactables = []
# test_button = Button(None, None, True, pygame.Rect(100, 100, 100, 100), None, 'Test', 16, 'white')
# interactables.append(test_button)
open_pause = Interactable(hotkey=pygame.K_ESCAPE, on_click=pause_game, context=game)
interactables.append(open_pause)
interactables.append(game.deck)

shop = Shop()
# Debug shop screen
# game.game_state = GameState.in_shop
shop.items = [extra_life, extra_loop]
for item in shop.items:
    item.location = shop
    item.is_active = False
    # item.on_hover = lambda x: print(item.name)
interactables.extend(shop.items)

# Debug win screen
# for foundation in foundations:
#    foundation.append(Card('K', foundation.suit))

# Debug round end
# deck.loops = deck.max_loops - 1
# deck.cards = []

# Debug game over
# player.lives = 1
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

    keystate = pygame.key.get_pressed()

    for interactable in interactables:
        interactable.is_active = False

    if game.game_state == GameState.in_round:
        deck.is_active = True
        open_pause.is_active = True
            
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
            for card in cards_being_dragged:
                card.being_dragged = False
                card.time_held = 0
                card.velocity = 0
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
        # TO-DO: Add a bit of lag and momentum to moving the card around so it actually FEELS like you're dragging it around
        if cards_being_dragged:
            stack_offset = 30
            top_card = cards_being_dragged[0]
            # top_card.rect.topleft = pygame.mouse.get_pos()[0] + card_mouse_offset.x, pygame.mouse.get_pos()[1] + card_mouse_offset.y
            top_card.rect.center = top_card.drag_tween(pygame.mouse.get_pos())
            # top_card_velocity = (top_card.rect.x - top_card_prev_pos[0], top_card.rect.y - top_card_prev_pos[1])

            for i, card in enumerate(cards_being_dragged[1:], start=1):
                card.rect.topleft = (cards_being_dragged[0].rect.x, cards_being_dragged[0].rect.y + i * stack_offset)

            for card in cards_being_dragged:
                card.being_dragged = True
                card.time_held += 1
                card.render(screen)

        # Game win detection
        foundation_top_cards = [foundation.cards[-1].value for foundation in foundations if foundation.cards]
        if foundation_top_cards == ['K', 'K', 'K', 'K']:
            game.game_state = GameState.round_win

    if game.game_state == GameState.paused:
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
                game.game_state = GameState.in_round
                game.reset()
                deck, piles, foundations, waste = game.deck, game.piles, game.foundations, game.waste

    if game.game_state == GameState.in_shop:
        next_round_rect = shop.render(screen, game.player)

        for item in shop.items:
            item.context = game.player
            item.is_active = True

        for item in game.player.items:
            item.on_click = None

        if next_round_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            if pygame.mouse.get_pressed()[0]:
                game.game_state = GameState.in_round

    if game.game_state == GameState.round_win:
        pop_up_text = 'You won!'

        # Render game-end pop-up
        reset_rect = game.render_game_end(screen, pop_up_text)

        if reset_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            if pygame.mouse.get_pressed()[0]:
                game.reset()
                interactables.remove(deck)
                interactables.append(game.deck)
                deck, piles, foundations, waste = game.deck, game.piles, game.foundations, game.waste
                if game.game_state == GameState.round_over:
                    game.game_state = GameState.in_shop
                elif game.game_state == GameState.game_over:
                    game.game_state = GameState.in_round
                    game.player = Player()
                    player = game.player

    if game.game_state == GameState.round_over:
        pop_up_text = f'Round over! You have {player.lives} lives remaining'

        # Render game-end pop-up
        reset_rect = game.render_game_end(screen, pop_up_text)

        if reset_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            if pygame.mouse.get_pressed()[0]:
                game.reset()
                interactables.remove(deck)
                interactables.append(game.deck)
                deck, piles, foundations, waste = game.deck, game.piles, game.foundations, game.waste
                game.game_state = GameState.in_shop

    if game.game_state == GameState.game_over:
        pop_up_text = f'Game over! Total score: {player.total_score}'

        # Render game-end pop-up
        reset_rect = game.render_game_end(screen, pop_up_text)

        if reset_rect.collidepoint(pygame.mouse.get_pos()):
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            if pygame.mouse.get_pressed()[0]:
                game.reset()
                interactables.remove(deck)
                interactables.append(game.deck)
                deck, piles, foundations, waste = game.deck, game.piles, game.foundations, game.waste
                game.game_state = GameState.in_round
                game.player = Player()
                player = game.player

    # Render and handle all interactable objects
    #   Ex: Deck, Cards, Buttons, etc.
    for interactable in interactables:
        if interactable.is_active:
            interactable.render(screen)
            is_hovering = interactable.rect.collidepoint(pygame.mouse.get_pos()) if interactable.rect else False
            mb1_down = pygame.mouse.get_pressed()[0]
            hotkey_down = keystate[interactable.hotkey] if interactable.hotkey else False
            if is_hovering:
                if interactable.on_hover:
                    interactable.on_hover(interactable.context)
                if interactable.on_click:
                    pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND)
            if not interactable.debounce:
                if (is_hovering and mb1_down) or hotkey_down:
                    if interactable.on_click:
                        interactable.on_click(interactable.context)
                    interactable.debounce = True
            if not(mb1_down or hotkey_down):
                interactable.debounce = False

    pygame.display.flip()

    clock.tick(60)

pygame.quit()
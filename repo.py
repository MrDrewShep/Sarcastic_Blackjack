
import sarcastic_blackjack
import pprint
import os
import time

#F ? turn both **check_if_players_still_playing** and **check_if_dealers_turn** and **dealer_check_needs_to_play_out_hand** can be combined into 1 round.player_hands_still_in_play int value?
#Test various payouts: push, push after having doubled down, otherwise-natural-blackjack dealt to a split hand
#F Turn the time.sleep values into variables, and use depending on outcomes

back_story_1 = "This dealer needs to go, and you're the one who can get her fired!"
back_story_2 = "The Whipperwill Truck-Stop/Dinner-Theatre/Casino in Bugtussle, KY has one mean Blackjack dealer. You and the other patrons have had enough of her salty one-liners. Time to get her fired. So here's the plan: Other patrons will spread a rumor for management to catch wind of -- that she's off her rocker and paying out too much for winning hands (she isn't). Double your bankroll to $500, and the management will surely cut her loose. Good luck! This game is rated PG-13."
house_rules_1 = "House rules:"
house_rules_2 = ["- Player selects the number of decks", "- Dealer hits below 17", "- If dealer's Ace would bring her total to, or above, 17 (but not above 21) then dealer must count the Ace as 11", "- Blackjack pays 3:2", "- Minimum wager is $10", "- A Blackjack dealt to a split hand pays only 1:1"]
rules_not_used = ["- Split Aces can only be hit up to once more"]


def deal_card(shoe, hand):
    """Deals 1 card to a specified hand"""
    hand.receive_card(shoe.deal_card())


def new_game_setup(name, decks):
    """Constructs main objects for a new game: Game, shoe (cards), player, dealer"""
    game = sarcastic_blackjack.Game()
    shoe = game.init_new_shoe(decks)
    player = game.init_player(name)
    dealer = game.init_dealer()

    return game


def new_round_setup(game):
    """Constructs a new round of play"""
    this_round = game.init_new_round()
    this_round.clear_all_hands()
    game.dealer.set_needs_to_play_out_my_hand(True)

    player_hand = game.player.add_hand()
    dealer_hand = game.dealer.add_hand()

    return this_round


def set_wager(hand, wager):
    """Eval and set the player's wager"""
    bank = hand.owner.bank
    wager_message = ""

    try:
        wager = int(wager)
    except:
        wager_message += "\nSure. Because this game is free.... Not."
        wager = False
        return wager, wager_message

    if wager == 0:
        wager_message += "\nSure. Because this game is free.... Not."
        wager = False
    if wager > bank:
        wager_message += "\nMoneybags, you ain\'t got enough."
        wager = False
    if not wager % 10 == 0:
        wager_message += "\nPoor thing. No one taught you to read. Increments of $10 only."
        wager = False

    if wager:
        hand.set_wager(wager)
        hand.owner.withdraw_from_bank(wager)
    
    return wager, wager_message


def increase_wager(game, hand, increase):
    """Eval and increase the wager, i.e. for doubling down and splitting hands"""
    hand.increase_wager(increase)


def initial_dealing(game):
    """Deals the initial rounds of cards to player and dealer"""
    player_hand = game.player.hands[0]
    dealer_hand = game.dealer.hands[0]

    player_hand.receive_card(game.shoe.deal_card())          #F come back and make these modular for multiple players
    dealer_hand.receive_card(game.shoe.deal_card())
    player_hand.receive_card(game.shoe.deal_card())
    dealer_hand.receive_card(game.shoe.deal_card(False))

    refresh_hand(player_hand)
    refresh_hand(dealer_hand)


def refresh_hand(hand):
    """Takes the current status of the designated hand, and updates all relevant hand attributes. E.g. The total point value, is the hand eligible to be doubled down. Run after each card is dealt."""
    hand.refresh()


def check_initial_dealing(game):
    """Used only after initial_dealing, checks if any hand results dictate that the round is resolved upon arrival."""
    dealer = game.dealer
    dealer_hand = dealer.hands[0]
    player = game.player
    player_hand = player.hands[0]
    wager = player_hand.wager
    bank = player.bank
    dealer_msg = ""
    end_of_round_msg = ""
    winresult = ""

    if dealer_hand.isblackjack:
        in_player_turns = False
        in_dealers_turn = False
        dealer.set_needs_to_play_out_my_hand(False)
        dealer.reveal_cards()
        if player_hand.isblackjack:
            winresult = "push"
            dealer_msg = dealer.sarcastic("push_blackjacks")
            end_of_round_msg = f"Dealer and {player.name} push"
        else:
            winresult = "lose"
            dealer_msg = dealer.sarcastic("dealer_blackjack")
            end_of_round_msg = "Dealer has blackjack"
    elif player_hand.isblackjack:
        winresult = "blackjack"
        in_player_turns = False
        in_dealers_turn = False
        dealer.reveal_cards()
        dealer_msg = dealer.sarcastic("player_blackjack")
        end_of_round_msg = f"Player wins $winnings!"  #F f-string winnings
    else:
        game.round.set_next_turn()
        in_player_turns = True
        in_dealers_turn = True

    if winresult:
        player_hand.set_winresult(winresult)
        payout_hand(game, player_hand)

    return in_player_turns, in_dealers_turn, end_of_round_msg, dealer_msg


def eval_hand(game, hand, end_of_round=False):
    """If applicable, assignes the hand.winresult attribute."""
    winresult = hand.winresult
    hand_value = hand.value
    dealer_value = game.dealer.hands[0].value
    
    if winresult:
        return winresult, True

    if end_of_round:
        if dealer_value > 21:
            winresult = "win"
        elif hand_value > dealer_value:
            winresult = "win"
        elif hand_value == dealer_value:
            winresult = "push"
        elif hand_value < dealer_value:
            winresult = "lose"
    else:
        if hand.isbusted:
            winresult = "lose"
        elif hand.value == 21:
            #F insert dealer message here? you got to 21, without natural blackjack
            goto_next_turn(game)

    hand.set_winresult(winresult)

    return winresult, False


def payout_hand(game, hand):
    """If not done already, pays out the designated hand"""
    winresult = hand.winresult
    bank = hand.owner.bank
    wager = hand.wager

    if not winresult:
        return

    winnings = 0
    
    if winresult == "lose":
        pass
    elif winresult == "win":
        winnings = wager * 2
    elif winresult == "push":
        winnings = wager
    elif winresult == "blackjack":
        winnings = int(wager * 5/2)

    return hand.owner.deposit_to_bank(winnings)


def get_turn(game):
    """Returns the hand whose turn it currently is, or None"""
    return game.round.get_turn()


def goto_next_turn(game):
    """Sets the round turn_owner and turn_hand attributes to the next applicable hand around the table."""
    game.round.set_next_turn()


def check_if_dealers_turn(game):
    """Returns whether or not the game is still playing hands of the players, or has moved onto the dealer's hand."""
    current_player = game.round.turn_owner

    if not current_player or current_player == game.dealer:
        in_player_turns = False
    elif current_player == game.player:
        in_player_turns = True
    
    return in_player_turns
        #F no more players to go through
        #F goto end of round
    
    #FF Add to this.... once we get to dealer, run dealer_autoplay, and after dealer, run end_of_round


def play_player_hand(game, selection):
    """Takes in the player's selection from the game screen, and executes the applicable choice, if eligible."""
    hand = game.round.get_turn()
    bank = hand.owner.bank
    wager = hand.wager
    shoe = game.shoe
    dealer_msg = None

    if selection == "stand":
        goto_next_turn(game)
    elif selection == "hit":
        deal_card(shoe, hand)
        hand.set_isdoublable(False)
    elif selection == "double_down":
        if wager > bank:
            difference = abs(bank - wager)
            dealer_msg = f"You'd be ${difference} short. Put it on your tab?"
        else:
            if hand.isdoublable:
                increase_wager(game, hand, wager)
                hand.owner.withdraw_from_bank(wager)
                deal_card(shoe, hand)
                goto_next_turn(game)
            else:
                dealer_msg = "Can\'t double after hitting. You must play this game a lot."
    elif selection == "split":
        if hand.issplitable:
            if wager > bank:
                dealer_msg = game.dealer.sarcastic("insufficient_funds")
            else:
                hand.split_hand()
                #F to fix the issplitalbe/isdoublable attributes on each hand, probably need to jump from here to the dealing of the other cards. or, store an additional attribute so that when that hand comes up for play again it "auto-deals" x cards, then resets those 2 attributes.
        else:
            dealer_msg = "You were dropped on your head as a child? Can\'t split those."

    refresh_hand(hand)
    winresult, already_paid = eval_hand(game, hand)

    if winresult:
        if hand.is21:
            dealer_msg = "Even a blind squirrel..."
        if hand.isbusted:
            dealer_msg = game.dealer.sarcastic("bust")
            if bank < 50:
                dealer_msg = game.dealer.sarcastic("low_bank")
        if not already_paid:
            payout_hand(game, hand)
        goto_next_turn(game)

    return dealer_msg


def check_if_players_still_playing(game):
    """#F TBD"""
    in_player_turns = check_if_dealers_turn(game)
    return in_player_turns


def reveal_dealer_cards(game):
    """Turns up any dealer cards which are face down."""
    game.dealer.reveal_cards()


def check_dealer_needs_to_play_out_my_hand(game):
    return game.dealer.check_needs_to_play_out_my_hand(game)


def eval_dealer_next_play(game):
    pass  #F


def play_dealer_hand(game):
    """Plays 1 iteration of the dealer's turn, returns Bool whether dealer should play another iteration."""
    dealer = game.dealer
    dealer_hand = game.dealer.hands[0]
    dealer_msg = ""

    if dealer_hand.isbusted:
        dealer_msg = dealer.sarcastic("dealer_bust")
        dealer.set_needs_to_play_out_my_hand(False)
        goto_next_turn(game)
    elif 21 >= dealer_hand.value >= 17:
        dealer.set_needs_to_play_out_my_hand(False)
        goto_next_turn(game)
    else:
        dealer_hand.receive_card(game.shoe.deal_card())

    refresh_hand(dealer_hand)

    return dealer.needs_to_play_out_my_hand, dealer_msg


def end_of_round(game):
    """Ensures eval and payment of any hands which required the dealer having played before resolving."""
    for hand in game.player.hands:
        winresult, already_paid = eval_hand(game, hand, True)
        if not already_paid:
            payout_hand(game, hand)


# def get_game(game):       #F Looks like this is unused? Marked for deletion.
#     game.get_game()


def check_game_over(game):
    """Used after the conclusion of each round, evals whether the player is bankrupt or achieved the goal."""
    bank = game.player.bank
    game_over = False
    is_win = None
    dealer_msg = ""

    if bank < 10:
        game_over = True
        is_win = False
        dealer_msg = game.dealer.sarcastic("game_over_loser")
    elif bank >= 500:
        game_over = True
        is_win = True
        dealer_msg = game.dealer.sarcastic("game_over_winner")


    return game_over, is_win, dealer_msg

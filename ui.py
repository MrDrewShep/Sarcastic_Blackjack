
""" NOTES FROM DREW TO ADAM 10/24/19
- I use #F so I can ctrl+f the areas of my files I need to return and "fix".
- Maybe if you don't mind using #A for "Adam comments" I'll be able to distinguish

- There are likely variables or chunks of functions that are now unused/obsolete, that I'll need to cull. Sorry.
- Game is 99% functional. Multiple bugs to still work out, including:
    - Assignment of colors / whose turn it is
    - Dealer sometimes unnecessarily plays her hand out, even if player hands are already fully resolved

Future iterations of this game:
- Want to add more quotes for various scenarios
- v2.0 in pygame with GUI
    - Include gestures from the dealer?
    - Show stacks of chips to match actual values?
    - Dribble payouts into the player's bank, rapidly $1 at a time
- v3.0 with multiplayer
- v4.0 with saved games (?)

"""

#F refactor display of dealer/player hands DRY

import os
import time
import textwrap
import random
import pprint
import repo
from colorama import init
init()
from colorama import Fore, Back, Style


splash_1 = r"""
  _________                                     __  .__         
 /   _____/____ _______   ____ _____    _______/  |_|__| ____   
 \_____  \\__  \\_  __ \_/ ___\\__  \  /  ___/\   __\  |/ ___\  
 /        \/ __ \|  | \/\  \___ / __ \_\___ \  |  | |  \  \___  
/_______  (____  /__|    \___  >____  /____  > |__| |__|\___  > 
        \/     \/            \/     \/     \/               \/  
__________.__                 __         __               __    
\______   \  | _____    ____ |  | __    |__|____    ____ |  | __
 |    |  _/  | \__  \ _/ ___\|  |/ /    |  \__  \ _/ ___\|  |/ /
 |    |   \  |__/ __ \\  \___|    <     |  |/ __ \\  \___|    < 
 |______  /____(____  /\___  >__|_ \/\__|  (____  /\___  >__|_ \
        \/          \/     \/     \/\______|    \/     \/     \/ """ + "\n"

stack_10 = """
     _______
    (_______)
   (_______)
"""


def clear_screen():
    """Clears the screen, usually before "refreshing" the game"""
    os.system('cls' if os.name == "nt" else 'clear')


def display_menu(screen="home", in_main=True):
    """Displays the root game menu, with prompts"""
    clear_screen()
    print(splash_1)
    if screen == "home":
        pass
    elif screen == "rules":
        rules_screen()
    elif screen == "story":
        story_screen()

    while in_main:
        main_menu = """
        1) Play a game
        2) Read the story
        3) Read the house rules
        4) Exit
            > """
        try:
            selection = int(input(main_menu))
        except:
            display_menu()

        if selection == 4:    # Exit
            in_main = False
            in_game = False
            in_round = False
            hand_in_play = False
            clear_screen()
            quit()
        elif selection == 3:    # Rules
            display_menu("rules")
        elif selection == 2:    # Story
            display_menu("story")
        elif selection == 1:    # Play
            in_main = False
            name, decks = new_game_info()
            game = repo.new_game_setup(name, decks)
            display_game(game)

def story_screen():
    """Display the game's backstory"""
    print(textwrap.fill(repo.back_story_1))
    print("\n")
    print(textwrap.fill(repo.back_story_2))


def rules_screen():
    """Display the game's rules"""
    print(textwrap.fill(repo.house_rules_1))
    print("\n")
    print("\n".join(repo.house_rules_2))


def new_game_info():
    """User inputs preliminary info before start of game"""
    in_new_game_info = True
    while in_new_game_info:
        in_new_game_info = False
        clear_screen()
        print(splash_1)
        print("\n", build_speech_bubble())
        print(" - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ")
        print("New game:", "\n")

        try:
            name = input("I'm Opal... What's your name partner? ").title()
            if len(name) < 1:
                raise KeyError
            decks = int(input("How many decks would you like to play with (1-6)? "))    #F build logic to restrict values from 1-6
        except:
            in_new_game_info = True

    return name, decks


def build_speech_bubble(text=None):
    """Constructs the ascii-art-esque speech bubble with dealer quotes, or "blank filler space," refreshed routinely within the game screen"""
    if text:
        list_text_lines = textwrap.wrap(text, width=25)
        list_speech_bubble_lines =  [r"           ^                     ",
                                     r" _________/ \___________________ ",
                                     r"|                               |"]
                            
        for line in list_text_lines:
            ending_spaces = 28 - len(line)
            list_speech_bubble_lines.append("|   " + line + ending_spaces*" " + "|")
        list_speech_bubble_lines.append(r"|_______________________________|")
        remaining = 8 - len(list_speech_bubble_lines)
        for i in range(0, remaining):
            list_speech_bubble_lines.append(" ")

        speech_bubble = ""
        for line in list_speech_bubble_lines:
            speech_bubble += " "*30 + line + "\n"
    else:
        speech_bubble = "\n\n\n\n\n\n\n\n"

    return speech_bubble


def display_header(game, dealer_msg=None):
    """Display header info: Game logo, player's bankroll, dealer speech bubble"""
    bank = game.player.bank
    
    print(splash_1)
    print(f'Bankroll: ${bank}')
    print(build_speech_bubble(dealer_msg))
    print(" - - - - - - - - - - - - - - - - - - - - - - - - - - - - - ")


def display_hands(game):
    """Display current status of all hands at the table"""
    turn_hand = repo.get_turn(game)

    longest_wager = ""
    for hand in game.player.hands:
        len_wager = len(str(hand.wager))
        len_longest = len(longest_wager)
        if len_wager > len_longest:
            longest_wager = str(hand.wager)

    longest_wager = f'(${longest_wager}):  '

    dealer_label = "Dealer\'s hand:  "
    len_dealer_label = len(dealer_label)
    longest_player_label = f'{game.player.name}\'s hand ' + longest_wager
    len_longest_player_label = len(longest_player_label)
    
    longest = 0
    if len_longest_player_label > len_dealer_label:
        longest = len_longest_player_label
    else:
        longest = len_dealer_label

    while len(dealer_label) < longest:
        dealer_label += " "

    
    print("  ", dealer_label, end="")
    if game.dealer.hands[0] == turn_hand:
        print(Back.WHITE, end="")
        print(Fore.BLACK, end="")
    card_count = len(game.dealer.hands[0].cards)
    hand_display = ""
    for card in game.dealer.hands[0].cards:
        card_count -= 1
        if card_count:
            if card.face == "10":
                append_spaces = " "
            else:
                append_spaces = "  "
        else:
            append_spaces = ""
        hand_display += str(card) + append_spaces
    print(hand_display, end="")

    print(Style.RESET_ALL)
    
    for hand in game.player.hands:
        winresult = hand.winresult
        card_count = len(hand.cards)
        player_label = f'{game.player.name}\'s hand:  '
        while len(player_label) < longest:
            player_label += " "
        print("\n\n  ", player_label, end="")
        if not winresult:
            pass
        elif winresult == "win":
            print(Back.GREEN, end="")
        elif winresult == "lose":
            print(Back.RED, end="")
        elif winresult == "push":
            print(Back.LIGHTYELLOW_EX, end="")
            print(Fore.BLACK, end="")
        elif winresult == "blackjack":
            print(Back.CYAN, end="")
        if hand == turn_hand:
            print(Back.WHITE, end="")
            print(Fore.BLACK, end="")
        hand_display = ""
        for card in hand.cards:
            card_count -= 1
            if card_count:
                if card.face == "10":
                    append_spaces = " "
                else:
                    append_spaces = "  "
            else:
                append_spaces = ""
            hand_display += card.face + append_spaces
        print(hand_display, end="")
        print(Style.RESET_ALL, end="")

    print()


def display_game(game, in_game=True, quitting=False, wager_message=""):
    """Game state"""
    while not quitting and in_game:
        """Game state"""
        in_round = True
        this_round = repo.new_round_setup(game)

        while not quitting and in_round:
            """Round state"""
            
            in_wager = True
            in_reveal_dealer_hand = True
            in_end_of_round = True

            while not quitting and in_wager:
                """Gather player's initial wager"""
                
                hand = game.player.hands[0]
                wager = False
                while not quitting and not wager:
                    clear_screen()
                    display_header(game, wager_message)
                    wager_input = input("Make a wager ($10 minimum increments) or (Q) to quit: ")
                    if wager_input.casefold() == "q":
                        quitting = True
                        break
                    wager, wager_message = repo.set_wager(hand, wager_input)
                in_wager = False

            repo.initial_dealing(game)
            in_player_turns, in_dealers_turn, end_of_round_msg, dealer_msg = repo.check_initial_dealing(game)

            while not quitting and in_player_turns:
                """Player's turn(s)"""
                clear_screen()
                display_header(game, dealer_msg)
                display_hands(game)

                in_player_turns = repo.check_if_players_still_playing(game)
                if not in_player_turns:
                    break

                prompt = """
                (H) Hit
                (S) Stay
                (D) Double down
                (Y) Split
                (Q) Quit game
                    > """

                options = ["h", "s", "d", "y", "q"]
                try:
                    selection = input(prompt).lower()
                    if selection not in options:
                        raise KeyError
                    elif selection == "q":
                        quitting = True
                        break
                        #F Learn how to garbage collect all the data I've built so far, just use "del"? past hands, rounds, etc
                    elif selection == "h":
                        selection = "hit"
                    elif selection == "s":
                        selection = "stand"
                    elif selection == "d":
                        selection = "double_down"
                    elif selection == "y":
                        selection = "split"
                except:
                    pass
                
                dealer_msg = repo.play_player_hand(game, selection)

            #F This is already done, correct(?), if initial dealing dictated it. If that's the case, then executing this should be conditional.
            while not quitting and in_reveal_dealer_hand:
                """Reveal dealer's hold card, after players are done playing"""
                time.sleep(1)
                repo.reveal_dealer_cards(game)
                clear_screen()
                display_header(game, dealer_msg)
                display_hands(game)
                time.sleep(1)

                in_dealers_turn = repo.check_dealer_needs_to_play_out_my_hand(game)
                in_reveal_dealer_hand = False

            while not quitting and in_dealers_turn:
                """Dealer's turn"""
                in_dealers_turn, dealer_msg = repo.play_dealer_hand(game)
                clear_screen()
                display_header(game, dealer_msg)
                display_hands(game)
                time.sleep(1)

            while not quitting and in_end_of_round:
                """End of round display"""
                repo.end_of_round(game)

                clear_screen()
                display_header(game, dealer_msg)
                display_hands(game)

                game_over, is_win, dealer_msg = repo.check_game_over(game)
                if not game_over:
                    input("\n   ENTER to play next hand")
                else:
                    input("\n   ENTER")
                in_end_of_round = False
                in_round = False

        while not quitting and game_over:
            """Game over display"""
            clear_screen()
            display_header(game, dealer_msg)
            if is_win:
                print('\n   You win.')
            else:
                print('\n   Adios.')

            input("\n   ENTER for main menu")
            game_over = False
            in_game = False

    display_menu()


if __name__ == "__main__":
    display_menu()

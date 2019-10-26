
import pprint
import random
import time

#f EXPAND THE SARCASTIC LIBRARY

class Card:

    def __init__(self, face, suit, value):
        self.face = face
        self.suit = suit
        self.value = value
        self.isfaceup = True

    def __repr__(self):
        return f'{self.face}' if self.isfaceup else f'?'

    def set_isfaceup(self, value):
        """Changes the face up/down value of a card."""
        self.isfaceup = value


class Shoe:

    def __init__(self, decks):
        self.decks = decks
        self.cards = []

        self.fill_shoe()

    def fill_shoe(self):
        """Builds a shuffled stack of cards, of specified number of decks. Also used when "reshuffling"."""
        suits = [
            "Spades",
            "Hearts",
            "Diamonds",
            "Clubs"
        ]
        cards = [
            {"face": "A", "value": 11}, 
            {"face": "K", "value": 10}, 
            {"face": "Q", "value": 10}, 
            {"face": "J", "value": 10}, 
            {"face": "10", "value": 10}, 
            {"face": "9", "value": 9}, 
            {"face": "8", "value": 8}, 
            {"face": "7", "value": 7}, 
            {"face": "6", "value": 6}, 
            {"face": "5", "value": 5}, 
            {"face": "4", "value": 4}, 
            {"face": "3", "value": 3}, 
            {"face": "2", "value": 2}
        ]
        for i in range(self.decks):
            for suit in suits:
                for card in cards:
                    new_card = Card(card["face"], suit, card["value"])
                    self.cards.append(new_card)

        self.shuffle_shoe()

    def __repr__(self):
        return f'{self.cards}'

    def length(self):
        return len(self.cards)

    def shuffle_shoe(self):
        """Shuffles the shoe/deck."""
        random.shuffle(self.cards)

    def deal_card(self, isfaceup=True):
        """Provides 1 card, upon request."""
        if self.length() == 0:
            self.fill_shoe()

        card = self.cards.pop(0)

        if not isfaceup:
            card.isfaceup = False

        return card


class Hand:

    def __init__(self, owner, starter_card=None, wager=0):
        self.owner = owner
        if not starter_card:
            self.cards = []
        else:
            self.cards = starter_card
        self.length = 0
        self.value = 0
        self.wager = wager
        self.issplitable = None
        self.isdoublable = None
        self.isbusted = False
        self.isblackjack = None
        self.is21 = None
        self.winresult = None       # Options: win, lose, push, blackjack, or None means not yet resolved

    def __repr__(self):
        return f'{self.cards}'

    def refresh(self):
        """Updates all hand attributes, based upon the current status of the hand."""
        self.check_isbusted()
        self.check_issplitable()
        self.check_isdoublable()
        self.check_length()
        self.check_isblackjack()
        self.check_is21()

    def check_length(self):
        self.length = len(self.cards)
        return self.length

    def check_is21(self):
        if self.value == 21:
            self.is21 = True
        return self.is21

    def receive_card(self, card):
        """Append a drawn card to the hand."""
        self.cards.append(card)

    def set_isdoublable(self, value):
        """If the hand has taken a hit, it cannot be doubled."""
        self.isdoublable = value

    def check_isbusted(self):  #F Break these into 2 separate methods? They seem to be related enough.
        """Updates self.value of the hand, also returns Bool indicating whether busted or not."""
        sum = 0
        aces = 0
        for card in self.cards:
            if card.face == "A":
                aces += 1
            sum += card.value
        self.value = sum

        if sum > 21:
            if aces == 0:
                self.isbusted = True
            elif aces > 0:
                for ace in range(aces):
                    sum -= 10
                    if sum <= 21:
                        self.value = sum
                        break
                if sum > 21:
                    self.value = sum
                    self.isbusted = True
        else:
            self.value = sum

        return self.isbusted

    def check_issplitable(self):
        """Bool, a hand must have only 2 cards, of identical face values."""
        self.issplitable = True if self.check_length() == 2 and self.cards[0].face == self.cards[1].face else False
        return self.issplitable
        #? How can I pytest this because it doesn't take any args?
        #? Do I have to break it down further into methods that accept args?

    def check_isdoublable(self):
        """Evals and sets the isdoublable attribute."""
        self.isdoublable = True if len(self.cards) == 2 else False
        return self.isdoublable

    def check_isblackjack(self):
        """Evals and sets the isblackjack attribute."""
        if self.check_length() != 2:
            self.isblackjack = False
        else:
            aces = 0
            ten_cards = 0
            for card in self.cards:
                if card.value == 11: aces += 1
                if card.value == 10: ten_cards += 1
            if aces == 1 and ten_cards == 1:
                self.isblackjack = True
                self.isincomplete = False
            else:
                self.isblackjack = False

        return self.isblackjack

    def set_wager(self, wager):
        """Writes the player's wager to the hand."""
        self.wager = wager

    def increase_wager(self, increase):
        """Adds to the hand's wager, in the event of a double down."""
        self.wager += increase

    def set_issplittable(self, value):
        self.issplitable = value

    def split_hand(self):
        """Builds a new, empty hand. Takes 1 card from the original hand and gives it to the new hand. Each hand will then have 1 card, of identical face value."""
        self.set_issplittable(True)
        self.set_isdoublable(True)      #F before these would work, need to auto-deal cards following the split, then reset the issplitable/isdoublable elements on each of the 2 split hands.
        starter_card = [self.cards.pop()]
        self.owner.add_hand(starter_card, self.wager)

    def set_winresult(self, result):
        """Sets the winresult: win, lose, push, blackjack."""
        self.winresult = result


class Player:

    def __init__(self, name):
        self.name = name
        self.hands = []
        self.bank = 250

    def __repr__(self):
        return f'{self.name}\'s got {self.hands}'

    def add_hand(self, starter_card=None, wager=0):
        """Creates a new hand, assigning it to the player."""
        new_hand = Hand(self, starter_card, wager)
        if wager:
            new_hand.wager = wager
            self.withdraw_from_bank(wager)
        self.hands.append(new_hand)              
        return new_hand

    def get_hand(self, index):  #F Is this in use, or needs deleted?
        """Returns the hand of a player, at the specified index."""
        return self.hands[index]

    def get_bank(self):
        """Returns the money in the player's bank."""
        return self.bank

    def withdraw_from_bank(self, wager):
        """Reduce the player's bank, when a wager is made."""
        self.bank -= wager
        return self.bank

    def deposit_to_bank(self, deposit):
        """Deposit in the player's bank, when paying out a winning hand."""
        self.bank += deposit
        return deposit

    # def refresh_hands(self):        #F maybe ditch this, and refresh at the hand level
    #     for hand in self.hands:
    #         hand.refresh()


class Dealer:

    def __init__(self, name="Opal"):
        self.name = name
        self.hands = []
        self.needs_to_play_out_my_hand = True    # Sets to False if: Dealer or player blackjack, Dealer busts, Dealer scores btwn 17-21 inclusive, All Player hands .winresult is True (!= None) before dealer would play

    def __repr__(self):
        return f'{self.name}\'s got {self.hands}'

    def add_hand(self):
        new_hand = Hand(self)
        self.hands.append(new_hand)
        return new_hand

    def refresh_hands(self):
        for hand in self.hands:
            hand.refresh()

    def reveal_cards(self):
        """Turns all the dealer's cards faceup."""
        for card in self.hands[0].cards:
            card.isfaceup = True

    
    def check_needs_to_play_out_my_hand(self, game):
        hands_unresolved = False
        for hand in game.player.hands:
            if not hand.winresult:
                hands_unresolved = True

        self.set_needs_to_play_out_my_hand(hands_unresolved)
        return self.needs_to_play_out_my_hand

    def set_needs_to_play_out_my_hand(self, value):
        self.needs_to_play_out_my_hand = value
        return self.needs_to_play_out_my_hand

    def sarcastic(self, quote_type):
        """Returns a randomly selected, sarcastic quip for a specified scenario type."""
        bust = [
            "High score!",
            "Save some cards for the other customers.",
            "You should give Blackjack lessons.",
            "",
            ""
        ]

        dealer_bust = [
            "Drat",
            "Don't think me busting means you're good at this."
        ]

        low_bank = [
            "Quit, while you can still afford the buffet.",
            "Can hardly see you over that stack of chips.",
            "Are you an \"I don\'t need to win to be happy\" type?"
            "",
            ""
        ]

        push_blackjacks = [
            "Glad we got something accomplished there...",
            ""
        ]

        dealer_blackjack = [
            "Participation ribbons are by the door.",
            "Better to have played and lost, than never to have played at all.",
            ""
        ]

        player_blackjack = [
            "Worked hard for that one, did ya?"
        ]

        insufficient_funds = [
            "You a math teacher? Insufficient funds.",
            "Let me get out my credit card machine.",
            "With what chips?",
            ""
        ]

        game_over_winner = [
            "Wait, what?!?! I don\'t want to get fired!!!!"
        ]

        game_over_loser = [
            "You\'re a regular Ed Norton huh?"
        ]

        if quote_type == "bust":
            quote_type = bust
        elif quote_type == "low_bank":
            quote_type = low_bank
        elif quote_type == "push_blackjacks":
            quote_type = push_blackjacks
        elif quote_type == "dealer_blackjack":
            quote_type = dealer_blackjack
        elif quote_type == "player_blackjack":
            quote_type = player_blackjack
        elif quote_type == "insufficient_funds":
            quote_type = insufficient_funds
        elif quote_type == "dealer_bust":
            quote_type = dealer_bust
        elif quote_type == "game_over_winner":
            quote_type = game_over_winner
        elif quote_type == "game_over_loser":
            quote_type = game_over_loser

        dealer_msg = random.choice(quote_type)
        return dealer_msg


class Round:

    def __init__(self, game):
        self.game = game
        self.player = self.game.player
        self.dealer = self.game.dealer
        self.turn_owner = None
        self.turn_hand = None
        self.in_play = True     #F what does this do

    def clear_all_hands(self):
        """Empites the list of hands for both player and dealer. When resetting for a new round of play."""
        self.player.hands = []
        self.dealer.hands = []

    def set_in_play(self, value):  #F Is this needed, or delete?
        self.in_play = value

    def get_turn(self):
        """Returns the hand which is currently in play, or None."""
        return self.turn_hand

    def set_next_turn(self):
        """Rotates the hand whose turn it is, sequentially through each of a player's hand, then through each player, finally to the dealer's hand."""
        if not self.turn_hand:
            self.turn_hand = self.game.player.hands[0]
            self.turn_owner = self.turn_hand.owner
            return self.turn_owner, self.turn_hand, self.dealer
        else:
            all_hands = []
            for hand in self.game.player.hands:
                all_hands.append(hand)
            all_hands.append(self.game.dealer.hands[0])

            switch = False
            for hand in all_hands:
                if switch:
                    self.turn_hand = hand
                    self.turn_owner = hand.owner
                    anybody_still_need_evaled = False
                    for i in self.game.player.hands:
                        if not i.winresult:
                            anybody_still_need_evaled = True
                    if hand.owner == self.dealer and not anybody_still_need_evaled:
                        self.turn_owner = None
                        self.turn_hand = None
                        self.in_play = False  ###F needed or delete?
                        break
                    break

                if hand == self.turn_hand:
                    switch = True
                    if hand.owner == self.dealer:
                        self.turn_owner = None
                        self.turn_hand = None
                        self.in_play = False  ###F needed or delete?
                        break
            return self.in_play


class Game:

    def __init__(self):
        self.dealer = None
        self.player = None
        self.shoe = None
        self.round = None

    # def get_game(self):   #F Needed, or delete?
    #     return self

    def init_new_round(self):
        this_round = Round(self)
        self.round = this_round
        return this_round

    def init_new_shoe(self, decks):
        shoe = Shoe(decks)
        self.shoe = shoe
        return shoe

    def init_dealer(self):
        dealer = Dealer()
        self.dealer = dealer
        return dealer

    def init_player(self, name):
        player = Player(name)
        self.player = player
        return player

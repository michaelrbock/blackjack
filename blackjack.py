import random
import sys


STARTING_CHIPS = 100


class Card(object):
    number_to_name = {1: 'A', 11: 'J', 12: 'Q', 13: 'K'}

    def __init__(self, number, suit):
        self.number = number
        self.suit = suit
        self.name = (self.number_to_name[number] if number in self.number_to_name else str(number))
        self.value = min(number, 10)
        self.display = []
        self.generate_display()

    def generate_display(self):
        self.display.append(' ' + ('_' * 9) + ' ')
        self.display.append('/' + (' ' * 9) + '\\')
        self.display.append('|' + self.name + (' ' * (7 if self.name == '10' else 8)) + '|')
        if self.suit == 'Spades':
            self.display.append('|' + (' ' * 4) + ',' + (' ' * 4) + '|')
            self.display.append('|   / \\   |')
            self.display.append('|  (_ _)  |')
            self.display.append('|   /_\\   |')
            self.display.append('|' + (' ' * 9) +'|')
        elif self.suit == 'Hearts':
            self.display.append('|   _ _   |')
            self.display.append('|  / ^ \\  |')
            self.display.append('|  \\   /  |')
            self.display.append('|   \\ /   |')
            self.display.append('|    `    |')
        elif self.suit == 'Clubs':
            self.display.append('|    _    |')
            self.display.append('|   (_)   |')
            self.display.append('|  (_)_)  |')
            self.display.append('|   /_\\   |')
            self.display.append('|' + (' ' * 9) +'|')
        elif self.suit == 'Diamonds':
            self.display.append('|' + (' ' * 9) +'|')
            self.display.append('|    /\\   |')
            self.display.append('|   <  >  |')
            self.display.append('|    \\/   |')
            self.display.append('|' + (' ' * 9) +'|')
        self.display.append('|' + (' ' * (7 if self.name == '10' else 8)) + self.name + '|')
        self.display.append('\\' + ('_' * 9) +'/')


class Hand(object):
    HIDDEN_CARD = [(' ' + ('_' * 9) + ' '),
                   ('/' + (' ' * 9) + '\\'),
                   ('|X' + (' ' * 8) + '|'),
                   ('|         |'),
                   ('|         |'),
                   ('|         |'),
                   ('|         |'),
                   ('|         |'),
                   ('|' + (' ' * 8) + 'X|'),
                   ('\\' + ('_' * 9) +'/')]

    def __init__(self, cards):
        self.hand = cards

    def all_scores(self):
        number_of_aces = sum(card.name == 'A' for card in self.hand)
        score = sum(card.value for card in self.hand)
        return [(score + (i * 10)) for i in xrange(number_of_aces + 1)]

    def possible_scores(self):
        return [score for score in self.all_scores() if score <= 21]

    def add_card(self, card):
        self.hand.append(card)

    def print_hand(self, hide_first_card=False):
        for row in xrange(10):
            for idx, card in enumerate(self.hand):
                if hide_first_card and idx == 0:
                    sys.stdout.write(self.HIDDEN_CARD[row])
                else:
                    sys.stdout.write(card.display[row])
                sys.stdout.write('  ')
            print '' # newline
        print ''


class Deck(object):
    unshuffled_deck = [
        Card(num, suit) for num in xrange(1, 14) for suit in 
        ['Spades', 'Hearts', 'Clubs', 'Diamonds']
    ]

    def __init__(self, number_of_decks=1):
        self.deck = self.unshuffled_deck * number_of_decks
        random.shuffle(self.deck)

    def deal_card(self):
        return self.deck.pop()

    def deal_hand(self):
        return Hand([self.deal_card(), self.deal_card()])


class Player(object):
    def __init__(self, name='You', chips=STARTING_CHIPS):
        self.name = name
        self.chips = chips
        self.bet = 0
        self.hand = None
        self.stand = False

    def reset(self):
        self.bet = 0
        self.hand = None
        self.stand = False

    def lose(self, loss):
        self.chips -= loss

    def win(self, winnings):
        self.chips += winnings

    def hit(self, card):
        self.hand.add_card(card)

    def is_bust(self):
        return len(self.hand.possible_scores()) == 0

    def scores(self):
        return self.hand.all_scores() if self.is_bust() else self.hand.possible_scores()

    def max_score(self):
        return max(self.scores())

    def min_score(self):
        return min(self.scores())


class Game(object):
    def __init__(self):
        self.dealer = Player(name='Dealer')
        self.player = Player()
        self.deck = Deck()

    def print_table(self, hide_dealer_card=True):
        print '==================\n'
        print 'Dealer: %s' % ('' if hide_dealer_card else (str(self.dealer.max_score())
            if self.dealer.max_score() <= 21 else str(self.dealer.min_score())))
        self.dealer.hand.print_hand(hide_first_card=hide_dealer_card)
        print 'You: %d' % (self.player.max_score() if self.player.max_score() <= 21 
            else self.player.min_score())
        self.player.hand.print_hand()

    def set_up(self):
        self.deck = Deck()
        self.dealer.reset()
        self.player.reset()

    def get_player_bet(self):
        while True:
            bet_input = raw_input("Enter bet for this hand (or 'exit' to quit): ").strip().lower()
            if bet_input == 'exit':
                print 'Thanks for playing :)'
                sys.exit(0)
            if not bet_input.isdigit():
                print 'Input Error! Please try again.'
            elif int(bet_input) > self.player.chips:
                print 'You do not have enough chips! Please try again.'
            else:
                return int(bet_input)

    def deal_and_print_initial_hands(self):
        self.dealer.hand = self.deck.deal_hand()
        self.player.hand = self.deck.deal_hand()
        self.print_table()

    def blackjack_check(self):
        if self.player.max_score() == 21 and self.dealer.max_score() == 21:
            self.print_table(hide_dealer_card=False)
            print 'You PUSH!'
            print 'You keep your %d chips.' % self.player.bet
            return True
        elif self.player.max_score() == 21:
            print 'BLACKJACK! You win %d chips!' % (self.player.bet * 1.5)
            self.player.win(self.player.bet * 1.5)
            return True
        return False

    def player_choices(self):
        print ''
        while not self.player.stand and not self.player.is_bust():
            correct_input = False
            while not correct_input:
                hit_or_stand = raw_input("Enter 'hit' or 'stand': ").strip().lower()
                if (hit_or_stand != 'hit' and hit_or_stand != 'stand' and
                    hit_or_stand != 'h' and hit_or_stand != 's'):
                    print 'Input Error! Please try again.'
                else:
                    correct_input = True
            if hit_or_stand == 'hit' or hit_or_stand == 'h':
                # Hit and re-print table
                self.player.hit(self.deck.deal_card())
                self.print_table()
            elif hit_or_stand == 'stand' or hit_or_stand == 's':
                self.player.stand = True

    def check_player_bust(self):
        if self.player.is_bust():
            self.player.stand = True
            print 'You BUST!'
            print 'You lose %d chips.\n' % self.player.bet
            self.player.lose(self.player.bet)

    def dealer_choices(self):
        if not self.player.is_bust():
            self.print_table(hide_dealer_card=False)
            while self.dealer.max_score() < 17:
                self.dealer.hit(self.deck.deal_card())
                self.print_table(hide_dealer_card=False)

    def final_outcome(self):
        if not self.player.is_bust():
            if self.dealer.is_bust():
                print 'Dealer BUST!'
                print 'You win %d chips.\n' % self.player.bet
                self.player.win(self.player.bet)
            elif self.player.max_score() == self.dealer.max_score():
                print 'You PUSH!'
                print 'You keep your bet of %d chip.\n' % self.player.bet
            elif self.player.max_score() > self.dealer.max_score():
                print 'You WIN!'
                print 'You win %d chips.\n' % self.player.bet
                self.player.win(self.player.bet)
            elif self.player.max_score() < self.dealer.max_score():
                print 'You LOSE!'
                print 'You lose %d chips.\n' % self.player.bet
                self.player.lose(self.player.bet)

    def play(self):
        print 'Welcome to Blackjack!'

        while self.player.chips > 0:
            # 1: Set up
            self.set_up()
            print 'You have %d chips remaining' % self.player.chips
            
            # 2: Get player's bet
            self.player.bet = self.get_player_bet()

            self.deal_and_print_initial_hands()

            # 3: Check for blackjacks
            if self.blackjack_check():
                continue

            # 4: Ask user hit or stand until stand/bust
            self.player_choices()

            # 5: print display again
            self.print_table()

            # 6: Check if player bust
            self.check_player_bust()

            # 7: Once stand, reveal dealer card, dealer logic
            self.dealer_choices()

            # 8: Check for final outcome
            self.final_outcome()

            print '===================================='

        print 'You are out of money!'
        print 'Game over :('

if __name__ == '__main__':
    game = Game()
    game.play()

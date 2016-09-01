from Cards import create_deck, shuffle_deck, deal_card, deal_cards, card_as_str
from itertools import product
from collections import namedtuple

def prompt(text):
    '''Prompt the user, and if the answer is Y or y return True, False otherwise'''
    answer = input(text)
    if answer.lower() == 'y':
        return True
    else:
        return False

def get_hand_values(hand):
    '''Given a hand of cards, calculate all possible values for the cards'''
    card_values = [get_value(x) for x in hand]
    all_possible_values = [sum(x) for x in product(*card_values)]
    return all_possible_values

def get_value(card):
    '''Get the value of a card'''
    (rank, suit) = card
    return get_values_of_rank(rank)

def make_lookup_table():
    '''Create a lookup table to get the value of a rank, then return a lambda to call that table'''
    table = dict((str(x),[int(x)]) for x in range(2,11))
    for face_card in ['Jack', 'Queen', 'King']:
        table[face_card] = [10]
    table['Ace'] = [1,11]
    return lambda rank: table[rank]

get_values_of_rank = make_lookup_table()
    
def hand_as_str(hand, is_dealer):
    '''Output a string representation of the hand'''
    if not is_dealer:
        value = get_hand_value(hand)
        return 'Hand: {0} ({1})'.format(', '.join((card_as_str(c) for c in hand)), value)
    else:
        return 'Dealer: {0}'.format(', '.join([card_as_str(hand[0])] + ['Card' for _ in hand[1:2]] + [card_as_str(x) for x in hand[2:]]))

def display_players(players):
    '''Display the player's hand and one of the dealers cards'''
    print(hand_as_str(players[0], True))
    for player in players[1:]:
        print(hand_as_str(player, False))

def hit(hand, deck, discard):
    (card, new_deck, new_discard) = deal_card(deck, discard)
    return (hand + [card], deck, discard)
    
def get_hand_value(hand, default_value = None):
    '''Get the maximum value of the hand that is under 21'''
    hand_values = get_hand_values(hand)
    cards_under_21 = filter(lambda x: x < 22, hand_values)
    valid_values = [x for x in cards_under_21]
    if any(valid_values):
        return max(valid_values)
    else:
        return default_value

def make_bet(credits, default_bet):
    try:
        prompt = 'What would you like to bet? ({0} credits, default {1}) '.format(credits, default_bet)
        bet = int(input(prompt))
        if credits < default_bet:
            print('Not enough money to bet.')
            return (credits, 0)

        if bet <= credits:
            if bet >= default_bet:
                return (credits - bet, bet)
            else:
                print('Bet must be greater than the minimum bet.')
                return make_bet(credits, default_bet)
        else:
            print('Cannot bet more money than you have.')
            return make_bet(credits, default_bet)
    except:
        return (credits - default_bet, default_bet)
    
def dealer_turn(hand, deck, discard):
    '''Dealer hits on 16 or lower'''
    hand_value = get_hand_value(hand)
    while hand_value != None and hand_value < 17:
        print('Dealer is hitting...')
        (hand, deck, discard) = hit(hand, deck, discard)
        print(hand_as_str(hand, True))
        hand_value = get_hand_value(hand)
    return (hand, deck, discard)

def resolve_hand(hand, deck, discard):
    while prompt('Hit? (y/n) '):
        (hand, deck, discard) = hit(hand, deck, discard)
        if get_hand_value(hand) == None:
            print('Busted')
            break
        print(hand_as_str(hand, False))
    return (hand, deck, discard)


def player_turn(player, dealer, deck, discard, minimum_bet):
    '''Player chooses how much to bet, and if they want to hit'''
    # Players can have 1-2 hands if the cards are the same
    # * (Unless it's double aces, in which case they only get +1 card each hand)
    # Players can get insurance if the dealer has an Ace
    # Players can double down, but I forgot how
    (name, credits) = player
    (credits, bet) = make_bet(credits, minimum_bet)
    (hand, deck, discard) = deal_cards(deck, discard, 2)
    print(hand_as_str(dealer, False))
    ((rank1, _), (rank2, _)) = hand
    if rank1 == rank2 and prompt('Would you like to split? (y/n) '):
        card1, card2 = hand
        hand1, hand2 = [card1], [card2]
        (credits, bet2) = make_bet(credits, bet)

        print(hand_as_str(hand1, False))
        (hand1, deck, discard) = resolve_hand(hand1, deck, discard)
        print(hand_as_str(hand2, False))
        (hand2, deck, discard) = resolve_hand(hand2, deck, discard)
        return (player, [(hand1, bet), (hand2, bet2)], deck, discard)
    else:
        display_players([dealer, hand])
        resolve_hand(hand, deck, discard)
        player = (name, credits)
        return (player, [(hand, bet)], deck, discard)

def play_round(player, deck, discard, minimum_bet):
    name, credits = player
    (dealer, deck, discard) = deal_cards(deck, discard, 2)
    (player, hands, deck, discard) = player_turn(player, dealer, deck, discard, minimum_bet)
    max_hand_values = [get_hand_value(hand) for (hand, _) in hands]

    # Dealer
    if any([max_hand_value for max_hand_value in max_hand_values if max_hand_value != None]):
        (dealer, deck, discard) = dealer_turn(dealer, deck, discard)
    max_dealer_hand_value = get_hand_value(dealer)

    fancy_template = '--==(({0}))==--'
    print(fancy_template.format('Dealer'))
    print(hand_as_str(dealer, False))
    print(fancy_template.format(name))
    for (hand, bet) in hands:
        print('{0} ({1} credits)'.format(hand_as_str(hand, False), bet))
        max_hand_value = get_hand_value(hand)
        if max_hand_value == None:
            print('You busted.')
            credits = credits - bet
        elif max_dealer_hand_value == None:
            print('Dealer has busted. You win!')
            credits = credits + bet
        elif max_hand_value > max_dealer_hand_value:
            print('You won! {0} vs. {1}'.format(max_hand_value, max_dealer_hand_value))
            credits = credits + bet
        else:
            print('You lose! {0} vs. {1}'.format(max_hand_value, max_dealer_hand_value))
            credits = credits - bet
    print('Player: {0}, Credits Remaining: {1}'.format(name, credits))
    discard = discard + dealer + [card for card in [hand for (hand, bet) in hands]]
    return ((name, credits), deck, discard)

def play_blackjack():
    (state, deck) = shuffle_deck(create_deck(False))
    name = input('Please enter your name: ')
    credits = 100
    player = (name, credits)
    minimum_bet = 5
    discard = []
    while credits > minimum_bet:
        (player, deck, discard) = play_round(player, deck, discard, minimum_bet)
        _, credits = player

play_blackjack()

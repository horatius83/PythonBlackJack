from random import shuffle, seed, getstate
from itertools import product

def deal_card(deck, discard):
    try:
        return (deck.pop(), deck, discard)
    except:
        (_, deck) = shuffle_deck(discard)
        discard = []
        return (deck.pop(), deck, discard)

def deal_cards(deck, discard, n_cards):
    cards = []
    while n_cards > 0:
        (card, deck, discard) = deal_card(deck, discard)
        cards.append(card)
        n_cards = n_cards - 1
    return (cards, deck, discard)

def create_deck(hasJoker):
    '''bool -> [(str, str) | str]'''
    ranks = [str(x) for x in range(2,11)] + ['Jack', 'Queen', 'King', 'Ace']
    suits = ['Hearts', 'Diamonds', 'Clubs', 'Spades']
    cards = [(rank, suit) for rank in ranks for suit in suits]
    if not hasJoker:
        return cards
    else:
        return cards + ['Joker', 'Joker']

def shuffle_deck(deck):
    '''[a] -> (state, [a])'''
    new_deck = deck[:]
    shuffle(new_deck)
    return (getstate(), new_deck)

def card_as_str(card):
    try:
        (rank, suit) = card
        return '{0} of {1}'.format(rank, suit)
    except:
        if card is 'Joker':
            return card
        else:
            raise Exception('Card "{0}" is invalid'.format(card))


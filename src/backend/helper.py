import random

from typing import Optional

from lib import Board, Direction
from lib.scraper import get_letters_and_words

# # Get words from wordbench
# words = get_letters_and_words()[1]
# print(words)

# Hardcoded word list
# words = ['foreign', 'finger', 'ignore', 'region', 'grief', 'fine', 'fire', 'grin', 'iron', 'ring', 'ego', 'fog', 'for', 'nor', 'one']

def generate_board(seed: str) -> (Board, str):
    # words = ['eat', 'era', 'hat', 'tea', 'bare', 'bet', 'bat', 'art', 'beat', 'tree', 'here', 'herb', 'beer', 'bear', 'rate', 'the', 'rat', 'her', 'ear', 'bee', 'earth', 'there', 'tear', 'three', 'heat', 'breathe', 'breath', 'heart', 'hear', 'hate', 'bath', 'bar']
    words = ['norm', 'normal', 'normalise', 'normalised', 'side', 'lid', 'nail', 'mail', 'male', 'said', 'ram', 'lie', 'die', 'mile', 'sale', 'sail']

    board = Board(20, 20)
    random.seed(seed)

    first_word = "candle"
    direction = random.choice([Direction.ACROSS, Direction.DOWN])
    if direction == Direction.ACROSS:
        x = int(board.width / 2 - len(first_word) / 2)
        y = int(board.height / 2)
        board.place_word(first_word, x, y, direction)
    else:
        x = int(board.width / 2)
        y = int(board.height / 2 - len(first_word) / 2)
        board.place_word(first_word, x, y, direction)

    board.generate(words)
    # board.letters = ['b', 'r', 'e', 'a', 't', 'h', 'e']
    board.letters = ['n', 'o', 'r', 'm', 'a', 'l', 'i', 's', 'e', 'd']
    board.shrink()
    return board
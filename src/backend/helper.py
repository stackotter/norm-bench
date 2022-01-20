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
    words = ['eat', 'era', 'hat', 'tea', 'bare', 'bet', 'bat', 'art', 'beat', 'tree', 'here', 'herb', 'beer', 'bear', 'rate', 'the', 'rat', 'her', 'ear', 'bee', 'earth', 'there', 'tear', 'three', 'heat', 'breathe', 'breath', 'heart', 'hear', 'hate', 'bath', 'bar']

    board = Board(20, 20)
    if seed != "norm":
        random.seed(seed)

        board.generate(words)
        board.letters = ['b', 'r', 'e', 'a', 't', 'h', 'e']
        board.shrink()
        return board
    else:
        board.letters = ['n', 'o', 'r', 'm', 'a', 'l', 'i', 's', 'e', 'd']
        board.place_word('normalised', 10, 2, Direction.DOWN)
        board.place_word('side', 5, 3, Direction.ACROSS)
        board.place_word('sine', 5, 3, Direction.DOWN)
        board.place_word('lines', 3, 5, Direction.ACROSS)
        board.place_word('linear', 3, 5, Direction.DOWN)
        board.place_word('norm', 1, 10, Direction.ACROSS)
        board.place_word('nose', 1, 10, Direction.DOWN)
        board.place_word('learn', 0, 13, Direction.ACROSS)
        board.place_word('main', 4, 10, Direction.DOWN)
        board.place_word('sea', 7, 5, Direction.DOWN)
        board.place_word('candle', 6, 7, Direction.ACROSS)
        board.place_word('normal', 8, 7, Direction.DOWN)
        board.place_word('land', 7, 11, Direction.ACROSS)
        board.place_word('one', 1, 8, Direction.ACROSS)
        board.place_word('ear', 10, 10, Direction.ACROSS)
        board.place_word('red', 12, 10, Direction.DOWN)
        board.place_word('sir', 6, 9, Direction.ACROSS)
        board.place_word('mod', 7, 1, Direction.DOWN)
        board.place_word('men', 7, 1, Direction.ACROSS)
        board.place_word('no', 9, 1, Direction.DOWN)
        board.place_word('on', 9, 2, Direction.ACROSS)
        board.shrink()
        return board
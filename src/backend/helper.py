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

    board = Board(14, 14)
    random.seed(seed)
    board.generate(words)
    board.letters = ['b', 'r', 'e', 'a', 't', 'h', 'e']
    board.shrink()
    return board
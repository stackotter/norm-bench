import random

from typing import Optional

from lib import Board, Direction
from lib.word_list import WordList

def generate_board(seed: str, word_list: WordList) -> (Board, str):
    board = Board(20, 20)
    if seed != "norm":
        random.seed(seed)

        words = word_list.choose_normbench_words(7)
        
        board.generate(words)
        board.letters = [char for char in words[0]]
        board.shrink()
        return board
    else:
        board = Board(13, 14)
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
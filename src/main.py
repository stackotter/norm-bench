from random import randint, choice, shuffle

from lib.board import Board, Direction
from lib.scraper import get_letters_and_words

# # Get words from wordbench
# words = get_letters_and_words()[1]
# print(words)

# Hardcoded word list
# words = ['foreign', 'finger', 'ignore', 'region', 'grief', 'fine', 'fire', 'grin', 'iron', 'ring', 'ego', 'fog', 'for', 'nor', 'one']
words = ['eat', 'era', 'hat', 'tea', 'bare', 'bet', 'bat', 'art', 'beat', 'tree', 'here', 'herb', 'beer', 'bear', 'rate', 'the', 'rat', 'her', 'ear', 'bee', 'earth', 'there', 'tear', 'three', 'heat', 'breathe', 'breath', 'heart', 'hear', 'hate', 'bath', 'bar']
words = list(reversed(sorted(words, key=len)))

# The seed word
first_word = words.pop(0)

# Sort the words by size
buckets: dict[int, list[str]] = {}
for word in words:
    length = int(len(word) / 2)
    if length in buckets.keys():
        buckets[length].append(word)
    else:
        buckets[length] = [word]

# Create an empty board
board = Board(20, 20)

x = int(board.width / 2 - len(first_word) / 2)
y = int(board.height / 2)
direction = Direction.ACROSS
board.place_word(first_word, x, y, direction)

discarded_words: list[str] = []

unused_words: list[str] = []
for bucket in buckets.values():
    shuffle(bucket)

    for word in unused_words:
        board.try_place(word)

    discarded_words.extend(unused_words)
    unused_words = []

    for word in bucket:
        if not board.try_place(word):
            unused_words.append(word)

for word in unused_words:
    board.try_place(word)

for word in discarded_words:
    board.try_place(word)

board.print()

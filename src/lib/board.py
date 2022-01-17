import sys

from typing import Tuple
from enum import Enum
from random import shuffle

class Direction(Enum):
    DOWN = 0
    ACROSS = 1

class Board:
    width: int
    height: int
    rows: list[list[str]]
    words: list[Tuple[int, int, Direction, str]]

    def __init__(self, width, height):
        self.rows = []
        for i in range(height):
            row = []
            for i in range(width):
                row.append(" ")
            self.rows.append(row)

        self.width = width
        self.height = height
        self.words = []

    def print(self):
        for row in self.rows:
            print(" ".join(row))
        

    def cell(self, x: int, y: int) -> str:
        """Gets the current value of a board cell. Returns just a space if the coordinates are outside the board."""

        if x < 0 or y < 0 or x >= self.width or y >= self.height:
            return " "
        return self.rows[y][x]

    def set_cell(self, x: int, y: int, value: str):
        """Sets the value of a board cell. Does nothing if the coordinates are ouside the board."""

        if x >= 0 and y >= 0 and x < self.width and y < self.height:
            self.rows[y][x] = value

    def place_word(self, word: str, x: int, y: int, direction: Direction):
        if direction == Direction.ACROSS:
            for i in range(len(word)):
                self.set_cell(x + i, y, word[i])
        else:
            for i in range(len(word)):
                self.set_cell(x, y + i, word[i])
        self.words.append((x, y, direction, word))

    def can_place_word(self, word: str, x: int, y: int, direction: Direction) -> bool:
        is_connected = False

        # Across
        if direction == Direction.ACROSS:
            startX = x
            endX = startX + len(word) - 1

            if startX < 0 or endX >= self.width:
                return False

            if self.cell(startX - 1, y) != " ":
                return False
            if self.cell(endX + 1, y) != " ":
                return False

            for i in range(len(word)):
                currentX = startX + i
                value = self.cell(currentX, y)

                if value == word[i] and (self.cell(currentX, y - 1) != " " or self.cell(currentX, y + 1) != " "):
                    is_connected = True
                    continue
                elif value == " " and self.cell(currentX, y + 1) == " " and self.cell(currentX, y - 1) == " ":
                    continue
                return False
                
        # Down
        else:
            startY = y
            endY = startY + len(word) - 1

            if endY >= self.height:
                return False

            if self.cell(x, startY - 1) != " ":
                return False
            if self.cell(x, endY + 1) != " ":
                return False

            for i in range(len(word)):
                currentY = startY + i
                value = self.cell(x, currentY)
                
                if value == word[i] and (self.cell(x - 1, currentY) != " " or self.cell(x + 1, currentY) != " "):
                    is_connected = True
                    continue
                elif value == " " and self.cell(x + 1, currentY) == " " and self.cell(x - 1, currentY) == " ":
                    continue
                return False
        
        return is_connected

    def try_place(self, word: str) -> bool:
        """Attempts to place a word into the crossword, returns True if it succeeds to place the word."""

        placed_words = self.words
        shuffle(placed_words)
        # placed_words = sorted(placed_words, key=lambda x: int(len(x)/4))
        for (placed_x, placed_y, placed_direction, placed_word) in placed_words:
            print("Trying to place %s on %s" % (word, placed_word))
            # Find all locations that letters match between the two words
            locations: dict[str, list[int]] = {}
            unique_letters = set(placed_word)
            for letter in unique_letters:
                for (i, char) in enumerate(word):
                    if char == letter:
                        if char in locations.keys():
                            locations[char].append(i)
                        else:
                            locations[char] = [i]
        
            # Check all combinations
            for (offset, letter) in enumerate(placed_word):
                if not letter in locations.keys():
                    continue
                indices = locations[letter]
                shuffle(indices)
                for index in indices:
                    # Attempt to place the word
                    if placed_direction == Direction.ACROSS:
                        x = placed_x + offset
                        y = placed_y - index
                        if self.can_place_word(word, x, y, Direction.DOWN):
                            self.place_word(word, x, y, Direction.DOWN)
                            print("Placed %s" % word)
                            return True
                    if placed_direction == Direction.DOWN:
                        x = placed_x - index
                        y = placed_y + offset
                        if self.can_place_word(word, x, y, Direction.ACROSS):
                            self.place_word(word, x, y, Direction.ACROSS)
                            print("Placed %s" % word)
                            return True
        return False

    
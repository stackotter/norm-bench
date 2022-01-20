import sys

from typing import Tuple
from enum import Enum
from random import shuffle, choice

class Direction(Enum):
    DOWN = "down"
    ACROSS = "across"

class Board:
    width: int
    height: int
    rows: list[list[str]]
    words: list[Tuple[int, int, Direction, str]]
    letters: list[str]

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
        self.letters = []

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

            if startY < 0 or endY >= self.height:
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
                            return True
                    if placed_direction == Direction.DOWN:
                        x = placed_x - index
                        y = placed_y + offset
                        if self.can_place_word(word, x, y, Direction.ACROSS):
                            self.place_word(word, x, y, Direction.ACROSS)
                            return True
        return False

    def generate(self, words: list[str]):
        """Adds a list of words into the cross word"""

        # Sort by length in descending order (attempt to place bigger words first)
        words = list(reversed(sorted(words, key=len)))

        # Place a seed word if the board is currently empty
        if len(self.words) == 0:
            first_word = words.pop(0)

            direction = choice([Direction.ACROSS, Direction.DOWN])
            if direction == Direction.ACROSS:
                x = int(self.width / 2 - len(first_word) / 2)
                y = int(self.height / 2)
                self.place_word(first_word, x, y, direction)
            else:
                x = int(self.width / 2)
                y = int(self.height / 2 - len(first_word) / 2)
                self.place_word(first_word, x, y, direction)

        # Sort the words by size (each bucket has two sizes of words to make it a bit more interesting)
        buckets: dict[int, list[str]] = {}
        for word in words:
            length = int(len(word) / 2)
            if length in buckets.keys():
                buckets[length].append(word)
            else:
                buckets[length] = [word]

        # Each word gets retried twice at different stages. Once in the round after it was first tried, and once at the end when all words have been placed or attempted twice.
        discarded_words: list[str] = []
        unused_words: list[str] = []
        for bucket in buckets.values():
            # Add an element of random to create more varied puzzles
            shuffle(bucket)

            last_bucket_unused_words = unused_words
            unused_words = []

            # Attempt to place all words in the current bucket
            for word in bucket:
                if not self.try_place(word):
                    unused_words.append(word)

            # Attempt to place all words that could not be placed from the previous bucket
            for word in last_bucket_unused_words:
                if self.try_place(word):
                    last_bucket_unused_words.remove(word)

            # Save any words that still haven't been placed to be attempted once more right at the end
            discarded_words.extend(last_bucket_unused_words)

        # Try to place all words from the final round again
        for word in unused_words:
            self.try_place(word)

        # Give all remaining words a final chance
        for word in discarded_words:
            self.try_place(word)

    def shrink(self):
        """Shrinks the board to fit the words it contains"""

        # Remove empty rows and find empty columns
        leftmost_column = None
        rightmost_column = None
        first_row_index = None
        removed_row_count = 0
        for (i, row) in enumerate(self.rows):
            contains_letter = False
            for cell in row:
                if cell != " ":
                    contains_letter = True
                    break
            if not contains_letter:
                self.rows.pop(i - removed_row_count)
                removed_row_count += 1
            else:
                if first_row_index == None:
                    first_row_index = i
                has_found_first_column = False
                for (i, cell) in enumerate(row):
                    if cell != " ":
                        if not has_found_first_column and (leftmost_column == None or leftmost_column > i):
                            has_found_first_column = True
                            leftmost_column = i
                        if rightmost_column == None or rightmost_column < i:
                            rightmost_column = i

        # Adjust the y coordinate of all words accordingly
        if first_row_index != None and first_row_index != 0:
            for i in range(len(self.words)):
                word = list(self.words[i])
                word[1] -= first_row_index
                self.words[i] = tuple(word)

        # Adjust the x coordinate of all words accordingly
        if leftmost_column != None and leftmost_column != 0:
            for i in range(len(self.words)):
                word = list(self.words[i])
                word[0] -= leftmost_column
                self.words[i] = tuple(word)
        
        # Adjust the dimensions of the board accordingly
        self.height = len(self.rows)
        self.width = rightmost_column - leftmost_column + 1

        # Remove empty columns
        for row in self.rows:
            for i in range(len(row)):
                if i < leftmost_column:
                    row.pop(0)
                elif i > rightmost_column:
                    row.pop(rightmost_column - leftmost_column)
                            



    
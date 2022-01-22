import random

from dataclasses import dataclass
from itertools import combinations

@dataclass
class WordList:
    words: list[str]
    
    @classmethod
    def from_file(cls, file_name: str) -> 'WordList':
        """Loads an Aspell word list."""

        with open(file_name, 'r') as f:
            print("Loading word list from %s" % file_name)
            words = [line.strip().lower() for line in f.readlines()]

            print("Removing annotations")
            # Remove any annotations from the wordlist
            for (i, word) in enumerate(words):
                if not word[-1].isalpha():
                    words[i] = word[:-1]
            
            print("Finished loading wordlist")
            return WordList(words)

    def apply_exclude_list(self, exclude_list_file: str):
        """Removes all words and plurals of words that appear in the given exclude list from the word list."""

        print("Loading exclude list from %s" % exclude_list_file)
        words_to_remove: list[str] = []
        with open(exclude_list_file, 'r') as f:
            words_to_remove = [line.strip().lower() for line in f.readlines()]

        print("Removing excluded words")
        initial_length = len(self.words)
        for (i, word) in enumerate(reversed(self.words)):
            if word in words_to_remove:
                self.words.pop(initial_length - i - 1)
            # Remove plurals
            elif word[-1] == "s" and str(word[:-1]) in words_to_remove:
                self.words.pop(initial_length - i - 1)

    def save(self, file_name: str):
        """Saves the wordlist to a file"""

        with open(file_name, 'w') as f:
            f.write("\n".join(self.words))

    def choose_normbench_words(self, letter_count: int) -> list[str]:
        """Chooses a random 7 letter word and finds all anagrams. Returns a list containing the word and its anagrams. The word is always first in the list"""

        offset = ord('a')
        primes: list[int] = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101]

        def prime_product(word: str) -> int:
            """Calculates the product of a word's letters where each letter has a prime number value. Useful for finding anagrams."""

            product = 1
            for letter in word:
                prime = primes[ord(letter) - offset]
                product *= prime
            return product
        
        n_letter_words = list(filter(lambda word: len(word) == letter_count, self.words))
        smaller_words = list(filter(lambda word: len(word) < letter_count, self.words))

        seed_word = random.choice(n_letter_words)
        seed_word_product = prime_product(seed_word)

        anagrams: list[str] = [seed_word]

        # Find all n letter anagrams
        for word in n_letter_words:
            product = prime_product(word)
            if product == seed_word_product and word != seed_word:
                anagrams.append(word)

        # Find all anagrams with less than n letters
        for word in smaller_words:
            product = prime_product(word)
            if len(word) > 3 and (seed_word_product / product).is_integer():
                anagrams.append(word)

        # Remove either the word or its plural if both appear
        for word in anagrams:
            if not word.endswith("s") and word + "s" in anagrams:
                if word + "s" == seed_word:
                    anagrams.remove(word)
                elif random.choice([True, False]):
                    anagrams.remove(word)
                else:
                    anagrams.remove(word + "s")
        
        return anagrams


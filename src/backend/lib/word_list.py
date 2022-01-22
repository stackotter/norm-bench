import random

from dataclasses import dataclass

@dataclass
class WordList:
    words: list[str]
    
    @classmethod
    def from_file(cls, file_name: str) -> 'WordList':
        """Loads an Aspell word list."""

        with open(file_name, 'r') as f:
            words = [line.strip().lower() for line in f.readlines()]

            # Remove any annotations from the wordlist
            for (i, word) in enumerate(words):
                if not word[-1].isalpha():
                    words[i] = word[:-1]

            return WordList(words)

    def apply_exclude_list(self, exclude_list_file: str):
        """Removes all words and plurals of words that appear in the given exclude list from the word list."""

        words_to_remove: list[str] = []
        with open(exclude_list_file, 'r') as f:
            words_to_remove = [line.strip().lower() for line in f.readlines()]
        
        # Some words in the offensive wordlist may be missing plurals. Here is a quick solution to that
        for word in words_to_remove:
            words_to_remove.append(word + "s")

        num_removed = 0
        for (i, word) in enumerate(self.words):
            if word in words_to_remove:
                self.words.pop(i - num_removed)

    def choose_normbench_letters(self, letter_count: int, seed: str):
        offset = ord('a')
        primes: list[int] = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101]

        def prime_product(word: str) -> int:
            """Calculates the product of a word's letters where each letter has a prime number value. Useful for finding anagrams."""

            product = 1
            for letter in seed_word:
                prime = primes[ord(letter) - offset]
                product *= prime
            return product
        
        n_letter_words = filter(lambda word: len(word) == letter_count, self.words)
        smaller_words = filter(lambda word: len(word) < letter_count, self.words)

        seed_word = random.choice(n_letter_words)
        seed_word_product = prime_product(seed_word)

        anagrams: list[str] = []

        # Find all n letter anagrams
        for word in n_letter_words:
            product = 1
            for letter in word:
                prime = primes[ord(letter) - offset]
                product *= prime
            if product == seed_word_product:
                anagrams.append(word)

        print(anagrams)


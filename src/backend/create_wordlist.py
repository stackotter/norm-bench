import uuid

from lib.word_list import WordList

word_list = WordList.from_file("word_lists/3of6game.txt")
word_list.apply_exclude_list("word_lists/offensive_words.txt")
word_list.save("word_lists/norm_bench.txt")

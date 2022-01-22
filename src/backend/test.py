import uuid

from lib.word_list import WordList

word_list = WordList.from_file("word_lists/norm_bench.txt")

word_list.choose_normbench_letters(7, uuid.uuid4().hex)
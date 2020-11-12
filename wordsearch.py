#! /usr/bin/env python3
# CLI Arguments
from sys import argv
from getopt import getopt, GetoptError

from string import ascii_lowercase
from typing import TYPE_CHECKING

from trie import Trie


if TYPE_CHECKING:
    from typing import Dict, List


WINDOW_SIZE = 500  # type: int
MAX_WORD_LENGTH = 24  # type: int


class WordSearch(object):

    def __init__(self, grid: str, axis_length: int = ROW_LENGTH, window_size: int = WINDOW_SIZE, max_word: int = MAX_WORD_LENGTH) -> None:
        self._cache = {}  # type: Dict[str, bool]
        self._trie = Trie(grid, axis_length, window_size, max_word)  # type: Trie

    def is_present(self, word: str) -> bool:
        """ Checks if word is present in grid. """
        if word not in self._cache:
            self._cache[word] = word in self._trie

        return self._cache[word]


def read_grid(path: str) -> str:
    """ Read grid from file. """
    grid = ''  # type: str
    with open(path, "r") as file:
        for line in file:
            grid += ''.join(filter(lambda x: x in ascii_lowercase, line))

    return grid


def read_words(path: str) -> 'List[str]':
    """ Read words from file. """
    words = []  # type: List[str]

    with open(path, "r") as file:
        for line in file:
            words.append(line.strip())

    return words


if __name__ == "__main__":
    try:
        options, args = getopt(argv[1:], 'h', ['grid=', 'words='])
    except GetoptError as e:
        raise RuntimeError from e
    if len(options) == 0:
        raise RuntimeError
    for option, argument in options:
        if option == '-h':
            pass
            exit()
        elif option == '--grid':
            grid = read_grid(argument)  # type: str

        if option  == '--words':
            words_to_find = read_words(argument)  # type: List[str]

    ws = WordSearch(grid)  # type: WordSearch

    for word in words_to_find:
        if ws.is_present(word):
            print("found {}".format(word))

#! /usr/bin/env python3
# Multiprocessing
from ctypes import c_wchar_p
from itertools import product
from multiprocessing import Pool, RawArray

# CLI Arguments
from sys import argv
from getopt import getopt, GetoptError

from string import ascii_lowercase
from typing import TYPE_CHECKING

from trie import Trie


if TYPE_CHECKING:
    from typing import Dict, List, Tuple
    from multiprocessing.sharedctypes import _Array

    # There doesn't seem to be a better way to get the correct type for these
    SharedAxes = _Array

    Axes = Tuple[str, ...]


ROW_LENGTH = 10000 # type: int
WINDOW_SIZE = 500  # type: int
MAX_WORD_LENGTH = 24  # type: int


def share_axes(rows: 'SharedAxes', columns: 'SharedAxes') -> None:
    """ Load axes from memory and share them with workers """
    global axes
    axes = tuple(
        tuple(axis)
        for axis in (rows, columns)
    )  # type: Tuple[Axes, ...]


def contains_word(word: str, search_index: int) -> bool:
    """ Check if word is contained in axes."""
    global axes
    for axis in axes:
        for index in range(search_index, search_index + WINDOW_SIZE):
            if word in axis[index]:
                return True

    return False


class WordSearch(object):

    def __init__(self, grid: str, use_trie: bool = False, axis_length: int = ROW_LENGTH, window_size: int = WINDOW_SIZE, max_word: int = MAX_WORD_LENGTH) -> None:
        self._cache = {}  # type: Dict[str, bool]
        self._use_trie = use_trie  # type: bool
        if self._use_trie:
            self._trie = Trie(grid, axis_length, window_size, max_word)  # type: Trie
        else:
            print('Loading grid: ....')
            self._axis_length = axis_length  # type: int
            size = self._axis_length**2  # type: int
            if len(grid) != size:
                raise RuntimeError("Not enough words!")

            self.rows = self._generate_rows(grid)  # type: Axes
            self.columns = self._generate_columns()  # type: Axes

            self._shared_rows = self._share_axes(self.rows)  # type:SharedAxes
            self._shared_columns = self._share_axes(self.columns)  # type: SharedAxes
            print('Loading grid: DONE')

    def _generate_rows(self, grid: str) -> 'Axes':
        """ Split grid into rows. """
        return tuple(
            grid[self._axis_length*row:self._axis_length*(row + 1)]
            for row in range(self._axis_length)
        )

    def _generate_columns(self) -> 'Axes':
        """ Transpose rows to get columns. """
        return tuple(
            ''.join(column)
            for column in zip(*self.rows)
        )

    def _share_axes(self, axes: 'Axes') -> 'SharedAxes':
        """ Create in memory array for storing and sharing axes. """
        return RawArray(c_wchar_p, axes)

    def _linear_search(self, word: str) -> bool:
        """ Iterates through rows and columns and checks for word presence. """
        for row, column in zip(self.rows, self.columns):
            if word in row:
                return True
            elif word in column:
                return True
        return False

    def _multiprocess_search(self, word: str) -> bool:
        """ Splits axes up and checks for word presence using multiple processes. """
        initargs = (self._shared_rows, self._shared_columns)
        with Pool(initializer=share_axes, initargs=initargs) as pool:
            results = pool.starmap(
                contains_word,
                product(
                    (word,),
                    range(0, self._axis_length, WINDOW_RANGE),
                ),
            )  # type: List[bool]

            return any(results)

    def is_present(self, word: str, use_multiprocess: bool = False) -> bool:
        """ Checks if word is present in grid. """
        if word not in self._cache:
            if self._use_trie:
                present = word in self._trie  # type: bool
            else:
                if use_multiprocess:
                    present = self._multiprocess_search(word)  # type: bool
                else:
                    present = self._linear_search(word)  # type: bool

            self._cache[word] = present

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

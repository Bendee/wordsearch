#! /usr/bin/env python3
# Multiprocessing
from ctypes import c_wchar_p
from multiprocessing import Value

# CLI Arguments
from sys import argv
from getopt import getopt, GetoptError

from string import ascii_lowercase
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import Dict, List, Tuple
    from multiprocessing.sharedctypes import _Value
    from threading import Event

    Axes = Tuple[str, ...]
    # There doesn't seem to be a better way to get the correct type for this
    SharedAxis = _Value
    CombinedAxis = Tuple[SharedAxis, SharedAxis]
    CombinedAxes = Tuple[CombinedAxis, ...]


ROW_LENGTH = 10000  # type: int


def share_axes(combined_axes: 'CombinedAxes') -> None:
    """ Make axes available to workers. """
    global axes
    axes = combined_axes  # type: CombinedAxes


def contains_word(event: 'Event', word: str, index: int) -> bool:
    """ Check if word is contained in axes."""
    global axes
    found = any(
        word in axis.value
        for axis in axes[index]
    )  # type: bool

    if found:
        event.set()

    return found


class WordSearch(object):

    def __init__(self, grid: str, axis_length: int = ROW_LENGTH) -> None:
        self._axis_length = axis_length  # type: int
        self._cache = {}  # type: Dict[str, bool]

        print('Loading grid: ....')
        if len(grid) != self._axis_length**2:
            raise RuntimeError("Not enough words!")

        self.rows = self._generate_rows(grid)  # type: Axes
        self.columns = self._generate_columns(self.rows)  # type: Axes
        self.axes = self._combine_axes(self.rows, self.columns)  # type: CombinedAxes
        print('Loading grid: DONE')

    def _generate_rows(self, grid: str) -> 'Axes':
        """ Split grid into rows. """
        return tuple(
            grid[self._axis_length*row:self._axis_length*(row + 1)]
            for row in range(self._axis_length)
        )

    def _generate_columns(self, rows: 'Axes') -> 'Axes':
        """ Transpose rows to get columns. """
        return tuple(
            ''.join(column)
            for column in zip(*rows)
        )

    def _combine_axes(self, rows: 'Axes', columns: 'Axes') -> 'CombinedAxes':
        """ Combine the axes and make them sharable across processes. """
        return tuple(
            (
                Value(c_wchar_p, row, lock=False),
                Value(c_wchar_p, column, lock=False),
            )
            for row, column in zip(rows, columns)
        )

    def _is_present(self, word: str) -> bool:
        """ Iterates through rows and columns and checks for word presence. """
        for row, column in zip(self.rows, self.columns):
            if word in row:
                return True
            elif word in column:
                return True
        return False

    def is_present(self, word: str) -> bool:
        """ Checks if word is present in grid. """
        if word not in self._cache:
            present = self._is_present(word)
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

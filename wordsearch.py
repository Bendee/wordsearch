#! /usr/bin/env python3
# Multiprocessing
from ctypes import c_wchar_p
from itertools import product
from multiprocessing import Pool, RawArray
from numpy import asarray, copyto, frombuffer

# CLI Arguments
from sys import argv
from getopt import getopt, GetoptError

from string import ascii_lowercase
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from typing import Dict, List, Tuple, Type
    from multiprocessing.sharedctypes import _Array

    from numpy import ndarray

    # There doesn't seem to be a better way to get the correct type for these
    SharedAxes = _Array
    AxesArray = Type[ndarray]

    Axes = Tuple[str, ...]


ROW_LENGTH = 10000  # type: int
WINDOW_RANGE = 100  # type: int


def share_axes(rows: 'SharedAxes', columns: 'SharedAxes', dtype: str) -> None:
    """ Load axes from memory and share them with workers """
    global axes
    axes = tuple(
        frombuffer(axis, dtype=dtype)
        for axis in (rows, columns)
    )  # type: Tuple[AxesArray, ...]


def contains_word(word: str, search_index: int) -> bool:
    """ Check if word is contained in axes."""
    global axes
    for axis in axes:
        for index in range(search_index, search_index + WINDOW_RANGE):
            if word in axis[index].decode('utf-8'):
                return True

    return False


class WordSearch(object):

    def __init__(self, grid: str, axis_length: int = ROW_LENGTH) -> None:
        self._axis_length = axis_length  # type: int
        self._cache = {}  # type: Dict[str, bool]

        print('Loading grid: ....')
        size = self._axis_length**2  # type: int
        if len(grid) != size:
            raise RuntimeError("Not enough words!")

        self._dtype = '|S{size}'.format(size=self._axis_length)  # type: str

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

    def _initialise_axis_array(self, adjust: int = 1) -> 'SharedAxes':
        """ Create in memory array for storing numpy arrays. """
        return RawArray(c_wchar_p, int(self._axis_length*12.5*adjust))

    def _share_axes(self, axes: 'Axes') -> 'SharedAxes':
        """ Create shared numpy array of a certain axis. """
        axes_array = self._initialise_axis_array()  # type: SharedAxes
        shared_axes = frombuffer(axes_array, dtype=self._dtype)  # type: AxesArray
        if shared_axes.size < self._axis_length:
            adjustment = self._axis_length//shared_axes.size  # type: int
            axes_array = self._initialise_axis_array(adjustment)  # type: SharedAxes
            shared_axes = frombuffer(axes_array, dtype=self._dtype)  # type: AxesArray

        copyto(shared_axes, asarray(axes, dtype=self._dtype))
        return axes_array

    def _is_present(self, word: str) -> bool:
        """ Splits axes up and checks for word presence using multiple processes. """
        initargs = (self._shared_rows, self._shared_columns, self._dtype)
        with Pool(initializer=share_axes, initargs=initargs) as pool:
            results = pool.starmap(
                contains_word,
                product(
                    (word,),
                    range(0, self._axis_length, WINDOW_RANGE),
                ),
            )  # type: List[bool]

            return any(results)

    def is_present(self, word: str) -> bool:
        """ Checks if word is present in grid. """
        if word not in self._cache:
            present = self._is_present(word)  # type: bool
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

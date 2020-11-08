#! /usr/bin/env python3
from sys import argv
from getopt import getopt, GetoptError
from string import ascii_lowercase
from typing import Dict, List


ROW_LENGTH = 10000  # type: int


class WordSearch(object):

    def __init__(self, grid: str, axis_length: int = ROW_LENGTH) -> None:
        self._axis_length = axis_length  # type: int
        self._cache = {}  # type: Dict[str, bool]

        if len(grid) != self._axis_length**2:
            raise RuntimeError("Not enough words!")

        self.rows = self._generate_rows(grid)  # type: List[str]
        self.columns = self._generate_columns()  # type: List[str]

    def _generate_rows(self, grid: str) -> List[str]:
        """ Split grid into rows. """
        return [
            grid[self._axis_length*row:self._axis_length*(row + 1)]
            for row in range(self._axis_length)
        ]

    def _generate_columns(self) -> List[str]:
        """ Transpose rows to get columns. """
        return [
            ''.join(column)
            for column in zip(*self.rows)
        ]

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


def read_words(path: str) -> List[str]:
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

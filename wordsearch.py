#! /usr/bin/env python3
from sys import argv
from getopt import getopt, GetoptError
from string import ascii_lowercase
from typing import Dict, List


ROW_LENGTH: int = 1000


class WordSearch(object):

    def __init__(self, grid: str, axis_length: int = ROW_LENGTH) -> None:
        self._axis_length: int = axis_length
        self._present: Dict[str, bool] = {}

        if len(grid) != self._axis_length**2:
            raise RuntimeError("Not enough words!")

        self._rows: List[str] = [
            grid[self._axis_length*row:self._axis_length*(row + 1)]
            for row in range(self._axis_length)
        ]

        self._columns: List[str] = [
            ''.join(column)
            for column in zip(*self._rows)

    def _is_present(self, word: str) -> bool:
        for row, column in zip(self._rows, self._columns):
            if word in row:
                return True
            elif word in column:
                return True
        return False

    def is_present(self, word: str) -> bool:
        if word not in self._present:
            present = self._is_present(word)
            self._present[word] = present

        return self._present[word]

def read_grid(path: str) -> str:
    grid: str = ''
    with open(path, "r") as file:
        for line in file:
            grid += ''.join(filter(lambda x: x in ascii_lowercase, line))

    return grid

def read_words(path: str) -> List[str]:
    words: List[str] = []

    with open(path, "r") as file:
        for line in file:
            words.append(line.strip())

    return words


if __name__ == "__main__":
    debug: bool = False
    try:
        options, args = getopt(argv[1:], 'hd', ['grid=', 'words='])
    except GetoptError as e:
        raise RuntimeError from e
    if len(options) == 0:
        raise RuntimeError
    for option, argument in options:
        if option == '-h':
            pass
            exit()
        elif option == '-d':
            debug = True
            grid: str = test_grid()
        elif option == '--grid':
            grid: str = read_grid(argument)

        if option  == '--words':
            words_to_find: List[str] = read_words(argument)

    ws: WordSearch = WordSearch(grid)

    for word in words_to_find:
        if ws.is_present(word):
            print("found {}".format(word))

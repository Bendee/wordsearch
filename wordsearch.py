#! /usr/bin/env python3
from sys import argv
from getopt import getopt, GetoptError
from string import ascii_lowercase
from typing import List


ROW_LENGTH: int = 1000


class WordSearch(object):

    def __init__(self, grid: str) -> None:
        self.grid: List[str] = [
            grid[ROW_LENGTH*i:ROW_LENGTH*(i+1)]
            for i in range(ROW_LENGTH)
        ]
        if len(self.grid[-1]) != ROW_LENGTH:
            raise RuntimeError("Not enough words!")

    def is_present(self, word: str) -> bool:
        return True


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


def test_grid() -> str:
    from random import choice

    return ''.join(choice(ascii_lowercase) for i in range(ROW_LENGTH*ROW_LENGTH))


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

    # for word in words_to_find:
    #     if ws.is_present(word):
    #         print "found {}".format(word)

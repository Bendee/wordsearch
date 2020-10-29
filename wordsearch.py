#! /usr/bin/env python3
from sys import stdin
from typing import Iterable, Iterator, List


ROW_LENGTH: int = 1000
CHARS: str = 'abcdefghijklmnopqrstuvwxyz'


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


def read_grid() -> str:
    words: Iterable[str] = map(lambda x: x.lower(), stdin.readlines())
    filtered_words: Iterator[str] = (
        ''.join(filter(lambda x: x in CHAR, word))
        for word in words
    )
    return ''.join(filtered_words)


if __name__ == "__main__":
    grid: str = read_grid()
    ws: WordSearch = WordSearch(grid)

    # for word in words_to_find:
    #     if ws.is_present(word):
    #         print "found {}".format(word)

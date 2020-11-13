#! /usr/bin/env python3
from typing import TYPE_CHECKING
from argparse import ArgumentParser

from utils import Grid, read_grid, read_words, Trie


if TYPE_CHECKING:
    from typing import Dict, List, Union
    from argparse import Namespace as ParsedArguments


ROW_LENGTH = 10000 # type: int
WINDOW_SIZE = 500  # type: int
MAX_WORD_LENGTH = 24  # type: int


class WordSearch(object):

    def __init__(
                self,
                grid: str,
                use_trie: bool = False,
                axis_length: int = ROW_LENGTH,
                window_size: int = WINDOW_SIZE,
                max_word: int = MAX_WORD_LENGTH
            ) -> None:
        self._cache = {}  # type: Dict[str, bool]
        self._use_trie = use_trie  # type: bool
        if self._use_trie:
            self._data = Trie(
                grid,
                axis_length,
                window_size,
                max_word,
            )  # type: Union[Grid, Trie]
        else:
            self._data = Grid(
                grid,
                axis_length,
                window_size,
            )  # type: Union[Grid, Trie]

    def is_present(self, word: str, use_multiprocess: bool = False) -> bool:
        """ Checks if word is present in grid. """
        if word not in self._cache:
            if self._use_trie:
                present = word in self._data  # type: bool
            else:
                if use_multiprocess:
                    present = self._data.multiprocess_search(word)  # type: bool
                else:
                    present = self._data.linear_search(word)  # type: bool

            self._cache[word] = present

        return self._cache[word]


if __name__ == "__main__":
    parser = ArgumentParser(
        description='Check presence of words in a given grid',
    )  # type: ArgumentParser

    parser.add_argument(
        'grid',
        help='The file containing the grid of words',
    )
    parser.add_argument(
        'words',
        help='The list of words to check'
    )

    arguments = parser.parse_args()  # type: ParsedArguments

    grid = read_grid(arguments.grid)  # type: str
    words_to_find = read_words(arguments.words)  # type: List[str]

    ws = WordSearch(arguments.grid)  # type: WordSearch

    for word in words_to_find:
        if ws.is_present(word):
            print("found {}".format(word))

from typing import TYPE_CHECKING
from string import ascii_lowercase


if TYPE_CHECKING:
    from typing import List
    from pathlib import Path


def read_grid(path: 'Path') -> str:
    """ Read grid from file. """
    grid = ''  # type: str
    with path.open('r') as file:
        for line in file:
            grid += ''.join(filter(lambda x: x in ascii_lowercase, line))

    return grid


def read_words(path: 'Path') -> 'List[str]':
    """ Read words from file. """
    words = []  # type: List[str]

    with path.open('r') as file:
        for line in file:
            words.append(line.strip())

    return words

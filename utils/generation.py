from typing import TYPE_CHECKING
from argparse import ArgumentParser
from json import dump
from math import sqrt
from random import choice, randrange, sample, shuffle
from string import ascii_lowercase

from utils import Grid, read_grid


if TYPE_CHECKING:
    from typing import Dict, List
    from argparse import (
        _SubParsersAction as SubParsers,
        Namespace as ParsedArguments,
    )


def create_grid(length: int) -> str:
    """ Create a random grid. """
    return ''.join(choice(ascii_lowercase) for _ in range(length**2))


def write_grid(path: str, length: int) -> None:
    """ Write a random grid to a file. """
    grid = create_grid(length)  # type: str

    with open(path, "w") as file:
        for i in range(length):
            file.write(grid[i*length:(i+1)*length] + '\n')


def generate_words(grid_string: str, amount: int) -> 'Dict[str, bool]':
    """ Get random words from the grid.

    Also trys to construct words that won't be contained
    """
    length = int(sqrt(len(grid_string)))
    grid = Grid(grid_string, axis_length=length, window_size=0)
    length = len(grid.rows)

    words = {}  # type: Dict[str, bool]
    for _ in range(amount):
        axis = choice(choice((grid.rows, grid.columns)))  # type: str
        index = randrange(length)  # type: int

        in_word = axis[
            index:index + randrange(5, max(12, min(24, (length - index))))
        ]  # type: str
        words[in_word] = True

        out_word = ''.join(sample(in_word, len(in_word)))  # type: str
        words[out_word] = grid.linear_search(out_word)

    return words


def write_words(path: str, amount: int, grid: str, json: bool) -> None:
    """ Writes the list of words to a file. """
    words = generate_words(grid, amount)  # type: Dict[str, bool]
    with open(path, 'w') as file:
        if json:
            dump(words, file)
        else:
            words_list = list(words.keys())  # type: List[str]
            words_list.extend(sample(words_list, len(words_list)//3))
            shuffle(words_list)
            for word in words:
                file.write(word + '\n')


def parse_grid(arguments: 'ParsedArguments') -> None:
    write_grid(arguments.path, arguments.size)


def parse_words(arguments: 'ParsedArguments') -> None:
    write_words(
        arguments.path,
        arguments.amount,
        read_grid(arguments.grid),
        arguments.json,
    )

if __name__ == '__main__':
    parser = ArgumentParser(
        description='Create grids and words to use with wordsearch',
    )  # type: ArgumentParser
    subparsers = parser.add_subparsers()  # type: SubParsers

    grid_parser = subparsers.add_parser('grid')  # type: ArgumentParser
    grid_parser.add_argument(
        'path',
        help='Location at which to store generated grid',
    )
    grid_parser.add_argument(
        'size',
        type=int,
        help='Size of the generated grid',
    )
    grid_parser.set_defaults(function=parse_grid)

    words_parser = subparsers.add_parser('words')  # type: ArgumentParser
    words_parser.add_argument(
        'path',
        help='Location at which to store generated words',
    )
    words_parser.add_argument(
        'amount',
        type=int,
        help='The amount of words to generate',
    )
    words_parser.add_argument(
        'grid',
        help='The grid to retrieve the words from.',
    )
    words_parser.add_argument(
        '--json',
        help='Whether to store words with their presence in json form.',
        action='store_true',
    )
    words_parser.set_defaults(function=parse_words)

    arguments = parser.parse_args()  # type: ParsedArguments
    arguments.function(arguments)

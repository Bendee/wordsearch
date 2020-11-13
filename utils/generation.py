from typing import TYPE_CHECKING
from json import dump
from math import sqrt
from random import choice, randrange, sample, shuffle
from string import ascii_lowercase
from sys import argv

from utils import Grid, read_grid


if TYPE_CHECKING:
    from typing import Dict, List


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


def write_words(path: str, amount: int, grid: str, presence: bool) -> None:
    """ Writes the list of words to a file. """
    words = generate_words(grid, amount)  # type: Dict[str, bool]
    with open(path, 'w') as file:
        if presence:
            dump(words, file)
        else:
            words_list = list(words.keys())  # type: List[str]
            words_list.extend(sample(words_list, len(words_list)//3))
            shuffle(words_list)
            for word in words:
                file.write(word + '\n')


if __name__ == '__main__':
    if len(argv) != 0:
        command, path, *args = argv[1:]
        if command == 'grid':
            write_grid(path, int(args[0]))
        elif command == 'words':
            try:
                length = int(args[1])
                grid = create_grid(length)
            except ValueError:
                grid = read_grid(args[1])

            try:
                presence = bool(args[0])
            except IndexError:
                presence = False

            write_words(path, int(args[0]), grid, presence)
        else:
            raise RuntimeError('{} is not a valid command'.format(command))

from random import choice
from string import ascii_lowercase

from wordsearch import read_grid


NEW_GRID = False
GRID_FILE: str = 'grid.txt'
AXIS_LENGTH: int = 10000


def create_test_grid() -> None:
    with open(GRID_FILE, "w") as file:
        for i in range(AXIS_LENGTH):
            file.write(''.join(
                choice(ascii_lowercase)
                for j in range(AXIS_LENGTH)
            ) + '\n')


if NEW_GRID:
    create_test_grid()


def test_read_grid(benchmark):
    benchmark(read_grid, path=GRID_FILE)

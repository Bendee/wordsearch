from pathlib import Path
from random import choice, randrange, sample, shuffle
from string import ascii_lowercase
from typing import Dict, List

from pytest import mark

from wordsearch import WordSearch, read_grid

GRID_FILE = 'grid.txt'  # type: str
WORD_FILE = 'words.txt'  # type: str
NEW_GRID = not Path(GRID_FILE).exists()  # type: bool
AXIS_LENGTH = 10000  # type: int


def create_test_grid() -> None:
    """ Create and write a random grid to a file. """
    with open(GRID_FILE, "w") as file:
        for i in range(AXIS_LENGTH):
            file.write(''.join(
                choice(ascii_lowercase)
                for j in range(AXIS_LENGTH)
            ) + '\n')


def write_words(words: List[str]) -> None:
    """ Writes the list of words to a file. """
    words.extend(sample(words, len(words)//3))
    shuffle(words)
    with open(WORD_FILE, 'w') as f:
        for word in words:
            f.write(word + '\n')


def get_words(amount: int = 100) -> Dict[str, bool]:
    """ Get random words from the grid. 

    Also trys to construct words that won't be contained
    """
    words = {}  # type: Dict[str, bool]
    for i in range(amount):
        axis = choice(choice((WS.rows, WS.columns)))  # type: str
        index = randrange(AXIS_LENGTH)  # type: int

        in_word = axis[
            index:index + randrange(5, max(12, min(24, (AXIS_LENGTH - index))))
        ]  # type: str
        words[in_word] = True

        out_word = ''.join(sample(in_word, len(in_word)))  # type: str
        words[out_word] = WS.is_present(out_word)

    return words


if NEW_GRID:
    create_test_grid()

GRID = read_grid(GRID_FILE)  # type: str
WS = WordSearch(GRID, AXIS_LENGTH)  # type: WordSearch
WORDS = get_words()  # type: Dict[str, bool]

if NEW_GRID:
    write_words(list(get_words(400).keys()))


def test_read_grid(benchmark) -> None:
    benchmark(read_grid, path=GRID_FILE)


def test__generate_rows(benchmark) -> None:
    benchmark(WS._generate_rows, grid=GRID)


def test__generate_columns(benchmark) -> None:
    benchmark(WS._generate_columns, rows=WS.rows)


def test__combine_axes(benchmark) -> None:
    benchmark(WS._combine_axes, rows=WS.rows, columns=WS.columns)


@mark.parametrize("word, expected", WORDS.items())
def test_is_present(benchmark, word: str, expected: bool) -> None:
    result = benchmark(WS.is_present, word=word)  # type: bool
    assert result == expected


@mark.parametrize("word, expected", WORDS.items())
def test__is_present(benchmark, word: str, expected: bool) -> None:
    result = benchmark(WS._is_present, word=word)  # type: bool
    assert result == expected

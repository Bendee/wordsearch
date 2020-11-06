from pathlib import Path
from random import choice, randrange, sample, shuffle
from string import ascii_lowercase
from typing import Dict, List

from pytest import mark

from wordsearch import WordSearch, read_grid

GRID_FILE: str = 'grid.txt'
WORD_FILE: str = 'words.txt'
NEW_GRID: bool = not Path(GRID_FILE).exists()
AXIS_LENGTH: int = 10000


def create_test_grid() -> None:
    with open(GRID_FILE, "w") as file:
        for i in range(AXIS_LENGTH):
            file.write(''.join(
                choice(ascii_lowercase)
                for j in range(AXIS_LENGTH)
            ) + '\n')


def write_words(words: List[str]) -> None:
    words.extend(sample(words, len(words)//3))
    shuffle(words)
    with open(WORD_FILE, 'w') as f:
        for word in words:
            f.write(word + '\n')


def get_words(amount: int = 100) -> Dict[str, bool]:
    words: Dict[str, bool] = {}
    for i in range(amount):
        axis: str = choice(choice((WS.rows, WS.columns)))
        index: int = randrange(AXIS_LENGTH)

        in_word: str = axis[index:index + randrange(5, max(12, min(24, (AXIS_LENGTH - index))))]
        words[in_word] = True

        out_word: str = ''.join(sample(in_word, len(in_word)))
        words[out_word] = WS.is_present(out_word)

    return words


if NEW_GRID:
    create_test_grid()

GRID: str = read_grid(GRID_FILE)
WS: WordSearch = WordSearch(GRID, AXIS_LENGTH)
WORDS: Dict[str, bool] = get_words()

if NEW_GRID:
    write_words(list(get_words(400).keys()))


def test_read_grid(benchmark):
    benchmark(read_grid, path=GRID_FILE)


def test__generate_rows(benchmark):
    benchmark(WS._generate_rows, grid=GRID)


def test__generate_columns(benchmark):
    benchmark(WS._generate_columns)


@mark.parametrize("word, expected", WORDS.items())
def test_is_present(benchmark, word: str, expected: bool):
    result: bool = benchmark(WS.is_present, word=word)
    assert result == expected


@mark.parametrize("word, expected", WORDS.items())
def test__is_present(benchmark, word: str, expected: bool):
    result: bool = benchmark(WS._is_present, word=word)
    assert result == expected

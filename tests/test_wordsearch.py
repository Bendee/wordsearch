from pytest import mark

from wordsearch import WordSearch
from utils import read_grid

from tests.data import GRID, GRID_FILE, ROW_LENGTH, WORDS_MAP


WS = WordSearch(GRID, axis_length=ROW_LENGTH)  # type: WordSearch


def test_read_grid(benchmark) -> None:
    grid = benchmark(read_grid, path=GRID_FILE)  # type: str
    assert grid == GRID


@mark.parametrize("word, expected", WORDS_MAP.items())
def test_is_present(benchmark, word: str, expected: bool) -> None:
    result = benchmark(WS.is_present, word=word)  # type: bool
    assert result == expected

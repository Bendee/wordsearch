from typing import TYPE_CHECKING

from pytest import mark

from utils import Grid
from tests.test_wordsearch import GRID_STRING, ROW_LENGTH, WINDOW_SIZE, WORDS


if TYPE_CHECKING:
    from utils.grid import Axes


GRID = Grid(GRID_STRING, axis_length=ROW_LENGTH, window_size=WINDOW_SIZE)


def test__generate_rows(benchmark) -> None:
    benchmark(GRID._generate_rows, grid=GRID_STRING)


def test__generate_columns(benchmark) -> None:
    benchmark(GRID._generate_columns)


@mark.parametrize("axes", (GRID.rows, GRID.columns))
def test__share_axes(benchmark, axes: 'Axes') -> None:
    benchmark(GRID._share_axes, axes=axes)


@mark.parametrize("word, expected", WORDS.items())
def test_linear_search(benchmark, word: str, expected: bool) -> None:
    result = benchmark(GRID.linear_search, word=word)  # type: bool
    assert result == expected


@mark.parametrize("word, expected", WORDS.items())
def test_multiprocess_search(benchmark, word: str, expected: bool) -> None:
    result = benchmark(GRID.multiprocess_search, word=word)  # type: bool
    assert result == expected

from typing import TYPE_CHECKING

from pytest import mark

from utils.grid import Grid

from tests.data import GRID, ROW_LENGTH, WINDOW_SIZE, WORDS_MAP


if TYPE_CHECKING:
    from utils.grid import Axes


GRID_INSTANCE = Grid(GRID, axis_length=ROW_LENGTH, window_size=WINDOW_SIZE)  # type: Grid


def test__generate_rows(benchmark) -> None:
    benchmark(GRID_INSTANCE._generate_rows, grid=GRID)


def test__generate_columns(benchmark) -> None:
    benchmark(GRID_INSTANCE._generate_columns)


@mark.parametrize("axes", (GRID_INSTANCE.rows, GRID_INSTANCE.columns))
def test__share_axes(benchmark, axes: 'Axes') -> None:
    benchmark(GRID_INSTANCE._share_axes, axes=axes)


@mark.parametrize("word, expected", WORDS_MAP.items())
def test_linear_search(benchmark, word: str, expected: bool) -> None:
    result = benchmark(GRID_INSTANCE.linear_search, word=word)  # type: bool
    assert result == expected


@mark.parametrize("word, expected", WORDS_MAP.items())
def test_multiprocess_search(benchmark, word: str, expected: bool) -> None:
    result = benchmark(GRID_INSTANCE.multiprocess_search, word=word)  # type: bool
    assert result == expected

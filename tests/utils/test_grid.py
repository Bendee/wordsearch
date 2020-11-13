from typing import TYPE_CHECKING

from pytest import mark

from utils.grid import Grid, _share_axes, _contains_word

from tests.data import GRID, ROW_LENGTH, WINDOW_SIZE, WORDS_MAP, WINDOW_WORDS


if TYPE_CHECKING:
    from utils.grid import Axes, AxesInfo


GRID_INSTANCE = Grid(GRID, axis_length=ROW_LENGTH, window_size=WINDOW_SIZE)  # type: Grid
AXES_INFO = {
    'rows': GRID_INSTANCE._shared_rows,
    'columns': GRID_INSTANCE._shared_columns,
    'window': GRID_INSTANCE._window_size,
}  # type: AxesInfo


def test__share_axes(benchmark) -> None:
    benchmark(_share_axes, axes_info=AXES_INFO)


@mark.parametrize('word, expected', WINDOW_WORDS.items())
def test__contains_word(benchmark, word: str, expected: bool) -> None:
    _share_axes(AXES_INFO)
    result = benchmark(_contains_word, word=word, search_index=100)  # type: bool
    assert result == expected


def test_Grid__generate_rows(benchmark) -> None:
    benchmark(GRID_INSTANCE._generate_rows, grid=GRID)


def test_Grid__generate_columns(benchmark) -> None:
    benchmark(GRID_INSTANCE._generate_columns)


@mark.parametrize('axes', (GRID_INSTANCE.rows, GRID_INSTANCE.columns))
def test_Grid__share_axes(benchmark, axes: 'Axes') -> None:
    benchmark(GRID_INSTANCE._share_axes, axes=axes)


@mark.parametrize('word, expected', WORDS_MAP.items())
def test_Grid_linear_search(benchmark, word: str, expected: bool) -> None:
    result = benchmark(GRID_INSTANCE.linear_search, word=word)  # type: bool
    assert result == expected


@mark.parametrize("word, expected", WORDS_MAP.items())
def test_Grid_multiprocess_search(benchmark, word: str, expected: bool) -> None:
    result = benchmark(GRID_INSTANCE.multiprocess_search, word=word)  # type: bool
    assert result == expected

from typing import TYPE_CHECKING

from pytest import mark, raises

from utils.grid import Grid, _GridWorker

from tests.data import GRID, ROW_LENGTH, WINDOW_SIZE, WORDS_MAP, WINDOW_WORDS


if TYPE_CHECKING:
    from typing import Tuple

    from utils.grid import Axes


GRID_INSTANCE = Grid(GRID, ROW_LENGTH, WINDOW_SIZE, False)  # type: Grid
SHARED_AXES = tuple(
    tuple(axis)
    for axis in (GRID_INSTANCE._shared_rows, GRID_INSTANCE._shared_columns)
)  # type: Tuple[Axes, ...]


def test__GridWorker_contains_word_unshared() -> None:
    worker = _GridWorker()  # type: _GridWorker
    with raises(RuntimeError):
        worker.contains_word(word='test', search_index=100)


def test__GridWorker_share_data(benchmark) -> None:
    worker = _GridWorker()  # type: _GridWorker
    benchmark(
        worker.share_data,
        rows=GRID_INSTANCE._shared_rows,
        columns=GRID_INSTANCE._shared_columns,
        window_size=GRID_INSTANCE._window_size,
    )

    assert worker._window_size == GRID_INSTANCE._window_size
    assert worker._axes == SHARED_AXES


@mark.parametrize('word, expected', WINDOW_WORDS.items())
def test__GridWorker_contains_word(benchmark, word: str, expected: bool) -> None:
    worker = _GridWorker()  # type: _GridWorker
    worker.share_data(
        GRID_INSTANCE._shared_rows,
        GRID_INSTANCE._shared_columns,
        GRID_INSTANCE._window_size,
    )
    result = benchmark(worker.contains_word, word=word, search_index=100)  # type: bool

    assert result == expected


def test_Grid__generate_rows(benchmark) -> None:
    benchmark(GRID_INSTANCE._generate_rows, grid=GRID)


def test_Grid__generate_columns(benchmark) -> None:
    benchmark(GRID_INSTANCE._generate_columns)


@mark.parametrize('axes', (GRID_INSTANCE.rows, GRID_INSTANCE.columns))
def test_Grid__share_axes(benchmark, axes: 'Axes') -> None:
    benchmark(GRID_INSTANCE._share_axes, axes=axes)


@mark.parametrize('word, expected', WORDS_MAP.items())
def test_Grid__linear_search(benchmark, word: str, expected: bool) -> None:
    result = benchmark(GRID_INSTANCE._linear_search, word=word)  # type: bool

    assert result == expected


@mark.parametrize("word, expected", WORDS_MAP.items())
def test_Grid__multiprocess_search(benchmark, word: str, expected: bool) -> None:
    result = benchmark(GRID_INSTANCE._multiprocess_search, word=word)  # type: bool

    assert result == expected


@mark.parametrize("word, expected", WORDS_MAP.items())
def test_Grid___contains__(benchmark, word: str, expected: bool) -> None:
    result = benchmark(GRID_INSTANCE.__contains__, word=word)  # type: bool

    assert result == expected

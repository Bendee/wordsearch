from typing import TYPE_CHECKING
from ctypes import Array

from numpy import ndarray, asarray
from pytest import mark, raises

from utils.trie import Trie, _TrieDict, _TrieWorker

from tests.data import (
    GRID,
    ROW_LENGTH,
    TRIES,
    TRIE_NODE,
    WINDOW_SIZE,
    MAX_WORD_LENGTH,
    WORDS_MAP,
)


if TYPE_CHECKING:
    from typing import Any, Dict, List

    from utils.trie import SharedGridArray, Grid


TRIE_INSTANCE = Trie(GRID, ROW_LENGTH, WINDOW_SIZE, MAX_WORD_LENGTH)  # type: Trie


class FakePool:

    def __init__(self, pool_length: int):
        self._pool = [0]*pool_length  # type List[int]


def _make_np_array(array: 'List[str]') -> 'Grid':
    return asarray(array, dtype=TRIE_INSTANCE._dtype).flatten()  # type: Grid


POOL = FakePool(10)  # type: FakePool
RANGES = range(0, TRIE_INSTANCE._axis_length, WINDOW_SIZE)  # type: range


trie_instance = _TrieDict()  # type: _TrieDict
@mark.parametrize('array, expected', TRIES)
def test__TrieDict_add_children(benchmark, array: 'List[str]', expected: 'Dict[str, Any]') -> None:
    benchmark(trie_instance.add_children, children=_make_np_array(array))

    assert trie_instance == expected


trie_instance = _TrieDict()  # type: _TrieDict
@mark.parametrize('array, expected', TRIES)
def test__TrieDict__add_child(benchmark, array: 'List[str]', expected: 'Dict[str, Any]') -> None:
    np = _make_np_array(array)  # type: Grid
    benchmark(trie_instance._add_child, child=np[0], children=np[1:])

    assert trie_instance == expected


def test__TrieDict___or__(benchmark) -> None:
    trie1, trie2 = _TrieDict(), _TrieDict()
    trie1.add_children(_make_np_array(TRIES[0][0]))
    trie2.add_children(_make_np_array(TRIES[1][0]))
    result = benchmark(trie1.__or__, other=trie2)  # type: _TrieDict

    assert result == TRIES[1][1]


@mark.parametrize('word, expected', WORDS_MAP.items())
def test__TrieDict___contains__(benchmark, word: str, expected: bool) -> None:
    result = benchmark(TRIE_INSTANCE._root.__contains__, word=list(word))  # type: bool

    assert result == expected


def test__TrieWorker_iterate_window_unshared() -> None:
    worker = _TrieWorker()  # type: _TrieWorker
    with raises(RuntimeError):
        worker.iterate_window(ranges=(10, 10))


def test__TrieWorker_share_data(benchmark) -> None:
    worker = _TrieWorker()  # type: _TrieWorker
    benchmark(
        worker.share_data,
        grid=TRIE_INSTANCE._grid,
        shape=TRIE_INSTANCE._shape,
        dtype=TRIE_INSTANCE._dtype,
        window_size=WINDOW_SIZE,
        axis_length=TRIE_INSTANCE._axis_length,
        max_word_length=MAX_WORD_LENGTH,
    )

    assert worker._max_word_length == MAX_WORD_LENGTH
    assert worker._axis_length == TRIE_INSTANCE._axis_length
    assert worker._window_size == WINDOW_SIZE
    assert worker._dtype == TRIE_INSTANCE._dtype
    assert worker._shape == TRIE_INSTANCE._shape
    assert worker._grid == TRIE_INSTANCE._grid


def test__TrieWorker_iterate_window(benchmark) -> None:
    worker = _TrieWorker()  # type: _TrieWorker
    result = benchmark(worker.iterate_window, ranges=(10, 10))  # type: _TrieDict

    assert result == TRIE_NODE


def test_Trie__load_grid(benchmark) -> None:
    result = benchmark(TRIE_INSTANCE._load_grid, grid=GRID)  # type: SharedGridArray

    assert isinstance(result, Array)


def test_Trie__format_grid(benchmark) -> None:
    size = TRIE_INSTANCE._axis_length**2
    result = benchmark(TRIE_INSTANCE._format_grid, grid=GRID, size=size)  # type: Grid

    assert isinstance(result, ndarray)


def test_Trie_fill_trie(benchmark) -> None:
    benchmark(TRIE_INSTANCE._fill_trie, window_size=WINDOW_SIZE, max_word=MAX_WORD_LENGTH)


def test_Trie__calculate_chunks(benchmark) -> None:
    result = benchmark(TRIE_INSTANCE._calculate_chunksize, pool=POOL, ranges=RANGES)  # type: int

    assert result == 1


@mark.parametrize('word, expected', WORDS_MAP.items())
def test_Trie___contains__(benchmark, word: str, expected: bool) -> None:
    result = benchmark(TRIE_INSTANCE.__contains__, word=word)  # type: bool

    assert result == expected

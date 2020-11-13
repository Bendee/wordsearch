from typing import TYPE_CHECKING
from ctypes import Array

from numpy import ndarray, asarray, frombuffer
from pytest import mark

from utils.trie import Trie, TrieDict, _init_window, _iterate_window

from tests.data import GRID, ROW_LENGTH, TRIES, TRIE_NODE, WINDOW_SIZE, MAX_WORD_LENGTH, WORDS_MAP


if TYPE_CHECKING:
    from typing import Any, Dict, List

    from utils.trie import SharedGridArray, Grid, GridInfo


TRIE_INSTANCE = Trie(GRID, ROW_LENGTH, WINDOW_SIZE, MAX_WORD_LENGTH)  # type: Trie
GRID_INFO = {
    'grid': TRIE_INSTANCE._grid,
    'shape': TRIE_INSTANCE._shape,
    'dtype': TRIE_INSTANCE._dtype,
    'window': WINDOW_SIZE,
    'axis': TRIE_INSTANCE._axis_length,
    'max': MAX_WORD_LENGTH,
}  # type: GridInfo


def _make_np_array(array: 'List[str]') -> 'Grid':
    return asarray(array, dtype=TRIE_INSTANCE._dtype).flatten()  # type: Grid


POOL = FakePool(10)  # type: FakePool
RANGES = range(0, TRIE_INSTANCE._axis_length, WINDOW_SIZE)  # type: range


trie_instance = TrieDict()  # type: TrieDict
@mark.parametrize('array, expected', TRIES)
def test_TrieDict_add_children(benchmark, array: 'List[str]', expected: 'Dict[str, Any]') -> None:
    benchmark(trie_instance.add_children, children=_make_np_array(array))
    assert trie_instance == expected


trie_instance = TrieDict()  # type: TrieDict
@mark.parametrize('array, expected', TRIES)
def test_TrieDict_add_child(benchmark, array: 'List[str]', expected: 'Dict[str, Any]') -> None:
    np = _make_np_array(array)  # type: Grid
    benchmark(trie_instance.add_child, child=np[0], children=np[1:])
    assert trie_instance == expected


def test_TrieDict___or__(benchmark) -> None:
    trie1, trie2 = TrieDict(), TrieDict()
    trie1.add_children(_make_np_array(TRIES[0][0]))
    trie2.add_children(_make_np_array(TRIES[1][0]))
    result = benchmark(trie1.__or__, other=trie2)  # type: TrieDict
    assert result == TRIES[1][1]


@mark.parametrize('word, expected', WORDS_MAP.items())
def test_TrieDict___contains__(benchmark, word: str, expected: bool) -> None:
    result = benchmark(TRIE_INSTANCE._root.__contains__, word=list(word))  # type: bool
    assert result == expected


def test__init_window(benchmark) -> None:
    benchmark(_init_window, grid_info=GRID_INFO)


def test__iterate_window(benchmark) -> None:
    _init_window(GRID_INFO)
    result = benchmark(_iterate_window, ranges=(10, 10))  # type: TrieDict
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


class FakePool:
    def __init__(self, pool_length: int):
        self._pool = [0]*pool_length  # type List[int]


def test_Trie__calculate_chunks(benchmark) -> None:
    result = benchmark(TRIE_INSTANCE._calculate_chunksize, pool=POOL, ranges=RANGES)  # type: int
    assert result == 1


@mark.parametrize('word, expected', WORDS_MAP.items())
def test_Trie___contains__(benchmark, word: str, expected: bool) -> None:
    result = benchmark(TRIE_INSTANCE.__contains__, word=word)  # type: bool
    assert result == expected

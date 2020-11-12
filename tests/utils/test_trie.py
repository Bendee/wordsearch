from typing import TYPE_CHECKING
from ctypes import Array

from numpy import ndarray
from pytest import mark

from utils.trie import Trie

from tests.data import GRID, ROW_LENGTH, WINDOW_SIZE, MAX_WORD_LENGTH, WORDS_MAP


if TYPE_CHECKING:
    from utils.trie import SharedGridArray, Grid


TRIE_INSTANCE = Trie(GRID, ROW_LENGTH, WINDOW_SIZE, MAX_WORD_LENGTH)  # type: Trie


def test__load_grid(benchmark) -> None:
    result = benchmark(TRIE_INSTANCE._load_grid, grid=GRID)  # type: SharedGridArray
    assert isinstance(result, Array)


def test__format_grid(benchmark) -> None:
    size = TRIE_INSTANCE._axis_length**2
    result = benchmark(TRIE_INSTANCE._format_grid, grid=GRID, size=size)  # type: Grid
    assert isinstance(result, ndarray)


def test__fill_trie(benchmark) -> None:
    benchmark(TRIE_INSTANCE._fill_trie, window_size=WINDOW_SIZE, max_word=MAX_WORD_LENGTH)


class FakePool:
    def __init__(self, pool_length: int):
        self._pool = [0]*pool_length  # type List[int]


POOL = FakePool(10)  # type: FakePool
RANGES = range(0, TRIE_INSTANCE._axis_length, WINDOW_SIZE)  # type: range


def test__calculate_chunks(benchmark) -> None:
    result = benchmark(TRIE_INSTANCE._calculate_chunksize, pool=POOL, ranges=RANGES)  # type: int
    assert result == 1


@mark.parametrize('word, expected', WORDS_MAP.items())
def test___contains__(benchmark, word: str, expected: bool) -> None:
    result = benchmark(TRIE_INSTANCE.__contains__, word=word)  # type: bool
    assert result == expected

from typing import TYPE_CHECKING
from numpy import fromstring, frombuffer, copyto
from ctypes import c_char
from multiprocessing import Pool, RawArray
from itertools import product


if TYPE_CHECKING:
    from typing import List, Set, Tuple, Type

    from ctypes import _CDataMeta as CType
    from multiprocessing.pool import Pool as PoolType
    from multiprocessing.sharedctypes import _Array as SharedArray

    from numpy import ndarray

    SharedGridArray = SharedArray
    GridType = Tuple[CType, Tuple[int]]
    GridShape = Tuple[int, int]
    Grid = Type[ndarray]
    Range = Tuple[int, int]


GRID = 'bgvtt zpibu vxzft oakis fvqwl'
AXIS_LENGTH = 5  # type: int
WINDOW_SIZE = 5  # type: int
MAX_WORD_LENGTH = 24  # type: int


class TrieDict(dict):

    def add_children(self, children: 'Grid') -> None:
        if children.size != 0:
            self.add_child(children[0], children[1:])

    def add_child(self, character: bytes, children: 'Grid') -> None:
        character_string = character.decode('utf-8')

        try:
            node = self[character_string]  # type: TrieDict
        except KeyError:
            node = TrieDict()  # type: TrieDict

        node.add_children(children)

        self[character_string] = node

    def __ior__(self, other: 'TrieDict') -> 'TrieDict':
        both = self.keys() & other.keys()  # type: Set[str]
        for child in both:
            self[child] |= other[child]

        unique = other.keys() - both  # type: Set[str]
        for child in unique:
            self[child] = other[child]

        return self

    def __contains__(self, word: 'List[str]') -> bool:
        character, *remaining = word
        if character in self.keys():
            if remaining:
                return remaining in self[character]
            else:
                return True
        else:
            return False


def init_window(grid: 'SharedGridArray', array_shape: 'GridShape', array_dtype: 'GridType') -> None:
    global shared_grid, shape, dtype
    shared_grid = grid
    shape = array_shape
    dtype = array_dtype


def iterate_window(ranges: 'Range') -> 'TrieDict':
    global shared_grid, shape, dtype
    grid = frombuffer(shared_grid, dtype=dtype).reshape(shape)  # type: Grid

    x, y = ranges
    node = TrieDict()  # type: TrieDict
    for i in range(x, x + WINDOW_SIZE):
        for j in range(y, y + WINDOW_SIZE):
            node.add_children(grid[i, j:min(AXIS_LENGTH, j + MAX_WORD_LENGTH)])
            node.add_children(grid[i:min(AXIS_LENGTH, i + MAX_WORD_LENGTH), j])

    return node


class Trie:

    def __init__(self, grid: str, axis_length: int = AXIS_LENGTH, window_size: int = WINDOW_SIZE) -> None:
        self._axis_length = axis_length  # type: int
        self._shape = (axis_length,)*2  # type: GridShape
        self._dtype = (c_char, (1,))  # type: GridType
        self._grid = self._load_grid(grid)  # type: SharedGridArray
        self._root = TrieDict()  # type: TrieDict
        self._fill_trie(window_size)

    def _load_grid(self, grid: str) -> 'SharedGridArray':
        size = self._axis_length**2

        grid_array = RawArray(c_char, size)  # type: SharedGridArray
        shared_grid = frombuffer(
            grid_array,
            dtype=self._dtype,
        ).reshape(self._shape)  # type: Grid
        copyto(shared_grid, self._format_grid(grid, size))

        return grid_array

    def _format_grid(self, grid: str, size: int) -> 'Grid':
        return fromstring(
            grid,
            dtype=self._dtype,
            count=size,
        ).reshape(self._shape)

    def _fill_trie(self, window_size: int) -> None:
        window_ranges = list(product(
            range(0, self._axis_length, window_size),
            range(0, self._axis_length, window_size),
        ))  # List[Range]

        with Pool(initializer=init_window, initargs=(self._grid, self._shape, self._dtype)) as pool:
            chunk_size = self._calculate_chunksize(pool, window_ranges)  # type: int

            for node in pool.imap_unordered(iterate_window, window_ranges, chunksize=chunk_size):
                self._root |= node

    def _calculate_chunksize(self, pool: 'PoolType', ranges: 'List[Range]') -> int:
        chunk_size, extra = divmod(len(ranges), len(pool._pool) * 4)
        if extra:
            chunk_size += 1

        return chunk_size

    def __contains__(self, word: str) -> bool:
        return list(word) in self._root


def read_grid() -> str:
    return GRID.replace(' ', '')


if __name__ == '__main__':
    trie = Trie(read_grid())

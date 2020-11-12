from typing import TYPE_CHECKING
from numpy import fromstring, frombuffer, copyto
from ctypes import c_char
from multiprocessing import Pool, RawArray
from itertools import product


if TYPE_CHECKING:
    from typing import List, Set, Tuple, Type
    from typing_extensions import TypedDict
    from ctypes import _CDataMeta as CType
    from multiprocessing.pool import Pool as PoolType
    from multiprocessing.sharedctypes import _Array as SharedArray

    from numpy import ndarray

    SharedGridArray = SharedArray
    GridDType = Tuple[CType, Tuple[int]]
    GridShape = Tuple[int, int]
    Grid = Type[ndarray]
    Range = Tuple[int, int]
    GridInfo = TypedDict(
        'GridInfo',
        {
            'grid': SharedGridArray,
            'shape': GridShape,
            'dtype': GridDType,
            'window': int,
            'axis': int,
            'max': int,
        },
    )


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


def init_window(grid_info: 'GridInfo') -> None:
    global shared_grid, shape, dtype, window_size, axis_length, max_word
    shared_grid = grid_info.get('grid')
    shape = grid_info.get('shape')
    dtype = grid_info.get('dtype')
    window_size = grid_info.get('window')
    axis_length = grid_info.get('axis')
    max_word = grid_info.get('max')


def iterate_window(ranges: 'Range') -> 'TrieDict':
    global shared_grid, shape, dtype, window_size, axis_length, max_word
    grid = frombuffer(shared_grid, dtype=dtype).reshape(shape)  # type: Grid

    x, y = ranges
    node = TrieDict()  # type: TrieDict
    for i in range(x, x + window_size):
        for j in range(y, y + window_size):
            node.add_children(grid[i, j:min(axis_length, j + max_word)])
            node.add_children(grid[i:min(axis_length, i + max_word), j])

    return node


class Trie:

    def __init__(self, grid: str, axis_length: int, window_size: int, max_word: int) -> None:
        self._axis_length = axis_length  # type: int
        self._shape = (axis_length,)*2  # type: GridShape
        self._dtype = (c_char, (1,))  # type: GridDType
        self._grid = self._load_grid(grid)  # type: SharedGridArray
        self._root = TrieDict()  # type: TrieDict
        self._fill_trie(window_size, max_word)

    def _load_grid(self, grid: str) -> 'SharedGridArray':
        size = self._axis_length**2
        if len(grid) != size:
            raise RuntimeError("Not enough words!")

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

    def _fill_trie(self, window_size: int, max_word: int) -> None:
        window_ranges = list(product(
            range(0, self._axis_length, window_size),
            range(0, self._axis_length, window_size),
        ))  # List[Range]

        grid_info = {
            'grid': self._grid,
            'shape': self._shape,
            'dtype': self._dtype,
            'window': window_size,
            'axis': self._axis_length,
            'max': max_word,
        }  # type: GridInfo

        with Pool(initializer=init_window, initargs=(grid_info,)) as pool:
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

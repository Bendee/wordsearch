from typing import TYPE_CHECKING
from ctypes import c_char
from itertools import product
from multiprocessing import Pool, RawArray

from numpy import fromstring, frombuffer, copyto


if TYPE_CHECKING:
    from typing import List, Set, Tuple, Type
    from typing_extensions import TypedDict
    from ctypes import Array, _CDataMeta as CType
    from multiprocessing.pool import Pool as PoolType

    from numpy import ndarray

    SharedGridArray = Array[c_char]
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
        """ Recursively add an array of children. """
        if children.size != 0:
            self.add_child(children[0], children[1:])

    def add_child(self, character: bytes, children: 'Grid') -> None:
        """ Add a child and its children. """
        character_string = character.decode('utf-8')

        try:
            node = self[character_string]  # type: TrieDict
        except KeyError:
            node = TrieDict()  # type: TrieDict

        node.add_children(children)

        self[character_string] = node

    def __or__(self, other: 'TrieDict') -> 'TrieDict':
        """ Merge two TrieDicts.

        Keeps the structure of both intact.
        """
        both = self.keys() & other.keys()  # type: Set[str]
        for child in both:
            node = self[child] | other[child]  # type: TrieDict
            self[child] = node

        unique = other.keys() - both  # type: Set[str]
        for child in unique:
            node = other[child]  # type: TrieDict
            self[child] = node

        return self

    def __contains__(self, word: 'List[str]') -> bool:
        """ Checks if a word is contained within the TrieDict. """
        character, *remaining = word
        if character in self.keys():
            if remaining:
                return remaining in self[character]
            else:
                return True
        else:
            return False


def _init_window(grid_info: 'GridInfo') -> None:
    """ Share the constant variables with the workers via inheritance. """
    global shared_grid, shape, dtype, window_size, axis_length, max_word
    shared_grid = grid_info.get('grid')
    shape = grid_info.get('shape')
    dtype = grid_info.get('dtype')
    window_size = grid_info.get('window')
    axis_length = grid_info.get('axis')
    max_word = grid_info.get('max')


def _iterate_window(ranges: 'Range') -> 'TrieDict':
    """Iterate through a given range and generate a Trie for that range. """
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

        self._fill_trie(window_size, max_word)

    def _load_grid(self, grid: str) -> 'SharedGridArray':
        """ Load the grid into shared memory. """
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
        """ Load the grid from the string. """
        return fromstring(
            grid,
            dtype=self._dtype,
            count=size,
        ).reshape(self._shape)

    def _fill_trie(self, window_size: int, max_word: int) -> None:
        """ Fill the trie with the possible words from the grid. """
        self._root = TrieDict()  # type: TrieDict

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

        i = 0
        print('Iterating through windows.')
        print('WARNING: This can take a while!')
        with Pool(initializer=_init_window, initargs=(grid_info,)) as pool:
            chunk_size = self._calculate_chunksize(pool, window_ranges)  # type: int

            for node in pool.imap_unordered(_iterate_window, window_ranges, chunksize=chunk_size):
                i += 1

                print('Merging node:', i, end='\r')
                self._root = self._root | node
            print('.'*16, end='\r')
            print('Merging: Done')

        pool.join()

    def _calculate_chunksize(self, pool: 'PoolType', ranges: 'List[Range]') -> int:
        """ Calculate the chunk size to use for batching processes. """
        chunk_size, extra = divmod(len(ranges), len(pool._pool) * 4)
        if extra:
            chunk_size += 1

        return chunk_size

    def __contains__(self, word: str) -> bool:
        """ Check if the word is contained within the Trie. """
        return list(word) in self._root

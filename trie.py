from typing import TYPE_CHECKING
from numpy import fromstring, frombuffer, copyto
from ctypes import c_char
from multiprocessing import Pool, RawArray
from itertools import product


if TYPE_CHECKING:
    from typing import List, Set, Tuple


GRID = 'bgvtt zpibu vxzft oakis fvqwl'
AXIS_LENGTH = 5  # type: int
WINDOW_SIZE = 5  # type: int
MAX_WORD_LENGTH = 24  # type: int


class TrieDict(dict):

    def add_children(self, children: 'List[bytes]'):
        if children.size != 0:
            self.add_child(children[0], children[1:])

    def add_child(self, character: bytes, children: 'List[bytes]') -> None:
        character_string = character.decode('utf-8')

        try:
            node = self[character_string]  # type: TrieDict
        except KeyError:
            node = TrieDict()

        node.add_children(children)

        self[character_string] = node

    def __add__(self, other: 'TrieDict') -> 'TrieDict':
        both = self.keys() & other.keys()  # type: Set[str]
        for child in both:
            node = self[child] + other[child]  # type: TrieDict
            self[child] = node

        unique = other.keys() - both  # type: Set[str]
        for child in unique:
            node = other[child]  # type: TrieDict
            self[child] = node

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


def init_window(grid, shape_list) -> None:
    global shared_grid, shape
    shared_grid = grid
    shape = shape_list


def iterate_window(args: 'Tuple[int, int]') -> 'TrieDict':
    global shared_grid, shape
    grid = frombuffer(shared_grid, dtype=(c_char, (1,))).reshape(shape)
    x, y = args
    node = TrieDict()
    for i in range(x, x + WINDOW_SIZE):
        for j in range(y, y + WINDOW_SIZE):
            node.add_children(grid[i, j:min(AXIS_LENGTH, j + MAX_WORD_LENGTH)])
            node.add_children(grid[i:min(AXIS_LENGTH, i + MAX_WORD_LENGTH), j])

    return node


class Trie:

    def __init__(self, grid: str, axis_length: int = AXIS_LENGTH, window_size: int = WINDOW_SIZE) -> None:
        self._axis_length = axis_length  # type: int
        self._shape = [axis_length]*2  # type: List[int]
        self._dtype = (c_char, (1,))  # type: Tuple[c_char, Tuple[int]]
        self._grid = self._load_grid(grid)
        self._trie = self._generate_trie(window_size)  # type: TrieDict

    def _load_grid(self, grid: str):
        size = self._axis_length**2

        grid_array = RawArray(c_char, size)
        shared_grid = frombuffer(grid_array, dtype=self._dtype).reshape(self._shape)
        copyto(shared_grid, self._format_grid(grid))

        return grid_array

    def _format_grid(self, grid: str, size: int):
        return fromstring(
            grid,
            dtype=self._dtype,
            count=size,
        ).reshape(self._shape)

    def _generate_trie(self, window_size: int) -> TrieDict:
        window_ranges = product(
            range(0, self._axis_length, window_size),
            range(0, self._axis_length, window_size),
        )

        with Pool(initializer=init_window, initargs=(self._grid, self._shape)) as pool:
            nodes = pool.map(iterate_window, window_ranges)

        return sum(nodes, TrieDict())

    def __contains__(self, word: str) -> bool:
        return list(word) in self._trie


def read_grid() -> str:
    return GRID.replace(' ', '')


if __name__ == '__main__':
    trie = Trie(read_grid())

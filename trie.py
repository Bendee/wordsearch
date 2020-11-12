from typing import TYPE_CHECKING
from numpy import fromstring, frombuffer, copyto
from ctypes import c_char
from multiprocessing import Pool, RawArray
from itertools import product


if TYPE_CHECKING:
    from typing import Dict, List, Set, Tuple, Union


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

    def __contains__(self, word: 'Union[str, List[str]]') -> bool:
        character, *remaining = word
        if character in self.keys():
            if remaining:
                return remaining in self[character]
            else:
                return True
        else:
            return False


def init_window(grid, shape):
    shared_grid = grid
    shape = shape


def iterate_window(args: 'Tuple[int, int]') -> 'TrieDict':
    grid = frombuffer(shared_grid, dtype=(c_char, (1,))).reshape(shape)
    x, y = args
    node = TrieDict()
    for i in range(x, x + WINDOW_SIZE):
        for j in range(y, y + WINDOW_SIZE):
            node.add_children(grid[i, j:min(AXIS_LENGTH, j + MAX_WORD_LENGTH)])
            node.add_children(grid[i:min(AXIS_LENGTH, i + MAX_WORD_LENGTH), j])

    return node


def read_grid() -> str:
    return GRID.replace(' ', '')


def format_grid(grid: str, shape: 'List[int]') -> 'List[List[str]]':
    return fromstring(grid, dtype=(c_char, (1,)), count=AXIS_LENGTH**2).reshape(shape)


if __name__ == '__main__':
    shape = [AXIS_LENGTH]*2
    grid_string = read_grid()
    shared_grid = RawArray(c_char, AXIS_LENGTH**2)
    grid = frombuffer(shared_grid, dtype=(c_char, (1,))).reshape(shape)
    copyto(grid, format_grid(grid_string, shape))

    window_ranges = product(
        range(0, AXIS_LENGTH, WINDOW_SIZE),
        range(0, AXIS_LENGTH, WINDOW_SIZE),
    )

    with Pool(initializer=init_window, initargs=(shared_grid, shape)) as pool:
        nodes = pool.map(iterate_window, window_ranges)
    trie = sum(nodes, TrieDict())

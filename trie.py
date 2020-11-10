from typing import TYPE_CHECKING
from numpy import fromstring, frombuffer, copyto
from ctypes import c_char
from multiprocessing import Pool, RawArray
from itertools import product

if TYPE_CHECKING:
    from typing import Dict, List, Tuple, Union

    ChildMap = Dict[str, 'TrieNode']


GRID = 'bgvtt zpibu vxzft oakis fvqwl'
AXIS_LENGTH = 5  # type: int
MAX_WORD_LENGTH = 24  # type: int


class TrieNode:

    def __init__(self, character: str) -> None:
        self.character = character  # type: str
        self._children = {}  # type: ChildMap

    def __contains__(self, string: 'Union[str, List[str]]') -> bool:
        character, *remaining = string
        if character in self._children:
            if remaining:
                return remaining in self._children[character]
            else:
                return True
        else:
            return False

    def __add__(self, other: 'TrieNode') -> 'TrieNode':
        if self.character != other.character:
            raise ValueError('Characters do not match')

        both = self._children.keys() & other._children.keys()
        unique = other._children.keys() - both  # type: set[str]
        for child in both:
            node = self._children[child] + other._children[child]
            self._children[child] = node

        for child in unique:
            self._children[child] = other._children[child]

        return self

    def append(self, character: bytes, children: 'List[str]') -> None:
        character_string = character.decode('utf-8')
        node = self._children.get(character_string) or TrieNode(character_string)

        node.add_children(children)

        self._children[character_string] = node

    def add_children(self, children):
        if children.size != 0:
            self.append(children[:1][0], children[1:])


def init_window(grid, shape):
    shared_grid = grid
    shape = shape


def iterate_window(args: 'Tuple[int, int]') -> TrieNode:
    grid = frombuffer(shared_grid, dtype=(c_char, (1,))).reshape(shape)
    x, y = args
    node = TrieNode('')
    for i in range(x, x + 2):
        for j in range(y, y + 2):
            node.add_children(grid[i, j:min(AXIS_LENGTH, j + MAX_WORD_LENGTH)])
            node.add_children(grid[i:min(AXIS_LENGTH, i + MAX_WORD_LENGTH), j])

    return node


def read_grid() -> str:
    return GRID.replace(' ', '')


def format_grid(grid: str, shape: 'List[int]') -> 'List[List[str]]':
    return fromstring(grid, dtype=(c_char, (1,)), count=AXIS_LENGTH**2).reshape(shape)


if __name__ == '__main__':
    window_size = 2

    shape = [AXIS_LENGTH]*2
    grid_string = read_grid()
    shared_grid = RawArray(c_char, AXIS_LENGTH**2)
    grid = frombuffer(shared_grid, dtype=(c_char, (1,))).reshape(shape)
    copyto(grid, format_grid(grid_string, shape))

    window_ranges = product(
        range(0, AXIS_LENGTH, window_size),
        range(0, AXIS_LENGTH, window_size),
    )
    with Pool(4, initializer=init_window, initargs=(shared_grid, shape)) as pool:
        nodes = pool.map(iterate_window, window_ranges)

    trie = sum(nodes[1:], nodes[0])

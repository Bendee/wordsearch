from typing import TYPE_CHECKING
from numpy import fromstring, reshape
from ctypes import c_char
from itertools import product

if TYPE_CHECKING:
    from typing import Dict, List, Tuple

    ChildMap = Dict[str, 'TrieNode']


GRID = 'bgvtt zpibu vxzft oakis fvqwl'
AXIS_LENGTH = 5  # type: int
MAX_WORD_LENGTH = 24  # type: int


class TrieNode:

    def __init__(self, character: str) -> None:
        self.character = character  # type: str
        self._children = {}  # type: ChildMap

    def __contains__(self, string: 'List[str]'):
        character, *remaining = string
        if character in self._children:
            if remaining:
                return remaining in self._children[character]
            else:
                return True
        else:
            return False

    def append(self, character: bytes, children: 'List[str]') -> None:
        character_string = character.decode('utf-8')
        node = self._children.get(character_string) or TrieNode(character_string)

        if children.size != 0:
            node.append(children[:1][0], children[1:])

        self._children[character_string] = node


def iterate_window(args: 'Tuple[int, int]'):
    x, y = args
    for i in range(x, x + 2):
        for j in range(y, y + 2):
            character = grid[i, j]
            trie.append(character, grid[i, j+1:min(AXIS_LENGTH, j + MAX_WORD_LENGTH)])
            trie.append(character, grid[i+1:min(AXIS_LENGTH, i + MAX_WORD_LENGTH), j])


def read_grid() -> str:
    return GRID.replace(' ', '')


def format_grid(grid: str) -> 'List[List[str]]':
    return reshape(
        fromstring(grid, dtype=(c_char, (1,)), count=AXIS_LENGTH**2),
        [AXIS_LENGTH]*2,
    )


if __name__ == '__main__':
    grid = format_grid(read_grid())
    trie = TrieNode('')
    window_ranges = [
        (i, j)
        for i, j in product(range(0, AXIS_LENGTH, 2), range(0, AXIS_LENGTH, 2))
    ]
    for window_range in window_ranges:
        iterate_window(window_range)

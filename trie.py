from typing import TYPE_CHECKING
from numpy import fromstring, reshape

if TYPE_CHECKING:
    from typing import Dict, List

    ChildMap = Dict[str, 'TrieNode']


GRID = 'bgvtt zpibu vxzft oakis fvqwl'
AXIS_LENGTH = 5  # type: int
MAX_WORD_LENGTH = 24  # type: int


class TrieNode:

    def __init__(self, character: str) -> None:
        self.character = character  # type: str
        self._children = {}  # type: ChildMap

    def append(self, character: str, children: 'List[str]') -> None:
        node = self._children.get(character) or TrieNode(character)

        if children.size != 0:
            node.append(children[:1][0], children[1:])

        self._children[character] = node


class Trie:

    def __init__(self, grid: 'List[List[str]]') -> None:
        self.root = TrieNode('')
        self.grid = grid

        for row in self.grid:
            self.iterate_axis(row)
        for column in self.grid.T:
            self.iterate_axis(column)

    def iterate_axis(self, axis: 'List[str]'):
        for index, character in enumerate(axis):
            self.root.append(
                character,
                axis[index+1:min(AXIS_LENGTH, index + MAX_WORD_LENGTH)],
            )


def read_grid() -> str:
    return GRID.replace(' ', '')


def format_grid(grid: str) -> 'List[List[str]]':
    return reshape(
        fromstring(grid, dtype='S1', count=AXIS_LENGTH**2),
        [AXIS_LENGTH]*2,
    )


if __name__ == '__main__':
    trie = Trie(format_grid(read_grid()))  # type: Trie

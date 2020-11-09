from typing import TYPE_CHECKING
from numpy import fromstring, reshape
from ctypes import c_char

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



class Trie:

    def __init__(self, grid: 'List[List[str]]') -> None:
        self.root = TrieNode('')
        self.grid = grid

        for row in self.grid:
            self.iterate_axis(row)
        for column in self.grid.T:
            self.iterate_axis(column)

    def __contains__(self, string: str) -> bool:
        return list(string) in self.root

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
        fromstring(grid, dtype=(c_char, (1,)), count=AXIS_LENGTH**2),
        [AXIS_LENGTH]*2,
    )


if __name__ == '__main__':
    trie = Trie(format_grid(read_grid()))  # type: Trie

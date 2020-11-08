from typing import TYPE_CHECKING
from numpy import fromstring, reshape

if TYPE_CHECKING:
    from typing import Dict, List

    ChildMap = Dict[str, 'TrieNode']


GRID = 'bgvtt zpibu vxzft oakis fvqwl'
AXIS_LENGTH = 5  # type: int


class TrieNode:

    def __init__(self, character: str) -> None:
        self.character = character  # type: str
        self._children = {}  # type: ChildMap


def format_grid(grid: str) -> 'List[List[str]]':
    return reshape(
        fromstring(grid, dtype='S1', count=AXIS_LENGTH**2),
        [AXIS_LENGTH]*2,
    )

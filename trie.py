from typing import TYPE_CHECKING
from numpy import fromstring, reshape

if TYPE_CHECKING:


GRID = 'bgvtt zpibu vxzft oakis fvqwl'
AXIS_LENGTH = 5  # type: int


def format_grid(grid: str) -> 'List[List[str]]':
    return reshape(
        fromstring(grid, dtype='S1', count=AXIS_LENGTH**2),
        [AXIS_LENGTH]*2,
    )

from typing import TYPE_CHECKING
from ctypes import c_wchar_p
from itertools import product
from multiprocessing import Pool, RawArray


if TYPE_CHECKING:
    from typing import List, Tuple
    from typing_extensions import TypedDict
    from multiprocessing.sharedctypes import _Array as SharedArray

    SharedAxes = SharedArray
    Axes = Tuple[str, ...]
    AxesInfo = TypedDict(
        'AxesInfo',
        {
            'rows': SharedAxes,
            'columns': SharedAxes,
            'window': int,
        },
    )


def share_axes(axes_info: 'AxesInfo') -> None:
    """ Load axes from memory and share them with workers """
    global axes, window_size
    axes = tuple(
        tuple(axis)
        for axis in (axes_info.get('rows'), axes_info.get('columns'))
    )  # type: Tuple[Axes, ...]
    window_size = axes_info.get('info')  # type: int


def contains_word(word: str, search_index: int) -> bool:
    """ Check if word is contained in axes."""
    global axes
    for axis in axes:
        for index in range(search_index, search_index + WINDOW_SIZE):
            if word in axis[index]:
                return True

    return False


class Grid:

    def __init__(self, grid: str, axis_length: int, window_size: int) -> None:
        self._axis_length = axis_length  # type: int
        self._window_size = window_size  # type: int

        print('Loading Grid: ...', end='\r')
        if len(grid) != self._axis_length**2:
            raise RuntimeError('grid is not the right size!')

        self.rows = self._generate_rows(grid)  # type: Axes
        self.columns = self._generate_columns()  # type: Axes

        self._shared_rows = self._share_axes(self.rows)  # type:SharedAxes
        self._shared_columns = self._share_axes(self.columns)  # type: SharedAxes
        print('Loading Grid: DONE')

    def _generate_rows(self, grid: str) -> 'Axes':
        """ Split grid into rows. """
        return tuple(
            grid[self._axis_length*row:self._axis_length*(row + 1)]
            for row in range(self._axis_length)
        )

    def _generate_columns(self) -> 'Axes':
        """ Transpose rows to get columns. """
        return tuple(
            ''.join(column)
            for column in zip(*self.rows)
        )

    def _share_axes(self, axes: 'Axes') -> 'SharedAxes':
        """ Create in memory array for storing and sharing axes. """
        return RawArray(c_wchar_p, axes)

    def linear_search(self, word: str) -> bool:
        """ Iterates through rows and columns and checks for word presence. """
        for row, column in zip(self.rows, self.columns):
            if word in row:
                return True
            elif word in column:
                return True
        return False

    def multiprocess_search(self, word: str) -> bool:
        """ Splits axes up and checks for word presence using multiple processes. """
        axes_info = {
            'rows': self._shared_rows,
            'columns': self._shared_columns,
            'window': self._window_size,
        }  # type: AxesInfo

        with Pool(initializer=share_axes, initargs=(axes_info,)) as pool:
            results = pool.starmap(
                contains_word,
                product(
                    (word,),
                    range(0, self._axis_length, self._window_size),
                ),
            )  # type: List[bool]

            return any(results)

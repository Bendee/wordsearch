from typing import TYPE_CHECKING

from utils.files import read_grid, read_words

from tests.data import GRID_FILE, GRID, WORDS_FILE, WORDS


if TYPE_CHECKING:
    from typing import List


def test_read_grid(benchmark) -> None:
    grid = benchmark(read_grid, path=str(GRID_FILE))  # type: str
    assert grid == GRID

def test_read_words(benchmark) -> None:
    words = benchmark(read_words, path=str(WORDS_FILE))  # type: List[str]
    assert words == WORDS

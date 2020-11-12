from pytest import mark

from wordsearch import WordSearch, read_grid


if TYPE_CHECKING:
    from typing import Dict, List


GRID_FILE = 'grid.txt'  # type: str
WORD_FILE = 'words.txt'  # type: str
NEW_GRID = not Path(GRID_FILE).exists()  # type: bool
ROW_LENGTH = 100  # type: int
WINDOW_SIZE = 50  # type: int










GRID_STRING = read_grid(GRID_FILE)  # type: str
WS = WordSearch(GRID_STRING, axis_length=ROW_LENGTH)  # type: WordSearch
WORDS = get_words()  # type: Dict[str, bool]

if NEW_GRID:
    write_words(list(get_words(400).keys()))


def test_read_grid(benchmark) -> None:
    benchmark(read_grid, path=GRID_FILE)


@mark.parametrize("word, expected", WORDS.items())
def test_is_present(benchmark, word: str, expected: bool) -> None:
    result = benchmark(WS.is_present, word=word)  # type: bool
    assert result == expected

from typing import TYPE_CHECKING

from pytest import mark

from wordsearch import WordSearch
from utils import Grid, Trie

from tests.data import GRID, ROW_LENGTH, WINDOW_SIZE, WORDS_MAP


if TYPE_CHECKING:
    from typing import Type, Union

    DataType = Union[Type[Grid], Type[Trie]]


WS = WordSearch(GRID, axis_length=ROW_LENGTH)  # type: WordSearch


@mark.parametrize('use_trie, expected_type', {False: Grid, True: Trie})
def test_data_generation(benchmark, use_trie: bool, expected_type: 'DataType') -> None:
    wordsearch = benchmark(
        WordSearch,
        grid=GRID,
        use_trie=use_trie,
        axis_length=ROW_LENGTH,
        window_size=WINDOW_SIZE,
    )  # type: WordSearch
    assert isinstance(wordsearch._data, expected_type)


@mark.parametrize("word, expected", WORDS_MAP.items())
def test_is_present(benchmark, word: str, expected: bool) -> None:
    result = benchmark(WS.is_present, word=word)  # type: bool
    assert result == expected

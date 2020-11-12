from typing import TYPE_CHECKING
from json import load
from math import sqrt


if TYPE_CHECKING:
    from typing import Dict, Iterable

    WordMap = Dict[str, bool]


def _load_file(path: str) -> 'Iterable[str]':
    with open(path, 'r') as file:
        lines = iter(
            line.strip()
            for line in file
        )  # type: Iterable[str]

    return lines

def _load_json(path: str) -> 'WordMap':
    with open(path, 'r') as file:
        json = load(file)  # type: WordMap

    return json


GRID_FILE = 'test_grid.txt'  # type: str
WORDS_FILE = 'test_words.txt'  # type: str
_WORDS_JSON = 'test_words.json'  # type: str
WINDOW_SIZE = 100  # type: int

GRID = ''.join(_load_file(GRID_FILE))  # type: str
ROW_LENGTH = int(sqrt(len(GRID)))  # type: int
WORDS = _load_file(WORDS_FILE)  # type: Iterable[str]
WORDS_MAP = _load_json(_WORDS_JSON)  # type: WordMap

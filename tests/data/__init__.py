from typing import TYPE_CHECKING
from json import load
from math import sqrt


if TYPE_CHECKING:
    from typing import Dict, List
    from typing_extensions import TypedDict

    WordMap = Dict[str, bool]
    WordsMaps = TypedDict(
        'WordsMaps',
        {
            'all': WordMap,
            'index_100': WordMap,
        }
    )


def _load_file(path: str) -> 'List[str]':
    with open(path, 'r') as file:
        lines = [
            line.strip()
            for line in file
        ]  # type: List[str]

    return lines

def _load_json(path: str) -> 'WordsMaps':
    with open(path, 'r') as file:
        json = load(file)  # type: WordsMaps

    return json


GRID_FILE = 'tests/data/test_grid.txt'  # type: str
WORDS_FILE = 'tests/data/test_words.txt'  # type: str
_WORDS_JSON = 'tests/data/test_words.json'  # type: str
WINDOW_SIZE = 100  # type: int
MAX_WORD_LENGTH = 10  # type: int

GRID = ''.join(_load_file(GRID_FILE))  # type: str
ROW_LENGTH = int(sqrt(len(GRID)))  # type: int
WORDS = _load_file(WORDS_FILE)  # type: List[str]

_WORDS_MAPS = _load_json(_WORDS_JSON)  # type: WordsMaps
WORDS_MAP = _WORDS_MAPS['all']  # type: WordMap
WINDOW_WORDS = _WORDS_MAPS['index_100']  # type: WordMap

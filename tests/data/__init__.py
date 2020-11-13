from typing import TYPE_CHECKING
from json import load
from math import sqrt
from pathlib import Path


if TYPE_CHECKING:
    from typing import Any, Dict, List, Union
    from typing_extensions import TypedDict

    WordMap = Dict[str, bool]
    WordsMaps = TypedDict(
        'WordsMaps',
        {
            'all': WordMap,
            'index_100': WordMap,
        }
    )


def _load_file(path: Path) -> 'List[str]':
    with path.open('r') as file:
        lines = [
            line.strip()
            for line in file
        ]  # type: List[str]

    return lines

def _load_json(path: Path) -> 'Dict[str, Any]':
    with path.open('r') as file:
        json = load(file)  # type: Dict[str, Any]

    return json


_TEST_DIR = Path(__file__).parent  # type: Path

GRID_FILE = _TEST_DIR / 'grid.txt'  # type: Path
WORDS_FILE = _TEST_DIR / 'words.txt'  # type: Path
_WORDS_JSON = _TEST_DIR / 'words.json'  # type: Path
_TRIE_JSON = _TEST_DIR / 'trie.json'  # type: Path

WINDOW_SIZE = 100  # type: int
MAX_WORD_LENGTH = 5  # type: int

GRID = ''.join(_load_file(GRID_FILE))  # type: str
ROW_LENGTH = int(sqrt(len(GRID)))  # type: int
WORDS = _load_file(WORDS_FILE)  # type: List[str]

_WORDS_MAPS = _load_json(_WORDS_JSON)  # type: WordsMaps
WORDS_MAP = _WORDS_MAPS['all']  # type: WordMap
WINDOW_WORDS = _WORDS_MAPS['index_100']  # type: WordMap

_TRIES = _load_json(_TRIE_JSON)
TRIE_NODE = _TRIES['node']  # type: Dict[str, Any]
GRID_TRIE = _TRIES['grid']  # type: Dict[str, Any]
TRIES = _TRIES['tries']  # type: List[List[Union[List[str], Dict[str, Any]]]]

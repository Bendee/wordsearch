# Wordsearch
A tool to search a grid given as a text file for words present in a file.

## Contents
 - [Wordsearch](#wordsearch)
   - [Contents](#contents)
   - [Usage](#usage)
   - [Implementation Details](#implementation-details)
     - [Grid](#grid)
       - [Advantages/Disadvantages](#advantagesdisadvantages)
       - [Recommended Usage](#recommended-usage)
     - [Trie](#trie)
       - [Advantages/Disadvantages](#advantagesdisadvantages-1)
       - [Recommended Usage](#recommended-usage-1)
   - [Test Data](#test-data)

## Usage
```
wordsearch.py [-h] [--trie] [--multiprocess] grid words
```
with the following arguments:
 - Positional:
   - `grid`: The file containing the grid of words
   - `words`: The list of words to check
 - Optional:
   - `--trie`: Use trie data structure.
   - `--multiprocess`: Use multiple processes to search for words/generate Trie.


## Implementation Details
### Grid
Implemented in `utils/grid.py` this splits the grid into a list of rows and
also transposes them to get a list of columns.

Word presence is then checked using Python's `in` statement on each row &
column until the word is found or all rows & columns have been searched.
#### Advantages/Disadvantages
 - Initialisation is relatively quick.
   Transposing rows is the most intensive operation.
 - Grid has to be searched for every word.
 - Multiprocessing implementation is slower.
   I have been unable to fix this.
#### Recommended Usage
In my opinon you should use this without the `--multiprocessing` flag
for the best results

### Trie
Implemented in `utils/trie.py` this iterates through the grid, extracting
the possible words at each point and storing them in the form of a
[Trie](https://wikipedia.org/wiki/Trie).

Word presence is then checked by descending the Trie until all letters in
the word have been found or the next letter can't be found.
#### Advantages/Disadvantages
  - Search is quite quick as it has essentially 'found' all words already.
  - Entire grid is processed even if looking for one word.
  - Processing grid is quite resource intesive and can taka a long time.
#### Recommended Usage
**Don't**. This is sadly the worst option by far. Use Grid.
Although I do admit I did find this one the most interesting to implement.

If you *have* to use this use it with the `--multiprocessing` flag.


## Test Data
There is a test grid with a words file in `tests/data`.
However, these require setting the `ROW_LENGTH` to 1000.

These were generated using `utils/generation.py`.
For usage run `utils/generation.py --help`.

#! /usr/bin/env python3


class WordSearch(object):

    def __init__(self, grid):
        pass

    def is_present(self, word):
        return True


if __name__ == "__main__":
    ws = WordSearch(grid)

    for word in words_to_find:
        if ws.is_present(word):
            print "found {}".format(word)
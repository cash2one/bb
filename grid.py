#!/usr/bin/env python3

import time
import collections


class Grid(object):
    """
    >>> grid = Grid(3, 4)
    >>> grid.broadcast(5)
    [1, 2, 3, 4, 5, 6, 7, 8, 9]
    >>> grid.alter(4, 5)[1] == {3, 6, 9}
    True
    """
    def __init__(self, w, h):
        self.w = w
        self.h = h
        codes = {}

        code = 1
        for j in range(h):
            for i in range(w):
                codes[(i, j)] = code
                code += 1

        units = [[]]
        _ = [-1, 0, 1]
        units.extend(
            [codes[(i + x, j + y)]
             for y in _ for x in _ if (i + x, j + y) in codes]
            for j in range(h)
            for i in range(w)
            )

        units_set = list(map(frozenset, units))

        def kv(c1, c2):
            s1 = units_set[c1]
            s2 = units_set[c2]
            return (c1, c2), ((s1 ^ s2) - s2, (s1 ^ s2) - s1)

        self.codes = codes
        self.units = units
        self.alters = dict(kv(c1, c2)
                           for c1, o in enumerate(units_set)
                           for c2 in o
                           if c1 != c2)

    def broadcast(self, code):
        return self.units[code]

    def alter(self, code1, code2):
        return self.alters[(code1, code2)]



if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()
    #g = Grid(100, 100)
    #input()

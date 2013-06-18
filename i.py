#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Skeleton + Body + ??? -> I
"""


from __future__ import division, print_function, unicode_literals

import collections

class I(collections.defaultdict):
    """
    >>> i = I(1)
    >>> i["foo"]
    5
    >>> i.bar
    []
    >>> i.xixi = set()

    """

    __slots__ = ["i"]

    def __init__(self, n):
        i = int(n)
        object.__setattr__(self, "i", i)

    def __setattr__(self, k, v):
        self[k] = v

    def __getattr__(self, k):
        return self[k]

    def __missing__(self, k):
        self[k] = object.__getattribute__(self, "_" + k)()
        return self[k]

    def _foo(self):
        return 5

    def _bar(self):
        return []

    def _foobar(self):
        return collections.Counter()


if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()

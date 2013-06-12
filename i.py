#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Skeleton + Body + ??? -> I
"""


from __future__ import division, print_function, unicode_literals

import collections

class Body(object):
    """hash(I(N)) is useful

    >>> i = Body(1)
    >>> isinstance(i._, dict)
    True
    >>> i.m = 1
    >>> i.m == i["m"] == 1
    True
    >>> "m" in i
    True
    >>> "x" in i
    False
    """

    __slots__ = ["i", "_"]
    _factory = dict

    def __init__(self, n=0):
        i = int(n)
        _ = self._factory()
        object.__setattr__(self, "i", i)
        object.__setattr__(self, "_", _)

    def __setitem__(self, k, v):
        self._[k] = v

    def __getitem__(self, k):
        return self._[k]

    def __setattr__(self, k, v):
        self._[k] = v

    def __getattr__(self, k):
        return self._[k]

    # see: reference/datamodel.html#object.__contains__
    def __iter__(self):
        return iter(self._)

    def __repr__(self):
        return str(self.i)

    def __eq__(self, other):
        return self.i == other.i

    def __hash__(self):
        return self.i

class Skeleton(collections.defaultdict):
    """Data only, ID unrelatable, offer default initial data

    >>> i = Skeleton()
    >>> i["foo"]
    5
    """
    def __missing__(self, k):
        self[k] = getattr(self, "_" + k)()
        return self[k]

    def _foo(self):
        return 5

    def _bar(self):
        return []

    def _foobar(self):
        return collections.Counter()



class I(Body):
    """Implementation

    >>> i = I(1)
    >>> isinstance(i._, Skeleton)
    True
    >>> isinstance(i.foo, int) and i.foo == 5
    True
    >>> isinstance(i.foobar, collections.Counter)
    True
    >>> i.foobar[1] = 42
    >>> i.send("move", "up") == ("send", 1, "move", "up")
    True
    >>> i.save("foo") == ("save", 1, "foo", 5)
    True
    >>> i.log("lv-up") == ("log", 1, "lv-up", None, 1)
    True
    >>> i.pay(20) == ("pay", 1, 20)
    True
    >>> list(i.save_all()) == [
    ...     ("save", 1, "foobar", {1: 42}),
    ...     ("save", 1, "foo", 5),
    ... ]
    True

    """

    _factory = Skeleton

    def summon(self, source):
        for k, v in source.items():
            wrap = getattr(self, "_wrap_%s" % k, None)
            self[k] = wrap(v) if wrap else v

    def send(self, k, v):
        return "send", self.i, k, v

    def save(self, k):
        return "save", self.i, k, self[k]

    def log(self, k, infos=None, n=1):
        return "log", self.i, k, infos, n

    def pay(self, n):
        return "pay", self.i, n

    # in Python 3.3 or above, use "yield from"
    def save_all(self):
        for k in self:
            yield self.save(k)

    @staticmethod
    def _wrap_foobar(value):
        return collections.Counter(
            {int(k) if k.isdigit() else k: v for k, v in value.items()}
            )



if __name__ == "__main__":
    import logging
    logging.basicConfig(level=logging.DEBUG,
                        format="%(asctime)s:%(levelname)s:%(message)s",
                       )
    print("doctest:")
    import doctest
    doctest.testmod()

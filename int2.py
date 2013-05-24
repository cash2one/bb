#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Skeleton + Body + ??? -> I

>>> gc.isenabled()
False

"""


from __future__ import division, print_function, unicode_literals

import collections
import functools
import gc
import glob
import json
import logging
import os
import pickle
import sys

gc.disable()

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s:%(levelname)s:%(message)s",
                   )



if sys.version_info[0] >= 3:
    open = functools.partial(open, encoding='utf-8')


class Body(int):
    """hash(I(N)) is useful

    >>> Body()
    0
    >>> i = Body(1)
    >>> i
    1
    >>> isinstance(i.my, dict)
    True
    >>> i.m = 1
    >>> i.m == i['m'] == 1
    True
    >>> i['n'] = 2
    >>> i.n == i['n'] == 2
    True
    >>> 'n' in i
    True
    >>> 'x' in i
    False
    """

    _factory = dict

    def __init__(self, n=0):
        i = int(n)
        my = self._factory()
        object.__setattr__(self, 'my', my)
        self.init()

    def init(self):
        pass

    def __setitem__(self, k, v):
        self.my[k] = v

    def __getitem__(self, k):
        return self.my[k]

    def __setattr__(self, k, v):
        self.my[k] = v

    def __getattr__(self, k):
        return self.my[k]

    # see: reference/datamodel.html#object.__contains__
    def __iter__(self):
        return iter(self.my)


class Skeleton(collections.defaultdict):
    """Data only, ID unrelatable, offer default initial data

    >>> i = Skeleton()
    >>> i['foo']
    5
    >>> i['bar']
    []
    >>> i['foobar']
    Counter()
    >>> i['void']
    Traceback (most recent call last):
        ...
    AttributeError: 'Skeleton' object has no attribute '_void'
    """
    def __missing__(self, k):
        self[k] = getattr(self, '_' + k)()
        return self[k]

    def _foo(self):
        return 5

    def _bar(self):
        return []

    def _foobar(self):
        return collections.Counter()



class I(Body):
    """Implementation definite 

    init() and save(): use json, depend on locale file system

    >>> i = I(1)
    >>> isinstance(i.my, Skeleton)
    True
    >>> isinstance(i.foo, int) and i.foo == 5
    True
    >>> isinstance(i.foobar, collections.Counter)
    True
    >>> if os.path.exists("1/foobar"):
    ...     i.foobar[1]
    ... else:
    ...     42
    42
    >>> i.foobar[1] = 42
    >>> i.save_all()
    >>> os.path.exists("1/foo")
    True
    >>> os.path.exists("1/foobar")
    True

    """

    _factory = Skeleton

    # use some source, summon a life(or a monster? haha)
    def init(self):
        log('read', int(self))

        # debug
        home = str(self)
        if not os.path.exists(home):
            os.mkdir(home)
        source = {}
        for k in os.listdir(home):
            with open("%s/%s" % (home, k)) as f:
                source[k] = json.load(f)
        self.summon(source)
        # debug

    def summon(self, source):
        for k, v in source.items():
            wrap = getattr(self, '_wrap_%s' % k, None)
            self[k] = wrap(v) if wrap else v

    def save(self, k):
        return 'write', int(self), k, self[k]

    # in Python 3.3 you can use "yield from"
    def save_all(self):
        for k in self:
            yield self.save(k)

    @staticmethod
    def _wrap_foobar(value):
        return collections.Counter({int(k): v for k, v in value.items()})



if __name__ == '__main__':
    import doctest
    doctest.testmod()

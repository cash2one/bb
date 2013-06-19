#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Skeleton + Body + ??? -> I
"""


from __future__ import division, print_function, unicode_literals

import collections

class I(dict):
    """
    >>> i = I(1, {"a": 1, "b": 1})
    >>> i.a == "1"
    True
    >>> i.b == 1
    True
    >>> i["foo"]
    5
    >>> i.bar
    []
    >>> i.listener["jump"].add("x")

    """

    __slots__ = ["i", "logs", "listener"]

    def __init__(self, n, source):
        assert isinstance(source, dict)
        for k, v in source.items():
            wrap = getattr(self, "_wrap_%s" % k, None)
            self[k] = wrap(v) if wrap else v
        i = int(n)
        object.__setattr__(self, "i", i)
        object.__setattr__(self, "logs", collections.deque(maxlen=100))
        object.__setattr__(self, "listener", collections.defaultdict(set))

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

    @staticmethod
    def _wrap_foobar(raw):
        return collections.Counter(
            {int(k) if k.isdigit() else k: v for k, v in raw.items()}
            )

    @staticmethod
    def _wrap_a(raw):
        return str(raw)




_cbs = {}

def handle_log_callback(cb):
    _cbs[cb.__name__] = cb
    return cb

def bind(i, log_name, callback_name):
    if callable(callback_name):
        callback_name = callback_name.__name__
    i.listener[log_name].add(callback_name)

def unbind(i, log_name, callback_name):
    if callable(callback_name):
        callback_name = callback_name.__name__
    i.listener[log_name].remove(callback_name)

def log(i, k, n, infos):
    yield "log", i.i, k, n, infos
    cb_set = i.listener[k]
    if cb_set:
        for callback_name in cb_set:
            # 3.3+: yield from
            for x in _cbs[callback_name](i, k, n, infos, callback_name):
                yield x

@handle_log_callback
def callback_example(i, k, n, infos, callback_name):
    print(i, k, n, infos, callback_name)

print(_cbs)

if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()

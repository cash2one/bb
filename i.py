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
    >>> #i.logs.append("over")
    >>> #i.listeners["foo"].add("bar")
    >>> bind(i, "go", callback_example)
    >>> i.listeners["go"] == set(["callback_example"])
    True
    >>> unbind(i, "go", "callback_example")
    >>> i.listeners["go"] == set()
    True
    >>> bind(i, "go", callback_example)
    >>> bind(i, "go", callback_example2)
    >>> len(list(log(i, "go"))) == 5
    True

    """

    __slots__ = ["i", "logs", "listeners"]

    def __init__(self, n, source):
        assert isinstance(source, dict)
        for k, v in source.items():
            wrap = getattr(self, "_wrap_%s" % k, None)
            self[k] = wrap(v) if wrap else v
        i = int(n)
        object.__setattr__(self, "i", i)
        object.__setattr__(self, "logs", collections.deque(maxlen=100))
        object.__setattr__(self, "listeners", collections.defaultdict(set))

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

def register_log_callback(callback):
    name = callback.__name__
    assert name not in _cbs
    _cbs[name] = callback
    return callback


def bind(i, log_name, callback_name):
    if callable(callback_name):
        callback_name = callback_name.__name__
    i.listeners[log_name].add(callback_name)

def unbind(i, log_name, callback_name):
    if callable(callback_name):
        callback_name = callback_name.__name__
    log_callbacks_set = i.listeners[log_name]
    if callback_name in log_callbacks_set:
        log_callbacks_set.remove(callback_name)

def save(i, k):
    return "save", i.i, k, i[k]

def log(i, k, n=1, infos=None):
    yield "log", i.i, k, n, infos
    i.logs.append([k, n, infos])
    callbacks_set = i.listeners[k]
    for callback_name in list(callbacks_set):
        # 3.3+: yield from
        for x in _cbs[callback_name](i, k, n, infos, k, callback_name):
            yield x

@register_log_callback
def callback_example(i, k, n, infos, log_name, callback_name):
    unbind(i, log_name, callback_name)  # optional
    yield save(i, "foo")
    yield save(i, "bar")

@register_log_callback
def callback_example2(i, k, n, infos, log_name, callback_name):
    unbind(i, log_name, callback_name)  # optional
    return [save(i, "foobar"), save(i, "a")]


if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()

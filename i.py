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
    >>> bind(i, go__callback_example)
    >>> i.listeners["go"] == set(["go__callback_example"])
    True
    >>> unbind(i, "go__callback_example")
    >>> i.listeners["go"] == set()
    True
    >>> bind(i, go__callback_example)
    >>> bind(i, go__callback_example2)
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
    assert name.partition("__")[2]
    _cbs[name] = callback
    return callback

def bind(i, name):
    """standard name:
    LOG_KEYWORD__CALLBACK_NAME
    XXX__YYY
    """
    if callable(name):
        name = name.__name__
    assert name.partition("__")[2]
    surname = name.partition("__")[0]
    i.listeners[surname].add(name)

def unbind(i, name):
    if callable(name):
        name = name.__name__
    assert name.partition("__")[2]
    surname = name.partition("__")[0]
    log_callbacks_set = i.listeners[surname]
    if name in log_callbacks_set:
        log_callbacks_set.remove(name)

def save(i, k):
    return "save", i.i, k, i[k]

def send(i, k, v):
    return "send", i.i, k, v

def log(i, k, n=1, infos=None):
    yield "log", i.i, k, n, infos
    i.logs.append([k, n, infos])
    callbacks_set = i.listeners[k]
    for callback_name in list(callbacks_set):
        # 3.3+: yield from
        for x in _cbs[callback_name](i, k, n, infos, callback_name):
            yield x

# examples here:
@register_log_callback
def go__callback_example(i, k, n, infos, callback_name):
    unbind(i, callback_name)  # optional
    yield save(i, "foo")
    yield send(i, "msg", "haha")

@register_log_callback
def go__callback_example2(i, k, n, infos, callback_name):
    return [save(i, "foobar"), save(i, "a")]



if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()

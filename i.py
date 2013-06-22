#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Skeleton + Body + ??? -> I
"""


from __future__ import division, print_function, unicode_literals

import collections
import sys

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
    >>> i.listeners["go"] == set([("callback_example",)])
    True
    >>> unbind(i, "go", "callback_example")
    >>> i.listeners["go"] == set()
    True
    >>> bind(i, "go", callback_example)
    >>> bind(i, "go", callback_example2)
    >>> i.listeners["go"] == set([("callback_example",), ("callback_example2",)])
    True
    >>> len(list(log(i, "go")))
    5
    >>> i.listeners["go"] == set([("callback_example2",)])
    True
    >>> a = i._foobar
    >>> b = i._foobar
    >>> id(a) == id(b)
    False

    >>> bind(i, "gogogo", callback_example)
    >>> bind(i, "gogogogo", callback_example)
    >>> len(i.listeners)
    3
    >>> check_tower(i, "a > 1", f)
    >>> len(i.listeners["gogo"])  # daemon launched
    1
    >>> i.a = 2
    >>> _ = list(log(i, "gogo"))
    >>> len(i.listeners["gogo"])  # daemon quited
    0

    """

    __slots__ = ["i", "logs", "listeners", "checkers"]

    def __init__(self, n, source):
        assert isinstance(source, dict)
        for k, v in source.items():
            wrap = getattr(self, "_wrap_%s" % k, None)
            self[k] = wrap(v) if wrap else v
        i = int(n)
        object.__setattr__(self, "i", i)
        object.__setattr__(self, "logs", collections.deque(maxlen=100))
        object.__setattr__(self, "listeners", collections.defaultdict(set))
        object.__setattr__(self, "checkers", collections.defaultdict(set))

    def __setattr__(self, k, v):
        self[k] = v

    def __getattr__(self, k):
        return self[k]

    def __missing__(self, k):
        self[k] = object.__getattribute__(self, "_" + k)
        return self[k]

    @property
    def _foo(self):
        return 5

    @property
    def _bar(self):
        return list()

    @property
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

def bind(i, log, callback_name, *args):
    if callable(callback_name):
        callback_name = callback_name.__name__
    assert callback_name in _cbs
    callback_name_args = (callback_name,) + args
    i.listeners[log].add(callback_name_args)

def unbind(i, log, callback_name, *args):
    if callable(callback_name):
        callback_name = callback_name.__name__
    assert callback_name in _cbs
    log_callbacks_set = i.listeners[log]
    callback_name_args = (callback_name,) + args
    if callback_name_args in log_callbacks_set:
        log_callbacks_set.remove(callback_name_args)

def save(i, k):
    return "save", i.i, k, i[k]

def send(i, k, v):
    return "send", i.i, k, v

def log(i, k, infos=None, n=1):
    yield "log", i.i, k, infos, n
    i.logs.append([k, infos, n])
    callbacks_set = i.listeners[k]
    for callback in list(callbacks_set):
        # 3.3+: yield from
        for x in _cbs[callback[0]](i, k, infos, n, *callback[1:]):
            yield x

# examples here:
@register_log_callback
def callback_example(i, k, infos, n, *args):
    unbind(i, k, callback_example)
    # or:
    #   unbind(i, k, "callback_example")
    #   unbind(i, k, callback_example.__name__)
    yield save(i, "foo")
    yield send(i, "msg", "haha")

@register_log_callback
def callback_example2(i, k, infos, n, *args):
    return [save(i, "foobar"), save(i, "a")]

_cks = {}

def register_check_callback(callback):
    name = callback.__name__
    assert name not in _cks
    _cks["CK_" + name] = callback
    return callback

@register_check_callback
def check_tower(i, evaluation, callback):
    #print(evaluation, callback, file=sys.stderr)
    if eval(evaluation, {"a": int(i.a), "b": 2}):
        callback()
        unbind(i, "gogo", check_tower_daemon, evaluation, callback)
    else:
        bind(i, "gogo", check_tower_daemon, evaluation, callback)

def f():
    print("check `i.a > 1` --> ok", file=sys.stderr)

@register_log_callback
def check_tower_daemon(i, k, infos, n, evaluation, callback):
    #print(evaluation, callback, file=sys.stderr)
    check_tower(i, evaluation, callback)
    yield


if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()

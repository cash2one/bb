#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals


import collections
import sys

class I(dict):
    """
    >>> i = I(42, {"a": 1, "b": 3})
    >>> i.i
    42
    >>> i["a"] == "1"
    True
    >>> i["b"]
    3
    >>> i["foo"]
    5
    >>> a = i["foobar"]
    >>> b = i["foobar"]
    >>> id(a) == id(b)
    True
    >>> i.logs.append("over")
    >>> #i.listeners["foo"].add("bar")
    >>> i.bind("go", callback_example, 1)
    >>> i.listeners["go"] == set([("callback_example", 1)])
    True
    >>> i.unbind("go", "callback_example", 1)
    >>> i.listeners["go"] == set()
    True
    >>> i.bind("go", callback_example, 1, 2, 3)
    >>> i.bind("go", callback_example2)
    >>> i.listeners["go"] == set([("callback_example", 1, 2, 3), ("callback_example2",)])
    True
    >>> len(list(log(i, "go")))
    5
    >>> i.listeners["go"] == set([("callback_example2",)])
    True

    >>> i.bind("gogogo", callback_example)
    >>> i.bind("gogogogo", callback_example)
    >>> len(i.listeners)
    3
    >>> check(i, "tower", compile("a > 1", "<string>", "eval"), {"a": int(i["a"])}, f, "gogo")
    >>> len(i.listeners["gogo"])  # daemon launched
    1
    >>> i["a"] = 1
    >>> _ = list(log(i, "gogo"))  # "i.a > 1" is False, daemon is watching
    >>> len(i.listeners["gogo"])
    1
    >>> i["a"] = 2
    >>> _ = list(log(i, "gogo"))
    >>> len(i.listeners["gogo"])  # daemon quited
    0

    """

    __slots__ = ["i", "cache", "logs", "listeners"]

    def __init__(self, n, source):
        assert isinstance(source, dict)
        for k, v in source.items():
            wrap = getattr(self, "_wrap_%s" % k, None)
            self[k] = wrap(v) if wrap else v
        self.i = int(n)
        self.cache = list()
        self.logs = collections.deque(maxlen=100)
        self.listeners = collections.defaultdict(set)

    def __missing__(self, k):
        self[k] = getattr(self, "_default_" + k)
        return self[k]

    def bind(self, log, cb, *args):
        if callable(cb):
            cb = cb.__name__
        assert cb in _cbs, cb
        assert isinstance(log, str), log
        cb_args = (cb,) + args
        self.listeners[log].add(cb_args)

    def unbind(self, log, cb, *args):
        if callable(cb):
            cb = cb.__name__
        assert cb in _cbs, cb
        assert isinstance(log, str), log
        all_cb_args = self.listeners[log]
        cb_args = (cb,) + args
        if cb_args in all_cb_args:
            all_cb_args.remove(cb_args)

    def send(self, k, v):
        self.cache.append(["save", self.i, k, v])

    def log(self, k, infos=None, n=1):
        self.cache.append(["log", self.i, k, infos, n])
        self.logs.append([k, infos, n])
        all_cb_args = self.listeners[k]
        for cb_args in list(all_cb_args):
            _cbs[cb_args[0]](self, k, infos, n, *cb_args[1:])

    def save(self, k):
        self.cache.append(["save", self.i, k, self[k]])

    @property
    def _default_foo(self):
        return 5

    @property
    def _default_bar(self):
        return list()

    @property
    def _default_foobar(self):
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
    assert name not in _cbs, name
    _cbs[name] = callback
    return callback

def bind(i, log, callback_name, *args):
    if callable(callback_name):
        callback_name = callback_name.__name__
    assert callback_name in _cbs, callback_name
    callback_name_args = (callback_name,) + args
    i.listeners[log].add(callback_name_args)

def unbind(i, log, callback_name, *args):
    if callable(callback_name):
        callback_name = callback_name.__name__
    assert callback_name in _cbs, callback_name
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
    unbind(i, k, callback_example, *args)
    # or:
    #   unbind(i, k, "callback_example")
    #   unbind(i, k, callback_example.__name__)
    yield save(i, "foo")
    yield send(i, "msg", "haha")

@register_log_callback
def callback_example2(i, k, infos, n, *args):
    return [save(i, "foobar"), save(i, "a")]


def check(i, key, evaluation, env, callback, k):
    daemon = "%s_daemon" % key
    if eval(evaluation, None, env):
        callback(key)
        unbind(i, k, daemon, evaluation, callback)
    else:
        bind(i, k, daemon, evaluation, callback)


def f(func_name):
    print(func_name, "--> ok", file=sys.stderr)

@register_log_callback
def tower_daemon(i, k, infos, n, evaluation, callback):
    #print(evaluation, callback, file=sys.stderr)
    check(i, "tower", evaluation, {"a": int(i["a"])}, callback, k)
    yield


if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()

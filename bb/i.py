#!/usr/bin/env python3

import collections
import types
import sys

from bisect import bisect
from itertools import accumulate, chain
from random import random

from .util import EvalCache, Object
if __debug__:
    from .const import INSTRUCTIONS_LIST

gains_global = {}
cfg = Object()
cfg.items = {}

P = {}

def _register(attr, key, value):
    dct = getattr(I, attr)
    if not key:
        key = value.__name__
    assert isinstance(key, str), key
    assert key not in dct, key
    dct[key] = value
    return value

register_log_callback = lambda cb, name=None: _register("_hooks", name, cb)
register_default = lambda d, k=None: _register("_defaults", k, d)
register_wrapper = lambda w, k=None: _register("_wrappers", k, w)

class I(dict):
    """
    """

    __slots__ = ["_i", "_cache", "_logs", "_listeners", "online"]

    _eval_cache = EvalCache()

    # "foo": 5, "bar": lambda _: [_["foo"]],
    _defaults = {}

    # "stories": lambda raw: {int(k): v for k, v in raw.items()},
    _wrappers = {}

    # "func_name": func,
    _hooks = {}


    def __init__(self, n:int, source:dict=None):
        self._i = n
        self._cache = []
        self._logs = collections.deque(maxlen=50)
        self._listeners = collections.defaultdict(set)
        self.online = False
        if source:
            assert isinstance(source, dict), source
            for k, v in source.items():
                wrap = self._wrappers.get(k)
                self[k] = wrap(v) if wrap else v

    def __missing__(self, k):
        v = self._defaults[k]
        if callable(v):
            v = v(self)
        self[k] = v
        return v

    def __getattr__(self, k):  # use this prudently
        return self[k]

    # i is protected and readonly
    @property
    def i(self):
        return self._i

    def bind(self, log:str, cb:str, extra:hash):
        if callable(cb):
            cb = cb.__name__
        assert self._hooks[cb].__code__.co_argcount == 5, cb
        self._listeners[log].add((cb, extra))

    def unbind(self, log:str, cb:str, extra:hash):
        if callable(cb):
            cb = cb.__name__
        assert self._hooks[cb].__code__.co_argcount == 5, cb
        self._listeners[log].discard((cb, extra))

    def send(self, k:str, v):
        assert k in INSTRUCTIONS_LIST, k
        self._cache.append([self._i, k, v])

    def save(self, k:str):
        assert k in self._defaults, k
        self._cache.append(["save", self._i, k, self[k]])

    def log(self, k:str, infos:dict={}, n:int=1):
        self._cache.append(["log", self._i, k, infos, n])
        self._logs.append([k, infos, n])
        for cb in list(self._listeners[k]):  # need a copy for iter
            self._hooks[cb[0]](cb[1], self, k, infos, n)  # cb may change listeners[k]

    def flush(self, *others) -> list:
        """be called at end"""
        f = []
        c = self._cache
        if c:
            f.extend(c)
            del c[:]
        for o in others:
            c = o._cache
            f.extend(c)
            del c[:]
        return f

    def give(self, rc, cause=None):
        self.apply(self.render(rc), cause)

    def render(self, rc:tuple) -> list:
        """
        rc = (
            ("i", 1001, "lv**5"),
            (("c", 5), 0.5),
            ((("a", 1), ("b", 1)), (9, 1)),
        )
        """
        assert all(isinstance(r, tuple) for r in rc), rc
        booty = []
        for r in rc:
            foo, bar = r[0], r[-1]
            if isinstance(foo, str):
                assert isinstance(bar, (int, str))
                booty.append(list(r))
            elif isinstance(bar, tuple):
                assert foo, foo
                assert len(foo) == len(bar), foo + bar
                assert all(isinstance(t, tuple) for t in foo), foo
                assert all(n > 0 for n in bar), bar
                l = list(accumulate(bar))
                booty.append(list(foo[bisect(l, random() * l[-1])]))
            elif random() < bar:
                booty.append(list(foo))

        discount = 1 or 0.1 # todo
        gg, gl = gains_global, self["gains_local"]

        for i in booty:
            k, n = i[0], i[-1]
            if isinstance(n, str):
                n = eval(self._eval_cache[n], None, self)  # :)
            i[-1] = int(n * discount * (1 + gl.get(k, 0) + gg.get(k, 0)))

        return booty

    def apply(self, booty, cause):
        """
        apply all booty, and merge updated-messages from sub-call

        # write this directly or "render rc"
        booty = [["a", 50], ["b", 5], ["c", 1001, 25]]
        apply(booty)
        """
        assert all(isinstance(b[0], str) for b in booty), booty
        assert all(isinstance(b[-1], int) for b in booty), booty
        for b in booty:
            method = self.__getattribute__("apply_" + b[0])
            method(*b[1:], cause=cause)

    def apply_null(self, count, cause):
        """do nothing"""

    def apply_gold(self, count, cause=None):
        if count > 0 and not cause:
            raise Warning("+gold without cause is not allowed")
        before = self["gold"]
        gold = self["gold"] + count
        if gold < 0:
            raise Warning("gold: %s" % gold)
        self["gold"] = gold
        self.send("gold", gold)
        self.save("gold")
        self.log("gold", {"cause": cause, "before": before, "after": gold},
                 count)

    def apply_item(self, item, count, cause=None, custom=0):
        assert isinstance(count, int) and count, count
        assert isinstance(custom, int) and custom >= 0, custom
        if count > 0 and not cause:
            raise Warning("+item without cause is not allowed")
        bag = self["bag"]
        changes = {}
        multi = cfg.items[item].get("multi")
        if count > 0:
            if multi:
                try:
                    i = bag.index(None)
                    x = [item, count]  # ID and COUNT
                    bag[i] = x
                    changes[i] = x
                except ValueError:
                    self.log("lose", {"item": item,
                                      "count": count,
                                      "reason": "bag is full"})
            else:
                for _ in range(count):
                    try:
                        i = bag.index(None)
                        x = [item, {}]  # ID and META-INFO
                        bag[i] = x
                        changes[i] = x
                    except ValueError:
                        self.log("lose", {"item": item,
                                          "count": 1,
                                          "reason": "bag is full"})
        elif count < 0:
            if not multi:
                raise Warning("item %d has no multi, "
                              "-item (count=%d) is not allowed"
                              % (item, count))
            n = abs(count)
            for i in chain(range(custom, len(bag)), range(custom)):  # :)
                t = bag[i]
                if t and t[0] == item:
                    if t[1] > n:
                        t[1] -= n
                        n = 0
                        changes[i] = t
                    else:
                        bag[i] = None
                        n -= t[1]
                        changes[i] = None
                    if not n:
                        break
            else:
                lost = abs(count) - n
                if lost:
                    self.log("lose", {"item": item,
                                      "count": lost,
                                      "reason": "-item but not enough"})
                raise Warning("failed to -item")

        if changes:
            self.send("bag", changes)  # dict is only for update
            self.save("bag")

register_default(5, "foo")
register_default(lambda self: [self["foo"]] * 3, "bar")
@register_default
def foobar(_):
    return collections.Counter({1: 1, 2: 1})
register_default(lambda _: [0, 0], "xy")

@register_wrapper
def foobar(raw):
    return collections.Counter({int(k): v for k, v in raw.items()})

P[1] = I(1)


if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()

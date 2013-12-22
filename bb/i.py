#!/usr/bin/env python3

import collections
import types
import sys

from bisect import bisect
from itertools import accumulate, chain
from random import random

from bb.util import EvalCache

class _P(dict):
    def __missing__(self, k):
        i = I(k)
        self[k] = i
        return i

#P = _P()  # do not use this way
P = {}

# map looks like this:
#    {"func_name": func, ...}
# why prefer "func_name" mapping instead of use function directly:
#   * reload functions at running
#   * persist this "function-link" at shutdown
#   * easy to read
class Box(list):
    """
    """
    def exchange(self, i, j):
        assert i and j
        if i != j:
            self[i], self[j] = self[j], self[i]

def init_assets():
    I.assets["items"] = {
        1: {
            "multi": 99,
            "buy": 10,
            "sell": 5,
        },
        2: {
            "multi": 99,
            "buy": 88,
            "sell": 44,
        },
        # ...
        3: {
            "multi": 6,
            "buy": 88,
            "sell": 44,
            "output": (  # for apply
                ("hp", "lv * 3"),
                ((("mp", 1), ("mp", 5)), (9, 1)),
            ),
        },

        1001: {
            "buy": 2000,
            "sell": 1000,
            #"attributes": [
            #    ["strength", 2],
            #    ["dexterity", 3],
            #    ["strength", 1],
            #],
        },
        # ...
    }
    # ...


def _register(attr, key, value):
    dct = getattr(I, attr)
    if not key:
        key = value.__name__
    assert isinstance(key, str), key
    assert key not in dct, key
    dct[key] = value
    return value

register_log_callback = lambda cb, name=None: _register("_cbs", name, cb)
register_default = lambda d, k=None: _register("_defaults", k, d)
register_wrapper = lambda w, k=None: _register("_wrappers", k, w)

class I(dict):
    """
    >>> i = I(42, {"a": 1, "b": 3})
    >>> i.online = True
    >>> i.i
    42
    >>> i["a"]
    1
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
    >>> i.bind("go", "callback_example", 1)
    >>> i.listeners["go"] == set([("callback_example", 1)])
    True
    >>> i.unbind("go", "callback_example", 1)
    >>> i.listeners["go"] == set()
    True
    >>> i.bind("go", callback_example, (1, 2, 3))
    >>> i.bind("go", callback_example2, None)
    >>> i.listeners["go"] == set([("callback_example", (1, 2, 3)), ("callback_example2", None)])
    True
    >>> i.log("go")
    >>> len(i.cache)
    5
    >>> i.listeners["go"] == set([("callback_example2", None)])
    True

    >>> i.bind("gogogo", callback_example, None)
    >>> i.bind("gogogogo", callback_example, None)
    >>> len(i.listeners)
    3
    """

    __slots__ = ["_i", "_cache", "_logs", "_listeners", "online"]

    _eval_cache = EvalCache()

    _defaults = {
        #"foo": 5,
        #"bar": lambda _: [_["foo"]],
    }

    _wrappers = {
#        "foobar": lambda raw: collections.Counter(
#            {int(k) if k.isdigit() else k: v for k, v in raw.items()}),
#        "stories": lambda raw: {int(k): v for k, v in raw.items()},
#        "stories_done": lambda raw: set(raw),
    }

    _cbs = {}

    assets = {"items": {}}
    gains_global = {}


    def __init__(self, n, source=None):
        if not isinstance(n, int):
            raise ValueError("is not int: %r" % n)
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

    # i, cache, logs, listeners are protected and readonly
    @property
    def i(self):
        return self._i

    @property
    def cache(self):
        return self._cache

    @property
    def logs(self):
        return self._logs

    @property
    def listeners(self):
        return self._listeners

    def bind(self, log, cb, extra):
        if callable(cb):
            cb = cb.__name__
        assert isinstance(log, str), log
        assert cb in self._cbs, cb
        self.listeners[log].add((cb, extra))

    def unbind(self, log, cb, extra):
        if callable(cb):
            cb = cb.__name__
        assert isinstance(log, str), log
        assert cb in self._cbs, cb
        self.listeners[log].discard((cb, extra))

    def send(self, k, v):
        assert isinstance(k, str), k
        self.cache.append([self.i, k, v])

    def save(self, k):
        assert isinstance(k, str), k
        self.cache.append(["save", self.i, k, self[k]])

    def log(self, k, infos={}, n=1):
        """infos must be read-only
        default-value: `infos={}` is dangerous, but i like
        """
        assert isinstance(k, str), k
        assert isinstance(infos, dict), infos
        assert isinstance(n, int), n
        self.cache.append(["log", self.i, k, infos, n])
        self.logs.append([k, infos, n])
        for cb in list(self.listeners[k]):  # need a copy for iter
            self._cbs[cb[0]](cb[1], self, k, infos, n)  # cb may change listeners[k]

    def flush(self, *others):
        """be called at end"""
        f = []
        c = self.cache
        if c:
            f.extend(c)
            del c[:]
        for o in others:
            c = o.cache
            f.extend(c)
            del c[:]
        return f

    def give(self, rc, cause=None):
        self.apply(self.render(rc), cause)

    def render(self, rc):
        """
        rc = (
            ("a", "lv**5"),
            (("c", 1001, 5), 0.5),
            ((("a", 1), ("b", 1)), (9, 1)),
        )
        """
        assert isinstance(rc, tuple), rc
        assert all(isinstance(r, tuple) for r in rc), rc
        booty = []
        for foo, bar in rc:
            if isinstance(foo, str):
                assert isinstance(bar, (int, str))
                booty.append([foo, bar])
            elif isinstance(bar, tuple):
                assert foo, foo
                assert len(foo) == len(bar), foo + bar
                assert all(isinstance(t, tuple) for t in foo), foo
                assert all(n > 0 for n in bar), bar
                #l = list(accumulate(bar))   calc it outside!
                booty.append(list(foo[bisect(bar, random() * bar[-1])]))
            elif random() < bar:
                booty.append(list(foo))

        discount = 1 or 0.1 # todo
        gg, gl = self.gains_global, self["gains_local"]

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
        multi = self.assets["items"][item].get("multi")
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

init_assets()

register_default(5, "foo")
register_default(lambda _: [_["foo"]], "bar")
@register_default
def foobar(_):
    return collections.Counter({1: 1, 2: 1})
register_default(lambda _: {}, "gains_local")
register_default(500, "gold")
register_default(1, "lv")
register_default(lambda _: [None] * 8, "bag")
register_default(1, "story")
register_default(0, "story_task")
register_default(lambda _: {}, "stories")
register_default(lambda _: set(),"stories_done")
register_default(lambda _: [0, 0], "xy")

# examples here:
@register_log_callback
def callback_example(extra, i, log, infos, n):
    assert i.logs[-1] == [log, infos, n]
    i.unbind(log, callback_example, extra)
    i.save("foo")
    i.send("msg", "haha")

@register_log_callback
def callback_example2(extra, i, log, infos, n):
    i.save("foobar")
    i.save("a")



if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()
    i = I(9527)
    i["lv"] += 1
    rc = (
        ("a", "lv**5"),
        ((("a", 1), ("b", 1)), (9, 1)),
        (("c", 1001, 5), 0.5),
    )
    print(i.render(rc))
    c = collections.Counter()
    for _ in range(1000):
        result = i.render(rc)
        c[len(result)] += 1
        c[result[1][0]] += 1
    print(c)
    """
    """
    import json
    def p(o):
        print("egg:", json.dumps(o, separators=(", ", ": ")))
    i.apply([["gold", 1], ["null", 0]], 'xixi')
    i.apply([["gold", 2], ["gold", 3]], 'haha')
    #i.apply([["gold", -100], ["item", 2, 30], ["item", 1001, 20], ], 'pow')
    #i.bag.exchange(1, 2)
    i.give((("gold", "lv*100"),), "give")
    i.apply([["gold", 5], ["item", 1, 10], ["item", 2, 10], ["item", 2, 10], ], "test")
    i.apply([["item", 2, -5]], "test")
    i.apply_item(2, -5, custom=3)
    print(i)
    for _ in range(11):
        i.apply_item(2, 1, "test", custom=3)
    print(i)
    i.apply_item(2, -14)
    print(i)
    print(i.logs)
    #print(i.cache)

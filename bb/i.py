#!/usr/bin/env python

import collections
import types
import sys

from bisect import bisect
from itertools import accumulate, chain
from random import random

from bb.util import EvalCache

# map looks like this:
#    {"func_name": func, ...}
# why prefer "func_name" mapping instead of use function directly:
#   * reload functions at running
#   * persist this "function-link" at shutdown
#   * easy to read
_cbs = {}

def register_log_callback(callback):
    name = callback.__name__
    assert name not in _cbs, name
    _cbs[name] = callback
    return callback

class Box(list):
    """
    """
    def exchange(self, i, j):
        assert i and j
        if i != j:
            self[i], self[j] = self[j], self[i]

class I(dict):
    """
    >>> i = I(42, {"a": 1, "b": 3})
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
    >>> i.listeners["go"] == set([("callback_example", (1,))])
    True
    >>> i.unbind("go", "callback_example", 1)
    >>> i.listeners["go"] == set()
    True
    >>> i.bind("go", callback_example, 1, 2, 3)
    >>> i.bind("go", callback_example2)
    >>> i.listeners["go"] == set([("callback_example", (1, 2, 3)), ("callback_example2", ())])
    True
    >>> i.log("go")
    >>> len(i.cache)
    5
    >>> i.listeners["go"] == set([("callback_example2", ())])
    True

    >>> i.bind("gogogo", callback_example)
    >>> i.bind("gogogogo", callback_example)
    >>> len(i.listeners)
    3
    >>> check(i, "tower", "i.a > 1", {"i": i}, f, "gogo")
    >>> len(i.listeners["gogo"])  # daemon launched
    1
    >>> i["a"] = 1
    >>> i.log("gogo")  # "i["a"] > 1" is False, daemon is watching
    >>> len(i.listeners["gogo"])
    1
    >>> i["a"] = 2
    >>> i.log("gogo")
    >>> len(i.listeners["gogo"])  # daemon quited
    0

    """

    __slots__ = ["_i", "_cache", "_logs", "_listeners"]

    MAX_LOGS_DEQUE_LENGTH = 100
    MAX_BAG_SIZE = 10

    eval_cache = EvalCache()

    assets_items = {
        1: {
            "multiple": 99,
            "buy": 10,
            "sell": 5,
        },
        2: {
            "multiple": 99,
            "buy": 88,
            "sell": 44,
        },
        # ...

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

    def __init__(self, n, source=None):
        self._i = int(n)
        self._cache = []
        self._logs = collections.deque(maxlen=self.MAX_LOGS_DEQUE_LENGTH)
        self._listeners = collections.defaultdict(set)
        if source is not None:
            assert isinstance(source, dict), source
            for k, v in source.items():
                wrap = getattr(self, "_wrap_%s" % k, None)
                self[k] = wrap(v) if wrap else v

    def __missing__(self, k):
        v = self.__getattribute__("_default_%s" % k)
        self[k] = v
        return v

    def __getattr__(self, k):   # use this prudently
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

    def bind(self, log, cb, *args):
        if callable(cb):
            cb = cb.__name__
        assert isinstance(log, str), log
        assert cb in _cbs, cb
        cb_args = cb, args
        self.listeners[log].add(cb_args)

    def unbind(self, log, cb, *args):
        if callable(cb):
            cb = cb.__name__
        assert isinstance(log, str), log
        assert cb in _cbs, cb
        all_cb_args = self.listeners[log]
        cb_args = cb, args
        if cb_args in all_cb_args:
            all_cb_args.remove(cb_args)

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
        all_cb_args = self.listeners[k]
        if all_cb_args:
            for cb_args in list(all_cb_args):   # need a copy for iter
                _cbs[cb_args[0]](self, k, infos, n, *cb_args[1])

    def render(self, rc):
        """
        rc = (
            ("a", "lv**5"),
            ((("a", 1), ("b", 1)), (9, 1)),
            (("c", 1001, 5), 0.5),
        )
        """
        discount = self.foo   # just a example, 
        assert isinstance(rc, tuple), rc
        assert all(isinstance(r, tuple) for r in rc), rc
        booty = []
        for r in rc:
            foo, bar = r[0], r[1]
            if isinstance(foo, str):
                assert isinstance(bar, (int, str, types.CodeType))
                booty.append(list(r))
            elif isinstance(bar, tuple):
                assert foo, foo
                assert len(foo) == len(bar), foo + bar
                assert all(isinstance(t, tuple) for t in foo), foo
                assert all(n > 0 for n in bar), bar
                l = list(accumulate(bar))   # calc it outside?
                booty.append(list(foo[bisect(l, random() * l[-1])]))
            elif isinstance(bar, float):
                assert 0 < bar < 1, bar
                if random() < bar:
                    booty.append(list(foo))
            else:
                raise Warning("unsupported rc: %s" % (r,))

        env = {"lv": self["level"]}
        for i in booty:
            n = i[-1]
            if not isinstance(n, int):
                n = eval(self.eval_cache[n], None, env)   # environments
            i[-1] = int(n * discount)

        return booty

    def eval(self, expr, env=None):
        """is this necessary?"""
        return eval(self.eval_cache[expr], None, env)

    def apply(self, booty, cause=None):
        """
        apply all booty, and merge updated-messages from sub-call

        # write this directly or "render rc"
        booty = [["a", 50], ["b", 5], ["c", 1001, 25]]
        apply(booty)
        """
        assert all(isinstance(b[-1], int) for b in booty), booty
        assert all(isinstance(b[0], str) for b in booty), booty
        for b in booty:
            method = self.__getattribute__("apply_%s" % b[0])
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
        self.log("gold",
                 {"cause": cause, "before": before, "after": gold},
                 n=count)

    def apply_item(self, item, count, cause=None, custom=1):
        assert isinstance(count, int) and count, count
        assert isinstance(custom, int) and custom > 0, custom
        if count > 0 and not cause:
            raise Warning("+item without cause is not allowed")
        bag = self["bag"]
        changes = {}
        multi = self.assets_items[item].get("multiple")
        if count > 0:
            if multi:
                try:
                    i = bag.index(None)
                    x = [item, count]
                    bag[i] = x
                    changes[i] = x
                except ValueError:
                    self.log("lost", {"item": item,
                                      "count": count,
                                      "reason": "bag is full"})
            else:
                for _ in range(count):
                    try:
                        i = bag.index(None)
                        x = [item, count]
                        bag[i] = x
                        bag[i] = x
                        changes[i] = x
                    except ValueError:
                        self.log("lost", {"item": item,
                                          "reason": "bag is full"})
        elif count < 0:
            if not multi:
                raise Warning("item %d has no multi, "
                              "-item (count=%d) is not allowed"
                              % (item, count))
            n = abs(count)
            for i in chain(range(custom, len(bag)), range(1, custom)):  # :)
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
                self.log("lost", {"item": item,
                                  "count": abs(count)-n,
                                  "reason": "-item but not enough"})
                raise Warning("-item faild")

        if changes:
            self.send("bag", changes)   # dict is only for update
            self.save("bag")


    @property
    def _default_foo(self):
        return 5

    @property
    def _default_bar(self):
        return list()

    @property
    def _default_foobar(self):
        return collections.Counter()

    @property
    def _default_gold(self):
        return 500

    @property
    def _default_level(self):
        return 1

    @property
    def _default_bag(self):
        bag = []
        size = self.MAX_BAG_SIZE
        bag.append({"max": size, "extra": 0})
        bag.extend([None] * size * 2)
        return bag

    @staticmethod
    def _wrap_foobar(raw):
        return collections.Counter(
            {int(k) if k.isdigit() else k: v for k, v in raw.items()}
            )


# examples here:
@register_log_callback
def callback_example(i, k, infos, n, *args):
    i.unbind(k, callback_example, *args)
    # or:
    #   i.unbind(k, "callback_example")
    #   i.unbind(k, callback_example.__name__)
    i.save("foo")
    i.send("msg", "haha")

@register_log_callback
def callback_example2(i, k, infos, n, *args):
    i.save("foobar")
    i.save("a")


def check(i, key, evaluation, env, callback, k):
    daemon = "%s_daemon" % key
    if eval(evaluation, None, env):
        callback(key)
        i.unbind(k, daemon, evaluation, callback)
    else:
        i.bind(k, daemon, evaluation, callback)


def f(func_name):
    print(func_name, "--> ok", file=sys.stderr)

@register_log_callback
def tower_daemon(i, k, infos, n, evaluation, callback):
    #print(evaluation, callback, file=sys.stderr)
    check(i, "tower", evaluation, None, callback, k)


if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()
    i = I(9527)
    i["level"] += 1
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
    i.apply([["gold", 5], ["item", 1, 10], ["item", 2, 10], ["item", 2, 10], ], 'x')
    #i.apply([["item", 2, -15]])
    i.apply_item(2, -15, custom=3)
    print(i)
    for _ in range(11):
        i.apply_item(2, 1, "test", custom=3)
    print(i)
    i.apply_item(2, -14)
    print(i)
    print(i.logs)
    #print(i.cache)

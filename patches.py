#!/usr/bin/env python3

import collections
import types
import sys

from bisect import bisect
from itertools import accumulate, chain
from random import random

from bb import i
from bb.util import Object

cfg = Object()
cfg.items = {}

gains_global = {}

i.register_default(5, "gold")
i.register_default(lambda _: {}, "gains_local")
i.register_default(lambda _: [], "bag")

@i.method
def give(self, rc, cause=None):
    self.apply(self.render(rc), cause)

@i.method
def render(self, rc:tuple) -> list:
    """
    rc = (
        (("i", 1001, "lv**5"), 1),
        (("c", 5), 0.5),
        ((("a", 1), ("b", 1)), (9, 1)),
    )
    """
    booty = []
    for r in rc:
        foo, bar = r
        if isinstance(bar, tuple):
            assert foo, foo
            assert len(foo) == len(bar), foo + bar
            assert all(n >= 0 for n in bar), bar
            l = list(accumulate(bar))
            booty.append(list(foo[bisect(l, random() * l[-1])]))
        elif random() < bar:
            booty.append(list(foo))

    discount = 1 or 0.1 # todo
    gg, gl = gains_global, self["gains_local"]

    for i in booty:
        k, n = i[0], i[-1]
        if isinstance(n, str):
            n = eval(n, None, self)
        i[-1] = int(n * discount * (1 + gl.get(k, 0) + gg.get(k, 0)))

    return booty

@i.method
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

@i.method
def apply_null(self, count, cause):
    """do nothing"""

@i.method
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

@i.method
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

i.P[1] = i.I(1)


if __name__ == "__main__":
    pass

#!/usr/bin/env python3

import time

from bb.const import ATTR
from bb.inst import instructions, processes, handle, pre, run
from bb.i import I, P

# everyone could checkout my attributes(in the PUBLIC_ATTRS)
public_attrs = {
    "bag",
    "level",
}

def _echo_attr(key):
    """echo only"""
    def _(i, idx):
        if idx:
            if key not in public_attrs:
                raise KeyError(key)
            v = P[idx][key]
        else:
            v = i[key]
        return [[i.i, key, v]]
    return _

for idx, key in enumerate(sorted(I._defaults), ATTR):
    instructions[key] = idx
    processes[idx] = _echo_attr(key)


@handle
@pre((int, float, str, list, dict, bool))
def ping(i, n):
    if i.i:
        i.send("ping", n)
        return i.flush()
    else:
        caches = []
        for o in P.values():
            c = o.cache
            if c:
                caches.extend(c)
                del c[:]
        return caches

@I.register_log_callback
def _test(_, i, log, infos, n):
    return
    print(_, i, log, infos, n, i.listeners, i.logs, sep="\n")

@handle
@pre()
#@pre(bool, lambda x: x is True)
def online(i, b):
    i.online = b
    t = time.time()
    i.save("bag")
    if b:
        i.bind("online", "_test", "on")
        i.bind("offline", "_test", "off")
        i["login_time"] = t
        i.log("online", {"time": t})
        # blabla...
        #i.give((("item", 2, -3), ("gold", 1)), "cost")
        i.apply_item(2, -3, custom=2)
    else:
        i["logout_time"] = t
        i.log("offline", {"time": t})
        i.give((("item", 2, 10), ("gold", -1)), "give")
    return i.flush()

@run
def plus():
    for i in P.values():
        i.apply_gold(1, "plus")

#print(instructions)
#print(processes)

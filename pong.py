#!/usr/bin/env python

import time

from bb.inst import instructions, processes, handle, pre, run
from bb.i import I, P

assert len(I._defaults) < 256

def _echo_attr(key):
    """1-99 echo only"""
    return lambda i, _: [[i.i, key, i[key]]]

for idx, key in enumerate(sorted(I._defaults), 2**8):  # 256-511
    instructions[key] = idx
    processes[idx] = _echo_attr(key)


@handle
@pre((int, float, str, list, dict, bool))
def ping(i, n):
    i.send("ping", n)
    return i.flush()

@I.register_log_callback
def _test(_, i, log, infos, n):
    print(_, i, log, infos, n, i.listeners, i.logs, sep="\n")

@handle
#@pre(bool, lambda x: x is True)
def online(i, b):
    i.online = b
    t = time.time()
    if b:
        i.bind("online", "_test", "on")
        i.bind("offline", "_test", "off")
        i["login_time"] = t
        i.log("online", {"time": t})
        # blabla...
    else:
        i["logout_time"] = t
        i.log("offline", {"time": t})

@run
def plus():
    for i in P.values():
        i["gold"] += 1

#print(instructions)
#print(processes)

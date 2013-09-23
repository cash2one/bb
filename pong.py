#!/usr/bin/env python

import time

from bb.inst import instructions, processes, handle, run
from bb.i import I, P

assert len(I._defaults) <= 99

def _echo_attr(key):
    """1-99 echo only"""
    return lambda i, _: [[i.i, key, i[key]]]

for idx, key in enumerate(sorted(I._defaults)):
    instructions[key] = idx
    processes[idx] = _echo_attr(key)


@handle
def ping(i, n):
    i.send("ping", n)
    i.save("foo")
    return i.flush()

@I.register_log_callback
def _test(_, i, log, infos, n):
    print(_, i, log, infos, n, i.listeners, i.logs, sep="\n")

@handle
def online(i, b):
    i.online = b
    if b:
        i.bind("online", "_test", "on")
        i.bind("offline", "_test", "off")
        i.log("online", {"time": time.time()})
        # blabla...
    else:
        i.log("offline", {"time": time.time()})

@run
def plus():
    for i in P.values():
        i["gold"] += 1

#print(instructions)
#print(processes)

#!/usr/bin/env python

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

@handle
def online(i, n):
    i.online = n

@run
def plus():
    for i in P.values():
        i["gold"] += 1

#print(instructions)
#print(processes)

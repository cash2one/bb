#!/usr/bin/env python

from bb.inst import handle
from bb.i import P

@handle
def ping(i, n):
    i.send("pong", n + 1)
    i.save("foo")
    return i.flush()

@handle
def pong(i, n):
    j = P[1]
    i.send("pong", n)
    j.send("pong", n)
    return i.flush(j)


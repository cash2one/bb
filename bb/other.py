#!/usr/bin/env python

from bb.inst import handle
from bb.util import flush

P = {}

@handle
def ping(i, n):
    i = P[i]
    i.send("pong", n + 1)
    return flush(i.cache)


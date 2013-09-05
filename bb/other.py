#!/usr/bin/env python

from bb.inst import handle
from bb.util import flush

P = {}

@handle
def ping(i, n):
    i.send("pong", n + 1)
    i.save("foo")
    return flush(i.cache)


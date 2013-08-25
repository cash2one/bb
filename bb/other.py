#!/usr/bin/env python

from bb.i import I
from bb.inst import handle_input
from bb.util import flush

P = {}

@handle_input
def ping(i, n):
    i = P[i]
    i.send("pong", n + 1)
    return flush(i.cache)


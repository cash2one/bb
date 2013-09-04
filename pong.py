#!/usr/bin/env python

from bb.inst import handle
from bb.util import flush

@handle
def pong(i, n):
    i.send("pong", n)
    return flush(i.cache)


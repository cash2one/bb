#!/usr/bin/env python

from i import I
from inst import handle_input
from util import flush

staffs = {}
for i in range(10):   # init all, todo
    staffs[i] = I(i)

@handle_input
def ping(i, n):
    i = staffs[i]
    j = staffs[2]
    i.send("pong", n + 1)
    i.save("foo")
    j.send("pong", n + 2)
    return flush(i.cache, j.cache)


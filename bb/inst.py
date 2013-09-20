#!/usr/bin/env python

r"""
>>> commands["shell_push"]("1 + 6")
'7\n>>> '
"""

import time

# {1: func_1, 2: func_2, ...}
processes = {}

instructions_list = [
    "ping",
    "online",
]

# {"ping": 1, "pong": 2, ...}
instructions = dict(zip(instructions_list, range(100, 2**16)))

def handle(func):
    assert callable(func), func
    alias = func.__name__
    assert alias in instructions, alias
    signal = instructions[alias]
    assert signal not in processes, "%s:%d" % (alias, signal)
    processes[signal] = func
    return func


runners = {}  # launch certain function in runners by web

def run(func):
    assert callable(func), func
    alias = func.__name__
    assert alias not in runners, alias
    runners[alias] = func
    return func


import gc
import json
from bb.i import I, P
from bb.bd import BackdoorShell
from bb.oc import record, recorder
from bb.util import list_to_tuple

recorder.clear()
shell = BackdoorShell()

def _beginner(i):
    if i in P:
        raise KeyError("%d in P" % i)
    P[i] = I(i)
    return i

def _amend(i, k, v):
    v_ = P[i][k]  # old
    wrap = I._wrappers.get(k)
    if wrap:
        v = wrap(v)
    t_, t = type(v_), type(v)
    if t_ != t:
        raise ValueError("%s vs %s" % (t_, t))
    P[i][k] = v
    return i, k, v_, v

commands = {
    "shell": lambda line: shell.push(line),
    "status": lambda _: record() or dict(recorder),
    "gc": lambda _: gc.collect(),
    "beginner": lambda args: _beginner(int(args[0])),
    "amend": lambda args: _amend(int(args[0]), args[1], json.loads(args[2])),
    "run": lambda args: [runners[i]() or i for i in args if i],
    "render": lambda r: P[1].apply(P[1].render(list_to_tuple(r)), "from web"),
}



if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()

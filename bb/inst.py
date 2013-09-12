#!/usr/bin/env python

r"""
>>> commands["shell_push"]("1 + 6")
'7\n>>> '
"""

# {1: func_1, 2: func_2, ...}
processes = {}

instructions_list = [
    "ping",
    "pong",
    "type",
]

# {"ping": 1, "pong": 2, ...}
instructions = dict(zip(instructions_list, range(1, 2**16)))


def handle(func):
    assert callable(func), func
    alias = func.__name__
    assert alias in instructions, alias
    signal = instructions[alias]
    assert signal not in processes, "%s:%d" % (alias, signal)
    processes[signal] = func
    return func


from gc import collect
from bb.i import P
from bb.bd import BackdoorShell
from bb.oc import record, recorder
from bb.util import list_to_tuple

recorder.clear()
shell = BackdoorShell()

commands = {
    "shell": lambda line: shell.push(line),
    "status": lambda null: record() or dict(recorder),
    "gc": lambda null: collect(),
    "render": lambda r: P[1].apply(P[1].render(list_to_tuple(r)), "from web")
}



if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()

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


from bb.bd import BackdoorShell
shell = BackdoorShell()

from bb.oc import record, recorder

commands = {
    "shell": lambda line: shell.push(line),
    "hub_status": lambda null: record() or dict(recorder),
}



if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()

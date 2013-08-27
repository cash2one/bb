#!/usr/bin/env python

r"""
>>> commands["shell_push"]("1 + 6")
'7\n>>> '
"""

import logging

processes = {}

instructions_list = [
    "ping",
    "pong",
    "type",
]

instructions = dict(zip(instructions_list, range(1, 2**16)))


def handle(func):
    assert callable(func), func
    signal = func.__name__
    assert instructions[signal] not in processes, signal
    if signal in instructions:
        processes[instructions[signal]] = func
    else:
        logging.warning("\"%s\" is not in instructions", signal)
    return func


from bb.bd import BackdoorShell
shell = BackdoorShell()

commands = {
    "shell": lambda line: shell.push(line),
}



if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()

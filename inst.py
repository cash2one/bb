#!/usr/bin/env python

import logging

processes = {}

instructions_list = [
    "ping",
    "pong",
    "type",
]

instructions = dict(zip(instructions_list, range(1, 2**16)))
print(instructions)


def handle_input(func):
    assert callable(func), func
    signal = func.__name__
    assert instructions[signal] not in processes, signal
    if signal in instructions_list:
        processes[instructions[signal]] = func
    else:
        logging.warning("\"%s\" is not in instructions_list", signal)
    return func


if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()

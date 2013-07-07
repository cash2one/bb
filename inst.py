#!/usr/bin/env python

import logging

processes = {}

instructions_list = [
    "ping",
    "pong",
    "type",
]

instructions = {}

for i, v in enumerate(instructions_list, 1):
    instructions[i] = v
    instructions[v] = i

def handle_input(signal):
    def reg(func):
        assert signal not in processes
        if signal in instructions_list:
            processes[signal] = func
        else:
            logging.warning("\"%s\" is not in instructions_list", signal)
        return func
    return reg

def handle_input(func):
    assert callable(func), func
    signal = func.__name__
    assert signal not in processes, signal
    if signal in instructions_list:
        processes[signal] = func
    else:
        logging.warning("\"%s\" is not in instructions_list", signal)
    #return func


if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()

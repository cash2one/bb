#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
>>> q0 = queue.Queue()
>>> q1 = queue.Queue()
>>> q2 = queue.Queue()
>>> i = 3
>>> PING = 1
>>> PONG = 2
>>> q0.put([i, PING, b'64'])
>>> q0.put(None)
>>> hub(q0, q1, q2)

>>> q1.get() == [i, PONG, b'65']
True
>>> len(q2.get())
6
>>> len(q2.get())
4
>>> len(q2.get())
3
>>> q2.get() is None 
True

>>> q0.qsize(), q1.qsize(), q2.qsize()
(0, 0, 0)

"""

from __future__ import division, print_function, unicode_literals

import functools
import logging
import sys

if sys.version_info[0] >= 3:
    import queue
else:
    str = unicode
    range = xrange
    import Queue as queue

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s:%(levelname)s:%(message)s",
                   )



_processes = {
    #'foo': process_message_foo,
    #'ping': process_message_ping,
    # ...
}

instructions = [
    "ping",
    "pong",
    "type",
]

_instructions = {}

for i, v in enumerate(instructions, 1):
    _instructions[i] = v
    _instructions[v] = i


def handle_input(signal):
    def reg(func):
        assert signal not in _processes
        _processes[signal] = func
        return func
    return reg

@handle_input("ping")
def process_example(i, obj):
    yield "send", i, "pong", obj + 1
    yield "log", i, "record_some_thing", 3, {"xixi": 2}
    yield "save", i, "gold", list(range(100))
    yield
    yield
    yield "pay", i, 10

@handle_input("pong")
def process_example(i, obj):
    return [("send", i, "pong", obj - 1), ("send", i, "pong", obj - 2)]

@handle_input("type")
def process_example(i, obj):
    yield "send", i, "type", {"t": str(type(obj)), "v": obj}


def hub(Q_in, Q_out, Q_err):
    from time import time
    import signal
    def not_be_terminated(signal_number, stack_frame):
        logging.warning("received SIGTERM")
    signal.signal(signal.SIGTERM, not_be_terminated)

    # None: shutdown
    # (signal, int, bytes): process request from Q_in

    _filter = functools.partial(filter, None)

    procs = _processes
    instrs = _instructions

    from json import dumps, loads
    dump1 = functools.partial(dumps, ensure_ascii=False,
                              separators = (",", ":"))
    dump2 = functools.partial(dumps, ensure_ascii=False,
                              separators = (",", ": "),
                              sort_keys=True, indent=4)

    def send(_, i, k, obj):
        Q_out.put([int(i), instrs[k], dump1(obj).encode()])

    def save(cmd, i, k, obj):
        Q_err.put([cmd, int(i), k, obj])

    def log(cmd, i, k, n, infos):
        Q_err.put([cmd, int(i), time(), k, n, infos])

    def pay(cmd, i, n):
        Q_err.put([cmd, int(i), n])

    consumers = {
        "send": send,
        "save": save,
        "log": log,
        "pay": pay,
    }

    while True:
        try:
            v = Q_in.get()
        except Exception as e:
            logging.error(e)
            continue

        if v is None:
            logging.debug("hub exit")
            Q_err.put(None)
            break

        try:
            producer = procs[instrs[v[1]]]
            outs = producer(v[0], loads(v[2].decode()))
            #if not isinstance(outs, list):
                #outs = list(outs)
            for f in _filter(outs):
                consumers[f[0]](*f)
        except Exception:
            logging.exception("!!!")



if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()

#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
>>> q0 = queue.Queue()
>>> q1 = queue.Queue()
>>> q2 = queue.Queue()
>>> i = 3
>>> PING = 1
>>> PONG = 2
>>> q0.put((i, PING, b'64'))
>>> q0.put(None)
>>> hub(q0, q1, q2)

>>> q1.get() == (i, PONG, b'65')
True
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

instructions = {
    "ping": 1,
    "pong": 2,
    1: "ping",
    2: "pong",
}

def handle_input(signal):
    def reg(generator_function):
        _processes[signal] = generator_function
        return generator_function
    return reg

@handle_input("ping")
def process_example(i, obj):
    yield "send", i, "pong", obj + 1
    #yield 'log', i, 'example_log', 1, 2, 3

@handle_input("pong")
def process_example(i, obj):
    yield "send", i, "pong", obj - 1


def hub(Q_in, Q_out, Q_err):
    import signal
    def not_be_terminated(signal_number, stack_frame):
        logging.warning("received SIGTERM")
    signal.signal(signal.SIGTERM, not_be_terminated)

    # None: shutdown
    # (signal, int, bytes): process request from Q_in

    my_filter = functools.partial(filter, None)

    processes = _processes

    from json import dumps, loads
    separators = (",", ":")

    def send(_, i, k, obj):
        Q_out.put((i,
                   instructions[k],
                   dumps(obj, separators=separators).encode()))

    def err(*args):
        Q_err.put(args)

    consumers = {
        "send": send,
        "err": err,
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
            producer = processes[instructions[v[1]]]
            foods = my_filter(producer(v[0], loads(v[2].decode())))
            for f in foods:
                consumers[f[0]](*f)
        except Exception:
            logging.exception("!!!")



if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()

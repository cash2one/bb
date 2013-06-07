#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
>>> q0 = queue.Queue()
>>> q1 = queue.Queue()
>>> q2 = queue.Queue()
>>> i = 3
>>> q0.put((i, "ping", b'64'))
>>> q0.put(None)
>>> hub(q0, q1, q2)

>>> q1.get() == (i, "pong", b'65')
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

def handle_input(signal):
    def reg(generator_function):
        _processes[signal] = generator_function
        return generator_function
    return reg

@handle_input('ping')
def process_example(i, obj):
    yield "out", i, "pong", obj + 1
    #yield 'log', i, 'example_log', 1, 2, 3


def hub(Q_in, Q_out, Q_err):
    import signal
    def not_be_terminated(signal_number, stack_frame):
        logging.warning('received SIGTERM')
    signal.signal(signal.SIGTERM, not_be_terminated)

    # None: shutdown
    # (signal, int, bytes): process request from Q_in

    my_filter = functools.partial(filter, None)

    processes = _processes

    from json import dumps, loads

    def out(_, i, k, obj):
        Q_out.put((i, k, dumps(obj).encode()))

    def err(*args):
        Q_err.put(args)

    productors = {
        "out": out,
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
            foods = my_filter(processes[v[1]](v[0], loads(v[2].decode()))) #;foods = list(foods)   # optional
            for f in foods:
                productors[f[0]](*f)
        except Exception:
            logging.exception("!!!")



if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()

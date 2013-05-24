#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
>>> q0 = queue.Queue()
>>> q1 = queue.Queue()
>>> q2 = queue.Queue()
>>> pid = 3
>>> q0.put(('ping', pid, 64))
>>> q0.put(('_log', pid, 'lv', (42, 'qu')))
>>> q0.put(('_res', pid, {}))
>>> q0.put(None)
>>> hub(q0, q1, q2)

>>> q1.get() == ('pong', pid, 64 + 1)
True
>>> q2.get() == ('log', pid, 'example_log', 1, 2, 3)
True
>>> q2.get() == ('read', pid)
True
>>> q2.get() == ('write', pid, 'some_key', ['this', 'is', 'a', 'list'])
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
    yield 'send', 'pong', i, obj + 1
    yield 'log', i, 'example_log', 1, 2, 3
    yield 'read', i
    yield 'write', i, 'some_key', ['this', 'is', 'a', 'list']


def hub(Q_in, Q_out, Q_err):
    import signal
    def not_be_terminated(signal_number, stack_frame):
        logging.warning('received SIGTERM')
    signal.signal(signal.SIGTERM, not_be_terminated)

    # None: shutdown
    # (signal, int, bytes): process request from Q_in

    my_filter = functools.partial(filter, None)

    processes = _processes

    def proc_log_echo(*args):
        logging.debug("proc_log_echo: %r", args)
        yield

    def proc_res_echo(*args):
        logging.debug("proc_res_echo: %r", args)
        yield

    processes['_log'] = proc_log_echo
    processes['_res'] = proc_res_echo


    def send(_, k, i, obj):
        Q_out.put((k, i, obj))

    def log(*args):
        Q_err.put(args)

    productors = {
        'send': send,
        'log': log,
        'read': log,
        'write': log,
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
            foods = my_filter(processes[v[0]](*v[1:]))
            #foods = list(foods)   # optional
            for f in foods:
                #logging.debug(f)
                productors[f[0]](*f)
        except Exception:
            logging.exception('!!!')



if __name__ == '__main__':
    print('doctest:')
    import doctest
    doctest.testmod()

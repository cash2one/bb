#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
>>> q0 = queue.Queue()
>>> q1 = queue.Queue()
>>> q2 = queue.Queue()
>>> q0.put((1, 0, b'1'))
>>> q0.put((1, 'lv', (42, 'qu')))
>>> q0.put((1, {}))
>>> q0.put(None)
>>> hub(q0, q1, q2)

>>> q1.get() == (1, 65535, b'1')
True
>>> q1.get() == (0, 0, b'1')
True
>>> q1.get() == (0, 0, b'2')
True
>>> q2.get() == ('log', 1, 'example', 1, 2, 3)
True
>>> q2.get() == None
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


# config, sync with client
_aliases = {
    'foo': 0,
    'bar': 65535,
}

_processes = {
    #0: process_example,
    # ...
}

def handle_input(alias):
    def reg(func):
        _processes[_aliases[alias]] = func
        return func
    return reg

@handle_input('foo')
def process_example(i, obj):
    yield 'send', i, 'bar', obj
    yield 'log', i, 'example', 1, 2, 3



def hub(Q_in, Q_out, Q_err):
    import signal
    def not_be_terminated(signal_number, stack_frame):
        logging.warning('received SIGTERM')
    signal.signal(signal.SIGTERM, not_be_terminated)

    # None: shutdown
    # (int, int, bytes): process request from client
    # (int, str, ...): process log event came from log system
    # (int, dict): process result came from log system

    from json import dumps, loads
    my_filter = functools.partial(filter, None)
    valid = tuple   # or list

    processes = _processes
    aliases = _aliases

    def proc_request(i, k, b):
        return processes[k](i, loads(b.decode()))

    def proc_event(i, e, *args):
        yield 'send', 0, 'foo', 1

    def proc_source(i, d):
        yield 'send', 0, 'foo', 2

    # must be generator
    consumers = {
        int: proc_request,
        str: proc_event,
        dict: proc_source,
    }

    def send(_, i, k, obj):
        Q_out.put((i, aliases[k], dumps(obj).encode()))

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
            logging.debug(v)
        except Exception as e:
            logging.error(e)
            continue

        if v is None:
            logging.debug("hub exit")
            Q_err.put(None)
            break

        if v.__class__ is valid:
            try:
                foods = my_filter(consumers[v[1].__class__](*v))
                #foods = list(foods)   # optional
                for f in foods:
                    productors[f[0]](*f)
            except Exception:
                logging.exception('!!!')

        else:
            logging.warning(v)


if __name__ == '__main__':
    import doctest
    doctest.testmod()

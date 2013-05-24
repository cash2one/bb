#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
>>> q0 = queue.Queue()
>>> q2 = queue.Queue()
>>> pid = 2
>>> q2.put(('log', pid, 'dead', 1, 2, 3))
>>> q2.put(('read', pid))
>>> q2.put(('write', pid, 't', 42))
>>> q2.put(None)
>>> log(q0, q2)

>>> k, i, v, a = q0.get()
>>> k == '_log'
True
>>> i == pid
True
>>> v == 'dead'
True
>>> a == (1, 2, 3)
True

>>> k, i, v = q0.get()
>>> k == '_res'
True
>>> i == pid
True
>>> isinstance(v, dict)
True
>>> q0.qsize(), q2.qsize()
(0, 0)

"""

from __future__ import division, print_function, unicode_literals

import functools
import logging
import os
import sys

if sys.version_info[0] >= 3:
    import queue
    open = functools.partial(open, encoding='utf-8')
else:
    str = unicode
    range = xrange
    import Queue as queue

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s:%(levelname)s:%(message)s",
                   )



def log(Q_in, Q_err):
    import signal
    def not_be_terminated(signal_number, stack_frame):
        logging.warning('received SIGTERM')
    signal.signal(signal.SIGTERM, not_be_terminated)

    # None: shutdown
    # (command_word, int, str, ...): logs
    # (command_word, ...): some other commands

    from json import dump, load

    def log(i, k, *args):
        #logging.debug("%d, %s, %r" % (i, k, args))
        Q_in.put(('_log', i, k, args))

    def read(i):
        home = str(i)
        if not os.path.exists(home):
            os.mkdir(home)
        source = {}
        for k in os.listdir(home):
            with open("%s/%s" % (home, k)) as f:
                source[k] = load(f)
        Q_in.put(('_res', i, source))

    def write(i, k, v):
        with open("%s/%s" % (i, k), 'w') as f:
            dump(v, f)

    consumers = {
        'log': log,
        'read': read,
        'write': write,
    }

    while True:
        try:
            v = Q_err.get()
        except Exception as e:
            logging.error(e)
            continue

        if v is None:
            logging.debug("log exit")
            break

        try:
            consumers[v[0]](*v[1:])
        except Exception:
            logging.exception('!!!')


if __name__ == '__main__':
    print('doctest:')
    import doctest
    doctest.testmod()


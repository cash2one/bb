#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
>>> q2 = queue.Queue()
>>> i = 2
>>> q2.put(["log", i, 1370883768.117528, "dead", {"killed by": 3}, 1])
>>> q2.put(["save", i, "gold", b'1'])
>>> q2.put(None)
>>> log(q2)

>>> q2.qsize()
0

"""

from __future__ import division, print_function, unicode_literals

import functools
import logging
import os
import sys

if sys.version_info[0] >= 3:
    import queue
    #open = functools.partial(open, encoding="utf-8")
else:
    str = unicode
    range = xrange
    import Queue as queue

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s:%(levelname)s:%(message)s",
                   )



def log(Q_err):
    import signal
    def not_be_terminated(signal_number, stack_frame):
        logging.warning("received SIGTERM")
    signal.signal(signal.SIGTERM, not_be_terminated)

    # None: shutdown
    # (command_word, int, str, ...): logs
    # (command_word, ...): some other commands

    def log(_, i, t, k, infos, n):
        logging.info("%d, %f, %s, %r, %d", i, t, k, infos, n)

    def save(_, i, k, v):
        logging.info("%s/%s: %r", i, k, v)
        return
        with open("%s/%s" % (i, k), 'wb') as f:
            f.write(v)

    def pay(_, i, n):
        logging.info("%d, %d", i, n)

    consumers = {
        "log": log,
        "save": save,
        "pay": pay,
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
            consumers[v[0]](*v)
        except Exception:
            logging.exception("!!!")


if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()


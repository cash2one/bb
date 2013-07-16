#!/usr/bin/env python

"""
>>> import queue
>>> q2 = queue.Queue()
>>> i = 2
>>> q2.put(["log", i, "dead", {"killed by": 3}, 1])
>>> q2.put(["save", i, "gold", b'1'])
>>> q2.put(None)
>>> log(q2)

>>> q2.qsize()
0
"""


def worker(Q):
    import logging
    while True:
        v = Q.get()
        logging.info(v)
        if v is None:
            break

def log(Q_err):
    import logging
    import signal
    def not_be_terminated(signal_number, stack_frame):
        logging.warning("received SIGTERM")
    signal.signal(signal.SIGTERM, not_be_terminated)

    from threading import Thread
    from queue import Queue
    Q = Queue()

    Thread(target=worker, args=(Q,)).start()

    while True:
        try:
            v = Q_err.get()
            Q.put(v)
        except Exception as e:
            logging.error(e)
            continue

        if v is None:
            logging.debug("log exit")
            Q.put(None)
            break



if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()


#!/usr/bin/env python

"""
>>> import queue
>>> q2 = queue.Queue()
>>> i = 2
>>> q2.put(["log", i, 1370883768.117528, "dead", {"killed by": 3}, 1])
>>> q2.put(["save", i, "gold", b'1'])
>>> q2.put(None)
>>> log(q2)

>>> q2.qsize()
0
"""


def log(Q_err):
    import logging
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

    def pay(_, i, n):
        logging.info("%d, %d", i, n)

    def fight(_, i, n):
        logging.info("%d, %d", i, n)

    consumers = [
        log,
        save,
        pay,
        fight,
    ]

    for c in consumers:
        assert callable(c), c

    cm = {c.__name__: c for c in consumers}

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
            cm[v[0]](*v)
        except Exception:
            logging.exception("!!!")


if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()


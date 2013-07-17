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
    logging.info("log_worker start")
    while True:
        v = Q.get()
        logging.info(v)   # TODO
        if v is None:
            break
        Q.task_done()
    logging.info("log_worker exit")
    Q.task_done()

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
            logging.info("log exit")
            break

    Q.join()


def test(Q):
    while True:
        v = Q.get()
        print(v)
        if v is None:
            break
        Q.task_done()
    Q.task_done()

def main():
    from threading import Thread
    from queue import Queue

    n = 3
    Q = Queue()

    for i in range(n):
        Thread(target=test, args=(Q,)).start()

    for i in range(100):
        Q.put(i)

    for i in range(n):
        Q.put(None)
    Q.join()



if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()
    #main()


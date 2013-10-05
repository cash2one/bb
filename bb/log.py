#!/usr/bin/env python3

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
        Q.task_done()
        if v is None:
            break
        logging.info(v)   # TODO
    logging.info("log_worker exit")

def log(Q_err):
    import logging
    import signal

    def terminate(signal_number, stack_frame):
        logging.warning("received SIGTERM")
        nonlocal loop
        loop = False
    signal.signal(signal.SIGTERM, terminate)


    from threading import Thread
    from queue import Queue

    Q = Queue()
    Thread(target=worker, args=(Q,)).start()

    loop = True
    while loop:
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
    i = 0
    while True:
        v = Q.get()
        Q.task_done()
        #print(v)
        if v is None:
            break
        else:
            i += 1
    print(i)

def main():
    from threading import Thread
    from queue import Queue

    n = 3
    Q = Queue()

    for i in range(n):
        Thread(target=test, args=(Q,)).start()

    for i in range(1000**2):
        Q.put(i)
    print(i)

    for i in range(n):
        Q.put(None)
    Q.join()



if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()
    main()


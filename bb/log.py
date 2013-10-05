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

def worker(name, Q, task):
    import logging
    import time

    logging.info("log_worker %s start" % name)

    while True:
        v = Q.get()
        if v is None:
            break
        logging.info("%r: %r" % (name, v))

        try:
            task(*v)
            time.sleep(1)  # test blocking
        except Exception as e:
            logging.error(e)

        Q.task_done()

    logging.info("log_worker %s exit" % name)
    Q.task_done()


def log(Q_err):
    import logging
    import signal

    def terminate(signal_number, stack_frame):
        logging.warning("received SIGTERM")
        nonlocal loop
        loop = False
    signal.signal(signal.SIGTERM, terminate)

    from redis import StrictRedis
    db = StrictRedis()

    from threading import Thread
    from queue import Queue

    from bb.js import dump2

    tasks = {
        "save": (Queue(), lambda i, k, v: db.hset(i, k, dump2(v))),
        "log": (Queue(), lambda *args: logging.info(args)),
        "battle": (Queue(), lambda *args: logging.info(args)),
        "buy": (Queue(), lambda *args: logging.info(args)),
    }

    for k, v in tasks.items():
        Thread(target=worker, args=(k, v[0], v[1])).start()

    loop = True
    while loop:
        try:
            v = Q_err.get()
        except Exception as e:
            logging.error(e)
            continue

        if v is None:
            for q, _ in tasks.values():
                q.put(None)
                q.join()
            logging.info("log exit")
            break

        try:
            tasks[v[0]][0].put(v[1:])
        except Exception as e:
            logging.error(e)



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

    for i in range(100**2):
        Q.put(i)
    print(i)

    for i in range(n):
        Q.put(None)
    Q.join()



if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()
    #main()

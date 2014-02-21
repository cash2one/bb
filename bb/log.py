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

    get = Q.get
    done = Q.task_done

    while True:
        v = get()
        if v is None:
            break
        logging.info("%r: %r" % (name, v))

        try:
            task(*v)
            time.sleep(0.01)  # test blocking
        except Exception as e:
            logging.error(e)

        done()

    logging.info("log_worker %s exit" % name)
    done()


def log(Q_err, debug=True):
    import collections
    import logging
    import signal

    def terminate(signal_number, stack_frame):
        logging.warning("received SIGTERM")
        nonlocal loop
        loop = False

    try:
        signal.signal(signal.SIGTERM, terminate)
    except ValueError as e:
        logging.info(e)

    from threading import Thread
    from queue import Queue

    from redis import StrictRedis
    from .const import DB_HOST, DB_PORT, WORLD
    #db = StrictRedis(DB_HOST, DB_PORT)
    #hset = db.hset

    from .oc import record, recorder
    from .js import dump2

    def _save(i, k, v):
        if i == 0:
            i = WORLD
        #hset(i, k, dump2(v))

    tasks = {
        "save": (Queue(), _save),
        "log": (Queue(), lambda *args: logging.info(args)),
        "battle": (Queue(), lambda *args: logging.info(args)),
        "buy": (Queue(), lambda *args: logging.info(args)),
    }

    puts = {k: v[0].put for k, v in tasks.items()}

    for k, v in tasks.items():
        Thread(target=worker, args=(k, v[0], v[1])).start()

    get = Q_err.get
    loop = True

    while loop:
        try:
            v = get()
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
            puts[v[0]](v[1:])
        except Exception as e:
            logging.error(e)



def test(Q):
    i = 0
    get = Q.get
    done = Q.task_done
    while True:
        v = get()
        done()
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
    put = Q.put

    for i in range(n):
        Thread(target=test, args=(Q,)).start()

    for i in range(100**2):
        put(i)
    print(i)

    for i in range(n):
        put(None)
    Q.join()



if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()
    main()

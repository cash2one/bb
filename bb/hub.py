#!/usr/bin/env python

"""
>>> import queue
>>> q0 = queue.Queue()
>>> q1 = queue.Queue()
>>> q2 = queue.Queue()
>>> i = 2
>>> PING = 1
>>> PONG = 2
>>> q0.put([i, PING, "64"])
>>> q0.put(None)
>>> hub(q0, q1, q2)

>>> q1.get() == [i, PONG, "64"]
True
>>> q2.get() == ["save", i, "foo", 5]
True
>>> q2.get() is None 
True

>>> q0.qsize(), q1.qsize(), q2.qsize()
(0, 0, 0)

"""

def hub(Q_in, Q_out, Q_err):
    import functools
    import logging
    import io
    import signal
    import traceback

    from json import loads

    from bb import inst   # load all
    from bb.i import I, P
    from bb.js import dump1


    def not_be_terminated(signal_number, stack_frame):
        logging.warning("received SIGTERM")
        nonlocal loop
        loop = False
    signal.signal(signal.SIGTERM, not_be_terminated)


    _filter = functools.partial(filter, None)

    processes = inst.processes
    commands = inst.commands
    instructions = inst.instructions


    def init():
        # load others
        from os.path import splitext
        from glob import glob
        for m in set(map(lambda s: splitext(s)[0], glob('[a-z]*.py*'))):
            __import__(m)

        from collections import Counter

        from redis import StrictRedis
        db = StrictRedis()
        pipe = db.pipeline()
        raw = db.hgetall("z")  # TODO
        logging.info(len(raw))
        uids = {}
        for u, i in raw.items():
            uids[u.decode()] = int(i)  # raise it if error
        ids = list(uids.values())
        checker = Counter(ids)
        if len(checker) != len(ids):  # unique
            raise ValueError(checker.most_common(3))
        for i in ids:
            pipe.hgetall(i)
        properties = pipe.execute(True)  # DO NOT allow error occurs in redis

        for i, p in zip(ids, properties):
            d = {k.decode(): loads(v.decode()) for k, v in p.items()}
            P[i] = I(i, d)

    try:
        init()
        logging.info(len(P))
    except Exception as e:
        logging.exception(e)
        Q_err.put(None)
        return

    import gc
    gc.collect()
    loop = True
    while loop:
        try:
            v = Q_in.get()
        except Exception as e:
            logging.error(e)
            continue

        if v is None:
            logging.info("hub exit")
            Q_err.put(None)
            break

        try:
            if len(v) == 2:
                cmd, data = v
                try:
                    output = commands[cmd](data)
                except Exception:
                    _output = io.StringIO()
                    traceback.print_exc(file=_output)
                    output = _output.getvalue()
                    logging.exception(v)
                Q_out.put([cmd, output])   # echo cmd and result(or error)
            else:
                i, cmd, data = v
                producer = processes[cmd]
                outs = producer(P[i], loads(data))
                if outs:
                    for x in _filter(outs):   # is _filter neccessary?
                        if isinstance(x[0], int):
                            i, cmd, data = x
                            Q_out.put([i, instructions[cmd], dump1(data)])
                        else:
                            Q_err.put(x)
        except Exception:
            logging.exception(v)



if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()

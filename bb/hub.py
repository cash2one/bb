#!/usr/bin/env python

"""
>>> import queue
>>> q0 = queue.Queue()
>>> q1 = queue.Queue()
>>> q2 = queue.Queue()
>>> i = 3
>>> PING = 1
>>> PONG = 2
>>> q0.put([i, PING, b'64'])
>>> q0.put(None)
>>> hub(q0, q1, q2)

>>> q1.get() == [i, PONG, b'65']
True
>>> q1.get() == [2, PONG, b'66']
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
    import signal

    from bb import other, inst   # load all

    def not_be_terminated(signal_number, stack_frame):
        logging.warning("received SIGTERM")
    signal.signal(signal.SIGTERM, not_be_terminated)

    # None: shutdown
    # (signal, int, bytes): process request from Q_in

    _filter = functools.partial(filter, None)

    processes = inst.processes
    instructions = inst.instructions

    from json import dumps, loads, JSONEncoder

    class BBEncoder(JSONEncoder):
        def default(self, obj):
            if isinstance(obj, set):
                return list(obj)
            return JSONEncoder.default(self, obj)

    dump1 = functools.partial(dumps, ensure_ascii=False,
                              cls=BBEncoder,
                              separators = (",", ":"))
    dump2 = functools.partial(dumps, ensure_ascii=False,
                              cls=BBEncoder,
                              separators = (",", ": "),
                              sort_keys=True, indent=4)

    def init():
        from collections import Counter
        from redis import StrictRedis
        db = StrictRedis("via")
        pipe = db.pipeline()

        raw = db.hgetall("z")
        logging.info(len(raw))
        uids = {}
        for u, i in raw.items():
            if i.isdigit():
                uids[u.decode()] = int(i)
            else:
                logging.warning("%s -> %s", u, i)

        ids = list(uids.values())
        checker = Counter(ids)
        if len(checker) != len(ids):
            raise ValueError(checker.most_common(3))

        for i in ids:
            pipe.hgetall(i)
        properties = pipe.execute(False)
        P = other.P
        I = other.I
        for i, p in zip(ids, properties):
            if isinstance(p, dict):
                try:
                    d = {k.decode(): loads(v.decode()) for k, v in p.items()}
                    P[i] = I(i, d)
                except Exception as e:
                    logging.warning("%s: %d -> %s", e, i, p)
            else:
                logging.warning("%d -> %s", i, p)

    try:
        init()
        logging.info(len(other.P))
    except Exception as e:
        logging.exception(e)
        Q_err.put(None)
        return

    while True:
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
            producer = processes[v[1]]
            outs = producer(v[0], loads(v[2].decode()))
            if outs:
                for x in _filter(outs):   # is _filter neccessary?
                    i = x[0]
                    if isinstance(i, int):
                        Q_out.put([i, instructions[x[1]], dump1(x[2]).encode()])
                    else:
                        Q_err.put(x)
        except Exception:
            logging.exception("!!!")



if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()

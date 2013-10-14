#!/usr/bin/env python3

"""
>>> import queue
>>> q0 = queue.Queue()
>>> q1 = queue.Queue()
>>> q2 = queue.Queue()
>>> q0.put([1, 0, "0"])
>>> q0.put(None)
>>> hub(q0, q1, q2)

>>> q1.get() == [1, 0, "0"]
True
>>> q2.get() is None 
True

>>> q0.qsize(), q1.qsize(), q2.qsize()
(0, 0, 0)

"""


from bb import opt

def hub(Q_in, Q_out, Q_err, options=opt):
    import functools
    import logging
    import io
    import signal
    import traceback

    from json import loads

    from bb import inst   # load all instructions
    from bb.i import P
    from bb.js import dump1
    from bb.exc import exc_map, exc_recorder
    from bb.srv import load_data, build_all, check_all, import_others


    def terminate(signal_number, stack_frame):
        logging.warning("received SIGTERM")
        nonlocal loop
        loop = False

    try:
        signal.signal(signal.SIGTERM, terminate)
    except ValueError as e:
        logging.info(e)

    _filter = functools.partial(filter, None)

    processes = inst.processes
    commands = inst.commands
    instructions = inst.instructions

    try:
        build_all(load_data(options))
        check_all()
        import_others()
        logging.info(len(P))
    except Exception:
        logging.exception("init error")
        Q_err.put(None)
        return

    import gc
    gc.collect()

    _in = Q_in.get
    _out = Q_out.put
    _err = Q_err.put

    if options.debug:
        from time import strftime
        from redis import StrictRedis
        debug = StrictRedis(options.db_host, options.db_port)
        def _in():
            v = Q_in.get()
            debug.rpush("io", "%s in %s" % (strftime("%H:%M:%S"), v))
            return v
        def _out(v):
            debug.rpush("io", "%s out %s" % (strftime("%H:%M:%S"), v))
            Q_out.put(v)
        def _err(v):
            debug.rpush("io", "%s err %s" % (strftime("%H:%M:%S"), v))
            Q_err.put(v)

    loop = True

    while loop:
        try:
            v = _in()
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
                _out([cmd, output])   # echo cmd and result(or error)
            else:
                i, cmd, data = v
                producer = processes[cmd]
                try:
                    if producer:
                        outs = producer(P[i], loads(data))
                    else:
                        raise NotImplementedError(cmd)
                except Exception as e:
                    err = e.__class__.__name__
                    _out([i, 0, dump1(exc_map.get(err, 0))])
                    exc_recorder[i][err] += 1
                    raise e
                if outs:
                    for x in _filter(outs):   # is _filter neccessary?
                        if isinstance(x[0], int):
                            i, cmd, data = x
                            _out([i, instructions[cmd], dump1(data)])
                        else:
                            _err(x)
        except Exception:
            logging.exception(v)



if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()

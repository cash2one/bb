#!/usr/bin/env python3

"""
python3 -OO -m cProfile -s cumtime _.py >profile.txt
yes bag 1 | head -1000 | (./cli.py; sleep 3) | nc localhost 8000 >out
"""

if __name__ == "__main__":
    import collections
    import gc
    import itertools
    import os
    import time
    import urllib.parse
    import urllib.request

    from tornado.options import define, options, parse_command_line

    from bb import const
    from bb import opt
    from bb.web import main

    gc.disable()

    for k in dir(opt):
        if k[0].isalpha():
            v = getattr(opt, k)
            if isinstance(v, list):
                define(k, default=v, type=type(v[0]), multiple=True)
            else:
                define(k, default=v, type=type(v))

    parse_command_line()

    args = {
        "start": time.strftime("%y%m%d-%H%M%S"),
        "port": options.port,
        "backstage": options.backstage,
    }
    args = urllib.parse.urlencode(args)

    def to_leader(key):
        if options.leader:  # disable this
            url = "http://{}/{}?{}".format(options.leader, key, args)
            print(url)
            with urllib.request.urlopen(url) as f:
                s = f.read().decode()
                if s:
                    from json import loads
                    for k, v in loads(s).items():
                        print(k, v)
                        setattr(const, k, v)


    pidfile = "bb.pid"

    pid = os.getpid()
    print(pid)

    if not __debug__ and os.path.exists(pidfile):
        raise Warning(pidfile)

    if not os.environ.get("SUPERVISOR_ENABLED"):
        with open(pidfile, "w") as f:
            f.write(str(pid))

    to_leader("reg")
    main(options)
    to_leader("quit")

    if os.path.exists(pidfile):
        os.remove(pidfile)

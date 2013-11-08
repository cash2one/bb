#!/usr/bin/env python3

if __name__ == "__main__":
    import collections
    import itertools
    import time
    import urllib.parse
    import urllib.request

    from tornado.options import define, options, parse_command_line

    from bb import opt
    from bb.web import main

    for k in dir(opt):
        if k[0].isalpha():
            v = getattr(opt, k)
            if isinstance(v, list):
                define(k, default=v, type=type(v[0]), multiple=True)
            else:
                define(k, default=v, type=type(v))

    define("debug", type=bool)

    parse_command_line()

    debug = options.debug = options.logging == "debug"

    zones = options.zones
    if len(set(zones)) != len(zones) or sorted(zones) != zones:
        raise ValueError(zones)

    ports = (options.port, options.backstage, options.backdoor)
    start_time = time.strftime("%y%m%d-%H%M%S")
    args = [("start", start_time)]
    args.extend(zip(itertools.repeat("ports"), ports))
    args.extend(zip(itertools.repeat("zones"), zones))
    args = urllib.parse.urlencode(args)

    def to_leader(key):
        if not debug:
            url = "http://%s/%s?%s" % (options.leader, key, args)
            with urllib.request.urlopen(url) as f:
                print(f.read().decode())

    to_leader("reg")

    main(*ports, debug=debug, options=options)

    to_leader("quit")

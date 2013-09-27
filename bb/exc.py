#!/usr/bin/env python3

def collect_exceptions():
    import builtins
    idx = 0
    for i in sorted(dir(builtins)):
        i = getattr(builtins, i)
        if type(i) is type and issubclass(i, Exception):
            idx += 1
            yield i, idx

exc_map = dict(collect_exceptions())

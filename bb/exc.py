#!/usr/bin/env python3

import builtins
import collections

def collect_exceptions():
    idx = 0
    for i in sorted(dir(builtins)):
        i = getattr(builtins, i)
        if type(i) is type and issubclass(i, Exception):
            idx += 1
            yield i.__name__, idx

exc_map = dict(collect_exceptions())
exc_recorder = collections.defaultdict(collections.Counter)


if __name__ == "__main__":
    from pprint import pprint
    pprint(exc_map)



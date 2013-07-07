#!/usr/bin/env python
# Objects' Counter

import collections
import functools
import gc


recorder = collections.defaultdict(
    functools.partial(collections.deque, maxlen=30))

def count():
    counter = collections.Counter()
    for obj in gc.get_objects():
        counter[type(obj)] += 1
    return counter

def record():
    for t, n in count().items():
        name = "%s.%s" % (t.__module__, t.__name__)
        recorder[name].append(n)



if __name__ == "__main__":
    for i in range(15):
        record()

    for k, v in recorder.items():
        print(k, list(v))

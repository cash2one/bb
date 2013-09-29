#!/usr/bin/env python3

"""
"""

def import_others():
    from os.path import splitext
    from glob import glob
    for m in set(map(lambda s: splitext(s)[0], glob('[a-z]*.py*'))):
        __import__(m)

def load_data(index_name):
    """from redis
    uniq in index
    """
    from json import loads
    from redis import StrictRedis
    db = StrictRedis()
    pipe = db.pipeline()
    raw = db.hgetall(index_name)
    assert not print("all:", len(raw))
    uids = {}  # unique identifiers
    for u, i in raw.items():
        uids[u.decode()] = int(i)  # raise it if error
    ids = list(uids.values())

    from collections import Counter
    checker = Counter(ids)
    if len(checker) != len(ids):  # not unique
        raise ValueError(checker.most_common(3))

    for i in ids:
        pipe.hgetall(i)
    properties = pipe.execute(True)  # DO NOT allow error occurs in redis

    raw = {}
    for i, p in zip(ids, properties):
        raw[i] = {k.decode(): loads(v.decode()) for k, v in p.items()}
    return raw

def build_all(data):
    """
    """
    from bb.i import I, P
    for i, v in data.items():
        P[i] = I(i, v)


limits = {
    "foo": lambda v: v < 10,
    "level": lambda v: v < 250,
}

from bb.i import I
tpl = I(0)
types = {k: type(tpl[k]) for k in I._defaults}
assert not print(types)

def check(i, limits=limits):
    for k, t in types.items():
        v = i.get(k)
        if v is not None and type(v) is not t:
            raise TypeError("%d %r %r" % (i.i, k, v))
    for k, v in i.items():
        f = limits.get(k)
        if f and not f(v):
            raise ValueError("%d %r %r" % (i.i, k, v))

def check_all(limits=limits):
    """
    """
    from bb.i import P
    for i in P.values():
        check(i, limits)


if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()

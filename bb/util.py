#!/usr/bin/env python

def build_dict(title, key, values, value_wraps={}):
    r"""
    >>> title = [{"x":1, "y":1, "z":1}, {"x":2, "y":4, "z":8}]
    >>> wraps1 = {"y": float}
    >>> wraps2 = {"z": str}
    >>> build_dict(title, "x", "y", wraps1)
    {1: 1.0, 2: 4.0}
    >>> build_dict(title, "x", ["y", "z"])
    {1: [1, 1], 2: [4, 8]}
    >>> build_dict(title, "x", ("y", "z"))
    {1: (1, 1), 2: (4, 8)}
    >>> build_dict(title, "x", {"y", "z"}, wraps2) == \
    ... {1: {"y": 1, "z": "1"}, 2: {"y": 4, "z": "8"}}
    True
    """
    def wrap(k):
        wrapper = value_wraps.get(k)
        return wrapper(x[k]) if wrapper else x[k]
    dct = {}
    if isinstance(values, str):
        for x in title:
            dct[x[key]] = wrap(values)
    elif isinstance(values, list):
        for x in title:
            dct[x[key]] = list(wrap(k) for k in values)
    elif isinstance(values, tuple):
        for x in title:
            dct[x[key]] = tuple(wrap(k) for k in values)
    elif isinstance(values, set):
        for x in title:
            dct[x[key]] = dict((k, wrap(k)) for k in values)
    else:
        raise ValueError(values)
    return dct

def build_list(title, keys, value_wraps={}):
    r"""
    >>> title = [{"x":1, "y":1, "z":1}, {"x":2, "y":4, "z":8}]
    >>> build_list(title, "z", {"z": float})
    [1.0, 8.0]
    >>> build_list(title, ["y", "z"])
    [[1, 1], [4, 8]]
    >>> build_list(title, ("y", "z"))
    [(1, 1), (4, 8)]
    >>> build_list(title, {"y", "z"}) == \
    ... [{'y': 1, 'z': 1}, {'y': 4, 'z': 8}]
    True
    """
    def wrap(k):
        wrapper = value_wraps.get(k)
        return wrapper(x[k]) if wrapper else x[k]
    lst = []
    if isinstance(keys, str):
        for x in title:
            lst.append(wrap(keys))
    elif isinstance(keys, list):
        for x in title:
            lst.append(list(wrap(k) for k in keys))
    elif isinstance(keys, tuple):
        for x in title:
            lst.append(tuple(wrap(k) for k in keys))
    elif isinstance(keys, set):
        for x in title:
            lst.append(dict((k, wrap(k)) for k in keys))
    else:
        raise ValueError(keys)
    return lst


# eval cache
class EvalCache(dict):
    """
    >>> eval_cache = EvalCache()
    >>> calc_task = ["%d + x" % i for i in range(1000)]
    >>> x = 1
    >>> sum(eval(c) for c in calc_task)   # always slow
    500500
    >>> sum(eval(eval_cache[c]) for c in calc_task)   # slow at first time
    500500
    >>> sum(eval(eval_cache[c]) for c in calc_task)   # faster!
    500500
    """
    def __missing__(self, k):
        code = compile(k, k, "eval")
        self[k] = code
        return code


class Object(object):
    """
    >>> obj = Object({"x": 1, "y": 2, "z": 3})
    >>> obj.a = 42
    >>> obj.x
    1
    >>> obj.a
    42
    """
    def __init__(self, dct=None):
        self.__dict__.update(dct or {})
    def __repr__(self):
        return repr(self.__dict__)


def list_to_tuple(v):
    """
    >>> list_to_tuple([[[]]])
    (((),),)
    """
    if isinstance(v, (list, tuple)):
        v = tuple(list_to_tuple(i) for i in v)
    return v


def flush(*caches):
    """
    >>> l1 = [1, 2]
    >>> l2 = [3, 4, 5]
    >>> flush(l1, l2)
    [1, 2, 3, 4, 5]
    >>> l1
    []
    >>> l2
    []
    """
    o = []
    for i in caches:
        o.extend(i)
        del i[:]
    return o



if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()


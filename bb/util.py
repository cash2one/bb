#!/usr/bin/env python

def build_dict(title, key, values):
    """
    >>> title = [{"x":1, "y":1, "z":1}, {"x":2, "y":4, "z":8}]
    >>> build_dict(title, "x", "y")
    {1: 1, 2: 4}
    >>> build_dict(title, "x", ["y", "z"])
    {1: [1, 1], 2: [4, 8]}
    >>> build_dict(title, "x", ("y", "z"))
    {1: (1, 1), 2: (4, 8)}
    >>> build_dict(title, "x", {"y", "z"})
    {1: {'y': 1, 'z': 1}, 2: {'y': 4, 'z': 8}}
    """
    if isinstance(values, str):
        dct = ([x[key], x[values]] for x in title)
    elif isinstance(values, list):
        dct = ([x[key], list(x[k] for k in values)] for x in title)
    elif isinstance(values, tuple):
        dct = ([x[key], tuple(x[k] for k in values)] for x in title)
    elif isinstance(values, set):
        dct = ([x[key], dict((k, x[k]) for k in values)] for x in title)
    else:
        raise ValueError(values)
    return dict(dct)

def build_list(title, keys):
    """
    >>> title = [{"x":1, "y":1, "z":1}, {"x":2, "y":4, "z":8}]
    >>> build_list(title, "z")
    [1, 8]
    >>> build_list(title, ["y", "z"])
    [[1, 1], [4, 8]]
    >>> build_list(title, ("y", "z"))
    [(1, 1), (4, 8)]
    >>> build_list(title, {"y", "z"})
    [{'y': 1, 'z': 1}, {'y': 4, 'z': 8}]
    """
    if isinstance(keys, str):
        lst = (x[keys] for x in title)
    elif isinstance(keys, list):
        lst = (list(x[k] for k in keys) for x in title)
    elif isinstance(keys, tuple):
        lst = (tuple(x[k] for k in keys) for x in title)
    elif isinstance(keys, set):
        lst = (dict((k, x[k]) for k in keys) for x in title)
    else:
        raise ValueError(keys)
    return list(lst)

# eval cache
class EvalCache(dict):
    def __missing__(self, k):
        code = compile(k, k, "eval")
        self[k] = code
        return code

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


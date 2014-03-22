#!/usr/bin/env python3

def patch_eval():
    import functools
    c = functools.lru_cache(maxsize=None)(compile)
    e = eval

    def _eval(expr, globals=None, locals=None):
        return e(c(expr, expr, "eval"), globals, locals)

    import builtins
    builtins.eval = _eval

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
    >>> build_dict(title, "x", {"y", "z"}) == \
    ... build_dict(title, "x", frozenset({"y", "z"})) == \
    ... {1: {1}, 2: {4, 8}}
    True
    >>> build_dict(title, "x", dict.fromkeys(["y", "z"]), wraps2) == \
    ... {1: {"y": 1, "z": "1"}, 2: {"y": 4, "z": "8"}}
    True
    >>> build_dict(title, "x", ["y", "not_exist"])
    {1: [1, None], 2: [4, None]}
    """
    def wrap(k):
        w = value_wraps.get(k)
        v = x.get(k)
        if v is not None and callable(w):
            v = w(v)
        return v
    dct = {}
    if isinstance(values, str):
        for x in title:
            dct[x[key]] = wrap(values)
    elif isinstance(values, dict):
        for x in title:
            dct[x[key]] = dict((k, wrap(k)) for k in values)
    elif isinstance(values, (list, tuple, set, frozenset)):
        _type = type(values)
        for x in title:
            dct[x[key]] = _type(wrap(k) for k in values)
    else:
        raise TypeError(values)
    return dct

def build_list(title, values, value_wraps={}):
    r"""
    >>> title = [{"x":1, "y":1, "z":1}, {"x":2, "y":4, "z":8}]
    >>> build_list(title, "z", {"z": float})
    [1.0, 8.0]
    >>> build_list(title, ["y", "z"])
    [[1, 1], [4, 8]]
    >>> build_list(title, ("y", "z"))
    [(1, 1), (4, 8)]
    >>> build_list(title, {"y", "z"}) == \
    ... build_list(title, frozenset({"y", "z"})) == \
    ... [{1}, {4, 8}]
    True
    >>> build_list(title, dict.fromkeys(["y", "z"])) == \
    ... [{'y': 1, 'z': 1}, {'y': 4, 'z': 8}]
    True
    >>> build_list(title, "null")
    [None, None]
    """
    def wrap(k):
        w = value_wraps.get(k)
        v = x.get(k)
        if v is not None and callable(w):
            v = w(v)
        return v
    lst = []
    if isinstance(values, str):
        for x in title:
            lst.append(wrap(values))
    elif isinstance(values, dict):
        for x in title:
            lst.append(dict((k, wrap(k)) for k in values))
    elif isinstance(values, (list, tuple, set, frozenset)):
        _type = type(values)
        for x in title:
            lst.append(_type(wrap(k) for k in values))
    else:
        raise TypeError(values)
    return lst


# eval cache
class EvalCache(dict):
    """
    >>> eval_cache = EvalCache()
    >>> calc_task = ["%d + x" % i for i in range(1000)]
    >>> x = 1
    >>> sum(eval(c) for c in calc_task)  # always slow
    500500
    >>> sum(eval(eval_cache[c]) for c in calc_task)  # slow at first time
    500500
    >>> sum(eval(eval_cache[c]) for c in calc_task)  # faster!
    500500
    """
    def __missing__(self, k):
        code = compile(k, k, "eval")
        self[k] = code
        return code

class Default(dict):
    """
    >>> env = Default()
    >>> eval("{a:b,c:1}", None, env) == {'a': 'b', 'c': 1}
    True
    """
    def __missing__(self, k):
        return k

class Object(object):
    """
    >>> obj = Object({"x": 1, "y": 2, "z": 3})
    >>> obj.items = 42
    >>> obj.x
    1
    >>> obj.items
    42
    >>> Object()
    {}
    >>> Object({"key": "value"})
    {'key': 'value'}
    >>> obj = Object()
    >>> setattr(obj, "k", "v")
    >>> obj
    {'k': 'v'}
    """
    def __init__(self, dct=None):
        if isinstance(dct, dict):
            self.__dict__.update(dct)
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

def list_all_same_type(type_conv):
    """
    >>> list_float = list_all_same_type(float)
    >>> list_int = list_all_same_type(int)
    >>> list_float(["3.14", list(range(5))])
    [3.14, [0.0, 1.0, 2.0, 3.0, 4.0]]
    >>> list_int([1.1, 2.2])
    [1, 2]
    """
    def conv(v):
        return [conv(i) for i in v] if isinstance(v, list) else type_conv(v)
    return conv


if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()


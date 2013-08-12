#!/usr/bin/env python

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


#!/usr/bin/env python


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
        i.clear()
    return o

if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()


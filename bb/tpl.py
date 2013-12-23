#!/usr/bin/env python3

"""
"""

from .i import I
i = I(0)
types = {k: type(i[k]) for k in I._defaults}

limits = {
    "foo": lambda v: v < 10,
    "level": lambda v: v < 250,
}

for k, v in i.items():
    if k in limits:
        assert limits[k](v), k
assert all(limits[k](v) for k, v in i.items() if k in limits)

if __name__ == "__main__":
    print(types)
    print("doctest:")
    import doctest
    doctest.testmod()

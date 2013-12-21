#!/usr/bin/env python3

r"""
>>> dump1("中")
'"中"'
>>> dump1({1, 2})
'[1,2]'
>>> dump2({"a": 1, "b": 2})
'{\n    "a": 1,\n    "b": 2\n}'
"""

import functools
import json

dump1 = functools.partial(json.dumps, ensure_ascii=False, default=list,
                          separators=(",", ":"))

dump2 = functools.partial(json.dumps, ensure_ascii=False, default=list,
                          separators=(",", ": "), sort_keys=True, indent=4)


if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()

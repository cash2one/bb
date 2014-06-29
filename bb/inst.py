#!/usr/bin/env python3

r"""
>>> commands["shell"]("1 + 6")
'7\n>>> '
"""

import functools


features = {}

processes = [None] * 2**11  # all is 2048

# {"ping": 0, "online": 1, ...}
from .const import INSTRUCTIONS


def handle(func):
    assert callable(func), func
    co = func.__code__
    assert co.co_argcount == 2, (co.co_filename, co.co_firstlineno)
    alias = func.__name__
    assert alias in INSTRUCTIONS, alias
    signal = INSTRUCTIONS[alias]
    assert processes[signal] is None, "%s:%d" % (alias, signal)
    processes[signal] = func
    return func

def pre(types=None, value_checker=None):
    if types is not None:
        assert isinstance(types, (type, tuple))
    if value_checker is not None:
        assert callable(value_checker)
    def decorator(func):
        co = func.__code__
        assert co.co_argcount == 2, (co.co_filename, co.co_firstlineno)
        @functools.wraps(func)
        def wrapper(i, x):
            if types and not isinstance(x, types):
                raise TypeError(x)
            if value_checker and not value_checker(x):
                raise ValueError(x)
            #story = i["story"]
            #if story < limit:
            #    raise ReferenceError(alias, limit, story)
            return func(i, x)
        return wrapper
    return decorator



import pprint
import sys

from .i import I, P
from .bd import Shell
from .msg import dump3

def _show(expression):
    if expression:
        v = eval(expression, None, sys.modules)
        s = dir(v)
    else:
        v = None
        s = list(sys.modules.keys())
    return expression, str(type(v)), pprint.pformat(v)[:MAXLEN], s

shell = Shell()
MAXLEN = 100 * 1024  # could be changed via backdoor or web

def _shell(input):
    output = shell.push(input)
    if output is None:
        return "... "
    else:
        return output[:MAXLEN] + ">>> "

commands = {
    "shell": _shell,
    "show": _show,
    "eval": lambda exp: dump3(eval(exp, None, sys.modules) if exp else None),
}



if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()

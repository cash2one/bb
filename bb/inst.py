#!/usr/bin/env python3

r"""
>>> commands["shell"]("1 + 6")
'7\n>>> '
"""


features = {}

processes = [None] * 2**11  # all is 2048

# {"ping": 0, "online": 1, ...}
from bb.const import instructions_list, INST_LEN, PING
instructions = dict(zip(instructions_list, range(PING, PING + INST_LEN)))


def handle(func):
    assert callable(func), func
    alias = func.__name__
    assert alias in instructions, alias
    signal = instructions[alias]
    assert processes[signal] is None, "%s:%d" % (alias, signal)
    processes[signal] = func
    return func

def pre(types=None, value_checker=None):
    if types is not None:
        assert isinstance(types, (type, tuple))
    if value_checker is not None:
        assert callable(value_checker)
    def decorator(func):
        alias = func.__name__
        limit = features.get(alias, 0)
        assert isinstance(limit, int)
        def _(i, x):
            if types and not isinstance(x, types):
                raise TypeError(x)
            if value_checker and not value_checker(x):
                raise ValueError(x)
            story = i["story"]
            if story < limit:
                raise ReferenceError(alias, limit, story)
            return func(i, x)
        _.__name__ = alias
        return _
    return decorator


runners = {}  # launch certain function in runners by web

def run(func):
    assert callable(func), func
    alias = func.__name__
    assert alias not in runners, alias
    runners[alias] = func
    return func


import gc
import json
import sys
import time

from bb.i import I, P
from bb.bd import BackdoorShell
from bb.oc import record, recorder
from bb.util import list_to_tuple
from bb.js import dump1

recorder.clear()
shell = BackdoorShell()

def _beginner(i, name):
    if i in P:
        raise KeyError("%d in P" % i)
    P[i] = I(i, {"name": name})
    return i

def _amend(i, k, v):
    _i = P[i]
    wrap = I._wrappers.get(k)
    v_new = wrap(v) if wrap else v
    v_old = _i.get(k)
    if k in I._defaults:
        v_old = _i[k]
        t_old, t_new = type(v_old), type(v_new)
        if t_old != t_new:
            raise ValueError("%s vs %s" % (t_old, t_new))
    _i[k] = v_new
    return i, k, v_old, v_new

def _view_data(i, k):
    i = P[i]
    if k:
        i = i[k]
    return dump1(i)

def _view(path, attr, call):
    if path:
        x = sys.modules[path[0]]
        for k in path[1:]:
            x = getattr(x, k)
        if attr is not None:
            x = [str(eval("x[%s]" % (attr,))), []]
        elif call is not None:
            x = [str(eval("x(%s)" % (call,))), []]
        else:
            x = [str(x), dir(x)]
    else:
        x = ["all modules", list(sys.modules.keys())]
    return x


commands = {
    "shell": lambda line: shell.push(line),
    "status": lambda _: record() or dict(recorder),
    "gc": lambda _: gc.collect(),
    "beginner": lambda args: _beginner(int(args[0]), args[1]),
    "amend": lambda args: _amend(int(args[0]), args[1], json.loads(args[2])),
    "run": lambda args: [runners[i]() or i for i in args if i],
    "render": lambda r: P[1].apply(P[1].render(list_to_tuple(r)), "from web"),
    "view_data": lambda args: _view_data(int(args[0]), args[1]),
    "view_logs": lambda args: list(P[int(args[0])].logs),
    "view": lambda args: _view(*args),
}



if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()

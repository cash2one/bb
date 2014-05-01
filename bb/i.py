#!/usr/bin/env python3

import collections

_VOID = {}  # immutable

if __debug__:
    from .const import INSTRUCTIONS_LIST

P = {}

def _register(attr, key, value):
    dct = getattr(I, attr)
    if not key:
        key = value.__name__
    assert isinstance(key, str), key
    assert key not in dct, key
    dct[key] = value
    return value

register_log_callback = lambda cb, name=None: _register("_hooks", name, cb)
register_default = lambda d, k=None: _register("_defaults", k, d)
register_wrapper = lambda w, k=None: _register("_wrappers", k, w)

def method(func, attr=None):
    #print(func, attr)
    assert func.__code__.co_argcount > 0
    setattr(I, attr if attr else func.__name__, func)


class I(dict):
    """
    """

    __slots__ = ["_i", "_cache", "_logs", "_listeners", "online"]

    # "foo": 5, "bar": lambda _: [_["foo"]],
    _defaults = {}

    # "stories": lambda raw: {int(k): v for k, v in raw.items()},
    _wrappers = {}

    # "func_name": func,
    _hooks = {}

    def __init__(self, n:int, source:dict=None):
        self._i = n
        self._cache = []
        self._logs = collections.deque(maxlen=50)
        self._listeners = collections.defaultdict(set)
        self.online = False
        if source:
            assert isinstance(source, dict), source
            for k, v in source.items():
                wrap = self._wrappers.get(k)
                self[k] = wrap(v) if wrap else v

    def __missing__(self, k):
        v = self._defaults[k]
        if callable(v):
            v = v(self)
        self[k] = v
        return v

    def __getattr__(self, k):  # use this prudently
        return self[k]

    # i is protected and readonly
    @property
    def i(self):
        return self._i

    def listen(self, log:str, cb:str, extra:hash):
        if callable(cb):
            cb = cb.__name__
        assert self._hooks[cb].__code__.co_argcount == 5, cb
        self._listeners[log].add((cb, extra))

    def deafen(self, log:str, cb:str, extra:hash):
        if callable(cb):
            cb = cb.__name__
        assert self._hooks[cb].__code__.co_argcount == 5, cb
        self._listeners[log].discard((cb, extra))

    def send(self, k:str, v):
        assert k in INSTRUCTIONS_LIST, k
        self._cache.append([self._i, k, v])

    def save(self, k:str):
        assert k in self._defaults, k
        self._cache.append(["save", self._i, k, self[k]])

    def log(self, k:str, meta:dict=_VOID, n:int=1):
        self._cache.append(["log", self._i, k, meta, n])
        self._logs.append([k, meta, n])
        for cb in list(self._listeners[k]):  # need a copy for iter
            self._hooks[cb[0]](cb[1], self, k, meta, n)  # cb may change listeners[k]

    def flush(self, *others) -> list:
        """be called at end"""
        f = []
        c = self._cache
        if c:
            f.extend(c)
            del c[:]
        for o in others:
            c = o._cache
            f.extend(c)
            del c[:]
        return f


if __name__ == "__main__":
    print("doctest:")
    import doctest
    doctest.testmod()

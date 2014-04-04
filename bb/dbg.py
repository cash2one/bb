#!/usr/bin/env python3

def fake(*args, **kwargs):
    pass

class Fake:
    def __call__(self, *args, **kwargs):
        pass
    def __getattr__(self, attr):
        return fake
    def inout(self, func):
        return func

show = Fake()

if __debug__:
    try:
        from show import show
    except ImportError:
        pass

show.set(where=True)

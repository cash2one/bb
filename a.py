#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

import collections
import multiprocessing
import time

import gc
gc.disable()

def t():
    c = collections.Counter(range(100))
    q = multiprocessing.Queue()

    t0 = time.time()
    for i in range(10000):
        q.put(c)
    t1 = time.time()
    for i in range(10000):
        q.get()
    t2 = time.time()

    print(t1 - t0)
    print(t2 - t1)

t()

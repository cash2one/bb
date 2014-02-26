#!/usr/bin/env python

import collections
import json
import random
import unittest

from bb.i import I, register_log_callback
from bb.msg import dumps, loads

@register_log_callback
def cb_test(extra, i, k, infos, n):
    i["foo"] += 1

class TestI(unittest.TestCase):
    def setUp(self):
        self.assertIn("cb_test", I._hooks),
        i = random.randint(1, 10000)
        self.i_flag = i
        self.i = I(i)

    def test_basic_attributes(self):
        i = self.i
        self.assertEqual(i.i, self.i_flag)
        self.assertIsInstance(i._cache, list)
        self.assertIsInstance(i._logs, collections.deque)
        self.assertIsInstance(i._listeners, collections.defaultdict)
        self.assertIs(i._listeners.default_factory, set)

    def test_item_attribute_read(self):
        i = self.i
        self.assertEqual(i.foo, 5)

    def test_default_items(self):
        i = self.i
        bar = i["bar"]
        self.assertEqual(bar, [5, 5, 5])
        self.assertIs(bar, i["bar"])

    def test_wrappers(self):
        self.assertGreaterEqual(set(I._defaults), set(I._wrappers))  # :)
        i = self.i
        for k, w in i._wrappers.items():
            v = i[k]
            v2 = w(loads(dumps(v)))
            self.assertEqual(v, v2)
            self.assertIs(type(v), type(v2))

    def test_bind(self):
        i = self.i
        i.bind("go", cb_test, None)
        self.assertEqual(i._listeners["go"], {("cb_test", None)})
        i.bind("go", "cb_test", (1, 2, 3, 4, 5))
        self.assertEqual(i._listeners["go"],
                         {("cb_test", None), ("cb_test", (1, 2, 3, 4, 5))})

    def test_unbind(self):
        i = self.i
        i.bind("go", "cb_test", None)
        self.assertEqual(len(i._listeners["go"]), 1)
        i.unbind("go", cb_test, None)
        self.assertEqual(len(i._listeners["go"]), 0)

    def test_bind_repeated(self):
        i = self.i
        for _  in range(100):
            i.bind("go", "cb_test", None)
        self.assertEqual(i._listeners["go"], {("cb_test", None)})

    def test_unbind_not_exist(self):
        i = self.i
        for _  in range(100):
            i.unbind("go", "cb_test", None)
        self.assertEqual(len(i._listeners["go"]), 0)

    def test_send(self):
        i = self.i
        i.send("ping", 1)
        i.send("ping", 2)
        self.assertEqual(
            i.flush(),
            [[self.i_flag, "ping", 1], [self.i_flag, "ping", 2]]
            )

    def test_save(self):
        i = self.i
        i.save("foo")
        i.save("bar")
        self.assertEqual(i.flush(),
                         [
                             ["save", self.i_flag, "foo", 5],
                             ["save", self.i_flag, "bar", [5, 5, 5]],
                         ])

    def test_log(self):
        i = self.i
        N = 10
        i.bind("jump", "cb_test", None)
        for _ in range(N):
            i.log("jump")
        self.assertEqual(len(i._cache), N)
        self.assertEqual(i.flush(), [["log", i.i, "jump", {}, 1]] * N)
        self.assertEqual(len(i._cache), 0)
        self.assertEqual(list(i._logs), [["jump", {}, 1]] * N)
        self.assertEqual(i.foo, 5 + N)

    def test_log_infos(self):
        i = self.i
        i.log("jump", {"height": 3}, 5)
        self.assertEqual(i.flush(), [["log", i.i, "jump", {"height": 3}, 5]])
        self.assertEqual(list(i._logs), [["jump", {"height": 3}, 5]])

    def test_render(self): #TODO
        i = self.i

    def test_apply(self): #TODO
        i = self.i

    def test_reward(self): #TODO
        i = self.i

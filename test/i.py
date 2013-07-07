#!/usr/bin/env python

import collections
import random
import unittest

from i import I, register_log_callback, _cbs

@register_log_callback
def cb_test(i, k, infos, n, *args):
    #print(i.i, k, infos, n, *args)
    i["foo"] += 1

class TestI(unittest.TestCase):
    def setUp(self):
        self.assertIn("cb_test", _cbs), 
        i = random.randint(1, 10000)
        self.i_flag = i
        self.i = I(i)
        self.assertIsInstance(I(i + 1, {"x": "yz"}), dict)

    def test_basic_attributes(self):
        i = self.i
        self.assertEqual(i.i, self.i_flag)
        self.assertIsInstance(i.cache, list)
        self.assertIsInstance(i.logs, collections.deque)
        self.assertEqual(i.logs.maxlen, I.DEQUE_MAXLEN)
        self.assertIsInstance(i.listeners, collections.defaultdict)
        self.assertIs(i.listeners.default_factory, set)

    def test_item_attribute_read(self):
        i = self.i
        self.assertEqual(i.foo, 5)

    def test_default_items(self):
        i = self.i
        self.assertEqual(i["foo"], 5)
        bar = i["bar"]
        self.assertEqual(bar, [])
        self.assertIs(bar, i["bar"])

    def test_bind(self):
        i = self.i
        i.bind("go", "cb_test")
        self.assertEqual(i.listeners["go"], {("cb_test", ())})
        i.bind("go", "cb_test", 1, 2, 3, 4, 5)
        self.assertEqual(i.listeners["go"],
                         {("cb_test", ()), ("cb_test", (1, 2, 3, 4, 5))})

    def test_unbind(self):
        i = self.i
        i.bind("go", "cb_test")
        i.bind("go", "cb_test", 1)
        i.bind("go", "cb_test", 1, 2)
        i.bind("go", "cb_test", 1, 2, 3)
        i.bind("go", "cb_test", 1, 2, 3, 4)
        i.bind("go", "cb_test", 1, 2, 3, 4, 5)
        self.assertEqual(len(i.listeners["go"]), 6)
        i.unbind("go", "cb_test", 1, 2, 3, 4, 5)
        i.unbind("go", "cb_test", 1, 2, 3, 4)
        i.unbind("go", "cb_test", 1, 2, 3)
        i.unbind("go", "cb_test", 1, 2)
        i.unbind("go", "cb_test", 1)
        i.unbind("go", "cb_test")
        self.assertEqual(len(i.listeners["go"]), 0)

    def test_bind_repeated(self):
        i = self.i
        for _  in range(100):
            i.bind("go", "cb_test")
        self.assertEqual(i.listeners["go"], {("cb_test", ())})

    def test_unbind_not_exist(self):
        i = self.i
        self.assertEqual(len(i.listeners["go"]), 0)
        for _  in range(100):
            i.unbind("go", "cb_test")
        self.assertEqual(len(i.listeners["go"]), 0)

    def test_send(self):
        i = self.i
        i.send("tick", 1)
        i.send("tick", 2)
        self.assertEqual(i.cache,
                         [
                             ["send", self.i_flag, "tick", 1],
                             ["send", self.i_flag, "tick", 2],
                         ])

    def test_save(self):
        i = self.i
        i.save("foo")
        i.save("bar")
        self.assertEqual(i.cache,
                         [
                             ["save", self.i_flag, "foo", 5],
                             ["save", self.i_flag, "bar", []],
                         ])

    def test_log(self):
        i = self.i
        i.bind("jump", "cb_test")
        i.log("jump")
        self.assertEqual(i.cache, [["log", i.i, "jump", None, 1]])
        self.assertEqual(list(i.logs), [["jump", None, 1]])
        self.assertEqual(i["foo"], 6)   # see function cb_test

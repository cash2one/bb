#!/usr/bin/env python

import collections
import random
import unittest

from bb.i import I, register_log_callback, _cbs

@register_log_callback
def cb_test(extra, i, k, infos, n):
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
        self.assertEqual(i.logs.maxlen, I.MAX_LOGS_DEQUE_LENGTH)
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
        i.bind("go", "cb_test", None)
        self.assertEqual(i.listeners["go"], {("cb_test", None)})
        i.bind("go", "cb_test", (1, 2, 3, 4, 5))
        self.assertEqual(i.listeners["go"],
                         {("cb_test", None), ("cb_test", (1, 2, 3, 4, 5))})

    def test_unbind(self):
        i = self.i
        i.bind("go", "cb_test", None)
        self.assertEqual(len(i.listeners["go"]), 1)
        i.unbind("go", "cb_test", None)
        self.assertEqual(len(i.listeners["go"]), 0)

    def test_bind_repeated(self):
        i = self.i
        for _  in range(100):
            i.bind("go", "cb_test", None)
        self.assertEqual(i.listeners["go"], {("cb_test", None)})

    def test_unbind_not_exist(self):
        i = self.i
        for _  in range(100):
            i.unbind("go", "cb_test", None)
        self.assertEqual(len(i.listeners["go"]), 0)

    def test_send(self):
        i = self.i
        i.send("tick", 1)
        i.send("tick", 2)
        self.assertEqual(i.cache, [])
        i.online = True
        i.send("tick", 1)
        i.send("tick", 2)
        self.assertEqual(i.cache,
                         [
                             [self.i_flag, "tick", 1],
                             [self.i_flag, "tick", 2],
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
        i.bind("jump", "cb_test", None)
        i.log("jump")
        self.assertEqual(i.cache, [["log", i.i, "jump", {}, 1]])
        self.assertEqual(list(i.logs), [["jump", {}, 1]])
        self.assertEqual(i["foo"], 6)   # see function cb_test

    def test_log_infos(self):
        i = self.i
        i.log("jump", {"height": 3}, 5)
        self.assertEqual(i.cache, [["log", i.i, "jump", {"height": 3}, 5]])
        self.assertEqual(list(i.logs), [["jump", {"height": 3}, 5]])

    def test_render(self):
        i = self.i

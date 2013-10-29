#!/usr/bin/env python

import collections
import json
import random
import unittest

from bb.i import I
import rooms

NUM = 100

class TestRooms(unittest.TestCase):
    def setUp(self):
        rooms.room_ids.clear()
        rooms.rooms.clear()
        rooms.slots.clear()
        self.staff = [I(i) for i in range(NUM)]

    def test_enter(self):
        rooms.MAX = 9999
        i1, i2, i3, i4 = self.staff[1:5]

        self.assertEqual(rooms.enter(i1, 1), [[1, 'enter', {1: [0, 0, 1]}]])
        self.assertEqual(rooms.enter(i2, 1), [[2, 'enter', {1: [0, 0, 1], 2: [0, 0, 2]}],
                                              [1, 'enter', {2: [0, 0, 2]}]])
        self.assertEqual(rooms.enter(i3, 2), [[3, 'enter', {3: [0, 0, 3]}]])
        self.assertEqual(rooms.enter(i4, 2), [[4, 'enter', {3: [0, 0, 3], 4: [0, 0, 4]}],
                                              [3, 'enter', {4: [0, 0, 4]}]])
        self.assertEqual(rooms.room_ids, {1: 1, 2: 1, 3: 2, 4: 2})
        self.assertEqual(rooms.rooms[1], {1: [0, 0, 1], 2: [0, 0, 2]})
        self.assertEqual(rooms.rooms[2], {3: [0, 0, 3], 4: [0, 0, 4]})

        # exit room
        self.assertEqual(rooms.enter(i1, 0), [[2, 'enter', {1: None}]])
        self.assertEqual(rooms.room_ids, {2: 1, 3: 2, 4: 2})
        self.assertEqual(rooms.rooms[1], {2: [0, 0, 2]})

        # re-enter same room
        self.assertEqual(rooms.enter(i3, 2), [[4, 'enter', {3: None}],
                                              [3, 'enter', {3: [0, 0, 3], 4: [0, 0, 4]}],
                                              [4, 'enter', {3: [0, 0, 3]}]])
        self.assertEqual(rooms.room_ids, {2: 1, 3: 2, 4: 2})
        self.assertEqual(rooms.rooms[2], {3: [0, 0, 3], 4: [0, 0, 4]})

        # normal enter
        self.assertEqual(rooms.enter(i1, 1), [[1, 'enter', {1: [0, 0, 1], 2: [0, 0, 2]}],
                                              [2, 'enter', {1: [0, 0, 1]}]])
        # 1 exit room1 and enter room2(3 after 4 in room2, see enter(i3, 2) above)
        self.assertEqual(rooms.enter(i1, 2), [[2, 'enter', {1: None}],
                                              [1, 'enter', {1: [0, 0, 1], 3: [0, 0, 3], 4: [0, 0, 4]}],
                                              [4, 'enter', {1: [0, 0, 1]}],
                                              [3, 'enter', {1: [0, 0, 1]}]])
        # change room
        self.assertEqual(rooms.enter(i2, 2), [[2, 'enter', {1: [0, 0, 1], 2: [0, 0, 2], 3: [0, 0, 3], 4: [0, 0, 4]}],
                                              [4, 'enter', {2: [0, 0, 2]}],
                                              [3, 'enter', {2: [0, 0, 2]}],
                                              [1, 'enter', {2: [0, 0, 2]}]])
        self.assertEqual(rooms.room_ids, {1: 2, 2: 2, 3: 2, 4: 2})
        self.assertEqual(rooms.rooms[1], {})
        self.assertEqual(rooms.rooms[2], {1: [0, 0, 1], 2: [0, 0, 2], 3: [0, 0, 3], 4: [0, 0, 4]})

    def test_slots(self):
        n = 20
        room = 1
        rooms.MAX = n

        for i in self.staff:
            rooms.enter(i, room)
        self.assertEqual(len(rooms.slots[room]), rooms.MAX)

        for _, i in zip(range(NUM - n), self.staff):
            rooms.enter(i, 0)
        self.assertEqual(rooms.slots[room], set(range(NUM - n, NUM)))

    def test_move(self):
        n = 5
        rooms.MAX = n
        room = 1
        for i in self.staff:
            rooms.enter(i, room)
        self.assertEqual(len(rooms.move(self.staff[0], [20, 10])), NUM - 1)
        self.assertEqual(len(rooms.move(self.staff[n - 1], [20, 10])), NUM - 1)
        self.assertEqual(len(rooms.move(self.staff[n], [20, 10])), 0)
        

    '''
    def test_basic_attributes(self):
        i = self.i
        self.assertEqual(i.i, self.i_flag)
        self.assertIsInstance(i.cache, list)
        self.assertIsInstance(i.logs, collections.deque)
        self.assertIsInstance(i.listeners, collections.defaultdict)
        self.assertIs(i.listeners.default_factory, set)

    def test_item_attribute_read(self):
        i = self.i
        self.assertEqual(i.foo, 5)

    def test_default_items(self):
        i = self.i
        bar = i["bar"]
        self.assertEqual(bar, [5])
        self.assertIs(bar, i["bar"])

    def test_wrappers(self):
        self.assertGreaterEqual(set(I._defaults), set(I._wrappers))  # :)
        i = self.i
        for k, w in i._wrappers.items():
            v = i[k]
            v2 = w(json.loads(dump1(v)))
            self.assertEqual(v, v2)
            self.assertIs(type(v), type(v2))

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
                             ["save", self.i_flag, "bar", [5]],
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

    def test_render(self): #TODO
        i = self.i

    def test_apply(self): #TODO
        i = self.i

    def test_reward(self): #TODO
        i = self.i
    '''

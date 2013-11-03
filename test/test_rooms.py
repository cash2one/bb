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

        self.assertEqual(rooms.enter(i1, 1), [[1, 'enter', {}]])
        self.assertEqual(rooms.enter(i2, 1), [[2, 'enter', {1: [0, 0, 1]}],
                                              [1, 'enter', {2: [0, 0, 2]}]])
        self.assertEqual(rooms.enter(i3, 2), [[3, 'enter', {}]])
        self.assertEqual(rooms.enter(i4, 2), [[4, 'enter', {3: [0, 0, 3]}],
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
                                              [3, 'enter', {4: [0, 0, 4]}],
                                              [4, 'enter', {3: [0, 0, 3]}]])
        self.assertEqual(rooms.room_ids, {2: 1, 3: 2, 4: 2})
        self.assertEqual(rooms.rooms[2], {3: [0, 0, 3], 4: [0, 0, 4]})

        # normal enter
        self.assertEqual(rooms.enter(i1, 1), [[1, 'enter', {2: [0, 0, 2]}],
                                              [2, 'enter', {1: [0, 0, 1]}]])
        # 1 exit room1 and enter room2(3 after 4 in room2, see enter(i3, 2) above)
        self.assertEqual(rooms.enter(i1, 2), [[2, 'enter', {1: None}],
                                              [1, 'enter', {3: [0, 0, 3], 4: [0, 0, 4]}],
                                              [4, 'enter', {1: [0, 0, 1]}],
                                              [3, 'enter', {1: [0, 0, 1]}]])
        # change room
        self.assertEqual(rooms.enter(i2, 2), [[2, 'enter', {1: [0, 0, 1], 3: [0, 0, 3], 4: [0, 0, 4]}],
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

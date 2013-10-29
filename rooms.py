#!/usr/bin/env python3

import time
import collections

from bb.inst import handle, pre
from bb.i import I, P

room_ids = {}
rooms = collections.defaultdict(collections.OrderedDict)
slots = {}

MAX = 2  # max in a map

@handle
@pre(list, lambda x: len(x) == 2 and all(isinstance(i, int) for i in x))
def move(i, xy):
    id = i.i
    cmd = "move"
    rid = room_ids[id]
    room = rooms[rid]
    p = room[id]
    p[:2] = xy
    if id in slots[rid]:
        _ = {id: xy}
        i.cache.extend([k, cmd, _] for k in room if k != id)
    return i.flush()

@handle
@pre(int)
def enter(i, rid):
    id = i.i
    cmd = "enter"
    if id in room_ids or not rid:
        rid, _rid = room_ids.pop(id), rid
        room = rooms[rid]
        room.pop(id)
        slot = slots[rid]
        if id in slot:
            _slot = set(k for _, k in zip(range(MAX), room.keys()))
            _ = {id: None}
            for k in _slot - slot:  # supplement
                _[k] = room[k]
            i.cache.extend([k, cmd, _] for k in room)
        rid = _rid
    if rid:
        data = i["xy"][:]
        data.append(time.time())  # todo: append more
        room = rooms[rid]
        room[id], room_ids[id], staff, slot = data, rid, {}, set()
        for _, kv in zip(range(MAX), room.items()):
            k, v = kv
            staff[k] = v
            slot.add(k)
        slots[rid] = slot
        i.send(cmd, staff)
        if id in slot:
            _ = {id: data}
            i.cache.extend([k, cmd, _] for k in room if k != id)
    return i.flush()

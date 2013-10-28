#!/usr/bin/env python

import time
import collections

from bb.inst import handle, pre
from bb.i import I, P

room_ids = {}
rooms = collections.defaultdict(collections.OrderedDict)
slots = {}
deaf = set()

MAX = 2  # max in a map

@handle
@pre((list, int, dict))
def exist(i, data):
    id = i.i
    cmd = "exist"
    if isinstance(data, list):
        rid = room_ids[id]
        room = rooms[rid]
        p = room[id]
        p[0], p[1] = data
        if id in slots[rid]:
            _ = {id: data}
            i.cache.extend([k, cmd, _] for k in room if k not in deaf and k != id)
    elif isinstance(data, int):
        if id in room_ids or not data:
            rid = room_ids.pop(id)
            room = rooms[rid]
            room.pop(id)
            if id in slots[rid]:
                slots[rid] = set(k for _, k in zip(range(MAX), room.keys()))
                _ = {id: None}
                i.cache.extend([k, cmd, _] for k in room if k not in deaf)
        if data:
            rid = data
            room = rooms[rid]
            i.send(cmd, dict(kv for _, kv in zip(range(MAX), room.items())))
            room[id] = i["xy"]
            room_ids[id] = rid
            slots[rid] = set(k for _, k in zip(range(MAX), room.keys()))
            if id in slots[rid]:
                _ = {id: data}
                i.cache.extend([k, cmd, _] for k in room if k not in deaf and k != id)
    else:
        pass
    return i.flush()


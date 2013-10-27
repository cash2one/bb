#!/usr/bin/env python

import time
import collections

from bb.inst import handle, pre
from bb.i import I, P

room_idx = {}
rooms = collections.defaultdict(dict)

completion = (0,) * 10

@handle
#@pre((list, dict))
def exist(i, data):
    id = i.i
    cmd = "exist"
    if isinstance(data, list):
        if len(data) == 2:  # update x and y
            room = rooms[room_idx[id]]
            p = room[id]
            p[2], p[3] = data
            _ = {id: data}
            i.cache.extend([k, cmd, _] for k in room if k != id)
        else:  # enter, index0 is room_id
            if id in room_idx:
                room = rooms[room_idx.pop(id)]
                room.pop(id)
                _ = {id: None}
                i.cache.extend([k, cmd, _] for k in room)
            room_id = data[0]
            room = rooms[room_id]
            room[id] = data = [i["foo"], i["level"]] + data[1:]
            room_idx[id] = room_id
            i.send(cmd, room)
            _ = {id: data}
            i.cache.extend([k, cmd, _] for k in room if k != id)
    elif isinstance(data, dict):  # only for update
        room = rooms[room_idx[id]]
        p = room[id]
        for k, v in data.items():
            p[int(k)] = v
        _ = {id: data}
        i.cache.extend([k, cmd, _] for k in room if k != id)
    else:
        room = rooms[room_idx.pop(id)]
        room.pop(id)
        _ = {id: None}
        i.cache.extend([k, cmd, _] for k in room if k != id)
    return i.flush()


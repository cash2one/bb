#!/usr/bin/env python3

from bb.inst import handle, pre
from bb.i import I, P, register_log_callback

@handle
def chat(i, x):
    target, message = x
    if isinstance(target, int):
        t = P[target]
        if t.online:
            t.send("chat", [i.i, message])
        else:
            i.send("chat", [t.i, 1])
        return i.flush(t)
    else:
        return chat_subs[target](i, message)

def chat_team(i, msg):
    pass
def chat_map(i, msg):
    pass
def chat_party(i, msg):
    pass
def chat_world(i, msg):
    pass

chat_subs = {
    "team": chat_team,
    "map": chat_map,
    "party": chat_party,
    "world": chat_world,
}


#!/usr/bin/env python3

_str_to_list = lambda raw: tuple(
    filter(None, map(lambda s: s.strip(), raw.split())))

INSTRUCTIONS_LIST = _str_to_list(
    """
    ping
    online
    enter
    move
    chat
    """)

ATTRIBUTES_LIST = _str_to_list(
    """
    bag
    gold
    """)

_ = INSTRUCTIONS_LIST + ATTRIBUTES_LIST
assert len(_) == len(set(_))
#print(INSTRUCTIONS_LIST)
#print(ATTRIBUTES_LIST)

PING = 0
INST_LEN = len(INSTRUCTIONS_LIST)
ONLINE = PING + INSTRUCTIONS_LIST.index("online")

ATTR = 16  # head id of all attributes

assert PING + INST_LEN < ATTR

STRUCT = "!HH"
NULL = b'null'  # json format
#NULL = b'["online",null]'

DB_HOST = "localhost"
DB_PORT = 6379
IDS = list(range(1, 10))
WORLD = "dummy_world"

DEBUG_OUTPUT = "debug.log"

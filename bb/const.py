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
ONLINE = PING + INSTRUCTIONS_LIST.index("online")
ATTR = 16  # head id of all attributes
assert PING + len(INSTRUCTIONS_LIST) < ATTR

INSTRUCTIONS = dict(zip(INSTRUCTIONS_LIST, range(PING, 2**16)))

for idx, attr in enumerate(ATTRIBUTES_LIST, ATTR):
    INSTRUCTIONS[attr] = idx


STRUCT = "!HH"
NULL = b'null'  # json format
#NULL = b'["online",null]'

DB_HOST = "localhost"
DB_PORT = 6379
IDS = list(range(1, 10))
WORLD = "dummy_world"

DEBUG_OUTPUT = "debug.log"

TIME_FORMAT = "%Y-%m-%d %H:%M:%S"

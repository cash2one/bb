#!/usr/bin/env python3

HEAD_IGNORE = b'\r\n\r\n'
FMT = "!HH"
LEN = 4
NULL = "0"  # for json

INSTRUCTIONS_LIST = [
    "ping",
    "online",
    "enter",
    "move",
]

PING = 0
INST_LEN = len(INSTRUCTIONS_LIST)
ONLINE = PING + INSTRUCTIONS_LIST.index("online")

ATTR = 1001  # head id of all attributes

DB_HOST = "localhost"
DB_PORT = 6379
IDS = list(range(1, 10))
WORLD = "dummy_world"

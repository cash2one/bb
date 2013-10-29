#!/usr/bin/env python3

FMT = "!HH"
LEN = 4
NULL = "0"  # for json

instructions_list = [
    "ping",
    "online",
    "enter",
    "move",
]

PING = 2**8
INST_LEN = len(instructions_list)
ONLINE = PING + instructions_list.index("online")


# everyone could checkout my attributes(in the public_attrs)
public_attrs = {
    "bag",
    "level",
}

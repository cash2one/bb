#!/usr/bin/env python3
#
# seq 1000000 | ./cli.py >in
# (cat in; sleep 10) | nc localhost 2000 >out1
# (cat in; sleep 10) | nc localhost 2000 >out2
# (cat in; sleep 10) | nc localhost 2000 >out3

import json
import struct
import sys

from bb.msg import dump1
from bb.const import INSTRUCTIONS, STRUCT

HEAD = """tgw_l7_forward\r
Host:z.app.twsapp.com\r
1 token\r
\r
"""

if __name__ == "__main__":
    sys.stdout.write(HEAD)
    while True:
        try:
            s = input()
        except (KeyboardInterrupt, EOFError):
            break
        if not s:
            break
        inst, data = (s.split(None, 1) + [None])[:2]
        inst = INSTRUCTIONS[inst]
        data = dump1(eval(data)).encode() if data else b''
        #print(inst, data)
        sys.stdout.buffer.write(
            struct.pack(STRUCT, len(data) + 2, inst) + data)


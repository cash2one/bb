#!/usr/bin/env python3
# seq 1000000 | ./cli.py >in
# (cat in; sleep 10) | nc localhost 2000 >out1
# (cat in; sleep 10) | nc localhost 2000 >out2
# (cat in; sleep 10) | nc localhost 2000 >out3

import sys

if __name__ == "__main__":
    i = True
    while i:
        try:
            i = input()
        except (KeyboardInterrupt, EOFError):
            break
        l = len(i)
        sys.stdout.write(chr(l//256) + chr(l%256) + i)

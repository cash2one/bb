#!/usr/bin/env python3
# (seq 100000; sleep 3) | ./cli.py | nc z 2000 >out

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

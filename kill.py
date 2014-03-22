#!/usr/bin/env python3

if __name__ == "__main__":
    import signal
    import os
    with open("bb.pid") as pidfile:
        os.kill(int(pidfile.read()), signal.SIGTERM)

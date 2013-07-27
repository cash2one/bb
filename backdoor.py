#!/usr/bin/env python

import sys

from code import InteractiveInterpreter
from io import StringIO

from tornado.tcpserver import TCPServer


class BackdoorShell(InteractiveInterpreter):
    """backdoor"""
    def __init__(self):
        InteractiveInterpreter.__init__(self)
        self.buf = []
        self.io = StringIO()

    def push(self, line):
        buf = self.buf
        buf.append(line)
        source = "\n".join(buf)

        more = False
        io = sys.stdout = sys.stderr = self.io
        try:
            more = self.runsource(source)
        finally:
            sys.stdout, sys.stderr = sys.__stdout__, sys.__stderr__

        if not more:
            del buf[:]
        out = io.getvalue()
        io.truncate(0)
        return out


class Connection(object):
    def __init__(self, stream, address):
        self.address = address
        self.shell = BackdoorShell()
        self.stream = stream
        self._read_line()

    def _read_line(self):
        self.stream.read_until(b'\n', self._handle_read)

    def _handle_read(self, line):
        self.stream.write(self.shell.push(line.rstrip().decode()).encode())
        self._read_line()


import weakref
connections = weakref.WeakValueDictionary()

class Backdoor(TCPServer):
    def handle_stream(self, stream, address):
        connections[address] = Connection(stream, address)



if __name__ == "__main__":
    import gc
    gc.disable()
    server = Backdoor()
    server.listen(9527)
    from tornado import ioloop
    def record():
        gc.collect()
        print(list(connections))
    ioloop.PeriodicCallback(record, 1000).start()
    ioloop.IOLoop.instance().start()


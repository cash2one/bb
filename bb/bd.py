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
        out = io.getvalue() + ("... " if more else ">>> ")
        io.truncate(0)
        return out


class Connection(object):
    shell = BackdoorShell()   # global
    def __init__(self, stream, address):
        self.stream = stream
        self.stream.set_close_callback(self.stream.close)
        self.stream.write(b">>> ")
        self.stream.read_until(b'\n', self.handle_input)

    def handle_input(self, line):
        self.stream.write(self.shell.push(line.rstrip().decode()).encode())
        self.stream.read_until(b'\n', self.handle_input)


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
        #gc.collect()
        print(sys.getrefcount(Connection))
    #ioloop.PeriodicCallback(record, 1000).start()
    ioloop.IOLoop.instance().start()


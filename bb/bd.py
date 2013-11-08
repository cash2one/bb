#!/usr/bin/env python3
r"""
>>> bd = BackdoorShell()
>>> bd.push("1 + 6")
'7\n>>> '
>>> bd.push("list(range(5))")
'[0, 1, 2, 3, 4]\n>>> '
"""

import sys

from code import InteractiveInterpreter
from io import StringIO

from tornado.tcpserver import TCPServer


class BackdoorShell(InteractiveInterpreter):
    """backdoor"""
    def __init__(self):
        InteractiveInterpreter.__init__(self)
        self.buf = []

    def push(self, line):
        buf = self.buf
        buf.append(line.rstrip())
        source = "\n".join(buf)

        more = False
        stdout, stderr = sys.stdout, sys.stderr
        io = sys.stdout = sys.stderr = StringIO()
        try:
            more = self.runsource(source)
        finally:
            sys.stdout, sys.stderr = stdout, stderr

        if more:
            prompt = "... " 
        else:
            del buf[:]
            prompt = ">>> " 

        return io.getvalue() + prompt


class Connection(object):
    shell = BackdoorShell()   # global
    def __init__(self, stream, address):
        self.stream = stream
        self.stream.set_close_callback(self.stream.close)
        self.stream.write(b'>>> ')
        self.stream.read_until(b'\n', self.handle_input)

    def handle_input(self, line):
        self.stream.write(self.shell.push(line.decode()).encode())
        self.stream.read_until(b'\n', self.handle_input)


import weakref
connections = weakref.WeakValueDictionary()

class Backdoor(TCPServer):
    def handle_stream(self, stream, address):
        Connection(stream, address)


if __name__ == "__main__":
    import doctest
    doctest.testmod()

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


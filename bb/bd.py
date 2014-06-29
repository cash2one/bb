#!/usr/bin/env python3
r"""
>>> sh = Shell()
>>> sh.push("1 + 6")
'7\n'
>>> sh.push("list(range(5))")
'[0, 1, 2, 3, 4]\n'
>>> sh.push("if True:")
>>> sh.push("    1")
>>> sh.push("    2")
>>> sh.push("    3")
>>> sh.push("")
'1\n2\n3\n'
"""

import sys

from code import InteractiveInterpreter
from io import StringIO


class Shell(InteractiveInterpreter):
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
            return None

        del buf[:]
        return io.getvalue()



if __name__ == "__main__":
    import doctest
    doctest.testmod()

    import gc
    import weakref
    import urllib.parse

    from tornado.ioloop import IOLoop, PeriodicCallback
    from tornado.tcpserver import TCPServer
    from tornado.web import RequestHandler, Application

    gc.disable()

    connections = weakref.WeakValueDictionary()

    MAXLEN = 80 * 25 * 3

    class Connection(object):
        shell = Shell()  # global
        def __init__(self, stream, address):
            stream.set_close_callback(stream.close)
            stream.write(b'>>> ')
            stream.read_until(b'\n', self.handle_input)
            self.stream = stream

        def handle_input(self, line):
            output = self.shell.push(line.decode())
            stream = self.stream
            if output is None:  # more
                stream.write(b'... ')
            else:
                stream.write(output.encode()[:MAXLEN])
                stream.write(b'>>> ')
            stream.read_until(b'\n', self.handle_input)

    class Backdoor(TCPServer):
        def handle_stream(self, stream, address):
            Connection(stream, address)

    class Handler(RequestHandler):
        shell = Shell()  # global
        def get(self):
            cmd = urllib.parse.unquote(self.request.query)
            self.write(self.shell.push(cmd))

    Backdoor().listen(9527)

    Application([
        ("/", Handler),
    ]).listen(8000)

    def record():
        #gc.collect()
        print(sys.getrefcount(Connection))
    #PeriodicCallback(record, 1000).start()

    IOLoop.instance().start()


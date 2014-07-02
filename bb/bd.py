#!/usr/bin/env python3
r"""
>>> sh = Shell()
>>> sh.push("1 + 6")
'7\n'
>>> sh.push("list(range(5))")
'[0, 1, 2, 3, 4]\n'
>>> sh.push("")
''
>>> sh.push("")
''
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

    import collections
    import gc
    import json
    import logging
    import logging.handlers
    import urllib.parse
    import weakref

    from tornado.log import LogFormatter
    from tornado.ioloop import IOLoop, PeriodicCallback
    from tornado.options import parse_command_line
    from tornado.tcpserver import TCPServer
    from tornado.web import RequestHandler, Application

    gc.disable()
    parse_command_line()

    connections = weakref.WeakValueDictionary()

    MAXLEN = 80 * 25 * 3

    log_handler = logging.handlers.TimedRotatingFileHandler('logs/hist', 'D', 1)
    log_handler.setFormatter(LogFormatter(0))
    shell_log = logging.getLogger("shell")
    shell_log.setLevel(logging.INFO)
    shell_log.addHandler(log_handler)
    shell_log.propagate = False

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
                stream.write(output[:MAXLEN].replace("\n", "\r\n").encode())
                stream.write(b'>>> ')
            stream.read_until(b'\n', self.handle_input)

    class Backdoor(TCPServer):
        def handle_stream(self, stream, address):
            Connection(stream, address)

    class Handler(RequestHandler):
        shells = collections.defaultdict(Shell)
        def get(self):
            self.render("index.html")

    class ShellHandler(Handler):
        def get(self, name):
            self.render("shell.html")
        def post(self, name):
            sh = self.shells[name]
            input = urllib.parse.unquote(self.request.body.decode())
            shell_log.info(input)
            output = sh.push(input)
            self.write(json.dumps(output))

    Backdoor().listen(8200)

    Application([
        (r"/(.+)", ShellHandler),
        (r"/", Handler),
    ], static_path="s", template_path="t", debug=1).listen(8100)

    def record():
        #gc.collect()
        print(sys.getrefcount(Connection))
    #PeriodicCallback(record, 1000).start()

    def _deny():
        import sys
        import builtins
        def dummy(*args, **kwargs):
            raise NotImplementedError
        sys.exit = dummy
        builtins.exit = dummy
        builtins.quit = dummy
        builtins.input = dummy
    _deny()

    IOLoop.instance().start()


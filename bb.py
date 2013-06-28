#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

# This is bb server
"""
   /--->Q0--->\
Web            Hub --->Q2---> Log
   \<---Q1<---/

"""


import logging
logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s:%(levelname)s:%(message)s",
                   )

pid_index = 0
def main(port, backstage):
    import gc
    gc.disable()
    import time
    import multiprocessing
    Q0 = multiprocessing.Queue()
    Q1 = multiprocessing.Queue()
    Q2 = multiprocessing.Queue()

    from hub import hub
    from log import log
    hub = multiprocessing.Process(target=hub, args=(Q0, Q1, Q2))
    hub.start()
    log = multiprocessing.Process(target=log, args=(Q2,))
    log.start()


    # main from here
    from struct import pack, unpack
    from tornado import ioloop
    from tornado.tcpserver import TCPServer
    io_loop = ioloop.IOLoop.instance()

    class Connection(object):
        def __init__(self, stream, address, i):
            self.stream = stream
            self.i = i
            logging.info("%s in", self.i)
            self.stream.set_close_callback(self.close)
            #self.stream.read_bytes(1, self.msg_byte)
            #self.stream.read_until(b'\n', self.msg_print)
            self.stream.read_bytes(4, self.msg_head)

        def msg_byte(self, byte):
            print(byte)
            self.stream.write(byte)
            self.stream.read_bytes(1, self.msg_byte)

        def msg_print(self, chunk):
            logging.info(chunk)
            self.stream.read_until(b'\n', self.msg_print)

        def msg_head(self, chunk):
            instruction, length_of_body = unpack(b'!HH', chunk)
            #logging.info("%d, %d", instruction, length_of_body)
            self.instruction = instruction
            if not self.stream.closed():
                self.stream.read_bytes(length_of_body, self.msg_body)

        def msg_body(self, chunk):
            if not chunk:
                chunk = b'0'
            Q0.put([self.i, self.instruction, chunk])
            if not self.stream.closed():
                self.stream.read_bytes(4, self.msg_head)

        def close(self):
            self.stream.close()
            logging.info("%s out", self.i)

    import sys
    import weakref
    staffs = weakref.WeakValueDictionary()


    class BBServer(TCPServer):
        def handle_stream(self, stream, address):
            global pid_index
            pid_index += 1
            staffs[pid_index] = Connection(stream, address, pid_index)

    # SIGTERM
    import signal
    def term(signal_number, stack_frame):
        logging.info("will exit")
        Q0.put(None)
        io_loop.stop()
    signal.signal(signal.SIGTERM, term)

    def msg(fd, event):
        i, cmd, data = Q1.get()
        stream = staffs[i].stream
        if not stream.closed():
            stream.write(data)
    io_loop.add_handler(Q1._reader.fileno(), msg, io_loop.READ)

    server = BBServer()
    server.listen(port)

    # web interface
    from oc import record, recorder
    from tornado import web
    from tornado.template import Template

    ioloop.PeriodicCallback(record, 3000).start()

    template = Template("""
    <table border="1">
    {% for obj, history in sorted(types.items(), key=lambda x: x[1][-1], reverse=True) %}
        <tr>
        <td>{{ obj }}</td> <td>{{ list(history) }}</td>
        </tr>
    {% end %}
    </table>""")

    class MainHandler(web.RequestHandler):
        def get(self):
            self.write(template.generate(types=recorder))
            #gc.collect()

    web.Application([
        (r"/", MainHandler),
    ]).listen(backstage)

    gc.collect()
    io_loop.start()   # looping...

    hub.join()
    log.join()
    logging.debug("all sub-processes are exited")
    logging.debug("before clean Queues: %d, %d, %d",
                  Q0.qsize(), Q1.qsize(), Q2.qsize())
    while not Q0.empty():
        Q0.get()
    while not Q1.empty():
        Q1.get()
    while not Q2.empty():
        Q2.get()
    logging.debug("after clean Queues: %d, %d, %d",
                  Q0.qsize(), Q1.qsize(), Q2.qsize())

    logging.info("bye")



if __name__ == "__main__":
    from tornado.options import define, options, parse_command_line
    define("port", default=8000, type=int, help="main port(TCP)")
    define("backstage", default=8100, type=int, help="backstage port(HTTP)")
    define("leader", default="localhost:80", type=str, help="central controller")
    parse_command_line()

    main(options.port, options.backstage)

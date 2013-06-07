#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import division, print_function, unicode_literals

# This is bb server
"""
   /--->Q0--->\
Web            Hub --->Q2---> Log
   \<---Q1<---/

"""

import gc
import logging
import multiprocessing
import time

try:
    import queue
except ImportError:
    range = xrange
    import Queue as queue


gc.disable()

logging.basicConfig(level=logging.DEBUG,
                    format="%(asctime)s:%(levelname)s:%(message)s",
                   )

def main():
    Q0 = multiprocessing.Queue()
    Q1 = multiprocessing.Queue()
    Q2 = multiprocessing.Queue()

    from hub import hub
    from log import log
    hub = multiprocessing.Process(target=hub, args=(Q0, Q1, Q2))
    hub.start()
    log = multiprocessing.Process(target=log, args=(Q0, Q2))
    log.start()


    # main from here
    from tornado import ioloop
    from tornado.tcpserver import TCPServer
    io_loop = ioloop.IOLoop.instance()

    class Connection(object):
        def __init__(self, stream, address, i):
            self.stream = stream
            self.i = i
            logging.info("%s in", self.i)
            self.stream.set_close_callback(self.close)
            self.stream.read_until(b'\n', self.msg)

        def msg(self, chunk):
            Q0.put((self.i, "ping", chunk if chunk.strip().isdigit() else b'0'))
            self.stream.read_until(b'\n', self.msg)

        def close(self):
            self.stream.close()
            logging.info("%s out", self.i)

    import sys
    import weakref
    staffs = weakref.WeakValueDictionary()

    pid_index = 0

    class BBServer(TCPServer):
        def handle_stream(self, stream, address):
            nonlocal pid_index
            pid_index += 1
            staffs[pid_index] = Connection(stream, address, pid_index)

    # SIGTERM
    import signal
    def term(signal_number, stack_frame):
        logging.info("going to exit")
        Q0.put(None)
        io_loop.stop()
    signal.signal(signal.SIGTERM, term)

    def debug():
        ks = list(staffs.keys())
        print(len(ks), ks, list(map(sys.getrefcount, map(lambda k: staffs[k], ks))))
    #ioloop.PeriodicCallback(debug, 1000).start()

    def msg(fd, event):
        i, cmd, data = Q1.get()
        stream = staffs[i].stream
        if not stream.closed():
            stream.write(bytes(data))
    io_loop.add_handler(Q1._reader.fileno(), msg, io_loop.READ)

    server = BBServer()
    server.listen(8000)

    io_loop.start() # looping...

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
    main()

#!/usr/bin/env python
# This is bb server
"""
   /--->Q0--->\
Web            Hub --->Q2---> Log
   \<---Q1<---/

"""


def main(port, backstage):
    import gc
    gc.disable()

    import logging
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
    import time
    import weakref
    from struct import pack, unpack

    staffs = weakref.WeakValueDictionary()

    from tornado import ioloop
    from tornado.tcpserver import TCPServer
    io_loop = ioloop.IOLoop.instance()

    class Connection(object):
        def __init__(self, stream, address):
            self.stream = stream
            self.address = address
            #self.stream.read_bytes(1, self.msg_byte)
            #self.stream.read_until(b'\n', self.msg_print)
            self.stream.read_until(b'\n', self.login)
            logging.info("%s try in", address)

        def login(self, auth):
            i = int(auth)
            if i in range(10):   # lots todo :)
                self.i = i
                staffs[i] = self
                self.stream.set_close_callback(self.logout)
                self.stream.read_bytes(4, self.msg_head)
                logging.info("%s %s login", self.address, i)
            else:
                logging.info("%s %s auth failed", self.address, i)
                self.stream.close()

        def msg_byte(self, byte):
            print(byte)
            self.stream.write(byte)
            self.stream.read_bytes(1, self.msg_byte)

        def msg_print(self, chunk):
            logging.info(chunk)
            self.stream.read_until(b'\n', self.msg_print)

        def msg_head(self, chunk):
            #logging.info("head: %s", chunk)
            instruction, length_of_body = unpack("!HH", chunk)
            #logging.info("%d, %d", instruction, length_of_body)
            self.instruction = instruction
            if not self.stream.closed():
                self.stream.read_bytes(length_of_body, self.msg_body)

        def msg_body(self, chunk):
            #logging.info("body: %s", chunk)
            if not chunk:
                chunk = b'0'
            Q0.put([self.i, self.instruction, chunk])
            if not self.stream.closed():
                self.stream.read_bytes(4, self.msg_head)

        def logout(self):
            self.stream.close()
            logging.info("%s %s logout", self.address, self.i)


    class BBServer(TCPServer):
        def handle_stream(self, stream, address):
            Connection(stream, address)

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
    <form action="/gc_collect">
        <input type="submit" value="gc.collect()">
    </form>
    staffs: {{ list(staffs.keys()) }}
    <table border="1">
    {% for obj, history in sorted(types.items(), key=lambda x: x[1][-1], reverse=True) %}
        <tr>
        <td>{{ obj }}</td> <td>{{ list(history) }}</td>
        </tr>
    {% end %}
    </table>""")

    class MainHandler(web.RequestHandler):
        def get(self):
            self.write(template.generate(types=recorder, staffs=staffs))

    class GcHandler(web.RequestHandler):
        def get(self):
            gc.collect()
            self.redirect("/")

    web.Application([
        (r"/", MainHandler),
        (r"/gc_collect", GcHandler),
    ]).listen(backstage)

    gc.collect()
    io_loop.start()   # looping...

    hub.join()
    log.join()
    logging.info("all sub-processes are exited")
    logging.info("before clean Queues: %d, %d, %d",
                  Q0.qsize(), Q1.qsize(), Q2.qsize())
    while not Q0.empty():
        Q0.get()
    while not Q1.empty():
        Q1.get()
    while not Q2.empty():
        Q2.get()
    logging.info("after clean Queues: %d, %d, %d",
                  Q0.qsize(), Q1.qsize(), Q2.qsize())

    logging.info("bye")



if __name__ == "__main__":
    from tornado.options import define, options, parse_command_line
    define("port", default=8000, type=int, help="main port(TCP)")
    define("backstage", default=8100, type=int, help="backstage port(HTTP)")
    define("leader", default="localhost:80", type=str, help="central controller")
    parse_command_line()

    main(options.port, options.backstage)

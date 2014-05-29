#!/usr/bin/env python3
# This is bb server
"""
   /--->Q0--->\
Web            Hub --->Q2---> Log
   \<---Q1<---/

"""


def main(options):

    import logging
    from multiprocessing import Process
    from multiprocessing.queues import Queue, SimpleQueue

    if __debug__:
        from queue import Queue, Queue as SimpleQueue
        from threading import Thread, Thread as Process
        from datetime import timedelta
        delay = timedelta(milliseconds=300)

    Q0, Q1, Q2 = Queue(), SimpleQueue(), SimpleQueue()

    put = Q0.put
    get = Q1.get

    from .hub import hub
    from .log import log
    from .dbg import show

    sub_procs = {}

    def start():
        #import bb; print(dir(bb))  # modules have been loaded at here, hub will loads the others
        logging.info("starting sub processes...")
        if any(proc.is_alive() for proc in sub_procs.values()):
            logging.warning("sub processes are running, failed to start")
            return
        sub_procs["hub"] = Process(target=hub, args=(Q0, Q1, Q2))
        sub_procs["log"] = Process(target=log, args=(Q2,))
        for name, proc in sub_procs.items():
            proc.start()
            logging.info("%s started, pid:%d", name, getattr(proc, "pid", 0))
        logging.info("start sub processes success!")

    def stop():
        logging.info("stopping sub processes...")
        if all(proc.is_alive() for proc in sub_procs.values()):
            put(None)
        else:
            logging.warning("sub processes are not running, failed to stop")
        for name, proc in sub_procs.items():
            proc.join()
            logging.info("%s stopped, pid:%d", name, getattr(proc, "pid", 0))
        logging.info("stop sub processes success!")

    start()

    # main from here
    import collections
    import functools
    import signal
    import sys
    import time
    import urllib.parse
    import weakref

    from tornado import ioloop, web, autoreload

    from .conn import tcp, websocket, backdoor
    from .const import TIME_FORMAT, PING, NULL, DEBUG_OUTPUT
    from .oc import record, recorder

    ioloop._Timeout.__repr__ = lambda self: "{} ({})  {}".format(
        time.strftime(TIME_FORMAT, time.localtime(self.deadline)),
        self.deadline,
        self.callback and self.callback.__doc__)

    io_loop = ioloop.IOLoop.instance()

    tokens = {}
    staffs = weakref.WeakValueDictionary()
    hub_todo = collections.deque()


    # SIGTERM
    def _term(signal_number, stack_frame):
        logging.info("will exit")
        io_loop.stop()
        Q1.put(None)
        stop()

    signal.signal(signal.SIGTERM, _term)


    def msg(i, cmd, data):
        if i is None:
            try:
                hub_todo.popleft()(data)
            except StopIteration:
                pass
        else:
            s = staffs.get(i)
            if s:
                s.send(cmd, data) \
                        if not __debug__ else io_loop.add_timeout(delay, functools.partial(s.send, cmd, data))  # this line is for debug
            else:
                logging.warning("{} is not online failed to send {}-{}".format(i, cmd, data))

    if __debug__:
        def loop_msg():
            while True:
                x = get()
                show(x)
                if x is None:
                    break
                io_loop.add_callback(msg, *x)
        Thread(target=loop_msg).start()
    else:
        io_loop.add_handler(Q1._reader.fileno(),
                            lambda _,__: msg(*get()),
                            io_loop.READ)


    if __debug__:
        ioloop.PeriodicCallback(record, 3000).start()
        ioloop.PeriodicCallback(
            lambda: tokens.update(dict.fromkeys(range(100), "token")),
            1000).start()


    def hub_coroutine(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            generator = method(self, *args, **kwargs)
            try:
                cmd, expr = next(generator)
                hub_todo.append(generator.send)
                put([None, cmd, expr])
            except StopIteration:
                pass
        return wrapper


    class BaseHandler(web.RequestHandler):
        @property
        def browser(self):
            return self.request.host[-1].isalpha()

    class MainHandler(BaseHandler):
        def get(self):
            cmd = urllib.parse.unquote(self.request.query)
            result = repr(eval(cmd, None, sys.modules)) if cmd else ""
            self.render("index.html", cmd=cmd, result=result)

    class IOHistoryHandler(BaseHandler):
        def get(self):
            if not __debug__:
                return
            step = 25
            i = self.request.query
            with open(DEBUG_OUTPUT) as f:
                hist = list(f)
            page = int(i) if i.isdigit() else 1
            pages = int((len(hist) - 1) / step) + 1
            history = hist[step * (page - 1) : step * page]
            self.render("history.html", page=page, pages=pages,
                        history=history)

    class StatusHandler(BaseHandler):
        def get(self):
            if not __debug__:
                return
            self.render("status.html", recorder=recorder)

    class TokenUpdateHandler(BaseHandler):
        def get(self):
            """
            /token?10001.key
            """
            i, t = self.request.query.split(".", 1)
            tokens[int(i)] = t

    class HubHandler(BaseHandler):
        @hub_coroutine
        @web.asynchronous
        def get(self, cmd):
            """
            /hub_eval?
            /hub_show?
            """
            expr = urllib.parse.unquote(self.request.query)
            if cmd == "eval":
                self.set_header("Content-Type", "application/json")
                self.finish((yield cmd, expr))
            elif cmd == "show":
                echo = yield cmd, expr
                if isinstance(echo, str) and echo.startswith("Traceback"):
                    self.set_header("Content-Type", "text/plain")
                    self.finish(echo)
                else:
                    self.render("show.html", echo=echo)
            elif cmd == "reset":
                hub_todo.clear()
                stop()
                start()
                self.finish(cmd)
            else:
                raise web.HTTPError(404)



    tcp(staffs, tokens, put)().listen(options.port)
    backdoor(hub_coroutine)().listen(options.backdoor)#, "localhost")

    autoreload.add_reload_hook(stop)  # i like autoreload now :)

    web.Application(
        [
            (r"/", MainHandler),
            (r"/io", IOHistoryHandler),
            (r"/status", StatusHandler),
            (r"/hub_(.*)", HubHandler),
            (r"/token", TokenUpdateHandler),
        ],
        static_path="static",
        template_path="templates",
        debug=__debug__,
        ).listen(options.backstage)

    try:
        io_loop.start()   # looping...
    except KeyboardInterrupt:
        Q1.put(None)
        stop()

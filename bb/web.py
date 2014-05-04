#!/usr/bin/env python3
# This is bb server
"""
   /--->Q0--->\
Web            Hub --->Q2---> Log
   \<---Q1<---/

"""

from bb import opt

def main(options=opt):

    import logging
    from multiprocessing import Process
    from multiprocessing.queues import Queue, SimpleQueue

    if __debug__:
        from queue import Queue, Queue as SimpleQueue
        from threading import Thread as Process
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
    import sys
    import time
    import weakref
    import functools

    staffs = weakref.WeakValueDictionary()

    from tornado import ioloop
    from .const import TIME_FORMAT

    ioloop._Timeout.__repr__ = lambda self: "{} ({})  {}".format(
        time.strftime(TIME_FORMAT, time.localtime(self.deadline)),
        self.deadline,
        self.callback and self.callback.__doc__)

    io_loop = ioloop.IOLoop.instance()

    tokens = {}


    # SIGTERM
    import signal
    def term(signal_number, stack_frame):
        logging.info("will exit")
        io_loop.stop()
        Q1.put(None)
        stop()
    signal.signal(signal.SIGTERM, term)


    def msg(i, cmd, data):
        if i is None:
            hub_todo.popleft()(data)
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
        Process(target=loop_msg, args=()).start()
    else:
        io_loop.add_handler(Q1._reader.fileno(),
                            lambda _,__: msg(*get()),
                            io_loop.READ)


    from urllib.parse import unquote
    from tornado.web import RequestHandler, Application, HTTPError, asynchronous
    from .const import PING, NULL, DEBUG_OUTPUT

    if __debug__:
        from .oc import record, recorder
        ioloop.PeriodicCallback(record, 3000).start()
        ioloop.PeriodicCallback(
            lambda: tokens.update(dict.fromkeys(range(100), "token")),
            1000).start()

    class BaseHandler(RequestHandler):
        @property
        def browser(self):
            return self.request.host[-1].isalpha()

        def get(self):
            """dummy"""

    import collections
    hub_todo = collections.deque()


    class MainHandler(BaseHandler):
        def get(self):
            """
            """
            cmd = unquote(self.request.query)
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
            /token?1.key
            """
            i, t = self.request.query.split(".", 1)
            tokens[int(i)] = t
            logging.info("token_generation_1: %s, %r", i, t)

        def post(self):
            i, t = self.request.query.split(".", 1)
            tokens[int(i)] = t
            put([None, "update", [int(i), self.request.body.decode()]])
            logging.info("token_generation_2: %s, %r", i, t)

    def to_hub(method):
        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            todo = method(self, *args, **kwargs)
            if todo:
                cmd, expr, callback = todo
                hub_todo.append(callback)
                put([None, cmd, expr])
        return wrapper

    class HubHandler(BaseHandler):
        @to_hub
        @asynchronous
        def get(self, cmd):
            """
            /hub_eval?
            /hub_show?
            """
            expr = unquote(self.request.query)
            callback = None
            if cmd == "eval":
                self.set_header("Content-Type", "application/json")
                callback = self.finish
            elif cmd == "show":
                callback = self.deal_echoed
            elif cmd == "reset":
                hub_todo.clear()
                stop()
                start()
                return self.finish(cmd)
            else:
                raise HTTPError(404)
            return cmd, expr, callback

        def deal_echoed(self, echo):
            if isinstance(echo, str) and echo.startswith("Traceback"):
                self.set_header("Content-Type", "text/plain")
                self.finish(echo)
            else:
                self.render("show.html", echo=echo)

    class FlushHubHandler(BaseHandler):
        def get(self):
            """flush all in P, proxy via P[0]
            /flush
            /flush?3
            """
            i = self.request.query
            put([int(i) if i.isdigit() else 0, PING, NULL])

    class DummyIHandler(BaseHandler):
        def get(self, i):
            cmd, msg = unquote(self.request.query).split(".", 1)
            put([int(i), int(cmd), msg])

    from .conn import tcp, websocket, backdoor

    tcp(staffs, tokens, put)().listen(options.port)
    backdoor(to_hub)().listen(options.backdoor)#, "localhost")

    from tornado import autoreload
    autoreload.add_reload_hook(stop)  # i like autoreload now :)

    Application(
        [
            (r"/dummy", BaseHandler),
            (r"/", MainHandler),
            (r"/token", TokenUpdateHandler),
            (r"/flush", FlushHubHandler),
            (r"/ws", websocket(staffs, tokens, put)),
            (r"/io", IOHistoryHandler),
            (r"/status", StatusHandler),
            (r"/hub_(.*)", HubHandler),
            (r"/(\d+)", DummyIHandler),
        ],
        static_path="static",
        template_path="tpl",
        debug=__debug__,
        ).listen(options.backstage)

    try:
        io_loop.start()   # looping...
    except KeyboardInterrupt:
        Q1.put(None)
        stop()

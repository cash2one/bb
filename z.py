#!/usr/bin/env python3

import time
import functools
import itertools

import tornado.ioloop
import tornado.web

from tornado.util import ObjectDict
from tornado.httpclient import AsyncHTTPClient

group = {}
broken = {}

def check(i, response):
    #print(response)
    if response.error:
        if i in group:
            broken[i] = group.pop(i)
    else:
        if i in broken:  # resume if revive
            orphan = broken.pop(i)
            if i not in group:
                group[i] = orphan


def poll():
    print(group)
    print(broken)
    for k, v in itertools.chain(group.items(), broken.items()):
        AsyncHTTPClient().fetch("http://%s:%d/dummy" % (v.ip, v.ports[1]),
                                functools.partial(check, k),
                                connect_timeout=2, request_timeout=1)

tornado.ioloop.PeriodicCallback(poll, 100).start()

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(group)

class SonHandler(tornado.web.RequestHandler):
    """log todo"""
    def get(self, i):
        print(self.request.remote_ip)
        print(self.request.arguments)
        i = int(i)
        # register
        if i not in group:
            run = self.get_argument("run", None)
            if run:
                group[i] = ObjectDict(
                    run=run,
                    ip=self.request.remote_ip,
                    ports=tuple(map(int, self.get_arguments("ports"))),
                )
                self.write(group[i])
            else:
                raise tornado.web.HTTPError(402)
        # quit
        else:
            quit = self.get_argument("quit", None)
            if quit in (group[i].run, "force"):
                self.write(group.pop(i))
            else:
                raise tornado.web.HTTPError(409)

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/([0-9]+)", SonHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

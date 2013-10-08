#!/usr/bin/env python3

import collections
import functools
import logging
import itertools
import time

import tornado.ioloop
import tornado.options
import tornado.web

from tornado.util import ObjectDict
from tornado.httpclient import AsyncHTTPClient

hosts = {
    "127.0.0.1": "f1",
    "192.168.25.252": "f2",
}

all_zones = {}
servers = {}
broken = collections.Counter()
LIMIT_BROKEN = 1

tornado.options.parse_command_line()


def check(zones, response):
    logging.debug(zones)
    logging.debug(response)
    error = response.error
    if error:
        logging.warning(error)
        broken[zones] += 1
        if broken[zones] > LIMIT_BROKEN:
            broken[zones] = [
                error,
                servers.pop(zones),
                [all_zones.pop(i) and i for i in zones],
            ]
    else:
        broken.pop(zones, None)

def poll():
    logging.debug(all_zones)
    logging.debug(servers)
    logging.debug(broken)
    for k, v in servers.items():
        AsyncHTTPClient().fetch("http://%s:%d/dummy" % (v.ip, v.ports[1]),
                                functools.partial(check, k),
                                connect_timeout=0.5, request_timeout=0.5)

tornado.ioloop.PeriodicCallback(poll, 2000).start()

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(str(servers))

class RegHandler(tornado.web.RequestHandler):
    def get(self):
        logging.debug(self.request.remote_ip)
        logging.debug(self.request.arguments)
        zones = frozenset(map(int, self.get_arguments("zones")))
        if zones not in servers and not zones & frozenset(all_zones):
            ip = self.request.remote_ip
            ports = tuple(map(int, self.get_arguments("ports")))
            for i in zones:
                all_zones[i] = (hosts[ip], ports[0])
            s = ObjectDict(
                start=self.get_argument("start"),
                ip=ip,
                ports=ports,
            )
            servers[zones] = s
            self.write(s)
        else:
            raise tornado.web.HTTPError(409)

class QuitHandler(tornado.web.RequestHandler):
    def get(self):
        zones = frozenset(map(int, self.get_arguments("zones")))
        if zones in servers:
            servers.pop(zones)
            for i in zones:
                all_zones.pop(i)
        else:
            raise tornado.web.HTTPError(410)


application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/reg", RegHandler),
    (r"/quit", QuitHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

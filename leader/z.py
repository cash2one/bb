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

from bb import bd

all_zones = {}
servers = {}
broken = collections.Counter()
errors = {}
LIMIT_BROKEN = 1

tornado.options.parse_command_line()

entries = {}
domains = {}
lan_wan = {}

def init():
    from configparser import ConfigParser
    config = ConfigParser()
    config.read("config")
    entries.clear()
    domains.clear()
    lan_wan.clear()
    lan_wan.update(config["lan_wan"])
    for i, host_port in config["entries"].items():
        i = int(i)
        host, port = host_port.split(":")
        port = int(port)
        domains.setdefault((host, port), set()).add(i)

    print(entries)
    print(domains)
    print(lan_wan)


init()

def check(zones, response):
    logging.debug(zones)
    logging.debug(response)
    error = response.error
    if error:
        logging.warning(error)
        broken[zones] += 1
        if broken[zones] > LIMIT_BROKEN:
            errors[zones] = [
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
    logging.debug(errors)
    for k, v in servers.items():
        AsyncHTTPClient().fetch("http://%s:%d/dummy" % (v.ip, v.ports[1]),
                                functools.partial(check, k),
                                connect_timeout=0.5, request_timeout=0.5)

#tornado.ioloop.PeriodicCallback(poll, 2000).start()

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html",
                    all_zones=all_zones,
                    servers=servers,
                    broken=broken,
                    errors=errors)

class RegHandler(tornado.web.RequestHandler):
    def get(self):
        logging.debug(self.request.remote_ip)
        logging.debug(self.request.arguments)
        host, port = (self.request.remote_ip, int(self.get_argument("port")))
        domain = domains[(host, port)]
        ids = []
        for i in domain:
            ids.extend([i])#dummy todo: read ids
            entries[i] = (lan_wan.get(host, host), port)
        self.write({
            "WORLD": "_".join(map(str, sorted(domain))),
            "IDS": ids,
            "DB_HOST": "box",
        })

class QuitHandler(tornado.web.RequestHandler):
    def get(self):
        pass


application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/reg", RegHandler),
    (r"/quit", QuitHandler),
])

"""
backdoor = bd.Backdoor()
push = bd.Connection.shell.push
push("import __main__ as main")
push("from __main__ import all_zones, servers, broken, errors")
"""

if __name__ == "__main__":
    application.listen(65535)
    #backdoor.listen(65534)
    tornado.ioloop.IOLoop.instance().start()

#!/usr/bin/env python3

import collections
import json
import logging
import os
import re
import time

import tornado.ioloop
import tornado.web

from tornado.httpclient import AsyncHTTPClient
from tencent import mk_url

match = re.compile(r"^[0-9A-F]{32}$").match  # pattern of openid

REQUIRED = ("openid", "openkey", "pf", "pfkey")
ROLES = frozenset(range(1, 7))

IDX = {}
FS = {}
BEGINNERS = collections.defaultdict(set)
NAMES = collections.defaultdict(set)

def load_idx(d):
    for i in os.listdir(d):
        if i.isdigit():
            i, fn = int(i), "{}/{}".format(d, i)
            with open(fn) as f:
                IDX[i] = {k: int(v) for k, v in (s.split() for s in f)}
            FS[i] = open(fn, "a", 1)
    IDX["i"] = max(max(i.values()) for i in IDX.values() if i) + 1


class MainHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self):
        _ = self.get_arguments("_")
        if len(_) != 4:
            kwargs = {k: v[0].decode()
                      for k, v in self.request.arguments.items()}
            if all(kwargs.get(k) for k in REQUIRED) and match(kwargs["openid"]):
                self.kwargs = kwargs
                url = mk_url(kwargs, "v3/user/get_info")
                AsyncHTTPClient().fetch(url, self.on_response)
            else:
                self.finish("url arguments error")
        else:
            serverid, openid, role, name = int(_[0]), _[1], int(_[2]), _[3]
            if role in ROLES and 0 < len(name) < 8:
                if name in NAMES[serverid]:
                    self.new_one(serverid, openid, name)
                else:
                    BEGINNERS[serverid].remove(openid)
                    NAMES[serverid].add(name)
                    i = IDX["i"]
                    IDX["i"] += 1
                    IDX[serverid][openid] = i
                    FS[serverid].write("{} {}\n".format(openid, i))
                    AsyncHTTPClient().fetch("http://localhost:8000/begin")
                    self.login(i)
            else:
                self.finish("create error, try again")

    def on_response(self, response):
        if response.error:
            logging.warning(response)
            raise tornado.web.HTTPError(500)
        print(json.loads(response.body.decode()))
        print(self.kwargs)
        serverid, openid = int(self.kwargs["serverid"]), self.kwargs["openid"]
        i = IDX[serverid].get(openid)
        if i:
            self.login(i)
        else:  # create new one
            BEGINNERS[serverid].add(openid)
            self.new_one(serverid, openid)

    def new_one(self, serverid, openid, error=""):
        self.finish("{} - {} {}".format(serverid, openid, error))

    def login(self, i):
        AsyncHTTPClient().fetch("http://localhost:8000/t")
        self.finish(str(i))



application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    import tornado.options
    tornado.options.parse_command_line()
    logging.error(__name__)
    load_idx("idx")
    application.listen(1024)
    tornado.ioloop.IOLoop.instance().start()

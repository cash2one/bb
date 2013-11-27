#!/usr/bin/env python3

import collections
import json
import logging
import os
import re
import time

import tornado.gen
import tornado.ioloop
import tornado.web

from tornado.httpclient import AsyncHTTPClient
from tencent import mk_url

match = re.compile(r"^[0-9A-F]{32}$").match  # pattern of openid

REQUIRED = ("openid", "openkey", "pf", "pfkey")
ROLES = frozenset(range(1, 7))

ID = 0
IDX = {}
FS = {}
BEGINNERS = {}
NAMES = {}

def load_idx(d):
    for i in os.listdir(d):
        if i.isdigit():
            i, fn = int(i), "{}/{}".format(d, i)
            with open(fn) as f:
                IDX[i] = {k: int(v) for k, v in (s.split() for s in f)}
            FS[i] = open(fn, "a", 1)
            BEGINNERS[i] = set()
            NAMES[i] = {} # todo: read all names
    global ID
    ID = max(max(i.values()) for i in IDX.values() if i) + 1


a = AsyncHTTPClient()
class MainHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        _ = self.get_arguments("_")
        if len(_) == 4:
            serverid, openid, role, name = int(_[0]), _[1], int(_[2]), _[3]
            if role in ROLES and 0 < len(name) < 8:
                if name in NAMES[serverid]:
                    self.write("{} - {} {} exist".format(serverid, openid, name))
                else:
                    BEGINNERS[serverid].remove(openid)
                    global ID
                    ID += 1
                    responses = yield [a.fetch("http://localhost:8000/begin"),
                                       a.fetch("http://localhost:8000/t")]
                    if any(i.error for i in responses):
                        logging.warning(responses)
                        raise tornado.web.HTTPError(500)
                    FS[serverid].write("{} {}\n".format(openid, ID))
                    IDX[serverid][openid] = ID
                    NAMES[serverid][name] = openid
                    self.write(str(ID))
            else:
                self.write("create error, try again")
        else:
            kwargs = {k: v[0].decode()
                      for k, v in self.request.arguments.items()}
            if all(kwargs.get(k) for k in REQUIRED) and match(kwargs["openid"]):
                response = yield a.fetch(mk_url(kwargs, "/v3/user/get_info"))
                if response.error:
                    logging.warning(response)
                    raise tornado.web.HTTPError(500)
                self.write(response.body)
                serverid, openid = int(kwargs["serverid"]), kwargs["openid"]
                i = IDX[serverid].get(openid)
                if i is not None:
                    response = yield a.fetch("http://localhost:8000/t")
                    if response.error:
                        logging.warning(response)
                        raise tornado.web.HTTPError(500)
                    self.write(str(i))
                else:
                    BEGINNERS[serverid].add(openid)
                    self.write("reg plz {} - {}".format(serverid, openid))
            else:
                self.write("url arguments error")


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

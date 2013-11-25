#!/usr/bin/env python3

import collections
import json
import logging
import re
import time

import tornado.ioloop
import tornado.web
import tornado.options

from tornado.httpclient import AsyncHTTPClient
from redis import StrictRedis
from tencent import mk_url


match = re.compile(r"^[0-9A-F]{32}$").match  # pattern of openid
required = ["openid", "openkey", "pf", "pfkey"]
roles = set(map(str, range(1, 7)))

tornado.options.parse_command_line()

beginners = collections.defaultdict(set)
names = collections.defaultdict(set)

class MainHandler(tornado.web.RequestHandler):

    redis = StrictRedis(decode_responses=True)

    @tornado.web.asynchronous
    def get(self):
        _ = self.get_arguments("_")
        if len(_) != 4:
            kwargs = {k: v[0].decode()
                      for k, v in self.request.arguments.items()}
            if all(kwargs.get(k) for k in required) and match(kwargs["openid"]):
                self.kwargs = kwargs
                url = mk_url(kwargs, "v3/user/get_info")
                AsyncHTTPClient().fetch(url, self.on_response)
            else:
                self.finish("url arguments error")
        else:
            serverid, openid, role, name = _
            if role in roles and 0 < len(name) < 8:
                if name in names[serverid]:
                    self.new_one(serverid, openid, name)
                else:
                    beginners[serverid].remove(openid)
                    names[serverid].add(name)
                    r = self.redis
                    i = r.incr("i")
                    r.hset(serverid, openid, i)
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
        serverid, openid = self.kwargs["serverid"], self.kwargs["openid"]
        r = self.redis
        i = r.hget(serverid, openid)
        if i:
            self.login(i)
        else:  # create new one
            beginners[serverid].add(openid)
            self.new_one(serverid, openid)

    def new_one(self, serverid, openid, error=""):
        self.finish("%s - %s %s" % (serverid, openid, error))

    def login(self, i):
        AsyncHTTPClient().fetch("http://localhost:8000/t")
        self.finish(str(i))



application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    application.listen(1024)
    tornado.ioloop.IOLoop.instance().start()

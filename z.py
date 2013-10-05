#!/usr/bin/env python3

import time

import tornado.ioloop
import tornado.web

keys = ["port", "backstage", "backdoor"]

db = {
    1: [8000, 8100, 8200, None],
    2: [8000, 8100, 8200, None],
}

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write(db)

class SonHandler(tornado.web.RequestHandler):
    def get(self, i):
        i = db[int(i)]
        if i[-1] is None:
            i[-1] = self.get_argument("run")
            self.write(dict(zip(keys, i)))
        elif self.get_argument("quit") in (i[-1], "force"):
            i[-1] = None
            self.write("quit")

application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/([0-9]+)", SonHandler),
])

if __name__ == "__main__":
    application.listen(8888)
    tornado.ioloop.IOLoop.instance().start()

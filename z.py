#!/usr/bin/env python3

import time

import tornado.ioloop
import tornado.web

group = {
}

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
                group[i] = {
                    "run": run,
                    "ip": self.request.remote_ip,
                    "ports": tuple(self.get_arguments("ports")),
                }
                self.write(group[i])
            else:
                raise tornado.web.HTTPError(402)
        # quit
        else:
            quit = self.get_argument("quit", None)
            if quit in (group[i]["run"], "force"):
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

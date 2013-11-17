#!/usr/bin/env python3

import logging
import re

import tornado.httpclient
import tornado.ioloop
import tornado.web
import tornado.options

from tencent import mk_url

openid_pattern = re.compile(r"^[0-9A-F]{32}$")

class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        http = tornado.httpclient.AsyncHTTPClient()
        args = {k: v[0].decode() for k, v in self.request.arguments.items()}
        if args.get("pf") and \
           args.get("openkey") and \
           openid_pattern.match(args.get("openid", "")):
            url = mk_url(args, "v3/user/get_info")
            http.fetch(url, self.on_response)
        else:
            self.finish()

    def on_response(self, response):
        if response.error:
            logging.warning(response)
            raise tornado.web.HTTPError(500)
        print(response.body.decode())
        self.finish()

application = tornado.web.Application([
    (r"/", MainHandler),
])

if __name__ == "__main__":
    application.listen(1024)
    tornado.ioloop.IOLoop.instance().start()

#!/usr/bin/env python3

import tornado.web

class PyObjAttr(tornado.web.UIModule):
    def render(self, **kwargs):
        return self.render_string("modules/py_obj_attr.html", **kwargs)

    def javascript_files(self):
        return ["show.js"]

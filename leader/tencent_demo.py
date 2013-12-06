#!/usr/bin/env python3

import collections
import functools
import itertools
import json
import logging
import os
import random
import re
import time

import tornado.gen
import tornado.ioloop
import tornado.web
import tornado.httpclient

from urllib.parse import urlencode
from tencent import mk_url

REQUIRED = ("openid", "openkey", "pf", "pfkey")
ROLES = frozenset(range(1, 7))

ALIASES = {}  # serverid -> zoneid
DOMAINS = {}  # host:port(lan) -> zones
LAN_WAN = {}  # lan -> wan
WAN_LAN = {}  # wan -> lan
ENTRIES = {}  # zoneid -> host:port(wan)
BACKSTAGES = {}  # zoneid -> host:port(backstage)

ID = 0
IDX = {}
FS = {}
BEGINNERS = {}
NAMES = {}

match = re.compile(r"^[0-9A-F]{32}$").match  # pattern of openid
token_fmt = "{}.{}".format
token_url_fmt = "http://{}/token?{}".format
http = tornado.httpclient.AsyncHTTPClient()

def init():
    ALIASES.clear()
    DOMAINS.clear()
    LAN_WAN.clear()
    WAN_LAN.clear()
    ENTRIES.clear()

    from configparser import ConfigParser
    config = ConfigParser()
    config.read("config")

    ALIASES.update((int(k), int(v))
                   for k, v in config["serverid_zoneid"].items())
    for k, v in config["lan_wan"].items():
        LAN_WAN[k] = v
        WAN_LAN[v] = k

    for i, host_port in config["entries"].items():
        i = int(i)
        host, port = host_port.split(":")
        port = int(port)
        ENTRIES[i] = "{}:{}".format(LAN_WAN[host], port)
        DOMAINS.setdefault(host_port, set()).add(i)

    ###########################################################
    idx_dir = "idx"
    for i in os.listdir(idx_dir):
        if i.isdigit():
            i, fn = int(i), os.path.join(idx_dir, i)
            with open(fn) as f:
                IDX[i] = {k: int(v) for k, v in (s.split()[:2] for s in f)}
            FS[i] = open(fn, "a", 1)
            BEGINNERS[i] = set()
            NAMES[i] = {} # todo: read all names
    global ID
    ID = max(max(i.values()) for i in IDX.values() if i)



class MainHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        _ = self.get_arguments("_")
        if len(_) == 4:
            zoneid = int(_[0])
            openid = _[1]
            role = int(_[2])
            name = _[3].strip()
            if role in ROLES and 0 < len(name) < 8:
                if name in NAMES[zoneid]:
                    self.write("{} - {} {} exist".format(zoneid, openid, name))
                else:
                    BEGINNERS[zoneid].remove(openid)
                    global ID
                    ID += 1
                    response = yield http.fetch(
                        token_url_fmt(BACKSTAGES[zoneid], ID),
                        "POST",
                        json.dumps({
                            "name": name,
                            "role": role,
                        }),
                        )
                    if response.error:
                        logging.warning(response)
                        raise tornado.web.HTTPError(500)
                    token = random.randrange(1000)
                    response = yield http.fetch(
                        token_url_fmt(BACKSTAGES[zoneid], token_fmt(ID, token))
                        )
                    if response.error:
                        logging.warning(response)
                        raise tornado.web.HTTPError(500)
                    FS[zoneid].write(
                        "{} {} {} {} {}\n".format(
                            openid,
                            ID,
                            time.strftime("%Y-%m-%d %H:%M:%S"),
                            name,
                            role,
                            )
                        )
                    IDX[zoneid][openid] = ID
                    NAMES[zoneid][name] = openid
                    self.write(token_fmt(ID, token))
            else:
                self.write("create error, try again")
        else:
            kwargs = {k: self.get_argument(k) for k in self.request.arguments}
            if all(kwargs.get(k) for k in REQUIRED) and match(kwargs["openid"]):
                response = yield http.fetch(mk_url(kwargs, "/v3/user/get_info"))
                if response.error:
                    raise tornado.web.HTTPError(500)
                response = json.loads(response.body.decode())
                if response["ret"]:
                    raise tornado.web.HTTPError(400, reason=response["msg"])
                serverid, openid = int(kwargs["serverid"]), kwargs["openid"]
                zoneid = ALIASES[serverid]
                i = IDX[zoneid].get(openid)
                if i is not None:
                    token = random.randrange(1000)
                    response = yield http.fetch(
                        token_url_fmt(BACKSTAGES[zoneid], token_fmt(ID, token))
                        )
                    if response.error:
                        logging.warning(response)
                        raise tornado.web.HTTPError(500)
                    self.write(str(i))
                else:
                    BEGINNERS[zoneid].add(openid)
                    self.write("reg plz {} - {}".format(zoneid, openid))
            else:
                self.write("url arguments error")


class RegHandler(tornado.web.RequestHandler):
    def get(self):
        logging.debug(self.request.remote_ip)
        logging.debug(self.request.arguments)
        remote_ip = self.request.remote_ip
        kwargs = {k: self.get_argument(k) for k in self.request.arguments}
        hp = "{}:{}".format
        domain = hp(remote_ip, kwargs["port"])
        zs = DOMAINS[domain]
        ids_in_world = []
        for i in zs:
            BACKSTAGES[i] = hp(remote_ip, kwargs["backstage"])
            ids_in_world.extend(IDX[i].values())
        self.write({
            "WORLD": "z_" + "_".join(map(str, sorted(zs))),
            "IDS": ids_in_world,
            "HEAD_IGNORE": "",
            #"DB_HOST": "box",
        })

class QuitHandler(tornado.web.RequestHandler):
    def get(self):
        print("ALIASES", ALIASES)
        print("DOMAINS", DOMAINS)
        print("LAN_WAN", LAN_WAN)
        print("WAN_LAN", WAN_LAN)
        print("ENTRIES", ENTRIES)
        print("BACKSTAGES", BACKSTAGES)
        print("ID", ID)
        print("IDX", IDX)
        print("FS", FS)
        print("BEGINNERS", BEGINNERS)
        print("NAMES", NAMES)


application = tornado.web.Application([
    (r"/", MainHandler),
    (r"/reg", RegHandler),
    (r"/quit", QuitHandler),
])

if __name__ == "__main__":
    import tornado.options
    tornado.options.parse_command_line()
    from bb import bd
    bd.Connection.shell.push("import __main__ as m")
    bd.Backdoor().listen(65534)
    init()
    print("ALIASES", ALIASES)
    print("DOMAINS", DOMAINS)
    print("LAN_WAN", LAN_WAN)
    print("WAN_LAN", WAN_LAN)
    print("ENTRIES", ENTRIES)
    print("BACKSTAGES", BACKSTAGES)
    print("ID", ID)
    print("IDX", IDX)
    print("FS", FS)
    print("BEGINNERS", BEGINNERS)
    print("NAMES", NAMES)
    application.listen(65535)
    tornado.ioloop.IOLoop.instance().start()

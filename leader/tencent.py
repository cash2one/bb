#!/usr/bin/env python3


appid = 100689513
appkey = "3bbd56d30cdf04721ad318d1b15fb307"

host = "http://openapi.tencentyun.com"


import functools
import urllib.parse

from base64 import b64encode
from hashlib import sha1
from hmac import new

appkey = (appkey + "&").encode()
quote = functools.partial(urllib.parse.quote, safe="")

def mk_src(method, path, kw):
    return "%s&%s&%s" % (
        method,
        quote(path),
        quote("&".join("%s=%s" % kv for kv in sorted(kw.items()))),
    )

def mk_sig(src):
    return b64encode(
        new(appkey, src.encode(), sha1).digest()
        ).decode()

def mk_url(kw, api_name, method="GET"):
    kw["appid"] = appid
    kw["sig"] = mk_sig(mk_src(method, "/" + api_name, kw))
    return "%s/%s?%s" % (host, api_name, urllib.parse.urlencode(kw))


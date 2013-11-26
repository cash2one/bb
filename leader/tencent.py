#!/usr/bin/env python3


appid = 100689513
appkey = "3bbd56d30cdf04721ad318d1b15fb307"
appid = 100673142
appkey = "83c7c99e035c22c627b2cc7b5f25fd5b"

host = "http://openapi.tencentyun.com"
host = "http://119.147.19.43"


import functools

from base64 import b64encode
from hashlib import sha1
from hmac import new
from urllib.parse import quote, urlencode

appkey = (appkey + "&").encode()
quote = functools.partial(quote, safe="")

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

def mk_url(kw, api_name, method="GET", keys=None):
    kw = {k: kw[k] for k in keys} if keys else kw.copy()
    kw["appid"] = appid
    kw["sig"] = mk_sig(mk_src(method, "/" + api_name, kw))
    return "%s/%s?%s" % (host, api_name, urlencode(kw))


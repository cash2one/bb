#!/usr/bin/env python3

dummy_send = lambda x: print(x)

def http():
    """TODO"""

def websocket(staffs, tokens, send=dummy_send):
    import logging

    from tornado.websocket import WebSocketHandler

    from bb.const import NULL, ONLINE

    class WebSocket(WebSocketHandler):
        def open(self):
            print(id(self))

        def on_close(self):
            i = self.i
            send([i, ONLINE, NULL])
            staffs.pop(i, i)  # :(
            logging.info("%s %s logout", "ws", i)

        def on_message(self, message):
            logging.debug("ws message: %r", message)
            i, msg = message.split(None, 1)
            i = int(i)
            try:
                send([self.i, i, msg or NULL])
            except AttributeError:  # if has no attribute `i`, login it
                self.login(i, msg)

        def login(self, i, k):
            assert isinstance(i, int), i
            assert isinstance(k, str), k
            try:
                t = tokens.pop(i)
                if k != t:
                    raise Warning("token error: {!r} != {!r}".format(k, t))
                if i in staffs:
                    staffs.pop(i).logout()
                self.i = i
                staffs[i] = self
                logging.info("%s %s login", "ws", i)
            except Exception as e:
                self.close()
                logging.error("failed to auth: %s: %s", type(e).__name__, e)

        def send(self, cmd, data):
            self.write_message(str(cmd) + " " + data)

        def logout(self):
            self.close()
            self.on_close()

    return WebSocket


def tcp(staffs, tokens, send=dummy_send):
    import logging
    import re
    from struct import pack, unpack

    from tornado.tcpserver import TCPServer

    from bb.const import FMT, LEN, NULL, ONLINE

    head_match = re.compile(r'.*(\d+) (\w+)\r\n\r\n$', re.S).match

    class Connection(object):
        def __init__(self, stream, address):
            self.stream = stream
            self.address = address
            self.stream.read_until(b'\r\n\r\n', self.login)
            logging.info("%s try in", self.address)

        def login(self, auth):
            """format: .* id token\r\n\r\n
            token can be generated by visit //bb/t?=1.token
            """
            stream = self.stream
            try:
                auth = auth.decode()
                i, k = head_match(auth).groups()
                i = int(i)
                t = tokens.pop(i)
                if k != t:
                    raise Warning("token error: {!r} != {!r}".format(k, t))
                if i in staffs:
                    staffs.pop(i).logout()
                self.i = i
                stream.set_close_callback(self.logout)
                stream.read_bytes(LEN, self.msg_head)
                staffs[i] = self
                logging.info("%s %s login", self.address, i)
            except Exception as e:
                stream.close()
                logging.error("failed to auth: {}({}) {!r}".format(
                    type(e).__name__, e, auth))

        def send(self, cmd, data):
            stream = self.stream
            if not stream.closed():
                stream.write(pack(FMT, cmd, len(data)) + data.encode())

        def logout(self):
            stream = self.stream
            if stream.closed():
                i = self.i
                send([i, ONLINE, NULL])
                logging.info("%s %s logout", self.address, i)
            else:
                stream.close()

        def msg_head(self, chunk):
            stream = self.stream
            logging.debug("head: %s", chunk)
            instruction, length_of_body = unpack(FMT, chunk)
            logging.debug("%d, %d", instruction, length_of_body)
            self.instruction = instruction
            if not stream.closed():
                stream.read_bytes(length_of_body, self.msg_body)

        def msg_body(self, chunk):
            stream = self.stream
            logging.debug("body: %s", chunk)
            send([self.i, self.instruction, chunk.decode() or NULL])
            if not stream.closed():
                stream.read_bytes(LEN, self.msg_head)

    class Server(TCPServer):
        def handle_stream(self, stream, address):
            Connection(stream, address)

    return Server


def backdoor(staffs, send=dummy_send):
    from tornado.tcpserver import TCPServer

    class Connection(object):
        def __init__(self, stream, address):
            self.stream = stream
            staffs[address] = stream
            stream.set_close_callback(stream.close)
            self.stream.write(b"Backdoor\n>>> ")
            self.stream.read_until(b'\n', self.handle_input)

        def handle_input(self, line):
            send([None, "shell", line.decode()])
            self.stream.read_until(b'\n', self.handle_input)

    class Server(TCPServer):
        def handle_stream(self, stream, address):
            Connection(stream, address)

    return Server

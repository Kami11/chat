#!/usr/bin/env python3

import os
import sys
import logging
import argparse

from tornado import websocket, web, ioloop

from .chat import WSHandlerFactory, AAAManager, ChatManager, CommandManager


class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("html/index.html")


WSHandler = WSHandlerFactory()


app = web.Application([
    (r'/', IndexHandler),
    (r'/ws', WSHandler),
], static_path=os.path.join(os.path.dirname(__file__), "static"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--address", default="127.0.0.1",
        help="IP address to listen on (default: 127.0.0.1)")
    parser.add_argument("-p", "--port", default=8888, type=int,
        help="TCP port to listen on (default: 8888)")
    parser.add_argument("-t", "--token",
        help="file with hashed authentication token")
    parser.add_argument("-d", "--debug", action="store_true",
        help="enable debug output")
    args = parser.parse_args()

    loglevel = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=loglevel, datefmt="%H:%M:%S",
                        format='[%(asctime)s] %(levelname)s: %(message)s')

    if args.token:
        try:
            with open(args.token, "r") as f:
                token_hash = f.read()
        except IOError as exc:
            logging.fatal("could not open {}: {}".format(args.token, exc.strerror))
            sys.exit(1)
    else:
        logging.warning("no auth token specified, admin logins are disabled")
        token_hash = None

    # Make chat stack
    aaa = AAAManager(WSHandler, token_hash)
    chat = ChatManager(aaa)
    cmd = CommandManager(chat)

    try:
        app.listen(port=args.port, address=args.address)
    except OSError as exc:
        logging.fatal(exc.strerror)
        sys.exit(2)

    logging.info("starting server on {}:{}".format(args.address, args.port))

    try:
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        logging.fatal("interrupted by user")
        sys.exit(0)


if __name__ == "__main__":
    main()

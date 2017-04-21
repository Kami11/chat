#!/usr/bin/env python3

import os
import sys
import logging
import argparse

import socket

import yaml
from tornado import websocket, web, ioloop

from .chat import UserDAO, WSHandlerFactory, AAAManager, \
                  ChatManager, CommandManager


# Path to default config file
DEFAULT_CONFIG = "/etc/kisschat.yml"


class IndexHandler(web.RequestHandler):
    def get(self):
        self.render("html/index.html")


WSHandler = WSHandlerFactory()


app = web.Application([
    (r'/', IndexHandler),
    (r'/ws', WSHandler),
], static_path=os.path.join(os.path.dirname(__file__), "static"))


def read_config(path):
    '''
        Read and parse config file specified by path.
        If config is invalid, log the error and exit program
        with non-zero error code.
        Parameters:
            path - file location, string.
        Return value:
            dict
    '''
    # Open file and parse YAML
    try:
        with open(path, "r") as f:
            config = yaml.load(f)
    except IOError as exc:
        logging.fatal("unable to open '{}': {}".format(path, exc.strerror))
        return sys.exit(1)
    except yaml.error.YAMLError as exc:
        logging.fatal("yaml error: {}".format(exc))
        return sys.exit(2)

    # Make sure config has all the required fields
    if not isinstance(config, dict):
        logging.fatal("config should be a dict")
        return sys.exit(3)
    for key in ["user", "passwd", "host", "port", "db"]:
        if key not in config:
            logging.fatal("config file is missing key '{}'".format(key))
            return sys.exit(4)
        if key != "port" and not isinstance(config[key], str):
            logging.fatal("config file key '{}' is not a str".format(key))
            return sys.exit(5)
    if not isinstance(config["port"], int) or not (0 < config["port"] < 65536):
        logging.fatal("config file key 'port' should be a positive int < 65536")
        return sys.exit(6)

    return config


def main():

    # Define and parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--address", default="127.0.0.1",
        help="IP address to listen on (default: 127.0.0.1)")
    parser.add_argument("-p", "--port", default=8888, type=int,
        help="TCP port to listen on (default: 8888)")
    parser.add_argument("-c", "--config", default=DEFAULT_CONFIG,
        help="path to config file (default: {})".format(DEFAULT_CONFIG))
    parser.add_argument("-d", "--debug", action="store_true",
        help="enable debug output")
    args = parser.parse_args()

    # Setup logging
    loglevel = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=loglevel, datefmt="%H:%M:%S",
                        format='[%(asctime)s] %(levelname)s: %(message)s')

    # Read and parse config file
    config = read_config(args.config)

    # Connect to the database
    try:
        db = UserDAO(config["user"], config["passwd"], config["host"],
                     config["port"], config["db"])
    except UserDAO.ConnectionError as exc:
        logging.fatal("connection to database failed: {}".format(exc))
        return sys.exit(7)
    else:
        logging.info("connected to database {}:{}".format(config["host"], config["port"]))

    # Make chat stack
    aaa = AAAManager(WSHandler, db)
    chat = ChatManager(aaa)
    cmd = CommandManager(chat)

    # Listen on given ip and port
    try:
        app.listen(port=args.port, address=args.address)
    except OSError as exc:
        logging.fatal(exc.strerror)
        return sys.exit(7)

    logging.info("starting server on {}:{}".format(socket.gethostbyname(socket.gethostname()), args.port))

    # Start the server
    try:
        ioloop.IOLoop.instance().start()
    except KeyboardInterrupt:
        logging.fatal("interrupted by user")
        sys.exit(0)


if __name__ == "__main__":
    main()

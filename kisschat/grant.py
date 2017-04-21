#!/usr/bin/env python3

'''
    A script that allows to change user status more easily.
    An alternative would be to use MySQL client to edit 'users' table directly.
'''

import sys
import logging
import argparse

from .server import DEFAULT_CONFIG, read_config
from .chat import UserDAO
from .chat.struct import User


def show(names, db):
    '''
        Print to stdout statuses of users with given names.
        If some user is not in the database, log the error.
        Parameters:
            names - list of user names (strings);
            db - UserDAO instance.
        Return value:
            None
    '''
    for name in names:
        try:
            user = db.getUser(name)
        except db.DoesNotExistError:
            logging.error("user not found: {}".format(name))
        else:
            sys.stdout.write("{} : {}\n".format(name, user.status.name))


def set_status(names, status, db):
    '''
        Set status of all the users with given names.
        If some user is not in the database, log the error.
        Parameters:
            names - list of user names (strings);
            status - enum entry (User.Status);
            db - UserDAO instance.
        Return value:
            None
    '''
    for name in names:
        if not db.setUserStatus(name, status):
            logging.error("user not found: {}".format(name))


def main():

    # Define and parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("command", help="what to do: 'show', 'grant' or 'revoke'")
    parser.add_argument("user", nargs="+", help="user(s) to operate on")
    parser.add_argument("-c", "--config", default=DEFAULT_CONFIG,
        help="path to config file (default: {})".format(DEFAULT_CONFIG))
    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

    # Read and parse config file
    config = read_config(args.config)

    # Connect to the database
    try:
        db = UserDAO(config["user"], config["passwd"], config["host"],
                     config["port"], config["db"])
    except UserDAO.ConnectionError as exc:
        logging.fatal("connection to database failed: {}".format(exc))
        return sys.exit(7)

    # Parse command
    if "show".startswith(args.command):
        show(args.user, db)
    elif "grant".startswith(args.command):
        set_status(args.user, User.Status.admin, db)
    elif "revoke".startswith(args.command):
        set_status(args.user, User.Status.user, db)
    else:
        logging.fatal("unrecognized command: {}".format(args.command))

    sys.exit(0)


if __name__ == "__main__":
    main()

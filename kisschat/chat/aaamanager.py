
import sys
import json
import base64
import hashlib
import getpass
import logging
import argparse

import observer

from .struct import User


class AAAManager:


    @staticmethod
    def hash(string):
        utf8 = string.encode("utf8")
        hash_ = hashlib.sha512(utf8 + b"Inn0p0l1sF0reva&!$#@**").digest()
        return base64.b64encode(hash_).decode("ascii")


    def __init__(self, transport, token_hash=None):

        self.token_hash = token_hash

        self._current_usernames = set()
        self._banned_usernames = set()
        self._banned_ips = set()
        self._endpoint_to_user = {}
        self._user_to_endpoint = {}

        self.userConnected = observer.Event()
        self.userDisconnected = observer.Event()
        self.userSentMessage = observer.Event()

        transport.newConnection.on(self._onConnection)
        transport.newData.on(self._onData)
        transport.droppedConnection.on(self._onDisconnect)


    def _onConnection(self, endpoint):
        if endpoint.ip in self._banned_ips:
            logging.debug("<{}> tried to connect but banned".format(endpoint.ip))
            endpoint.disconnect()
        else:
            logging.debug("<{}>: connected".format(endpoint.ip))


    def _onData(self, endpoint, data):

        if endpoint in self._endpoint_to_user:
            user = self._endpoint_to_user[endpoint]
            data = data.strip()
            if data:
                self.userSentMessage.trigger(user, data)
            return

        logging.debug("received data from <{}>: {}".format(endpoint.ip, data))

        try:
            request = json.loads(data)
        except json.decoder.JSONDecodeError:
            logging.debug("<{}>: auth info is not a valid JSON, aborting".format(endpoint.ip))
            return self._abortAuthentication(endpoint)

        try:
            name = request["name"].strip()
            token = request.get("token")
            assert isinstance(name, str) and (not token or isinstance(token, str))
        except (TypeError, KeyError, AttributeError, AssertionError):
            logging.debug("<{}>: invalid auth info format, avorting".format(endpoint.ip))
            return self._abortAuthentication(endpoint)

        if name in self._current_usernames:
            logging.debug("<{}>: username '{}' in use, reject".format(endpoint.ip, name))
            return self._abortAuthentication(endpoint, "username_in_use")

        if not name or name in self._banned_usernames:
            logging.debug("<{}>: username '{}' banned, reject".format(endpoint.ip, name))
            return self._abortAuthentication(endpoint, "username_banned")

        if token and self.hash(token) != self.token_hash:
            logging.debug("<{}>: wrong auth token, reject".format(endpoint.ip, name))
            return self._abortAuthentication(endpoint, "authentication_failed")
        elif token:
            user_status = User.Status.admin
        else:
            user_status = User.Status.user

        user = User(name, user_status, endpoint.ip)
        self._endpoint_to_user[endpoint] = user
        self._user_to_endpoint[user] = endpoint
        self._current_usernames.add(user.name)
        endpoint.sendData(json.dumps({"ok": True}))
        self.userConnected.trigger(user)


    def _onDisconnect(self, endpoint):
        if endpoint not in self._endpoint_to_user: return
        logging.debug("<{}>: disconnected".format(endpoint.ip))
        user = self._endpoint_to_user[endpoint]
        self._purgeUser(user)
        self.userDisconnected.trigger(user)


    def _abortAuthentication(self, endpoint, reason=None):
        if reason:
            endpoint.sendData(json.dumps({"ok": False, "reason": reason}))
        endpoint.disconnect()


    def sendTo(self, user, data):
        endpoint = self._user_to_endpoint[user]
        endpoint.sendData(data)
        logging.debug("sending to [{}]: {}".format(user.name, data))


    def disconnect(self, user):
        endpoint = self._user_to_endpoint[user]
        endpoint.disconnect()
        self._purgeUser(user)


    def ban(self, username):
        if username in self._banned_usernames:
            return False
        self._banned_usernames.add(username)
        for endpoint, user in tuple(self._endpoint_to_user.items()):
            if user.name == username:
                endpoint.disconnect()
                self._purgeUser(user)
        return True


    def banip(self, ip):
        if ip in self._banned_ips:
            return False
        self._banned_ips.add(ip)
        for endpoint, user in tuple(self._endpoint_to_user.items()):
            if endpoint.ip == ip:
                endpoint.disconnect()
                self._purgeUser(user)
        return True


    def _purgeUser(self, user):
        endpoint = self._user_to_endpoint.pop(user)
        del self._endpoint_to_user[endpoint]
        self._current_usernames.remove(user.name)


    def unban(self, username):
        try:
            self._banned_usernames.remove(username)
        except KeyError:
            return False
        else:
            return True


    def unbanip(self, ip):
        try:
            self._banned_ips.remove(ip)
        except KeyError:
            return False
        else:
            return True


    def getBannedUsernames(self):
        return frozenset(self._banned_usernames)


    def getBannedIps(self):
        return frozenset(self._banned_ips)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("-o", "--output", default="token.hash", help="output file")
    args = parser.parse_args()

    token = getpass.getpass("Enter your token: ")
    hash_ = AAAManager.hash(token)

    try:
        with open(args.output, "w") as f:
            f.write(hash_)
    except IOError as exc:
        print("FATAL: unable to write token hash to {}: {}"
              .format(args.output, exc.strerror))
        sys.exit(1)
    else:
        print("Token is written to {}".format(args.output))
        sys.exit(0)


if __name__ == "__main__":
    main()

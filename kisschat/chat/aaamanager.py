
import sys
import json
import base64
import hashlib
import getpass
import logging
import argparse

import sha3 # monkey patches hashlib
import observer

from .struct import User


class AAAManager:


    @staticmethod
    def hash(string, salt):
        '''
            Hash given string with given salt.
            Parameters:
                string - to be hashed;
                salt - to be hashed with, bytes.
            Return value:
                bytes - hashed string with given salt
        '''
        hash_ = string.encode("utf8")
        for b in salt:
            hash_ = hashlib.sha3_512(hash_ + b.to_bytes(1, "big")).digest()
        return hash_


    def __init__(self, transport, db):

        self._db = db
        self._current_usernames = set()
        self._endpoint_to_user = {}
        self._user_to_endpoint = {}

        self.userConnected = observer.Event()
        self.userDisconnected = observer.Event()
        self.userSentMessage = observer.Event()

        transport.newConnection.on(self._onConnection)
        transport.newData.on(self._onData)
        transport.droppedConnection.on(self._onDisconnect)


    def _onConnection(self, endpoint):
        if self._db.isIpBanned(endpoint.ip):
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
            passwd = request["passwd"].strip()
            assert isinstance(name, str) and (not token or isinstance(token, str))
        except (TypeError, KeyError, AttributeError, AssertionError):
            logging.debug("<{}>: invalid auth info format, avorting".format(endpoint.ip))
            return self._abortAuthentication(endpoint)

        if name in self._current_usernames:
            logging.debug("<{}>: user '{}' already logged in, reject".format(endpoint.ip, name))
            return self._abortAuthentication(endpoint, "user_logged_in")

        if not name or self._db.isUsernameBanned(name):
            logging.debug("<{}>: user '{}' banned, reject".format(endpoint.ip, name))
            return self._abortAuthentication(endpoint, "user_banned")

        # Try to retreive user from database by name
        try:
            user = self._db.getUser(name)
        except self._db.DoesNotExist:
            # If user does not exist, create them
            salt = bytes([random.randrange(256) for _ in range(64)])
            passwd_hash = self.hash(passwd, salt)
            try:
                user = self._db.createUser(name, User.Status.user, passwd_hash, salt)
            except self._db.InvalidFieldError:
                # Most likely, name is too long. The name length should be
                # controlled by frontend, so we just abort with no error message
                return self._abortAuthentication(endpoint)
        else:
            # If user exists, authenticate
            if self.hash(passwd, user.passwd_salt) != user.passwd_hash:
                logging.debug("<{}>: wrong password, reject".format(endpoint.ip))
                return self._abortAuthentication(endpoint, "authentication_failed")

        # Add ip address to user object (when retreived from db, user.ip is None)
        user = user._replace(ip=endpoint.ip) # _replace is NOT private, see Python docs

        # Add user to all needed structures of AAAManager
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
        if not self._db.banUsername(username):
            return False
        for endpoint, user in tuple(self._endpoint_to_user.items()):
            if user.name == username:
                endpoint.disconnect()
                self._purgeUser(user)
        return True


    def banip(self, ip):
        if not self._db.banIp(ip):
            return False
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
        return self._db.unbanUsername(username)


    def unbanip(self, ip):
        return self._db.unbanIp(ip)


    def getBannedUsernames(self):
        return [user.name for user in self._db.getBannedUsers()]


    def getBannedIps(self):
        return self._db.getBannedIps()


if __name__ == "__main__":
    main()

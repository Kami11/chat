
from enum import Enum
from collections import namedtuple


class User(namedtuple("UserTuple", ["name", "status", "ip", "is_banned",
                                    "passwd_hash", "passwd_salt"])):
    '''
        Immutable object that represents chat user.
        It can refer both to an online user as well as to a user retreived from
        database. If the user is not online, it's "ip" value is usually None.
        Fields:
            name - user name, string
            status - user status, enum (declared below)
            ip - user ip address (if user is online), string
            is_banned - if user is banned or not, bool
            passwd_hash - password hash, bytes
            passwd_salt - password salt, bytes
    '''

    # User status enum
    class Status(Enum):
        admin = 0
        user = 1

    # Status from int conversion
    StatusFromInt = {en.value: en for en in Status}


class WSEndpoint:

    def __init__(self, websocket):
        self._ws = websocket

    def __eq__(self, other):
        return isinstance(other, WSEndpoint) and self._ws is other._ws

    def __hash__(self):
        return hash(self._ws) + 5

    @property
    def ip(self):
        return self._ws.request.remote_ip

    @property
    def sendData(self):
        return self._ws.write_message

    @property
    def disconnect(self):
        return self._ws.close

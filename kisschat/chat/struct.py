
from enum import Enum
from collections import namedtuple


class User(namedtuple("UserTuple", ["name", "status", "ip"])):

    class Status(Enum):
        admin = 0
        user = 1


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

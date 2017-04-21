
import json
import logging
import datetime

import observer

from .struct import User


class ChatManager:

    greeting_message = "Welcome, {username}!"

    admin_greeting = "Welcome, {username}!\n" \
        "You are the Admin. Some magic commands:\n" \
        " * @who - view list of users currently online\n" \
        " * @kick [user] - kick user by username or ip\n" \
        " * @ban [username] - ban username\n" \
        " * @banip [ip] - ban ip address\n" \
        " * @banlist - view list usernames and ip addresses banned\n" \
        " * @unban [user] - unban username\n" \
        " * @unbanip [ip] - unban ip address"

    command_prefix = "@"


    @staticmethod
    def time():
        time = datetime.datetime.now().time()
        return "[{:02}:{:02}]".format(time.hour, time.minute)


    def __init__(self, aaa_manager):

        self._aaa = aaa_manager
        self._users = set()
        self.commandReceived = observer.Event()

        self._aaa.userConnected.on(self._onUserConnect)
        self._aaa.userDisconnected.on(self._onUserDisconnect)
        self._aaa.userSentMessage.on(self._onUserMessage)


    def _onUserConnect(self, user):
        self._users.add(user)
        if user.status == User.Status.admin:
            logging.info("admin connected: {} ({})".format(user.name, user.ip))
            self.sendTo(user, self.admin_greeting.format(username=user.name))
        else:
            logging.info("user connected: {} ({})".format(user.name, user.ip))
            self.sendTo(user, self.greeting_message.format(username=user.name))
        if len(self._users) > 1:
            self._sendEventTo(user, "new_users",
                              names=[u.name for u in self._users if u != user])
        self._broadcastEvent("new_users", names=[user.name], except_=[user])


    def _onUserDisconnect(self, user):
        logging.info("user disconnected: {} ({})".format(user.name, user.ip))
        self._users.remove(user)
        self._broadcastEvent("del_users", names=[user.name])


    def _onUserMessage(self, user, message):
        logging.debug("message from [{}]: {}".format(user.name, message))
        if message.startswith(self.command_prefix):
            words = message.split()
            words[0] = words[0][len(self.command_prefix):]
            self.sendTo(user, "{} >> {}".format(self.time(), " ".join(words)))
            self.commandReceived.trigger(user, words)
        else:
            self.broadcast("{} <{}> {}".format(self.time(), user.name, message))


    def sendTo(self, user, message):
        self._sendEventTo(user, "new_message", message=message)


    def broadcast(self, message, except_=[]):
        self._broadcastEvent("new_message", message=message, except_=except_)


    def _sendEventTo(self, user, event_type, **kw):
        event = kw
        event["type"] = event_type
        data = json.dumps(event)
        self._aaa.sendTo(user, data)


    def _broadcastEvent(self, event_type, **kw):
        except_ = set(kw.pop("except_", []))
        event = kw
        event["type"] = event_type
        data = json.dumps(event)

        for user in (self._users - except_):
            self._aaa.sendTo(user, data)


    def kick(self, user):
        self._aaa.disconnect(user)
        self._purgeUsers([user])


    def ban(self, username):
        success = self._aaa.ban(username) # false means that username is already banned
        if success:
            logging.info("username banned: {}".format(username))
            self._purgeUsers([u for u in self._users if u.name == username])
        return success


    def banip(self, ip):
        success = self._aaa.banip(ip) # false means that ip is already banned
        if success:
            logging.info("ip banned: {}".format(ip))
            self._purgeUsers([u for u in self._users if u.ip == ip])
        return success


    def _purgeUsers(self, users):
        if not users: return
        self._users -= set(users)
        names = sorted(u.name for u in users)
        self._broadcastEvent("del_users", names=names)
        if len(names) > 1:
             logging.info("users kicked: {}".format(", ".join(names)))
        else:
            logging.info("user kicked: {}".format(", ".join(names)))


    def unban(self, username):
        success = self._aaa.unban(username)
        if success:
            logging.info("username unbanned: {}".format(username))
        return success


    def unbanip(self, ip):
        success = self._aaa.unbanip(ip)
        if success:
            logging.info("ip unbanned: {}".format(ip))
        return success


    def getBannedUsernames(self):
        return self._aaa.getBannedUsernames()


    def getBannedIps(self):
        return self._aaa.getBannedIps()


    def getAllUsers(self):
        return list(self._users)

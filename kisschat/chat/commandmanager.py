
from .. import helpers
from .struct import User


class CommandManager:

    user_command = helpers.FunctionMapper()
    admin_command = helpers.FunctionMapper()


    def __init__(self, chat_manager):

        self._chat = chat_manager
        self._chat.commandReceived.on(self._onCommand)
        self._user_commands = self.user_command.all
        self._admin_commands = self.admin_command.all


    def _onCommand(self, user, words):

        cmd = words[0]

        if user.status == User.Status.admin and cmd in self._admin_commands:
            self._admin_commands[cmd](self, user, words[1:])

        elif cmd in self._user_commands:
            self._user_commands[cmd](self, user, words[1:])

        else:
            self._chat.sendTo(user, "Command not found: {}".format(cmd))


    @admin_command("who")
    def _who(self, user, args):

        users = self._chat.getAllUsers()
        if not users:
            return self._chat.sendTo(user, "No users online.")
        else:
            msg = "\n * ".join(["Users online:"]
                + ["{} ({})".format(other.name, other.ip) for other in users])
            self._chat.sendTo(user, msg)


    @admin_command("kick")
    def _kick(self, user, args):

        if not self._assertArgCount(user, args, 1):
            return

        users = self._getMatchingUsers(args[0])
        if not users:
            self._chat.sendTo(user, "User is not online.")
        else:
            for other in users:
                self._chat.kick(other)


    @admin_command("ban")
    def _ban(self, user, args):

        if not self._assertArgCount(user, args, 1):
            return

        if not self._chat.ban(args[0]):
            self._chat.sendTo(user, "User already banned.")


    @admin_command("banip")
    def _banip(self, user, args):

        if not self._assertArgCount(user, args, 1):
            return

        if not helpers.is_ip(args[0]):
            self._chat.sendTo(user, "Not an IP address.")
        elif not self._chat.banip(args[0]):
            self._chat.sendTo(user, "IP address already banned.")


    @admin_command("unban")
    def _unban(self, user, args):

        if not self._assertArgCount(user, args, 1):
            return

        if not self._chat.unban(args[0]):
            self._chat.sendTo(user, "User is not banned.")


    @admin_command("unbanip")
    def _unbanip(self, user, args):

        if not self._assertArgCount(user, args, 1):
            return

        if not self._chat.unbanip(args[0]):
            self._chat.sendTo(user, "IP address is not banned.")


    @admin_command("banlist")
    def _banlist(self, user, args):

        names = self._chat.getBannedUsernames()
        ips = self._chat.getBannedIps()

        if not names and not ips:
            return self._chat.sendTo(user, "Banlist is empty.")

        messages = []
        if names:
            messages.append("\n * ".join(["Banned user names:"] + sorted(names)))
        if ips:
            messages.append("\n * ".join(["Banned IP addresses:"] + sorted(ips)))
        self._chat.sendTo(user, "\n".join(messages))


    def _getMatchingUsers(self, username_or_ip):

        matches = []
        for user in self._chat.getAllUsers():
            if user.name == username_or_ip or user.ip == username_or_ip:
                matches.append(user)
        return matches


    def _assertArgCount(self, user, args, min_args):
        if len(args) < min_args:
            self._chat.sendTo(user, "Too few arguments, expected {}.".format(min_args))
            return False
        return True

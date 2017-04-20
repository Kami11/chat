'''
    A file that contains all the database logic.
'''

class UserDAO:
    '''
        This class encapsulates all the interaction with the database
        that has to do with user records.
    '''

    # General case error
    class Error(Exception): pass

    # Error for constructor if failed to establish connection to the database
    class ConnectionError(Error): pass

    # Error if requested object does not exist in the database
    class DoesNotExist(Error): pass


    def __init__(self, user, passwd, host, port, dbname):
        '''
            Initialize the instance. Parameters:
                user - database user name, string;
                passwd - database user password, string;
                host - database address, string;
                port - database port number, int;
                dbname - database name, string.
            Raises:
                self.ConnectionError if failed to establish connection
        '''


    def getUser(self, name):
        '''
            Get user by name.
            Parameters:
                name - user name, string.
            Return value:
                User object. Note that this object has 'ip' equal to None.
            Raises:
                self.DoesNotExist of there is no user with such name
        '''


    def createUser(self, name, status, passwd_hash, salt):
        '''
            Add new user to the database.
            Parameters:
                name - user name, string;
                status - user status, integer;
                passwd_hash - user password hash, bytes;
                salt - user password hash salt, bytes;
        '''


    def isUsernameBanned(self, name):
        '''
            Check if given user name is banned or not.
            Parameters:
                name - user name, string.
            Return value:
                True if given user name is banned, False otherwise
        '''


    def banUsername(self, name):
        '''
            Ban given user name. If already banned, do nothing.
            Parameters:
                name - user name, string.
            Return value:
                True if user name had not been banned before this method call,
                False if it is already banned.
        '''


    def unbanUsername(self, name):
        '''
            Unban given username. If not banned, do nothing.
            Parameters:
                name - user name, string.
            Return value:
                True if user name had been banned before this method call,
                False if it is not banned.
        '''


    def getBannedUsers(self):
        '''
            Get the list of banned users.
            Return value:
                list of User objects that are banned
        '''


    def isIpBanned(self, ip):
        '''
            Check if given ip is banned or not.
            Parameters:
                ip - ip address, string;
            Return value:
                True if given ip is banned, False otherwise.
        '''


    def banIp(self, ip):
        '''
            Ban given ip address.
            Parameters:
                ip - ip address, string;
            Return value:
                True if this ip had not been banned before this method call,
                False if ip is already banned.
        '''


    def unbanIp(self, ip):
        '''
            Unban given ip address.
            Parameters:
                ip - ip address, string;
            Return value:
                True if this ip had been banned before this method call,
                False if it is not banned.
        '''

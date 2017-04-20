'''
    A file that contains all the database logic.
'''

from sqlalchemy import create_engine, Table, Column, Integer, Binary, Boolean, \
    String, MetaData, DateTime, Sequence
from sqlalchemy.sql import select
from sqlalchemy.exc import OperationalError

from .struct import User


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
    class DoesNotExistErorr(Error): pass

    # Error if trying to create object with onvalid field value
    class InvalidFieldError(Error): pass


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

        # Create db engine (but it does not connect at this point)
        engine_str = "mysql+pymysql://{}:{}@{}:{}/{}".format(user, passwd, host,
                                                     port, dbname)
        self._engine = create_engine(engine_str, isolation_level="READ UNCOMMITTED")

        # Define tables
        self._metadata = MetaData()
        self._users = Table('users', self._metadata,
            Column('id', Integer, Sequence('users_id_seq'), primary_key=True),
            Column('name', String(32), nullable=False, unique=True),
            Column('passwd_hash', Binary(64), nullable=False),
            Column('passwd_salt', Binary(64), nullable=False),
            Column('status', Integer, nullable=False),
            Column('is_banned', Boolean, index=True, nullable=False),
        )
        self._ips = Table('banned_ips', self._metadata,
            Column('id', Integer, Sequence('ips_id_seq'), primary_key=True),
            Column('ip', String(15), nullable=False),
        )

        # Create tables
        try:
            self._metadata.create_all(self._engine)
        except OperationalError as exc:
            raise self.ConnectionError(str(exc))

        # Save connection
        self._conn = self._engine.connect()


    def getUser(self, name):
        '''
            Get user by name.
            Parameters:
                name - user name, string.
            Return value:
                User object. Note that this object has 'ip' equal to None.
            Raises:
                self.DoesNotExistErorr of there is no user with such name
        '''
        s = select([self._users]).where(self._users.c.name == name)
        rows = self._conn.execute(s).fetchall()
        if rows:
            user = rows[0] # this is SQLAlchemy dict-like object
            return User(name=user.name, status=user.status, ip=None,
                        is_banned=user.is_banned, passwd_hash=user.passwd_hash,
                        passwd_salt=user.passwd_salt)
        else:
            raise self.DoesNotExistErorr


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

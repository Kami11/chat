'''
    A file that contains all the database logic.
'''

from sqlalchemy import create_engine, Table, Column, Integer, Binary, Boolean, \
    String, MetaData, DateTime, Sequence
from sqlalchemy.sql import select
from sqlalchemy.exc import SQLAlchemyError

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
    class DoesNotExistError(Error): pass

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
            Column('name', String(32), nullable=False, unique=True, index=True),
            Column('passwd_hash', Binary(64), nullable=False),
            Column('passwd_salt', Binary(64), nullable=False),
            Column('status', Integer, nullable=False),
            Column('is_banned', Boolean, index=True, nullable=False),
        )
        self._ips = Table('banned_ips', self._metadata,
            Column('id', Integer, Sequence('ips_id_seq'), primary_key=True),
            Column('ip', String(15), nullable=False, unique=True),
        )

        # Create tables
        try:
            self._metadata.create_all(self._engine)
        except SQLAlchemyError as exc:
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
                self.DoesNotExistError of there is no user with such name
        '''
        s = select([self._users]).where(self._users.c.name == name)
        row = self._conn.execute(s).fetchone()
        if row:
            return User(name=row.name, status=User.StatusFromInt[row.status],
                        is_banned=row.is_banned, passwd_hash=row.passwd_hash,
                        passwd_salt=row.passwd_salt, ip=None)
        else:
            raise self.DoesNotExistError


    def createUser(self, name, status, passwd_hash, passwd_salt, is_banned=False):
        '''
            Add new user to the database.
            Parameters:
                name - user name, string;
                status - user status, enum (from User.Status);
                passwd_hash - user password hash, bytes;
                passwd_salt - user password hash salt, bytes;
                is_banned - if user is banned, bool.
            Return value:
                User object that got created
            Raises:
                self.InvalidFieldError if one of the fields has invalid value
                self.Error if failed to insert for some other reason
        '''
        status_int = status.value # convert enum to int
        invalid_fields = self._validateUserEntry(name, status_int, passwd_hash,
                                                 passwd_salt, is_banned)
        if invalid_fields:
            raise self.InvalidFieldError(invalid_fields)
        else:
            row = {"name": name, "status": status_int, "passwd_hash": passwd_hash,
                   "passwd_salt": passwd_salt, "is_banned": is_banned}
            try:
                self._conn.execute(self._users.insert(), [row])
            except SQLAlchemyError as exc:
                raise self.Error(str(exc))
            else:
                return User(name=name, status=status, ip=None,
                            is_banned=is_banned, passwd_hash=passwd_hash,
                            passwd_salt=passwd_salt)


    def _validateUserEntry(self, name, status, passwd_hash, passwd_salt, is_banned):
        '''
            Check that field values are valid for the db table.
            Parameters:
                name - user name, string;
                status - user status, integer;
                passwd_hash - user password hash, bytes;
                passwd_salt - user password hash salt, bytes;
                is_banned - if user is banned, bool.
            Return value:
                list of field names which values are invalid
        '''
        # For convenience, create a dict
        row = {
            "name": name,
            "status": status,
            "passwd_hash": passwd_hash,
            "passwd_salt": passwd_salt,
            "is_banned": is_banned
        }
        # For readability, create validator functions for each type
        validators = {
            String: lambda col, val: isinstance(val, str) and len(val) <= col.type.length,
            Binary: lambda col, val: isinstance(val, bytes) and len(val) <= col.type.length,
            Integer: lambda col, val: isinstance(val, int) and (-(2**31) < val < 2**31),
            Boolean: lambda col, val: isinstance(val, bool)
        }
        # Find invalid column values
        invalid = [] # invalid column names
        for column in self._users.columns:
            colname = column.name
            if colname != "id":
                value = row[colname]
                if not validators.get(column.type.__class__)(column, value):
                    invalid.append(colname)
        return invalid


    def isUsernameBanned(self, name):
        '''
            Check if given user name is banned or not.
            Parameters:
                name - user name, string.
            Return value:
                True if given user name is banned, False otherwise
        '''
        s = select([self._users.c.is_banned]).where(self._users.c.name == name)
        row = self._conn.execute(s).fetchone()
        if row:
            return row[0]
        else:
            return False


    def banUsername(self, name):
        '''
            Ban given user name. If already banned, do nothing.
            Parameters:
                name - user name, string.
            Return value:
                True if user name had not been banned before this method call,
                False if it is already banned.
        '''
        # Fetch record from database
        s = select([self._users.c.is_banned]).where(self._users.c.name == name)
        row = self._conn.execute(s).fetchone()
        if row:
            if row[0]:
                return False # user already banned
            else:
                u = self._users.update().where(self._users.c.name == name) \
                        .values(is_banned=True)
                self._conn.execute(u)
                return True
        else:
            # User is not in the database. In this case, create dummy user
            # and ban it
            try:
                self.createUser(name, User.Status.user, b"", b"", True)
            except self.InvalidFieldError:
                # Such user name is impossible, so we may think like
                # it is already banned
                return False
            else:
                return True


    def unbanUsername(self, name):
        '''
            Unban given username. If not banned, do nothing.
            Parameters:
                name - user name, string.
            Return value:
                True if user name had been banned before this method call,
                False if it is not banned.
        '''
        # Fetch record from database
        try:
            user = self.getUser(name)
        except self.DoesNotExistError:
            return False
        else:
            if not user.is_banned:
                return False
            elif not user.passwd_hash:
                # If user does not have password hash, it is a dummy user
                # and we'd better delete it to save database space
                d = self._users.delete().where(self._users.c.name == name)
                self._conn.execute(d)
                return True
            else:
                u = self._users.update().where(self._users.c.name == name) \
                        .values(is_banned=False)
                self._conn.execute(u)
                return True


    def getBannedUsers(self):
        '''
            Get the list of banned users.
            Return value:
                list of User objects that are banned
        '''
        s = select([self._users]).where(self._users.c.is_banned == True)
        rows = self._conn.execute(s)
        return [User(name=row.name, status=User.StatusFromInt[row.status],
                    ip=None, is_banned=row.is_banned, passwd_hash=row.passwd_hash,
                    passwd_salt=row.passwd_salt) for row in rows]


    def isIpBanned(self, ip):
        '''
            Check if given ip is banned or not.
            Parameters:
                ip - ip address, string;
            Return value:
                True if given ip is banned, False otherwise.
        '''
        s = select([self._ips]).where(self._ips.c.ip == ip)
        row = self._conn.execute(s).fetchone()
        return bool(row)


    def banIp(self, ip):
        '''
            Ban given ip address.
            Parameters:
                ip - ip address, string;
            Return value:
                True if this ip had not been banned before this method call,
                False if ip is already banned.
        '''
        try:
            self._conn.execute(self._ips.insert(), [{"ip": ip}])
        except SQLAlchemyError:
            # We are relying on the 'unique' constraint of the 'ip' column
            return False
        else:
            return True


    def unbanIp(self, ip):
        '''
            Unban given ip address.
            Parameters:
                ip - ip address, string;
            Return value:
                True if this ip had been banned before this method call,
                False if it is not banned.
        '''
        s = select([self._ips]).where(self._ips.c.ip == ip)
        row = self._conn.execute(s).fetchone()
        d = self._ips.delete().where(self._ips.c.ip == ip)
        self._conn.execute(d)
        return bool(row)


    def getBannedIps(self):
        '''
            Return a list of all banned ip addresses (strings).
        '''
        s = select([self._ips.c.ip])
        rows = self._conn.execute(s)
        return [row[0] for row in rows]

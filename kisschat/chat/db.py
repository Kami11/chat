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


    def __init__(self, user, passwd, host, port, dbname):
        '''
            Initialize the instance. Parameters:
                user - database user name, string;
                passwd - database user password, string;
                host - database address, string;
                port - database port number, int;
                dbname - database name, string.
            Raises:
                self.Error if failed to establish connection
        '''

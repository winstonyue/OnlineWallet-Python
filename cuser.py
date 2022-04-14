class Cuser(object):
    '''
    classdocs
    '''

    def __init__(self, u: str, p: str, a: str, b):
        '''
        Constructor
        '''
        self._username = u
        self._password = p 
        self._alias = a
        self._balance = b
        
    def __str__(self):
        return 'Alias:{}\nUsername:{}\n'.format(self._alias,self._username)
        
    def login(self, u: str, p: str) -> bool:
        if ((self._username == u) and (self._password == p)):
            return True
        else:
            return False

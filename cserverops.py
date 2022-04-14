from cmessage import Cmessage
from cprotocol import Cprotocol
from cuser import Cuser



class Cserverops(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self._users = {}
        self._aliases = {}
        self._courses = {}
        self.sproto = Cprotocol()
        self.connected = False
        self._login = False
        self._route = {'LGIN': self._doLogin, 'REGI': self._doRegister, 'PAYR': self._doPay, 'CHCK': self._doCheck, 'LOUT': self._doLogout, 'ADDF': self._doAdd, 'RQST': self._doRequest}
        self._debug = True
        
    def _debugPrint(self, m: str):
        if self._debug:
            print(m)
        
    def load(self, uname: str):
        with open(uname) as fp:
            for line in fp:
                if line != '\n':
                    line = line.strip()
                    values = line.split()
                    user = Cuser(values[0],values[1],values[2],values[3])
                    self._users[values[0]] = user
                    self._aliases[values[2]] = values[0]
                


            
    def _doLogin(self, req: Cmessage) -> Cmessage:
        resp = Cmessage()
        u = req.getParam('username')
        p = req.getParam('password')
        if u in self._users:
            if self._users[u].login(u,p):
                resp.setType('GOOD')
                resp.addParam('message', 'Login successful. Welcome.')
                resp.addParam('alias', self._users[u]._alias)
                self._login = True
                global currentUser
                currentUser = self._users[u]._username
            else:
                resp.setType('ERRO')
                resp.addParam('message', 'Bad login')
                self.connected = False
        else:
            resp.setType('ERRO')
            resp.addParam('message', 'Bad login')
            self.connected = False
        return resp

    def _doCheck(self, req: Cmessage) -> Cmessage:
        resp = Cmessage()
        resp.setType('DATA')
        resp.addParam('message', self._users[currentUser]._balance)
        return resp

    def _doAdd(self, req: Cmessage) -> Cmessage:
        d = int(req.getParam('amount'))
        oldbalance = self._users[currentUser]._balance
        newbalance = d + int(oldbalance)
        newbalance = str(newbalance)
        f= open("users.txt", "r")
        

        with open("users.txt", "r") as f:
            lines = f.readlines()
            with open("users.txt", "w") as f:
                for line in lines:
                    if self._users[currentUser]._username + ' ' + self._users[currentUser]._password + ' ' + self._users[currentUser]._alias + ' ' + self._users[currentUser]._balance not in line:
                        f.write(line)
                f.write("\n" + self._users[currentUser]._username + ' ' + self._users[currentUser]._password + ' ' + self._users[currentUser]._alias + ' ' + newbalance)



    def _doRegister(self, req: Cmessage) -> Cmessage:
        resp = Cmessage()
        u = req.getParam('username')
        p = req.getParam('password')
        a = req.getParam('alias')
        if u in self._users:
            resp.setType('ERRO')
            resp.addParam('message', 'Username already exsists')
        else:
            resp.setType('GOOD')
            with open('users.txt', 'a') as f:
                k = u + ' ' + p + ' ' + a
                f.write('\n'+ k)
            resp.addParam('message', 'Account created')
            self._login = False
            self.connected = False
        return resp
         
        
    
    def _doLogout(self, req: Cmessage) -> Cmessage:
        self._login = False
        self.connected = False
    

    def _doRequest(self, req: Cmessage) -> Cmessage:
        resp = Cmessage()
        recipient = req.getParam('recipient')
        amount = int(req.getParam('amount'))
        resp.setType('DATA')
        if recipient in self._aliases:
            line = recipient + ' ' + self._users[currentUser]._alias + ' ' + str(amount)
            with open('pending.txt', 'a') as f:
                f.write(line + '\n')
            resp.addParam('message', 'Request sent')
        else:
            resp.setType('ERRO')
            resp.addParam('message', 'recipient not found')
        return resp


    def _doPay(self, req: Cmessage) -> Cmessage:
        resp = Cmessage()
        recipient = req.getParam('recipient')
        amount = int(req.getParam('amount'))
        resp.setType('DATA')
        
        recipientuser = self._aliases[recipient]
        currentbalance = int(self._users[currentUser]._balance)
        print(currentbalance)
        if currentbalance < amount:
            resp.setType('ERRO')
            resp.addParam('message', 'balance is insufficient')
            return resp

        if recipient in self._aliases:
            
            currentbalance = currentbalance - amount
            currentbalance = str(currentbalance)

            with open("users.txt", "r") as f:
                lines = f.readlines()
                with open("users.txt", "w") as f:
                    for line in lines:
                        if self._users[currentUser]._username + ' ' + self._users[currentUser]._password + ' ' + self._users[currentUser]._alias + ' ' + self._users[currentUser]._balance not in line:
                            f.write(line)
                    f.write("\n" + self._users[currentUser]._username + ' ' + self._users[currentUser]._password + ' ' + self._users[currentUser]._alias + ' ' + currentbalance)

            patho = self._users[currentUser]._username + 'o.txt'
            with open(patho, 'a') as f:
                f.write("\n" + self._users[recipientuser]._alias + ' ' + str(amount))
            
            pathi = self._users[recipientuser]._username + 'i.txt'
            with open(pathi, 'a') as f:
                f.write(self._users[currentUser]._alias + ' ' + str(amount))

            nbalance = int(self._users[recipientuser]._balance) + amount
            nbalance = str(nbalance)

            with open("users.txt", "r") as f:
                lines = f.readlines()
                with open("users.txt", "w") as f:
                    for line in lines:
                        if self._users[recipientuser]._username + ' ' + self._users[recipientuser]._password + ' ' + self._users[recipientuser]._alias + ' ' + self._users[recipientuser]._balance not in line:
                            f.write(line)
                    f.write('\n' + self._users[recipientuser]._username + ' ' + self._users[recipientuser]._password + ' ' + self._users[recipientuser]._alias + ' ' + nbalance)
            
            resp.addParam('message', 'operation completed')
        
        else:
            resp.setType('ERRO')
            resp.addParam('message', 'recipient not found')
        return resp
                        
    def _process(self, req: Cmessage) -> Cmessage:
        m = self._route[req.getType()]
        return m(req)
    
    def shutdown(self):
        self.sproto.close()
        self.connected = False
        self._login = False
        
    def run(self):
        try:
            while (self.connected):
                #get message
                req = self.sproto.getMessage()
                self._debugPrint(req)
                
                # process request
                #resp = self._process(req)
                resp = self._process(req)
                self._debugPrint(resp)
    
                # send response
                self.sproto.putMessage(resp)
                
        except Exception as e:
            print(e)
            
        self.shutdown()
import socket
from cprotocol import Cprotocol
from cmessage import Cmessage
from request import Request

class Cclientops(object):
    '''
    classdocs
    '''


    def __init__(self):
        '''
        Constructor
        '''
        self._cproto = Cprotocol()
        self._login = False
        self._done = False
        self._debug = True
        self._targets = {}
        self._requesters = {}
        
    def _debugPrint(self, m: str):
        if self._debug:
            print(m)
            
    def _connect(self):
        commsoc = socket.socket()
        commsoc.connect(("localhost",4600))
        self._cproto = Cprotocol(commsoc)
            
    def _doLogin(self):
        u = input('username: ')
        p = input('password: ')

        global currentuser
        currentuser = u
        
        self._connect()
        
        req = Cmessage()
        req.setType('LGIN')
        req.addParam('username', u)
        req.addParam('password', p)
        self._cproto.putMessage(req)
        resp = self._cproto.getMessage()
        if resp:
            print(resp.getParam('message'))
            global currentAlias
            currentAlias = resp.getParam('alias')
            if resp.getType() == 'GOOD':
                self._login = True
            else:
                self._cproto.close()

    def _doRegister(self):
        u = input('username: ')
        p = input('password: ')
        a = input('alias: ')
        
        self._connect()
        req = Cmessage()
        req.setType('REGI')
        req.addParam('username', u)
        req.addParam('password', p)
        req.addParam('alias', a)
        self._cproto.putMessage(req)
        resp = self._cproto.getMessage()
        print(resp.getParam('message'))
        if resp.getType() == 'ERRO':
            self._cproto.close()
        else:
            path1 = u + "i.txt"
            path2 = u + "o.txt"

            with open(path1, 'w') as fp:
                pass
            with open(path2, 'w') as fp:
                pass
            self._login = False
        
    
    def _doLogout(self):
        req = Cmessage()
        req.setType('LOUT')
        self._cproto.putMessage(req)
        self._login = False
    

    
    
    def _shutdown(self):
        if self._login:
            self._doLogout()
            self._cproto.close()
        self._login = False
        self._done = True
            
    def _doMainMenu(self):
        menu = [' 1. Login', '2. Register', '99. Exit']
        choices = {'1': self._doLogin, '2': self._doRegister, '99': self._shutdown}
        print('\n'.join(menu))
        choice = input('>')
        if choice in choices:
            m = choices[choice]
            m()
        
    def _doPersonalMenu(self):
        menu = [' 1. Inbox', ' 2. Pay', '3. Request', '4. Balance', '5. Cancel', '6. Transactions', '7. Logout', '99. Exit', '>']
        choices = {'1': self._doInbox, '2': self._doPay, '3': self._doRequest, '4': self._doCheck,'5': self._doCancel, '6': self._doTransactions, '7': self._doLogout, '99': self._shutdown}
        print('\n'.join(menu))
        choice = input()
        if choice in choices:
            m = choices[choice]
            m()

    def _doCheck(self):
        req = Cmessage()
        req.setType('CHCK')
        self._cproto.putMessage(req)
        resp = self._cproto.getMessage()
        print("Your balance is: " + resp.getParam('message'))
        ans = input("Would you like to add to your wallet? Enter yes or no: ")
        if ans == "yes":
            amount = input("Please enter funds you would like to add: ")
            self._doAdd(amount)

    def _doInbox(self):
        with open('pending.txt') as f:
            for line in f:
                line = line.strip()
                values = line.split()
                pend = Request(values[0],values[1],values[2])
                self._targets[values[0]] = pend
        if currentAlias in self._targets:
            answer = input(self._targets[currentAlias]._requester + " has requsted $" + self._targets[currentAlias]._amount + " from you. Pay it? yes/no ")
            if answer == "yes":
                self._quickPay(self._targets[currentAlias]._requester, self._targets[currentAlias]._amount)
            else:
                with open("pending.txt", "r") as f:
                    lines = f.readlines()
                with open("pending.txt", "w") as f:
                    for line in lines:
                        if line.strip("\n") != self._targets[currentAlias]._target + ' ' + self._targets[currentAlias]._requester + ' ' + self._targets[currentAlias]._amount:
                            f.write(line)
                print("Request declined")
        else:
            print("Inbox is empty")

            """                with open("pending.txt", "r") as f:
                    lines = f.readlines()
                with open("pending.txt", "w") as f:
                    for line in lines:
                        if line.strip("\n") != self._targets[currentAlias]._target + ' ' + self._targets[currentAlias]._requester + ' ' + self._targets[currentAlias]._amount:
                            f.write(line)"""
        
    def _doCancel(self):
        with open('pending.txt') as f:
            for line in f:
                line = line.strip()
                values = line.split()
                pend = Request(values[0],values[1],values[2])
                self._requesters[values[1]] = pend
        if currentAlias in self._requesters:
            print("Here are all your pending requests: \n")
            print("Target: "+ self._requesters[currentAlias]._target + ", Amount Requested: " + self._requesters[currentAlias]._amount)
            answer = input("Would you like you cancel this request? yes/no ")
            if answer == "yes":
                with open("pending.txt", "r") as f:
                    lines = f.readlines()
                with open("pending.txt", "w") as f:
                    for line in lines:
                        if line.strip("\n") != self._requesters[currentAlias]._target + ' ' + self._requesters[currentAlias]._requester + ' ' + self._requesters[currentAlias]._amount:
                            f.write(line)
            print("Request cancelled")
        else:
            print("No pending requests")

    def _doTransactions(self):
        filepath1 = currentuser + "i.txt"
        filepath2 = currentuser + "o.txt"
        print("Here are your incoming transactions: ")
        with open(filepath1, 'r') as f:
            lines = f.readlines()
        with open(filepath1, "r") as f:
            for line in lines:
                print(line)
        print("Here are your outgoing transactions: ")
        with open(filepath2, 'r') as f:
            lines = f.readlines()
        with open(filepath2, "r") as f:
            for line in lines:
                print(line)
        answer = input("Would you like to request a refund? ")
        if answer == "yes":
            target = input("Please enter the alias of the person you paid included in the list: ")
            with open(filepath2) as f:
                for line in f:
                    if line != '\n':
                        line = line.strip()
                        values = line.split()
                        if target == values[0]:
                            req = Cmessage()
                            req.setType('RQST')
                            req.addParam('recipient', target)
                            req.addParam('amount', values[1])
                            self._cproto.putMessage(req)
                            resp = self._cproto.getMessage()
                            print(resp.getParam('message'))




    def _doRequest(self):
        recipient = input('Enter alias of the user you want to request from: ')
        amount = input('How much would you like you request? ')

        req = Cmessage()
        req.setType('RQST')
        req.addParam('recipient', recipient)
        req.addParam('amount', amount)
        self._cproto.putMessage(req)
        resp = self._cproto.getMessage()
        print(resp.getParam('message'))

    def _doAdd(self, deposit):
        req = Cmessage()
        req.setType('ADDF')
        req.addParam('amount', deposit)
        self._cproto.putMessage(req)

    def _quickPay(self, recipient, amount):
        req = Cmessage()
        req.setType('PAYR')
        req.addParam('recipient', recipient)
        req.addParam('amount', amount)
        self._cproto.putMessage(req)
        resp = self._cproto.getMessage()

        print(resp.getParam('message'))

    def _doPay(self):
        recipient = input('Enter alias of the user you want to pay: ')
        amount = input('How much would you like you pay? ')


        req = Cmessage()
        req.setType('PAYR')
        req.addParam('recipient', recipient)
        req.addParam('amount', amount)
        self._cproto.putMessage(req)
        resp = self._cproto.getMessage()

        print(resp.getParam('message'))

    
    def run(self):
        while (self._done == False):
            if (self._login == False):
                self._doMainMenu()
            else:
                self._doPersonalMenu()
        self._shutdown()
        
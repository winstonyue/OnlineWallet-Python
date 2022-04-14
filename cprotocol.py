'''
Created on Feb 24, 2022

@author: nigel
'''
import socket
from cmessage import Cmessage

class Cprotocol(object):
    '''
    classdocs
    '''
    BUFSIZE = 8196

    def __init__(self, s: socket=-1):
        '''
        Constructor
        '''
        self._sock = s
        
    def _loopRecv(self, size: int):
        data = bytearray(b" "*size)
        mv = memoryview(data)
        while size:
            rsize = self._sock.recv_into(mv,size)
            mv = mv[rsize:]
            size -= rsize
        return data
        
    def putMessage(self, m: Cmessage):
        data = m.marshal()
        self._sock.sendall(data.encode('utf-8'))
    
    def getMessage(self) -> Cmessage:
        try:
            m = Cmessage()
            size = int(self._loopRecv(4).decode('utf-8'))
            mtype = self._loopRecv(4).decode('utf-8')
            params = self._loopRecv(size).decode('utf-8')
            m.unmarshal(params)
            m.setType(mtype)
        except Exception:
            raise Exception('bad getMessage')
        else:
            return m
    
    def close(self):
        self._sock.close()
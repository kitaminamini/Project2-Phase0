#!/usr/bin/en/env python
import asyncore, socket
import logging
from cStringIO import StringIO
from urlparse import urlparse
import sys
import time as T


NumReq = 1000
concurrent = 115
url = "http://10.27.8.20:8080/"
Gcount = 0
global Gcount

start = T.time()



def make_request(req_type, what, details, ver="1.1"):
    NL = "\r\n"
    req_line = "{verb} {w} HTTP/{v}".format(
        verb=req_type, w=what, v=ver
    )
    details = [
        "{name}: {v}".format(name=n,v=v) for (n,v) in details.iteritems()
    ]
    detail_lines = NL.join(details)
    full_request = "".join([req_line, NL, detail_lines, NL, NL])
    return full_request
def parse_url(url, DEFAULT_PORT=80):
    parsed_url = urlparse(url)
    host, path, port = (parsed_url.hostname,
                        parsed_url.path,
                        parsed_url.port)
    if not port:
        port = DEFAULT_PORT
    return (host, path, port)


#HTTPClient inherits from asyncore.dispatcher
class HTTPClient(asyncore.dispatcher):
    ## Size of the buffer for each recv
    RECV_CHUNK_SIZE = 8192
 
    def __init__(self, request,host,port):
        asyncore.dispatcher.__init__(self)
        self.request = request
        self.host,self.port = host,port
        self.countread = 0
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect((host, port))
        (self.recvbuf, self.sendbuf) = (StringIO(), "")
        self.write(self.request)

 
    def write(self, data):
        
        """ Schedule to deliver data over the socket """
        self.sendbuf += data
 
    def handle_connect(self):
        pass
    def handle_close(self):
        global dic2
        global Gcount

        if Gcount < 1000:
            del dic2[self.getSocket()]
            a = HTTPClient(self.request,self.host,self.port)
            dic2[a.getSocket()] = a
            #print Gcount
            Gcount +=1
            
        else:
            self.close()
            totalTime = T.time() - start
            print str(totalTime) + "s"
            print str(Gcount/totalTime) + "n/s"
            sys.exit()
        self.close()
        
 
    def writeable(self):
        #print 'writeable'
        return len(self.sendbuf) > 0
 
    def handle_write(self):
        #print 'hwrite'
        bytes_sent = self.send(self.sendbuf)
        self.sendbuf = self.sendbuf[bytes_sent:]
 
    def handle_read(self):
        #print 'read'
        recv_bytes = self.recv(HTTPClient.RECV_CHUNK_SIZE)
        if self.countread == 0:
            pass
            #print recv_bytes[9:12]
        self.countread = 1

    def getSocket(self):
        return self.socket.fileno()


host, path, port = parse_url(url)
request = make_request('GET', path,
            {'Host': host,
             'Connection': 'close'}
        )
count = 0

def AmountOfConcurrentRequests(maxConc,request,host,port):
    dic = {}
    count = 0
    lst = []
    
    for i in range(maxConc):
        obj = HTTPClient(request,host,port)
        dic[obj.getSocket()] = obj
    global dic
    return dic
    


global dic2
dic2 =AmountOfConcurrentRequests(concurrent,request,host,port)

if __name__ == "__main__":
    asyncore.loop(map=dic2)


        




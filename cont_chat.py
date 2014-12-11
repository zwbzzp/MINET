#!usr/bin/env python
#_*_coding:utf-8 _*_
import socket
import threading
import select
import random
from format import Message

class Chat_Server(threading.Thread):
    def __init__(self, port, newMsgSignal):
        threading.Thread.__init__(self)
        self.running = True
        self.conn = None
        self.addr = None
        self.port = port
        self.newMsgSignal = newMsgSignal
        self.dialog = []

    def run(self):
        HOST = ''
        PORT = self.port
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST,PORT))
        s.listen(1)

        while self.running == True:
            clientsock, addr = s.accept()
            t = threading.Thread(target=self.recv, args=[clientsock])
            t.start()

    def recv(self, clientsock):
        while True: # Assume always alive
            msg = clientsock.recv(1024)
            lines = msg.split('\n')
            requestline = lines[0].split(' ')
            if 'P2PMESSAGE' in requestline:
                user = requestline[2]
                dialog = lines[3]
                time_cur = lines[1].split('HEADERNAME ')[1]
                print user, time_cur
                print dialog
                info = time_cur+' '+user+'\n'+dialog + '\n' + 'pri'
                self.newMsgSignal.emit(info)
                self.dialog.append(time_cur+' '+user+'\n'+dialog)
            # else:
            #     print 'Wrong Message Recieved'

    def retrieve_msg(self):
        if self.dialog != []:
            msg = self.dialog[-1]
            self.dialog = self.dialog[:-1]
        else: msg = None
        return msg

    def kill(self):
        self.running = 0
 
class Chat_Client(threading.Thread):
    def __init__(self, name):
        threading.Thread.__init__(self)
        self.running = 1
        self.connected_peers = {}
        self.msg = Message()
        self.name = name

    def run(self):
        pass

    def send(self, msg, name, host, port):
        if name not in self.connected_peers:
            self.connect(host, port, name)
        sock = self.connected_peers[name]
        dialog = self.msg.p2pMsg(self.name, msg)
        sock.send(dialog)
        
    def connect(self, host, port, name):
        # create a new socket and connect to dest
        # use name to identify the sock, name is for debug purpose
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.connect((host, port))
        self.connected_peers[name] = sock
        
    def kill(self):
        self.running = 0


# if __name__ == "__main__":
#     port = random.randint(10000, 60000)
#     print "Port:", port
#     chat_server = Chat_Server(port)
#     chat_client = Chat_Client('jane')
#     chat_server.start()
#     chat_client.start()

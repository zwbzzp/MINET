#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Base Server
 
import socket
import sys
import thread
import threading
import time
from format import Message
import traceback
host = ''
port = 54321

s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind((host, port))
s.listen(100)
print "Waiting for connections... "

global eve
eve = threading.Event()

global cancelSignal
mutex = threading.Lock()
mutex.acquire()
cancelSignal = ""
mutex.release()
global usernames
usernames = set()
global userips
userips = set()
global login
login = {}
global p2p
p2p = {}
global count
count = 0
global judge
judge = {}
judge[""] = 2
global time_beat
time_beat = {}
time_lock = threading.Lock()

def getTime():
    return int(time.strftime('%S',time.localtime(time.time())))
    pass

def sendMessageToAll(clientsock,client,name): #群聊监听用户发来信息
    global cancelSignal
    global judge
    global messageAll
    m = Message()
    while True:
        eve.clear()   # 若已设置标志则清除
        eve.wait()    # 调用wait方法
        if cancelSignal != "":
            if name == cancelSignal:
                # print "name" , name
                time.sleep(0.01)
                mutex.acquire()
                cancelSignal = ""
                mutex.release()
                eve.clear()
                clientsock.send(m.updateOnlineUsersMsg(name,judge[name]))#judge为判断上下线
                if judge[name] == 0:
                    clientsock.close()
                    thread.exit_thread()
                    pass
                pass
            pass
        #if judge[client2[0]] == 1:
        else:
            print messageAll
            clientsock.send(messageAll)
            pass
        time.sleep(0.05)
        pass

def Beat(name,clientsock):
    global usernames
    global userips
    global login
    global time_lock
    now = getTime()
    time_lock.acquire()
    last = time_beat[name]
    if now < last:
        now += 60
        pass
    time_lock.release()
    # print "now" , now
    # print "last", last
    while now - last < 10:
        time.sleep(1)
        time_lock.acquire()
        last = time_beat[name]
        now = getTime()
        if now < last:
            now += 60
            pass
        time_lock.release()
        # print "now" , now
        # print "last", last
        pass
    if name in usernames: #如果下线用户还在用户列表中，说明他是第一次下线，因为有可能是从心跳中剔除了名字
        #print "close"
        mutex.acquire()
        usernames.remove(name)#移除名字
        userips.remove((login[name])[0])#移除Ip地址
        del login[name]
        judge[name] = 0 #1为上线，0为下线
        #clientsock.close()
        global cancelSignal
        cancelSignal = name
        mutex.release()
        eve.set()
        pass
    thread.exit_thread()
    pass

def createClient(clientsock,client):
    global cancelSignal
    global judge
    global usernames
    global userips
    global login
    global p2p
    global time_beat
    m = Message()
    name = ""
    while True:
        try:
            reco = clientsock.recv(1024)
            print "close1"
        except socket.error, (value, message):
            print "close2"
            clientsock.close()
        if judge[name] == 0:
            print "close3"
            break
            pass
        rec_all = reco.split('\n')
        rec = rec_all[0].split(' ')
        for x in rec:
            print x
            pass
        if rec[0] != "CS1.1":
            #print "break"
            break
            pass
        if rec[1] == 'LOGIN': #用户登录
            if rec[2] in usernames:
                clientsock.send(m.loginServerMsg("0","有相同用户名用户"))
                #print m.loginServerMsg("0","有相同用户名用户")
                continue
                pass
            else:
                if client[0] in userips:
                    clientsock.send(m.loginServerMsg('0',"之前已登录"))
                    #print m.loginServerMsg('0',"之前已登录")
                    continue
                    pass
                else:
                    name = rec[2]
                    clientsock.send(m.loginServerMsg('1',""))
                    #print m.loginServerMsg('1',"")
                    mutex.acquire()
                    usernames.add(rec[2])
                    userips.add(client[0])
                    login[rec[2]] = client
                    p = rec_all[1].split(' ')
                    p2p[rec[2]] = [str(client[0]),p[1]]
                    time_beat[rec[2]] = getTime()
                    thread.start_new_thread(sendMessageToAll, (clientsock,client,rec[2]))
                    thread.start_new_thread(Beat, (rec[2],clientsock))
                    time.sleep(0.05)
                    cancelSignal = rec[2]
                    judge[rec[2]] = 1#1为上线，0为下线
                    mutex.release()
                    eve.set()
                pass
        if rec[1] == 'GETLIST':
            clientsock.send(m.getOnlineUserListMsg(login))
            #print m.getOnlineUserListMsg(login)
            pass
        if rec[1] == 'LEAVE': #群聊监听用户发来信息
            if rec[2] in usernames: #如果下线用户还在用户列表中，说明他是第一次下线，因为有可能是从心跳中剔除了名字
                usernames.remove(rec[2])#移除名字
                userips.remove(login[rec[2][0]])#移除Ip地址
                del login[rec[2]]
                judge[rec[2]] = 0 #1为上线，0为下线
                #mutex.release()
                #终结该用户的群聊线程
                mutex.acquire()
                cancelSignal = count
                mutex.release()
                clientsock.close()
                eve.set()
                break
                pass
            pass
        if rec[1] == 'MESSAGE':
            global messageAll
            mutex.acquire()
            messageAll = m.serverSendToUserMsg(rec[2],rec_all[3])
            mutex.release()
            eve.set()
            pass
        if rec[1] == 'P2PCONNECT':
            clientsock.send(m.ServerP2p(rec[2],p2p[rec[2]][0],p2p[rec[2]][1]))
            pass
        if rec[1] == 'BEAT':
            print "rec[2]",rec[2]
            time_lock.acquire()
            time_beat[rec[2]] = getTime()
            time_lock.release()
            pass
    
    thread.exit_thread()
    pass

while True: #主线程，用来监听client的连接
    mes = Message()
    clientsock, client = s.accept()
    request = clientsock.recv(1024)
    request_msg = request.split(" ")
    # print request_msg[0]
    # print request_msg[1]
    if request_msg[0] != "MINET":#判断是不是自己人，不是自己人的话就关闭SOCKET，重新进入监听状态
        clientsock.send('MIRO False\n')
        clientsock.close()
        continue;
    #如果是自己人
    clientsock.send(mes.handshakeMsg(request_msg[1]))
    thread.start_new_thread(createClient,(clientsock,client))
    pass
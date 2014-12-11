#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from time import ctime
CODEC = "ascii"

class Message(object):
    def __init__(self):
        self.msg_type = "handshake"
        self.msg = ''
    
    def handshakeMsg(self, hostname):
        self.msg = "MINET " + hostname + '\n'
        return self.msg
        
    def loginUserMsg(self, username, port):
        requestline = "CS1.1 LOGIN " + username + '\n'
        headerline = "Port " + str(port) + '\n'
        blank = '\n'
        
        self.msg = requestline + headerline + blank
        return self.msg
    
    def loginServerMsg(self, status, reason = None):
        requestline = "CS1.1 STATUS " + status + '\n' 
        headerline = "HEADERNAME " + ctime() + '\n'
        blank = '\n'
        
        if status == "0":
            entity = "Failed for " + reason
        else :
            entity = "Success"
        
        self.msg = requestline + headerline + blank + entity
        return self.msg
    
    def getOnlineUserListMsg(self, userinfos):
        requestline = "CS1.1 LIST\n"
        headerline = "HEADERNAME " + ctime() + '\n'
        blank = '\n'
        data = ''
        
        for users in userinfos.keys():
            ip = userinfos[users][0]
            port = userinfos[users][1]
            data += str(users) + ' ' + str(ip) + ' ' + str(port) + '\n'
        
        self.msg = requestline + headerline + blank + data + blank
        return self.msg
        
    def requestOnlineUsersMsg(self):
        requestline = "CS1.1 GETLIST\n"
        headerline = "HEADERNAME " + ctime() + '\n'
        blank = '\n'
        
        self.msg = requestline + headerline + blank
        return self.msg
        
    def updateOnlineUsersMsg(self, username, status):
        requestline = "CS1.1 UPDATE " + str(status) + ' ' + username + '\n'
        headerline = "HEADERNAME " + ctime() + '\n'
        blank = '\n'
        
        self.msg = requestline + headerline + blank
        return self.msg
    
    def userLeaveMsg(self, username):
        requestline = "CS1.1 LEAVE " + username + '\n'
        headerline = "HEADERNAME " + ctime() + '\n'
        blank = '\n'
        
        self.msg = requestline + headerline + blank
        return self.msg
    
    def userTalkToAllMsg(self, username, msg):
        requestline = "CS1.1 MESSAGE " + username + '\n'
        headerline = "HEADERNAME " + ctime() + '\n'
        blank = '\n'
        
        self.msg = requestline + headerline + blank + msg
        return self.msg
    
    def serverSendToUserMsg(self, username, msg):
        requestline = "CS1.1 CSMESSAGE " + username + '\n'
        headerline = "HEADERNAME " + ctime() + '\n'
        blank = '\n'
        
        self.msg = requestline + headerline + blank + msg
        return self.msg
    
    def sendBeatToServerMsg(self, username):
        requestline = "CS1.1 BEAT " + username + '\n'
        headerline = "HEADERNAME " + ctime() + '\n'
        blank = '\n'
        
        self.msg = requestline + headerline + blank
        return self.msg
    
    def p2pMsg(self, username, msg):
        requestline = "P2P.1 P2PMESSAGE " + username + '\n'
        headerline = "HEADERNAME " + ctime() + '\n'
        blank = '\n'
        
        self.msg = requestline + headerline + blank + msg
        return self.msg
    
    
    
    
        
    
    
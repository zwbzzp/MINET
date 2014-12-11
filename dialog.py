#!/usr/bin/env python
#_*_coding:utf-8 _*_
import sys
from cs_client import *
from PyQt4 import QtGui, QtCore
from time import ctime, time
from cont_chat import Chat_Server, Chat_Client
import threading
import thread
import signal
signal.signal(signal.SIGINT, signal.SIG_DFL)

class gridLayoutWindow(QtGui.QWidget, QtCore.QObject):
    newMsgSignal = QtCore.pyqtSignal(str)
    newPrvMsgSignal = QtCore.pyqtSignal(str)
    chatSwitch = QtCore.pyqtSignal()
    #初始话窗口，比如调用客户端代码，开启心跳和接受聊天内容线程
    #开启p2p服务端和客户端线程
    def __init__(self, client, parent):
        
        super(gridLayoutWindow, self).__init__()
        self.client = client
        self.client.userEnterTalkingRoom()
        self.peers = {}
        self.chatHistory = {"Group Chat":[]}
        self.currentChat = "Group Chat"
        self.parent = parent
        self.chatServer = Chat_Server(client.port, \
            self.newPrvMsgSignal)
        #print "client.port", client.port
        self.chatClient = Chat_Client(client.username)
        self.chatServer.start()
        self.chatClient.start()
        self.getUi()
    #界面函数
    def getUi(self):
        grid = QtGui.QGridLayout()
        grid.setSpacing(10)
        self.dialog = QtGui.QListWidget(self)
        self.user_talk = QtGui.QTextEdit(self)
        
        self.sendBtn = QtGui.QPushButton('send', self)
        self.sendBtn.resize(50, 30)
        btnGrid = QtGui.QGridLayout()
        spaceGrid = QtGui.QHBoxLayout()
        btnGrid.addLayout(spaceGrid, 0, 1, 1, 3)
        btnGrid.addWidget(self.sendBtn, 0, 4)
        
        self.sendBtn.clicked.connect(self.send_msg)
        
        self.users = QtGui.QListWidget(self)
        self.users.itemSelectionChanged.connect(self.chat_switch)
        self.onlineUserListControl()
        self.users.setMaximumWidth(100)
        self.add_group_chat_item()
        grid.addWidget(self.users, 0, 1, 8, 1)
        grid.addWidget(self.dialog, 0, 0, 6, 1)
        grid.addWidget(self.user_talk, 6, 0, 2, 1)
        grid.addLayout(btnGrid, 9, 0, 1, 1)
        
        self.setLayout(grid)
        self.resize(700, 500)
        self.center()
        
        self.setWindowTitle('Common talking room')
        p = self.palette()
        p.setColor(self.backgroundRole(), QtGui.QColor('white'))
        
        self.update = threading.Thread(target=self.updateDialogs)
        self.newMsgSignal.connect(self.show_msg)
        self.newPrvMsgSignal.connect(self.show_prv_msg)
        self.chatSwitch.connect(self.chat_switch)
        self.update.start()
        #self.show() 
    #在用户窗口栏加入其他用户的信息
    def add_group_chat_item(self):
        item = QtGui.QListWidgetItem()
        item.setText("Group Chat")
        self.users.addItem(item)
    #通过其他在线用户列表获取对等方
    def get_peers(self):
        namePacks = self.client.getOnlineUsers()
        for pck in namePacks:
            name, host, port = pck.split(' ')
            self.peers[name] = (host, int(port))
    #更新用户列表
    def refresh_user_list(self):
        namesToAdd = self.peers.keys()
        itemRange = range(self.users.count())
        itemRange.reverse()
        for i in itemRange:
            name = str(self.users.item(i).text())
            if name == "Group Chat": continue
            if name not in namesToAdd:
                self.users.takeItem(i)
            else:
                namesToAdd.remove(name)

        for name in namesToAdd:
            item = QtGui.QListWidgetItem()
            item.setText(name)
            self.users.addItem(item)
            
        #self.users.addStretch(1)
    #在群聊和私聊的信息交换
    def chat_switch(self):
        if self.users.currentItem() != None:
            self.currentChat = str(self.users.currentItem().text())
        user = self.currentChat
        if user not in self.chatHistory:
            assert type(user) == str
            self.chatHistory[user] = []

        self.dialog.clear()
        chatCache = self.chatHistory[user][-5:]
        for info in chatCache:
            self.insert_single_chat(info)
    #在窗口更新用户列表
    def onlineUserListControl(self):
        self.get_peers()
        self.refresh_user_list()
    #更新用户的聊天内容
    def updateDialogs(self):
        while self.client.protocol.connected:
            s = self.client.getMessage()
            if s == "talk":
                content = self.client.getRecentDialog()
                print "Content:", content, type(content)
                self.newMsgSignal.emit(content)
            else:
                self.onlineUserListControl()
    
    def center(self):   
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    #在用户列表中提取用户信息
    def extract_user_from_info(self, info):
        info = str(info)
        user = info.split("\n")[0].split(" ")[-1]
        return user
    #为每个聊天的用户添加一个聊天标志颜色
    def generate_icon(self, info):
        pixmap = QtGui.QPixmap(20, 20)
        user = self.extract_user_from_info(info)
        color = QtGui.QColor(hash(user)%255,
            (hash(user)/2)%255,
            (hash(user)/3)%255,
            255)
        pixmap.fill(color)
        icon = QtGui.QIcon(pixmap)
        return icon
    #添加一个私聊的信息
    def insert_single_chat(self, info):
        item = QtGui.QListWidgetItem()
        item.setText(info)
        item.setIcon(self.generate_icon(info))
        self.dialog.addItem(item)
    #用于切换窗口间的信息显示
    def show_msg(self, info):
        #user = self.currentChat
        #print info, type(info)
        info = str(info)
        infos = info.split('\n')
        info = infos[0] + '\n' + infos[1]
        if len(infos) != 3:
            user = 'Group Chat'
        else:
            user = infos[0].split()[-1]
        if user not in self.chatHistory:
            assert type(user) == str
            self.chatHistory[user] = []
        
       # print "self.client.username={}, self.currentChat={}, user={}".format(self.client.username, self.currentChat, user)
        if self.client.username == user:
            self.chatHistory[self.currentChat].append(info)
        else:
            self.chatHistory[user].append(info)
            
        if self.currentChat == user:
            self.insert_single_chat(info)
        else:
            self.chat_switch()
    #显示私聊内容
    def show_prv_msg(self, info):
        user = self.extract_user_from_info(info)
        if user not in self.chatHistory:
            assert type(user) == str
            self.chatHistory[user] = []

        print "history:"
        print self.chatHistory
        
        infos = str(info).split('\n')
        info = infos[0] + '\n' + infos[1]
        self.chatHistory[user].append(info)
        if self.currentChat == user:
            self.insert_single_chat(info)
        else:
            self.chat_switch()
    #发送消息
    def send_msg(self):
        msg = str(self.user_talk.toPlainText())

        name = self.currentChat
        if name == "Group Chat":
            self.client.send_to_all(msg)
        else:
            host, port = self.peers[name]
            self.chatClient.send(msg, name, host, int(port))
            info = ctime()+" "+self.client.username+"\n"+msg+'\n'+'pri'
            self.newMsgSignal.emit(info)
        self.user_talk.clear()
    #关闭窗口事件处理
    def closeEvent(self, event):
        self.client.leaveApplication()
        print 'Already Leave'
        event.accept()
        # self.exit()
        print self.parent

# def main():
  
#   app = QtGui.QApplication(sys.argv)
#   w = gridLayoutWindow()
#   sys.exit(app.exec_())
  
# if __name__ == '__main__':
#   main()

#!/usr/bin/env python
#_*_coding:utf-8 _*_
import sys
from cs_client import *
from PyQt4 import QtGui, QtCore
import random
from dialog import *

CODEC = 'utf-8'


class LoginWindow(QtGui.QWidget):

    def __init__(self):
        super(LoginWindow, self).__init__()
        self.port = random.randint(10000, 40000)
        self.client = ClientFactoryForCs(self.port)
        self.initUI()
    # 登录窗口初始化

    def initUI(self):

        name = QtCore.QString(u"用户名:")
        username = QtGui.QLabel(name)
        self.userEdit = QtGui.QLineEdit()
        #userEdit.setFixedSize(130, 30)

        grid = QtGui.QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(username, 1, 0)
        grid.addWidget(self.userEdit, 1, 1)

        title = QtGui.QLabel('MINET', self)
        title.setFont(QtGui.QFont('SansSerif', 20))
        title.resize(80, 40)
        title.move(115, 20)

        btn = QtGui.QPushButton('Enter', self)
        btn.setToolTip('enter the app')
        btn.resize(btn.sizeHint())
        btn.move(115, 150)
        btn.clicked.connect(self.sendData)

        self.setLayout(grid)

        self.resize(300, 200)
        self.center()
        self.setWindowTitle('login')
        self.setWindowIcon(QtGui.QIcon('icon.gif'))

        self.show()

    def center(self):
        qr = self.frameGeometry()
        cp = QtGui.QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())
    # 提示的窗口

    def showHint(self, s):
        QtGui.QMessageBox.question(self, 'Message',
                                   s, QtGui.QMessageBox.Yes |
                                   QtGui.QMessageBox.No, QtGui.QMessageBox.No)
    # 发送登录信息进入聊天窗口

    def sendData(self):
        s = self.userEdit.text()
        self.connect = self.client.startApplication()
        if self.connect == False:
            self.showHint('Network is not connected, please check!')
        else:
            if s:
                #self.showHint('name is ', )
                s = str(s)
                self.username = s
                self.login = self.client.userLogin(s)
                print self.login
                if self.login:
                    self.hide()
                    self.talk = gridLayoutWindow(self.client, self)
                    # self.client.userEnterTalkingRoom()
                    self.talk.show()
                else:
                    self.showHint('Name is already registered, change a name')
            else:
                self.showHint('Name cannot be empty!')


def main():
    app = QtGui.QApplication(sys.argv)
    w = LoginWindow()
    print "Here"
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()

from PyQt5 import QtCore, QtWebSockets, QtNetwork
from PyQt5.QtWidgets import QApplication

class DocumentServer(QtCore.QObject):
    def __init__(self, parent):
        super(QtCore.QObject, self).__init__(parent)
        self.clients = []
        print("server name: {}".format(parent.serverName()))
        self.server = QtWebSockets.QWebSocketServer(parent.serverName(), parent.secureMode(), parent)
        if self.server.listen(QtNetwork.QHostAddress.LocalHost, 1302):
            print('Listening: {}:{}:{}'.format(
                self.server.serverName(), self.server.serverAddress().toString(),
                str(self.server.serverPort())))
        else:
            print('error')
        self.server.acceptError.connect(self.onAcceptError)
        self.server.newConnection.connect(self.onNewConnection)
        self.clientConnection = None
        print(self.server.isListening())

    def onAcceptError(accept_error):
        print("Accept Error: {}".format(accept_error))

    def onNewConnection(self):
        print("onNewConnection")
        self.clientConnection = self.server.nextPendingConnection()
        self.clientConnection.textMessageReceived.connect(self.processTextMessage)

        self.clientConnection.textFrameReceived.connect(self.processTextFrame)

        self.clientConnection.binaryMessageReceived.connect(self.processBinaryMessage)
        self.clientConnection.disconnected.connect(self.socketDisconnected)

        print("newClient")
        self.clients.append(self.clientConnection)

    def processTextFrame(self, frame, is_last_frame):
        print("in processTextFrame")
        print("\tFrame: {} ; is_last_frame: {}".format(frame, is_last_frame))

    def processTextMessage(self, message):
        print("processTextMessage - message: {}".format(message))
        if self.clientConnection:
            for client in self.clients:
                # if client!= self.clientConnection:
                client.sendTextMessage(message)
            # self.clientConnection.sendTextMessage(message)

    def processBinaryMessage(self, message):
        print("b:",message)
        if self.clientConnection:
            self.clientConnection.sendBinaryMessage(message)

    def socketDisconnected(self):
        print("socketDisconnected")
        if self.clientConnection:
            self.clients.remove(self.clientConnection)
            self.clientConnection.deleteLater()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    serverObject = QtWebSockets.QWebSocketServer('My Socket', QtWebSockets.QWebSocketServer.NonSecureMode)
    server = MyServer(serverObject)
    serverObject.closed.connect(app.quit)
    app.exec_()
#The client uses some QTimer to call the required methods outside of the __init__method. I also added ping / pong methods to check the connection :

import sys

'''from PyQt5 import QtCore, QtWebSockets, QtNetwork
from PyQt5.QtCore import QUrl, QCoreApplication, QTimer
from PyQt5.QtWidgets import QApplication


class Client(QtCore.QObject):
    def __init__(self, parent):
        super().__init__(parent)'''
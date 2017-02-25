#!/usr/bin/env python3
# vim:fileencoding=utf-8

import sys
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebSockets import *
from PyQt5.QtNetwork import *
from PyQt5.QtWebChannel import *
from lxml import etree
from cylib import ui

class DocumentServer(QObject):
    def __init__(self,  parent=None):
        super(QObject, self).__init__(parent)
        self.server = QWebSocketServer('My Socket', QWebSocketServer.NonSecureMode)
        if self.server.listen(QHostAddress.LocalHost, 1302):
            print('Connected: '+self.server.serverName()+' : '+self.server.serverAddress().toString()+':'+str(self.server.serverPort()))
        else:
            print('error')
        self.server.newConnection.connect(self.onNewConnection)

        print(self.server.isListening())

    def onNewConnection(self):
        clientConnection = self.server.nextPendingConnection()
        clientConnection.disconnected.connect(clientConnection.deleteLater)
        print(self.sender())
        print("inside")
        clientConnection.textMessageReceived.connect(self.processTextMessage)
        clientConnection.binaryMessageReceived.connect(self.processBinaryMessage)
        #self.server.disconnect.connect(self.socketDisconnected)
        self.server.disconnected.connect(self.socketDisconnected)

    def processTextMessage(self,  message):
        print(message)

    def processBinaryMessage(self,  message):
        print(message)

    def socketDisconnected(self):
        print('out')

qwebchannel_js = QFile(':/qtwebchannel/qwebchannel.js')
if not qwebchannel_js.open(QIODevice.ReadOnly):
    raise SystemExit(
        'Failed to load qwebchannel.js with error: %s' %
        qwebchannel_js.errorString())
qwebchannel_js = bytes(qwebchannel_js.readAll()).decode('utf-8')

def client_script():
    script = QWebEngineScript()
    script.setSourceCode(qwebchannel_js)
    script.setName('xxx')
    script.setWorldId(QWebEngineScript.MainWorld)
    script.setInjectionPoint(QWebEngineScript.DocumentReady)
    script.setRunsOnSubFrames(True)
    return script

class WebPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, msg, linenumber, source_id):
        try:
            print('%s:%s: %s' % (source_id, linenumber, msg))
        except OSError:
            pass

    @pyqtSlot(str)
    def print(self, text):
        print('From JS:', text)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.form_widget = FormWidget(self)
        _widget = QWidget()
        _layout = QVBoxLayout(_widget)
        _layout.addWidget(self.form_widget)
        self.setCentralWidget(_widget)
        self.initToolbar()

    def initToolbar(self):
        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        editMenu = menubar.addMenu('&Edit')
        docMenu = menubar.addMenu('&Document')
        plotMenu = menubar.addMenu('&Plot')
        settingMenu = menubar.addMenu('&Setting')
        researchMenu = menubar.addMenu('&Research')
        helpMenu = menubar.addMenu('&Help')

        fileMenu = ui.initFileMenu(self, fileMenu)
        editMenu = ui.initEditMenu(self, editMenu)
        docMenu = ui.initDocMenu(self, docMenu)

        # self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('CyWriter')
        self.show()

class FormWidget(QWidget):
    def __init__(self, parent):
        super(FormWidget, self).__init__(parent)
        self.server = DocumentServer()
        self.grid = QGridLayout()
        self.document = {"tree": None, "currentChapter": 1, "chapterCount": 1}

        self.ctitlelabel = QLabel('Chapter Title')
        self.ctitle = QLineEdit()
        self.prevbutton = QPushButton("<")
        self.chapterlist = QPushButton("-")
        self.nextbutton = QPushButton(">")

        self.grid.addWidget(self.ctitlelabel, 1, 0)
        self.grid.addWidget(self.ctitle, 1, 1)

        self.grid.addWidget(self.prevbutton, 1, 2)
        self.prevbutton.setEnabled(False)
        self.prevbutton.clicked.connect(self.getPreviousChapter)

        self.grid.addWidget(self.chapterlist, 1, 3)
        self.chapterlist.clicked.connect(self.showChapterList)

        self.grid.addWidget(self.nextbutton, 1, 4)
        self.nextbutton.clicked.connect(self.getNextChapter)
        self.nextbutton.setEnabled(False)

        self.page = WebPage()
        self.view = QWebEngineView()
        self.view.setPage(self.page)
        self.page.profile().scripts().insert(client_script())
        self.channel = QWebChannel(self.page)
        self.page.setWebChannel(self.channel)
        self.channel.registerObject('bridge', self.page)
        self.view.load(QUrl('file:///home/family/Documents/Projects/CyWriter/index.html'))
        self.view.loadFinished.connect(self.openDocumentTemplate)

        self.grid.addWidget(self.view, 2, 0, 6, 6)

        self.setLayout(self.grid)

    def setChapter(self, chapterNumber):
        c1title = self.document["tree"].xpath("Chapters/Chapter[@sortOrder='" + str(chapterNumber) + "']/Title")[0]
        c1text = self.document["tree"].xpath(
            "Chapters/Chapter[@sortOrder='" + str(chapterNumber) + "']/Content/Text[@active='True']")[0]
        self.ctitle.setText(c1title.text.strip())
        self.document["currentChapter"] = chapterNumber
        self.toggleChapterButtons()
        self.server.processTextMessage(c1text)

    def getPreviousChapter(self):
        chapter = self.document["currentChapter"] - 1
        self.setChapter(chapter)

    def getNextChapter(self):
        chapter = self.document["currentChapter"] + 1
        self.setChapter(chapter)

    def showChapterList(self):
        print("Open chapter list here...")

    def toggleChapterButtons(self):
        self.nextbutton.setEnabled(True)
        self.prevbutton.setEnabled(True)
        print("Is current chapter >= chapter count?")
        print(self.document)
        if self.document["currentChapter"] == 1:
            self.prevbutton.setEnabled(False)
            print("No prev button")
        if self.document["currentChapter"] >= self.document["chapterCount"]:
            print("No next button")
            self.nextbutton.setEnabled(False)

    def openDocumentTemplate(self):
        self.document["tree"] = etree.parse("./cylib/basedoc.template.cyw")
        self.loadDocument()
        print(self.document)

    def loadDocument(self):
        self.document["chapterCount"] = len(self.document["tree"].xpath("Chapters/Chapter"))
        self.setChapter(1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    app.exec_()

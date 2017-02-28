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
from cylib import document
from DocumentServer import DocumentServer
from SocketClient import SocketClient

'''---------------------------
SETUP QWEBCHANNEL
This allows webchannel to be used on the client end of things (allows qwebchannel.js)
---------------------------'''
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


'''---------------------------
Main controller for the QWebEngine Page
---------------------------'''
class WebPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, msg, linenumber, source_id):
        try:
            print('%s:%s: %s' % (source_id, linenumber, msg))
        except OSError:
            pass

    @pyqtSlot(str)
    def print(self, text):
        print('From JS:', text)

'''---------------------------
MAIN WINDOW
This is the main window that opens when the
application is run
---------------------------'''
class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.form_widget = FormWidget(self)
        _widget = QWidget()
        _layout = QVBoxLayout(_widget)
        _layout.addWidget(self.form_widget)
        self.setCentralWidget(_widget)
        self.initToolbar()

    # ------------------------
    # Toolbar Initialization
    # This is in charge of the menus and menu items
    # ------------------------
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

'''---------------------------
FORM WIDGET
This is in charge of setting up all of the
items that appear in the main page and for
the sending and retrieving of data
---------------------------'''
class FormWidget(QWidget):
    def __init__(self, parent):
        super(FormWidget, self).__init__(parent)
        self.grid = QGridLayout()
        self.document = {"tree": None, "currentChapter": 1, "chapterCount": 1}
        self.doc = document.Document()
        self.socketclient = SocketClient(self)

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
        self._dialog = None

    # ------------------------
    # Sets the currently active chapter and displays it in the view
    # ------------------------
    def setChapter(self, chapterNumber):
        c1title = self.doc.getChapterTitle(chapterNumber)
        c1text = self.doc.getChapterText(chapterNumber)
        #c1title = self.document["tree"].xpath("Chapters/Chapter[@sortOrder='" + str(chapterNumber) + "']/Title")[0]
        #c1text = self.document["tree"].xpath(
        #   "Chapters/Chapter[@sortOrder='" + str(chapterNumber) + "']/Content/Text[@active='True']")[0]
        self.ctitle.setText(c1title)

        #self.document["currentChapter"] = chapterNumber
        self.doc.currentChapter = chapterNumber
        self.toggleChapterButtons()
        print("sending chapter data...")
        #self.server.acceptError.connect(self.onAcceptError)
        #self.server.newConnectiond.connect(self.onNewConnection)
        #self.server.processTextMessage(c1text.text)
        print(c1text)
        self.socketclient.send_message(c1text)

    # ------------------------
    # Moves backwards one chapter
    # ------------------------
    def getPreviousChapter(self):
        chapter = self.doc.currentChapter - 1
        #chapter = self.document["currentChapter"] - 1
        self.setChapter(chapter)

    # ------------------------
    # Moves forwards one chapter
    # ------------------------
    def getNextChapter(self):
        chapter = self.doc.currentChapter + 1
        #chapter = self.document["currentChapter"] + 1
        self.setChapter(chapter)

    #  ------------------------
    # Opens a chapter list to choose a chapter to view
    # ------------------------
    def showChapterList(self):
        if self._dialog is None:
            self._dialog = QDialog(self)

            clist = QComboBox(self._dialog)
            grid = QGridLayout(self._dialog)

            clist.InsertAtTop
            grid.addWidget(clist)
            self._dialog.setLayout(grid)
            self._dialog.resize(200, 100)
            self._dialog.show()

    # ------------------------
    # Determines what navigation buttons are enabled
    # ------------------------
    def toggleChapterButtons(self):
        self.nextbutton.setEnabled(True)
        self.prevbutton.setEnabled(True)
        print("Is current chapter >= chapter count?")
        #print(self.document)
        #if self.document["currentChapter"] == 1:
        if self.doc.currentChapter == 1:
            self.prevbutton.setEnabled(False)
            print("No prev button")
        #if self.document["currentChapter"] >= self.document["chapterCount"]:
        if self.doc.currentChapter >= self.doc.chapterCount:
            print("No next button")
            self.nextbutton.setEnabled(False)

    # ------------------------
    # Opens the template document
    # ------------------------
    def openDocumentTemplate(self):
        self.doc.tree = etree.parse("./cylib/basedoc.template.cyw")
        #self.document["tree"] = etree.parse("./cylib/basedoc.template.cyw")
        self.loadDocument()
        #print(self.document)

    # ------------------------
    # Sets up a newly-opened document
    # ------------------------
    def loadDocument(self):
        self.doc.chapterCount = self.doc.getChapterCount()
        #self.document["chapterCount"] = len(self.document["tree"].xpath("Chapters/Chapter"))
        self.setChapter(1)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    win = MainWindow()
    #server = SocketServer()
    win.form_widget.serverObject = QWebSocketServer('My Socket', QWebSocketServer.NonSecureMode)
    win.form_widget.server = DocumentServer(win.form_widget.serverObject)
    win.form_widget.serverObject.closed.connect(app.quit)

    win.show()
    app.exec_()

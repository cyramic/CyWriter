#!/usr/local/bin/python36
import sys
from PyQt5.Qt import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebSockets import *
from PyQt5.QtNetwork import *
from PyQt5.QtWebChannel import *
from cylib import ui
from lxml import etree
import base64

import time

class DateDialog(QDialog):
    def __init__(self, parent = None):
        super(DateDialog, self).__init__(parent)

        layout = QVBoxLayout(self)

        # nice widget for editing the date
        self.datetime = QDateTimeEdit(self)
        self.datetime.setCalendarPopup(True)
        self.datetime.setDateTime(QDateTime.currentDateTime())
        layout.addWidget(self.datetime)

        # OK and Cancel buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            Qt.Horizontal, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    # get current date and time from the dialog
    def dateTime(self):
        return self.datetime.dateTime()

    # static method to create the dialog and return (date, time, accepted)
    @staticmethod
    def getDateTime(parent = None):
        dialog = DateDialog(parent)
        result = dialog.exec_()
        date = dialog.dateTime()
        return (date.date(), date.time(), result == QDialog.Accepted)

class MainWindow(QMainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.form_widget = FormWidget(self)
        _widget = QWidget()
        _layout = QVBoxLayout(_widget)
        _layout.addWidget(self.form_widget)
        self.setCentralWidget(_widget)
        self.initUI()

    def initUI(self):               
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
        
        #self.setGeometry(300, 300, 300, 200)
        self.setWindowTitle('CyWriter')    
        self.show()
        
        
class WebPage(QWebEnginePage):
    def javaScriptConsoleMessage(self, level, msg, linenumber, source_id):
        try:
            print('%s:%s: %s' % (source_id, linenumber, msg))
        except OSError:
            pass

    @pyqtSlot(str)
    def print(self, text):
        print('From JS:', text)


class FormWidget(QWidget):
    def __init__(self, parent):
        super(FormWidget, self).__init__(parent)
        self.__controls()
        self.__layout()
        self.document = {"tree": None, "currentChapter": 1, "chapterCount": 1}

        self.wc_js = QFile(':/qtwebchannel/qwebchannel.js')
        if not self.wc_js.open(QIODevice.ReadOnly):
            raise SystemExit('Failed to load qwebchannel.js with error %s' % self.wc_js.errorSstring())
        self.wc_js = bytes(self.wc_js.readAll()).decode('utf-8')
        #time.sleep(5)
        #self.openDocumentTemplate()

    def __controls(self):
        #self.browser = QWebEngineView()
        #self.browser.load(QUrl('file:///home/family/Documents/Projects/CyWriter2/index.html'))
        self.ctitlelabel = QLabel('Chapter Title')
        self.ctitle = QLineEdit(self)
        self.prevbutton = QPushButton("<")
        self.chapterlist = QPushButton("-")
        self.nextbutton = QPushButton(">")
        self.webpage = WebPage()
        self.browser = QWebEngineView()
        self.browser.loadFinished.connect(self.openDocumentTemplate)
        self.browser.setPage(self.webpage)
        self.channel = QWebChannel(self.webpage)
        self.webpage.setWebChannel(self.channel)
        self.channel.registerObject('doceditor', self.channel)
        self.browser.load(QUrl('file:///home/family/Documents/Projects/CyWriter2/index.html'))
        #self.browser.page().mainFrame().javaScriptWindowObjectCleared.connect(self.populateJavaScriptWindowObject)
        #self.document = QTextEdit()

    def __layout(self):
        self.grid = QGridLayout()
        self.grid.addWidget(self.ctitlelabel,1, 0)
        self.grid.addWidget(self.ctitle, 1, 1)
        
        self.grid.addWidget(self.prevbutton, 1, 2)
        self.prevbutton.setEnabled(False)
        self.prevbutton.clicked.connect(self.getPreviousChapter)
        
        self.grid.addWidget(self.chapterlist, 1, 3)
        self.chapterlist.clicked.connect(self.showChapterList)
        
        self.grid.addWidget(self.nextbutton, 1, 4)
        self.nextbutton.clicked.connect(self.getNextChapter)
        self.nextbutton.setEnabled(False)
        self.grid.addWidget(self.browser, 2, 0, 6, 6)

        self.setLayout(self.grid)

        #self.getboundsbutton.clicked.connect(self.getBounds)

    def makeNewChapter(self, name, insertloc):
        print(name)

    @pyqtSlot()
    def saveText(self):
        #frame = self.browser.page().mainFrame()
        #documentText = frame.findFirstElement('#documenttext')
        documentText = self.browser.page().runJavaScript("$(tinyMCE.activeEditor.getContent({format : 'raw'}));")
        print(documentText)

    def openNewChapterDialog(self):
        #date, time, ok = DateDialog.getDateTime()
        d = QDialog()
        d.resize(300,110)
        l1 = QLabel("Chapter Name:", d)
        l1.move(10,10)
        cname = QLineEdit(d)
        cname.move(110,10)

        l1 = QLabel("Insert After:", d)
        l1.move(10, 40)
        cnum = QComboBox(d)
        cnum.addItem("Insert at beginning")
        chapterlist = self.document["tree"].xpath("Chapters/Chapter")
        for chapter in chapterlist:
            title = chapter.xpath("Title")[0].text
            if title.strip() == "" or title is None:
                cnum.addItem("After [Chapter "+str(chapter.attrib["sortOrder"])+"]")
            else:
                cnum.addItem("After ["+str(title.strip())+"]")
        cnum.move(110, 40)

        b1 = QPushButton("ok", d)
        b1.move(110, 75)

        #b1.clicked.connect(self.makeNewChapter(cname.text(), cnum.itemData(cnum.currentIndex())))
        d.setWindowTitle("New Chapter")
        d.setWindowModality(Qt.ApplicationModal)
        d.exec_()
        self.saveText()

    def setChapter(self, chapterNumber):
        c1title = self.document["tree"].xpath("Chapters/Chapter[@sortOrder='"+str(chapterNumber)+"']/Title")[0]
        c1text = self.document["tree"].xpath("Chapters/Chapter[@sortOrder='"+str(chapterNumber)+"']/Content/Text[@active='True']")[0]
        self.ctitle.setText(c1title.text.strip())
        self.document["currentChapter"] = chapterNumber
        self.toggleChapterButtons()
        #self.browser.page().runJavaScript('$(tinymce.get("documenttext").getBody()).html("'+str(c1text.text.strip())+'");', callback)
        #self.browser.page().runJavaScript('setText("'+(base64.b64encode(c1text.text.encode('utf8'))).decode('utf8')+'")')
        #self.channel.registerObject(QString("DocumentText"), c1text.text)
        
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
        #self.document["chapter"] = len(self.document["tree"].xpath("Chapters/Chapter"))
        #c1title = self.document["tree"].xpath("Chapters/Chapter[@sortOrder='1']/Title")[0]
        #c1text = self.document["tree"].xpath("Chapters/Chapter[@sortOrder='1']/Content/Text[@active='True']")[0]
        #self.ctitle.setText(c1title.text.strip())
        #self.document["currentChapter"] = 1
        #self.toggleChapterButtons()
        #self.browser.page().runJavaScript('$(tinymce.get("documenttext").getBody()).html("'+str(c1text.text.strip())+'");', callback)

    def loadDocument(self):
        self.document["chapterCount"] = len(self.document["tree"].xpath("Chapters/Chapter"))
        self.setChapter(1)

    def updateText(self):
        print("Hi")
    #def getBounds(self):
    #    self.browser.page().runJavaScript("document.getElementById('document').innerHTML", callback)

class MyServer(QObject):
    def __init__(self, parent):
        super(QObject, self).__init__(parent)
        self.clients = []
        self.server = QWebSocketServer(parent.serverName(), parent.secureMode(), parent)
        if self.server.listen(QHostAddress.LocalHost, 1302):
            print('Connected: '+self.server.serverName()+' : '+self.server.serverAddress().toString()+':'+str(self.server.serverPort()))
        else:
            print('error')
        self.server.newConnection.connect(self.onNewConnection)

        print(self.server.isListening())

    def onNewConnection(self):
        print("Connected")
        self.clientConnection = self.server.nextPendingConnection()
        self.clientConnection.textMessageReceived.connect(self.processTextMessage)

        self.clientConnection.binaryMessageReceived.connect(self.processBinaryMessage)
        self.clientConnection.disconnected.connect(self.socketDisconnected)

        self.clients.append(self.clientConnection)

    def processTextMessage(self, message):
        if (self.clientConnection):
            print(message)
            self.clientConnection.sendTextMessage(str(1))

    def processBinaryMessage(self,  message):
        if (self.clientConnection):
            print("Binary")
            self.clientConnection.sendBinaryMessage(message)

    def socketDisconnected(self):
        if (self.clientConnection):
            print("Disconnect")
            self.clients.remove(self.clientConnection)
            self.clientConnection.deleteLater()

def callback(result):
    print("Callback: "+str(result))

def main():
    import sys
    app = QApplication(sys.argv)    
    win = MainWindow()
    win.app = app
    serverObject = QWebSocketServer('My Socket', QWebSocketServer.NonSecureMode)
    win.server = MyServer(serverObject)
    serverObject.closed.connect(app.quit)
    win.show()
    app.exec_()

if __name__ == '__main__':
    sys.exit(main())

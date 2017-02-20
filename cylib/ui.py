from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtWebEngineWidgets import *
from PyQt5.QtWebSockets import *
from PyQt5.QtNetwork import *

from cylib import editfunctions
from cylib import filefunctions
from cylib import documentfunctions

def initFileMenu(self, fileMenu):
	newAction = QAction(QIcon('new.png'), '&New', self)
	newAction.setShortcut('Ctrl+N')
	newAction.setStatusTip('New Document')
	newAction.triggered.connect(lambda: filefunctions.newDialog(self))
	
	openAction = QAction(QIcon('open.png'), '&Open', self)
	openAction.setShortcut('Ctrl+O')
	openAction.setStatusTip('Open Document')
	openAction.triggered.connect(lambda: filefunctions.openDialog(self))
	
	saveAction = QAction(QIcon('save.png'), '&Save', self)
	saveAction.setShortcut('Ctrl+S')
	saveAction.setStatusTip('Save Document')
	saveAction.triggered.connect(filefunctions.saveDialog)
	
	exitAction = QAction(QIcon('exit.png'), '&Exit', self)        
	exitAction.setShortcut('Ctrl+Q')
	exitAction.setStatusTip('Exit application')
	exitAction.triggered.connect(qApp.quit)
	
	fileMenu.addAction(newAction)
	fileMenu.addAction(openAction)
	fileMenu.addAction(saveAction)
	fileMenu.addAction(exitAction)

	return fileMenu

def initEditMenu(self, editMenu):
	undoAction = QAction(QIcon('undo.png'), '&Undo', self)        
	undoAction.setShortcut('Ctrl+Z')
	undoAction.setStatusTip('Undo')
	undoAction.triggered.connect(editfunctions.undo)
	
	redoAction = QAction(QIcon('redo.png'), '&Redo', self)        
	redoAction.setShortcut('Ctrl+Y')
	redoAction.setStatusTip('Redo')
	redoAction.triggered.connect(editfunctions.redo)
	
	cutAction = QAction(QIcon('cut.png'), 'Cu&t', self)        
	cutAction.setShortcut('Ctrl+X')
	cutAction.setStatusTip('Cut')
	cutAction.triggered.connect(editfunctions.cut)
	
	copyAction = QAction(QIcon('copy.png'), '&Copy', self)        
	copyAction.setShortcut('Ctrl+C')
	copyAction.setStatusTip('Copy')
	copyAction.triggered.connect(editfunctions.copy)
	
	pasteAction = QAction(QIcon('paste.png'), '&Paste', self)        
	pasteAction.setShortcut('Ctrl+V')
	pasteAction.setStatusTip('Paste')
	pasteAction.triggered.connect(editfunctions.paste)
	
	preferencesAction = QAction(QIcon('preferences.png'), 'Preference&s', self)        
	preferencesAction.setStatusTip('Preferences')
	preferencesAction.triggered.connect(editfunctions.preferences)
	
	#edit = QTextEdit(self)
	#copyAction.triggered.connect(edit.copy)
	
	editMenu.addAction(undoAction)
	editMenu.addAction(redoAction)
	editMenu.addAction(cutAction)
	editMenu.addAction(copyAction)
	editMenu.addAction(pasteAction)
	editMenu.addAction(preferencesAction)
	
	return editMenu

def initDocMenu(self, docMenu):
	newChapterAction = QAction(QIcon('newchapter.png'), '&New Chapter', self)        
	newChapterAction.setShortcut('Ctrl+E')
	newChapterAction.setStatusTip('New Chapter')
	newChapterAction.triggered.connect(lambda: documentfunctions.newChapter(self))
	
	chapterBrowserAction = QAction(QIcon('chapterbrowser.png'), '&Chapter Browser', self)        
	chapterBrowserAction.setShortcut('Ctrl+B')
	chapterBrowserAction.setStatusTip('Chapter Browser')
	chapterBrowserAction.triggered.connect(documentfunctions.chapterBrowser)
	
	docMenu.addAction(newChapterAction)
	docMenu.addAction(chapterBrowserAction)

from PyQt5.QtWidgets import *
from lxml import etree

def newDialog(docobj):
	#Need to check to see if there is a currently opened document, and prompt to save if so before continuing
	docobj.form_widget.document["tree"] = etree.parse("./cylib/basedoc.template.cyw")
	docobj.form_widget.loadDocument()
	return True

def openDialog(docobj):
	fname = QFileDialog.getOpenFileName(None, 'Open file', '', "CyWriter Files (*.cyw);;All Files(*)")
	if fname[0]:
		docobj.form_widget.document["tree"] = etree.parse(fname[0])
		docobj.form_widget.loadDocument()
	return True
	
def saveDialog(self):
	return True

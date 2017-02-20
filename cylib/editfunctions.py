def undo(self):
	return True

def redo(self):
	return True

def cut(self):
	cb = QApplication.clipboard()
	cb.clear(mode=cb.Clipboard )
	cb.setText("Clipboard Text", mode=cb.Clipboard)

def copy(self):
	cb = QApplication.clipboard()
	cb.clear(mode=cb.Clipboard )
	cb.setText("Clipboard Text", mode=cb.Clipboard)

def paste(self):
	cb = QApplication.clipboard()
	cb.clear(mode=cb.Clipboard )
	cb.setText("Clipboard Text", mode=cb.Clipboard)

def preferences(self):
	return True

class Character:
	def __init__(self, firstname, lastname):
		self.firstname = firstname
		self.lastname = lastname
		self.gender = None
		self.haircolor = None
		self.eyecolor = None
		self.skincolor = None
		self.personalitydescription = ""
		self.meyersbriggs = {"decisions": None, "outer": None, "focus": None, "information": None, "testanswers": {}}

	def getWholeName(self):
		return self.firstname + " " + self.lastname


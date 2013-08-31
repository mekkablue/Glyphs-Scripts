#MenuTitle: Extract kern strings (1st character)
# -*- coding: utf-8 -*-
"""Analyze a textfile: look for certain characters and output all letter combinations occurring in the text file to the Macro Window."""

import GlyphsApp
import vanilla

myExcludeString = """ 
""" # default = space and return
 # default empty

def openFileDialog(message="Open plaintext file", filetypes=["txt"]):
	Panel = NSOpenPanel.openPanel().retain()
	Panel.setTitle_(message)
	Panel.setAllowsMultipleSelection_(True)
	Panel.setCanChooseFiles_(True)
	Panel.setCanChooseDirectories_(False)
	Panel.setResolvesAliases_(True)
	Panel.setAllowedFileTypes_(filetypes)
	pressedButton = Panel.runModalForTypes_(filetypes)
	if pressedButton == 1: # 1=OK, 0=Cancel
		return Panel.filenames()
	return None

def searchForKernPairs( kernChars=u"Ľľďť", text=u"""blabla""", excludeString="" ):
	myPairList = []

	for x in range(len(text)):
		if text[x] in kernChars and text[x+1] not in excludeString:
			mypair = text[x:x+2]
			if mypair not in myPairList:
				myPairList += [mypair]

	return sorted( myPairList )

class kernPairSearcher(object):
	
	def __init__(self):
		"""Window for entering characters you want to find kerning pairs for."""
		self.w = vanilla.Window( (400,200), "Extract kern string", minSize=(370,150) )
		self.w.textdescription = vanilla.TextBox((15, 12+2, -15, 14), "Search for kern pairs where these characters are on the left:", sizeStyle='small')
		self.w.kernChars = vanilla.EditText((15, 40, -15, -40), u"Ľľďť", sizeStyle='small')
		self.w.goButton = vanilla.Button((-80, -30, -15, 17), "Search", sizeStyle='small', callback=self.buttonCallback)
		self.w.center()
		self.w.open()
	
	def buttonCallback(self, sender):
		"""Runs when the Search button is pressed."""
		kernChars = self.w.kernChars.get() #.decode("utf-8")
		self.w.close()
		myFiles = openFileDialog()
		literature = u""

		if myFiles != None:
			for filepath in myFiles:
				f = open( filepath, mode='r' )
				print ">>> Reading:", f.name
				literature += f.read().decode('utf-8')
				f.close()

			myPairList = searchForKernPairs( kernChars=kernChars, text=literature, excludeString=myExcludeString )
			editTabString = " ".join( myPairList )
			
			try:
				# try to guess the frontmost window:
				Doc = Glyphs.currentDocument
				Doc.windowController().performSelectorOnMainThread_withObject_waitUntilDone_("addTabWithString:", editString, True)
				
			except:
				# if that fails, take the Macro Window:
				Glyphs.clearLog()
				Glyphs.showMacroWindow()
				print "Copy this paragraph and paste it into an Edit tab in text mode:"
				print editTabString
		
kernPairSearcher()
#MenuTitle: Extract kern strings (2nd character)
# -*- coding: utf-8 -*-
"""Analyze a textfile: look for certain characters and output all letter combinations occurring in the text file to the Macro Window."""

import GlyphsApp
import vanilla

myExcludeString = """ 
""" # default = space and return
 # default empty

def searchForKernPairs( kernChars=u"þð", text=u"""blabla""", excludeString="" ):
	myPairList = []
	
	for x in range(len(text)):
		if text[x] in kernChars and text[x+1] not in excludeString:
			mypair = text[x:x+2]
			if mypair not in myPairList:
				myPairList += [mypair]
	
	return sorted(myPairList, key=lambda pair: pair[::-1])

class kernPairSearcher(object):
	
	def __init__(self):
		"""Window for entering characters you want to find kerning pairs for."""
		self.w = vanilla.Window( (400,200), "Extract kern string", minSize=(370,150) )
		self.w.textdescription = vanilla.TextBox((15, 12+2, -15, 14), "Search for kern pairs where these characters are on the right:", sizeStyle='small')
		self.w.kernChars = vanilla.EditText((15, 40, -15, -40), u"þð", sizeStyle='small')
		self.w.goButton = vanilla.Button((-80, -30, -15, 17), "Search", sizeStyle='small', callback=self.buttonCallback)
		self.w.center()
		self.w.open()
	
	def buttonCallback(self, sender):
		"""Runs when the Search button is pressed."""
		kernChars = self.w.kernChars.get() #.decode("utf-8")
		self.w.close()
		myFiles = GetOpenFile(message="Open plaintext file", filetypes=["txt"])
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
				Doc = Glyphs.font.parent # document for current font
				Doc.windowController().performSelectorOnMainThread_withObject_waitUntilDone_("addTabWithString:", editTabString, True)
			except:
				# if that fails, take the Macro Window:
				Glyphs.clearLog()
				Glyphs.showMacroWindow()
				print "Copy this paragraph and paste it into an Edit tab in text mode:"
				print editTabString
		
kernPairSearcher()
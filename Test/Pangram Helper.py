#MenuTitle: Pangram Helper
# -*- coding: utf-8 -*-
__doc__="""
Helps you write pangrams by displaying which letters are still missing.
"""

import vanilla

fullAlphabet = "abcdefghijklmnopqrstuvwxyz"

class PangramHelper( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 300
		windowHeight = 160
		windowWidthResize  = 500 # user can resize width by this value
		windowHeightResize = 500 # user can resize height by this value
		self.w = vanilla.Window(
			( windowWidth, windowHeight ), # default window size
			"Pangram Helper", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.PangramHelper.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		self.w.missingLetters = vanilla.TextBox( (15, 12+2, -15, 14), "Missing: %s" % fullAlphabet.upper(), sizeStyle='small' )
		self.w.pangram = vanilla.TextEditor( (1, 40, -1, -45), "The quick brown fox jumps over the lazy dog.", checksSpelling=True, callback = self.updateMissingLetters)
		
		# Run Button:
		self.w.copyButton = vanilla.Button((-170, -20-15, -110, -15), "Copy", sizeStyle='regular', callback=self.PangramHelperMain )
		self.w.tabButton = vanilla.Button((-100, -20-15, -15, -15), "Open Tab", sizeStyle='regular', callback=self.PangramHelperMain )
		self.w.setDefaultButton( self.w.tabButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Pangram Helper' could not load preferences. Will resort to defaults"
		
		# Open window and focus on it:
		self.updateMissingLetters( None )
		self.w.open()
		self.w.pangram.selectAll()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.PangramHelper.pangram"] = self.w.pangram.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.PangramHelper.pangram", "The quick brown fox jumps over the lazy dog.")
			self.w.pangram.set( Glyphs.defaults["com.mekkablue.PangramHelper.pangram"] )
		except:
			return False
			
		return True
	
	def decompose(self, glyph):
		unicodeValue = "%04X" % ord(glyph)
		info = Glyphs.glyphInfoForUnicode(unicodeValue)
		if info.components:
			listOfCharacters = [c.unicharString() for c in info.components if c.category == "Letter"]
			return listOfCharacters
		return []
	
	def updateMissingLetters( self, sender ):
		currentTextEntry = unicode( Glyphs.defaults["com.mekkablue.PangramHelper.pangram"].lower() )
		containedBaseLetters = ""
		for thisLetter in currentTextEntry:
			if ord(thisLetter) > 191:
				components = self.decompose(thisLetter)
				containedBaseLetters += "".join(components)

		currentTextEntry += containedBaseLetters
		missingLetters = ""
		for thisLetter in fullAlphabet:
			if not thisLetter in currentTextEntry:
				missingLetters += thisLetter.upper()
		self.w.missingLetters.set( "Missing: %s" % missingLetters )
		
		
	def PangramHelperMain( self, sender ):
		try:
			myText = Glyphs.defaults["com.mekkablue.PangramHelper.pangram"]
			
			if myText:
				if sender == self.w.copyButton:
					myClipboard = NSPasteboard.generalPasteboard()
					myClipboard.declareTypes_owner_( [NSStringPboardType], None )
					myClipboard.setString_forType_( myText, NSStringPboardType )
				elif sender == self.w.tabButton:
					Glyphs.font.newTab(myText)
					self.w.close() # delete if you want window to stay open
			else:
				Message("Pangram Helper Error", "The entered text is empty.", OKButton=None)
			
			if not self.SavePreferences( self ):
				print "Note: 'Pangram Helper' could not write preferences."
			
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "Pangram Helper Error: %s" % e

PangramHelper()
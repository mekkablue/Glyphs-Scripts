#MenuTitle: Add PUA Unicode Values to Selected Glyphs
# -*- coding: utf-8 -*-
__doc__="""
Adds custom Unicode values to selected glyphs.
"""

import vanilla
import GlyphsApp

class CustomUnicode( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 320
		windowHeight = 95
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Custom Unicodes for Selected Glyphs", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.CustomUnicode.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		self.w.text_1 = vanilla.TextBox( (15, 12+2, 155, 14), "Unicode values starting at:", sizeStyle='small' )
		self.w.unicode = vanilla.EditText( (170, 12, -15, 15+3), "E700", sizeStyle = 'small')
		
		# Run Button:
		self.w.runButton = vanilla.Button((-80-15, -20-15, -15, -15), "Apply", sizeStyle='regular', callback=self.CustomUnicodeMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Add PUA Unicode Values to Selected Glyphs' could not load preferences. Will resort to defaults"
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.CustomUnicode.unicode"] = self.w.unicode.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			NSUserDefaults.standardUserDefaults().registerDefaults_(
				{
					"com.mekkablue.CustomUnicode.unicode": "E700"
				}
			)
			self.w.unicode.set( Glyphs.defaults["com.mekkablue.CustomUnicode.unicode"] )
		except:
			return False
			
		return True
	
	def checkUnicodeEntry( self, unicodeValue ):
		length = len(unicodeValue)
		if length < 4 or length > 5:
			return False
		
		for digit in unicodeValue:
			if not digit in "0123456789ABCDEF":
				return False
		
		return True
		
	def CustomUnicodeMain( self, sender ):
		try:
			enteredUnicode = self.w.unicode.get().upper()
			
			if self.checkUnicodeEntry(enteredUnicode):
				thisFont = Glyphs.font # frontmost font
				listOfSelectedGlyphs = [l.parent for l in thisFont.selectedLayers] # currently selected glyphs
				PUAcode = int(enteredUnicode,16) # calculate the integer number from the Unicode string
			
				# Report in Macro window:
				Glyphs.clearLog()
				print "Setting Unicode values:"
				
				# Apply Unicodes to selected glyphs:
				for thisGlyph in listOfSelectedGlyphs:
					unicodeValue = "%04X" % PUAcode
					thisGlyph.setUnicode_( unicodeValue )
					print "  %s: %s" % (unicodeValue, thisGlyph.name)
					PUAcode += 1
				
				# Try to save prefs:
				if not self.SavePreferences( self ):
					print "Note: 'Add PUA Unicode Values to Selected Glyphs' could not write preferences."
			
				self.w.close() # closes window
			else:
				Message("Unicode Error", "The Unicode value entered does not seem to be a valid UTF16 codepoint. It must be a four- or five-digit hexadecimal number, i,e, contain only 0123456789ABCDEF.", OKButton=None)
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "Add PUA Unicode Values to Selected Glyphs Error:\n%s" % e

CustomUnicode()
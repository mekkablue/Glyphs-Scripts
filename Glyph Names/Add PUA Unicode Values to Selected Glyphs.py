#MenuTitle: Add PUA Unicode Values to Selected Glyphs
# -*- coding: utf-8 -*-
__doc__="""
Adds custom Unicode values to selected glyphs.
"""

import vanilla


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
		self.w.unicode = vanilla.EditText( (170, 12, -15, 15+3), "E700", sizeStyle = 'small', callback=self.sanitizeEntry)
		
		# Run Button:
		self.w.runButton = vanilla.Button((-80-15, -20-15, -15, -15), "Apply", sizeStyle='regular', callback=self.CustomUnicodeMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Add PUA Unicode Values to Selected Glyphs' could not load preferences. Will resort to defaults"
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def sanitizeEntry(self, sender):
		enteredUnicode = sender.get().upper().strip()
		for digit in enteredUnicode:
			if not digit in "0123456789ABCDEF":
				enteredUnicode = enteredUnicode.replace(digit,"")
		sender.set(enteredUnicode)
		self.SavePreferences(sender)
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.CustomUnicode.unicode"] = self.w.unicode.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.CustomUnicode.unicode", "E700")
			self.w.unicode.set( Glyphs.defaults["com.mekkablue.CustomUnicode.unicode"] )
		except:
			return False
			
		return True
	
	def checkUnicodeEntry( self, unicodeValue ):
		length = len(unicodeValue)
		if length < 4 or length > 5:
			print "ERROR: Entry has %i digits and therefore an invalid length. UTF-16 values must contain 4 or 5 hexadecimal digits." % length
			return False
		
		# after sanitization, this will probably never be accessed anymore:
		for digit in unicodeValue:
			allDigitsValid = True
			if not digit in "0123456789ABCDEF":
				print "ERROR: Found '%s' in entry. Not a valid hex digit." % digit
				allDigitsValid = False
		
		return allDigitsValid
		
	def CustomUnicodeMain( self, sender ):
		try:
			# just to be safe:
			self.sanitizeEntry(self.w.unicode)
			enteredUnicode = Glyphs.defaults["com.mekkablue.CustomUnicode.unicode"]
			
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
				Message("The entered code is not a valid Unicode value. It must be either a four- or five-digit hexadecimal number. Find more details in the Macro Window.", "Unicode Error", OKButton=None)
				Glyphs.showMacroWindow()
				
		except Exception, e:
			# brings macro window to front and reports error:
			Message("The following error occurred (more details in the Macro Window): %s"%e, "Script Error", OKButton=None)
			import traceback
			print traceback.format_exc()
			Glyphs.showMacroWindow()

CustomUnicode()
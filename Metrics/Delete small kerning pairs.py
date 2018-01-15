#MenuTitle: Delete Small Kerning Pairs
# -*- coding: utf-8 -*-
__doc__="""
Specify a kerning value, and every kerning in the current master smaller than that will be removed.
"""

import vanilla


def nameForID( Font, ID ):
	"""Return the name of a group or glyph for a given kerning ID."""
	try:
		if ID[0] == "@": # is a group
			return ID
		else: # is a glyph
			return Font.glyphForId_( ID ).name
	except Exception as e:
		raise e

class DeleteSmallKerningPairs( object ):
	def __init__( self ):
		# Window 'self.w':
		offset = 10
		line = 20
		
		windowWidth  = 325
		windowHeight = 2*offset+7*line
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Delete Small Kerning Pairs", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.DeleteSmallKerningPairs.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		self.w.text_1 = vanilla.TextBox( (15-1, offset+2, -15, line), "In the current font master, delete all pairs smaller than:", sizeStyle='small' )
		self.w.howMuch = vanilla.EditText((15-1, offset+line+1, -15, line), "10", sizeStyle='small', callback=self.SavePreferences)
		
		self.w.text_2 = vanilla.TextBox( (15-1, offset*2+line*2+2, -15, line), "Only delete:", sizeStyle='small' )
		self.w.positive = vanilla.CheckBox( (25, offset*2+line*3, -15, line), "Positive,", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.zero = vanilla.CheckBox( (90, offset*2+line*3, -15, line), "zero, and", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.negative = vanilla.CheckBox( (162, offset*2+line*3, -15, line), "negative pairs", value=True, callback=self.SavePreferences, sizeStyle='small' )

		self.w.keepWindow = vanilla.CheckBox( (25, offset*2+line*4, -15, line), "Keep window open", value=True, callback=self.SavePreferences, sizeStyle='small' )
		
		# Run Button:
		self.w.runButton = vanilla.Button((-80-15, -20-15, -15, -15), "Remove", sizeStyle='regular', callback=self.DeleteSmallKerningPairsMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Delete Small Kerning Pairs' could not load preferences. Will resort to defaults"
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.DeleteSmallKerningPairs.howMuch"] = str(float(self.w.howMuch.get()))
			Glyphs.defaults["com.mekkablue.DeleteSmallKerningPairs.positive"] = str(int(self.w.positive.get()))
			Glyphs.defaults["com.mekkablue.DeleteSmallKerningPairs.zero"] = str(int(self.w.zero.get()))
			Glyphs.defaults["com.mekkablue.DeleteSmallKerningPairs.negative"] = str(int(self.w.negative.get()))
			Glyphs.defaults["com.mekkablue.DeleteSmallKerningPairs.keepWindow"] = str(int(self.w.keepWindow.get()))
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			NSUserDefaults.standardUserDefaults().registerDefaults_(
				{
					"com.mekkablue.DeleteSmallKerningPairs.howMuch": "10",	
					"com.mekkablue.DeleteSmallKerningPairs.positive": "1",	
					"com.mekkablue.DeleteSmallKerningPairs.zero": "0",	
					"com.mekkablue.DeleteSmallKerningPairs.negative": "1",	
					"com.mekkablue.DeleteSmallKerningPairs.keepWindow": "1"
				}
			)
			self.w.howMuch.set( Glyphs.defaults["com.mekkablue.DeleteSmallKerningPairs.howMuch"] )
			self.w.positive.set( bool(Glyphs.defaults["com.mekkablue.DeleteSmallKerningPairs.positive"]) )
			self.w.zero.set( bool(Glyphs.defaults["com.mekkablue.DeleteSmallKerningPairs.zero"]) )
			self.w.negative.set( bool(Glyphs.defaults["com.mekkablue.DeleteSmallKerningPairs.negative"]) )
			self.w.keepWindow.set( bool(Glyphs.defaults["com.mekkablue.DeleteSmallKerningPairs.keepWindow"]) )
		except:
			return False
			
		return True

	def DeleteSmallKerningPairsMain( self, sender ):
		try:
			# brings macro window:
			Glyphs.showMacroWindow()
			
			# read the user entry:
			shouldRemovePositive = self.w.positive.get()
			shouldRemoveZero = self.w.zero.get()
			shouldRemoveNegative = self.w.negative.get()
			keepWindowOpen = self.w.keepWindow.get()
			try:
				# convert to positive decimal number:
				maxKernValue = abs(float( self.w.howMuch.get() ))
			except:
				# bad entry, default to 0 (could be left empty for zero pairs only):
				maxKernValue = 0.0
			
			# set the variables:
			thisFont = Glyphs.font # frontmost font
			thisFontMaster = thisFont.selectedFontMaster # active master
			thisFontMasterID = thisFontMaster.id # active master ID
			thisFontMasterKernDict = thisFont.kerning[thisFontMasterID] # kerning dictionary

			if ((shouldRemovePositive or shouldRemoveNegative) and maxKernValue) or shouldRemoveZero:
				willRemove = "kernings smaller than %i" % maxKernValue
				if shouldRemoveZero and ((not maxKernValue) or (not shouldRemoveNegative and not shouldRemovePositive)):
					willRemove = "zero kernings"
				print "Deleting %s in %s %s..." % (willRemove, thisFont.familyName, thisFontMaster.name)
				
				# collect pairs to be removed:
				kernpairsToBeRemoved = []
				countZero = 0
				countPositive = 0
				countNegative = 0
				for leftGlyphID in thisFontMasterKernDict.keys():
					for rightGlyphID in thisFontMasterKernDict[ leftGlyphID ].keys():
						kerningValue = thisFontMasterKernDict[ leftGlyphID ][ rightGlyphID ]
						leftName  = nameForID( thisFont, leftGlyphID )
						rightName = nameForID( thisFont, rightGlyphID )
					
						if shouldRemoveZero and kerningValue == 0.0:
							kernpairsToBeRemoved.append( (leftName, rightName) )
							countZero += 1
						elif shouldRemovePositive and 0.0 < kerningValue < maxKernValue:
							kernpairsToBeRemoved.append( (leftName, rightName) )
							countPositive += 1
						elif shouldRemoveNegative and 0.0 > kerningValue > -maxKernValue:
							kernpairsToBeRemoved.append( (leftName, rightName) )
							countNegative += 1
				
				# remove the pairs:
				for thisKernPair in kernpairsToBeRemoved:
					leftSide = thisKernPair[0]
					rightSide = thisKernPair[1]
					thisFont.removeKerningForPair( thisFontMasterID, leftSide, rightSide )
				print "   Removed %i kerning pairs:" % len(kernpairsToBeRemoved)
				print "   %i negative pairs" % countNegative
				print "   %i zero pairs" % countZero
				print "   %i positive pairs" % countPositive
				print "Done."
			else:
				print "Note: No kerning removed, because no options were picked."
			
			if not self.SavePreferences( self ):
				print "Note: 'Delete Small Kerning Pairs' could not write preferences."
			
			if not keepWindowOpen:
				self.w.close()
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "Delete Small Kerning Pairs Error: %s" % e

# clear macro window log:
Glyphs.clearLog()

# execute GUI:
DeleteSmallKerningPairs()
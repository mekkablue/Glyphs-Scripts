#MenuTitle: New Tab with Large Kerning Pairs
# -*- coding: utf-8 -*-
__doc__="""
Shows all Kerning Pairs beyond a threshold value.
"""

import vanilla

class ShowLargeKerningPairs( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 300
		windowHeight = 140
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Show Large Kerning Pairs in this Master", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.ShowLargeKerningPairs.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		self.w.text_1 = vanilla.TextBox( (15-1, 12+2, 190, 14), "New tab with kern pairs beyond:", sizeStyle='small' )
		self.w.threshold = vanilla.EditText( (190, 12-1, -15, 20), "100", sizeStyle = 'small')
		self.w.positive = vanilla.CheckBox( (15, 40, -15, 20), "Positive pairs", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.negative = vanilla.CheckBox( (15, 60, -15, 20), "Negative pairs", value=True, callback=self.SavePreferences, sizeStyle='small' )
		
		
		# Run Button:
		self.w.runButton = vanilla.Button((-80-15, -20-15, -15, -15), "Open Tab", sizeStyle='regular', callback=self.ShowLargeKerningPairsMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Show Large Kerning Pairs' could not load preferences. Will resort to defaults"
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			if sender == self.w.positive and self.w.positive.get() == 0:
				self.w.negative.set( 1 )
			elif sender == self.w.negative and self.w.negative.get() == 0:
				self.w.positive.set( 1 )

			Glyphs.defaults["com.mekkablue.ShowLargeKerningPairs.negative"] = self.w.negative.get()
			Glyphs.defaults["com.mekkablue.ShowLargeKerningPairs.positive"] = self.w.positive.get()
			Glyphs.defaults["com.mekkablue.ShowLargeKerningPairs.threshold"] = self.w.threshold.get()
			
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			NSUserDefaults.standardUserDefaults().registerDefaults_(
				{
					"com.mekkablue.ShowLargeKerningPairs.negative": "1",
					"com.mekkablue.ShowLargeKerningPairs.positive": "1",
					"com.mekkablue.ShowLargeKerningPairs.threshold": "100"
				}
			)
			self.w.negative.set( Glyphs.defaults["com.mekkablue.ShowLargeKerningPairs.negative"] )
			self.w.positive.set( Glyphs.defaults["com.mekkablue.ShowLargeKerningPairs.positive"] )
			self.w.threshold.set( Glyphs.defaults["com.mekkablue.ShowLargeKerningPairs.threshold"] )
		except:
			return False
			
		return True

	def ShowLargeKerningPairsMain( self, sender ):
		try:
			thisFont = Glyphs.font # frontmost font
			thisMaster = thisFont.selectedFontMaster
			thisKerning = thisFont.kerning[thisMaster.id]
			
			negative = bool(Glyphs.defaults["com.mekkablue.ShowLargeKerningPairs.negative"])
			positive = bool(Glyphs.defaults["com.mekkablue.ShowLargeKerningPairs.positive"])

			try:
				# validate user input:
				threshold = int( Glyphs.defaults["com.mekkablue.ShowLargeKerningPairs.threshold"] )
			except Exception as e:
				import traceback
				print traceback.format_exc()
				Message("Threshold Error", "The threshold value you supplied could not be read as an integer value.", OKButton=None)
				threshold = 0
			
			if threshold:
				# gather kerning groups:
				exportingGlyphs = [ g for g in thisFont.glyphs if g.export ]
				leftGroups = {}
				rightGroups = {}
				for thisGlyph in exportingGlyphs:
					if not thisGlyph.leftKerningGroup in leftGroups:
						leftGroups[thisGlyph.leftKerningGroup] = thisGlyph.name
					if not thisGlyph.rightKerningGroup in rightGroups:
						rightGroups[thisGlyph.rightKerningGroup] = thisGlyph.name
				
				tabText = ""
				for leftKey in thisKerning:
					for rightKey in thisKerning[leftKey]:
						if (positive and thisKerning[leftKey][rightKey] > threshold) or (negative and thisKerning[leftKey][rightKey] < -threshold):
							# add two glyphs and a space to the tabText
							leftGlyphName = None
							rightGlyphName = None
							if leftKey[0] == "@":
								# leftKey is a group name like "@MMK_L_y"
								groupName = leftKey[7:]
								if groupName in rightGroups:
									leftGlyphName = rightGroups[groupName]
							else:
								# leftKey is a glyph ID like "59B740DA-A4F4-43DF-B6DD-1DFA213FFFE7"
								leftGlyph = thisFont.glyphForId_(leftKey)
								leftGlyphName = leftGlyph.name
						
							if rightKey[0] == "@":
								# rightKey is a group name like "@MMK_R_y"
								groupName = rightKey[7:]
								if groupName in leftGroups:
									rightGlyphName = leftGroups[groupName]
							else:
								# rightKey is a glyph ID like "59B740DA-A4F4-43DF-B6DD-1DFA213FFFE7"
								rightGlyph = thisFont.glyphForId_(rightKey)
								rightGlyphName = rightGlyph.name
							
							if leftGlyphName and rightGlyphName:
								tabText += "/%s/%s  " % (leftGlyphName,rightGlyphName)
							
				if tabText:
					# opens new Edit tab:
					thisFont.newTab( tabText[:-2] )
				else:
					Message("No Excess Kerning Found", "No kerning found that exceeds the threshold in this master. Or perhaps you have empty groups.", OKButton=None)
					
			
			if not self.SavePreferences( self ):
				print "Note: 'Show Large Kerning Pairs' could not write preferences."
			
			# self.w.close() # delete if you want window to stay open
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "Show Large Kerning Pairs Error: %s" % e
			import traceback
			print traceback.format_exc()

ShowLargeKerningPairs()
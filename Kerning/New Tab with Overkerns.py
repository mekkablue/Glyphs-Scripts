#MenuTitle: New Tab with Overkerned Pairs
# -*- coding: utf-8 -*-
__doc__="""
Asks a threshold percentage, and opens a new tab with all kern pairs going beyond the width threshold.
"""

import vanilla

class FindOverkerns( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 350
		windowHeight = 135
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Find Negative Overkerns in This Master", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.FindOverkerns.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		self.w.text_1 = vanilla.TextBox( (15-1, 12+2, 220, 14), "Open tab with kerns beyond threshold:", sizeStyle='small' )
		self.w.threshold = vanilla.EditText( (225, 12-1, -15, 20), "40", sizeStyle = 'small')
		self.w.text_2 = vanilla.TextBox( (15-1, 12+25, -15, 14), "(Maximum percentage of letter widths that may be kerned.)", sizeStyle='small' )
		self.w.limitToExportingGlyphs = vanilla.CheckBox( (15, 12+50, 150, 20), "Limit to exporting glyphs", value=True, callback=self.SavePreferences, sizeStyle='small' )
		
		# Run Button:
		self.w.runButton = vanilla.Button((-100-15, -20-15, -15, -15), "Open Tab", sizeStyle='regular', callback=self.FindOverkernsMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print "Note: 'Find Overkerns' could not load preferences. Will resort to defaults"
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.FindOverkerns.threshold"] = self.w.threshold.get()
			Glyphs.defaults["com.mekkablue.FindOverkerns.limitToExportingGlyphs"] = self.w.limitToExportingGlyphs.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.FindOverkerns.threshold", "40")
			Glyphs.registerDefault("com.mekkablue.FindOverkerns.limitToExportingGlyphs", True)
			self.w.threshold.set( Glyphs.defaults["com.mekkablue.FindOverkerns.threshold"] )
			self.w.limitToExportingGlyphs.set( Glyphs.defaults["com.mekkablue.FindOverkerns.limitToExportingGlyphs"] )
		except:
			return False
			
		return True

	def FindOverkernsMain( self, sender ):
		try:
			# retrieve user entry:
			thresholdFactor = None
			try:
				thresholdFactor = float( Glyphs.defaults["com.mekkablue.FindOverkerns.threshold"] )/100.0
			except:
				Message(title="Value Error", message="The threshold value you entered is invalid", OKButton="Oops")
			
			limitToExportingGlyphs = bool( Glyphs.defaults["com.mekkablue.FindOverkerns.limitToExportingGlyphs"] )
			
			# continuer if user entry is valid: 
			if not thresholdFactor is None:
				thisFont = Glyphs.font # frontmost font
				thisMaster = thisFont.selectedFontMaster # current master
				masterKerning = thisFont.kerning[thisMaster.id] # kerning dictionary
				tabText = "" # the text appearing in the new tab
			
				# collect minimum widths for every kerning group:
				leftGroupMinimumWidths = {}
				leftGroupNarrowestGlyphs = {}
				rightGroupMinimumWidths = {}
				rightGroupNarrowestGlyphs = {}
				if limitToExportingGlyphs:
					theseGlyphs = [g for g in thisFont.glyphs if g.export]
				else:
					theseGlyphs = thisFont.glyphs
				for thisGlyph in theseGlyphs:
					thisLayer = thisGlyph.layers[thisMaster.id]
					
					# left side of the glyph (= right side of kern pair)
					if thisGlyph.leftKerningGroup:
						if thisGlyph.leftKerningGroup in leftGroupMinimumWidths:
							if thisLayer.width < leftGroupMinimumWidths[thisGlyph.leftKerningGroup]:
								leftGroupMinimumWidths[thisGlyph.leftKerningGroup] = thisLayer.width
								leftGroupNarrowestGlyphs[thisGlyph.leftKerningGroup] = thisGlyph.name
						else:
							leftGroupMinimumWidths[thisGlyph.leftKerningGroup] = thisLayer.width
							leftGroupNarrowestGlyphs[thisGlyph.leftKerningGroup] = thisGlyph.name
							
					# right side of the glyph (= left side of kern pair)
					if thisGlyph.rightKerningGroup:
						if thisGlyph.rightKerningGroup in rightGroupMinimumWidths:
							if thisLayer.width < rightGroupMinimumWidths[thisGlyph.rightKerningGroup]:
								rightGroupMinimumWidths[thisGlyph.rightKerningGroup] = thisLayer.width
								rightGroupNarrowestGlyphs[thisGlyph.rightKerningGroup] = thisGlyph.name
						else:
							rightGroupMinimumWidths[thisGlyph.rightKerningGroup] = thisLayer.width
							rightGroupNarrowestGlyphs[thisGlyph.rightKerningGroup] = thisGlyph.name
			
				# go through kern values and collect them in tabText:
				for leftKey in masterKerning:
					for rightKey in masterKerning[leftKey]:
						kernValue = masterKerning[leftKey][rightKey]
						if kernValue < 0:
							leftWidth = None
							rightWidth = None
							
							try:
								# collect widths for comparison
								if leftKey[0] == "@":
									# leftKey is a group name like "@MMK_L_y"
									groupName = leftKey[7:]
									leftWidth = rightGroupMinimumWidths[groupName]
									leftGlyphName = rightGroupNarrowestGlyphs[groupName]
								else:
									# leftKey is a glyph ID like "59B740DA-A4F4-43DF-B6DD-1DFA213FFFE7"
									leftGlyph = thisFont.glyphForId_(leftKey)
									# exclude if non-exporting and user limited to exporting glyphs:
									if limitToExportingGlyphs and not leftGlyph.export:
										kernValue = 0.0
									leftWidth = leftGlyph.layers[thisMaster.id].width
									leftGlyphName = leftGlyph.name
							
								if rightKey[0] == "@":
									# rightKey is a group name like "@MMK_R_y"
									groupName = rightKey[7:]
									rightWidth = leftGroupMinimumWidths[groupName]
									rightGlyphName = leftGroupNarrowestGlyphs[groupName]
								else:
									# rightKey is a glyph ID like "59B740DA-A4F4-43DF-B6DD-1DFA213FFFE7"
									rightGlyph = thisFont.glyphForId_(rightKey)
									# exclude if non-exporting and user limited to exporting glyphs:
									if limitToExportingGlyphs and not rightGlyph.export:
										kernValue = 0.0
									rightWidth = rightGlyph.layers[thisMaster.id].width
									rightGlyphName = rightGlyph.name
							
								# compare widths and collect overkern if it is one:
								# (kernValue of excluded glyphs will be 0.0 and not trigger the if clause)
								if abs(kernValue) > thresholdFactor*leftWidth or abs(kernValue) > thresholdFactor*rightWidth:
									tabText += "/%s/%s\n" % (leftGlyphName, rightGlyphName)
									
							except Exception, e:
								# probably a kerning group name found in the kerning data, but no glyph assigned to it:
								# brings macro window to front and reports warning:
								Glyphs.showMacroWindow()
								import traceback
								errormsg = traceback.format_exc().lower()
								for side in ("left","right"):
									if not side in errormsg:
										print "Warning: The %s group '%s' found in your kerning data does not appear in any glyph. Clean up your kerning, and run the script again."
								
				
				if tabText:
					# opens new Edit tab:
					thisFont.newTab( tabText[:-1] )
				else:
					Message(title="No Overkerns Found", message="Could not find any kern pairs beyond the threshold in this master.", OKButton="Phew!")
					
			if not self.SavePreferences( self ):
				print "Note: 'Find Overkerns' could not write preferences."
			
			# self.w.close() # delete if you want window to stay open
		except Exception, e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print "Find Overkerns Error: %s" % e
			import traceback
			print traceback.format_exc()

FindOverkerns()
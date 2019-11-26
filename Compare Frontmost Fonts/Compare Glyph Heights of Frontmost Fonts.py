#MenuTitle: Compare Glyph Heights
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
from builtins import str
__doc__="""
Lists all glyphs that differ from the second font in height beyond a given threshold.
"""

import vanilla

class CompareGlyphHeightsOfFrontmostFonts( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 320
		windowHeight = 200
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Compare Glyph Heights of Frontmost Fonts", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.CompareGlyphHeightsOfFrontmostFonts.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 28), u"Lists all glyphs that differ in height more than the given threshold. Detailed report in Macro Window.", sizeStyle='small', selectable=True )
		linePos += lineHeight*2
		
		self.w.tolerateText = vanilla.TextBox( (inset, linePos+2, 140, 14), u"Tolerate difference up to:", sizeStyle='small', selectable=True )
		self.w.tolerate = vanilla.EditText( (inset+140, linePos, -inset, 19), "5", callback=self.SavePreferences, sizeStyle='small' )
		self.w.tolerate.getNSTextField().setToolTip_("How much of a difference is OK. Hint: overshoot size is a good idea for this one.")
		linePos += lineHeight
		
		self.w.heights = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Compare top bounds (‘heights’)", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.heights.getNSButton().setToolTip_("Measures and compares the heights of the top edges (bbox maximum).")
		linePos += lineHeight
		
		self.w.depths = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Compare bottom bounds (‘depths’)", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.depths.getNSButton().setToolTip_("Measures and compares the heights of the bottom edges (bbox minimum).")
		linePos += lineHeight
		
		self.w.includeNonExporting = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Include non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.includeNonExporting.getNSButton().setToolTip_("If enabled, also measures glyphs that are set to not export.")
		linePos += lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-120-inset, -20-inset, -inset, -inset), "Compare", sizeStyle='regular', callback=self.CompareGlyphHeightsOfFrontmostFontsMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Compare Glyph Heights of Frontmost Fonts' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def updateGUI(self):
		if not self.w.heights.get() and not self.w.depths.get():
			self.w.runButton.enable(False)
		else:
			self.w.runButton.enable(True)
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.CompareGlyphHeightsOfFrontmostFonts.heights"] = self.w.heights.get()
			Glyphs.defaults["com.mekkablue.CompareGlyphHeightsOfFrontmostFonts.depths"] = self.w.depths.get()
			Glyphs.defaults["com.mekkablue.CompareGlyphHeightsOfFrontmostFonts.tolerate"] = self.w.tolerate.get()
			Glyphs.defaults["com.mekkablue.CompareGlyphHeightsOfFrontmostFonts.includeNonExporting"] = self.w.includeNonExporting.get()
			self.updateGUI()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.CompareGlyphHeightsOfFrontmostFonts.heights", 0)
			Glyphs.registerDefault("com.mekkablue.CompareGlyphHeightsOfFrontmostFonts.depths", 0)
			Glyphs.registerDefault("com.mekkablue.CompareGlyphHeightsOfFrontmostFonts.tolerate", 0)
			Glyphs.registerDefault("com.mekkablue.CompareGlyphHeightsOfFrontmostFonts.includeNonExporting", 0)
			self.w.heights.set( Glyphs.defaults["com.mekkablue.CompareGlyphHeightsOfFrontmostFonts.heights"] )
			self.w.depths.set( Glyphs.defaults["com.mekkablue.CompareGlyphHeightsOfFrontmostFonts.depths"] )
			self.w.tolerate.set( Glyphs.defaults["com.mekkablue.CompareGlyphHeightsOfFrontmostFonts.tolerate"] )
			self.w.includeNonExporting.set( Glyphs.defaults["com.mekkablue.CompareGlyphHeightsOfFrontmostFonts.includeNonExporting"] )
			self.updateGUI()
		except:
			return False
			
		return True

	def CompareGlyphHeightsOfFrontmostFontsMain( self, sender ):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences( self ):
				print("Note: 'Compare Glyph Heights of Frontmost Fonts' could not write preferences.")
			
			if len(Glyphs.fonts) < 2:
				Message(title="Compare Error", message="You need to have at least two fonts open for comparing.", OKButton="Ooops")	
			else:
				# brings macro window to front and clears its log:
				Glyphs.clearLog()
				# Glyphs.showMacroWindow()
				
				thisFont = Glyphs.font # frontmost font
				otherFont = Glyphs.fonts[1] # second font
				print("Compare Glyph Heights of Frontmost Fonts Report for:\n  (1) %s: %s\n      %s\n  (2) %s: %s\n      %s" % (
					thisFont.familyName, thisFont.filepath.lastPathComponent(), thisFont.filepath,
					otherFont.familyName, otherFont.filepath.lastPathComponent(), otherFont.filepath,
					))
				print()
			
				heights = Glyphs.defaults["com.mekkablue.CompareGlyphHeightsOfFrontmostFonts.heights"]
				depths = Glyphs.defaults["com.mekkablue.CompareGlyphHeightsOfFrontmostFonts.depths"]
				tolerate = float(Glyphs.defaults["com.mekkablue.CompareGlyphHeightsOfFrontmostFonts.tolerate"])
				includeNonExporting = Glyphs.defaults["com.mekkablue.CompareGlyphHeightsOfFrontmostFonts.includeNonExporting"]
			
				theseIDs = [m.id for m in thisFont.masters]
				otherIDs = [m.id for m in otherFont.masters]
				masters = zip(theseIDs, otherIDs)
				collectedGlyphNames = []
				
				if len(theseIDs) != len(otherIDs):
					print(u"⚠️ Different number of masters in %s and %s" % (thisFont.filepath.lastPathComponent(), otherFont.filepath.lastPathComponent()))
			
				for thisGlyph in thisFont.glyphs:
					if thisGlyph.export or includeNonExporting:
						glyphName = thisGlyph.name
						otherGlyph = otherFont.glyphs[glyphName]
						if not otherGlyph:
							print(u"⚠️ %s: not in other font (%s)" % (glyphName, otherFont.familyName))
						else:
							for idPair in masters:
								thisID, otherID = idPair[0], idPair[1]
								thisLayer = thisGlyph.layers[thisID]
								otherLayer = otherGlyph.layers[otherID]
								if not (thisLayer and otherLayer):
									print(u"⚠️ Cannot compare layers in %s" % glyphName)
								else:
									if heights:
										thisHeight = thisLayer.bounds.origin.y + thisLayer.bounds.size.height
										otherHeight = otherLayer.bounds.origin.y + otherLayer.bounds.size.height
										if abs(thisHeight-otherHeight) > tolerate:
											print(u"❌ %s heights: 1st %.1f, 2nd %.1f" % (glyphName, thisHeight, otherHeight))
											collectedGlyphNames.append(glyphName)
									if depths:
										thisDepth = thisLayer.bounds.origin.y
										otherDepth = otherLayer.bounds.origin.y
										if abs(thisDepth-otherDepth) > tolerate:
											print(u"❌ %s depths: 1st %.1f, 2nd %.1f" % (glyphName, thisDepth, otherDepth))
											collectedGlyphNames.append(glyphName)
											
				if not collectedGlyphNames:
					Message(title="No significant differences", message="No differences larger than %.1f found between the two frontmost fonts. See the macro window for error messages."%tolerate, OKButton=u"😎 Cool")
				else:
					collectedGlyphNames = tuple(set(collectedGlyphNames))
					tabText = "/"+"/".join(collectedGlyphNames)
					thisFont.newTab(tabText)
			
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Compare Glyph Heights of Frontmost Fonts Error: %s" % e)
			import traceback
			print(traceback.format_exc())

CompareGlyphHeightsOfFrontmostFonts()
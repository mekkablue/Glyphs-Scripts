#MenuTitle: Monospace Checker
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__="""
Checks if all glyph widths in the frontmost font are actually monospaced. Reports in Macro Window and opens a tab with affected layers.
"""

import vanilla

class MonospaceChecker( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 270
		windowHeight = 200
		windowWidthResize  = 200 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Monospace Checker", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.MonospaceChecker.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 12, 22
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, lineHeight*2), u"New tab with glyphs that do not match the width of the default glyph in each master:", sizeStyle='small', selectable=True )
		linePos += lineHeight*2
		
		self.w.defaultGlyphText = vanilla.TextBox( (inset, linePos, 85, 14), u"Default Glyph:", sizeStyle='small', selectable=True )
		self.w.defaultGlyph = vanilla.EditText( (inset+85, linePos-3, -inset, 19), "A", callback=self.SavePreferences, sizeStyle='small' )
		self.w.defaultGlyph.getNSTextField().setToolTip_(u"For each master, will measure the width of this glyph, and compare all other widths to it.")
		linePos += lineHeight
		
		self.w.toleranceText = vanilla.TextBox( (inset, linePos, 105, 14), u"Tolerance in units:", sizeStyle='small', selectable=True )
		self.w.tolerance = vanilla.EditText( (inset+105, linePos-3, -inset, 19), "0.0", callback=self.SavePreferences, sizeStyle='small' )
		self.w.tolerance.getNSTextField().setToolTip_(u"Allow deviations up to this value. 1 unit may be acceptable. If you are not sure, keep it at zero.")
		linePos += lineHeight
		
		self.w.reportZeroWidths = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Report Zero Widths in Macro Window", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.reportZeroWidths.getNSButton().setToolTip_(u"In the Macro Window (and only there), will also report glyphs that have zero width. Usually you can ignore those.")
		linePos += lineHeight
		
		self.w.includeNonExporting = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Include Non-Exporting Glyphs", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.includeNonExporting.getNSButton().setToolTip_(u"If disabled, will ignore non-exporting glyphs. If you are unsure, leave it off.")
		linePos += lineHeight
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-100-inset, -20-inset, -inset, -inset), "Check", sizeStyle='regular', callback=self.MonospaceCheckerMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Monospace Checker' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.MonospaceChecker.defaultGlyphName"] = self.w.defaultGlyphName.get()
			Glyphs.defaults["com.mekkablue.MonospaceChecker.tolerance"] = self.w.tolerance.get()
			Glyphs.defaults["com.mekkablue.MonospaceChecker.reportZeroWidths"] = self.w.reportZeroWidths.get()
			Glyphs.defaults["com.mekkablue.MonospaceChecker.includeNonExporting"] = self.w.includeNonExporting.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.MonospaceChecker.defaultGlyphName", "A")
			Glyphs.registerDefault("com.mekkablue.MonospaceChecker.tolerance", 0.0)
			Glyphs.registerDefault("com.mekkablue.MonospaceChecker.reportZeroWidths", 0)
			Glyphs.registerDefault("com.mekkablue.MonospaceChecker.includeNonExporting", 0)
			self.w.defaultGlyphName.set( Glyphs.defaults["com.mekkablue.MonospaceChecker.defaultGlyphName"] )
			self.w.tolerance.set( Glyphs.defaults["com.mekkablue.MonospaceChecker.tolerance"] )
			self.w.reportZeroWidths.set( Glyphs.defaults["com.mekkablue.MonospaceChecker.reportZeroWidths"] )
			self.w.includeNonExporting.set( Glyphs.defaults["com.mekkablue.MonospaceChecker.includeNonExporting"] )
		except:
			return False
			
		return True

	def MonospaceCheckerMain( self, sender ):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences( self ):
				print("Note: 'Monospace Checker' could not write preferences.")
			
			# brings macro window to front and clears its log:
			Glyphs.clearLog()
			
			thisFont = Glyphs.font # frontmost font
			print("Monospace Checker Report for:\n%s" % thisFont.familyName)
			print(thisFont.filepath)
			
			defaultGlyphName = Glyphs.defaults["com.mekkablue.MonospaceChecker.defaultGlyphName"].strip()
			defaultGlyph = thisFont.glyphs[defaultGlyphName]
			tolerance = float(Glyphs.defaults["com.mekkablue.MonospaceChecker.tolerance"])
			includeNonExporting = Glyphs.defaults["com.mekkablue.MonospaceChecker.includeNonExporting"]
			reportZeroWidths = Glyphs.defaults["com.mekkablue.MonospaceChecker.reportZeroWidths"]
			
			if not defaultGlyph:
				Message(
					title="Glyph Not Found",
					message="Could not find a glyph named '%s' in the frontmost font (%s). Aborting."%(defaultGlyphName, thisFont.familyName),
					OKButton="Oops",
				)
			else:
				affectedLayers = []
				deviatingWidthCount = 0
				for thisMaster in thisFont.masters:
					masterID = thisMaster.id
					defaultWidth = defaultGlyph.layers[masterID].width
					print("\nⓂ️ Master %s, default width: %.1f" % (thisMaster.name, defaultWidth))
					for thisGlyph in thisFont.glyphs:
						if thisGlyph.export or includeNonExporting:
							for thisLayer in thisGlyph.layers:
								if thisLayer.associatedMasterId == masterID and (thisLayer.isMasterLayer or thisLayer.isSpecialLayer):
									thisWidth = thisLayer.width
									if thisWidth == 0.0:
										if reportZeroWidths:
											print("ℹ️ %s, layer '%s': zero width" % (thisGlyph.name, thisLayer.name))
									elif not (defaultWidth-tolerance) <= thisWidth <= (defaultWidth+tolerance):
										affectedLayers.append(thisLayer)
										deviatingWidthCount += 1
										print("⛔️ %s, layer '%s': %.1f" % (thisGlyph.name, thisLayer.name, thisWidth))
									
					# add a newline:
					if affectedLayers:
						newLine = GSControlLayer.newline()
						affectedLayers.append(newLine)
			
			if affectedLayers:
				# Floating notification:
				Glyphs.showNotification( 
					u"Inconsistent widths in %s" % (thisFont.familyName),
					u"Found %i width deviation%s. Details in Macro Window." % (
						deviatingWidthCount,
						"" if deviatingWidthCount==1 else "s",
						),
					)
				# opens new Edit tab:
				newTab = thisFont.newTab()
				newTab.layers = affectedLayers
			else:
				# Floating notification:
				Glyphs.showNotification( 
					u"🥇 %s has consistent widths" % (thisFont.familyName),
					u"All glyph widths are monospaced. Congrats!",
					)
				
			# self.w.close() # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Monospace Checker Error: %s" % e)
			import traceback
			print(traceback.format_exc())

MonospaceChecker()
#MenuTitle: Vertical Metrics Manager
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")
__doc__="""
Manage and sync ascender, descender and linegap values for hhea, OS/2 sTypo and OS/2 usWin.
"""

import vanilla

def cleanInt(numberString):
	exportString = ""
	numberString = unicode(numberString)
	for char in numberString:
		if char in "1234567890+-":
			exportString += char
	floatNumber = float(exportString)
	floatNumber = round(floatNumber)
	return int(floatNumber)

def roundUpByValue(x, roundBy):
	if x == 0: 
		# avoid division by zero
		return 0
	else:
		sign = x/abs(x) # +1 or -1
		factor=0
		if x%roundBy:
			factor=1
		return int((abs(x)//roundBy*roundBy + factor*roundBy) * sign)

class VerticalMetricsManager( object ):
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 330
		windowHeight = 410
		windowWidthResize  = 100 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Vertical Metrics Manager", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.VerticalMetricsManager.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), u"Manage and sync hhea, typo and win values.", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.titleAscent = vanilla.TextBox( (inset+70, linePos+4, 70, 14), u"Ascender", sizeStyle='small', selectable=True )
		self.w.titleDescent = vanilla.TextBox( (inset+140, linePos+4, 70, 14), u"Descender", sizeStyle='small', selectable=True )
		self.w.titleLineGap = vanilla.TextBox( (inset+210, linePos+4, 70, 14), u"Line Gap", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.titleWin = vanilla.TextBox( (inset, linePos+3, 70, 14), u"OS/2 usWin", sizeStyle='small', selectable=True )
		self.w.winAsc = vanilla.EditText( (inset+70, linePos, 65, 19), "", callback=self.SavePreferences, sizeStyle='small' )
		self.w.winAsc.getNSTextField().setToolTip_("OS/2 usWinAscent. Should be the maximum height in your font. Expect clipping or rendering artefacts beyond this point.")
		self.w.winDesc = vanilla.EditText( (inset+140, linePos, 65, 19), "", callback=self.SavePreferences, sizeStyle='small' )
		self.w.winDesc.getNSTextField().setToolTip_("OS/2 usWinDescent (unsigned integer). Should be the maximum depth in your font, like the lowest descender you have. Expect clipping or rendering artefacts beyond this point.")
		self.w.winGap = vanilla.EditText( (inset+210, linePos, 65, 19), "", callback=None, sizeStyle='small', readOnly=True, placeholder=u"n/a" )
		self.w.winGap.getNSTextField().setToolTip_("OS/2 usWinLineGap does not exist, hence greyed out here.")
		self.w.winUpdate = vanilla.SquareButton( (inset+280, linePos, 20, 19), u"↺", sizeStyle='small', callback=self.update )
		self.w.winUpdate.getNSButton().setToolTip_("Will recalculate the OS/2 usWin values in the fields to the left. Takes the measurement settings below into account, except for the Limit options.")
		linePos += lineHeight+4
		
		self.w.parenTypo = vanilla.TextBox( (inset-12, linePos+5, 15, 20), u"┏", sizeStyle='small', selectable=False )
		self.w.titleTypo = vanilla.TextBox( (inset, linePos+3, 70, 14), u"OS/2 sTypo", sizeStyle='small', selectable=True )
		self.w.typoAsc = vanilla.EditText( (inset+70, linePos, 65, 19), "", callback=self.SavePreferences, sizeStyle='small' )
		self.w.typoAsc.getNSTextField().setToolTip_("OS/2 sTypoAscender (positive value), should be the same as hheaAscender. Should be the maximum height of the glyphs relevant for horizontal text setting in your font, like the highest accented uppercase letter, typically Aring or Ohungarumlaut. Used for first baseline offset in DTP and office apps and together with the line gap value, also in browsers.")
		self.w.typoDesc = vanilla.EditText( (inset+140, linePos, 65, 19), "", callback=self.SavePreferences, sizeStyle='small' )
		self.w.typoDesc.getNSTextField().setToolTip_("OS/2 sTypoDescender (negative value), should be the same as hheaDescender. Should be the maximum depth of the glyphs relevant for horizontal text setting in your font, like the lowest descender or bottom accent, typically Gcommaccent, Ccedilla, or one of the lowercase descenders (gjpqy). Together with the line gap value, used for line distance calculation in office apps and browsers.")
		self.w.typoGap = vanilla.EditText( (inset+210, linePos, 65, 19), "", callback=self.SavePreferences, sizeStyle='small' )
		self.w.typoGap.getNSTextField().setToolTip_("OS/2 sTypoLineGap (positive value), should be the same as hheaLineGap. Should be either zero or a value for padding between lines that makes sense visually. Office apps insert this distance between the lines, browsers add half on top and half below each line, also for determining text object boundaries.")
		self.w.typoUpdate = vanilla.SquareButton( (inset+280, linePos, 20, 19), u"↺", sizeStyle='small', callback=self.update )
		self.w.typoUpdate.getNSButton().setToolTip_("Will recalculate the OS/2 sTypo values in the fields to the left. Takes the measurement settings below into account.")
		linePos += lineHeight

		self.w.parenConnect = vanilla.TextBox( (inset-12, linePos-int(lineHeight/2)+4, 15, 20), u"┃", sizeStyle='small', selectable=False )
		self.w.parenHhea = vanilla.TextBox( (inset-12, linePos+3, 15, 20), u"┗", sizeStyle='small', selectable=False )
		self.w.titleHhea = vanilla.TextBox( (inset, linePos+3, 70, 14), u"hhea", sizeStyle='small', selectable=True )
		self.w.hheaAsc = vanilla.EditText( (inset+70, linePos, 65, 19), "", callback=self.SavePreferences, sizeStyle='small' )
		self.w.hheaAsc.getNSTextField().setToolTip_("hheaAscender (positive value), should be the same as OS/2 sTypoAscender. Should be the maximum height of the glyphs relevant for horizontal text setting in your font, like the highest accented uppercase letter, typically Aring or Ohungarumlaut. Used for first baseline offset in Mac office apps and together with the line gap value, also in Mac browsers.")
		self.w.hheaDesc = vanilla.EditText( (inset+140, linePos, 65, 19), "", callback=self.SavePreferences, sizeStyle='small' )
		self.w.hheaDesc.getNSTextField().setToolTip_("hheaDescender (negative value), should be the same as OS/2 sTypoDescender. Should be the maximum depth of the glyphs relevant for horizontal text setting in your font, like the lowest descender or bottom accent, typically Gcommaccent, Ccedilla, or one of the lowercase descenders (gjpqy). Together with the line gap value, used for line distance calculation in office apps and browsers.")
		self.w.hheaGap = vanilla.EditText( (inset+210, linePos, 65, 19), "", callback=self.SavePreferences, sizeStyle='small' )
		self.w.hheaGap.getNSTextField().setToolTip_("hheaLineGap (positive value), should be the same as OS/2 sTypoLineGap. Should be either zero or a value for padding between lines that makes sense visually. Mac office apps insert this distance between the lines, Mac browsers add half on top and half below each line, also for determining text object boundaries.")
		self.w.hheaUpdate = vanilla.SquareButton( (inset+280, linePos, 20, 19), u"↺", sizeStyle='small', callback=self.update )
		self.w.hheaUpdate.getNSButton().setToolTip_("Will recalculate the hhea values in the fields to the left. Takes the measurement settings below into account.")
		linePos += lineHeight
		
		self.w.useTypoMetrics = vanilla.CheckBox( (inset+70, linePos, -inset, 20), u"Use Typo Metrics (fsSelection bit 7)", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.useTypoMetrics.getNSButton().setToolTip_("Should ALWAYS BE ON. Only uncheck if you really know what you are doing. If unchecked, line behaviour will be not consistent between apps and browsers because some apps prefer win values to sTypo values for determining line distances.")
		self.w.useTypoMetricsUpdate = vanilla.SquareButton( (inset+280, linePos, 20, 19), u"↺", sizeStyle='small', callback=self.update )
		self.w.useTypoMetricsUpdate.getNSButton().setToolTip_("Will reset the checkbox to the left to ON, because it should ALWAYS be on. Strongly recommended.")
		linePos += lineHeight*1.5
		
		self.w.descriptionMeasurements = vanilla.TextBox( (inset, linePos+2, -inset, 14), u"Taking Measurements (see tooltips for info):", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.round = vanilla.CheckBox( (inset, linePos, 70, 20), u"Round by:", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.round.getNSButton().setToolTip_("Turn on if you want your values rounded. Recommended.")
		self.w.roundValue = vanilla.EditText( (inset+75, linePos, 60, 19), "10", callback=self.SavePreferences, sizeStyle='small' )
		self.w.roundValue.getNSTextField().setToolTip_("All value calculations will be rounded up to the next multiple of this value. Recommended: 10.")
		linePos += lineHeight
		
		self.w.includeAllMasters = vanilla.CheckBox( (inset, linePos, -inset, 20), u"Include all masters (otherwise current master only)", value=True, callback=self.SavePreferences, sizeStyle='small' )
		self.w.includeAllMasters.getNSButton().setToolTip_("If checked, all masters will be measured. If unchecked, only the current master will be measured. Since vertical metrics should be the same throughout all masters, it also makes sense to measure on all masters.")
		linePos += lineHeight
		
		self.w.respectMarkToBaseOffset = vanilla.CheckBox( (inset, linePos, -inset, 20), "Include mark-to-base offset for OS/2 usWin", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.respectMarkToBaseOffset.getNSButton().setToolTip_("If checked will calculate the maximum possible height that can be reached with top-anchored marks, and the lowest depth with bottom-anchored marks, and use those values for the OS/2 usWin values. Strongly recommended for making fonts work on Windows if they rely on mark-to-base positioning (e.g. Arabic). Respects the ‘Limit to Script’ setting.")
		linePos += lineHeight
		
		self.w.ignoreNonExporting = vanilla.CheckBox( (inset, linePos, -inset, 20), u"Ignore non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.ignoreNonExporting.getNSButton().setToolTip_("If checked, glyphs that do not export will be excluded from measuring. Recommended. (Ignored for calculating the OS/2 usWin values.)")
		linePos += lineHeight
		
		self.w.preferSelectedGlyphs = vanilla.CheckBox( (inset, linePos, -inset, 20), u"Limit to selected glyphs", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.preferSelectedGlyphs.getNSButton().setToolTip_("If checked, only the current glyphs will be measured. Can be combined with the other Limit options. May make sense if you want your metrics to be e.g. Latin-CE-centric.")
		linePos += lineHeight
		
		self.w.preferScript = vanilla.CheckBox( (inset, linePos, inset+110, 20), u"Limit to script:", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.preferScript.getNSButton().setToolTip_("If checked, only measures glyphs belonging to the selected writing system. Can be combined with the other Limit options. (Ignored for calculating the OS/2 usWin values, but respected for mark-to-base calculation.)")
		self.w.preferScriptPopup = vanilla.PopUpButton( (inset+115, linePos+1, -inset-25, 17), (u"latin", u"greek"), sizeStyle='small', callback=self.SavePreferences )
		self.w.preferScriptPopup.getNSPopUpButton().setToolTip_("Choose a writing system ('script') you want the measurements to be limited to. May make sense to ignore other scripts if the font is intended only for e.g. Cyrillic. Does not apply to OS/2 usWin")
		self.w.preferScriptUpdate = vanilla.SquareButton( (-inset-20, linePos+1, -inset, 18), u"↺", sizeStyle='small', callback=self.update )
		self.w.preferScriptUpdate.getNSButton().setToolTip_("Update the script popup to the left with all scripts (writing systems) found in the current font.")
		linePos += lineHeight

		self.w.preferCategory = vanilla.CheckBox( (inset, linePos, inset+110, 20), u"Limit to category:", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.preferCategory.getNSButton().setToolTip_("If checked, only measures glyphs belonging to the selected glyph category. Can be combined with the other Limit options. (Ignored for calculating the OS/2 usWin values.)")
		self.w.preferCategoryPopup = vanilla.PopUpButton( (inset+115, linePos+1, -inset-25, 17), (u"Letter", u"Number"), sizeStyle='small', callback=self.SavePreferences )
		self.w.preferCategoryPopup.getNSPopUpButton().setToolTip_("Choose a glyph category you want the measurements to be limited to. It may make sense to limit only to Letter.")
		self.w.preferCategoryUpdate = vanilla.SquareButton( (-inset-20, linePos+1, -inset, 18), u"↺", sizeStyle='small', callback=self.update )
		self.w.preferCategoryUpdate.getNSButton().setToolTip_("Update the category popup to the left with all glyph categories found in the current font.")
		linePos += lineHeight
		
		self.w.allOpenFonts = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"⚠️ Read out and apply to ALL open fonts", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.allOpenFonts.getNSButton().setToolTip_(u"If activated, does not only measure the frontmost font, but all open fonts. Careful: when you press the Apply button, will also apply it to all open fonts. Useful if you have all font files for a font family open.")
		linePos += lineHeight
		
		
		# Run Button:
		self.w.helpButton = vanilla.HelpButton((inset-2, -20-inset, 21, -inset+2), callback=self.openURL )
		self.w.helpButton.getNSButton().setToolTip_("Opens the Vertical Metrics tutorial (highly recommended) in your web browser.")
		
		self.w.runButton = vanilla.Button( (-120-inset, -20-inset, -inset, -inset), "Apply to Font", sizeStyle='regular', callback=self.VerticalMetricsManagerMain )
		self.w.runButton.getNSButton().setToolTip_("Insert the OS/2, hhea and fsSelection values above as custom parameters in the font. The number values will be inserted into each master. Blank values will delete the respective parameters.")
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Vertical Metrics Manager' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
	
	def updateUI(self, sender=None):
		self.w.includeAllMasters.enable(not self.w.allOpenFonts.get())
		self.w.runButton.setTitle( "Apply to Font%s" % (
			"s" if self.w.allOpenFonts.get() else ""
		))
	
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.VerticalMetricsManager.allOpenFonts"] = self.w.allOpenFonts.get()
			Glyphs.defaults["com.mekkablue.VerticalMetricsManager.preferSelectedGlyphs"] = self.w.preferSelectedGlyphs.get()
			Glyphs.defaults["com.mekkablue.VerticalMetricsManager.preferCategory"] = self.w.preferCategory.get()
			Glyphs.defaults["com.mekkablue.VerticalMetricsManager.preferScript"] = self.w.preferScript.get()
			Glyphs.defaults["com.mekkablue.VerticalMetricsManager.ignoreNonExporting"] = self.w.ignoreNonExporting.get()
			Glyphs.defaults["com.mekkablue.VerticalMetricsManager.includeAllMasters"] = self.w.includeAllMasters.get()
			Glyphs.defaults["com.mekkablue.VerticalMetricsManager.respectMarkToBaseOffset"] = self.w.respectMarkToBaseOffset.get()
			Glyphs.defaults["com.mekkablue.VerticalMetricsManager.round"] = self.w.round.get()
			Glyphs.defaults["com.mekkablue.VerticalMetricsManager.roundValue"] = self.w.roundValue.get()
			Glyphs.defaults["com.mekkablue.VerticalMetricsManager.useTypoMetrics"] = self.w.useTypoMetrics.get()
			Glyphs.defaults["com.mekkablue.VerticalMetricsManager.hheaGap"] = int(self.w.hheaGap.getNSTextField().integerValue())
			Glyphs.defaults["com.mekkablue.VerticalMetricsManager.hheaDesc"] = int(self.w.hheaDesc.getNSTextField().integerValue())
			Glyphs.defaults["com.mekkablue.VerticalMetricsManager.hheaAsc"] = int(self.w.hheaAsc.getNSTextField().integerValue())
			Glyphs.defaults["com.mekkablue.VerticalMetricsManager.typoGap"] = int(self.w.typoGap.getNSTextField().integerValue())
			Glyphs.defaults["com.mekkablue.VerticalMetricsManager.typoDesc"] = int(self.w.typoDesc.getNSTextField().integerValue())
			Glyphs.defaults["com.mekkablue.VerticalMetricsManager.typoAsc"] = int(self.w.typoAsc.getNSTextField().integerValue())
			Glyphs.defaults["com.mekkablue.VerticalMetricsManager.winDesc"] = int(self.w.winDesc.getNSTextField().integerValue())
			Glyphs.defaults["com.mekkablue.VerticalMetricsManager.winAsc"] = int(self.w.winAsc.getNSTextField().integerValue())
			
			self.updateUI()
		except:
			import traceback
			print(traceback.format_exc())
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.VerticalMetricsManager.allOpenFonts", 0)
			Glyphs.registerDefault("com.mekkablue.VerticalMetricsManager.preferSelectedGlyphs", 0)
			Glyphs.registerDefault("com.mekkablue.VerticalMetricsManager.preferCategory", 0)
			Glyphs.registerDefault("com.mekkablue.VerticalMetricsManager.preferScript", 0)
			Glyphs.registerDefault("com.mekkablue.VerticalMetricsManager.ignoreNonExporting", 1)
			Glyphs.registerDefault("com.mekkablue.VerticalMetricsManager.includeAllMasters", 1)
			Glyphs.registerDefault("com.mekkablue.VerticalMetricsManager.respectMarkToBaseOffset", 0)
			Glyphs.registerDefault("com.mekkablue.VerticalMetricsManager.round", 1)
			Glyphs.registerDefault("com.mekkablue.VerticalMetricsManager.roundValue", 10)
			Glyphs.registerDefault("com.mekkablue.VerticalMetricsManager.useTypoMetrics", 1)
			Glyphs.registerDefault("com.mekkablue.VerticalMetricsManager.hheaGap", 0)
			Glyphs.registerDefault("com.mekkablue.VerticalMetricsManager.hheaDesc", 0)
			Glyphs.registerDefault("com.mekkablue.VerticalMetricsManager.hheaAsc", 0)
			Glyphs.registerDefault("com.mekkablue.VerticalMetricsManager.typoGap", 0)
			Glyphs.registerDefault("com.mekkablue.VerticalMetricsManager.typoDesc", 0)
			Glyphs.registerDefault("com.mekkablue.VerticalMetricsManager.typoAsc", 0)
			Glyphs.registerDefault("com.mekkablue.VerticalMetricsManager.winDesc", 0)
			Glyphs.registerDefault("com.mekkablue.VerticalMetricsManager.winAsc", 0)
			
			self.w.allOpenFonts.set( Glyphs.defaults["com.mekkablue.VerticalMetricsManager.allOpenFonts"] )
			self.w.preferSelectedGlyphs.set( Glyphs.defaults["com.mekkablue.VerticalMetricsManager.preferSelectedGlyphs"] )
			self.w.preferCategory.set( Glyphs.defaults["com.mekkablue.VerticalMetricsManager.preferCategory"] )
			self.w.preferScript.set( Glyphs.defaults["com.mekkablue.VerticalMetricsManager.preferScript"] )
			self.w.ignoreNonExporting.set( Glyphs.defaults["com.mekkablue.VerticalMetricsManager.ignoreNonExporting"] )
			self.w.includeAllMasters.set( Glyphs.defaults["com.mekkablue.VerticalMetricsManager.includeAllMasters"] )
			self.w.respectMarkToBaseOffset.set( Glyphs.defaults["com.mekkablue.VerticalMetricsManager.respectMarkToBaseOffset"] )
			self.w.round.set( Glyphs.defaults["com.mekkablue.VerticalMetricsManager.round"] )
			self.w.roundValue.set( Glyphs.defaults["com.mekkablue.VerticalMetricsManager.roundValue"] )
			self.w.useTypoMetrics.set( Glyphs.defaults["com.mekkablue.VerticalMetricsManager.useTypoMetrics"] )
			self.w.hheaGap.set( "%i"%Glyphs.defaults["com.mekkablue.VerticalMetricsManager.hheaGap"] )
			self.w.hheaDesc.set( "%i"%Glyphs.defaults["com.mekkablue.VerticalMetricsManager.hheaDesc"] )
			self.w.hheaAsc.set( "%i"%Glyphs.defaults["com.mekkablue.VerticalMetricsManager.hheaAsc"] )
			self.w.typoGap.set( "%i"%Glyphs.defaults["com.mekkablue.VerticalMetricsManager.typoGap"] )
			self.w.typoDesc.set( "%i"%Glyphs.defaults["com.mekkablue.VerticalMetricsManager.typoDesc"] )
			self.w.typoAsc.set( "%i"%Glyphs.defaults["com.mekkablue.VerticalMetricsManager.typoAsc"] )
			self.w.winDesc.set( "%i"%Glyphs.defaults["com.mekkablue.VerticalMetricsManager.winDesc"] )
			self.w.winAsc.set( "%i"%Glyphs.defaults["com.mekkablue.VerticalMetricsManager.winAsc"] )
			
			self.updateUI()
		except:
			import traceback
			print(traceback.format_exc())
			return False
			
		return True
	
	def openURL( self, sender ):
		URL = None
		if sender == self.w.helpButton:
			URL = "https://glyphsapp.com/tutorials/vertical-metrics"
		if URL:
			import webbrowser
			webbrowser.open( URL )
	
	def update(self, sender=None):
		Glyphs.clearLog() # clears macro window log
		
		# update settings to the latest user input:
		if not self.SavePreferences( self ):
			print("Note: 'Vertical Metrics Manager' could not write preferences.")
		
		frontmostFont = Glyphs.font
		allOpenFonts = Glyphs.defaults["com.mekkablue.VerticalMetricsManager.allOpenFonts"]
		if allOpenFonts:
			theseFonts = Glyphs.fonts
		else:
			theseFonts = (frontmostFont,) # iterable tuple of frontmost font only
			
		theseFamilyNames = [f.familyName for f in theseFonts]
		print("\nVertical Metrics Manager\nUpdating values for:\n")
		for i, thisFont in enumerate(theseFonts):
			print("%i. %s:"%(i+1, thisFont.familyName))
			if thisFont.filepath:
				print(thisFont.filepath)
			else:
				print("⚠️ The font file has not been saved yet.")
			print()
		
		ignoreNonExporting = Glyphs.defaults["com.mekkablue.VerticalMetricsManager.ignoreNonExporting"]
		includeAllMasters = Glyphs.defaults["com.mekkablue.VerticalMetricsManager.includeAllMasters"]
		shouldRound = Glyphs.defaults["com.mekkablue.VerticalMetricsManager.round"]
		roundValue = int(Glyphs.defaults["com.mekkablue.VerticalMetricsManager.roundValue"])
		respectMarkToBaseOffset = Glyphs.defaults["com.mekkablue.VerticalMetricsManager.respectMarkToBaseOffset"]
		shouldLimitToScript = Glyphs.defaults["com.mekkablue.VerticalMetricsManager.preferScript"]
		selectedScript = self.w.preferScriptPopup.getTitle()

		# win measurements:
		if sender == self.w.winUpdate:
			print("Determining OS/2 usWin values:\n")
			lowest, highest = 0.0, 0.0
			lowestGlyph, highestGlyph = None, None
			
			# respectMarkToBaseOffset:
			highestTopAnchor, lowestBottomAnchor = 0.0, 1.0
			highestTopAnchorGlyph, lowestBottomAnchorGlyph = None, None
			largestTopMark, largestBottomMark = 0.0, 0.0
			largestTopMarkGlyph, largestBottomMarkGlyph = None, None
			
			fontReport = ""
			for i,thisFont in enumerate(theseFonts):
				if allOpenFonts:
					fontReport = "%i. %s, " % (i+1, thisFont.familyName)
				currentMaster = thisFont.selectedFontMaster
				for thisGlyph in thisFont.glyphs:
					if thisGlyph.export or not ignoreNonExporting:
						scriptCheckOK = not shouldLimitToScript or thisGlyph.script == selectedScript # needed for respectMarkToBaseOffset
						
						for thisLayer in thisGlyph.layers:
							belongsToCurrentMaster = thisLayer.associatedFontMaster() == currentMaster
							if belongsToCurrentMaster or includeAllMasters or allOpenFonts:
								if thisLayer.isSpecialLayer or thisLayer.isMasterLayer:
									lowestPointInLayer = thisLayer.bounds.origin.y
									highestPointInLayer = lowestPointInLayer + thisLayer.bounds.size.height
									if lowestPointInLayer < lowest:
										lowest = lowestPointInLayer
										lowestGlyph = "%s%s, layer: %s" % (fontReport, thisGlyph.name, thisLayer.name)
									if highestPointInLayer > highest:
										highest = highestPointInLayer
										highestGlyph = "%s%s, layer: %s" % (fontReport, thisGlyph.name, thisLayer.name)
									
									# respectMarkToBaseOffset:
									if respectMarkToBaseOffset and scriptCheckOK:
										if thisGlyph.category == "Mark":
											topAnchors = [a for a in thisLayer.anchorsTraversingComponents() if a.name=="_top"]
											if topAnchors:
												topAnchor = topAnchors[0]
												topSpan = highestPointInLayer - topAnchor.y
												if topSpan > largestTopMark:
													largestTopMark = topSpan
													largestTopMarkGlyph = "%s%s, layer: %s" % (fontReport, thisGlyph.name, thisLayer.name)
											bottomAnchors = [a for a in thisLayer.anchorsTraversingComponents() if a.name=="_bottom"]
											if bottomAnchors:
												bottomAnchor = bottomAnchors[0]
												bottomSpan = abs(lowestPointInLayer - bottomAnchor.y)
												if bottomSpan > largestBottomMark:
													largestBottomMark = bottomSpan
													largestBottomMarkGlyph = "%s%s, layer: %s" % (fontReport, thisGlyph.name, thisLayer.name)
										else:
											topAnchors = [a for a in thisLayer.anchorsTraversingComponents() if a.name=="top"]
											if topAnchors:
												topAnchor = topAnchors[0]
												if topAnchor.y > highestTopAnchor:
													highestTopAnchor = topAnchor.y
													highestTopAnchorGlyph = "%s%s, layer: %s" % (fontReport, thisGlyph.name, thisLayer.name)
											bottomAnchors = [a for a in thisLayer.anchorsTraversingComponents() if a.name=="bottom"]
											if bottomAnchors:
												bottomAnchor = bottomAnchors[0]
												if bottomAnchor.y < lowestBottomAnchor:
													lowestBottomAnchor = bottomAnchor.y
													lowestBottomAnchorGlyph = "%s%s, layer: %s" % (fontReport, thisGlyph.name, thisLayer.name)
										
			
			print("Highest relevant glyph:")
			print("- %s (%i)" % (highestGlyph, highest))
			print()
			print("Lowest relevant glyph:")
			print("- %s (%i)" % (lowestGlyph, lowest))
			print()
			
			if respectMarkToBaseOffset:
				highestMarkToBase = highestTopAnchor+largestTopMark
				lowestMarkToBase = lowestBottomAnchor-largestBottomMark
				
				print("Highest top anchor:")
				print("- %s (%i)" % (highestTopAnchorGlyph, highestTopAnchor))
				print("Largest top mark span (_top to top edge):")
				print("- %s (%i)" % (largestTopMarkGlyph, largestTopMark))
				print("Highest possible mark-to-base: %i + %i = %i" % (highestTopAnchor, largestTopMark, highestMarkToBase))
				print()
				print("Lowest bottom anchor:")
				print("- %s (%i)" % (lowestBottomAnchorGlyph, lowestBottomAnchor))
				print("Largest bottom mark span (_bottom to bottom edge):")
				print("- %s (%i)" % (largestBottomMarkGlyph, largestBottomMark))
				print("Lowest possible mark-to-base: %i - %i = %i" % (lowestBottomAnchor, largestBottomMark, lowestMarkToBase))
				print()
				
				if lowestMarkToBase < lowest:
					lowest = lowestMarkToBase
				if highestMarkToBase > highest:
					highest = highestMarkToBase
				
		
			if shouldRound:
				highest = roundUpByValue(highest,roundValue)
				lowest = roundUpByValue(lowest,roundValue)
		
			winAsc = int(highest)
			winDesc = abs(int(lowest))
		
			print("Calculated values:")
			print("- usWinAscent: %s" % winAsc)
			print("- usWinDescent: %s" % winDesc)
			print()
		
			Glyphs.defaults["com.mekkablue.VerticalMetricsManager.winAsc"] = winAsc
			Glyphs.defaults["com.mekkablue.VerticalMetricsManager.winDesc"] = winDesc


		# Use Typo Metrics checkbox
		elif sender == self.w.useTypoMetricsUpdate:
			print("Use Typo Metrics (fsSelection bit 7) should always be YES.")
			Glyphs.defaults["com.mekkablue.VerticalMetricsManager.useTypoMetrics"] = 1


		# hhea and typo popups:
		elif sender in (self.w.hheaUpdate, self.w.typoUpdate):
			if sender == self.w.hheaUpdate:
				name = "hhea"
			else:
				name = "OS/2 sTypo"
				
			print("Determining %s values:\n" % name)
			lowest, highest = 0.0, 0.0
			lowestGlyph, highestGlyph = None, None
			
			shouldLimitToCategory = Glyphs.defaults["com.mekkablue.VerticalMetricsManager.preferCategory"]
			shouldLimitToScript = Glyphs.defaults["com.mekkablue.VerticalMetricsManager.preferScript"]
			shouldLimitToSelectedGlyphs = Glyphs.defaults["com.mekkablue.VerticalMetricsManager.preferSelectedGlyphs"]
			selectedCategory = self.w.preferCategoryPopup.getTitle()
			selectedScript = self.w.preferScriptPopup.getTitle()
			
			if shouldLimitToSelectedGlyphs:
				selectedGlyphNames = [l.parent.name for l in frontmostFont.selectedLayers]
				if not selectedGlyphNames:
					print(u"⚠️ Ignoring limitation to selected glyphs because no glyphs are selected (in frontmost font).")
					shouldLimitToSelectedGlyphs = False
					Glyphs.defaults["com.mekkablue.VerticalMetricsManager.preferSelectedGlyphs"] = shouldLimitToSelectedGlyphs
					self.LoadPreferences()
			else:
				selectedGlyphNames = ()
			
			for i,thisFont in enumerate(theseFonts):
				if allOpenFonts:
					fontReport = "%i. %s, " % (i+1, thisFont.familyName)
				else:
					fontReport = ""
					
				currentMaster = thisFont.selectedFontMaster
				
				# ascender & descender calculation:
				for thisGlyph in thisFont.glyphs:
					exportCheckOK = not ignoreNonExporting or thisGlyph.export
					categoryCheckOK = not shouldLimitToCategory or thisGlyph.category == selectedCategory
					scriptCheckOK = not shouldLimitToScript or thisGlyph.script == selectedScript
					selectedCheckOK = not shouldLimitToSelectedGlyphs or thisGlyph.name in selectedGlyphNames
				
					if exportCheckOK and categoryCheckOK and scriptCheckOK and selectedCheckOK:
						for thisLayer in thisGlyph.layers:
							belongsToCurrentMaster = thisLayer.associatedFontMaster() == currentMaster
							if belongsToCurrentMaster or includeAllMasters or allOpenFonts:
								if thisLayer.isSpecialLayer or thisLayer.isMasterLayer:
									lowestPointInLayer = thisLayer.bounds.origin.y
									highestPointInLayer = lowestPointInLayer + thisLayer.bounds.size.height
									if lowestPointInLayer < lowest:
										lowest = lowestPointInLayer
										lowestGlyph = "%s%s, layer: %s" % (fontReport, thisGlyph.name, thisLayer.name)
									if highestPointInLayer > highest:
										highest = highestPointInLayer
										highestGlyph = "%s%s, layer: %s" % (fontReport, thisGlyph.name, thisLayer.name)
										
			print("Highest relevant glyph:")
			print("- %s (%i)" % (highestGlyph, highest))
			print()
			print("Lowest relevant glyph:")
			print("- %s (%i)" % (lowestGlyph, lowest))
			print()
		
			if shouldRound:
				highest = roundUpByValue(highest,roundValue)
				lowest = roundUpByValue(lowest,roundValue)
		
			asc = int(highest)
			desc = int(lowest)
			
			# line gap calculation:
			xHeight = 0
			for thisFont in theseFonts:
				# determine highest x-height:
				for thisMaster in thisFont.masters:
					measuredX = thisMaster.xHeight
					if measuredX >= thisMaster.capHeight or measuredX > thisFont.upm*5: # all caps font or NSNotFound
						measuredX = thisMaster.capHeight/2
					if measuredX > xHeight:
						xHeight = thisMaster.xHeight
				if shouldRound:
					xHeight = roundUpByValue(xHeight, roundValue)
			
			# calculate linegap, based on highest x-height and calculated asc/desc values:
			# 
			# TODO: verify
			# LineGap >= (yMax - yMin) - (Ascender - Descender
			# source: <https://learn.microsoft.com/en-us/typography/opentype/spec/recom#stypoascender-stypodescender-and-stypolinegap>
			# and <https://learn.microsoft.com/en-us/typography/opentype/spec/recom#baseline-to-baseline-distances>
			
			idealLineSpan = abs(xHeight * 2.8)
			if shouldRound:
				idealLineSpan = roundUpByValue(idealLineSpan, roundValue)
			actualLineSpan = abs(asc)+abs(desc)
			if idealLineSpan > actualLineSpan:
				gap = idealLineSpan - actualLineSpan
				if shouldRound:
					gap = roundUpByValue(gap, roundValue)
			else:
				gap = 0
			
			if gap > thisFont.upm*5: # probably NSNotFound
				gap = 0
			
			print("Calculated values:")
			print("- %s Ascender: %i" % (name, asc))
			print("- %s Descender: %i" % (name, desc))
			print("- %s LineGap: %i" % (name, gap))
			print()
		
			if sender == self.w.hheaUpdate:
				Glyphs.defaults["com.mekkablue.VerticalMetricsManager.hheaAsc"] = asc
				Glyphs.defaults["com.mekkablue.VerticalMetricsManager.hheaDesc"] = desc
				Glyphs.defaults["com.mekkablue.VerticalMetricsManager.hheaGap"] = gap
			else:
				Glyphs.defaults["com.mekkablue.VerticalMetricsManager.typoAsc"] = asc
				Glyphs.defaults["com.mekkablue.VerticalMetricsManager.typoDesc"] = desc
				Glyphs.defaults["com.mekkablue.VerticalMetricsManager.typoGap"] = gap
		
		# Updating "Limit to Script" popup:
		elif sender == self.w.preferScriptUpdate:
			scripts = []
			shouldIgnoreNonExporting = Glyphs.defaults["com.mekkablue.VerticalMetricsManager.ignoreNonExporting"]
			for thisGlyph in frontmostFont.glyphs:
				inclusionCheckOK = thisGlyph.export or not shouldIgnoreNonExporting
				if inclusionCheckOK and thisGlyph.script and not thisGlyph.script in scripts:
					scripts.append(thisGlyph.script)
			if scripts:
				self.w.preferScriptPopup.setItems(scripts)
				print(u"✅ Found scripts:\n%s" % ", ".join(scripts))
			else:
				msg = u"Found no glyphs belonging to any script in the frontmost font. Please double check."
				print("⚠️ %s"%msg)
				Message(title="Error Determining Scripts", message="Cannot determine list of scripts. %s"%msg, OKButton=None)
			
			
		# Updating "Limit to Category" popup:
		elif sender == self.w.preferCategoryUpdate:
			categories = []
			shouldIgnoreNonExporting = Glyphs.defaults["com.mekkablue.VerticalMetricsManager.ignoreNonExporting"]
			for thisGlyph in thisFont.glyphs:
				inclusionCheckOK = thisGlyph.export or not shouldIgnoreNonExporting
				if inclusionCheckOK and not thisGlyph.category in categories:
					categories.append(thisGlyph.category)
			if categories:
				self.w.preferCategoryPopup.setItems(categories)
				print(u"✅ Found categories:\n%s" % ", ".join(categories))
			else:
				msg = u"Found no glyphs belonging to any category in the current font. Please double check."
				print("⚠️ %s"%msg)
				Message(title="Error Determining Categories", message="Cannot determine list of categories. %s"%msg, OKButton=None)
				
		
		self.LoadPreferences()
			
		print("hheaGap", Glyphs.defaults["com.mekkablue.VerticalMetricsManager.hheaGap"])
		print("hheaDesc", Glyphs.defaults["com.mekkablue.VerticalMetricsManager.hheaDesc"])
		print("hheaAsc", Glyphs.defaults["com.mekkablue.VerticalMetricsManager.hheaAsc"])
		print("typoGap", Glyphs.defaults["com.mekkablue.VerticalMetricsManager.typoGap"])
		print("typoDesc", Glyphs.defaults["com.mekkablue.VerticalMetricsManager.typoDesc"])
		print("typoAsc", Glyphs.defaults["com.mekkablue.VerticalMetricsManager.typoAsc"])
		print("winDesc", Glyphs.defaults["com.mekkablue.VerticalMetricsManager.winDesc"])
		print("winAsc", Glyphs.defaults["com.mekkablue.VerticalMetricsManager.winAsc"])
		
		
	def VerticalMetricsManagerMain( self, sender ):
		try:
			Glyphs.clearLog() # clears macro window log
			print("Vertical Metrics Manager: setting parameters\n")
			
			# update settings to the latest user input:
			if not self.SavePreferences( self ):
				print("Note: 'Vertical Metrics Manager' could not write preferences.\n")
			
			
			typoAsc = int(Glyphs.defaults["com.mekkablue.VerticalMetricsManager.typoAsc"])
			typoDesc = int(Glyphs.defaults["com.mekkablue.VerticalMetricsManager.typoDesc"])
			typoGap = int(Glyphs.defaults["com.mekkablue.VerticalMetricsManager.typoGap"])
			hheaAsc = int(Glyphs.defaults["com.mekkablue.VerticalMetricsManager.hheaAsc"])
			hheaDesc = int(Glyphs.defaults["com.mekkablue.VerticalMetricsManager.hheaDesc"])
			hheaGap = int(Glyphs.defaults["com.mekkablue.VerticalMetricsManager.hheaGap"])
			winDesc = int(Glyphs.defaults["com.mekkablue.VerticalMetricsManager.winDesc"])
			winAsc = int(Glyphs.defaults["com.mekkablue.VerticalMetricsManager.winAsc"])
			verticalMetricDict = {
				"typoAscender": typoAsc,
				"typoDescender": typoDesc,
				"typoLineGap": typoGap,
				"hheaAscender": hheaAsc,
				"hheaDescender": hheaDesc,
				"hheaLineGap": hheaGap,
				"winDescent": winDesc,
				"winAscent": winAsc,
			}
			
			
			allOpenFonts = Glyphs.defaults["com.mekkablue.VerticalMetricsManager.allOpenFonts"]
			if allOpenFonts:
				theseFonts = Glyphs.fonts
			else:
				theseFonts = (Glyphs.font,) # iterable tuple of frontmost font only
			
			for i, thisFont in enumerate(theseFonts):
				print("\n\n🔠 %s%s:"%(
					"%i. "%(i+1) if allOpenFonts else "", 
					thisFont.familyName,
					))
				if thisFont.filepath:
					print("📄 %s" % thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
			
				for verticalMetricName in sorted(verticalMetricDict.keys()):
					try:
						metricValue = int( verticalMetricDict[verticalMetricName] )
						print(u"🔢 %s: %i" % (verticalMetricName, metricValue))
						for thisMaster in thisFont.masters:
							thisMaster.customParameters[verticalMetricName] = metricValue
							print(u"  ✅ Master %s: custom parameter set." % thisMaster.name)
					except:
						print(u"❌ %s: No valid value found. Deleting parameters:" % verticalMetricName)
						for thisMaster in thisFont.masters:
							if thisMaster.customParameters[verticalMetricName]:
								del thisMaster.customParameters[verticalMetricName]
								print(u"  ⚠️ Master %s: custom parameter removed." % thisMaster.name)
							else:
								print(u"  ❎ Master %s: no custom parameter found." % thisMaster.name)
			
				useTypoMetrics = Glyphs.defaults["com.mekkablue.VerticalMetricsManager.useTypoMetrics"]
				print(u"*️⃣ Use Typo Metrics (fsSelection bit 7)")
				if useTypoMetrics:
					thisFont.customParameters["Use Typo Metrics"] = True
					print(u"  ✅ Set Use Typo Metrics parameter to YES.")
				else:
					thisFont.customParameters["Use Typo Metrics"] = False
					print(u"  ⁉️ Set Use Typo Metrics parameter to NO. This is not recommended. Are you sure?")
			
			# Floating notification:
			Glyphs.showNotification( 
				u"Vertical Metrics Set",
				u"Set vertical metrics in %i font%s. Detailed report in Macro Window." % (
					len(theseFonts),
					"" if len(theseFonts)==1 else "s",
				),
				)
			
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Vertical Metrics Manager Error: %s" % e)
			import traceback
			print(traceback.format_exc())

VerticalMetricsManager()
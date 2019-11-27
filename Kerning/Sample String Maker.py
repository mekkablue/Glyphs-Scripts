#MenuTitle: Sample String Maker
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals

__doc__="""
Creates kern strings for all kerning groups in user-defined categories and adds them to the Sample Strings. Group kerning only, glyphs without groups are ignored.
"""

import vanilla, sampleText

class SampleStringMaker( object ):
	categoryList = (
		"Letter:Uppercase",
		"Letter:Lowercase",
		"Letter:Smallcaps",
		"Punctuation",
		"Symbol:Currency",
		"Symbol:Math",
		"Symbol:Other",
		"Symbol:Arrow",
		"Number:Decimal Digit",
		"Number:Small",
		"Number:Fraction",
	)
	
	scripts = ("latin","cyrillic","greek")
	
	exclusion = (
		"ldot",
		"Ldot",
		"ldot.sc",
		"Ldot.sc",
		"ldot.smcp",
		"Ldot.c2sc",
		"Fhook",
		"florin",
	)
	
	def __init__( self ):
		# Window 'self.w':
		windowWidth  = 340
		windowHeight = 220
		windowWidthResize  = 300 # user can resize width by this value
		windowHeightResize = 0   # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			( windowWidth, windowHeight ), # default window size
			"Sample String Maker", # window title
			minSize = ( windowWidth, windowHeight ), # minimum size (for resizing)
			maxSize = ( windowWidth + windowWidthResize, windowHeight + windowHeightResize ), # maximum size (for resizing)
			autosaveName = "com.mekkablue.SampleStringMaker.mainwindow" # stores last window position and size
		)
		
		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		
		self.w.descriptionText = vanilla.TextBox( (inset, linePos+2, -inset, 14), u"Builds group kern strings, adds them to the Sample Texts.", sizeStyle='small', selectable=True )
		linePos += lineHeight
		
		self.w.scriptText = vanilla.TextBox( (inset, linePos+2, 45, 14), u"Script:", sizeStyle='small', selectable=True )
		self.w.scriptPopup = vanilla.PopUpButton( (inset+45, linePos, -inset, 17), self.scripts, sizeStyle='small', callback=self.SavePreferences )
		self.w.scriptPopup.getNSPopUpButton().setToolTip_("Script for letters, will be ignored for all other categories (e.g., numbers).")
		linePos += lineHeight
		
		self.w.leftCategoryText = vanilla.TextBox( (inset, linePos+2, 90, 14), u"Left Category:", sizeStyle='small', selectable=True )
		self.w.leftCategoryPopup = vanilla.PopUpButton( (inset+90, linePos, -inset, 17), self.categoryList, sizeStyle='small', callback=self.SavePreferences )
		self.w.leftCategoryPopup.getNSPopUpButton().setToolTip_("Category:Subcategory for left side of kern pair.")
		linePos += lineHeight
		
		self.w.rightCategoryText = vanilla.TextBox( (inset, linePos+2, 90, 14), u"Right Category:", sizeStyle='small', selectable=True )
		self.w.rightCategoryPopup = vanilla.PopUpButton( (inset+90, linePos, -inset, 17), self.categoryList, sizeStyle='small', callback=self.SavePreferences )
		self.w.rightCategoryPopup.getNSPopUpButton().setToolTip_("Category:Subcategory for right side of kern pair.")
		linePos += lineHeight
		
		self.w.includeNonExporting = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Also include non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.includeNonExporting.getNSButton().setToolTip_("Also add glyphs of these categories if they are set to not export.")
		linePos += lineHeight
		
		self.w.excludeText = vanilla.TextBox( (inset, linePos+2, 150, 14), u"Exclude glyphs containing:", sizeStyle='small', selectable=True )
		self.w.excludedGlyphNameParts = vanilla.EditText( (inset+150, linePos, -inset, 19), ".tf, .tosf, ord", callback=self.SavePreferences, sizeStyle='small' )
		self.w.excludedGlyphNameParts.getNSTextField().setToolTip_("If the glyph name includes any of these comma-separated fragments, the glyph will be ignored. Always excluded: Ldot, ldot, ldot.sc, Fhook and florin.")
		linePos += lineHeight
		
		self.w.openTab = vanilla.CheckBox( (inset, linePos-1, -inset, 20), u"Open new tab at first kern string.", value=False, callback=self.SavePreferences, sizeStyle='small' )
		self.w.openTab.getNSButton().setToolTip_("If checked, a new tab will be opened with the first found kern string, and the cursor positioned accordingly, ready for group kerning and switching to the next sample string.")
		linePos += lineHeight
		
		
		# Run Button:
		self.w.runButton = vanilla.Button( (-80-inset, -20-inset, -inset, -inset), "Add", sizeStyle='regular', callback=self.SampleStringMakerMain )
		self.w.setDefaultButton( self.w.runButton )
		
		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Sample String Maker' could not load preferences. Will resort to defaults")
		
		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		
	def SavePreferences( self, sender ):
		try:
			Glyphs.defaults["com.mekkablue.SampleStringMaker.scriptPopup"] = self.w.scriptPopup.get()
			Glyphs.defaults["com.mekkablue.SampleStringMaker.leftCategoryPopup"] = self.w.leftCategoryPopup.get()
			Glyphs.defaults["com.mekkablue.SampleStringMaker.rightCategoryPopup"] = self.w.rightCategoryPopup.get()
			Glyphs.defaults["com.mekkablue.SampleStringMaker.includeNonExporting"] = self.w.includeNonExporting.get()
			Glyphs.defaults["com.mekkablue.SampleStringMaker.excludedGlyphNameParts"] = self.w.excludedGlyphNameParts.get()
			Glyphs.defaults["com.mekkablue.SampleStringMaker.openTab"] = self.w.openTab.get()
		except:
			return False
			
		return True

	def LoadPreferences( self ):
		try:
			Glyphs.registerDefault("com.mekkablue.SampleStringMaker.scriptPopup", 0)
			Glyphs.registerDefault("com.mekkablue.SampleStringMaker.leftCategoryPopup", 0)
			Glyphs.registerDefault("com.mekkablue.SampleStringMaker.rightCategoryPopup", 0)
			Glyphs.registerDefault("com.mekkablue.SampleStringMaker.includeNonExporting", 0)
			Glyphs.registerDefault("com.mekkablue.SampleStringMaker.excludedGlyphNameParts", ".tf, .tosf, ord")
			Glyphs.registerDefault("com.mekkablue.SampleStringMaker.openTab", 1)
			self.w.scriptPopup.set( Glyphs.defaults["com.mekkablue.SampleStringMaker.scriptPopup"] )
			self.w.leftCategoryPopup.set( Glyphs.defaults["com.mekkablue.SampleStringMaker.leftCategoryPopup"] )
			self.w.rightCategoryPopup.set( Glyphs.defaults["com.mekkablue.SampleStringMaker.rightCategoryPopup"] )
			self.w.includeNonExporting.set( Glyphs.defaults["com.mekkablue.SampleStringMaker.includeNonExporting"] )
			self.w.excludedGlyphNameParts.set( Glyphs.defaults["com.mekkablue.SampleStringMaker.excludedGlyphNameParts"] )
			self.w.openTab.set( Glyphs.defaults["com.mekkablue.SampleStringMaker.openTab"] )
		except:
			return False
			
		return True

	def glyphNameIsExcluded(self, glyphName):
		forbiddenParts = [n.strip() for n in Glyphs.defaults["com.mekkablue.SampleStringMaker.excludedGlyphNameParts"].split(",")]
		for forbiddenPart in forbiddenParts:
			if forbiddenPart in glyphName:
				return True
		return False
	
	def SampleStringMakerMain( self, sender ):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences( self ):
				print("Note: 'Sample String Maker' could not write preferences.")
			
			thisFont = Glyphs.font # frontmost font
			print("Sample String Maker Report for %s" % thisFont.familyName)
			print(thisFont.filepath)
			print()
			
			leftChoice = self.categoryList[ Glyphs.defaults["com.mekkablue.SampleStringMaker.leftCategoryPopup"] ]
			rightChoice = self.categoryList[ Glyphs.defaults["com.mekkablue.SampleStringMaker.rightCategoryPopup"] ]
			chosenScript = self.scripts[ Glyphs.defaults["com.mekkablue.SampleStringMaker.scriptPopup"] ]
			leftCategory = leftChoice.split(":")[0]
			rightCategory = rightChoice.split(":")[0]
			
			leftSubCategory, rightSubCategory = None, None
			if ":" in leftChoice:
				leftSubCategory = leftChoice.split(":")[1]
			if ":" in rightChoice:
				rightSubCategory = rightChoice.split(":")[1]
				
			includeNonExporting = Glyphs.defaults["com.mekkablue.SampleStringMaker.includeNonExporting"]
			
			glyphNamesLeft = [ 
				g.name for g in thisFont.glyphs 
				if g.category == leftCategory
				and (
					leftSubCategory is None 
					or g.subCategory == leftSubCategory
					)
				and (
					g.script == chosenScript
					or (leftCategory != "Letter" and g.script is None)
					)
				and (g.export or includeNonExporting)
				and not g.name in self.exclusion
				and not self.glyphNameIsExcluded(g.name)
			]
			
			
			glyphNamesRight = [ 
				g.name for g in thisFont.glyphs 
				if g.category == rightCategory
				and (
					rightSubCategory is None 
					or g.subCategory == rightSubCategory
					)
				and (
					g.script == chosenScript
					or (rightCategory != "Letter" and g.script is None)
					)
				and (g.export or includeNonExporting)
				and not g.name in self.exclusion
				and not self.glyphNameIsExcluded(g.name)
			]
			
			print("Found %i left groups, %i right groups." % (
				len(glyphNamesLeft),
				len(glyphNamesRight),
			))
			
			linePrefix = "nonn"
			linePostfix = "noon"
				
			numberTriggers = ("Math","Currency","Decimal Digit")
			if leftSubCategory in numberTriggers or rightSubCategory in numberTriggers:
				linePrefix = "1200"
				linePostfix = "0034567"

			if leftSubCategory == "Uppercase":
				linePrefix = "HOOH"
			elif leftSubCategory == "Smallcaps":
				linePrefix = "/h.sc/o.sc/h.sc/h.sc"
			if rightSubCategory == "Smallcaps":
				linePostfix = "/h.sc/o.sc/o.sc/h.sc"
				
				
			# if rightSubCategory == "Uppercase":
			# 	linePostfix = "HOOH"

			kernStrings = sampleText.buildKernStrings( 
				glyphNamesLeft, glyphNamesRight, 
				thisFont=thisFont, 
				linePrefix=linePrefix, 
				linePostfix=linePostfix,
			)

			sampleText.executeAndReport( kernStrings )
			
			if Glyphs.defaults["com.mekkablue.SampleStringMaker.openTab"]:
				newTab = thisFont.newTab()
				sampleText.setSelectSampleTextIndex( thisFont, tab=newTab )
				cursorPos = 5
				if len(newTab.text) >= cursorPos:
					newTab.textCursor = cursorPos
			
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Sample String Maker Error: %s" % e)
			import traceback
			print(traceback.format_exc())

SampleStringMaker()
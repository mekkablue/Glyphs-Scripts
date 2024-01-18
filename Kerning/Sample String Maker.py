# MenuTitle: Sample String Maker
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Creates kern strings for all kerning groups in user-defined categories and adds them to the Sample Strings. Group kerning only, glyphs without groups are ignored.
"""

import vanilla
import sampleText
from GlyphsApp import Glyphs, Message
from mekkaCore import mekkaObject

CASE = (None, "Uppercase", "Lowercase", "Smallcaps", "Minor")


class SampleStringMaker(mekkaObject):
	prefDict = {
		"scriptPopup": 0,
		"leftCategoryPopup": 0,
		"rightCategoryPopup": 0,
		"includeNonExporting": 0,
		"excludedGlyphNameParts": ".tf, .tosf, ord, Ldot, ldot, .loclCAT",
		"openTab": 1,
		"lockKerning": 1,
		"overrideContext": 0,
		"contextGlyphs": "HOOH,noon",
		"mirrorPair": 0,
	}

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

	scripts = ("latin", "cyrillic", "greek")

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

	def __init__(self):
		# Window 'self.w':
		windowWidth = 340
		windowHeight = 265
		windowWidthResize = 1000  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Sample String Maker",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Builds group kern strings, adds them to the Sample Texts.", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.scriptText = vanilla.TextBox((inset, linePos + 2, 45, 14), "Script:", sizeStyle='small', selectable=True)
		self.w.scriptPopup = vanilla.PopUpButton((inset + 45, linePos, -inset, 17), self.scripts, sizeStyle='small', callback=self.SavePreferences)
		self.w.scriptPopup.getNSPopUpButton().setToolTip_("Script for letters, will be ignored for all other categories (e.g., numbers).")
		linePos += lineHeight

		self.w.leftCategoryText = vanilla.TextBox((inset, linePos + 2, 90, 14), "Left Category:", sizeStyle='small', selectable=True)
		self.w.leftCategoryPopup = vanilla.PopUpButton((inset + 90, linePos, -inset, 17), self.categoryList, sizeStyle='small', callback=self.SavePreferences)
		self.w.leftCategoryPopup.getNSPopUpButton().setToolTip_("Category:Subcategory for left side of kern pair.")
		linePos += lineHeight

		self.w.rightCategoryText = vanilla.TextBox((inset, linePos + 2, 90, 14), "Right Category:", sizeStyle='small', selectable=True)
		self.w.rightCategoryPopup = vanilla.PopUpButton((inset + 90, linePos, -inset, 17), self.categoryList, sizeStyle='small', callback=self.SavePreferences)
		self.w.rightCategoryPopup.getNSPopUpButton().setToolTip_("Category:Subcategory for right side of kern pair.")
		linePos += lineHeight

		self.w.includeNonExporting = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Also include non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeNonExporting.getNSButton().setToolTip_("Also add glyphs of these categories if they are set to not export.")
		linePos += lineHeight

		self.w.excludeText = vanilla.TextBox((inset, linePos + 2, 150, 14), "Exclude glyphs containing:", sizeStyle='small', selectable=True)
		self.w.excludedGlyphNameParts = vanilla.EditText((inset + 150, linePos, -inset, 19), ".tf, .tosf, ord, Ldot, ldot, .loclCAT", callback=self.SavePreferences, sizeStyle='small')
		self.w.excludedGlyphNameParts.getNSTextField(
		).setToolTip_("If the glyph name includes any of these comma-separated fragments, the glyph will be ignored. Always excluded: Ldot, ldot, ldot.sc, Fhook and florin.")
		linePos += lineHeight

		self.w.overrideContext = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Override context glyphs:", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.overrideContext.getNSButton().setToolTip_("If checked, the surrounding glyphs will be replaced with those given in the text box. Use a comma to differentiate the left-side context from the right-side context: ‘HOOH,noon’ will put HOOH on the left side, ‘noon’ on the right side.")
		self.w.contextGlyphs = vanilla.EditText((inset + 150, linePos, -inset, 19), "HOOH,noon", callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.mirrorPair = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Mirror kerning pair (AV→AVA)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.mirrorPair.getNSButton().setToolTip_("If checked, will create a mirrored version of the kerning string. E.g., instead of just AV, it will show AVA between the context glyphs.")
		linePos += lineHeight

		self.w.openTab = vanilla.CheckBox((inset, linePos - 1, 170, 20), "Open tab at first kern string", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.openTab.getNSButton().setToolTip_("If checked, a new tab will be opened with the first found kern string, and the cursor positioned accordingly, ready for group kerning and switching to the next sample string.")
		self.w.lockKerning = vanilla.CheckBox((inset + 170, linePos - 1, -inset, 20), "in kerning mode", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.lockKerning.getNSButton().setToolTip_("Will set the kerning lock in the tab, prevents you from spacing accidentally.")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Add", sizeStyle='regular', callback=self.SampleStringMakerMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Sample String Maker' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def glyphNameIsExcluded(self, glyphName):
		forbiddenParts = [n.strip() for n in self.pref("excludedGlyphNameParts").split(",")]
		for forbiddenPart in forbiddenParts:
			if forbiddenPart in glyphName:
				return True
		return False

	def parseTheContextGlyphs(self):
		separator = ","
		txt = self.pref("contextGlyphs")
		if separator in txt:
			linePrefix, linePostfix = txt.split(separator)[:2]
		else:
			linePrefix, linePostfix = txt, txt
		return linePrefix, linePostfix

	def SampleStringMakerMain(self, sender):
		try:
			# update settings to the latest user input:
			if not self.SavePreferences(self):
				print("Note: 'Sample String Maker' could not write preferences.")

			thisFont = Glyphs.font  # frontmost font
			print("Sample String Maker Report for %s" % thisFont.familyName)
			print(thisFont.filepath)
			print()

			leftChoice = self.categoryList[self.pref("leftCategoryPopup")]
			rightChoice = self.categoryList[self.pref("rightCategoryPopup")]
			chosenScript = self.scripts[self.pref("scriptPopup")]
			leftCategory = leftChoice.split(":")[0]
			rightCategory = rightChoice.split(":")[0]

			leftSubCategory, rightSubCategory = None, None
			if ":" in leftChoice:
				leftSubCategory = leftChoice.split(":")[1]
			if ":" in rightChoice:
				rightSubCategory = rightChoice.split(":")[1]

			includeNonExporting = self.pref("includeNonExporting")

			glyphNamesLeft, glyphNamesRight = [], []
			for g in thisFont.glyphs:
				glyphSubCategory = g.subCategory
				if Glyphs.versionNumber >= 3:
					if glyphSubCategory is None:
						glyphSubCategory = CASE[g.case]

				# LEFT
				if g.category == leftCategory and \
					(leftSubCategory is None or glyphSubCategory == leftSubCategory) and \
					(g.script == chosenScript or (leftCategory != "Letter" and g.script is None)) and \
					(g.export or includeNonExporting) and \
					g.name not in self.exclusion and \
					not self.glyphNameIsExcluded(g.name):
					glyphNamesLeft.append(g.name)

				# RIGHT
				if g.category == rightCategory and \
					(rightSubCategory is None or glyphSubCategory == rightSubCategory) and \
					(g.script == chosenScript or (rightCategory != "Letter" and g.script is None)) and \
					(g.export or includeNonExporting) and \
					g.name not in self.exclusion and \
					not self.glyphNameIsExcluded(g.name):
					glyphNamesRight.append(g.name)

			numLeftGlyphs = len(glyphNamesLeft)
			numRightGlyphs = len(glyphNamesRight)

			print("Found %i left glyphs, %i right glyphs." % (numLeftGlyphs, numRightGlyphs))

			linePrefix = "nonn"
			linePostfix = "noon"

			numberTriggers = ("Math", "Currency", "Decimal Digit")
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
			if self.pref("overrideContext"):
				linePrefix, linePostfix = self.parseTheContextGlyphs()

			mirrorPair = False
			if self.pref("mirrorPair"):
				mirrorPair = True

			kernStrings = sampleText.buildKernStrings(glyphNamesLeft, glyphNamesRight, thisFont=thisFont, linePrefix=linePrefix, linePostfix=linePostfix, mirrorPair=mirrorPair)

			if not kernStrings:
				if numLeftGlyphs * numRightGlyphs == 0:
					Message(
						title="No Kern Strings Created",
						message="The current settings are too strict. Found %i left, %i right glyphs, no kerning combinations could be built." % (numLeftGlyphs, numRightGlyphs),
						OKButton=None
					)
				else:
					Message(
						title="No Kern Strings Created",
						message="Could not build any kerning combinations with available groups. Make sure groups are set for the chosen glyphs.",
						OKButton=None
					)
				print("No kern strings built. Done.")
			else:
				sampleText.executeAndReport(kernStrings)

				if self.pref("openTab"):
					newTab = thisFont.newTab()
					if Glyphs.versionNumber >= 3:
						sampleText.setSelectSampleTextIndex(thisFont, tab=newTab, marker="Sample String Maker")
					else:
						sampleText.setSelectSampleTextIndex(thisFont, tab=newTab)
					cursorPos = 5
					if len(newTab.text) >= cursorPos:
						newTab.textCursor = cursorPos

					# set it to lock kerning:
					if self.pref("lockKerning"):
						newTab.graphicView().setDoSpacing_(0)
						newTab.graphicView().setDoKerning_(1)
						newTab.updateKerningButton()

				self.w.close()

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Sample String Maker Error: %s" % e)
			import traceback
			print(traceback.format_exc())


Glyphs.clearLog()
SampleStringMaker()

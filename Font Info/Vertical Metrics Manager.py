# MenuTitle: Vertical Metrics Manager
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:  # noqa: F841
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")
__doc__ = """
Manage and sync ascender, descender and linegap values for hhea, OS/2 sTypo and OS/2 usWin.
"""

import vanilla, string
from GlyphsApp import Glyphs, Message, GetOpenFile, GSUppercase, GSLowercase, GSGlyph, GSLayer
from mekkablue import mekkaObject, UpdateButton
from AppKit import NSRightTextAlignment


def topEdge(rect):
	return rect.origin.y + rect.size.height


def bottomEdge(rect):
	return rect.origin.y


def glyphHeight(glyph):
	return max([topEdge(l.bounds) for l in glyph.layers if l.isMasterLayer or l.isSpecialLayer])


def glyphDepth(glyph):
	return min([bottomEdge(l.bounds) for l in glyph.layers if l.isMasterLayer or l.isSpecialLayer])


def cleanInt(numberString):
	exportString = ""
	numberString = str(numberString)
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
		sign = x / abs(x)  # +1 or -1
		factor = 0
		if x % roundBy:
			factor = 1
		return int((abs(x) // roundBy * roundBy + factor * roundBy) * sign)


class VerticalMetricsManager(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"allOpenFonts": 0,
		"preferSelectedGlyphs": 0,
		"preferCategory": 0,
		"preferScript": 0,
		"ignoreNonExporting": 1,
		"includeAllMasters": 1,
		"respectMarkToBaseOffset": 0,
		"writeToPopup": 0,
		"round": 1,
		"roundValue": 10,
		"useTypoMetrics": 1,
		"hheaGap": 0,
		"hheaDesc": 0,
		"hheaAsc": 0,
		"typoGap": 0,
		"typoDesc": 0,
		"typoAsc": 0,
		"winDesc": 0,
		"winAsc": 0,
		"calculate": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 330
		windowHeight = 540
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Vertical Metrics Manager",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight, fieldWidth = 10, 15, 22, 60

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Manage and sync hhea, typo and win values:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.titleAscent = vanilla.TextBox((inset + 70, linePos + 4, 70, 14), "Ascender", sizeStyle='small', selectable=True)
		self.w.titleDescent = vanilla.TextBox((inset + 140, linePos + 4, 70, 14), "Descender", sizeStyle='small', selectable=True)
		self.w.titleLineGap = vanilla.TextBox((inset + 210, linePos + 4, 70, 14), "Line Gap", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.titleWin = vanilla.TextBox((inset, linePos + 3, 70, 14), "OS/2 usWin", sizeStyle='small', selectable=True)
		self.w.winAsc = vanilla.EditText((inset + 70, linePos, fieldWidth, 19), "", callback=self.SavePreferences, sizeStyle='small')
		self.w.winAsc.getNSTextField().setToolTip_("OS/2 usWinAscent. Should be the maximum height in your font. Expect clipping or rendering artefacts beyond this point.")
		self.w.winDesc = vanilla.EditText((inset + 140, linePos, fieldWidth, 19), "", callback=self.SavePreferences, sizeStyle='small')
		self.w.winDesc.getNSTextField().setToolTip_("OS/2 usWinDescent (unsigned integer). Should be the maximum depth in your font, like the lowest descender you have. Expect clipping or rendering artefacts beyond this point.")
		self.w.winGap = vanilla.EditText((inset + 210, linePos, fieldWidth, 19), "", callback=None, sizeStyle='small', readOnly=True, placeholder="n/a")
		self.w.winGap.getNSTextField().setToolTip_("OS/2 usWinLineGap does not exist, hence greyed out here.")
		self.w.winUpdate = UpdateButton((-inset - 18, linePos - 1, -inset, 18), callback=self.update)
		self.w.winUpdate.getNSButton().setToolTip_("Will recalculate the OS/2 usWin values in the fields to the left. Takes the measurement settings below into account, except for the Limit options.")
		linePos += lineHeight + 6

		self.w.parenTypo = vanilla.TextBox((inset - 12, linePos + 3, 15, 20), "┏", sizeStyle='small', selectable=False)
		self.w.titleTypo = vanilla.TextBox((inset, linePos + 3, 70, 14), "OS/2 sTypo", sizeStyle='small', selectable=True)
		self.w.typoAsc = vanilla.EditText((inset + 70, linePos, fieldWidth, 19), "", callback=self.SavePreferences, sizeStyle='small')
		self.w.typoAsc.getNSTextField().setToolTip_("OS/2 sTypoAscender (positive value), should be the same as hheaAscender. Should be the maximum height of the glyphs relevant for horizontal text setting in your font, like the highest accented uppercase letter, typically Aring or Ohungarumlaut. Used for first baseline offset in DTP and office apps and together with the line gap value, also in browsers.")
		self.w.typoDesc = vanilla.EditText((inset + 140, linePos, fieldWidth, 19), "", callback=self.SavePreferences, sizeStyle='small')
		self.w.typoDesc.getNSTextField().setToolTip_("OS/2 sTypoDescender (negative value), should be the same as hheaDescender. Should be the maximum depth of the glyphs relevant for horizontal text setting in your font, like the lowest descender or bottom accent, typically Gcommaccent, Ccedilla, or one of the lowercase descenders (gjpqy). Together with the line gap value, used for line distance calculation in office apps and browsers.")
		self.w.typoGap = vanilla.EditText((inset + 210, linePos, fieldWidth, 19), "", callback=self.SavePreferences, sizeStyle='small')
		self.w.typoGap.getNSTextField().setToolTip_("OS/2 sTypoLineGap (positive value), should be the same as hheaLineGap. Should be either zero or a value for padding between lines that makes sense visually. Office apps insert this distance between the lines, browsers add half on top and half below each line, also for determining text object boundaries.")
		self.w.typoUpdate = UpdateButton((-inset - 18, linePos - 1, -inset, 18), callback=self.update)
		self.w.typoUpdate.getNSButton().setToolTip_("Will recalculate the OS/2 sTypo values in the fields to the left. Takes the measurement settings below into account.")
		linePos += lineHeight

		self.w.parenConnect = vanilla.TextBox((inset - 12, linePos - int(lineHeight / 2) + 3, 15, 20), "┃", sizeStyle='small', selectable=False)
		self.w.parenHhea = vanilla.TextBox((inset - 12, linePos + 4, 15, 20), "┗", sizeStyle='small', selectable=False)
		self.w.titleHhea = vanilla.TextBox((inset, linePos + 3, 70, 14), "hhea", sizeStyle='small', selectable=True)
		self.w.hheaAsc = vanilla.EditText((inset + 70, linePos, fieldWidth, 19), "", callback=self.SavePreferences, sizeStyle='small')
		self.w.hheaAsc.getNSTextField().setToolTip_("hheaAscender (positive value), should be the same as OS/2 sTypoAscender. Should be the maximum height of the glyphs relevant for horizontal text setting in your font, like the highest accented uppercase letter, typically Aring or Ohungarumlaut. Used for first baseline offset in Mac office apps and together with the line gap value, also in Mac browsers.")
		self.w.hheaDesc = vanilla.EditText((inset + 140, linePos, fieldWidth, 19), "", callback=self.SavePreferences, sizeStyle='small')
		self.w.hheaDesc.getNSTextField().setToolTip_("hheaDescender (negative value), should be the same as OS/2 sTypoDescender. Should be the maximum depth of the glyphs relevant for horizontal text setting in your font, like the lowest descender or bottom accent, typically Gcommaccent, Ccedilla, or one of the lowercase descenders (gjpqy). Together with the line gap value, used for line distance calculation in office apps and browsers.")
		self.w.hheaGap = vanilla.EditText((inset + 210, linePos, fieldWidth, 19), "", callback=self.SavePreferences, sizeStyle='small')
		self.w.hheaGap.getNSTextField().setToolTip_("hheaLineGap (positive value), should be the same as OS/2 sTypoLineGap. Should be either zero or a value for padding between lines that makes sense visually. Mac office apps insert this distance between the lines, Mac browsers add half on top and half below each line, also for determining text object boundaries.")
		self.w.hheaUpdate = UpdateButton((-inset - 18, linePos - 1, -inset, 18), callback=self.update)
		self.w.hheaUpdate.getNSButton().setToolTip_("Will copy the typo values into the hhea values (should always be in sync), unless typo values are not set. In that case, will recalculate the hhea values in the fields to the left. Takes the measurement settings below into account.")
		linePos += lineHeight

		# right align:
		for textCell in (self.w.winAsc, self.w.winDesc, self.w.typoAsc, self.w.typoDesc, self.w.typoGap, self.w.hheaAsc, self.w.hheaDesc, self.w.hheaGap):
			textCell.getNSTextField().setAlignment_(NSRightTextAlignment)

		self.w.useTypoMetrics = vanilla.CheckBox((inset + 57, linePos + 6, -inset, 18), "Use Typo Metrics (fsSelection bit 7)", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.useTypoMetrics.getNSButton().setToolTip_("Should ALWAYS BE ON. Only uncheck if you really know what you are doing. If unchecked, line behaviour will not be consistent between apps and browsers because some apps prefer win values to sTypo values for determining line distances.")
		self.w.useTypoMetricsUpdate = UpdateButton((-inset - 18, linePos + 3, -inset, 18), callback=self.update)
		self.w.useTypoMetricsUpdate.getNSButton().setToolTip_("Will reset the checkbox to the left to ON, because it should ALWAYS be on. Strongly recommended.")
		linePos += int(lineHeight * 1.4)
		
		# METHODS
		self.w.separatorMethods = vanilla.HorizontalLine((inset, linePos, -inset, 6))
		linePos += lineHeight - 7
		
		self.w.descriptionMethods = vanilla.TextBox((inset, linePos, -inset, 14), "Vertical metrics methods:", sizeStyle="small", selectable=True)
		linePos += lineHeight
		
		self.w.calculateText = vanilla.TextBox((inset, linePos+2, 70, 14), "Use method", sizeStyle="small", selectable=True)
		self.w.calculate = vanilla.PopUpButton((inset+70, linePos, -80-inset, 17), ("Google", "Webfonts (2019)", "Microsoft (Legacy)"), sizeStyle="small", callback=self.SavePreferences)
		self.w.calculateButton = vanilla.Button((-70 - inset, linePos, -inset, 17), "Calculate", sizeStyle="small", callback=self.calculateMethod)
		
		linePos += lineHeight
		
		
		
		# EXTRACT FROM EXISTING FONT
		self.w.extractText = vanilla.TextBox((inset, linePos + 2, -70 - inset, 14), "Copy values from existing OpenType font:", sizeStyle="small", selectable=True)
		self.w.extractButton = vanilla.Button((-70 - inset, linePos, -inset, 17), "Extract", sizeStyle="small", callback=self.extract)
		self.w.extractButton.getNSButton().setToolTip_("Extracts values from an existing compiled font (.otf or .ttf) and inserts them in the fields above. Useful if you need to stay in sync with a pre-existing font.")
		linePos += int(lineHeight * 1.2)

		self.w.separator = vanilla.HorizontalLine((inset, linePos, -inset, 6))
		linePos += lineHeight - 7
		
		# MEASUREMENT SETTINGS
		self.w.descriptionMeasurements = vanilla.TextBox((inset, linePos, -inset, 14), "Taking measurements (see tooltips for info):", sizeStyle='small')
		linePos += lineHeight

		self.w.round = vanilla.CheckBox((inset + 2, linePos, 70, 18), "Round by", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.round.getNSButton().setToolTip_("Turn on if you want your values rounded. Recommended.")
		self.w.roundValue = vanilla.EditText((inset + 70, linePos - 1, 60, 19), "10", callback=self.SavePreferences, sizeStyle='small')
		self.w.roundValue.getNSTextField().setToolTip_("All value calculations will be rounded up to the next multiple of this value. Recommended: 10.")
		linePos += lineHeight

		self.w.includeAllMasters = vanilla.CheckBox((inset + 2, linePos, -inset, 18), "Include all masters (otherwise current master only)", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeAllMasters.getNSButton().setToolTip_("If checked, all masters will be measured. If unchecked, only the current master will be measured. Since vertical metrics should be the same throughout all masters, it also makes sense to measure on all masters.")
		linePos += lineHeight

		self.w.respectMarkToBaseOffset = vanilla.CheckBox((inset + 2, linePos, -inset, 18), "Include mark-to-base offset for OS/2 usWin", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.respectMarkToBaseOffset.getNSButton().setToolTip_("If checked will calculate the maximum possible height that can be reached with top-anchored marks, and the lowest depth with bottom-anchored marks, and use those values for the OS/2 usWin values. Strongly recommended for making fonts work on Windows if they rely on mark-to-base positioning (e.g. Arabic). Respects the ‘Limit to Script’ setting.")
		linePos += lineHeight

		self.w.ignoreNonExporting = vanilla.CheckBox((inset + 2, linePos, -inset, 18), "Ignore non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.ignoreNonExporting.getNSButton().setToolTip_("If checked, glyphs that do not export will be excluded from measuring. Recommended. (Ignored for calculating the OS/2 usWin values.)")
		linePos += lineHeight

		self.w.preferSelectedGlyphs = vanilla.CheckBox((inset + 2, linePos, -inset, 20), "Limit to selected glyphs", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.preferSelectedGlyphs.getNSButton().setToolTip_("If checked, only the current glyphs will be measured. Can be combined with the other Limit options. May make sense if you want your metrics to be e.g. Latin-CE-centric.")
		linePos += lineHeight

		self.w.preferScript = vanilla.CheckBox((inset + 2, linePos, inset + 110, 18), "Limit to script", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.preferScript.getNSButton().setToolTip_("If checked, only measures glyphs belonging to the selected writing system. Can be combined with the other Limit options. (Ignored for calculating the OS/2 usWin values, but respected for mark-to-base calculation.)")
		self.w.preferScriptPopup = vanilla.PopUpButton((inset + 108, linePos, -inset - 22, 17), ("latin", "greek"), sizeStyle='small', callback=self.SavePreferences)
		self.w.preferScriptPopup.getNSPopUpButton().setToolTip_("Choose a writing system ('script') you want the measurements to be limited to. May make sense to ignore other scripts if the font is intended only for e.g. Cyrillic. Does not apply to OS/2 usWin")
		self.w.preferScriptUpdate = UpdateButton((-inset - 18, linePos - 2, -inset, 18), callback=self.update)
		self.w.preferScriptUpdate.getNSButton().setToolTip_("Update the script popup to the left with all scripts (writing systems) found in the current font.")
		linePos += lineHeight

		self.w.preferCategory = vanilla.CheckBox((inset + 2, linePos, inset + 110, 18), "Limit to category", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.preferCategory.getNSButton().setToolTip_("If checked, only measures glyphs belonging to the selected glyph category. Can be combined with the other Limit options. (Ignored for calculating the OS/2 usWin values.)")
		self.w.preferCategoryPopup = vanilla.PopUpButton((inset + 108, linePos, -inset - 22, 17), ("Letter", "Number"), sizeStyle='small', callback=self.SavePreferences)
		self.w.preferCategoryPopup.getNSPopUpButton().setToolTip_("Choose a glyph category you want the measurements to be limited to. It may make sense to limit only to Letter.")
		self.w.preferCategoryUpdate = UpdateButton((-inset - 18, linePos - 2, -inset, 18), callback=self.update)
		self.w.preferCategoryUpdate.getNSButton().setToolTip_("Update the category popup to the left with all glyph categories found in the current font.")
		linePos += int(lineHeight * 1.2)

		self.w.separatorAction = vanilla.HorizontalLine((inset, linePos, -inset, 6))
		linePos += lineHeight - 7

		self.w.writeToText = vanilla.TextBox((inset, linePos + 2, 90, 14), "Write values to", sizeStyle="small", selectable=True)
		self.w.writeToPopup = vanilla.PopUpButton((inset + 90, linePos, -inset-22, 17), ("All masters (recommended)", "First master only (experimental)", "Font-wide (experimental)"), sizeStyle="small", callback=self.SavePreferences)
		linePos += lineHeight

		self.w.allOpenFonts = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "⚠️ Read out and apply to ALL open fonts", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.allOpenFonts.getNSButton().setToolTip_("If activated, does not only measure the frontmost font, but all open fonts. Careful: when you press the Apply button, will also apply it to all open fonts. Useful if you have all font files for a font family open.")
		linePos += lineHeight

		# Run Button:
		self.w.helpButton = vanilla.HelpButton((inset - 2, -20 - inset, 21, -inset + 2), callback=self.openURL)
		self.w.helpButton.getNSButton().setToolTip_("Opens the Vertical Metrics tutorial (highly recommended) in your web browser.")

		self.w.runButton = vanilla.Button((-120 - inset, -20 - inset, -inset, -inset), "Apply to Font", callback=self.VerticalMetricsManagerMain)
		self.w.runButton.getNSButton().setToolTip_("Insert the OS/2, hhea and fsSelection values above as custom parameters in the font. The number values will be inserted into each master. Blank values will delete the respective parameters.")
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()


	def updateUI(self, sender=None):
		self.w.includeAllMasters.enable(not self.w.allOpenFonts.get())
		self.w.runButton.setTitle(f'Apply to Font{"s" if self.w.allOpenFonts.get() else ""}')


	def openURL(self, sender):
		URL = None
		if sender == self.w.helpButton:
			URL = "https://glyphsapp.com/tutorials/vertical-metrics"
		if URL:
			import webbrowser
			webbrowser.open(URL)


	def extract(self, sender=None):
		Glyphs.clearLog()  # clears macro window log

		sourceFile = GetOpenFile(
			message="Choose font file (.otf or .ttf) for vertical metrics",
			allowsMultipleSelection=False,
			filetypes=("otf", "ttf", "woff", "woff2"),
		)
		if not sourceFile:
			print("❌ No font file specified for extracting vertical metrics.")
			return

		# extract from font file with fontTools:
		# import fontTools
		from fontTools import ttLib
		font = ttLib.TTFont(sourceFile)
		os2Table = font["OS/2"]
		hheaTable = font["hhea"]
		extractedValues = {
			"winAsc": os2Table.usWinAscent,
			"winDesc": os2Table.usWinDescent,
			"typoAsc": os2Table.sTypoAscender,
			"typoDesc": os2Table.sTypoDescender,
			"typoGap": os2Table.sTypoLineGap,
			"hheaAsc": hheaTable.ascender,
			"hheaDesc": hheaTable.descender,
			"hheaGap": hheaTable.lineGap,
			"useTypoMetrics": int(os2Table.fsSelection & (2**7) == 2**7),
		}

		# set prefs, update UI:
		print(f"📄 Extracting from: {sourceFile}\n")
		for verticalMetric in extractedValues.keys():
			print(f"📤 {verticalMetric} = {extractedValues[verticalMetric]}")
			self.setPref(verticalMetric, extractedValues[verticalMetric])
		self.LoadPreferences()
		print("✅ Done.")


	def chosenGlyphs(self, font):
		if not font:
			return []

		shouldLimitToScript = self.pref("preferScript")
		selectedScript = self.w.preferScriptPopup.getTitle()
		shouldLimitToCategory = self.pref("preferCategory")
		selectedCategory = self.w.preferCategoryPopup.getTitle()
		ignoreNonExporting = self.pref("ignoreNonExporting")
		shouldLimitToSelectedGlyphs = self.pref("preferSelectedGlyphs")
		if font.selectedLayers:
			selectedGlyphNames = [l.parent.name for l in font.selectedLayers if isinstance(l, GSLayer)]
		else:
			selectedGlyphNames = []
		
		glyphs = []
		for glyph in font.allGlyphs():
			if shouldLimitToScript and glyph.script != selectedScript:
				continue
			if shouldLimitToCategory and glyph.category != selectedCategory:
				continue
			if ignoreNonExporting and not glyph.export:
				continue
			if shouldLimitToSelectedGlyphs and glyph.name not in selectedGlyphNames:
				continue
			glyphs.append(glyph)
		
		return glyphs


	def update(self, sender=None):
		Glyphs.clearLog()  # clears macro window log

		# update settings to the latest user input:
		self.SavePreferences()

		frontmostFont = Glyphs.font
		allOpenFonts = self.pref("allOpenFonts")
		if allOpenFonts:
			theseFonts = Glyphs.fonts
		else:
			theseFonts = (frontmostFont, )  # iterable tuple of frontmost font only

		# theseFamilyNames = [f.familyName for f in theseFonts]
		print("\nVertical Metrics Manager\nUpdating values for:\n")
		for i, thisFont in enumerate(theseFonts):
			print(f"{i + 1}. {thisFont.familyName}:")
			if thisFont.filepath:
				print(thisFont.filepath)
			else:
				print("⚠️ The font file has not been saved yet.")
			print()

		ignoreNonExporting = self.pref("ignoreNonExporting")
		includeAllMasters = self.pref("includeAllMasters")
		shouldRound = self.pref("round")
		roundValue = self.prefInt("roundValue")
		respectMarkToBaseOffset = self.pref("respectMarkToBaseOffset")
		shouldLimitToScript = self.pref("preferScript")
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
			for i, thisFont in enumerate(theseFonts):
				if allOpenFonts and len(theseFonts) > 1:
					fontReport = f"{i + 1}. {thisFont.familyName}, "
				currentMaster = thisFont.selectedFontMaster
				for thisGlyph in thisFont.allGlyphs():
					if not thisGlyph.export and ignoreNonExporting:
						continue
					scriptCheckOK = not shouldLimitToScript or thisGlyph.script == selectedScript  # needed for respectMarkToBaseOffset

					for thisLayer in thisGlyph.layers:
						belongsToCurrentMaster = thisLayer.associatedFontMaster() == currentMaster
						if not(belongsToCurrentMaster or includeAllMasters or allOpenFonts):
							continue
						if not thisLayer.isSpecialLayer and not thisLayer.isMasterLayer:
							continue
						lowestPointInLayer = thisLayer.bounds.origin.y
						highestPointInLayer = lowestPointInLayer + thisLayer.bounds.size.height
						if lowestPointInLayer < lowest:
							lowest = lowestPointInLayer
							lowestGlyph = f"{fontReport}{thisGlyph.name}, layer: {thisLayer.name}"
						if highestPointInLayer > highest:
							highest = highestPointInLayer
							highestGlyph = f"{fontReport}{thisGlyph.name}, layer: {thisLayer.name}"

						# respectMarkToBaseOffset:
						if respectMarkToBaseOffset and scriptCheckOK:
							allAnchors = thisLayer.anchorsTraversingComponents()
							if not allAnchors:
								continue
							if thisGlyph.category == "Mark":
								topAnchors = [a for a in allAnchors if a.name == "_top"]
								if topAnchors:
									topAnchor = topAnchors[0]
									topSpan = highestPointInLayer - topAnchor.y
									if topSpan > largestTopMark:
										largestTopMark = topSpan
										largestTopMarkGlyph = f"{fontReport}{thisGlyph.name}, layer: {thisLayer.name}"
								bottomAnchors = [a for a in allAnchors if a.name == "_bottom"]
								if bottomAnchors:
									bottomAnchor = bottomAnchors[0]
									bottomSpan = abs(lowestPointInLayer - bottomAnchor.y)
									if bottomSpan > largestBottomMark:
										largestBottomMark = bottomSpan
										largestBottomMarkGlyph = f"{fontReport}{thisGlyph.name}, layer: {thisLayer.name}"
							else:
								topAnchors = [a for a in allAnchors if a.name == "top"]
								if topAnchors:
									topAnchor = topAnchors[0]
									if topAnchor.y > highestTopAnchor:
										highestTopAnchor = topAnchor.y
										highestTopAnchorGlyph = f"{fontReport}{thisGlyph.name}, layer: {thisLayer.name}"
								bottomAnchors = [a for a in allAnchors if a.name == "bottom"]
								if bottomAnchors:
									bottomAnchor = bottomAnchors[0]
									if bottomAnchor.y < lowestBottomAnchor:
										lowestBottomAnchor = bottomAnchor.y
										lowestBottomAnchorGlyph = f"{fontReport}{thisGlyph.name}, layer: {thisLayer.name}"

			print("Highest relevant glyph:")
			print(f"- {highestGlyph} (highest)")
			print()
			print("Lowest relevant glyph:")
			print(f"- {lowestGlyph} (lowest)")
			print()

			if respectMarkToBaseOffset:
				highestMarkToBase = highestTopAnchor + largestTopMark
				lowestMarkToBase = lowestBottomAnchor - largestBottomMark

				print("Highest top anchor:")
				print(f"- {highestTopAnchorGlyph} ({highestTopAnchor})")
				print("Largest top mark span (_top to top edge):")
				print(f"- {largestTopMarkGlyph} ({largestTopMark})")
				print(f"Highest possible mark-to-base: {highestTopAnchor} + {largestTopMark} = {highestMarkToBase}")
				print()
				print("Lowest bottom anchor:")
				print(f"- {lowestBottomAnchorGlyph} ({lowestBottomAnchor})")
				print("Largest bottom mark span (_bottom to bottom edge):")
				print(f"- {largestBottomMarkGlyph} ({largestBottomMark})")
				print(f"Lowest possible mark-to-base: {lowestBottomAnchor} - {largestBottomMark} = {lowestMarkToBase}")
				print()

				if lowestMarkToBase < lowest:
					lowest = lowestMarkToBase
				if highestMarkToBase > highest:
					highest = highestMarkToBase

			if shouldRound:
				highest = roundUpByValue(highest, roundValue)
				lowest = roundUpByValue(lowest, roundValue)

			winAsc = int(highest)
			winDesc = abs(int(lowest))

			print("Calculated values:")
			print("- usWinAscent: %s" % winAsc)
			print("- usWinDescent: %s" % winDesc)
			print()

			self.setPref("winAsc", winAsc)
			self.setPref("winDesc", winDesc)

		# Use Typo Metrics checkbox
		elif sender == self.w.useTypoMetricsUpdate:
			print("Use Typo Metrics (fsSelection bit 7) should always be YES.\n")
			self.setPref("useTypoMetrics", True)

		# hhea and typo popups:
		elif sender in (self.w.hheaUpdate, self.w.typoUpdate):
			if sender == self.w.hheaUpdate:
				name = "hhea"
			else:
				name = "OS/2 sTypo"

			print(f"Determining {name} values:\n")

			if sender == self.w.hheaUpdate and self.pref("typoAsc") and self.pref("typoDesc"):
				print("💞 Copying existing OS/2 sTypo values into hhea values...\n")
				asc = cleanInt(self.pref("typoAsc"))
				desc = cleanInt(self.pref("typoDesc"))
				gap = cleanInt(self.pref("typoGap"))
			else:
				lowest, highest = 0.0, 0.0
				lowestGlyph, highestGlyph = None, None

				shouldLimitToCategory = self.pref("preferCategory")
				shouldLimitToScript = self.pref("preferScript")
				shouldLimitToSelectedGlyphs = self.pref("preferSelectedGlyphs")
				selectedCategory = self.w.preferCategoryPopup.getTitle()
				selectedScript = self.w.preferScriptPopup.getTitle()

				if shouldLimitToSelectedGlyphs:
					selectedGlyphNames = [layer.parent.name for layer in frontmostFont.selectedLayers]
					if not selectedGlyphNames:
						print("⚠️ Ignoring limitation to selected glyphs because no glyphs are selected (in frontmost font).")
						shouldLimitToSelectedGlyphs = False
						self.setPref("preferSelectedGlyphs", shouldLimitToSelectedGlyphs)
						self.LoadPreferences()
				else:
					selectedGlyphNames = ()

				for i, thisFont in enumerate(theseFonts):
					if allOpenFonts and len(theseFonts) > 1:
						fontReport = f"{i + 1}. {thisFont.familyName}, "
					else:
						fontReport = ""

					currentMaster = thisFont.selectedFontMaster

					# ascender & descender calculation:
					for thisGlyph in self.chosenGlyphs(thisFont):
						for thisLayer in thisGlyph.layers:
							belongsToCurrentMaster = thisLayer.associatedFontMaster() == currentMaster
							if not(belongsToCurrentMaster or includeAllMasters or allOpenFonts):
								continue
							if not thisLayer.isSpecialLayer and not thisLayer.isMasterLayer:
								continue
							lowestPointInLayer = thisLayer.bounds.origin.y
							highestPointInLayer = lowestPointInLayer + thisLayer.bounds.size.height
							if lowestPointInLayer < lowest:
								lowest = lowestPointInLayer
								lowestGlyph = f"{fontReport}{thisGlyph.name}, layer: {thisLayer.name}"
							if highestPointInLayer > highest:
								highest = highestPointInLayer
								highestGlyph = f"{fontReport}{thisGlyph.name}, layer: {thisLayer.name}"

				print("Highest relevant glyph:")
				print(f"- {highestGlyph} ({highest})\n")
				print("Lowest relevant glyph:")
				print(f"- {lowestGlyph} ({lowest})\n")

				if shouldRound:
					highest = roundUpByValue(highest, roundValue)
					lowest = roundUpByValue(lowest, roundValue)

				asc = int(highest)
				desc = int(lowest)

				# line gap calculation:
				xHeight = 0
				for thisFont in theseFonts:
					# determine highest x-height:
					for thisMaster in thisFont.masters:
						measuredX = thisMaster.xHeight
						if measuredX >= thisMaster.capHeight or measuredX > thisFont.upm * 5:  # all caps font or NSNotFound
							measuredX = thisMaster.capHeight / 2
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
				actualLineSpan = abs(asc) + abs(desc)
				if idealLineSpan > actualLineSpan:
					gap = idealLineSpan - actualLineSpan
					if shouldRound:
						gap = roundUpByValue(gap, roundValue)
				else:
					gap = 0

				if gap > thisFont.upm * 5:  # probably NSNotFound
					gap = 0

				print("Calculated values:")
				print(f"- {name} Ascender: {asc}")
				print(f"- {name} Descender: {desc}")
				print(f"- {name} LineGap: {gap}")
				print()

			if sender == self.w.hheaUpdate:
				self.setPref("hheaAsc", asc)
				self.setPref("hheaDesc", desc)
				self.setPref("hheaGap", gap)
			else:
				self.setPref("typoAsc", asc)
				self.setPref("typoDesc", desc)
				self.setPref("typoGap", gap)

		# Updating "Limit to Script" popup:
		elif sender == self.w.preferScriptUpdate:
			scripts = []
			shouldIgnoreNonExporting = self.pref("ignoreNonExporting")
			for thisGlyph in frontmostFont.allGlyphs():
				inclusionCheckOK = thisGlyph.export or not shouldIgnoreNonExporting
				if inclusionCheckOK and thisGlyph.script and thisGlyph.script not in scripts:
					scripts.append(thisGlyph.script)
			if scripts:
				self.w.preferScriptPopup.setItems(scripts)
				print(f"✅ Found scripts:\n{', '.join(scripts)}")
			else:
				msg = "Found no glyphs belonging to any script in the frontmost font. Please double check."
				print(f"⚠️ {msg}")
				Message(
					title="Error Determining Scripts",
					message=f"Cannot determine list of scripts. {msg}",
					OKButton=None,
				)

		# Updating "Limit to Category" popup:
		elif sender == self.w.preferCategoryUpdate:
			categories = []
			shouldIgnoreNonExporting = self.pref("ignoreNonExporting")
			for thisGlyph in thisFont.allGlyphs():
				inclusionCheckOK = thisGlyph.export or not shouldIgnoreNonExporting
				if inclusionCheckOK and thisGlyph.category not in categories:
					categories.append(thisGlyph.category)
			if categories:
				self.w.preferCategoryPopup.setItems(categories)
				print(f"✅ Found categories:\n{', '.join(categories)}")
			else:
				msg = "Found no glyphs belonging to any category in the current font. Please double check."
				print(f"⚠️ {msg}")
				Message(
					title="Error Determining Categories",
					message=f"Cannot determine list of categories. {msg}", 
					OKButton=None,
					)

		self.LoadPreferences()

		print(f"🔢 OS/2.winAscent     {cleanInt(self.pref('winAsc')):5}")
		print(f"🔢 OS/2.winDescent    {cleanInt(self.pref('winDesc')):5}")
		print(f"🔢 OS/2.typoAscender  {cleanInt(self.pref('typoAsc')):5}")
		print(f"🔢 OS/2.typoDescender {cleanInt(self.pref('typoDesc')):5}")
		print(f"🔢 OS/2.typoLineGap   {cleanInt(self.pref('typoGap')):5}")
		print(f"🔢 hhea.ascender      {cleanInt(self.pref('hheaAsc')):5}")
		print(f"🔢 hhea.descender     {cleanInt(self.pref('hheaDesc')):5}")
		print(f"🔢 hhea.lineGap       {cleanInt(self.pref('hheaGap')):5}")


	def calculateMethod(self, sender=None):
		method = self.pref("calculate")
		if method == 0:
			self.methodGoogle()
		elif method == 1:
			self.methodWebfonts2019()
		elif method == 2:
			self.methodMicrosoft()


	def methodWebfonts2019(self, sender=None):
		ascender = 0
		descender = 0
		highestCapHeight = 0

		if self.pref("allOpenFonts"):
			theseFonts = Glyphs.fonts
		else:
			theseFonts = (Glyphs.font,)
		for thisFont in theseFonts:
			capHeight = max([m.capHeight for m in thisFont.masters])
			if capHeight > highestCapHeight:
				highestCapHeight = capHeight
			if ascender < capHeight:
				ascender = capHeight
			
			for glyph in self.chosenGlyphs(thisFont):
				glyphAscender = capHeight + (glyphHeight(glyph) - capHeight) * 0.92
				glyphDescender = glyphDepth(glyph)
				if glyph.case != GSLowercase and glyphAscender > ascender:
					ascender = glyphAscender
				elif glyph.case != GSUppercase and len(glyph.layers[0].components)==0 and glyphDescender < descender:
					descender = glyphDescender
		
		# center cap height:
		if (ascender - highestCapHeight) < 0.94 * abs(descender):
			ascender = highestCapHeight + 0.95 * abs(descender)
		elif (ascender - highestCapHeight) > abs(descender):
			ascender = highestCapHeight + 0.98 * abs(descender)
		
		idealLineSpan = highestCapHeight * 1.75
		lineGap = idealLineSpan - (ascender + abs(descender))
		lineGap = max(0, lineGap)
		
		shouldRound = self.pref("round")
		roundValue = int(self.pref("roundValue"))
		if shouldRound:
			ascender = roundUpByValue(ascender, roundValue)
			descender = roundUpByValue(descender, roundValue)
			lineGap = roundUpByValue(lineGap, roundValue)
		
		# update typo values:
		self.setPref("typoAsc", ascender)
		self.setPref("typoDesc", descender)
		self.setPref("typoGap", lineGap)
		self.LoadPreferences()
		
		# update win values:
		self.update(sender=self.w.winUpdate)

		# update hhea values:
		self.update(sender=self.w.hheaUpdate)

		# update useTypoMetrics:
		self.update(sender=self.w.useTypoMetricsUpdate)


	def methodMicrosoft(self, sender=None):
		shouldRound = self.pref("round")
		roundValue = int(self.pref("roundValue"))
		
		self.update(sender=self.w.winUpdate)
		
		self.setPref("hheaAsc", self.pref("winAsc"))
		self.setPref("hheaDesc", self.pref("winDesc"))
		self.setPref("hheaLineGap", 0)
		self.setPref("useTypoMetrics", False)
		self.LoadPreferences()
		
		if self.pref("allOpenFonts"):
			theseFonts = Glyphs.fonts
		else:
			theseFonts = (Glyphs.font,)
		
		descender = 0
		
		for thisFont in theseFonts:
			for name in string.ascii_letters:
				thisGlyph = thisFont.glyphs[name]
				if not thisGlyph:
					continue
				descender = min(descender, glyphDepth(thisGlyph))
		
		if shouldRound:
			descender = roundUpByValue(descender, roundValue)
		
		ascender = Glyphs.font.upm - abs(descender)
		lineGap = max(0, self.pref("winAsc") + self.pref("winDesc") - Glyphs.font.upm)
		
		if shouldRound:
			lineGap = roundUpByValue(lineGap, roundValue)
			
		self.setPref("typoAsc", ascender)
		self.setPref("typoDesc", descender)
		self.setPref("typoGap", lineGap)
		self.LoadPreferences()
		


	def methodGoogle(self, sender=None):
		shouldRound = self.pref("round")
		roundValue = int(self.pref("roundValue"))
		ignoreNonExporting = self.pref("ignoreNonExporting")

		if self.pref("allOpenFonts"):
			theseFonts = Glyphs.fonts
		else:
			theseFonts = (Glyphs.font,)

		ascender = 0
		descender = 0

		for thisFont in theseFonts:
			capHeight = max([m.capHeight for m in thisFont.masters])
			# print(capHeight, type(capHeight), roundValue, type(roundValue))

			abreveacute = thisFont.glyphs["Abreveacute"]
			if abreveacute:
				abreveacuteHeight = glyphHeight(abreveacute)
			else:
				abreveacuteHeight = 0
				for glyph in thisFont.glyphs:
					if ignoreNonExporting and not glyph.export:
						continue
					if glyph.category == "Letter" and glyph.case == GSUppercase:
						if glyphHeight(glyph) > abreveacuteHeight:
							abreveacuteHeight = glyphHeight(glyph)
				if abreveacuteHeight < capHeight:
					abreveacuteHeight = capHeight

			descender = max(descender, capHeight - abreveacuteHeight)
			if descender > 0:
				descender *= -1
			ascender = max(ascender, abreveacuteHeight)

			for glyph in thisFont.glyphs:
				if glyph.category != "Letter":
					continue
				if glyphDepth(glyph) < descender:
					descender = glyphDepth(glyph)
					ascender = capHeight + abs(descender)

		# optically center cap height:
		# descender = roundUpByValue(descender * 1.015, roundValue)
		if shouldRound:
			descender = roundUpByValue(glyphDepth(glyph), roundValue)
			ascender = roundUpByValue(capHeight + abs(descender), roundValue)
			
		# update typo values:
		self.setPref("typoAsc", ascender)
		self.setPref("typoDesc", descender)
		self.setPref("typoGap", 0)
		self.LoadPreferences()

		# update win values:
		self.update(sender=self.w.winUpdate)

		# update hhea values:
		self.update(sender=self.w.hheaUpdate)

		# update useTypoMetrics:
		self.update(sender=self.w.useTypoMetricsUpdate)


	def VerticalMetricsManagerMain(self, sender):
		try:
			Glyphs.clearLog()  # clears macro window log
			print("Vertical Metrics Manager: setting parameters\n")

			# update settings to the latest user input:
			self.SavePreferences()

			typoAsc = cleanInt(self.pref("typoAsc"))
			typoDesc = cleanInt(self.pref("typoDesc"))
			typoGap = cleanInt(self.pref("typoGap"))
			hheaAsc = cleanInt(self.pref("hheaAsc"))
			hheaDesc = cleanInt(self.pref("hheaDesc"))
			hheaGap = cleanInt(self.pref("hheaGap"))
			winDesc = cleanInt(self.pref("winDesc"))
			winAsc = cleanInt(self.pref("winAsc"))
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

			allOpenFonts = self.pref("allOpenFonts")
			if allOpenFonts:
				theseFonts = Glyphs.fonts
			else:
				theseFonts = (Glyphs.font, )  # iterable tuple of frontmost font only

			for i, thisFont in enumerate(theseFonts):
				print("\n\n🔠 %s%s:" % (
					"%i. " % (i + 1) if allOpenFonts else "",
					thisFont.familyName,
				))
				if thisFont.filepath:
					print(f"📄 {thisFont.filepath}")
				else:
					print("⚠️ The font file has not been saved yet.")

				for verticalMetricName in sorted(verticalMetricDict.keys()):
					try:
						metricValue = int(verticalMetricDict[verticalMetricName])
						print(f"🔢 {verticalMetricName}: {metricValue}")

						# clean legacy master settings:
						if not thisFont.customParameters[verticalMetricName] is None:
							del thisFont.customParameters[verticalMetricName]
							print(f"  🚫 Font {thisFont.familyName}: custom parameter removed.")
						for thisMaster in thisFont.masters:
							if not thisMaster.customParameters[verticalMetricName] is None:
								del thisMaster.customParameters[verticalMetricName]
								print(f"  🚫 Master {thisMaster.name}: custom parameter removed.")

						# write new values:
						if self.pref("writeToPopup") == 0:
							for thisMaster in thisFont.masters:
								thisMaster.customParameters[verticalMetricName] = metricValue
								print(f"  ✅ Master {thisMaster.name}: custom parameter set.")
						elif self.pref("writeToPopup") == 2:
							# add to font, not to masters:
							thisFont.customParameters[verticalMetricName] = metricValue
							print("  ✅ Font: custom parameter set.")
						else:
							thisMaster = thisFont.masters[0]
							thisMaster.customParameters[verticalMetricName] = metricValue
							print(f"  ✅ Master {thisMaster.name}: custom parameter set.")

					except:
						print(f"❌ {verticalMetricName}: No valid value found. Deleting parameters:")
						for thisMaster in thisFont.masters:
							if not thisMaster.customParameters[verticalMetricName] is None:
								del thisMaster.customParameters[verticalMetricName]
								print(f"  ⚠️ Master {thisMaster.name}: custom parameter removed.")
							else:
								print(f"  ❎ Master {thisMaster.name}: no custom parameter found.")

				useTypoMetrics = self.pref("useTypoMetrics")
				print("*️⃣ Use Typo Metrics (fsSelection bit 7)")
				if useTypoMetrics:
					thisFont.customParameters["Use Typo Metrics"] = True
					print("  ✅ Set Use Typo Metrics parameter to YES.")
				else:
					thisFont.customParameters["Use Typo Metrics"] = False
					print("  ⁉️ Set Use Typo Metrics parameter to NO. This is not recommended. Are you sure?")

			Message(
				title="Vertical Metrics Set",
				message="Set vertical metrics in %i font%s. Detailed report in Macro Window." % (
					len(theseFonts),
					"" if len(theseFonts) == 1 else "s",
				),
				OKButton=None,
			)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Vertical Metrics Manager Error: {e}")
			import traceback
			print(traceback.format_exc())


VerticalMetricsManager()

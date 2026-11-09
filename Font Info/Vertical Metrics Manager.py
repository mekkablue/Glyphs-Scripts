# MenuTitle: Vertical Metrics Manager
__doc__ = """
Manage and sync ascender, descender and linegap values for hhea, OS/2 sTypo and OS/2 usWin.
"""

import string
import objc
import vanilla
from mekkablue import mekkaObject, UpdateButton
from GlyphsApp import Glyphs, Message, GetOpenFile, GSUppercase, GSLowercase, GSLayer
from AppKit import NSColor, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut, NSTextAlignmentRight
from Foundation import NSNumberFormatter


class SteppingEditText(vanilla.EditText):
	"""EditText with arrow-key stepping, as in Glyphs’ own numeric fields."""
	nsTextFieldClass = objc.lookUpClass("GSSteppingTextField")


def topEdge(rect):
	return rect.origin.y + rect.size.height


def bottomEdge(rect):
	return rect.origin.y


def glyphHeight(glyph):
	return max([topEdge(l.bounds) for l in glyph.layers if l.isMasterLayer or l.isSpecialLayer])


def glyphDepth(glyph):
	return min([bottomEdge(l.bounds) for l in glyph.layers if l.isMasterLayer or l.isSpecialLayer])


def markHeight(glyph):
	height = 0
	for l in glyph.layers:
		if not l.isMasterLayer and not l.isSpecialLayer:
			continue
		if l.anchors["_top"]:
			thisHeight = l.bounds.origin.x + l.bounds.size.height - l.anchors["_top"].position.y
			if thisHeight > height:
				height = thisHeight
	return height


def cleanInt(numberString):
	if isinstance(numberString, (int, float)):
		# stepping fields with a number formatter may deliver numbers instead of strings
		return int(round(numberString))
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
		"writeToPopup": 2 if Glyphs.versionNumber >= 4 else 0,  # font-wide in Glyphs 4+, all masters in Glyphs 3
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
		windowWidth = 370
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Vertical Metrics Manager",  # window title
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements:
		inset = 15

		# unsigned integers for usWin, signed integers for typo and hhea; fields may be left empty (no parameter):
		unsignedFormatter = NSNumberFormatter.alloc().init()
		unsignedFormatter.setAllowsFloats_(False)
		unsignedFormatter.setMinimum_(0)
		signedFormatter = NSNumberFormatter.alloc().init()
		signedFormatter.setAllowsFloats_(False)
		roundFormatter = NSNumberFormatter.alloc().init()
		roundFormatter.setAllowsFloats_(False)
		roundFormatter.setMinimum_(1)

		self.w.descriptionText = vanilla.TextBox("auto", "Manage and sync hhea, typo and win values:", sizeStyle="small", selectable=True)

		self.w.titleAscent = vanilla.TextBox("auto", "Ascender", sizeStyle="small", selectable=True)
		self.w.titleDescent = vanilla.TextBox("auto", "Descender", sizeStyle="small", selectable=True)
		self.w.titleLineGap = vanilla.TextBox("auto", "Line Gap", sizeStyle="small", selectable=True)

		self.w.titleWin = vanilla.TextBox("auto", "OS/2 usWin", sizeStyle="small", selectable=True)
		self.w.winAsc = SteppingEditText("auto", "", callback=self.SavePreferences, sizeStyle="small", formatter=unsignedFormatter)
		self.w.winAsc.setToolTip("OS/2 usWinAscent. Should be the maximum height in your font. Expect clipping or rendering artefacts beyond this point.")
		self.w.winDesc = SteppingEditText("auto", "", callback=self.SavePreferences, sizeStyle="small", formatter=unsignedFormatter)
		self.w.winDesc.setToolTip("OS/2 usWinDescent (unsigned integer). Should be the maximum depth in your font, like the lowest descender you have. Expect clipping or rendering artefacts beyond this point.")
		self.w.winGap = vanilla.EditText("auto", "", callback=None, sizeStyle="small", readOnly=True, placeholder="n/a")
		self.w.winGap.setToolTip("OS/2 usWinLineGap does not exist, hence greyed out here.")
		self.w.winUpdate = UpdateButton("auto", callback=self.update)
		self.w.winUpdate.setToolTip("Will recalculate the OS/2 usWin values in the fields to the left. Takes the measurement settings below into account, except for the Limit options.")

		self.w.parenTypo = vanilla.TextBox("auto", "┏", sizeStyle="small", selectable=False)
		self.w.titleTypo = vanilla.TextBox("auto", "OS/2 sTypo", sizeStyle="small", selectable=True)
		self.w.typoAsc = SteppingEditText("auto", "", callback=self.SavePreferences, sizeStyle="small", formatter=signedFormatter)
		self.w.typoAsc.setToolTip("OS/2 sTypoAscender (positive value), should be the same as hheaAscender. Should be the maximum height of the glyphs relevant for horizontal text setting in your font, like the highest accented uppercase letter, typically Aring or Ohungarumlaut. Used for first baseline offset in DTP and office apps and together with the line gap value, also in browsers.")
		self.w.typoDesc = SteppingEditText("auto", "", callback=self.SavePreferences, sizeStyle="small", formatter=signedFormatter)
		self.w.typoDesc.setToolTip("OS/2 sTypoDescender (negative value), should be the same as hheaDescender. Should be the maximum depth of the glyphs relevant for horizontal text setting in your font, like the lowest descender or bottom accent, typically Gcommaccent, Ccedilla, or one of the lowercase descenders (gjpqy). Together with the line gap value, used for line distance calculation in office apps and browsers.")
		self.w.typoGap = SteppingEditText("auto", "", callback=self.SavePreferences, sizeStyle="small", formatter=signedFormatter)
		self.w.typoGap.setToolTip("OS/2 sTypoLineGap (positive value), should be the same as hheaLineGap. Should be either zero or a value for padding between lines that makes sense visually. Office apps insert this distance between the lines, browsers add half on top and half below each line, also for determining text object boundaries.")
		self.w.typoUpdate = UpdateButton("auto", callback=self.update)
		self.w.typoUpdate.setToolTip("Will recalculate the OS/2 sTypo values in the fields to the left. Takes the measurement settings below into account.")

		self.w.parenHhea = vanilla.TextBox("auto", "┗", sizeStyle="small", selectable=False)
		self.w.titleHhea = vanilla.TextBox("auto", "hhea", sizeStyle="small", selectable=True)
		self.w.hheaAsc = SteppingEditText("auto", "", callback=self.SavePreferences, sizeStyle="small", formatter=signedFormatter)
		self.w.hheaAsc.setToolTip("hheaAscender (positive value), should be the same as OS/2 sTypoAscender. Should be the maximum height of the glyphs relevant for horizontal text setting in your font, like the highest accented uppercase letter, typically Aring or Ohungarumlaut. Used for first baseline offset in Mac office apps and together with the line gap value, also in Mac browsers.")
		self.w.hheaDesc = SteppingEditText("auto", "", callback=self.SavePreferences, sizeStyle="small", formatter=signedFormatter)
		self.w.hheaDesc.setToolTip("hheaDescender (negative value), should be the same as OS/2 sTypoDescender. Should be the maximum depth of the glyphs relevant for horizontal text setting in your font, like the lowest descender or bottom accent, typically Gcommaccent, Ccedilla, or one of the lowercase descenders (gjpqy). Together with the line gap value, used for line distance calculation in office apps and browsers.")
		self.w.hheaGap = SteppingEditText("auto", "", callback=self.SavePreferences, sizeStyle="small", formatter=signedFormatter)
		self.w.hheaGap.setToolTip("hheaLineGap (positive value), should be the same as OS/2 sTypoLineGap. Should be either zero or a value for padding between lines that makes sense visually. Mac office apps insert this distance between the lines, Mac browsers add half on top and half below each line, also for determining text object boundaries.")
		self.w.hheaUpdate = UpdateButton("auto", callback=self.update)
		self.w.hheaUpdate.setToolTip("Will copy the typo values into the hhea values (should always be in sync), unless typo values are not set. In that case, will recalculate the hhea values in the fields to the left. Takes the measurement settings below into account.")

		# decoration: bracket linking typo and hhea values
		for bracket in (self.w.parenTypo, self.w.parenHhea):
			bracket.getNSTextField().setTextColor_(NSColor.tertiaryLabelColor())

		# right align:
		gridFields = (self.w.winAsc, self.w.winDesc, self.w.typoAsc, self.w.typoDesc, self.w.typoGap, self.w.hheaAsc, self.w.hheaDesc, self.w.hheaGap)
		for textCell in gridFields:
			textCell.getNSTextField().setAlignment_(NSTextAlignmentRight)
		for columnTitle in (self.w.titleAscent, self.w.titleDescent, self.w.titleLineGap):
			columnTitle.getNSTextField().setAlignment_(NSTextAlignmentRight)

		self.w.useTypoMetrics = vanilla.CheckBox("auto", "Use Typo Metrics (fsSelection bit 7)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.useTypoMetrics.setToolTip("Should ALWAYS BE ON. Only uncheck if you really know what you are doing. If unchecked, line behaviour will not be consistent between apps and browsers because some apps prefer win values to sTypo values for determining line distances.")
		self.w.useTypoMetricsUpdate = UpdateButton("auto", callback=self.update)
		self.w.useTypoMetricsUpdate.setToolTip("Will reset the checkbox to the left to ON, because it should ALWAYS be on. Strongly recommended.")

		# METHODS
		self.w.separatorMethods = vanilla.HorizontalLine("auto")

		self.w.descriptionMethods = vanilla.TextBox("auto", "Vertical metrics methods:", sizeStyle="small", selectable=True)

		calculateTooltip = "Choose a vertical metrics strategy and press Calculate to fill the fields above.\n\n• Google: centers the caps between ascender and descender, no line gap.\n• Webfonts (2019): slightly compressed values for webfont line spacing.\n• ArrowType: target line height of 130% resp. 150% of the UPM, with the cap height centered between hhea ascender and descender, usWin synced with hhea, a tight sTypo ascender on the cap height for the best first baseline in DTP apps, and Use Typo Metrics off. Pick the looser 1.5×UPM setting for more generous line spacing.\n• Microsoft (Legacy): usWin-based metrics without Use Typo Metrics."
		self.w.calculateText = vanilla.TextBox("auto", "Use method", sizeStyle="small", selectable=True)
		self.w.calculateText.setToolTip(calculateTooltip)
		self.w.calculate = vanilla.PopUpButton("auto", ("Google", "Webfonts (2019)", "ArrowType (1.3×UPM)", "ArrowType (1.5×UPM)", "Microsoft (Legacy)"), sizeStyle="small", callback=self.SavePreferences)
		self.w.calculate.setToolTip(calculateTooltip)
		self.w.calculateButton = vanilla.Button("auto", "Calculate", sizeStyle="small", callback=self.calculateMethod)

		# EXTRACT FROM EXISTING FONT
		self.w.extractText = vanilla.TextBox("auto", "Copy values from existing OpenType font:", sizeStyle="small", selectable=True)
		extractTooltip = "Extracts values from an existing compiled font (.otf or .ttf) and inserts them in the fields above. Useful if you need to stay in sync with a pre-existing font."
		self.w.extractText.setToolTip(extractTooltip)
		self.w.extractButton = vanilla.Button("auto", "Extract", sizeStyle="small", callback=self.extract)
		self.w.extractButton.setToolTip(extractTooltip)

		self.w.separator = vanilla.HorizontalLine("auto")

		# MEASUREMENT SETTINGS
		self.w.descriptionMeasurements = vanilla.TextBox("auto", "Taking measurements (see tooltips for info):", sizeStyle="small")

		self.w.round = vanilla.CheckBox("auto", "Round by", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.round.setToolTip("Turn on if you want your values rounded. Recommended.")
		self.w.roundValue = SteppingEditText("auto", "10", callback=self.SavePreferences, sizeStyle="small", formatter=roundFormatter)
		self.w.roundValue.setToolTip("All value calculations will be rounded up to the next multiple of this value. Recommended: 10.")

		self.w.includeAllMasters = vanilla.CheckBox("auto", "Include all masters (otherwise current master only)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.includeAllMasters.setToolTip("If checked, all masters will be measured. If unchecked, only the current master will be measured. Since vertical metrics should be the same throughout all masters, it also makes sense to measure on all masters.")

		self.w.respectMarkToBaseOffset = vanilla.CheckBox("auto", "Include mark-to-base offset for OS/2 usWin", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.respectMarkToBaseOffset.setToolTip("If checked will calculate the maximum possible height that can be reached with top-anchored marks, and the lowest depth with bottom-anchored marks, and use those values for the OS/2 usWin values. Strongly recommended for making fonts work on Windows if they rely on mark-to-base positioning (e.g. Arabic). Respects the ‘Limit to Script’ setting.")

		self.w.ignoreNonExporting = vanilla.CheckBox("auto", "Ignore non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.ignoreNonExporting.setToolTip("If checked, glyphs that do not export will be excluded from measuring. Recommended. (Ignored for calculating the OS/2 usWin values.)")

		self.w.preferSelectedGlyphs = vanilla.CheckBox("auto", "Limit to selected glyphs", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.preferSelectedGlyphs.setToolTip("If checked, only the current glyphs will be measured. Can be combined with the other Limit options. May make sense if you want your metrics to be e.g. Latin-CE-centric.")

		self.w.preferScript = vanilla.CheckBox("auto", "Limit to script", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.preferScript.setToolTip("If checked, only measures glyphs belonging to the selected writing system. Can be combined with the other Limit options. (Ignored for calculating the OS/2 usWin values, but respected for mark-to-base calculation.)")
		self.w.preferScriptPopup = vanilla.PopUpButton("auto", ("latin", "greek"), sizeStyle="small", callback=self.SavePreferences)
		self.w.preferScriptPopup.setToolTip("Choose a writing system ('script') you want the measurements to be limited to. May make sense to ignore other scripts if the font is intended only for e.g. Cyrillic. Does not apply to OS/2 usWin")
		self.w.preferScriptUpdate = UpdateButton("auto", callback=self.update)
		self.w.preferScriptUpdate.setToolTip("Update the script popup to the left with all scripts (writing systems) found in the current font.")

		self.w.preferCategory = vanilla.CheckBox("auto", "Limit to category", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.preferCategory.setToolTip("If checked, only measures glyphs belonging to the selected glyph category. Can be combined with the other Limit options. (Ignored for calculating the OS/2 usWin values.)")
		self.w.preferCategoryPopup = vanilla.PopUpButton("auto", ("Letter", "Number"), sizeStyle="small", callback=self.SavePreferences)
		self.w.preferCategoryPopup.setToolTip("Choose a glyph category you want the measurements to be limited to. It may make sense to limit only to Letter.")
		self.w.preferCategoryUpdate = UpdateButton("auto", callback=self.update)
		self.w.preferCategoryUpdate.setToolTip("Update the category popup to the left with all glyph categories found in the current font.")

		self.w.separatorAction = vanilla.HorizontalLine("auto")

		writeToTooltip = "Where the number values are written to: into all masters (Glyphs 3), into the first master only, or into the font itself (Glyphs 4+). Default: font-wide in Glyphs 4 and later, all masters in Glyphs 3."
		self.w.writeToText = vanilla.TextBox("auto", "Write values to", sizeStyle="small", selectable=True)
		self.w.writeToText.setToolTip(writeToTooltip)
		self.w.writeToPopup = vanilla.PopUpButton("auto", ("All masters (Glyphs 3)", "First master only (experimental)", "Font-wide (Glyphs 4+)"), sizeStyle="small", callback=self.SavePreferences)
		self.w.writeToPopup.setToolTip(writeToTooltip)

		self.w.allOpenFonts = vanilla.CheckBox("auto", "⚠️ Read out and apply to ALL open fonts", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.allOpenFonts.setToolTip("If activated, does not only measure the frontmost font, but all open fonts. Careful: when you press the Apply button, will also apply it to all open fonts. Useful if you have all font files for a font family open.")

		# Run Button:
		self.w.helpButton = vanilla.HelpButton("auto", callback=self.openURL)
		self.w.helpButton.setToolTip("Opens the Vertical Metrics tutorial (highly recommended) in your web browser.")

		self.w.runButton = vanilla.Button("auto", "Apply to Font", callback=self.VerticalMetricsManagerMain)
		self.w.runButton.setToolTip("Insert the OS/2, hhea and fsSelection values above as custom parameters in the font. The number values will be inserted where the Write values to popup says (all masters, first master, or font-wide), and removed from the other places. Blank values will delete the respective parameters everywhere.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes and square buttons stretch vertically by default; with everything
		# hugging, the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# in the Limit rows, the checkboxes hug their text and the popups stretch up to it
		for checkBox in (self.w.preferScript, self.w.preferCategory):
			checkBox.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		for popup in (self.w.preferScriptPopup, self.w.preferCategoryPopup):
			popup.getNSPopUpButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# labels in front of fields: right-aligned, all the same width as the widest one
		labelNames = ("titleWin", "titleTypo", "titleHhea", "calculateText", "writeToText")
		widestLabel = "writeToText"  # the label with the longest text
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		labelRules = [
			{"view1": getattr(self.w, labelName), "attribute1": "width", "view2": getattr(self.w, widestLabel), "attribute2": "width"}
			for labelName in labelNames if labelName != widestLabel
		]

		# the cells of the grid share one width, measured against the first one
		referenceCell = self.w.winAsc
		columnRules = [
			{"view1": cell, "attribute1": "width", "view2": referenceCell, "attribute2": "width"}
			for cell in gridFields[1:] + (self.w.winGap, )
		]
		# column titles sit on top of their column
		titleRules = []
		for columnTitle, columnCell in ((self.w.titleAscent, self.w.winAsc), (self.w.titleDescent, self.w.winDesc), (self.w.titleLineGap, self.w.winGap)):
			titleRules.append({"view1": columnTitle, "attribute1": "left", "view2": columnCell, "attribute2": "left"})
			titleRules.append({"view1": columnTitle, "attribute1": "width", "view2": columnCell, "attribute2": "width"})

		# everything else in a row follows the control that has the intrinsic height
		centerRows = (
			(self.w.titleAscent, (self.w.titleDescent, self.w.titleLineGap)),
			(self.w.winAsc, (self.w.titleWin, self.w.winDesc, self.w.winGap, self.w.winUpdate)),
			(self.w.typoAsc, (self.w.parenTypo, self.w.titleTypo, self.w.typoDesc, self.w.typoGap, self.w.typoUpdate)),
			(self.w.hheaAsc, (self.w.parenHhea, self.w.titleHhea, self.w.hheaDesc, self.w.hheaGap, self.w.hheaUpdate)),
			(self.w.useTypoMetrics, (self.w.useTypoMetricsUpdate, )),
			(self.w.calculate, (self.w.calculateText, self.w.calculateButton)),
			(self.w.extractButton, (self.w.extractText, )),
			(self.w.round, (self.w.roundValue, )),
			(self.w.preferScript, (self.w.preferScriptPopup, self.w.preferScriptUpdate)),
			(self.w.preferCategory, (self.w.preferCategoryPopup, self.w.preferCategoryUpdate)),
			(self.w.writeToPopup, (self.w.writeToText, )),
			(self.w.runButton, (self.w.helpButton, )),
		)
		centerRules = [
			{"view1": otherView, "attribute1": "centerY", "view2": mainView, "attribute2": "centerY"}
			for mainView, otherViews in centerRows for otherView in otherViews
		]

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[titleWin]-gap-[winAsc(>=50)]-gap-[winDesc]-gap-[winGap]-gap-[winUpdate(18)]-inset-|",
				"H:|-bracketInset-[parenTypo]",
				"H:|-inset-[titleTypo]-gap-[typoAsc]-gap-[typoDesc]-gap-[typoGap]-gap-[typoUpdate(18)]-inset-|",
				"H:|-bracketInset-[parenHhea]",
				"H:|-inset-[titleHhea]-gap-[hheaAsc]-gap-[hheaDesc]-gap-[hheaGap]-gap-[hheaUpdate(18)]-inset-|",
				"H:[useTypoMetrics]-(>=gap)-[useTypoMetricsUpdate(18)]-inset-|",
				"H:|-inset-[separatorMethods]-inset-|",
				"H:|-inset-[descriptionMethods]-inset-|",
				"H:|-inset-[calculateText]-gap-[calculate]-gap-[calculateButton(>=70)]-inset-|",
				"H:|-inset-[extractText]-(>=gap)-[extractButton(>=70)]-inset-|",
				"H:|-inset-[separator]-inset-|",
				"H:|-inset-[descriptionMeasurements]-inset-|",
				"H:|-inset-[round]-gap-[roundValue(60)]-(>=inset)-|",
				"H:|-inset-[includeAllMasters]-(>=inset)-|",
				"H:|-inset-[respectMarkToBaseOffset]-(>=inset)-|",
				"H:|-inset-[ignoreNonExporting]-(>=inset)-|",
				"H:|-inset-[preferSelectedGlyphs]-(>=inset)-|",
				"H:|-inset-[preferScript]-gap-[preferScriptPopup]-gap-[preferScriptUpdate(18)]-inset-|",
				"H:|-inset-[preferCategory]-gap-[preferCategoryPopup]-gap-[preferCategoryUpdate(18)]-inset-|",
				"H:|-inset-[separatorAction]-inset-|",
				"H:|-inset-[writeToText]-gap-[writeToPopup]-inset-|",
				"H:|-inset-[allOpenFonts]-(>=inset)-|",
				"H:|-inset-[helpButton]-(>=gap)-[runButton(>=120)]-inset-|",
				"V:|-inset-[descriptionText]-row-[titleAscent]-row-[winAsc]-groupGap-[typoAsc]-tightRow-[hheaAsc]-row-[useTypoMetrics]-inset-[separatorMethods(1)]-inset-[descriptionMethods]-row-[calculate]-row-[extractButton]-inset-[separator(1)]-inset-[descriptionMeasurements]-row-[round]-stackRow-[includeAllMasters]-stackRow-[respectMarkToBaseOffset]-stackRow-[ignoreNonExporting]-stackRow-[preferSelectedGlyphs]-stackRow-[preferScript]-stackRow-[preferCategory]-inset-[separatorAction(1)]-inset-[writeToPopup]-checkRow-[allOpenFonts]-inset-[runButton]-inset-|",
				# the checkbox lines up with the first column of the grid:
				{"view1": self.w.useTypoMetrics, "attribute1": "left", "view2": self.w.winAsc, "attribute2": "left"},
				# both popups of the Limit rows get the same width, and so do their checkboxes:
				{"view1": self.w.preferCategory, "attribute1": "width", "view2": self.w.preferScript, "attribute2": "width"},
				{"view1": self.w.extractButton, "attribute1": "width", "view2": self.w.calculateButton, "attribute2": "width"},
			] + labelRules + columnRules + titleRules + centerRules,
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5, "stackRow": 8, "groupGap": 9, "tightRow": 3, "bracketInset": 3},
		)

		self.LoadPreferences()
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
			print(f"{i+1}. {thisFont.familyName}:")
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
					fontReport = f"{i+1}. {thisFont.familyName}, "
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
						lowestPointInLayer = bottomEdge(thisLayer.bounds)
						highestPointInLayer = topEdge(thisLayer.bounds)
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
		elif sender is self.w.hheaUpdate:
			print("💞 Copying existing OS/2 sTypo values into hhea values...\n")
			asc = cleanInt(self.pref("typoAsc"))
			desc = cleanInt(self.pref("typoDesc"))
			gap = cleanInt(self.pref("typoGap"))
			self.setPref("hheaAsc", asc)
			self.setPref("hheaDesc", desc)
			self.setPref("hheaGap", gap)
			
		elif sender is self.w.typoUpdate:
			name = "OS/2 sTypo"
			print(f"Determining {name} values:\n")

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
					fontReport = f"{i+1}. {thisFont.familyName}, "
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
						lowestPointInLayer = bottomEdge(thisLayer.bounds)
						highestPointInLayer = topEdge(thisLayer.bounds)
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
			self.methodArrowType(lineHeightFactor=1.3)
		elif method == 3:
			self.methodArrowType(lineHeightFactor=1.5)
		elif method == 4:
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
		roundValue = self.prefInt("roundValue")
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


	def methodArrowType(self, sender=None, lineHeightFactor=1.3):
		"""
		ArrowType strategy, see https://github.com/arrowtype/vertical-metrics
		Starts with a target line height of lineHeightFactor times the UPM, and
		centers the cap height between hhea ascender and descender. usWin is synced
		with hhea, and Use Typo Metrics is turned off, so Windows apps fall back to
		the usWin values while the Mac uses the hhea values, and both are the same.
		The tight sTypo ascender yields the best possible first baseline position in
		apps like InDesign.
		"""
		shouldRound = self.pref("round")
		roundValue = self.prefInt("roundValue")

		if self.pref("allOpenFonts"):
			theseFonts = Glyphs.fonts
		else:
			theseFonts = (Glyphs.font, )

		capHeight = 0
		lineHeight = 0

		for thisFont in theseFonts:
			lineHeight = max(lineHeight, thisFont.upm * lineHeightFactor)
			capHeight = max([m.capHeight for m in thisFont.masters] + [capHeight])

		if capHeight <= 0:
			Message(
				title="Cannot Measure Font",
				message="Could not determine the cap height of the masters. Please check your master metrics.",
				OKButton=None,
			)
			return

		if shouldRound:
			capHeight = roundUpByValue(capHeight, roundValue)

		# center the cap height between hhea ascender and descender:
		hheaAsc = (capHeight + lineHeight) / 2
		if shouldRound:
			hheaAsc = roundUpByValue(hheaAsc, roundValue)
		hheaDesc = capHeight - hheaAsc

		print(f"ArrowType strategy ({lineHeightFactor}\u00d7UPM):\n")
		print(f"- cap height: {capHeight}")
		print(f"- target line height ({lineHeightFactor:.0%} of UPM): {lineHeight}")
		print()

		# hhea, with usWin in sync, and sTypo tight on the cap height:
		self.setPref("hheaAsc", int(hheaAsc))
		self.setPref("hheaDesc", int(hheaDesc))
		self.setPref("hheaGap", 0)
		self.setPref("typoAsc", int(capHeight))
		self.setPref("typoDesc", int(hheaDesc))
		self.setPref("typoGap", int(abs(hheaDesc)))
		self.setPref("winAsc", int(hheaAsc))
		self.setPref("winDesc", int(abs(hheaDesc)))

		# hhea and usWin determine the line spacing, so Use Typo Metrics stays off:
		self.setPref("useTypoMetrics", False)
		self.LoadPreferences()


	def methodMicrosoft(self, sender=None):
		shouldRound = self.pref("round")
		roundValue = self.prefInt("roundValue")
		
		self.update(sender=self.w.winUpdate)
		
		self.setPref("hheaAsc", self.pref("winAsc"))
		self.setPref("hheaDesc", self.pref("winDesc"))
		self.setPref("hheaGap", 0)
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
		roundValue = self.prefInt("roundValue")
		ignoreNonExporting = self.pref("ignoreNonExporting")

		if self.pref("allOpenFonts"):
			theseFonts = Glyphs.fonts
		else:
			theseFonts = (Glyphs.font,)

		ascender = 0
		descender = 0
		capHeight = 0

		for thisFont in theseFonts:
			capHeight = max([m.capHeight for m in thisFont.masters] + [capHeight])
			# print(capHeight, type(capHeight), roundValue, type(roundValue))

			abreveacute = thisFont.glyphs["Abreveacute"]
			agrave = thisFont.glyphs["Agrave"]
			if abreveacute:
				abreveacuteHeight = glyphHeight(abreveacute)
			elif agrave:
				abreveacuteHeight = glyphHeight(agrave)
				acute = thisFont.glyphs["acutecomb.case"] or thisFont.glyphs["acutecomb"]
				if acute:
					abreveacuteHeight += markHeight(acute)
			else:
				abreveacuteHeight = 0
				for glyph in thisFont.glyphs:
					if ignoreNonExporting and not glyph.export:
						continue
					if glyph.category == "Letter":
						thisGlyphHeight = glyphHeight(glyph)
						if thisGlyphHeight > abreveacuteHeight:
							abreveacuteHeight = thisGlyphHeight
				if abreveacuteHeight < capHeight:
					abreveacuteHeight = capHeight

			ascender = max(ascender, abreveacuteHeight)
			descender = min(descender, capHeight - abreveacuteHeight)
			if descender > 0:
				descender *= -1
			
			# sanity check: descender must go below all actual descenders
			for glyph in thisFont.glyphs:
				if glyph.category != "Letter":
					continue
				if glyphDepth(glyph) < descender:
					descender = glyphDepth(glyph)
					ascender = max(ascender, capHeight + abs(descender))

		# center caps again:
		distance = max(abs(descender), ascender - capHeight)
		ascender = capHeight + distance
		descender = -distance

		# round if requested
		if shouldRound:
			descender = roundUpByValue(descender, roundValue)
			ascender = roundUpByValue(ascender, roundValue)

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


	def removeParameter(self, thisFont, parameterName, keepInFont=False, keepMasterIndexes=()):
		"""Deletes a custom parameter from the font and from all masters, except where it is to be kept."""
		if not keepInFont and thisFont.customParameters[parameterName] is not None:
			del thisFont.customParameters[parameterName]
			print(f"  🚫 Font {thisFont.familyName}: custom parameter removed.")
		for masterIndex, thisMaster in enumerate(thisFont.masters):
			if masterIndex in keepMasterIndexes:
				continue
			if thisMaster.customParameters[parameterName] is not None:
				del thisMaster.customParameters[parameterName]
				print(f"  🚫 Master {thisMaster.name}: custom parameter removed.")

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

			writeTo = self.prefInt("writeToPopup")  # 0: all masters, 1: first master only, 2: font-wide
			allOpenFonts = self.pref("allOpenFonts")
			if allOpenFonts:
				theseFonts = Glyphs.fonts
			else:
				theseFonts = (Glyphs.font, )  # iterable tuple of frontmost font only

			for i, thisFont in enumerate(theseFonts):
				print("\n\n🔠 %s%s:" % (
					"%i. " % (i+1) if allOpenFonts else "",
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

						# remove the parameter everywhere except where the new value is written:
						if writeTo == 0:
							keepMasterIndexes = set(range(len(thisFont.masters)))
						elif writeTo == 1:
							keepMasterIndexes = {0}
						else:
							keepMasterIndexes = set()
						self.removeParameter(thisFont, verticalMetricName, keepInFont=(writeTo == 2), keepMasterIndexes=keepMasterIndexes)

						# write new values:
						if writeTo == 0:
							for thisMaster in thisFont.masters:
								thisMaster.customParameters[verticalMetricName] = metricValue
								print(f"  ✅ Master {thisMaster.name}: custom parameter set.")
						elif writeTo == 2:
							# add to font, not to masters:
							thisFont.customParameters[verticalMetricName] = metricValue
							print("  ✅ Font: custom parameter set.")
						else:
							thisMaster = thisFont.masters[0]
							thisMaster.customParameters[verticalMetricName] = metricValue
							print(f"  ✅ Master {thisMaster.name}: custom parameter set.")

					except:
						print(f"❌ {verticalMetricName}: No valid value found. Deleting parameters:")
						self.removeParameter(thisFont, verticalMetricName, keepInFont=False, keepMasterIndexes=set())

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

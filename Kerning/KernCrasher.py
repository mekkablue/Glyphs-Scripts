# MenuTitle: KernCrasher
__doc__ = """
Finds kerning collisions in the current master (or in more masters and fonts, see Scope) and opens a tab with them, one tab per font.
"""

import vanilla
from timeit import default_timer as timer
from AppKit import NSTextAlignmentRight, NSWindowStyleMaskResizable, NSSize, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut
from Foundation import NSNotFound
from kernanalysis import intervalList, categoryList, sortedIntervalsFromString, effectiveKerning, minDistanceBetweenTwoLayers, distanceFromEntry
from GlyphsApp import Glyphs, GSControlLayer, Message
from mekkablue import mekkaObject, caseDict, UpdateButton

# entries for the left and right glyph popups; the new ones come last, so saved popup positions stay valid:
currentTabEntry = "All glyphs in current tab"
categoriesForAllEntries = {
	"All letters": ("Letter", ),
	"All letters and punctuation": ("Letter", "Punctuation"),
	"All letters, punctuation and figures (slow)": ("Letter", "Punctuation", "Number"),
}
glyphChoices = tuple(categoryList) + (currentTabEntry, ) + tuple(categoriesForAllEntries.keys())
scopeChoices = (
	"Current master",
	"⚠️ All masters of frontmost font",
	"⚠️ Current masters of all open fonts",
	"⚠️ All masters of all open fonts",
)


class KernCrasher(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"minDistance": "10",
		"popupScope": 0,
		"popupScript": "latin",
		"popupSpeed": 0,
		"popupLeftCat": 0,
		"popupRightCat": 0,
		"excludeSuffixes": ".locl, .alt, .sups, .sinf, .tf, .tosf, Ldot, ldot, Jacute, jacute",
		"excludeNonExporting": 1,
		"reportCrashesInMacroWindow": 0,
		"ignoreIntervals": "",
		"pathGlyphsOnly": 0,
		"reuseCurrentTab": 1,
		"limitRightSuffixes": "",
		"limitLeftSuffixes": "",
		"directionSensitive": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 470
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"KernCrasher",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 16

		self.w.descriptionText = vanilla.TextBox("auto", "Find kerning collisions and open tab", sizeStyle='small')

		self.w.textScope = vanilla.TextBox("auto", "Scope", sizeStyle='small')
		self.w.popupScope = vanilla.PopUpButton("auto", scopeChoices, callback=self.SavePreferences, sizeStyle='small')
		tooltipText = "Which masters to check for kerning collisions. Whatever you choose, each font gets at most one tab with its results (opened, or reused, if ‘Reuse current tab’ is on)."
		self.w.textScope.setToolTip(tooltipText)
		self.w.popupScope.setToolTip(tooltipText)

		self.w.textScript = vanilla.TextBox("auto", "Script", sizeStyle='small')
		self.w.popupScript = vanilla.ComboBox("auto", ("latin", "cyrillic", "greek"), callback=self.SavePreferences, sizeStyle='small')
		self.w.popupScript.setToolTip("Limits the kerning pairs only to glyphs of this script, and those of no script.")
		self.w.updateScriptsButton = UpdateButton("auto", callback=self.update)
		self.w.updateScriptsButton.setToolTip("Scans the frontost font for the scripts of all its glyphs (Latin, Greek, Cyrillic, Hebrew, Arabic, Thai, ...) and lists only those in the combo box.")
		self.w.textDistance = vanilla.TextBox("auto", "Min distance", sizeStyle='small')
		self.w.minDistance = vanilla.EditText("auto", "10", sizeStyle='small')
		tooltipText = "Minimum distance required between glyphs in any given pairing with the current setup. Measured in units."
		self.w.textDistance.setToolTip(tooltipText)
		self.w.minDistance.setToolTip(tooltipText)

		self.w.textSpeed = vanilla.TextBox("auto", "Speed", sizeStyle='small')
		self.w.popupSpeed = vanilla.PopUpButton("auto", ("very slow", "slow", "medium", "fast", "very fast"), callback=self.popupSpeedAction, sizeStyle='small')
		intervalIndex = self.pref("popupSpeed")
		if intervalIndex is None:
			intervalIndex = 0
		self.w.text_speedExplanation = vanilla.TextBox("auto", "Measuring every %i units." % intervalList[intervalIndex], sizeStyle='small')
		tooltipText = "The distances within every glyph pair will be measured from top to bottom. This setting determines how many measurements are taken. Higher speed means less measurements and thus less accuracy. Many measurements are more accurate, but also slow down the script significantly."
		self.w.textSpeed.setToolTip(tooltipText)
		self.w.popupSpeed.setToolTip(tooltipText)
		self.w.text_speedExplanation.setToolTip(tooltipText)

		self.w.text_popupLeftCat = vanilla.TextBox("auto", "Left glyph", sizeStyle='small')
		self.w.popupLeftCat = vanilla.PopUpButton("auto", glyphChoices, callback=self.SavePreferences, sizeStyle='small')
		tooltipText = "The glyphs for the LEFT side of the kerning pair. In ‘AV’, that would be ‘A’. Choose a category, all glyphs in the current tab (each counted once), or all letters, optionally with punctuation and figures. The settings below (script, exclusions, non-exporting glyphs, paths only) are respected in every case."
		self.w.text_popupLeftCat.setToolTip(tooltipText)
		self.w.popupLeftCat.setToolTip(tooltipText)

		self.w.text_popupRightCat = vanilla.TextBox("auto", "Right glyph", sizeStyle='small')
		self.w.popupRightCat = vanilla.PopUpButton("auto", glyphChoices, callback=self.SavePreferences, sizeStyle='small')
		tooltipText = "The glyphs for the RIGHT side of the kerning pair. In ‘AV’, that would be ‘V’. Choose a category, all glyphs in the current tab (each counted once), or all letters, optionally with punctuation and figures. The settings below (script, exclusions, non-exporting glyphs, paths only) are respected in every case."
		self.w.text_popupRightCat.setToolTip(tooltipText)
		self.w.popupRightCat.setToolTip(tooltipText)

		self.w.text_limitLeftSuffixes = vanilla.TextBox("auto", "Left glyph must contain", sizeStyle='small')
		self.w.limitLeftSuffixes = vanilla.EditText("auto", "", callback=self.SavePreferences, sizeStyle='small')
		self.w.limitLeftSuffixes.getNSTextField().setPlaceholderString_("tilde, macron, dieresis, circumflex, caron")
		tooltipText = "Only glyphs with these parts in their glyph names will be considered for the LEFT side. Comma-separated list. Usually not necessary, but useful for tracking down problems with wide diacritics."
		self.w.text_limitLeftSuffixes.setToolTip(tooltipText)
		self.w.limitLeftSuffixes.setToolTip(tooltipText)

		self.w.text_limitRightSuffixes = vanilla.TextBox("auto", "Right glyph must contain", sizeStyle='small')
		self.w.limitRightSuffixes = vanilla.EditText("auto", "", callback=self.SavePreferences, sizeStyle='small')
		self.w.limitRightSuffixes.getNSTextField().setPlaceholderString_("tilde, macron, dieresis, circumflex, caron")
		tooltipText = "Only glyphs with these parts in their glyph names will be considered for the RIGHT side. Comma-separated list. Usually not necessary, but useful for tracking down problems with wide diacritics."
		self.w.text_limitRightSuffixes.setToolTip(tooltipText)
		self.w.limitRightSuffixes.setToolTip(tooltipText)

		self.w.text_excludeSuffixes = vanilla.TextBox("auto", "Exclude glyphs containing", sizeStyle='small')
		self.w.excludeSuffixes = vanilla.EditText("auto", ".locl, .alt, .sups, .sinf, .tf, .tosf, Ldot, ldot, Jacute, jacute", callback=self.SavePreferences, sizeStyle='small')
		tooltipText = "Glyphs with these particles in their glyph names will be ignored. Comma-separated list. Useful for excluding impossible pairings, like ldot (can only appear before l) and jacute (can only appear after iacute), or OpenType variants."
		self.w.text_excludeSuffixes.setToolTip(tooltipText)
		self.w.excludeSuffixes.setToolTip(tooltipText)

		self.w.text_ignoreIntervals = vanilla.TextBox("auto", "Ignore height intervals", sizeStyle='small')
		self.w.ignoreIntervals = vanilla.EditText("auto", "", callback=self.SavePreferences, sizeStyle='small')
		self.w.ignoreIntervals.getNSTextField().setPlaceholderString_("200:300, 400:370, -200:-150")
		tooltipText = "Will not measure between the specified heights. Useful for excluding connectors of connecting script typefaces or rekha lines like in Devanagari, where an overlap is intended by design. Specify two numbers separated by a colon, e.g., 200:300, and it will only measure until y=200 and start measuring again at y=300, skipping everything in between. If you specify multiple ranges, separate them with commas. You can also specify glyph names, e.g. x:o (from bottom of x to top of o)."
		self.w.text_ignoreIntervals.setToolTip(tooltipText)
		self.w.ignoreIntervals.setToolTip(tooltipText)

		self.w.pathGlyphsOnly = vanilla.CheckBox("auto", "Limit to glyphs containing paths (i.e., exclude composites)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.pathGlyphsOnly.setToolTip("If enabled, will ignore glyphs that do not have paths. Useful for focusing on the base shapes (before you deal with the specific problems of composite diacritics).")

		self.w.excludeNonExporting = vanilla.CheckBox("auto", "Exclude non-exporting glyphs", value=True, sizeStyle='small', callback=self.SavePreferences)
		self.w.excludeNonExporting.setToolTip("If enabled, will ignore glyphs that are set to not export. Recommended, otherwise you may get a lot of false positives.")

		self.w.directionSensitive = vanilla.CheckBox("auto", "Auto-detect writing direction (LTR vs. RTL)", value=True, sizeStyle='small', callback=self.SavePreferences)
		self.w.directionSensitive.setToolTip("If enabled, will determine writing direction based on settings in current tab. If disabled, LTR will be used")

		self.w.reuseCurrentTab = vanilla.CheckBox("auto", "Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.reuseCurrentTab.setToolTip("If enabled, will not open a new tab with the collisions, but reuse the current Edit tab of each font. Will open an Edit tab if none is open.")
		self.w.reportCrashesInMacroWindow = vanilla.CheckBox("auto", "Verbose report in Macro Window", value=False, sizeStyle='small', callback=self.SavePreferences)
		self.w.reportCrashesInMacroWindow.setToolTip("Will output a detailed report of the kern crashing in Window > Macro Panel. Will slow down the script a bit. Usually not necessary, but can be useful for checking if a certain pairing has been taken care of or not.")

		# Percentage:
		self.w.bar = vanilla.ProgressBar("auto")

		# Status line, with the prediction:
		self.w.statusText = vanilla.TextBox("auto", "🔢 Will analyze – pairs.", sizeStyle='small')
		self.w.statusText.setToolTip("How many glyph pairs will be measured with the current settings, across all masters and fonts of the chosen scope.")
		self.w.statusText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# Buttons:
		self.w.nextButton = vanilla.Button("auto", "Next Master", callback=self.masterSwitch)

		# Run Button:
		self.w.nextButton.setToolTip("Switches the frontmost font to its next master.")
		self.w.runButton = vanilla.Button("auto", "Open Tab", callback=self.KernCrasherMain)
		self.w.runButton.setToolTip("Measures the distances between all glyph pairs of the chosen scope and opens a tab with the pairs that collide.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels hug their text, and resist compression, so the fields take the leftover width:
		labelNames = (
			"textScope",
			"textScript",
			"textSpeed",
			"text_popupLeftCat",
			"text_popupRightCat",
			"text_limitLeftSuffixes",
			"text_limitRightSuffixes",
			"text_excludeSuffixes",
			"text_ignoreIntervals",
		)
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# all labels share the width of the widest one, so the fields line up:
		widthRules = [
			{
				"view1": getattr(self.w, labelName),
				"attribute1": "width",
				"view2": self.w.text_excludeSuffixes,
				"attribute2": "width",
			} for labelName in labelNames if labelName != "text_excludeSuffixes"
		]

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[textScope]-gap-[popupScope]-inset-|",
				"H:|-inset-[textScript]-gap-[popupScript(>=110)]-gap-[updateScriptsButton]-gap-[textDistance]-gap-[minDistance(50)]-inset-|",
				"H:|-inset-[textSpeed]-gap-[popupSpeed]-gap-[text_speedExplanation]-(>=inset)-|",
				"H:|-inset-[text_popupLeftCat]-gap-[popupLeftCat]-inset-|",
				"H:|-inset-[text_popupRightCat]-gap-[popupRightCat]-inset-|",
				"H:|-inset-[text_limitLeftSuffixes]-gap-[limitLeftSuffixes]-inset-|",
				"H:|-inset-[text_limitRightSuffixes]-gap-[limitRightSuffixes]-inset-|",
				"H:|-inset-[text_excludeSuffixes]-gap-[excludeSuffixes]-inset-|",
				"H:|-inset-[text_ignoreIntervals]-gap-[ignoreIntervals]-inset-|",
				"H:|-inset-[pathGlyphsOnly]-(>=inset)-|",
				"H:|-inset-[excludeNonExporting]-(>=inset)-|",
				"H:|-inset-[directionSensitive]-(>=inset)-|",
				"H:|-inset-[reuseCurrentTab]-gap-[reportCrashesInMacroWindow]-(>=inset)-|",
				"H:|-inset-[bar]-inset-|",
				"H:|-inset-[statusText]-(>=gap)-[nextButton(>=70)]-gap-[runButton(>=70)]-inset-|",
				"V:|-inset-[descriptionText]-headlineGap-[popupScope]-row-[popupScript]-row-[popupSpeed]-row-[popupLeftCat]-row-[popupRightCat]-row-[limitLeftSuffixes]-row-[limitRightSuffixes]-row-[excludeSuffixes]-row-[ignoreIntervals]-row-[pathGlyphsOnly]-5-[excludeNonExporting]-5-[directionSensitive]-5-[reportCrashesInMacroWindow]-barGap-[bar(16)]-inset-[runButton]-inset-|",
				"V:[nextButton]-inset-|",
				# one baseline per row:
				{"view1": self.w.textScope, "attribute1": "centerY", "view2": self.w.popupScope, "attribute2": "centerY"},
				{"view1": self.w.statusText, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
				{"view1": self.w.textScript, "attribute1": "centerY", "view2": self.w.popupScript, "attribute2": "centerY"},
				{"view1": self.w.updateScriptsButton, "attribute1": "centerY", "view2": self.w.popupScript, "attribute2": "centerY"},
				{"view1": self.w.textDistance, "attribute1": "centerY", "view2": self.w.popupScript, "attribute2": "centerY"},
				{"view1": self.w.minDistance, "attribute1": "centerY", "view2": self.w.popupScript, "attribute2": "centerY"},
				{"view1": self.w.textSpeed, "attribute1": "centerY", "view2": self.w.popupSpeed, "attribute2": "centerY"},
				{"view1": self.w.text_speedExplanation, "attribute1": "centerY", "view2": self.w.popupSpeed, "attribute2": "centerY"},
				{"view1": self.w.text_popupLeftCat, "attribute1": "centerY", "view2": self.w.popupLeftCat, "attribute2": "centerY"},
				{"view1": self.w.text_popupRightCat, "attribute1": "centerY", "view2": self.w.popupRightCat, "attribute2": "centerY"},
				{"view1": self.w.text_limitLeftSuffixes, "attribute1": "centerY", "view2": self.w.limitLeftSuffixes, "attribute2": "centerY"},
				{"view1": self.w.text_limitRightSuffixes, "attribute1": "centerY", "view2": self.w.limitRightSuffixes, "attribute2": "centerY"},
				{"view1": self.w.text_excludeSuffixes, "attribute1": "centerY", "view2": self.w.excludeSuffixes, "attribute2": "centerY"},
				{"view1": self.w.text_ignoreIntervals, "attribute1": "centerY", "view2": self.w.ignoreIntervals, "attribute2": "centerY"},
				{"view1": self.w.reuseCurrentTab, "attribute1": "centerY", "view2": self.w.reportCrashesInMacroWindow, "attribute2": "centerY"},
				# the speed popup is as wide as the script combo box:
				{"view1": self.w.popupSpeed, "attribute1": "width", "view2": self.w.popupScript, "attribute2": "width"},
			] + widthRules,
			metrics={"inset": inset, "gap": 8, "row": 5, "headlineGap": 14, "barGap": 14},
		)

		# Load Settings:
		self.LoadPreferences()
		self.updateUI()  # prediction in the status line

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

		# make the window horizontally resizable, but keep the height that Auto Layout determined.
		# (Content sizes set directly on the NSWindow, so the title bar is not counted twice.)
		nsWindow = self.w.getNSWindow()
		nsWindow.setStyleMask_(nsWindow.styleMask() | NSWindowStyleMaskResizable)
		nsWindow.layoutIfNeeded()  # make sure the content has its final size before we read it
		contentSize = nsWindow.contentView().frame().size
		nsWindow.setContentMinSize_(NSSize(contentSize.width, contentSize.height))
		nsWindow.setContentMaxSize_(NSSize(contentSize.width + 1000, contentSize.height))

	def updateUI(self, sender=None):
		pairCount = self.predictedPairCount()
		self.w.statusText.set(f"🔢 Will analyze {pairCount:,} pair{'' if pairCount == 1 else 's'}.")

	def update(self, sender=None):
		if sender == self.w.updateScriptsButton and Glyphs.font:
			scriptList = [g.script for g in Glyphs.font.glyphs if g.script]
			if scriptList:
				updatedScriptList = list(set(scriptList))
				self.w.popupScript.setItems(updatedScriptList)
				self.w.popupScript.set(updatedScriptList[0])

	def popupSpeedAction(self, sender):
		self.SavePreferences()
		intervalIndex = self.pref("popupSpeed")
		if intervalIndex is None:
			intervalIndex = 0
		self.w.text_speedExplanation.set("Measuring every %i units." % intervalList[intervalIndex])

	def nameUntilFirstPeriod(self, glyphName):
		if "." not in glyphName:
			return glyphName
		else:
			offset = glyphName.find(".")
			return glyphName[:offset]

	def glyphPassesFilters(self, thisGlyph, requiredScript, excludedGlyphNameParts, excludeNonExporting, pathGlyphsOnly, mustContain):
		"""The settings below the popups, applied to every choice of glyphs."""
		glyphName = thisGlyph.name
		if excludedGlyphNameParts and any(thisNamePart in glyphName for thisNamePart in excludedGlyphNameParts):
			return False
		if mustContain and not any(thisNamePart in glyphName for thisNamePart in mustContain):
			return False
		if excludeNonExporting and not thisGlyph.export:
			return False
		if thisGlyph.script is not None and thisGlyph.script != requiredScript:
			return False
		if pathGlyphsOnly and not thisGlyph.layers[0].paths:
			return False
		return True

	def listOfNamesForCategories(self, thisFont, requiredCategory, requiredSubCategory, requiredScript, excludedGlyphNameParts, excludeNonExporting, pathGlyphsOnly, mustContain):
		nameList = []
		for thisGlyph in thisFont.glyphs:
			if not self.glyphPassesFilters(thisGlyph, requiredScript, excludedGlyphNameParts, excludeNonExporting, pathGlyphsOnly, mustContain):
				continue
			if thisGlyph.category != requiredCategory:
				continue
			if requiredSubCategory:
				if Glyphs.versionNumber >= 3 and requiredSubCategory in caseDict:
					if thisGlyph.case != caseDict[requiredSubCategory]:
						continue
				elif not (thisGlyph.subCategory == requiredSubCategory or (requiredSubCategory == "Other" and thisGlyph.subCategory is None)):
					continue
			nameList.append(thisGlyph.name)
		return nameList

	def glyphNamesInCurrentTab(self, thisFont):
		"""Names of the glyphs in the font's current tab, each name once, in the order of the font."""
		thisTab = thisFont.currentTab
		if thisTab is None:
			return set()
		namesInTab = set()
		for thisLayer in thisTab.layers:
			if isinstance(thisLayer, GSControlLayer):
				continue  # line breaks and the like
			if thisLayer.parent is not None:
				namesInTab.add(thisLayer.parent.name)
		return namesInTab

	def glyphNamesForChoice(self, thisFont, choice, requiredScript, excludedGlyphNameParts, excludeNonExporting, pathGlyphsOnly, mustContain):
		"""Glyph names for an entry of the left or right glyph popup."""
		if choice == currentTabEntry:
			namesInTab = self.glyphNamesInCurrentTab(thisFont)
			return [
				thisGlyph.name for thisGlyph in thisFont.glyphs
				if thisGlyph.name in namesInTab and self.glyphPassesFilters(thisGlyph, requiredScript, excludedGlyphNameParts, excludeNonExporting, pathGlyphsOnly, mustContain)
			]
		if choice in categoriesForAllEntries:
			categories = categoriesForAllEntries[choice]
			return [
				thisGlyph.name for thisGlyph in thisFont.glyphs
				if thisGlyph.category in categories and self.glyphPassesFilters(thisGlyph, requiredScript, excludedGlyphNameParts, excludeNonExporting, pathGlyphsOnly, mustContain)
			]
		category, subCategory = self.splitString(choice)
		return self.listOfNamesForCategories(thisFont, category, subCategory, requiredScript, excludedGlyphNameParts, excludeNonExporting, pathGlyphsOnly, mustContain)

	def choiceFromPopup(self, prefName):
		index = self.prefInt(prefName)
		if not 0 <= index < len(glyphChoices):
			index = 0
		return glyphChoices[index]

	def glyphListsForFont(self, thisFont):
		"""Returns the glyph names for the left and for the right side, according to the current settings."""
		script = self.pref("popupScript")
		excludedGlyphNameParts = self.splitString(self.pref("excludeSuffixes"), delimiter=",", minimum=0)
		excludeNonExporting = self.prefBool("excludeNonExporting")
		pathGlyphsOnly = self.prefBool("pathGlyphsOnly")
		limitLeftSuffixes = self.splitString(self.pref("limitLeftSuffixes"), delimiter=",", minimum=0)
		limitRightSuffixes = self.splitString(self.pref("limitRightSuffixes"), delimiter=",", minimum=0)
		firstList = self.glyphNamesForChoice(
			thisFont, self.choiceFromPopup("popupLeftCat"), script, excludedGlyphNameParts, excludeNonExporting, pathGlyphsOnly, limitLeftSuffixes
		)
		secondList = self.glyphNamesForChoice(
			thisFont, self.choiceFromPopup("popupRightCat"), script, excludedGlyphNameParts, excludeNonExporting, pathGlyphsOnly, limitRightSuffixes
		)
		return firstList, secondList

	def targets(self):
		"""Returns (font, masters) tuples according to the scope."""
		scope = self.prefInt("popupScope")
		if scope in (0, 1):
			fonts = [Glyphs.font] if Glyphs.font else []
		else:
			fonts = list(Glyphs.fonts)
		targets = []
		for thisFont in fonts:
			if scope in (1, 3):
				masters = list(thisFont.masters)
			else:
				masters = [thisFont.selectedFontMaster]
			targets.append((thisFont, masters))
		return targets

	def predictedPairCount(self):
		"""How many glyph pairs will be measured in total."""
		pairCount = 0
		for thisFont, masters in self.targets():
			firstList, secondList = self.glyphListsForFont(thisFont)
			pairCount += len(firstList) * len(secondList) * len(masters)
		return pairCount

	def masterSwitch(self, sender=None):
		if sender is self.w.nextButton:
			Glyphs.font.masterIndex += 1

	def splitString(self, string, delimiter=":", minimum=2):
		# split string into a list:
		returnList = string.split(delimiter)

		# remove trailing spaces:
		for i in range(len(returnList)):
			returnList[i] = returnList[i].strip()

		# if necessary fill up with None:
		while len(returnList) < minimum:
			returnList.append(None)

		if returnList == [""]:
			return None

		return returnList

	def measureLayerAtHeightFromLeftOrRight(self, thisLayer, height, leftSide=True):
		try:
			if leftSide:
				measurement = thisLayer.lsbAtHeight_(height)
			else:
				measurement = thisLayer.rsbAtHeight_(height)
			if measurement < NSNotFound:
				return measurement
			else:
				return None
		except Exception as e:
			raise e
			return None

	def KernCrasherMain(self, sender):
		try:
			# update settings to the latest user input:
			self.SavePreferences()

			targets = self.targets()
			if not targets:
				Message(title="No Font Open", message="KernCrasher requires a font. Open a font and run the script again.", OKButton=None)
				return

			# reset progress bar:
			self.w.bar.set(0)

			# start taking time:
			start = timer()

			# start reporting to macro window:
			reportInMacroWindow = self.pref("reportCrashesInMacroWindow")
			if reportInMacroWindow:
				Glyphs.clearLog()
				print("KernCrasher Report\n")

			# query user input:
			step = intervalList[self.pref("popupSpeed")]
			directionSensitive = self.w.directionSensitive.get() == 1
			totalPairs = self.predictedPairCount()
			analyzedPairs = 0
			totalCrashCount = 0

			for thisFont, masters in targets:
				# get lists of glyph names:
				firstList, secondList = self.glyphListsForFont(thisFont)
				if not firstList or not secondList:
					print(
						"⚠️ %s: no pairs to analyze. With the current settings, there are %i glyphs for the left side and %i glyphs for the right side. Skipping this font." % (
							thisFont.familyName,
							len(firstList),
							len(secondList),
						)
					)
					continue

				crashes = {}  # left glyph name -> right glyph names (in order, each only once, even if they collide in more than one master)
				processedMasterIDs = []
				for thisFontMaster in masters:
					thisFontMasterID = thisFontMaster.id
					if reportInMacroWindow:
						print("%s, master %s:\n" % (thisFont.familyName, thisFontMaster.name))

					ignoreIntervals = sortedIntervalsFromString(self.pref("ignoreIntervals"), thisFont, thisFontMasterID)
					minDistance = 0.0
					try:
						minDistance = distanceFromEntry(self.pref("minDistance"), thisFont, thisFontMasterID)
					except Exception as e:
						print("⚠️ Warning: Could not read min distance entry. Will default to 0.\n%s" % e)
						import traceback
						print(traceback.format_exc())
						print()

					if reportInMacroWindow:
						print("Minimum Distance: %i\n" % minDistance)
						print("Left glyphs:\n%s\n" % ", ".join(firstList))
						print("Right glyphs:\n%s\n" % ", ".join(secondList))

					for firstGlyphName in firstList:
						# update progress bar:
						self.w.bar.set(int(100 * (float(analyzedPairs) / max(totalPairs, 1))))
						analyzedPairs += len(secondList)
						# determine left glyph:
						leftLayer = thisFont.glyphs[firstGlyphName].layers[thisFontMasterID].copyDecomposedLayer()
						leftLayer.decomposeSmartOutlines()

						# cycle through right glyphs:
						for secondGlyphName in secondList:
							rightLayer = thisFont.glyphs[secondGlyphName].layers[thisFontMasterID].copyDecomposedLayer()
							rightLayer.decomposeSmartOutlines()
							kerning = effectiveKerning(firstGlyphName, secondGlyphName, thisFont, thisFontMasterID, directionSensitive)
							distanceBetweenShapes = minDistanceBetweenTwoLayers(leftLayer, rightLayer, interval=step, kerning=kerning, report=False, ignoreIntervals=ignoreIntervals)
							if distanceBetweenShapes is not None and distanceBetweenShapes < minDistance:
								totalCrashCount += 1
								crashes.setdefault(firstGlyphName, {})[secondGlyphName] = None
								if reportInMacroWindow:
									print("- %s %s: %i" % (firstGlyphName, secondGlyphName, distanceBetweenShapes))
					processedMasterIDs.append(thisFontMasterID)

				# one tab per font, with the collisions of all its masters:
				if crashes:
					tabString = "\n".join("/space".join("/%s/%s" % (left, right) for right in rights) for left, rights in crashes.items())
					if len(tabString) > 40:
						# disable reporters (avoid slowdown)
						Glyphs.defaults["visibleReporters"] = None
					if self.pref("reuseCurrentTab") and thisFont.currentTab:
						tab = thisFont.currentTab
						tab.text = tabString
					else:
						tab = thisFont.newTab(tabString)
					# the tab has its own master; make it show a master that was checked:
					checkedIndexes = [i for i, thisMaster in enumerate(thisFont.masters) if thisMaster.id in processedMasterIDs]
					tab.masterIndex = thisFont.masterIndex if thisFont.masterIndex in checkedIndexes else checkedIndexes[0]

			# update progress bar:
			self.w.bar.set(100)

			if analyzedPairs == 0:
				Message(
					title="Error: could not find any pairs",
					message="The criteria for glyph selection are too strict. With the current settings, there are no glyph pairs to analyze.",
					OKButton=None,
				)

			# take time:
			end = timer()
			seconds = end - start
			if seconds > 60.0:
				timereport = "%i:%02i minutes" % (seconds // 60, seconds % 60)
			elif seconds < 1.0:
				timereport = "%.2f seconds" % seconds
			elif seconds < 20.0:
				timereport = "%.1f seconds" % seconds
			else:
				timereport = "%i seconds" % seconds

			if totalCrashCount:
				report = "%i kerning crashes have been found. Time elapsed: %s." % (totalCrashCount, timereport)
			else:
				report = "No collisions found. Time elapsed: %s. Congrats!" % timereport

			# Report in Macro Window:
			if reportInMacroWindow:
				print(report)
				Glyphs.showMacroWindow()

		except Exception as e:
			print("KernCrasher Error: %s" % e)
			import traceback
			print(traceback.format_exc())


KernCrasher()

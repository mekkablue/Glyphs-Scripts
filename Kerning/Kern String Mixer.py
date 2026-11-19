# MenuTitle: Kern String Mixer
__doc__ = """
Intersect two sets of glyphs with each other in order to get all possible glyph combinations, optionally without repeating pairs that are in the text already, and optionally only pairs of kerning groups. The glyphs come from the selection, from text entries, from categories or from tokens.
"""

import vanilla
from kernanalysis import stringToListOfGlyphsForFont, listOfNamesForCategories, categoryList, splitString
from mekkablue import mekkaObject, reportFontName, UpdateButton
from GlyphsApp import Glyphs, GSFeature, Message
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSTextAlignmentRight,
	NSWindowStyleMaskResizable,
)
from Foundation import NSSize

defaultTokens = (
	"$[category like 'Letter' and case in {upper,lower}]  # UPPERCASE AND LOWERCASE LETTERS",
	"$[category like 'Number' and case = minor]",
	"$[name like '*superior*' or name like '*inferior*']",
	"$[name like '*.ss??*']  # STYLISTIC SETS",
	"$[case = minor]",
	"$[case = smallCaps]",
	"$[category like 'Punctuation']",
	"$[subCategory in {'Quote','Parenthesis','Dash'}]",
	"$[category like 'Number' and case != minor]",
	"$[subCategory like 'Math']  # MATHEMATICAL OPERATORS",
	"$[category like 'Letter' and case = upper]",
	"$[category like 'Letter' and case = lower]",
	"$[category like 'Letter' and script like 'latin']",
	"$[category like 'Letter' and script like 'cyrillic']",
	"$[category like 'Letter' and script like 'greek']",
)

glyphsTabIndex, categoriesTabIndex, tokensTabIndex = 0, 1, 2
tabsHeight = 150  # the tabs have a fixed height; it must fit the tallest tab (Glyphs)


class KernStringMixer(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"tabs": glyphsTabIndex,
		"glyphsSource": 0,
		"manualFirst": "HOAFTVXY/*.ss01",
		"manualSecond": "",
		"scriptPopup": 0,
		"leftCategoryPopup": 0,
		"rightCategoryPopup": 0,
		"mixString1": defaultTokens[0],
		"mixString2": defaultTokens[1],
		"groupsOnly": False,
		"exportingOnly": True,
		"pathsOnly": False,
		"avoidDuplicates": True,
		"reuseTab": True,
	}
	scripts = ("latin", "cyrillic", "greek")

	def __init__(self):
		# Window 'self.w':
		windowWidth = 420
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Kern String Mixer",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15
		tabInset = 12

		self.w.descriptionText = vanilla.TextBox("auto", "Mix glyphs for a new tab of all possible glyph combos:", sizeStyle='small', selectable=True)

		# the controls inside of the tabs are kept here, because they are not attributes of the window:
		self.tabElements = {}
		self.w.tabs = vanilla.Tabs("auto", ("Glyphs", "Categories", "Tokens"), callback=self.SavePreferences, sizeStyle="small")
		self.w.tabs.setToolTip("Where the glyphs for the two sides of the pairs come from: the selection or text entries (Glyphs), categories, or tokens. The tab that is open is the one that counts.")
		glyphsTab, categoriesTab, tokensTab = self.w.tabs[0], self.w.tabs[1], self.w.tabs[2]

		# --- Glyphs tab ---
		glyphsTab.glyphsSource = vanilla.VerticalRadioGroup("auto", ("Currently selected glyphs", "Enter manually"), callback=self.SavePreferences, sizeStyle="small")
		glyphsTab.glyphsSource.setToolTip("Use the glyphs selected in the frontmost font for both sides of the pairs, or enter the glyphs for the two sides below.")
		entryTooltip = (
			"Characters (HOAFTVXY), slash-escaped glyph names (/Aacute /a.sc), names with wildcards (/*.ss01 for all glyphs that end in .ss01, "
			"/A? for A plus one more character) and categories (@Letter:Uppercase) can be mixed. Spaces are ignored."
		)
		glyphsTab.manualFirst = vanilla.EditText("auto", "HOAFTVXY/*.ss01", callback=self.SavePreferences, sizeStyle="small")
		glyphsTab.manualFirst.setToolTip("Glyphs for the first side of the pairs (one line of the text per glyph). " + entryTooltip)
		glyphsTab.manualSecond = vanilla.EditText("auto", "", callback=self.SavePreferences, sizeStyle="small")
		glyphsTab.manualSecond.getNSTextField().setPlaceholderString_("Leave empty to intersect first group with itself")
		glyphsTab.manualSecond.setToolTip("Glyphs for the second side of the pairs. Leave empty to intersect the first group with itself. " + entryTooltip)
		self.tabElements.update({
			"glyphsSource": glyphsTab.glyphsSource,
			"manualFirst": glyphsTab.manualFirst,
			"manualSecond": glyphsTab.manualSecond,
		})
		glyphsTab.addAutoPosSizeRules(
			[
				"H:|-inset-[glyphsSource]-(>=inset)-|",
				"H:|-indent-[manualFirst]-inset-|",
				"H:|-indent-[manualSecond]-inset-|",
				"V:|-gap-[glyphsSource]-gap-[manualFirst]-row-[manualSecond]-(>=gap)-|",
			],
			metrics={"inset": tabInset, "indent": tabInset + 18, "gap": 8, "row": 6},
		)

		# --- Categories tab ---
		categoriesTab.scriptText = vanilla.TextBox("auto", "Script:", sizeStyle='small', selectable=True)
		categoriesTab.scriptPopup = vanilla.PopUpButton("auto", self.scripts, sizeStyle='small', callback=self.SavePreferences)
		categoriesTab.scriptPopup.setToolTip("Script for letters, will be ignored for all other categories (e.g., numbers).")
		categoriesTab.scriptUpdate = UpdateButton("auto", callback=self.updateScripts)
		categoriesTab.scriptUpdate.setToolTip("Lists the scripts of the glyphs in the frontmost font.")
		categoriesTab.leftCategoryText = vanilla.TextBox("auto", "Left Category:", sizeStyle='small', selectable=True)
		categoriesTab.leftCategoryPopup = vanilla.PopUpButton("auto", categoryList, sizeStyle='small', callback=self.SavePreferences)
		categoriesTab.leftCategoryPopup.setToolTip("Category:Subcategory for the left side of the pairs.")
		categoriesTab.rightCategoryText = vanilla.TextBox("auto", "Right Category:", sizeStyle='small', selectable=True)
		categoriesTab.rightCategoryPopup = vanilla.PopUpButton("auto", categoryList, sizeStyle='small', callback=self.SavePreferences)
		categoriesTab.rightCategoryPopup.setToolTip("Category:Subcategory for the right side of the pairs.")
		self.tabElements.update({
			"scriptPopup": categoriesTab.scriptPopup,
			"leftCategoryPopup": categoriesTab.leftCategoryPopup,
			"rightCategoryPopup": categoriesTab.rightCategoryPopup,
		})
		# labels are right-aligned, hug their text and share one width:
		for label in (categoriesTab.scriptText, categoriesTab.leftCategoryText, categoriesTab.rightCategoryText):
			nsLabel = label.getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		categoriesTab.addAutoPosSizeRules(
			[
				"H:|-inset-[scriptText]-gap-[scriptPopup]-gap-[scriptUpdate]-inset-|",
				"H:|-inset-[leftCategoryText]-gap-[leftCategoryPopup]-inset-|",
				"H:|-inset-[rightCategoryText]-gap-[rightCategoryPopup]-inset-|",
				"V:|-gap-[scriptPopup]-row-[leftCategoryPopup]-row-[rightCategoryPopup]-(>=gap)-|",
				{"view1": categoriesTab.scriptText, "attribute1": "centerY", "view2": categoriesTab.scriptPopup, "attribute2": "centerY"},
				{"view1": categoriesTab.scriptUpdate, "attribute1": "centerY", "view2": categoriesTab.scriptPopup, "attribute2": "centerY"},
				{"view1": categoriesTab.leftCategoryText, "attribute1": "centerY", "view2": categoriesTab.leftCategoryPopup, "attribute2": "centerY"},
				{"view1": categoriesTab.rightCategoryText, "attribute1": "centerY", "view2": categoriesTab.rightCategoryPopup, "attribute2": "centerY"},
				{"view1": categoriesTab.scriptText, "attribute1": "width", "view2": categoriesTab.rightCategoryText, "attribute2": "width"},
				{"view1": categoriesTab.leftCategoryText, "attribute1": "width", "view2": categoriesTab.rightCategoryText, "attribute2": "width"},
			],
			metrics={"inset": tabInset, "gap": 8, "row": 6},
		)

		# --- Tokens tab ---
		tokenHelpText = "Write a token. Click on the help button for more info."
		tokensTab.mixString1 = vanilla.ComboBox("auto", defaultTokens, callback=self.SavePreferences)
		tokensTab.mixString1.setToolTip(tokenHelpText)
		tokensTab.mixString2 = vanilla.ComboBox("auto", defaultTokens, callback=self.SavePreferences)
		tokensTab.mixString2.setToolTip(tokenHelpText)
		tokensTab.helpTokens = vanilla.HelpButton("auto", callback=self.openURL)
		tokensTab.helpTokens.setToolTip("Opens the tutorial about tokens on glyphsapp.com.")
		self.tabElements.update({
			"mixString1": tokensTab.mixString1,
			"mixString2": tokensTab.mixString2,
		})
		# the combo boxes take the width, however long their tokens are:
		for comboBox in (tokensTab.mixString1, tokensTab.mixString2):
			comboBox.getNSComboBox().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		tokensTab.addAutoPosSizeRules(
			[
				"H:|-inset-[mixString1]-inset-|",
				"H:|-inset-[mixString2]-inset-|",
				"H:|-inset-[helpTokens]-(>=inset)-|",
				"V:|-gap-[mixString1]-row-[mixString2]-gap-[helpTokens]-(>=gap)-|",
			],
			metrics={"inset": tabInset, "gap": 8, "row": 6},
		)

		# --- checkboxes below the tabs ---
		self.w.groupsOnly = vanilla.CheckBox("auto", "Groups only", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.groupsOnly.setToolTip(
			"If enabled, looks for pairs of kerning groups, not of all glyphs. After ‘VB’ it will not add ‘VD’ if D and B are in the same left kerning group, because the same kerning pair applies to both. Glyphs without a group count as their own group."
		)
		self.w.exportingOnly = vanilla.CheckBox("auto", "Exporting only", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.exportingOnly.setToolTip("Skip glyphs that are set to not export.")
		self.w.pathsOnly = vanilla.CheckBox("auto", "Paths only", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.pathsOnly.setToolTip("Skip glyphs without paths of their own, i.e., pure composites (and spaces).")

		self.w.avoidDuplicates = vanilla.CheckBox("auto", "Avoid duplicate pairs", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.avoidDuplicates.setToolTip(
			"If enabled, a pair that is in the text already is not repeated. If ‘BA’ appeared in the A row, the B row will not contain it again. Makes the text shorter if both sides have glyphs in common, e.g., if both are the same."
		)
		self.w.reuseTab = vanilla.CheckBox("auto", "Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.reuseTab.setToolTip("If enabled, will not open a new tab, but reuse the current Edit tab. Will open an Edit tab if none is open.")

		# Status line, with the prediction:
		self.w.statusText = vanilla.TextBox("auto", "🔮 Will show – pairs.", sizeStyle='small')
		self.w.statusText.setToolTip("How many pairs the text will show with the current settings.")
		self.w.statusText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		self.w.runButton = vanilla.Button("auto", "Mix", callback=self.KernStringMixerMain)
		self.w.runButton.setToolTip("Opens a tab with the pairs: one line per glyph of the first side, each with all glyphs of the second side.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[tabs]-inset-|",
				"H:|-inset-[groupsOnly]-gap-[exportingOnly]-gap-[pathsOnly]-(>=inset)-|",
				"H:|-inset-[avoidDuplicates]-gap-[reuseTab]-(>=inset)-|",
				"H:|-inset-[statusText]-(>=gap)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-row-[tabs(tabsHeight)]-row-[groupsOnly]-checkRow-[avoidDuplicates]-inset-[runButton]-inset-|",
				{"view1": self.w.exportingOnly, "attribute1": "centerY", "view2": self.w.groupsOnly, "attribute2": "centerY"},
				{"view1": self.w.pathsOnly, "attribute1": "centerY", "view2": self.w.groupsOnly, "attribute2": "centerY"},
				{"view1": self.w.reuseTab, "attribute1": "centerY", "view2": self.w.avoidDuplicates, "attribute2": "centerY"},
				{"view1": self.w.statusText, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5, "tabsHeight": tabsHeight},
		)

		# Load Settings:
		self.LoadPreferences()

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

	# --- preferences and UI ---

	def uiElement(self, prefName):
		# the controls in the tabs are not attributes of the window:
		if prefName in self.tabElements:
			return self.tabElements[prefName]
		return super().uiElement(prefName)

	def updateUI(self, sender=None):
		manualEntry = self.prefInt("glyphsSource") == 1
		self.tabElements["manualFirst"].enable(manualEntry)
		self.tabElements["manualSecond"].enable(manualEntry)
		self.setStatus(self.predictionText())

	def setStatus(self, text):
		"""Sets the status line and redraws it right away."""
		self.w.statusText.set(text)
		self.w.statusText.getNSTextField().display()

	def openURL(self, sender=None):
		import webbrowser
		webbrowser.open("https://www.glyphsapp.com/learn/tokens")

	def updateScripts(self, sender=None):
		font = Glyphs.font
		if font:
			scripts = []
			for thisGlyph in font.glyphs:
				if thisGlyph.script and thisGlyph.script not in scripts:
					scripts.append(thisGlyph.script)
			if scripts:
				scriptPopup = self.tabElements["scriptPopup"]
				scriptPopup.setItems(scripts)
				scriptPopup.set(0)
				self.SavePreferences()

	# --- which glyphs ---

	def expandToken(self, token, font=None, verbose=True):
		if verbose:
			print("Token: %s" % token)

		# clean up token:
		if "#" in token:
			token = token[:token.find("#")]
		token = token.strip()
		if token.startswith("$[") and token.endswith("]"):
			token = token[2:-1]

		# check for font:
		if not font:
			font = Glyphs.font
			if not font:
				return ""

		if hasattr(GSFeature, "evaluatePredicateToken_font_contextLabel_error_"):
			evaluatedToken = GSFeature.evaluatePredicateToken_font_contextLabel_error_(token, font, "", None)
		else:
			evaluatedToken = GSFeature.evaluatePredicateToken_font_error_(token, font, None)
		if verbose:
			print("Evaluation: %s\n" % evaluatedToken)
		return evaluatedToken or ""

	def namesFromEntry(self, entry, font):
		"""Glyph names for an entry like ‘HOAFTVXY/*.ss01’, as understood by the parser of the kerning scripts."""
		return [thisGlyph.name for thisGlyph in stringToListOfGlyphsForFont(entry.strip(), font, report=False, excludeNonExporting=False)]

	def namesForCategory(self, font, popupName, script):
		index = self.prefInt(popupName)
		choice = categoryList[index if 0 <= index < len(categoryList) else 0]
		category, subCategory = splitString(choice)
		return [thisGlyph.name for thisGlyph in listOfNamesForCategories(font, category, subCategory, script, None, False)]

	def filteredNames(self, font, names):
		"""Each name only once, without the glyphs that are skipped according to ‘Exporting only’ and ‘Paths only’."""
		exportingOnly = self.prefBool("exportingOnly")
		pathsOnly = self.prefBool("pathsOnly")
		masterID = font.selectedFontMaster.id
		filteredNames = []
		for name in dict.fromkeys(names):
			thisGlyph = font.glyphs[name]
			if thisGlyph is None:
				continue
			if exportingOnly and not thisGlyph.export:
				continue
			if pathsOnly:
				thisLayer = thisGlyph.layers[masterID]
				if thisLayer is None or not thisLayer.paths:
					continue
			filteredNames.append(name)
		return filteredNames

	def glyphNameLists(self, font, verbose=False):
		"""Returns the glyph names for the first and the second side of the pairs, according to the tab that is open."""
		tab = self.prefInt("tabs")
		if tab == glyphsTabIndex:
			if self.prefInt("glyphsSource") == 0:
				firstNames = [thisLayer.parent.name for thisLayer in font.selectedLayers if thisLayer.parent is not None]
				secondNames = firstNames
			else:
				firstNames = self.namesFromEntry(self.pref("manualFirst"), font)
				secondEntry = self.pref("manualSecond").strip()
				secondNames = self.namesFromEntry(secondEntry, font) if secondEntry else firstNames
		elif tab == categoriesTabIndex:
			scripts = self.tabElements["scriptPopup"].getItems()
			scriptIndex = self.prefInt("scriptPopup")
			script = scripts[scriptIndex] if 0 <= scriptIndex < len(scripts) else self.scripts[0]
			firstNames = self.namesForCategory(font, "leftCategoryPopup", script)
			secondNames = self.namesForCategory(font, "rightCategoryPopup", script)
		else:
			firstNames = self.expandToken(self.pref("mixString1"), font=font, verbose=verbose).split()
			secondNames = self.expandToken(self.pref("mixString2"), font=font, verbose=verbose).split()
		return self.filteredNames(font, firstNames), self.filteredNames(font, secondNames)

	def groupsOfNames(self, font, names):
		"""Returns the right group and the left group for each glyph name (None for glyphs without a group)."""
		rightGroups, leftGroups = {}, {}
		for name in names:
			thisGlyph = font.glyphs[name]
			rightGroups[name] = thisGlyph.rightKerningGroup
			leftGroups[name] = thisGlyph.leftKerningGroup
		return rightGroups, leftGroups

	# --- the text ---

	def mixedText(self, firstNames, secondNames, avoidDuplicates=True, groups=None):
		"""
		Returns the text for the tab (one line per first glyph, ‘/a/b/a/c/a’, so a-b, b-a, a-c and c-a are all next to each other),
		the number of pairs left out because they were in the text already, and the number of pairs in the text.
		groups: None, or the right groups and the left groups of the glyphs (see groupsOfNames()); then pairs of groups count, not of glyphs.
		"""
		rightGroups, leftGroups = groups if groups else ({}, {})

		def pairKey(a, b):
			if not groups:
				return (a, b)
			# a glyph without a group stands for itself:
			return (
				("group", rightGroups[a]) if rightGroups.get(a) else ("glyph", a),
				("group", leftGroups[b]) if leftGroups.get(b) else ("glyph", b),
			)

		tabText = ""
		shownPairs = set()  # pairs of neighboring glyphs (or their groups) that are in the text already
		skippedCount = 0
		pairCount = 0
		for a in firstNames:
			glyphNames = []
			for b in secondNames:
				if (avoidDuplicates or groups) and pairKey(a, b) in shownPairs:
					skippedCount += 1
					continue
				glyphNames += [a, b]
				pairCount += 1
				# a is followed by b, and b by the next a (or the closing a of the line); register both right away,
				# so that with groups, the next glyph of the same group is recognized in this line already:
				shownPairs.add(pairKey(a, b))
				shownPairs.add(pairKey(b, a))
			if not glyphNames:
				continue  # all pairs of this line are in the text already
			glyphNames.append(a)
			tabText += "".join("/" + glyphName for glyphName in glyphNames) + "\n"
		return tabText, skippedCount, pairCount

	def mixForFont(self, font, verbose=False):
		"""Returns the glyph names of both sides, and the text with the pairs, left-out count and pair count."""
		firstNames, secondNames = self.glyphNameLists(font, verbose=verbose)
		groups = self.groupsOfNames(font, set(firstNames) | set(secondNames)) if self.prefBool("groupsOnly") else None
		return firstNames, secondNames, self.mixedText(firstNames, secondNames, avoidDuplicates=self.prefBool("avoidDuplicates"), groups=groups)

	def predictionText(self):
		font = Glyphs.font
		if font is None:
			return "🔮 Will show – pairs."
		firstNames, secondNames, (tabText, skippedCount, pairCount) = self.mixForFont(font)
		return f"🔮 Will show {pairCount:,} pair{'' if pairCount == 1 else 's'}."

	def KernStringMixerMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				report = reportFontName(thisFont)
				print("Kern String Mixer Report for %s" % report)
				print()

				firstNames, secondNames, (tabText, skippedCount, pairCount) = self.mixForFont(thisFont, verbose=True)
				if not firstNames or not secondNames:
					hint = {
						glyphsTabIndex: "Select glyphs in the frontmost font, or check the text entries.",
						categoriesTabIndex: "Check the script and the categories.",
						tokensTabIndex: "Check the tokens.",
					}[self.prefInt("tabs")]
					Message(
						title="Nothing to Mix",
						message="With the current settings, there are %i glyphs for the first side and %i glyphs for the second side in frontmost font ‘%s’. %s" % (
							len(firstNames),
							len(secondNames),
							thisFont.familyName,
							hint,
						),
						OKButton=None,
					)
					return

				if skippedCount:
					print("Left out %i pair%s that %s in the text already." % (skippedCount, "" if skippedCount == 1 else "s", "was" if skippedCount == 1 else "were"))

				thisTab = thisFont.currentTab
				if not thisTab or not self.pref("reuseTab"):
					thisTab = thisFont.newTab()
				thisTab.scale = 0.05
				thisTab.text = tabText
				thisTab.previewHeight = 0
				thisTab.updatePreview()

				self.w.close()  # delete if you want window to stay open

			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Kern String Mixer Error: %s" % e)
			import traceback
			print(traceback.format_exc())


KernStringMixer()

# MenuTitle: Remove Kerning Between Categories
__doc__ = """
Removes kerning between glyphs, categories, subcategories, scripts, cases. Optionally only exceptions, or only group kerning.
"""

import vanilla
from AppKit import NSTextAlignmentRight, NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject


class RemoveKerning(mekkaObject):
	prefDict = {
		"includeDirtyCategories": 0,
		"reportInMacroWindow": 0,
		"processAllMasters": 0,
		"limitToKind": 0,
		"kindToRemove": 0,
	}
	kindsToRemove = (
		"All exceptions (glyph-glyph, glyph-group, group-glyph)",
		"Strict exceptions (glyph-glyph)",
		"All group kernings (group-group, group-glyph, glyph-group)",
		"Strict group kernings (group-group)",
	)
	registeredCases = (
		"No Case",  # 0 GSNoCase
		"Uppercase",  # 1 GSUppercase
		"Lowercase",  # 2 GSLowercase
		"Smallcaps",  # 3 GSSmallcaps
		"Minor",  # 4 GSMinor
	)

	def __init__(self):
		# Window 'self.w':
		windowWidth = 620
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Remove Kerning Between Categories",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Removes group and singleton kerning between the following glyphs:", sizeStyle='small', selectable=True)

		rowNames = ("Category", "SubCategory", "Script", "Case")
		rowTitles = ("Category", "Subcategory", "Script", "Case")
		for rowName, rowTitle in zip(rowNames, rowTitles):
			setattr(self.w, f"left{rowName}Text", vanilla.TextBox("auto", f"L {rowTitle}", sizeStyle='small', selectable=True))
			setattr(self.w, f"left{rowName}", vanilla.PopUpButton("auto", (), sizeStyle='small', callback=self.updateUI))
			setattr(self.w, f"right{rowName}Text", vanilla.TextBox("auto", f"R {rowTitle}", sizeStyle='small', selectable=True))
			setattr(self.w, f"right{rowName}", vanilla.PopUpButton("auto", (), sizeStyle='small', callback=self.updateUI))

		if Glyphs.versionNumber < 3:
			self.w.leftCase.enable(False)
			self.w.rightCase.enable(False)

		self.ReloadCategories()

		self.w.limitToKind = vanilla.CheckBox("auto", "Only remove", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.limitToKind.setToolTip("Limit the removal to a kind of kerning pairs, chosen on the right. Without this, all pairs between the glyphs above are removed: exceptions as well as group kerning.")
		self.w.kindToRemove = vanilla.PopUpButton("auto", self.kindsToRemove, callback=self.SavePreferences, sizeStyle='small')
		self.w.kindToRemove.setToolTip(
			"Exceptions are pairs with a glyph on at least one side (glyph-glyph, glyph-group, group-glyph); ‘strict’ exceptions are glyph-glyph pairs only. "
			"Group kerning is pairs with a group on at least one side (group-group, group-glyph, glyph-group); ‘strict’ group kerning is group-group pairs only."
		)

		self.w.includeDirtyCategories = vanilla.CheckBox("auto", "Delete group kerning even if groups are ‘dirty’ (e.g., group with uppercase and lowercase letters mixed)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.reportInMacroWindow = vanilla.CheckBox("auto", "Detailed report in macro window", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.processAllMasters = vanilla.CheckBox("auto", "Process all masters (otherwise current master only)", value=False, callback=self.SavePreferences, sizeStyle='small')

		self.w.progress = vanilla.ProgressBar("auto")
		self.w.progress.set(0)  # set progress indicator to zero

		self.w.statusText = vanilla.TextBox("auto", "🔮 Will remove – pairs.", sizeStyle='small', selectable=True)
		self.w.statusText.setToolTip("Before you run: how many kerning pairs will be removed with the current settings. Afterwards: how many were removed.")
		self.w.statusText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Remove", callback=self.RemoveKerningMain)
		self.w.setDefaultButton(self.w.runButton)

		# Reload Button:
		self.w.reloadButton = vanilla.Button("auto", "Reload", callback=self.ReloadCategories)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.limitToKind.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		self.w.kindToRemove.getNSPopUpButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		self.w.kindToRemove.getNSPopUpButton().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# labels are right-aligned, hug their text and share one width:
		labelNames = [f"{side}{rowName}Text" for rowName in rowNames for side in ("left", "right")]
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		def equal(attribute, viewName, referenceName):
			return {"view1": getattr(self.w, viewName), "attribute1": attribute, "view2": getattr(self.w, referenceName), "attribute2": attribute}

		rules = ["H:|-inset-[descriptionText]-inset-|"]
		for rowName in rowNames:
			rules.append(f"H:|-inset-[left{rowName}Text]-gap-[left{rowName}(>=150)]-columnGap-[right{rowName}Text]-gap-[right{rowName}(>=150)]-inset-|")
			for viewName in (f"left{rowName}Text", f"right{rowName}Text", f"right{rowName}"):
				rules.append({"view1": getattr(self.w, viewName), "attribute1": "centerY", "view2": getattr(self.w, f"left{rowName}"), "attribute2": "centerY"})
			# all labels share one width, and so do all popups:
			if rowName != "Category":
				rules.append(equal("width", f"left{rowName}Text", "leftCategoryText"))
				rules.append(equal("width", f"left{rowName}", "leftCategory"))
			rules.append(equal("width", f"right{rowName}Text", "leftCategoryText"))
			rules.append(equal("width", f"right{rowName}", "leftCategory"))
		rules += [
			"H:|-inset-[limitToKind]-gap-[kindToRemove]-inset-|",
			"H:|-inset-[includeDirtyCategories]-(>=inset)-|",
			"H:|-inset-[reportInMacroWindow]-(>=inset)-|",
			"H:|-inset-[processAllMasters]-(>=inset)-|",
			"H:|-inset-[progress]-inset-|",
			"H:|-inset-[statusText]-(>=gap)-[reloadButton(>=70)]-gap-[runButton(>=70)]-inset-|",
			"V:|-inset-[descriptionText]-headlineGap-[leftCategory]-row-[leftSubCategory]-row-[leftScript]-row-[leftCase]-sectionGap-[limitToKind]-stackRow-[includeDirtyCategories]-stackRow-[reportInMacroWindow]-stackRow-[processAllMasters]-sectionGap-[progress(16)]-inset-[runButton]-inset-|",
			"V:[reloadButton]-inset-|",
			equal("centerY", "statusText", "runButton"),
			equal("centerY", "kindToRemove", "limitToKind"),
		]
		self.w.addAutoPosSizeRules(
			rules,
			metrics={"inset": inset, "gap": 8, "columnGap": 20, "row": 6, "headlineGap": 12, "sectionGap": 14, "stackRow": 8},
		)

		# Load Settings:
		self.LoadPreferences()
		self.updateUI()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def ReloadCategories(self, sender=None):
		try:
			categories = ["Any"] + self.allCategories()
			subcategories = ["Any"] + self.allSubCategories()
			scripts = ["Any"] + self.allScripts()
			cases = ["Any"] + self.allCases()
			self.w.leftCategory.setItems(categories)
			self.w.rightCategory.setItems(categories)
			self.w.leftSubCategory.setItems(subcategories)
			self.w.rightSubCategory.setItems(subcategories)
			self.w.leftScript.setItems(scripts)
			self.w.rightScript.setItems(scripts)
			self.w.leftCase.setItems(cases)
			self.w.rightCase.setItems(cases)
			if sender is not None:
				self.updateUI()  # the Reload button: the popups are back at ‘Any’
		except Exception as e:
			print(e)

	def updateUI(self, sender=None):
		self.w.kindToRemove.enable(bool(self.w.limitToKind.get()))
		self.buttonEnable()
		self.status(self.predictionText())

	def buttonEnable(self, sender=None):
		self.w.runButton.enable(self.anyCriterionIsSet())

	def allCases(self, sender=None):
		if Glyphs.versionNumber < 3:
			return []
		elif not Glyphs.font:
			return []
		else:
			cases = []
			for thisGlyph in Glyphs.font.glyphs:
				if thisGlyph.case is not None and thisGlyph.case not in cases:
					cases.append(thisGlyph.case)
			return sorted([self.registeredCases[c] for c in cases], key=lambda caseName: self.registeredCases.index(caseName))

	def caseAsNumberOrAny(self, caseName):
		if caseName == "Any":
			return caseName
		else:
			return self.registeredCases.index(caseName)

	def allCategories(self, sender=None):
		if not Glyphs.font:
			return []
		else:
			categories = []
			for thisGlyph in Glyphs.font.glyphs:
				if thisGlyph.category and thisGlyph.category not in categories:
					categories.append(thisGlyph.category)
			return categories

	def allSubCategories(self, sender=None):
		if not Glyphs.font:
			return []
		else:
			subcategories = []
			for thisGlyph in Glyphs.font.glyphs:
				if thisGlyph.subCategory and thisGlyph.subCategory not in subcategories:
					subcategories.append(thisGlyph.subCategory)
			return subcategories

	def allScripts(self, sender=None):
		if not Glyphs.font:
			return []
		else:
			scripts = []
			for thisGlyph in Glyphs.font.glyphs:
				if thisGlyph.script and thisGlyph.script not in scripts:
					scripts.append(thisGlyph.script)
			return scripts

	def status(self, statusmsg, macroWindow=False):
		self.w.statusText.set(statusmsg)
		if macroWindow:
			print(" %s" % statusmsg)

	def popupValues(self, side):
		"""Category, subcategory, script and case chosen in the popups of a side (‘left’ or ‘right’); ‘Any’ if not restricted."""
		category = getattr(self.w, f"{side}Category")
		subCategory = getattr(self.w, f"{side}SubCategory")
		script = getattr(self.w, f"{side}Script")
		case = getattr(self.w, f"{side}Case")
		return (
			category.getItems()[category.get()],
			subCategory.getItems()[subCategory.get()],
			script.getItems()[script.get()],
			self.caseAsNumberOrAny(case.getItems()[case.get()]),
		)

	def matchingGlyphsAndGroups(self, thisFont, reportInMacroWindow=None):
		"""
		Returns the names of the glyphs and the kerning groups that match the left and the right side:
		leftGlyphNames, rightGlyphNames, leftGroups, rightGroups.
		If reportInMacroWindow is not None, the status line shows the glyph that is looked at.
		"""
		announce = reportInMacroWindow is not None
		includeDirtyCategories = self.prefBool("includeDirtyCategories")
		leftCategory, leftSubCategory, leftScript, leftCase = self.popupValues("left")
		rightCategory, rightSubCategory, rightScript, rightCase = self.popupValues("right")

		leftGlyphNames, rightGlyphNames = [], []
		leftGroups, rightGroups = [], []

		for thisGlyph in thisFont.glyphs:
			if announce:
				self.status("🔠 %s" % thisGlyph.name, reportInMacroWindow)

			leftCategoryOK = leftCategory == "Any" or thisGlyph.category == leftCategory
			leftSubCategoryOK = leftSubCategory == "Any" or thisGlyph.subCategory == leftSubCategory
			leftScriptOK = leftScript == "Any" or thisGlyph.script == leftScript
			leftCaseOK = leftCase == "Any" or thisGlyph.case == leftCase
			isAMatchingLeftGlyph = leftCategoryOK and leftSubCategoryOK and leftScriptOK and leftCaseOK
			if isAMatchingLeftGlyph:
				leftGlyphNames.append(thisGlyph.name)
				if thisGlyph.rightKerningGroup and thisGlyph.rightKerningGroup not in leftGroups:
					leftGroups.append(thisGlyph.rightKerningGroup)

			rightCategoryOK = rightCategory == "Any" or thisGlyph.category == rightCategory
			rightSubCategoryOK = rightSubCategory == "Any" or thisGlyph.subCategory == rightSubCategory
			rightScriptOK = rightScript == "Any" or thisGlyph.script == rightScript
			rightCaseOK = rightCase == "Any" or thisGlyph.case == rightCase
			isAMatchingRightGlyph = rightCategoryOK and rightSubCategoryOK and rightScriptOK and rightCaseOK
			if isAMatchingRightGlyph:
				rightGlyphNames.append(thisGlyph.name)
				if thisGlyph.leftKerningGroup and thisGlyph.leftKerningGroup not in rightGroups:
					rightGroups.append(thisGlyph.leftKerningGroup)

		if not includeDirtyCategories:
			if announce:
				self.status("🛠️ Sorting out dirty groups…", reportInMacroWindow)
			if leftGroups or rightGroups:
				for thisGlyph in thisFont.glyphs:
					if thisGlyph.rightKerningGroup in leftGroups and thisGlyph.name not in leftGlyphNames:
						while thisGlyph.rightKerningGroup in leftGroups:
							leftGroups.remove(thisGlyph.rightKerningGroup)
						if announce:
							self.status("Dirty right group @MMK_L_%s skipped." % thisGlyph.rightKerningGroup, reportInMacroWindow)
					if thisGlyph.leftKerningGroup in rightGroups and thisGlyph.name not in rightGlyphNames:
						while thisGlyph.leftKerningGroup in rightGroups:
							rightGroups.remove(thisGlyph.leftKerningGroup)
						if announce:
							self.status("Dirty left group @MMK_R_%s skipped." % thisGlyph.leftKerningGroup, reportInMacroWindow)

		return leftGlyphNames, rightGlyphNames, leftGroups, rightGroups

	def mastersToProcess(self, thisFont):
		if self.prefBool("processAllMasters"):
			return tuple(m.id for m in thisFont.masters)
		return (thisFont.selectedFontMaster.id, )

	def pairsToRemove(self, thisFont, reportInMacroWindow=None):
		"""Returns (masterID, left name, right name) for each kerning pair that will be removed. Names are glyph names or @MMK_ group keys."""
		leftGlyphNames, rightGlyphNames, leftGroups, rightGroups = self.matchingGlyphsAndGroups(thisFont, reportInMacroWindow)

		# the kerning dictionary has glyph IDs and group keys; removeKerningForPair() wants glyph names and group keys:
		leftNameForKey, rightNameForKey = {}, {}
		for glyphNames, nameForKey in ((leftGlyphNames, leftNameForKey), (rightGlyphNames, rightNameForKey)):
			for glyphName in glyphNames:
				nameForKey[thisFont.glyphs[glyphName].id] = glyphName
		for groupName in leftGroups:
			leftNameForKey["@MMK_L_%s" % groupName] = "@MMK_L_%s" % groupName
		for groupName in rightGroups:
			rightNameForKey["@MMK_R_%s" % groupName] = "@MMK_R_%s" % groupName

		limitToKind = self.prefBool("limitToKind")
		kind = self.prefInt("kindToRemove")

		def isOfKind(leftKey, rightKey):
			leftIsGroup, rightIsGroup = leftKey.startswith("@"), rightKey.startswith("@")
			if kind == 0:  # all exceptions: a glyph on at least one side
				return not (leftIsGroup and rightIsGroup)
			if kind == 1:  # strict exceptions: glyph-glyph
				return not leftIsGroup and not rightIsGroup
			if kind == 2:  # all group kernings: a group on at least one side
				return leftIsGroup or rightIsGroup
			return leftIsGroup and rightIsGroup  # strict group kernings: group-group

		pairs = []
		for masterID in self.mastersToProcess(thisFont):
			kerning = thisFont.kerning[masterID]
			if not kerning:
				continue  # a master without any kerning has no kerning dictionary at all
			for leftKey in list(kerning.keys()):
				if leftKey not in leftNameForKey:
					continue
				for rightKey in list(kerning[leftKey].keys()):
					if rightKey in rightNameForKey and (not limitToKind or isOfKind(leftKey, rightKey)):
						pairs.append((masterID, leftNameForKey[leftKey], rightNameForKey[rightKey]))
		return pairs

	def predictionText(self):
		thisFont = Glyphs.font
		if thisFont is None or not self.anyCriterionIsSet():
			return "🔮 Will remove – pairs."
		pairCount = len(self.pairsToRemove(thisFont))
		return "🔮 Will remove %i pair%s." % (pairCount, "" if pairCount == 1 else "s")

	def anyCriterionIsSet(self):
		"""Without a criterion, everything would be removed: at least one popup is not ‘Any’, or the kind of pairs is limited."""
		if self.w.limitToKind.get():
			return True
		return any(
			getattr(self.w, f"{side}{rowName}").get() > 0
			for side in ("left", "right")
			for rowName in ("Category", "SubCategory", "Script", "Case")
		)

	def RemoveKerningMain(self, sender):
		try:
			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				self.status("❌ No font open.")
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return
			reportInMacroWindow = self.pref("reportInMacroWindow")

			# brings macro window to front and clears its log:
			if reportInMacroWindow:
				Glyphs.clearLog()

			print("Remove Kerning Between Categories Report for: %s" % thisFont.familyName)
			if thisFont.filepath:
				print(thisFont.filepath)
				print()

			pairs = self.pairsToRemove(thisFont, reportInMacroWindow)
			fullLength = max(1, len(pairs))
			removalCount = 0
			for masterID, leftName, rightName in pairs:
				masterName = thisFont.fontMasterForId_(masterID).name
				self.status("🛠️ Master %s: removing %s:%s" % (masterName, leftName, rightName), True)
				thisFont.removeKerningForPair(masterID, leftName, rightName)
				removalCount += 1
				self.w.progress.set(removalCount / fullLength * 100)

			self.w.progress.set(100)
			self.status(
				"✅ Removed %i pair%s." % (
					removalCount,
					"" if removalCount == 1 else "s",
				),
				True,
			)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Remove Kerning Between Categories Error: %s" % e)
			import traceback
			print(traceback.format_exc())


RemoveKerning()

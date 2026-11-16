# MenuTitle: Remove Kerning Between Categories
__doc__ = """
Removes kerning between glyphs, categories, subcategories, scripts.
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
	}
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
			"Remove Kerning",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Removes group and singleton kerning between the following glyphs:", sizeStyle='small', selectable=True)

		rowNames = ("Category", "SubCategory", "Script", "Case")
		rowTitles = ("Category", "Subcategory", "Script", "Case")
		for rowName, rowTitle in zip(rowNames, rowTitles):
			setattr(self.w, f"left{rowName}Text", vanilla.TextBox("auto", f"L {rowTitle}:", sizeStyle='small', selectable=True))
			setattr(self.w, f"left{rowName}", vanilla.PopUpButton("auto", (), sizeStyle='small', callback=self.buttonEnable))
			setattr(self.w, f"right{rowName}Text", vanilla.TextBox("auto", f"R {rowTitle}:", sizeStyle='small', selectable=True))
			setattr(self.w, f"right{rowName}", vanilla.PopUpButton("auto", (), sizeStyle='small', callback=self.buttonEnable))

		if Glyphs.versionNumber < 3:
			self.w.leftCase.enable(False)
			self.w.rightCase.enable(False)

		self.ReloadCategories()

		self.w.includeDirtyCategories = vanilla.CheckBox("auto", "Delete group kerning even if groups are ‘dirty’ (e.g., group with uppercase and lowercase letters mixed)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.reportInMacroWindow = vanilla.CheckBox("auto", "Detailed report in macro window", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.processAllMasters = vanilla.CheckBox("auto", "Process all masters (otherwise current master only)", value=False, callback=self.SavePreferences, sizeStyle='small')

		self.w.progress = vanilla.ProgressBar("auto")
		self.w.progress.set(0)  # set progress indicator to zero

		self.w.statusText = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle='small', selectable=True)
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
			"H:|-inset-[includeDirtyCategories]-(>=inset)-|",
			"H:|-inset-[reportInMacroWindow]-(>=inset)-|",
			"H:|-inset-[processAllMasters]-(>=inset)-|",
			"H:|-inset-[progress]-inset-|",
			"H:|-inset-[statusText]-(>=gap)-[reloadButton(>=70)]-gap-[runButton(>=70)]-inset-|",
			"V:|-inset-[descriptionText]-headlineGap-[leftCategory]-row-[leftSubCategory]-row-[leftScript]-row-[leftCase]-sectionGap-[includeDirtyCategories]-checkRow-[reportInMacroWindow]-checkRow-[processAllMasters]-sectionGap-[progress(16)]-inset-[runButton]-inset-|",
			"V:[reloadButton]-inset-|",
			equal("centerY", "statusText", "runButton"),
		]
		self.w.addAutoPosSizeRules(
			rules,
			metrics={"inset": inset, "gap": 8, "columnGap": 20, "row": 6, "headlineGap": 12, "sectionGap": 14, "checkRow": 5},
		)

		# Load Settings:
		self.LoadPreferences()

		self.buttonEnable()

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
		except Exception as e:
			print(e)

	def buttonEnable(self, sender=None):
		count = 0
		count += self.w.leftCategory.get()
		count += self.w.rightCategory.get()
		count += self.w.leftSubCategory.get()
		count += self.w.rightSubCategory.get()
		count += self.w.leftScript.get()
		count += self.w.rightScript.get()
		count += self.w.leftCase.get()
		count += self.w.rightCase.get()
		if count > 0:
			self.w.runButton.enable(True)
		else:
			self.w.runButton.enable(False)

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

	def RemoveKerningMain(self, sender):
		try:
			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				self.status("❌ No font open.")
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return
			includeDirtyCategories = self.pref("includeDirtyCategories")
			reportInMacroWindow = self.pref("reportInMacroWindow")

			# brings macro window to front and clears its log:
			if reportInMacroWindow:
				Glyphs.clearLog()

			print("'Remove Kerning' Report for: %s" % thisFont.familyName)
			if thisFont.filepath:
				print(thisFont.filepath)
				print()

			leftCategory = self.w.leftCategory.getItems()[self.w.leftCategory.get()]
			leftSubCategory = self.w.leftSubCategory.getItems()[self.w.leftSubCategory.get()]
			leftScript = self.w.leftScript.getItems()[self.w.leftScript.get()]
			leftCase = self.caseAsNumberOrAny(self.w.leftCase.getItems()[self.w.leftCase.get()])

			rightCategory = self.w.rightCategory.getItems()[self.w.rightCategory.get()]
			rightSubCategory = self.w.rightSubCategory.getItems()[self.w.rightSubCategory.get()]
			rightScript = self.w.rightScript.getItems()[self.w.rightScript.get()]
			rightCase = self.caseAsNumberOrAny(self.w.rightCase.getItems()[self.w.rightCase.get()])

			leftGlyphNames, rightGlyphNames = [], []
			leftGroups, rightGroups = [], []

			for thisGlyph in thisFont.glyphs:
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
				self.status("🛠️ Sorting out dirty groups…", reportInMacroWindow)
				if leftGroups or rightGroups:
					for thisGlyph in thisFont.glyphs:
						if thisGlyph.rightKerningGroup in leftGroups and thisGlyph.name not in leftGlyphNames:
							while thisGlyph.rightKerningGroup in leftGroups:
								leftGroups.remove(thisGlyph.rightKerningGroup)
							self.status("Dirty right group @MMK_L_%s skipped." % thisGlyph.rightKerningGroup, reportInMacroWindow)
						if thisGlyph.leftKerningGroup in rightGroups and thisGlyph.name not in rightGlyphNames:
							while thisGlyph.leftKerningGroup in rightGroups:
								rightGroups.remove(thisGlyph.leftKerningGroup)
							self.status("Dirty left group @MMK_R_%s skipped." % thisGlyph.leftKerningGroup, reportInMacroWindow)

			if self.pref("processAllMasters"):
				masterIDs = tuple([m.id for m in thisFont.masters])
			else:
				masterIDs = (thisFont.selectedFontMaster.id, )

			leftNames = leftGlyphNames + ["@MMK_L_%s" % groupname for groupname in leftGroups]
			rightNames = rightGlyphNames + ["@MMK_R_%s" % groupname for groupname in rightGroups]

			fullLength = max(1, len(masterIDs) * len(leftNames) * len(rightNames))
			counter = 0
			removalCount = 0

			for masterID in masterIDs:
				masterName = thisFont.fontMasterForId_(masterID).name
				self.status("🛠️ Processing master '%s'…" % masterName, reportInMacroWindow)
				if masterID in thisFont.kerning.keys():
					for leftName in leftNames:
						try:
							leftID = thisFont.glyphs[leftName].id
						except:
							# tried to find a glyph named like a group
							leftID = leftName
						if leftID in thisFont.kerning[masterID].keys():
							for rightName in rightNames:
								try:
									rightID = thisFont.glyphs[rightName].id
								except:
									# tried to find a glyph named like a group
									rightID = rightName
								if rightID in thisFont.kerning[masterID][leftID].keys():
									self.status("🛠️ Master %s: removing %s:%s" % (masterName, leftName, rightName), True)
									thisFont.removeKerningForPair(masterID, leftName, rightName)
									removalCount += 1
								counter += 1
								self.w.progress.set(counter / fullLength * 100)
						else:
							counter += len(rightNames)
							self.w.progress.set(counter / fullLength * 100)
				else:
					counter += len(leftNames) * len(rightNames)
					self.w.progress.set(counter / fullLength * 100)

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
			print("Remove Kerning Error: %s" % e)
			import traceback
			print(traceback.format_exc())


RemoveKerning()

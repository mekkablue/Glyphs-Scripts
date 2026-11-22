# MenuTitle: Compare Kerning Between Masters
__doc__ = """
Report differences in kerning structures between two masters, and sync them by adding zero kerns.
"""

import vanilla
from mekkablue import mekkaObject, newLineControlLayer, reportFontName, UpdateButton, makeWindowResizable
from GlyphsApp import Glyphs, Message
from Foundation import NSNotFound
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSTextAlignmentRight,
)


class CompareKerningBetweenMasters(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"firstMaster": 0,
		"secondMaster": 0,
		"group2group": True,
		"group2glyph": True,
		"glyph2group": True,
		"glyph2glyph": True,
		"reuseTab": True,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 350
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Compare Kerning Between Masters",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Compare kerning between two masters in frontmost font:", sizeStyle="small", selectable=True)

		self.w.firstMasterText = vanilla.TextBox("auto", "1st Master:", sizeStyle="small", selectable=True)
		self.w.firstMaster = vanilla.PopUpButton("auto", self.menuItemsForFrontMostFont(), sizeStyle="small", callback=self.SavePreferences)
		tooltipText = "The first of the two masters to compare."
		self.w.firstMasterText.setToolTip(tooltipText)
		self.w.firstMaster.setToolTip(tooltipText)

		self.w.secondMasterText = vanilla.TextBox("auto", "2nd Master:", sizeStyle="small", selectable=True)
		self.w.secondMaster = vanilla.PopUpButton("auto", self.menuItemsForFrontMostFont(), sizeStyle="small", callback=self.SavePreferences)
		tooltipText = "The second of the two masters to compare."
		self.w.secondMasterText.setToolTip(tooltipText)
		self.w.secondMaster.setToolTip(tooltipText)
		self.w.updateButton = UpdateButton("auto", callback=self.updateUI)
		self.w.updateButton.setToolTip("Updates the master lists from the frontmost font.")

		self.w.kernTypeText = vanilla.TextBox("auto", "Types of kerning to compare:", sizeStyle="small", selectable=True)

		self.w.group2group = vanilla.CheckBox("auto", "@group ↔︎ @group", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.group2group.setToolTip("Includes kern pairs between two groups in the comparison.")
		self.w.group2glyph = vanilla.CheckBox("auto", "@group ↔︎ glyph", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.group2glyph.setToolTip("Includes kern pairs between a group on the left and a glyph on the right in the comparison.")
		self.w.glyph2group = vanilla.CheckBox("auto", "glyph ↔︎ @group", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.glyph2group.setToolTip("Includes kern pairs between a glyph on the left and a group on the right in the comparison.")
		self.w.glyph2glyph = vanilla.CheckBox("auto", "glyph ↔︎ glyph", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.glyph2glyph.setToolTip("Includes kern pairs between two glyphs (exceptions) in the comparison.")

		self.w.reuseTab = vanilla.CheckBox("auto", "Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.reuseTab.setToolTip("If enabled, shows the result in the current Edit tab instead of opening a new tab.")

		# Buttons:
		self.w.syncButton = vanilla.Button("auto", "Sync Kern Pairs", callback=self.SyncKernPairs)
		self.w.syncButton.setToolTip(
			"Syncs kern pair structure between masters by adding zero kerns: kern pairs of the checked types that exist in only one of the two masters are added with the value 0 to the other one. Existing kerning is not changed. Helps preserve interpolatable kerning in OTVar exports."
		)
		self.w.runButton = vanilla.Button("auto", "Compare", callback=self.CompareKerningBetweenMastersMain)
		self.w.runButton.setToolTip("Opens a tab with the kern pairs of the checked types that exist in only one of the two masters.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels are right-aligned and hug their text, so the popups take the leftover width:
		for label in (self.w.firstMasterText, self.w.secondMasterText):
			nsLabel = label.getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[firstMasterText]-gap-[firstMaster]-inset-|",
				"H:|-inset-[secondMasterText]-gap-[secondMaster]-gap-[updateButton]-inset-|",
				"H:|-inset-[kernTypeText]-inset-|",
				"H:|-inset-[group2group]-inset-[group2glyph]-(>=inset)-|",
				"H:|-inset-[glyph2group]-inset-[glyph2glyph]-(>=inset)-|",
				"H:|-inset-[reuseTab]-(>=inset)-|",
				"H:|-inset-[syncButton(>=70)]-(>=gap)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-row-[firstMaster]-row-[secondMaster]-section-[kernTypeText]-row-[group2group]-checkRow-[glyph2group]-section-[reuseTab]-inset-[runButton]-inset-|",
				"V:[kernTypeText]-row-[group2glyph]-checkRow-[glyph2glyph]",
				{"view1": self.w.syncButton, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
				{"view1": self.w.firstMasterText, "attribute1": "centerY", "view2": self.w.firstMaster, "attribute2": "centerY"},
				{"view1": self.w.secondMasterText, "attribute1": "centerY", "view2": self.w.secondMaster, "attribute2": "centerY"},
				{"view1": self.w.updateButton, "attribute1": "centerY", "view2": self.w.secondMaster, "attribute2": "centerY"},
				# labels and the checkbox columns share one width each:
				{"view1": self.w.firstMasterText, "attribute1": "width", "view2": self.w.secondMasterText, "attribute2": "width"},
				{"view1": self.w.glyph2group, "attribute1": "width", "view2": self.w.group2group, "attribute2": "width"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5, "section": 12},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.verifyButtonStatus()
		self.w.open()
		self.w.makeKey()

	def menuItemsForFrontMostFont(self, sender=None):
		font = Glyphs.font
		if font:
			return [f"{m.name} (ID: {m.id})" for m in font.masters]
		else:
			return []

	def verifyButtonStatus(self, sender=None):
		font = Glyphs.font
		onOff = bool(font) and self.pref("firstMaster") != self.pref("secondMaster")
		self.w.runButton.enable(onOff)
		self.w.syncButton.enable(onOff)

	def updateUI(self, sender=None):
		menu = self.menuItemsForFrontMostFont()

		self.w.firstMaster.setItems(menu)
		leftChoice = self.pref("firstMaster")
		if len(menu) > leftChoice:
			self.w.firstMaster.set(leftChoice)

		self.w.secondMaster.setItems(menu)
		rightChoice = self.pref("secondMaster")
		if len(menu) > rightChoice:
			self.w.secondMaster.set(rightChoice)

		font = Glyphs.font
		onOff = bool(font) and self.pref("firstMaster") != self.pref("secondMaster")
		self.w.runButton.enable(onOff)
		self.w.syncButton.enable(onOff)

	def namesForGroupName(self, groupName, font, isLeft=True):
		names = []
		for g in font.glyphs:
			if isLeft:  # left side = right group
				if groupName[7:] == g.rightKerningGroup:
					names.append(g.name)
			else:
				if groupName[7:] == g.leftKerningGroup:
					names.append(g.name)
		return names

	def glyphNameForKerningName(self, name, font, isLeft=True):
		glyphName = None
		if name[0] == "@":
			names = self.namesForGroupName(name, font, isLeft=isLeft)
			if name.startswith("@MMK_"):
				glyphName = name.split("_")[2]
				if glyphName == "KO":
					glyphName = name.split("_")[3]
				if not font.glyphs[glyphName] or glyphName not in names:
					glyphName = None
			if not glyphName:
				for name in names:
					if font.glyphs[name]:
						glyphName = name
						break
		else:
			glyph = font.glyphForId_(name)
			if glyph:
				glyphName = glyph.name

		if glyphName:
			return glyphName
		else:
			print(f"⚠️ No glyph found for: {name}")
			return None

	def selectedMasters(self, font):
		"""Returns the first and the second master, as chosen in the popups."""
		masters = []
		for popup, prefName in ((self.w.firstMaster, "firstMaster"), (self.w.secondMaster, "secondMaster")):
			choice = popup.getItems()[self.prefInt(prefName)]
			masterID = choice.split("(ID: ")[1][:-1]
			masters.append(font.masters[masterID])
		return masters[0], masters[1]

	def enabledKinds(self):
		"""The kinds of kern pairs that are checked in the window."""
		return {kind for kind in ("group2group", "group2glyph", "glyph2group", "glyph2glyph") if self.pref(kind)}

	def kerningIsMissing(self, value):
		return value is None or value >= NSNotFound

	def missingKernPairs(self, font, firstMasterID, secondMasterID, firstKerning, secondKerning, enabledKinds, stats):
		"""
		Yields (kind, left, right, leftName, rightName, missingIn) for each kern pair that exists in only one of the two masters.
		kind: "group2group", "group2glyph", "glyph2group" or "glyph2glyph", limited to those in enabledKinds.
		left, right: the keys as in the kerning dictionary (glyph IDs or @MMK_ group keys).
		leftName, rightName: glyph names or @MMK_ group keys, as kerningForPair() and setKerningForPair() take them.
		missingIn: "first" or "second", or "both" if kerningForPair() finds the pair in neither master (e.g., RTL pairs).
		Pairs with stale glyph IDs are counted in stats["skipped"].
		"""
		for L in set(list(firstKerning.keys()) + list(secondKerning.keys())):
			LisGroup = L[0] == "@"
			RKeys = []
			for kerning in (firstKerning, secondKerning):
				if L in kerning.keys():
					RKeys.extend(list(kerning[L].keys()))
			for R in set(RKeys):
				RisGroup = R[0] == "@"

				# Guard against stale glyph IDs
				if LisGroup:
					Lname = L
				else:
					Lglyph = font.glyphForId_(L)
					if Lglyph is None:
						stats["skipped"] += 1
						continue
					Lname = Lglyph.name

				if RisGroup:
					Rname = R
				else:
					Rglyph = font.glyphForId_(R)
					if Rglyph is None:
						stats["skipped"] += 1
						continue
					Rname = Rglyph.name

				firstIsMissing = self.kerningIsMissing(font.kerningForPair(firstMasterID, Lname, Rname))
				secondIsMissing = self.kerningIsMissing(font.kerningForPair(secondMasterID, Lname, Rname))
				if not (firstIsMissing or secondIsMissing):
					continue

				if LisGroup and RisGroup:
					kind = "group2group"
				elif LisGroup:
					kind = "group2glyph"
				elif RisGroup:
					kind = "glyph2group"
				else:
					kind = "glyph2glyph"
				if kind not in enabledKinds:
					continue

				if firstIsMissing and secondIsMissing:
					missingIn = "both"
				elif secondIsMissing:
					missingIn = "second"
				else:
					missingIn = "first"
				yield kind, L, R, Lname, Rname, missingIn

	def shortKernName(self, name):
		return name.replace("@MMK_L_", "@").replace("@MMK_R_", "@")

	def SyncKernPairs(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			print(f"Sync Kern Pairs Report for {reportFontName(thisFont)}")
			print()

			firstMaster, secondMaster = self.selectedMasters(thisFont)
			masters = {"first": firstMaster, "second": secondMaster}
			kerningOfMaster = {}
			for key, master in masters.items():
				# a master without any kerning has no kerning dictionary at all:
				kerningOfMaster[key] = thisFont.kerning[master.id] or {}
				if not kerningOfMaster[key]:
					print(f"⚠️ Master ‘{master.name}’ has no kerning at all.")

			stats = {"skipped": 0}
			pairsToAdd = []
			for kind, L, R, Lname, Rname, missingIn in self.missingKernPairs(
				thisFont, firstMaster.id, secondMaster.id, kerningOfMaster["first"], kerningOfMaster["second"], self.enabledKinds(), stats
			):
				if missingIn == "both":
					continue  # kerningForPair() finds it in neither master (e.g., RTL), so we cannot tell and leave it alone
				pairsToAdd.append((masters[missingIn], Lname, Rname))

			if stats["skipped"]:
				print(f"⚠️ Skipped {stats['skipped']} pairs with stale or missing glyph IDs.")

			addedCounts = {firstMaster.id: 0, secondMaster.id: 0}
			for master, Lname, Rname in pairsToAdd:
				thisFont.setKerningForPair(master.id, Lname, Rname, 0.0)
				addedCounts[master.id] += 1
				print(f"\t➕ {master.name}: {self.shortKernName(Lname)}-{self.shortKernName(Rname)} = 0")

			addedCount = len(pairsToAdd)
			if addedCount:
				message = f"Added {addedCount} zero kern{'' if addedCount == 1 else 's'}: {addedCounts[firstMaster.id]} in ‘{firstMaster.name}’, {addedCounts[secondMaster.id]} in ‘{secondMaster.name}’."
			else:
				message = f"Kern pair structure of ‘{firstMaster.name}’ and ‘{secondMaster.name}’ is in sync already, given your selection."
			print(f"\n✅ {message}")
			Glyphs.showNotification("Sync Kern Pairs", message)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Sync Kern Pairs Error: {e}")
			import traceback
			print(traceback.format_exc())

	def CompareKerningBetweenMastersMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				reportName = reportFontName(thisFont)
				print(f"Compare Kerning Between Masters Report for {reportName}")
				print()

				group2groupLayersMissingFirst = []
				group2glyphLayersMissingFirst = []
				glyph2groupLayersMissingFirst = []
				glyph2glyphLayersMissingFirst = []
				group2groupLayersMissingSecond = []
				group2glyphLayersMissingSecond = []
				glyph2groupLayersMissingSecond = []
				glyph2glyphLayersMissingSecond = []

				firstMaster, secondMaster = self.selectedMasters(thisFont)
				firstMasterID = firstMaster.id
				secondMasterID = secondMaster.id
				# a master without any kerning has no kerning dictionary at all (None); then every pair of the other master is missing here:
				firstKerning = thisFont.kerning[firstMasterID] or {}
				secondKerning = thisFont.kerning[secondMasterID] or {}
				for master, kerning in ((firstMaster, firstKerning), (secondMaster, secondKerning)):
					if not kerning:
						print(f"⚠️ Master ‘{master.name}’ has no kerning at all.")

				spaceGlyph = thisFont.glyphs["space"]
				if spaceGlyph is None:
					print("⚠️ No 'space' glyph in font, cannot build tab output.")
					Message(title="Missing Space Glyph", message="The font has no 'space' glyph. The script needs it to build the comparison tab.", OKButton=None)
					return

				missingKernCount = 0
				skippedCount = 0
				targetLists = {
					("group2group", "first"): group2groupLayersMissingFirst,
					("group2group", "second"): group2groupLayersMissingSecond,
					("group2glyph", "first"): group2glyphLayersMissingFirst,
					("group2glyph", "second"): group2glyphLayersMissingSecond,
					("glyph2group", "first"): glyph2groupLayersMissingFirst,
					("glyph2group", "second"): glyph2groupLayersMissingSecond,
					("glyph2glyph", "first"): glyph2glyphLayersMissingFirst,
					("glyph2glyph", "second"): glyph2glyphLayersMissingSecond,
				}
				stats = {"skipped": 0}

				for kind, L, R, Lname, Rname, missingIn in self.missingKernPairs(thisFont, firstMasterID, secondMasterID, firstKerning, secondKerning, self.enabledKinds(), stats):
					if missingIn == "both":
						missingIn = "second"  # as before: if the pair is found in neither master, it is listed as missing in the second
					targetList = targetLists[(kind, missingIn)]

					glyphNameOnLSide = self.glyphNameForKerningName(L, thisFont, isLeft=True)
					glyphNameOnRSide = self.glyphNameForKerningName(R, thisFont, isLeft=False)
					if glyphNameOnLSide is None or glyphNameOnRSide is None:
						skippedCount += 1
						continue

					glyphOnLSide = thisFont.glyphs[glyphNameOnLSide]
					glyphOnRSide = thisFont.glyphs[glyphNameOnRSide]
					if glyphOnLSide is None or glyphOnRSide is None:
						skippedCount += 1
						continue

					missingKernCount += 1
					targetList.append(glyphOnLSide.layers[firstMaster.id])
					targetList.append(glyphOnRSide.layers[firstMaster.id])
					targetList.append(spaceGlyph.layers[firstMaster.id])
					targetList.append(glyphOnLSide.layers[secondMaster.id])
					targetList.append(glyphOnRSide.layers[secondMaster.id])
					targetList.append(newLineControlLayer())

				skippedCount += stats["skipped"]

				if skippedCount:
					print(f"⚠️ Skipped {skippedCount} pairs with stale or missing glyph IDs.")

				if not missingKernCount:
					Message(
						title="No kern pair missing",
						message=f"Nothing missing in the kerning structure between masters '{firstMaster.name}' and '{secondMaster.name}', given your selection.",
						OKButton=None,
					)
				else:
					if self.pref("reuseTab") and thisFont.currentTab:
						tab = thisFont.currentTab
						tab.text = ""
					else:
						tab = thisFont.newTab()
					tab.graphicView().setDoSpacing_(0)
					tab.graphicView().setDoKerning_(1)
					tab.updateKerningButton()

					def addNewline():
						tab.layers.append(newLineControlLayer())

					def addToTab(text, masterID=firstMasterID):
						for char in text:
							glyph = thisFont.glyphForCharacter_(ord(char))
							if glyph:
								tab.layers.append(glyph.layers[masterID])
						addNewline()

					if group2groupLayersMissingFirst:
						addToTab(f"Group-group missing in {firstMaster.name}:")
						tab.layers = list(tab.layers) + group2groupLayersMissingFirst
						addNewline()
					if group2groupLayersMissingSecond:
						addToTab(f"Group-group missing in {secondMaster.name}:", masterID=secondMasterID)
						tab.layers = list(tab.layers) + group2groupLayersMissingSecond
						addNewline()

					if group2glyphLayersMissingFirst:
						addToTab(f"Group-glyph missing in {firstMaster.name}:")
						tab.layers = list(tab.layers) + group2glyphLayersMissingFirst
						addNewline()
					if group2glyphLayersMissingSecond:
						addToTab(f"Group-glyph missing in {secondMaster.name}:", masterID=secondMasterID)
						tab.layers = list(tab.layers) + group2glyphLayersMissingSecond
						addNewline()

					if glyph2groupLayersMissingFirst:
						addToTab(f"Glyph-group missing in {firstMaster.name}:")
						tab.layers = list(tab.layers) + glyph2groupLayersMissingFirst
						addNewline()
					if glyph2groupLayersMissingSecond:
						addToTab(f"Glyph-group missing in {secondMaster.name}:", masterID=secondMasterID)
						tab.layers = list(tab.layers) + glyph2groupLayersMissingSecond
						addNewline()

					if glyph2glyphLayersMissingFirst:
						addToTab(f"Glyph-glyph missing in {firstMaster.name}:")
						tab.layers = list(tab.layers) + glyph2glyphLayersMissingFirst
						addNewline()
					if glyph2glyphLayersMissingSecond:
						addToTab(f"Glyph-glyph missing in {secondMaster.name}:", masterID=secondMasterID)
						tab.layers = list(tab.layers) + glyph2glyphLayersMissingSecond
						addNewline()

					print(f"\nDone. Found {missingKernCount} cases of missing kern pairs.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Compare Kerning Between Masters Error: {e}")
			import traceback
			print(traceback.format_exc())


CompareKerningBetweenMasters()

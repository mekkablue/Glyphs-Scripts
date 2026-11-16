# MenuTitle: Compare Kerning Between Masters
__doc__ = """
Report differences in kerning structures between two masters.
"""

import vanilla
from mekkablue import mekkaObject, newLineControlLayer, reportFontName, UpdateButton
from GlyphsApp import Glyphs, Message
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
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.descriptionText = vanilla.TextBox("auto", "Compare kerning between two masters in frontmost font:", sizeStyle="small", selectable=True)

		self.w.firstMasterText = vanilla.TextBox("auto", "1st Master:", sizeStyle="small", selectable=True)
		self.w.firstMaster = vanilla.PopUpButton("auto", self.menuItemsForFrontMostFont(), sizeStyle="small", callback=self.SavePreferences)

		self.w.secondMasterText = vanilla.TextBox("auto", "2nd Master:", sizeStyle="small", selectable=True)
		self.w.secondMaster = vanilla.PopUpButton("auto", self.menuItemsForFrontMostFont(), sizeStyle="small", callback=self.SavePreferences)
		self.w.updateButton = UpdateButton("auto", callback=self.updateUI)

		self.w.kernTypeText = vanilla.TextBox("auto", "Types of kerning to compare:", sizeStyle="small", selectable=True)

		self.w.group2group = vanilla.CheckBox("auto", "@group ↔︎ @group", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.group2glyph = vanilla.CheckBox("auto", "@group ↔︎ glyph", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.glyph2group = vanilla.CheckBox("auto", "glyph ↔︎ @group", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.glyph2glyph = vanilla.CheckBox("auto", "glyph ↔︎ glyph", value=True, callback=self.SavePreferences, sizeStyle="small")

		self.w.reuseTab = vanilla.CheckBox("auto", "Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle="small")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Compare", callback=self.CompareKerningBetweenMastersMain)
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
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-row-[firstMaster]-row-[secondMaster]-section-[kernTypeText]-row-[group2group]-checkRow-[glyph2group]-section-[reuseTab]-inset-[runButton]-inset-|",
				"V:[kernTypeText]-row-[group2glyph]-checkRow-[glyph2glyph]",
				{"view1": self.w.firstMasterText, "attribute1": "centerY", "view2": self.w.firstMaster, "attribute2": "centerY"},
				{"view1": self.w.secondMasterText, "attribute1": "centerY", "view2": self.w.secondMaster, "attribute2": "centerY"},
				{"view1": self.w.updateButton, "attribute1": "centerY", "view2": self.w.secondMaster, "attribute2": "centerY"},
				# labels and the checkbox columns share one width each:
				{"view1": self.w.firstMasterText, "attribute1": "width", "view2": self.w.secondMasterText, "attribute2": "width"},
				{"view1": self.w.glyph2group, "attribute1": "width", "view2": self.w.group2group, "attribute2": "width"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5, "section": 12},
		)

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
		if not font or self.pref("firstMaster") == self.pref("secondMaster"):
			self.w.runButton.enable(False)
		else:
			self.w.runButton.enable(True)

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
		if not font or self.pref("firstMaster") == self.pref("secondMaster"):
			self.w.runButton.enable(False)
		else:
			self.w.runButton.enable(True)

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

				group2group = bool(self.pref("group2group"))
				group2glyph = bool(self.pref("group2glyph"))
				glyph2group = bool(self.pref("glyph2group"))
				glyph2glyph = bool(self.pref("glyph2glyph"))
				firstMaster = self.prefInt("firstMaster")
				secondMaster = self.prefInt("secondMaster")

				group2groupLayersMissingFirst = []
				group2glyphLayersMissingFirst = []
				glyph2groupLayersMissingFirst = []
				glyph2glyphLayersMissingFirst = []
				group2groupLayersMissingSecond = []
				group2glyphLayersMissingSecond = []
				glyph2groupLayersMissingSecond = []
				glyph2glyphLayersMissingSecond = []

				firstMasterChoice = self.w.firstMaster.getItems()[firstMaster]
				firstMasterID = firstMasterChoice.split("(ID: ")[1][:-1]
				firstMaster = thisFont.masters[firstMasterID]
				firstKerning = thisFont.kerning[firstMaster.id]

				secondMasterChoice = self.w.secondMaster.getItems()[secondMaster]
				secondMasterID = secondMasterChoice.split("(ID: ")[1][:-1]
				secondMaster = thisFont.masters[secondMasterID]
				secondKerning = thisFont.kerning[secondMaster.id]

				spaceGlyph = thisFont.glyphs["space"]
				if spaceGlyph is None:
					print("⚠️ No 'space' glyph in font, cannot build tab output.")
					Message(title="Missing Space Glyph", message="The font has no 'space' glyph. The script needs it to build the comparison tab.", OKButton=None)
					return

				missingKernCount = 0
				skippedCount = 0

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
							Lglyph = thisFont.glyphForId_(L)
							if Lglyph is None:
								skippedCount += 1
								continue
							Lname = Lglyph.name

						if RisGroup:
							Rname = R
						else:
							Rglyph = thisFont.glyphForId_(R)
							if Rglyph is None:
								skippedCount += 1
								continue
							Rname = Rglyph.name

						kerningInFirstMaster = thisFont.kerningForPair(firstMasterID, Lname, Rname)
						kerningInSecondMaster = thisFont.kerningForPair(secondMasterID, Lname, Rname)
						if kerningInFirstMaster is None or kerningInSecondMaster is None:
							targetList = None
							if LisGroup and RisGroup and group2group:
								if kerningInFirstMaster is None:
									targetList = group2groupLayersMissingFirst
								if kerningInSecondMaster is None:
									targetList = group2groupLayersMissingSecond
							if LisGroup and not RisGroup and group2glyph:
								if kerningInFirstMaster is None:
									targetList = group2glyphLayersMissingFirst
								if kerningInSecondMaster is None:
									targetList = group2glyphLayersMissingSecond
							if not LisGroup and not RisGroup and glyph2glyph:
								if kerningInFirstMaster is None:
									targetList = glyph2glyphLayersMissingFirst
								if kerningInSecondMaster is None:
									targetList = glyph2glyphLayersMissingSecond
							if not LisGroup and RisGroup and glyph2group:
								if kerningInFirstMaster is None:
									targetList = glyph2groupLayersMissingFirst
								if kerningInSecondMaster is None:
									targetList = glyph2groupLayersMissingSecond

							if targetList is not None:
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

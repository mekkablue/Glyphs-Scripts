# MenuTitle: Group Lister
__doc__ = """
Lists kerning groups and their members in a new tab: first all left groups, then all right groups, one line per group. Optionally limited to selected glyphs, a category or a case. With selected glyphs, it can list all pairings of their groups instead.
"""

import math
import vanilla
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityDefaultLow,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSTextAlignmentRight,
)
from GlyphsApp import Glyphs, GSControlLayer, Message
from mekkablue import mekkaObject, caseDict, fontFileName, UpdateButton

scopeChoices = (
	"Currently selected glyphs",
	"All glyphs in frontmost font",
	"All open fonts",
)
caseChoices = (
	("Uppercase", "Uppercase"),
	("Lowercase", "Lowercase"),
	("Small caps", "Smallcaps"),
	("Minor", "Minor"),
	("Without case", "NoCase"),
)  # (title in the popup, key in caseDict)
sides = (
	("L", "leftKerningGroup", "leftGroups"),
	("R", "rightKerningGroup", "rightGroups"),
)  # (label in the tab, glyph attribute, name of the checkbox)
fallbackEditViewWidth = 40000


class GroupLister(mekkaObject):
	prefDict = {
		"leftGroups": True,
		"rightGroups": True,
		"includeGroupless": False,
		"scope": 1,
		"onlyCategory": False,
		"onlyCase": False,
		"caseChoice": 0,
		"listPairings": False,
		"reuseTab": True,
	}
	fittedEditViewWidth = None  # rough guess from the last listing

	def __init__(self):
		windowWidth = 440
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Group Lister",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "List kerning groups and their members in a new tab.", sizeStyle="small", selectable=True)

		self.w.leftGroups = vanilla.CheckBox("auto", "Left groups", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.leftGroups.setToolTip("List the left kerning groups of the glyphs (the left side of each glyph), one line per group, as ‘L groupname: /A/Aacute/Agrave’.")
		self.w.rightGroups = vanilla.CheckBox("auto", "Right groups", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.rightGroups.setToolTip("List the right kerning groups of the glyphs (the right side of each glyph), one line per group, as ‘R groupname: /A/Aacute/Agrave’. Listed after the left groups, with an empty line in between.")
		self.w.includeGroupless = vanilla.CheckBox("auto", "Also list groupless glyphs", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.includeGroupless.setToolTip("Add a line with the glyphs that have no group on that side, as ‘L (no group): /a/b/c’.")

		tooltipText = "Which glyphs to list the groups of: the glyphs currently selected in the frontmost font (with all members of their groups), all glyphs of the frontmost font, or all glyphs of all open fonts (one tab per font)."
		self.w.textScope = vanilla.TextBox("auto", "Scope", sizeStyle="small", selectable=True)
		self.w.scope = vanilla.PopUpButton("auto", scopeChoices, callback=self.scopeChanged, sizeStyle="small")
		self.w.textScope.setToolTip(tooltipText)
		self.w.scope.setToolTip(tooltipText)

		self.w.onlyCategory = vanilla.CheckBox("auto", "Only glyphs of category", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.onlyCategory.setToolTip("Only consider glyphs of the category chosen on the right, e.g., ‘Letter’.")
		self.w.categoryChoice = vanilla.PopUpButton("auto", [], callback=self.SavePreferences, sizeStyle="small")
		self.w.categoryChoice.setToolTip("All glyph categories found in the fonts of the scope.")
		self.w.updateCategoriesButton = UpdateButton("auto", callback=self.updateCategoriesAction)
		self.w.updateCategoriesButton.setToolTip("Recalculates the categories in the popup for the current scope.")

		self.w.onlyCase = vanilla.CheckBox("auto", "Only glyphs of case", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.onlyCase.setToolTip("Only consider glyphs of the case chosen on the right.")
		self.w.caseChoice = vanilla.PopUpButton("auto", [title for title, key in caseChoices], callback=self.SavePreferences, sizeStyle="small")
		self.w.caseChoice.setToolTip("The case of the glyphs to consider.")

		self.w.listPairings = vanilla.CheckBox("auto", "List all pairings for the selected groups instead", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.listPairings.setToolTip(
			"Only with ‘Currently selected glyphs’. Instead of the groups, lists all pairings of the right group of each selected glyph with the left group of the next selected glyph (select ‘Ta’ to see all T-group members next to all a-group members). With fewer than two glyphs selected, the two glyphs around the text cursor in the current tab are used, if there are any; with a single selected glyph and no such cursor, its right group is paired with its own left group."
		)

		self.w.reuseTab = vanilla.CheckBox("auto", "Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.reuseTab.setToolTip("If enabled, will not open a new tab, but reuse the current Edit tab of each font. Will open an Edit tab if none is open.")
		tooltipText = "Edit view width (‘Width of editor’ in the Preferences) decides where lines of the Edit view wrap. Toggle switches between a rough guess that fits the longest line of the last listing (40000 if there was none yet) and the width you had before."
		self.w.textEditViewWidth = vanilla.TextBox("auto", "Edit view width", sizeStyle="small", selectable=True)
		self.w.toggleEditViewWidth = vanilla.Button("auto", "Toggle", callback=self.toggleEditViewWidth, sizeStyle="small")
		self.w.textEditViewWidth.setToolTip(tooltipText)
		self.w.toggleEditViewWidth.setToolTip(tooltipText)

		# Status line, with the prediction:
		self.w.statusText = vanilla.TextBox("auto", "🔮 Will list – groups.", sizeStyle="small")
		self.w.statusText.setToolTip("Before you run: how many groups will be listed with the current settings. Afterwards: how many were listed.")
		self.w.statusText.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		self.w.listButton = vanilla.Button("auto", "List", callback=self.GroupListerMain)
		self.w.listButton.setToolTip("Opens a tab with the groups and their members. If the button is greyed out, check left groups or right groups.")
		self.w.setDefaultButton(self.w.listButton)

		# checkboxes and square buttons stretch vertically by default; with everything
		# hugging, the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# the checkboxes in front of a popup hug their text, the popups stretch;
		# the scope label is right-aligned and as wide as the checkboxes, so all popups start at one x-position:
		for checkBox in (self.w.onlyCategory, self.w.onlyCase):
			nsCheckBox = checkBox.getNSButton()
			nsCheckBox.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsCheckBox.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)  # keep the title on one line
		self.w.updateCategoriesButton.getNSButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		for popup in (self.w.scope, self.w.categoryChoice, self.w.caseChoice):
			popup.getNSPopUpButton().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)
		nsLabel = self.w.textScope.getNSTextField()
		nsLabel.setAlignment_(NSTextAlignmentRight)
		nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		def equalWidth(viewName, referenceName):
			return {"view1": getattr(self.w, viewName), "attribute1": "width", "view2": getattr(self.w, referenceName), "attribute2": "width"}

		def centerY(viewName, referenceName):
			return {"view1": getattr(self.w, viewName), "attribute1": "centerY", "view2": getattr(self.w, referenceName), "attribute2": "centerY"}

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[leftGroups]-gap-[rightGroups]-(>=inset)-|",
				"H:|-inset-[includeGroupless]-(>=inset)-|",
				"H:|-inset-[textScope]-popupGap-[scope]-inset-|",
				"H:|-inset-[onlyCategory]-popupGap-[categoryChoice]-gap-[updateCategoriesButton]-inset-|",
				"H:|-inset-[onlyCase]-popupGap-[caseChoice]-inset-|",
				"H:|-inset-[listPairings]-(>=inset)-|",
				"H:|-inset-[reuseTab]-(>=gap)-[textEditViewWidth]-gap-[toggleEditViewWidth(>=70)]-inset-|",
				"H:|-inset-[statusText]-(>=gap)-[listButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-row-[leftGroups]-checkRow-[includeGroupless]-section-[scope]-stackRow-[onlyCategory]-stackRow-[onlyCase]-stackRow-[listPairings]-section-[toggleEditViewWidth]-section-[listButton]-inset-|",
				centerY("rightGroups", "leftGroups"),
				centerY("textScope", "scope"),
				centerY("categoryChoice", "onlyCategory"),
				centerY("updateCategoriesButton", "onlyCategory"),
				centerY("caseChoice", "onlyCase"),
				centerY("reuseTab", "toggleEditViewWidth"),
				centerY("textEditViewWidth", "toggleEditViewWidth"),
				centerY("statusText", "listButton"),
				equalWidth("onlyCase", "onlyCategory"),
				equalWidth("textScope", "onlyCategory"),
			],
			metrics={"inset": inset, "gap": 8, "popupGap": 16, "row": 8, "checkRow": 5, "stackRow": 8, "section": 12},
		)

		# Load Settings:
		self.LoadPreferences()
		self.updateCategories()  # needs the scope, so only after loading the preferences
		self.updateUI()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	# --- preferences and UI ---

	def SavePreferences(self, sender=None):
		# the categories differ from font to font, so the popup is saved by title, not by position:
		categories = self.w.categoryChoice.getItems()
		if categories:
			self.setPref("categoryChoice", categories[self.w.categoryChoice.get()])
		super().SavePreferences(sender)

	def scopeChanged(self, sender=None):
		self.updateCategories()
		self.SavePreferences(sender)

	def updateCategoriesAction(self, sender=None):
		self.updateCategories()
		self.SavePreferences(sender)

	def updateCategories(self):
		"""Fills the category popup with the categories of all fonts in the scope, and keeps the choice if possible."""
		categories = sorted({thisGlyph.category for thisFont in self.fontsInScope() for thisGlyph in thisFont.glyphs if thisGlyph.category})
		self.w.categoryChoice.setItems(categories)
		savedCategory = Glyphs.defaults[self.domain("categoryChoice")]
		if savedCategory in categories:
			self.w.categoryChoice.set(categories.index(savedCategory))

	def pairingMode(self):
		return self.prefInt("scope") == 0 and self.prefBool("listPairings")

	def updateUI(self, sender=None):
		selectedScope = self.prefInt("scope") == 0
		pairingMode = self.pairingMode()
		self.w.listPairings.enable(selectedScope)

		# the groups and filters do not matter for pairings:
		for name in ("leftGroups", "rightGroups", "includeGroupless", "onlyCategory", "onlyCase"):
			getattr(self.w, name).enable(not pairingMode)
		self.w.categoryChoice.enable(not pairingMode and self.prefBool("onlyCategory"))
		self.w.updateCategoriesButton.enable(not pairingMode and self.prefBool("onlyCategory"))
		self.w.caseChoice.enable(not pairingMode and self.prefBool("onlyCase"))

		self.w.listButton.enable(pairingMode or self.prefBool("leftGroups") or self.prefBool("rightGroups"))
		self.setStatus(self.predictionText())

	def setStatus(self, text):
		"""Sets the status line and redraws it right away, so it shows while the script is busy."""
		self.w.statusText.set(text)
		self.w.statusText.getNSTextField().display()

	# --- what to list ---

	def fontsInScope(self):
		if self.prefInt("scope") == 2:
			return list(Glyphs.fonts)
		return [Glyphs.font] if Glyphs.font else []

	def selectedGlyphs(self, thisFont):
		"""The glyphs of the selected layers, each only once, in the order of the selection."""
		glyphs = []
		names = set()
		for thisLayer in thisFont.selectedLayers:
			thisGlyph = thisLayer.parent
			if thisGlyph is not None and thisGlyph.name not in names:
				names.add(thisGlyph.name)
				glyphs.append(thisGlyph)
		return glyphs

	def glyphFilter(self):
		"""Returns a function that tells if a glyph passes the category and case settings."""
		category = None
		if self.prefBool("onlyCategory"):
			categories = self.w.categoryChoice.getItems()
			category = categories[self.w.categoryChoice.get()] if categories else None
		case = None
		if self.prefBool("onlyCase"):
			case = caseDict[caseChoices[self.prefInt("caseChoice")][1]]

		def passes(thisGlyph):
			if category is not None and thisGlyph.category != category:
				return False
			if case is not None and thisGlyph.case != case:
				return False
			return True

		return passes

	def groupsOfFont(self, thisFont):
		"""
		Returns a dict for each side ("L", "R") with
		"groups": [(groupName, [member glyph names])] in the order they show up,
		"groupless": [glyph names],
		and under "lineWidths" a rough width in font units for each line that would be listed.
		The scope decides which groups are listed; the members are all glyphs of the font that pass the filters.
		"""
		passes = self.glyphFilter()
		masterID = thisFont.selectedFontMaster.id
		allGlyphs = [thisGlyph for thisGlyph in thisFont.glyphs if passes(thisGlyph)]
		if self.prefInt("scope") == 0:
			baseGlyphs = [thisGlyph for thisGlyph in self.selectedGlyphs(thisFont) if passes(thisGlyph)]
		else:
			baseGlyphs = allGlyphs
		widths = {thisGlyph.name: thisGlyph.layers[masterID].width for thisGlyph in allGlyphs}

		result = {}
		for label, attribute, checkBoxName in sides:
			members = {}
			for thisGlyph in allGlyphs:
				groupName = getattr(thisGlyph, attribute)
				if groupName:
					members.setdefault(groupName, []).append(thisGlyph.name)

			groups = []
			names = set()
			for thisGlyph in baseGlyphs:
				groupName = getattr(thisGlyph, attribute)
				if groupName and groupName not in names:
					names.add(groupName)
					groups.append((groupName, members[groupName]))

			groupless = [thisGlyph.name for thisGlyph in baseGlyphs if not getattr(thisGlyph, attribute)]
			result[label] = {"groups": groups, "groupless": groupless}

		result["widths"] = widths
		return result

	def textForFont(self, thisFont):
		"""Returns the text for the tab, the number of left and right groups listed, and the rough width of the longest line."""
		data = self.groupsOfFont(thisFont)
		widths = data["widths"]
		unitsPerEm = thisFont.upm
		blocks = []
		counts = {}
		longestLine = 0
		for label, attribute, checkBoxName in sides:
			counts[label] = 0
			if not self.prefBool(checkBoxName):
				continue
			lines = []
			entries = list(data[label]["groups"])
			counts[label] = len(entries)
			if self.prefBool("includeGroupless") and data[label]["groupless"]:
				entries.append(("(no group)", data[label]["groupless"]))
			for groupName, names in entries:
				prefix = f"{label} {groupName}: "
				lines.append(prefix + "".join(f"/{name}" for name in names))
				# the prefix is set in the font, too; assume about half an em per character:
				longestLine = max(longestLine, 0.5 * unitsPerEm * len(prefix) + sum(widths.get(name, unitsPerEm) for name in names))
			if lines:
				blocks.append("\n".join(lines))
		return "\n\n".join(blocks), counts["L"], counts["R"], longestLine

	def glyphsAroundCursor(self, thisFont):
		"""The two glyphs left and right of the text cursor in the current tab, if there is no text selection."""
		thisTab = thisFont.currentTab
		if thisTab and thisTab.textRange == 0:
			cursorPosition = thisTab.layersCursor
			if 0 < cursorPosition < len(thisTab.layers):
				layers = (thisTab.layers[cursorPosition - 1], thisTab.layers[cursorPosition])
				if not any(isinstance(thisLayer, GSControlLayer) for thisLayer in layers):
					return [thisLayer.parent for thisLayer in layers]
		return []

	def pairingsOfFont(self, thisFont):
		"""Returns the text with all pairings, the number of pairings, and the rough width of the longest line."""
		glyphs = [thisLayer.parent for thisLayer in thisFont.selectedLayers if thisLayer.parent is not None]
		if len(glyphs) < 2:
			glyphs = self.glyphsAroundCursor(thisFont) or glyphs
		if len(glyphs) == 1:
			glyphs = [glyphs[0], glyphs[0]]
		if len(glyphs) < 2:
			return "", 0, 0

		masterID = thisFont.selectedFontMaster.id
		spaceWidth = 0.25 * thisFont.upm
		blocks = []
		pairCount = 0
		longestLine = 0
		for firstGlyph, secondGlyph in zip(glyphs, glyphs[1:]):
			# glyphs without a group only stand for themselves:
			firstGroup = firstGlyph.rightKerningGroup
			secondGroup = secondGlyph.leftKerningGroup
			firstGlyphs = [g for g in thisFont.glyphs if g.rightKerningGroup == firstGroup] if firstGroup else [firstGlyph]
			secondGlyphs = [g for g in thisFont.glyphs if g.leftKerningGroup == secondGroup] if secondGroup else [secondGlyph]
			lines = []
			for leftGlyph in firstGlyphs:
				lines.append("".join(f"/{leftGlyph.name}/{rightGlyph.name}/space" for rightGlyph in secondGlyphs))
				pairCount += len(secondGlyphs)
				lineWidth = sum(leftGlyph.layers[masterID].width + rightGlyph.layers[masterID].width + spaceWidth for rightGlyph in secondGlyphs)
				longestLine = max(longestLine, lineWidth)
			blocks.append("\n".join(lines))
		return "\n\n".join(blocks), pairCount, longestLine

	def predictionText(self):
		fonts = self.fontsInScope()
		if self.pairingMode():
			pairCount = sum(self.pairingsOfFont(thisFont)[1] for thisFont in fonts)
			return f"🔮 Will list {pairCount:,} pairing{'' if pairCount == 1 else 's'}."
		counts = {"L": 0, "R": 0}
		for thisFont in fonts:
			text, leftCount, rightCount, longestLine = self.textForFont(thisFont)
			counts["L"] += leftCount
			counts["R"] += rightCount
		return self.groupCountText("🔮 Will list", counts["L"], counts["R"])

	def groupCountText(self, start, leftCount, rightCount):
		parts = []
		if self.prefBool("leftGroups"):
			parts.append(f"{leftCount:,} left")
		if self.prefBool("rightGroups"):
			parts.append(f"{rightCount:,} right")
		if not parts:
			return f"{start} – groups."
		total = (leftCount if self.prefBool("leftGroups") else 0) + (rightCount if self.prefBool("rightGroups") else 0)
		return f"{start} {' and '.join(parts)} group{'' if total == 1 else 's'}."

	# --- actions ---

	def GroupListerMain(self, sender=None):
		try:
			# update settings to the latest user input:
			self.SavePreferences()

			fonts = self.fontsInScope()
			if not fonts:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			Glyphs.clearLog()
			print("Group Lister Report\n")
			self.setStatus("🛠️ Listing groups…")

			pairingMode = self.pairingMode()
			totals = {"L": 0, "R": 0, "pairs": 0}
			longestLine = 0
			listedFontCount = 0
			for thisFont in fonts:
				if pairingMode:
					text, pairCount, fontLongestLine = self.pairingsOfFont(thisFont)
					totals["pairs"] += pairCount
				else:
					text, leftCount, rightCount, fontLongestLine = self.textForFont(thisFont)
					totals["L"] += leftCount
					totals["R"] += rightCount
				if not text:
					print(f"⚠️ {fontFileName(thisFont)}: nothing to list.")
					continue

				# one tab per font:
				if self.prefBool("reuseTab") and thisFont.currentTab:
					thisFont.currentTab.text = text
				else:
					thisFont.newTab(text)
				listedFontCount += 1
				longestLine = max(longestLine, fontLongestLine)
				print(f"✅ {fontFileName(thisFont)}: listed in a tab.")

			if not listedFontCount:
				self.setStatus("⚠️ Nothing to list.")
				return

			# a rough guess for the Edit view width that fits the longest line:
			margin = 1.1 * longestLine + max(thisFont.upm for thisFont in fonts)
			self.fittedEditViewWidth = int(math.ceil(margin / 100.0) * 100)

			if pairingMode:
				message = f"Listed {totals['pairs']:,} pairing{'' if totals['pairs'] == 1 else 's'}."
			else:
				message = self.groupCountText("Listed", totals["L"], totals["R"]).rstrip(".") + "."
			self.setStatus(f"✅ {message}")
			print(f"\n✅ {message}")
			Glyphs.showNotification("Group Lister", message)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			self.setStatus("❌ Error. Details in Macro Window.")
			print(f"Group Lister Error: {e}")
			import traceback
			print(traceback.format_exc())

	def toggleEditViewWidth(self, sender=None):
		"""Switches between a width that fits the lines and the width the user had before."""
		currentWidth = Glyphs.editViewWidth
		originalWidth = self.prefInt("originalEditViewWidth")  # 0 as long as we have not changed it
		if originalWidth and currentWidth != originalWidth:
			Glyphs.editViewWidth = originalWidth
			self.setPref("originalEditViewWidth", 0)
			message = f"✅ Edit view width back to {originalWidth:,}."
		else:
			fittedWidth = self.fittedEditViewWidth or fallbackEditViewWidth
			self.setPref("originalEditViewWidth", currentWidth)
			Glyphs.editViewWidth = fittedWidth
			message = f"✅ Edit view width set to {fittedWidth:,} (was {currentWidth:,})."
		for thisFont in Glyphs.fonts:
			if thisFont.currentTab:
				thisFont.currentTab.reflow()
		self.setStatus(message)


GroupLister()

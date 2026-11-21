# MenuTitle: Find and Replace in Anchors
__doc__ = """
Replaces strings in anchor names, in selected glyphs, in all glyphs of the font, or in all open fonts. Processes all layers.
"""

import re

import vanilla
from AppKit import (
	NSColor,
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSTextAlignmentRight,
	NSWindowStyleMaskResizable,
)
from Foundation import NSSize
from GlyphsApp import Glyphs
from mekkablue import mekkaObject, UpdateButton, fontFileName

basicAnchors = (
	"top", "bottom", "center", "topleft", "topright", "ogonek",
	"_top", "_bottom", "_center", "_topleft", "_topright", "_ogonek",
)  # fmt: skip


class SearchAndReplaceInAnchors(mekkaObject):
	prefDict = {
		"searchFor": "",
		"replaceBy": "",
		"scope": 1,
		"openTab": 1,
		"caseSensitive": 0,
		"exactMatch": 0,
	}

	def __init__(self):
		windowWidth = 340
		windowWidthResize = 800  # user can widen the window by this value
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Find and Replace in Anchors",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.textSearch = vanilla.TextBox("auto", "Find")
		self.w.searchFor = vanilla.ComboBox("auto", list(basicAnchors), callback=self.SavePreferences)
		self.w.searchFor.getNSComboBox().setNumberOfVisibleItems_(20)
		tooltip = "The text to look for in anchor names. Pick one from the list or type a text."
		self.w.textSearch.setToolTip(tooltip)
		self.w.searchFor.setToolTip(tooltip)
		self.w.updateButton = UpdateButton("auto", callback=self.updateAnchorList)
		self.w.updateButton.setToolTip("Fill the list with all anchors found in the frontmost font.")

		self.w.textReplace = vanilla.TextBox("auto", "Replace")
		self.w.replaceBy = vanilla.EditText("auto", "", callback=self.SavePreferences)
		tooltip = "The text that replaces it. Leave empty to delete the search text."
		self.w.textReplace.setToolTip(tooltip)
		self.w.replaceBy.setToolTip(tooltip)
		self.w.replaceBy.getNSTextField().setPlaceholderString_("top")

		tooltip = "Which glyphs to process. All layers of these glyphs are processed."
		self.w.textScope = vanilla.TextBox("auto", "Apply to")
		self.w.scope = vanilla.PopUpButton(
			"auto",
			("selected glyphs", "all glyphs in current font", "⚠️ all glyphs in ⚠️ all open fonts"),
			callback=self.SavePreferences,
		)
		self.w.textScope.setToolTip(tooltip)
		self.w.scope.setToolTip(tooltip)

		self.w.caseSensitive = vanilla.CheckBox("auto", "Case-sensitive", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.caseSensitive.setToolTip("If on, ‘Top’ is not found when searching for ‘top’.")
		self.w.exactMatch = vanilla.CheckBox("auto", "Exact match", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.exactMatch.setToolTip(
			"If on, the search text must be the entire anchor name. Searching for ‘top’ will then find only ‘top’, "
			"but neither ‘_top’ nor ‘top_2’."
		)

		self.w.openTab = vanilla.CheckBox("auto", "Open tab", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.openTab.setToolTip("After replacing, open a tab with the glyphs whose anchors were renamed (one tab per font).")

		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small")
		self.w.status.getNSTextField().setTextColor_(NSColor.secondaryLabelColor())
		self.w.replaceButton = vanilla.Button("auto", "Replace", callback=self.SearchAndReplaceInAnchorsMain)
		self.w.replaceButton.setToolTip("Replace in the anchor names of the chosen glyphs, on all layers.")
		self.w.setDefaultButton(self.w.replaceButton)

		# right-align the labels, give them one width, and let them hug their text:
		labelNames = ("textSearch", "textReplace", "textScope")
		widestLabel = "textReplace"  # the label with the longest text
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)
		widthRules = [
			{"view1": getattr(self.w, labelName), "attribute1": "width", "view2": getattr(self.w, widestLabel), "attribute2": "width"}
			for labelName in labelNames if labelName != widestLabel
		]

		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[textSearch]-gap-[searchFor(>=60)]-gap-[updateButton]-inset-|",
				"H:|-inset-[textReplace]-gap-[replaceBy(>=60)]-inset-|",
				"H:|-inset-[textScope]-gap-[scope]-inset-|",
				"H:[caseSensitive]-gap-[exactMatch]-gap-[openTab]-(>=inset)-|",
				"H:|-inset-[status]-gap-[replaceButton(>=70)]-inset-|",
				"V:|-inset-[searchFor]-row-[replaceBy]-row-[scope]-row-[caseSensitive]-inset-[replaceButton]-inset-|",
				{"view1": self.w.textSearch, "attribute1": "centerY", "view2": self.w.searchFor, "attribute2": "centerY"},
				{"view1": self.w.updateButton, "attribute1": "centerY", "view2": self.w.searchFor, "attribute2": "centerY"},
				{"view1": self.w.textReplace, "attribute1": "centerY", "view2": self.w.replaceBy, "attribute2": "centerY"},
				{"view1": self.w.textScope, "attribute1": "centerY", "view2": self.w.scope, "attribute2": "centerY"},
				{"view1": self.w.caseSensitive, "attribute1": "leading", "view2": self.w.searchFor, "attribute2": "leading"},
				{"view1": self.w.openTab, "attribute1": "centerY", "view2": self.w.caseSensitive, "attribute2": "centerY"},
				{"view1": self.w.exactMatch, "attribute1": "centerY", "view2": self.w.caseSensitive, "attribute2": "centerY"},
				{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.replaceButton, "attribute2": "centerY"},
			] + widthRules,
			metrics={"inset": inset, "gap": 8, "row": 6},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

		# Resizable in width only. Vanilla's minSize/maxSize would count the title bar twice,
		# so set the limits on the NSWindow, in content sizes, with the height Auto Layout asks for:
		nsWindow = self.w.getNSWindow()
		nsWindow.setStyleMask_(nsWindow.styleMask() | NSWindowStyleMaskResizable)
		contentHeight = nsWindow.contentView().fittingSize().height
		nsWindow.setContentMinSize_(NSSize(windowWidth, contentHeight))
		nsWindow.setContentMaxSize_(NSSize(windowWidth + windowWidthResize, contentHeight))

	def setStatus(self, text):
		self.w.status.set(text)
		self.w.status.getNSTextField().displayIfNeeded()

	def updateUI(self, sender=None):
		self.setStatus(self.predictionText())

	def predictionText(self):
		searchString = self.w.searchFor.get()
		if not searchString or not Glyphs.font:
			return "🔮 Will change – anchors."
		count = 0
		for thisFont in self.fontsInScope():
			for thisGlyph in self.glyphsInScope(thisFont):
				for thisLayer in thisGlyph.layers:
					for thisAnchor in thisLayer.anchors:
						if self.newAnchorName(thisAnchor.name) != thisAnchor.name:
							count += 1
		return f"🔮 Will change {count} anchor{'' if count == 1 else 's'}."

	def updateAnchorList(self, sender=None):
		font = Glyphs.font
		if not font:
			self.setStatus("❌ No font open.")
			return
		anchorNames = set()
		for glyph in font.glyphs:
			for layer in glyph.layers:
				for anchor in layer.anchors:
					anchorNames.add(anchor.name)
		# basic anchors first, then the other anchors of the font, sorted:
		extraNames = sorted(anchorNames.difference(basicAnchors))
		foundBasicNames = [name for name in basicAnchors if name in anchorNames]
		self.w.searchFor.setItems(foundBasicNames + extraNames)
		self.setStatus(f"📃 Updated Find with {len(anchorNames)} anchor{'' if len(anchorNames) == 1 else 's'}.")

	def fontsInScope(self):
		if self.prefInt("scope") == 2:
			return Glyphs.fonts
		return (Glyphs.font, )

	def glyphsInScope(self, thisFont):
		if self.prefInt("scope") == 0:
			glyphNames = []
			for thisLayer in thisFont.selectedLayers:  # active layers of currently selected glyphs
				glyphName = thisLayer.parent.name
				if glyphName not in glyphNames:  # several layers of one glyph may be selected
					glyphNames.append(glyphName)
			return [thisFont.glyphs[glyphName] for glyphName in glyphNames]
		return list(thisFont.glyphs)

	def newAnchorName(self, oldAnchorName):
		searchString = self.w.searchFor.get()
		replaceString = self.w.replaceBy.get()
		caseSensitive = self.prefBool("caseSensitive")
		if self.prefBool("exactMatch"):
			if caseSensitive:
				isMatch = oldAnchorName == searchString
			else:
				isMatch = oldAnchorName.lower() == searchString.lower()
			return replaceString if isMatch else oldAnchorName
		if caseSensitive:
			return oldAnchorName.replace(searchString, replaceString)
		return re.sub(re.escape(searchString), lambda matchObject: replaceString, oldAnchorName, flags=re.IGNORECASE)

	def SearchAndReplaceInAnchorsMain(self, sender):
		self.SavePreferences()
		if not Glyphs.font:
			self.setStatus("❌ No font open.")
			return
		if not self.w.searchFor.get():
			# an empty search string would insert the replacement between all characters
			self.setStatus("❌ Please enter a search string.")
			return

		print("Report for Find and Replace in Anchors\n")
		renamedCount = 0
		for thisFont in self.fontsInScope():
			print(f"📄 {fontFileName(thisFont)}")
			changedGlyphNames = []
			for thisGlyph in self.glyphsInScope(thisFont):
				self.setStatus(f"🔠 {thisGlyph.name}")
				reportString = f"\t🔠 {thisGlyph.name}:"
				displayReportString = False

				for thisGlyphLayer in thisGlyph.layers:
					for thisAnchor in thisGlyphLayer.anchors:
						oldAnchorName = thisAnchor.name
						newAnchorName = self.newAnchorName(oldAnchorName)
						if oldAnchorName != newAnchorName:
							thisAnchor.name = newAnchorName
							reportString += f"\n\t\tlayer ‘{thisGlyphLayer.name}’: {oldAnchorName} → {newAnchorName}"
							displayReportString = True
							renamedCount += 1

				if displayReportString:
					print(reportString)
					changedGlyphNames.append(thisGlyph.name)

			if changedGlyphNames and self.prefBool("openTab"):
				thisFont.newTab("/" + "/".join(changedGlyphNames))

		message = f"Renamed {renamedCount} anchor{'' if renamedCount == 1 else 's'}."
		self.setStatus(f"✅ {message}")
		Glyphs.showNotification("Find and Replace in Anchors", f"{message} Details in Macro Window.")


SearchAndReplaceInAnchors()

# MenuTitle: Find and Replace in Anchor Names
__doc__ = """
Replaces strings in anchor names of all selected glyphs.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs
from mekkablue import mekkaObject


class SearchAndReplaceInAnchorNames(mekkaObject):
	prefDict = {
		"searchFor": "",
		"replaceBy": "",
	}

	def __init__(self):
		windowWidth = 520
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Search And Replace In Anchor Names",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.textSearch = vanilla.TextBox("auto", "Search", sizeStyle="small")
		self.w.searchFor = vanilla.EditText("auto", "", callback=self.SavePreferences, sizeStyle="small")
		self.w.searchFor.getNSTextField().setPlaceholderString_("tip")

		self.w.textReplace = vanilla.TextBox("auto", "Replace", sizeStyle="small")
		self.w.replaceBy = vanilla.EditText("auto", "", callback=self.SavePreferences, sizeStyle="small")
		self.w.replaceBy.getNSTextField().setPlaceholderString_("top")

		self.w.replaceButton = vanilla.Button("auto", "Replace", callback=self.SearchAndReplaceInAnchorNamesMain)
		self.w.setDefaultButton(self.w.replaceButton)

		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[textSearch]-gap-[searchFor]-gap-[textReplace]-gap-[replaceBy]-gap-[replaceButton(>=70)]-inset-|",
				"V:|-inset-[replaceButton]-inset-|",
				{"view1": self.w.searchFor, "attribute1": "width", "view2": self.w.replaceBy, "attribute2": "width"},
				{"view1": self.w.textSearch, "attribute1": "centerY", "view2": self.w.replaceButton, "attribute2": "centerY"},
				{"view1": self.w.searchFor, "attribute1": "centerY", "view2": self.w.replaceButton, "attribute2": "centerY"},
				{"view1": self.w.textReplace, "attribute1": "centerY", "view2": self.w.replaceButton, "attribute2": "centerY"},
				{"view1": self.w.replaceBy, "attribute1": "centerY", "view2": self.w.replaceButton, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def SearchAndReplaceInAnchorNamesMain(self, sender):
		self.SavePreferences()
		searchString = self.w.searchFor.get()
		replaceString = self.w.replaceBy.get()

		thisFont = Glyphs.font  # frontmost font
		if not thisFont:
			Glyphs.showNotification("Find and Replace in Anchor Names", "No font open.")
			return
		if not searchString:
			# an empty search string would insert the replacement between all characters
			Glyphs.showNotification("Find and Replace in Anchor Names", "Please enter a search string.")
			return

		print("Report for Find and Replace in Anchor Names\n")
		renamedCount = 0
		glyphNames = []
		for thisLayer in thisFont.selectedLayers:  # active layers of currently selected glyphs
			thisGlyph = thisLayer.parent
			if thisGlyph.name not in glyphNames:  # several layers of one glyph may be selected
				glyphNames.append(thisGlyph.name)

		for glyphName in glyphNames:
			thisGlyph = thisFont.glyphs[glyphName]
			reportString = f"\t🔠 {glyphName}:"
			displayReportString = False

			for thisGlyphLayer in thisGlyph.layers:
				for thisAnchor in thisGlyphLayer.anchors:
					oldAnchorName = thisAnchor.name
					newAnchorName = oldAnchorName.replace(searchString, replaceString)
					if oldAnchorName != newAnchorName:
						thisAnchor.name = newAnchorName
						reportString += f"\n\t\tlayer ‘{thisGlyphLayer.name}’: {oldAnchorName} → {newAnchorName}"
						displayReportString = True
						renamedCount += 1

			if displayReportString:
				print(reportString)

		Glyphs.showNotification("Find and Replace in Anchor Names", f"Renamed {renamedCount} anchor{'' if renamedCount == 1 else 's'}. Details in Macro Window.")
		self.w.close()  # delete if you want window to stay open


SearchAndReplaceInAnchorNames()

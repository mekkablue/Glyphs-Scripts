# MenuTitle: Find and Replace in Layer Names
__doc__ = """
Replaces strings in layer names of all selected glyphs. Useful for adjusting layers for the bracket trick: https://glyphsapp.com/learn/alternating-glyph-shapes/
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut, NSTextAlignmentRight
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, makeWindowResizable


class replaceInLayerNames(mekkaObject):
	prefDict = {
		"searchFor": "[10]",
		"replaceBy": "[20]",
		"allGlyphs": True,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 280
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Find and Replace in Layer Names",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and width
		)

		# UI elements:
		inset = 15

		self.w.textSearch = vanilla.TextBox("auto", "Search for:", sizeStyle='small')
		self.w.searchFor = vanilla.EditText("auto", "[130]", sizeStyle='small', callback=self.SavePreferences)

		self.w.textReplace = vanilla.TextBox("auto", "Replace by:", sizeStyle='small')
		self.w.replaceBy = vanilla.EditText("auto", "[150]", sizeStyle='small', callback=self.SavePreferences)

		self.w.allGlyphs = vanilla.CheckBox("auto", "Include all glyphs in font", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.replaceButton = vanilla.Button("auto", "Replace", sizeStyle='small', callback=self.buttonCallback)

		# checkboxes stretch vertically by default; with everything hugging, the window
		# ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# labels are right-aligned and share one width, so the fields line up:
		for labelName in ("textSearch", "textReplace"):
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[textSearch]-gap-[searchFor]-inset-|",
				"H:|-inset-[textReplace]-gap-[replaceBy]-inset-|",
				"H:|-inset-[allGlyphs]-(>=inset)-|",
				"H:|-(>=inset)-[replaceButton(>=70)]-inset-|",
				"V:|-inset-[searchFor]-row-[replaceBy]-row-[allGlyphs]-inset-[replaceButton]-inset-|",
				{"view1": self.w.textSearch, "attribute1": "centerY", "view2": self.w.searchFor, "attribute2": "centerY"},
				{"view1": self.w.textReplace, "attribute1": "centerY", "view2": self.w.replaceBy, "attribute2": "centerY"},
				{"view1": self.w.textSearch, "attribute1": "width", "view2": self.w.textReplace, "attribute2": "width"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6},
		)

		makeWindowResizable(self.w)  # resizable horizontally only

		self.LoadPreferences()

		self.w.setDefaultButton(self.w.replaceButton)
		self.w.open()
		self.w.makeKey()

	def buttonCallback(self, sender):
		thisFont = Glyphs.font
		if thisFont is None:
			Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			return

		if self.pref("allGlyphs"):
			glyphsToProcess = thisFont.glyphs
		else:
			selectedLayers = thisFont.selectedLayers
			glyphsToProcess = [layer.parent for layer in selectedLayers]

		searchFor = self.pref("searchFor")
		replaceBy = self.pref("replaceBy")
		if not searchFor:
			# an empty search string would match everywhere and insert the replacement between all characters:
			Message(title="Nothing to search for", message="Please enter a search string.", OKButton=None)
			return

		replaceCount = 0

		thisFont.disableUpdateInterface()
		try:
			for thisGlyph in glyphsToProcess:
				for thisLayer in thisGlyph.layers:
					# do not change names of master layers:
					if thisLayer.layerId != thisLayer.associatedFontMaster().id:
						if thisLayer.name is None:
							print("Warning! Empty layer name in: %s" % thisGlyph.name)
						elif searchFor in thisLayer.name:
							thisLayer.name = thisLayer.name.replace(searchFor, replaceBy)
							print("%s: %s" % (thisGlyph.name, thisLayer.name))
							replaceCount += 1
		except Exception as e:
			Glyphs.showMacroWindow()
			print("\n⚠️ Script Error:\n")
			import traceback
			print(traceback.format_exc())
			print()
			raise e
		finally:
			thisFont.enableUpdateInterface()  # re-enables UI updates in Font View

		if replaceCount > 0:
			Message(title="Replaced successfully", message="Replaced %i occurrences." % replaceCount, OKButton=None)
		else:
			Message(title="Nothing replaced", message="Could not find any occurrences of search string in the processed layers.", OKButton=None)


replaceInLayerNames()

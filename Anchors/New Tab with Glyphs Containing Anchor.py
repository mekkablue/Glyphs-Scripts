# MenuTitle: New Tab with Glyphs Containing Anchor
__doc__ = """
Opens a new tab with all glyphs containing a specific anchor.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject


class NewTabWithAnchor(mekkaObject):
	prefDict = {
		"anchorName": "ogonek",
		"allLayers": 0,
		"keepWindowOpen": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 370
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"New Tab with Anchor",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements:
		inset = 15
		self.w.text_1 = vanilla.TextBox("auto", "Look for anchor", sizeStyle="small")
		self.w.anchorName = vanilla.EditText("auto", "ogonek", callback=self.SavePreferences, sizeStyle="small")
		tooltip = "The name of the anchor to look for."
		self.w.text_1.setToolTip(tooltip)
		self.w.anchorName.setToolTip(tooltip)
		self.w.text_2 = vanilla.TextBox("auto", "and open a tab with all glyphs containing it.", sizeStyle="small")

		self.w.allLayers = vanilla.CheckBox("auto", "Look on all layers (otherwise only on current master)", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.allLayers.setToolTip("If off, only the layers of the current master are checked.")
		self.w.keepWindowOpen = vanilla.CheckBox("auto", "Keep window open", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.keepWindowOpen.setToolTip("Keep this window open after opening the tab.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Open Tab", callback=self.NewTabWithAnchorMain)
		self.w.runButton.setToolTip("Open a tab with all glyphs containing the anchor.")
		self.w.setDefaultButton(self.w.runButton)

		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[text_1]-gap-[anchorName]-inset-|",
				"H:|-inset-[text_2]-(>=inset)-|",
				"H:|-inset-[allLayers]-(>=inset)-|",
				"H:|-inset-[keepWindowOpen]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-inset-[anchorName]-row-[text_2]-row-[allLayers]-checkRow-[keepWindowOpen]-inset-[runButton]-inset-|",
				{"view1": self.w.text_1, "attribute1": "centerY", "view2": self.w.anchorName, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def layerContainsAnchor(self, thisLayer, anchorName):
		anchorNames = [a.name for a in thisLayer.anchors]
		if anchorName in anchorNames:
			print(f"\t🔠 Found {anchorName} in {thisLayer.parent.name}, on layer ‘{thisLayer.name}’")
			return True
		return False

	def glyphContainsAnchor(self, thisGlyph, anchorName, masterIdToBeChecked):
		if masterIdToBeChecked:
			masterLayer = thisGlyph.layers[masterIdToBeChecked]
			return self.layerContainsAnchor(masterLayer, anchorName)
		else:
			for thisLayer in thisGlyph.layers:
				if self.layerContainsAnchor(thisLayer, anchorName):
					return True
			return False

	def errMsg(self, errorMessage):
		message = f"The script 'New Tab with Anchor' encountered the following error: {errorMessage}"
		print(f"❌ {message}")
		Message(title="New Tab with Anchor Error", message=message, OKButton=None)

	def NewTabWithAnchorMain(self, sender):
		thisFont = Glyphs.font  # frontmost font
		if not thisFont:
			self.errMsg("No font open. Please open a font and try again.")
			return

		print(f"‘New Tab with Glyphs Containing Anchor’ Report for {thisFont.familyName}")
		print(thisFont.filepath)
		print()

		try:
			self.SavePreferences()

			anchorName = self.pref("anchorName")
			allLayers = self.prefBool("allLayers")
			keepWindowOpen = self.prefBool("keepWindowOpen")

			if anchorName:
				allGlyphsContainingAnchor = []
				if allLayers:
					masterId = None
				else:
					masterId = thisFont.selectedFontMaster.id  # active master id

				# go through all glyphs and look for anchor:
				for thisGlyph in thisFont.glyphs:
					if self.glyphContainsAnchor(thisGlyph, anchorName, masterId):
						allGlyphsContainingAnchor.append(thisGlyph.name)

				if allGlyphsContainingAnchor:
					# create string with slash-escaped names:
					glyphNameString = "/" + "/".join(allGlyphsContainingAnchor)
					thisFont.newTab(glyphNameString)
				else:
					Message(
						title="Could not find anchor",
						message=f"No glyph with anchor ‘{anchorName}’ found in {thisFont.familyName}.",
						OKButton=None,
					)

				if not keepWindowOpen:
					self.w.close()  # closes window
			else:
				self.errMsg("No anchor name specified. Please enter an anchor name before pressing the button.")
		except Exception as e:
			self.errMsg(e)
			import traceback
			print(traceback.format_exc())


Glyphs.clearLog()  # clears macro window log
NewTabWithAnchor()

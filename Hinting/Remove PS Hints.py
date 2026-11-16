# MenuTitle: Remove PS Hints
__doc__ = """
Removes PS Hints, selectively or completely.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityDefaultLow, NSLayoutPriorityWindowSizeStayPut
from GlyphsApp import Glyphs, Message, STEM, BOTTOMGHOST, TOPGHOST
from mekkablue import mekkaObject


class RemovePSHints(mekkaObject):
	prefDict = {
		"horizontalStemHints": 1,
		"verticalStemHints": 1,
		"ghostHints": 1,
		"where": 2,
		"includeBackgrounds": 0,
	}

	wheres = (
		"current layer of selected glyphs",
		"all layers of selected glyphs",
		"this master",
		"⚠️ the complete font",
		"⚠️ all open fonts",
	)

	def __init__(self):
		# Window 'self.w':
		windowWidth = 410
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Remove PS Hints",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "Remove the following hints in", sizeStyle='small', selectable=True)
		self.w.where = vanilla.PopUpButton("auto", self.wheres, sizeStyle='small', callback=self.SavePreferences)

		self.w.horizontalStemHints = vanilla.CheckBox("auto", "Horizontal stem hints", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.verticalStemHints = vanilla.CheckBox("auto", "Vertical stem hints", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.ghostHints = vanilla.CheckBox("auto", "Ghost hints", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeBackgrounds = vanilla.CheckBox("auto", "Include backgrounds", value=False, callback=self.SavePreferences, sizeStyle="small")

		self.w.progress = vanilla.ProgressBar("auto")
		self.w.progress.set(0)  # set progress indicator to zero

		self.w.status = vanilla.TextBox("auto", "🤖 Ready.", sizeStyle="small", selectable=True)
		self.w.status.getNSTextField().setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityDefaultLow, NSLayoutConstraintOrientationHorizontal)

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Remove Hints", callback=self.RemovePSHintsMain)
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; with everything hugging,
		# the window ends up exactly as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.descriptionText.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-gap-[where]-inset-|",
				"H:|-inset-[horizontalStemHints]-(>=inset)-|",
				"H:|-inset-[verticalStemHints]-(>=inset)-|",
				"H:|-inset-[ghostHints]-gap-[includeBackgrounds]-(>=inset)-|",
				"H:|-inset-[progress]-inset-|",
				"H:|-inset-[status]-(>=gap)-[runButton(>=70)]-inset-|",
				"V:|-gap-[where]-headlineGap-[horizontalStemHints]-checkRow-[verticalStemHints]-checkRow-[ghostHints]-barGap-[progress(16)]-inset-[runButton]-inset-|",
				{"view1": self.w.descriptionText, "attribute1": "centerY", "view2": self.w.where, "attribute2": "centerY"},
				{"view1": self.w.includeBackgrounds, "attribute1": "centerY", "view2": self.w.ghostHints, "attribute2": "centerY"},
				{"view1": self.w.status, "attribute1": "centerY", "view2": self.w.runButton, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "headlineGap": 10, "checkRow": 5, "barGap": 12},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		buttonEnable = self.pref("horizontalStemHints") or \
			self.pref("verticalStemHints") or \
			self.pref("ghostHints")
		self.w.runButton.enable(onOff=buttonEnable)

	def removeHintsFromLayer(self, primaryLayer, horizontalStemHints, verticalStemHints, ghostHints, includeBackgrounds):
		delCount = 0

		layers = [primaryLayer]
		if includeBackgrounds:
			layers.append(primaryLayer.background)

		for layer in layers:
			for i in reversed(range(len(layer.hints))):
				h = layer.hints[i]
				if Glyphs.versionNumber >= 3:
					# GLYPHS 3
					isPostScriptHint = h.isPostScript
				else:
					# GLYPHS 2
					isPostScriptHint = h.isPostScript()

				if isPostScriptHint:
					if horizontalStemHints and h.horizontal and h.type == STEM:
						del layer.hints[i]
						delCount += 1
					elif verticalStemHints and not h.horizontal and h.type == STEM:
						del layer.hints[i]
						delCount += 1
					elif ghostHints and h.type in (BOTTOMGHOST, TOPGHOST):
						del layer.hints[i]
						delCount += 1
		return delCount

	def RemovePSHintsMain(self, sender):
		try:
			# update settings to the latest user input:
			self.SavePreferences()

			horizontalStemHints = self.pref("horizontalStemHints")
			verticalStemHints = self.pref("verticalStemHints")
			ghostHints = self.pref("ghostHints")
			where = self.pref("where")
			includeBackgrounds = self.pref("includeBackgrounds")

			if where >= 4:
				theseFonts = Glyphs.fonts
			else:
				theseFonts = (Glyphs.font, ) if Glyphs.font else ()

			if not theseFonts:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			deletedHintsCount = 0
			for thisFont in theseFonts:
				print("Remove PS Hints Report for %s" % thisFont.familyName)
				print(thisFont.filepath if thisFont.filepath else f"{thisFont.familyName} (unsaved)")
				print()

				if where == 0:
					# Current Layer of Selected Glyphs
					objectList = set(thisFont.selectedLayers)
					count = len(objectList)
					for i, l in enumerate(objectList):
						self.w.progress.set(i / count * 100)
						deletedHintsCount += self.removeHintsFromLayer(l, horizontalStemHints, verticalStemHints, ghostHints, includeBackgrounds)
				elif where == 1:
					# All Layers of Selected Glyphs
					objectList = set(thisFont.selectedLayers)
					count = len(objectList)
					for i, l in enumerate(objectList):
						self.w.progress.set(i / count * 100)
						g = l.parent
						for ll in g.layers:
							deletedHintsCount += self.removeHintsFromLayer(ll, horizontalStemHints, verticalStemHints, ghostHints, includeBackgrounds)
				elif where == 2:
					# this Master
					masterID = thisFont.selectedFontMaster.id
					objectList = thisFont.glyphs
					count = len(objectList)
					for i, g in enumerate(objectList):
						self.w.progress.set(i / count * 100)
						for layer in g.layers:
							if layer.associatedMasterId == masterID:
								deletedHintsCount += self.removeHintsFromLayer(layer, horizontalStemHints, verticalStemHints, ghostHints, includeBackgrounds)
				else:
					# the Complete Font
					objectList = thisFont.glyphs
					count = len(objectList)
					for i, glyph in enumerate(objectList):
						self.w.progress.set(i / count * 100 / len(theseFonts))
						for layer in glyph.layers:
							deletedHintsCount += self.removeHintsFromLayer(layer, horizontalStemHints, verticalStemHints, ghostHints, includeBackgrounds)

			# complete progress bar:
			self.w.progress.set(100)
			self.w.status.set(f"✅ Removed {deletedHintsCount} hint{'' if deletedHintsCount == 1 else 's'} in {len(theseFonts)} font{'' if len(theseFonts) == 1 else 's'}")
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Remove PS Hints Error: %s" % e)
			import traceback
			print(traceback.format_exc())


RemovePSHints()

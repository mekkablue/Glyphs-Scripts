# MenuTitle: Replicate Anchors
__doc__ = """
Batch-add anchors to selected glyphs. Specify a source glyph to replicate the anchors from.
"""

import vanilla
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutConstraintOrientationVertical, NSLayoutPriorityDefaultHigh, NSLayoutPriorityRequired, NSLayoutPriorityWindowSizeStayPut, NSWindowStyleMaskResizable
from Foundation import NSSize
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject, reportFontName


class ReplicateAnchors(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"keepWindowOpen": 0,
		"sourceGlyphName": "A",
		"deleteAllExistingAnchors": 0,
		"overwriteExistingAnchors": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 280
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Replicate Anchors",
			autosaveName=self.domain("mainwindow"),  # stores last window position
		)

		# UI elements:
		inset = 15
		sourceTooltip = "Name of the glyph to copy the anchors from. Its master layers are matched with the masters of the selected glyphs."
		glyphNames = [glyph.name for glyph in Glyphs.font.glyphs] if Glyphs.font else []

		self.w.descriptionText = vanilla.TextBox("auto", "Replicate anchors in all selected glyphs:", sizeStyle="small", selectable=True)

		self.w.sourceGlyphNameText = vanilla.TextBox("auto", "Source glyph:", sizeStyle="small", selectable=True)
		self.w.sourceGlyphNameText.setToolTip(sourceTooltip)
		self.w.sourceGlyphName = vanilla.ComboBox("auto", glyphNames, sizeStyle="small", callback=self.SavePreferences)
		self.w.sourceGlyphName.setToolTip(sourceTooltip)

		self.w.overwriteExistingAnchors = vanilla.CheckBox("auto", "Overwrite existing anchors", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.overwriteExistingAnchors.setToolTip("Anchors with the same name as a source anchor are moved to the source position. Otherwise they are left alone.")
		self.w.deleteAllExistingAnchors = vanilla.CheckBox("auto", "Delete all existing anchors", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.deleteAllExistingAnchors.setToolTip("Removes all anchors of the selected glyphs first, so they end up with exactly the anchors of the source glyph.")
		self.w.keepWindowOpen = vanilla.CheckBox("auto", "Keep window open", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.keepWindowOpen.setToolTip("Leave this window open after replicating, e.g. for another round with a different selection.")

		# Run Button:
		self.w.runButton = vanilla.Button("auto", "Replicate", callback=self.ReplicateAnchorsMain)
		self.w.runButton.setToolTip("Replicate the anchors of the source glyph in the selected glyphs.")
		self.w.setDefaultButton(self.w.runButton)

		# checkboxes stretch vertically by default; hug so the window is as tall as the content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# the label hugs its text, so the combo box takes the leftover width
		nsLabel = self.w.sourceGlyphNameText.getNSTextField()
		nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
		nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[sourceGlyphNameText]-gap-[sourceGlyphName(>=80)]-inset-|",
				"H:|-inset-[overwriteExistingAnchors]-(>=inset)-|",
				"H:|-inset-[deleteAllExistingAnchors]-(>=inset)-|",
				"H:|-inset-[keepWindowOpen]-(>=inset)-|",
				"H:|-(>=inset)-[runButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-row-[sourceGlyphName]-row-[overwriteExistingAnchors]-checkRow-[deleteAllExistingAnchors]-checkRow-[keepWindowOpen]-inset-[runButton]-inset-|",
				{"view1": self.w.sourceGlyphNameText, "attribute1": "centerY", "view2": self.w.sourceGlyphName, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

		# resizable horizontally only: lock the content height Auto Layout arrived at
		nsWindow = self.w.getNSWindow()
		nsWindow.setStyleMask_(nsWindow.styleMask() | NSWindowStyleMaskResizable)
		nsWindow.layoutIfNeeded()
		contentHeight = nsWindow.contentView().frame().size.height
		nsWindow.setContentMinSize_(NSSize(windowWidth * 0.9, contentHeight))
		nsWindow.setContentMaxSize_(NSSize(windowWidth + 1000, contentHeight))

	def updateUI(self, sender=None):
		self.w.overwriteExistingAnchors.enable(not self.w.deleteAllExistingAnchors.get())

	def ReplicateAnchorsMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
				return

			print(f"Replicate Anchors Report for {reportFontName(thisFont)}\n")

			sourceGlyphName = self.pref("sourceGlyphName")
			deleteAllExistingAnchors = self.pref("deleteAllExistingAnchors")
			overwriteExistingAnchors = self.pref("overwriteExistingAnchors")
			keepWindowOpen = self.pref("keepWindowOpen")

			sourceGlyph = thisFont.glyphs[sourceGlyphName]
			if not sourceGlyph:
				Message(
					title="Script Error",
					message=f"No glyph with name ‘{sourceGlyphName}’ found in font ‘{thisFont.familyName}’.",
					OKButton=None,
				)
				return

			# each selected glyph once, even if several of its layers are selected:
			targetGlyphs = []
			for layer in thisFont.selectedLayers:
				glyph = layer.parent
				if glyph and glyph != sourceGlyph and glyph not in targetGlyphs:
					targetGlyphs.append(glyph)
			if not targetGlyphs:
				Message(title="No Target Glyphs", message="Select at least one glyph other than the source glyph.", OKButton=None)
				return

			for thisGlyph in targetGlyphs:
				layerCount = 0
				anchorCount = 0
				for thisLayer in thisGlyph.layers:
					if not (thisLayer.isMasterLayer or thisLayer.isSpecialLayer):
						continue
					layerCount += 1
					if deleteAllExistingAnchors:
						thisLayer.anchors = None
					sourceLayer = sourceGlyph.layers[thisLayer.associatedMasterId]
					if not sourceLayer:
						print(f"⚠️ {sourceGlyphName} has no layer for the master of ‘{thisLayer.name}’ in {thisGlyph.name}")
						continue
					for sourceAnchor in sourceLayer.anchors:
						if overwriteExistingAnchors or not thisLayer.anchors[sourceAnchor.name]:
							thisLayer.anchors[sourceAnchor.name] = sourceAnchor.copy()
							anchorCount += 1
				print(f"🔠 replicated {anchorCount} anchors of {sourceGlyphName} in {layerCount} layers of {thisGlyph.name}")

			if not keepWindowOpen:
				self.w.close()

			# Final report:
			Glyphs.showNotification(
				f"{thisFont.familyName}: Done",
				"Replicate Anchors is finished. Details in Macro Window",
			)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Replicate Anchors Error: {e}")
			import traceback
			print(traceback.format_exc())


ReplicateAnchors()

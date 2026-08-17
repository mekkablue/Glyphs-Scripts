# MenuTitle: Alignment Manager
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Manage Automatic Alignment for (multiple) selected glyphs.
"""

import vanilla
from GlyphsApp import Glyphs
from mekkablue import mekkaObject
from AppKit import NSLayoutConstraintOrientationHorizontal, NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationVertical, NSLayoutPriorityWindowSizeStayPut


class AutoAlignmentManager(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"includeAllGlyphs": 0,
		"includeAllLayers": 1,
		"differentiation": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 376
		windowHeight = 1  # Auto Layout grows the window to the required size
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Alignment Manager",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		inset = 15

		self.w.descriptionText = vanilla.TextBox("auto", "Manage component alignment in selected glyphs:", sizeStyle="small", selectable=True)

		self.w.includeAllGlyphs = vanilla.CheckBox("auto", "⚠️ Apply to ALL glyphs in font, i.e., ignore glyph selection", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.includeAllGlyphs.setToolTip("No matter what your glyph selection is, will enable/disable component alignment for ALL glyphs in the font.")

		self.w.includeAllLayers = vanilla.CheckBox("auto", "Include all masters and special layers (recommended)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.includeAllLayers.setToolTip("If enabled, will enable/disable automatic alignment not only for the currently selected masters/layers, but for ALL master layers, brace layers and bracket layers of selected glyphs. Will still ignore backup layers (the ones with a timestamp in their names).")

		self.w.differentiationText = vanilla.TextBox("auto", "Differentiate:", sizeStyle="small", selectable=True)
		self.w.differentiation = vanilla.PopUpButton("auto", ("Treat all components equally", "Ignore first component", "Only apply to first component"), sizeStyle="small", callback=self.SavePreferences)
		self.w.differentiation.setToolTip("You can choose to exclude the first component (usually the base letter) from toggling auto-alignment. This can be useful if you want to keep the diacritic marks aligned to the base, but still move the base. Or if you want to keep the base letter aligned, and place the marks freely.")

		self.w.alignVertical = vanilla.SquareButton("auto", "↕", sizeStyle="small", callback=self.AutoAlignmentManagerMain)
		self.w.alignVertical.setToolTip("Vertical align: aligns the component, but makes it shiftable in the italic angle.")
		self.w.alignFull = vanilla.SquareButton("auto", "☯", sizeStyle="small", callback=self.AutoAlignmentManagerMain)
		self.w.alignFull.setToolTip("Full align: aligns the component according to base glyph position and/or anchors.")
		self.w.alignmentTypeText = vanilla.TextBox("auto", "Quick change for selected components: alignment type", sizeStyle="small", selectable=True)

		# Run Button:
		self.w.enableButton = vanilla.Button("auto", "✅ Enable", callback=self.AutoAlignmentManagerMain)
		self.w.enableButton.setToolTip("Enables automatic alignment with the current span and settings.")
		self.w.disableButton = vanilla.Button("auto", "🚫 Disable", callback=self.AutoAlignmentManagerMain)
		self.w.disableButton.setToolTip("Disables automatic alignment with the current span and settings.")
		self.w.rotateButton = vanilla.Button("auto", "🔄 Rotate", callback=self.rotateComponents)
		self.w.rotateButton.setToolTip("Moves the last component into first place. Useful if you quickly want to fix component order without leaving he script UI.")

		# a label next to a flexible control hugs its text, so the control gets the leftover width:
		self.w.differentiationText.getNSTextField().setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)

		# checkboxes and square buttons do not resist vertical stretching by default; with
		# every control hugging vertically and no flexible gap in the chain, the window ends
		# up exactly as tall as Auto Layout needs. NSLayoutPriorityWindowSizeStayPut (500) is
		# the level at which a constraint starts outranking "keep the window size".
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[descriptionText]-inset-|",
				"H:|-inset-[includeAllGlyphs]-inset-|",
				"H:|-inset-[includeAllLayers]-inset-|",
				"H:|-inset-[differentiationText]-[differentiation]-inset-|",
				"H:|-inset-[alignVertical(20)]-gap-[alignFull(20)]-gap-[alignmentTypeText]-inset-|",
				"H:|-(>=inset)-[rotateButton(>=70)]-gap-[disableButton(>=70)]-gap-[enableButton(>=70)]-inset-|",
				"V:|-gap-[descriptionText]-line-[includeAllGlyphs]-line-[includeAllLayers]-line-[differentiation]-line-[alignVertical(18)]-inset-[enableButton]-inset-|",
				"V:[alignFull(18)]",
				"V:[rotateButton]-inset-|",
				"V:[disableButton]-inset-|",
				# labels ride along with the control they belong to:
				{"view1": self.w.differentiationText, "attribute1": "centerY", "view2": self.w.differentiation, "attribute2": "centerY"},
				{"view1": self.w.alignFull, "attribute1": "centerY", "view2": self.w.alignVertical, "attribute2": "centerY"},
				{"view1": self.w.alignmentTypeText, "attribute1": "centerY", "view2": self.w.alignVertical, "attribute2": "centerY"},
			],
			metrics={"inset": inset, "gap": 8, "line": 8},
		)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()
		self.updateUI()

	def updateUI(self, sender=None):
		self.w.rotateButton.enable(not self.w.includeAllGlyphs.get())

	def rotateComponents(self, sender=None):
		thisFont = Glyphs.font  # frontmost font
		selectedGlyphs = [layer.parent for layer in thisFont.selectedLayers]

		for thisGlyph in selectedGlyphs:
			print(f"Rotating: {thisGlyph.name}")
			for thisLayer in thisGlyph.layers:
				if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
					if len(thisLayer.components) > 1:
						thisLayer.selection = None

						if Glyphs.versionNumber >= 3:
							lastComponent = thisLayer.components.objectAtIndex_(thisLayer.components.count() - 1)
							lastComponent.makeFirst()
						else:
							lastComponent = thisLayer.components[-1]
							thisLayer.makeFirstComponent_(lastComponent)
					else:
						print("⚠️ Not enough components for rotating.")

	def enableOrDisableLayer(self, thisLayer, differentiation=0, sender=None):
		if thisLayer.components:
			treatAll = differentiation == 0
			ignoreFirst = differentiation == 1
			onlyFirst = differentiation == 2
			for i, thisComponent in enumerate(thisLayer.components):
				if treatAll or (i == 0 and onlyFirst) or (i > 0 and ignoreFirst):
					if sender is self.w.enableButton:
						thisComponent.setDisableAlignment_(False)
						print(f"\tEnabling alignment on: {thisLayer.name}")
					elif sender is self.w.disableButton:
						thisComponent.setDisableAlignment_(True)
						print(f"\tDisabling alignment on: {thisLayer.name}")
					else:
						return False
		return True

	def AutoAlignmentManagerMain(self, sender):
		try:
			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			Glyphs.clearLog()
			print(f"Auto Alignment Manager Report for {thisFont.familyName}")
			if thisFont.filepath:
				print(thisFont.filepath)
			else:
				print("⚠️ File not saved yet.")
			print()

			includeAllLayers = self.pref("includeAllLayers")
			componentDifferentiation = self.pref("differentiation")
			currentMasterID = thisFont.selectedFontMaster.id

			if sender == self.w.alignVertical or sender == self.w.alignFull:
				alignmentType = 1
				if sender == self.w.alignVertical:
					alignmentType = 3
				selectedLayer = thisFont.selectedLayers[0]
				selectionDoesNotCount = not selectedLayer.selection
				if includeAllLayers:
					compIndexes = []
					for i, c in enumerate(selectedLayer.components):
						if c.selected or selectionDoesNotCount:
							compIndexes.append(i)
					if compIndexes:
						thisGlyph = selectedLayer.parent
						for layer in thisGlyph.layers:
							if layer.isMasterLayer and layer.compareString() == selectedLayer.compareString():
								for index in compIndexes:
									layer.components[index].alignment = alignmentType
									# print("index", index, "alignmentType", alignmentType)  # DEBUG
				else:
					for c in selectedLayer.components:
						if c.selected:
							c.alignment = alignmentType
			else:
				if includeAllLayers:
					if self.pref("includeAllGlyphs"):
						selectedGlyphs = thisFont.glyphs
					else:
						selectedGlyphs = [layer.parent for layer in thisFont.selectedLayers]

					for thisGlyph in selectedGlyphs:
						print(f"Processing: {thisGlyph.name}")
						for thisLayer in thisGlyph.layers:
							if thisLayer.isMasterLayer or thisLayer.isSpecialLayer:
								if not self.enableOrDisableLayer(thisLayer, differentiation=componentDifferentiation, sender=sender):
									print("⚠️ Error setting alignment.")
				else:
					if self.pref("includeAllGlyphs"):
						layersToBeProcessed = [g.layers[currentMasterID] for g in thisFont.glyphs]
					else:
						# just the visible layer selection (maybe non-master, non-special layer too):
						layersToBeProcessed = thisFont.selectedLayers

					for thisLayer in layersToBeProcessed:
						print(f"Processing: {thisLayer.parent.name}")
						if not self.enableOrDisableLayer(thisLayer, differentiation=componentDifferentiation, sender=sender):
							print("⚠️ Error setting alignment.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Auto Alignment Manager Error: {e}")
			import traceback
			print(traceback.format_exc())


AutoAlignmentManager()

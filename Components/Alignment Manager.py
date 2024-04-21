# MenuTitle: Alignment Manager
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Manage Automatic Alignment for (multiple) selected glyphs.
"""

import vanilla
from GlyphsApp import Glyphs
from mekkablue import mekkaObject


class AutoAlignmentManager(mekkaObject):
	prefDict = {
		# "prefName": defaultValue,
		"includeAllGlyphs": 0,
		"includeAllLayers": 1,
		"differentiation": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 320
		windowHeight = 180
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Alignment Manager",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22

		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Manage component alignment in selected glyphs:", sizeStyle="small", selectable=True)
		linePos += lineHeight

		self.w.includeAllGlyphs = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "⚠️ Apply to ALL glyphs in font, i.e., ignore glyph selection", value=False, callback=self.SavePreferences, sizeStyle="small")
		self.w.includeAllGlyphs.getNSButton().setToolTip_("No matter what your glyph selection is, will enable/disable component alignment for ALL glyphs in the font.")
		linePos += lineHeight

		self.w.includeAllLayers = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Include all masters and special layers (recommended)", value=True, callback=self.SavePreferences, sizeStyle="small")
		self.w.includeAllLayers.getNSButton().setToolTip_("If enabled, will enable/disable automatic alignment not only for the currently selected masters/layers, but for ALL master layers, brace layers and bracket layers of selected glyphs. Will still ignore backup layers (the ones with a timestamp in their names).")
		linePos += lineHeight

		self.w.differentiationText = vanilla.TextBox((inset, linePos + 2, 75, 14), "Differentiate:", sizeStyle="small", selectable=True)
		self.w.differentiation = vanilla.PopUpButton((inset + 75, linePos, -inset, 17), ("Treat all components equally", "Ignore first component", "Only apply to first component"), sizeStyle="small", callback=self.SavePreferences)
		self.w.differentiation.getNSPopUpButton().setToolTip_("You can choose to exclude the first component (usually the base letter) from toggling auto-alignment. This can be useful if you want to keep the diacritic marks aligned to the base, but still move the base. Or if you want to keep the base letter aligned, and place the marks freely.")
		linePos += lineHeight

		self.w.alignVertical = vanilla.SquareButton((inset, linePos, 20, 18), "↕", sizeStyle="small", callback=self.AutoAlignmentManagerMain)
		self.w.alignVertical.getNSButton().setToolTip_("Vertical align: aligns the component, but makes it shiftable in the italic angle.")
		self.w.alignFull = vanilla.SquareButton((inset + 25, linePos, 20, 18), "☯", sizeStyle="small", callback=self.AutoAlignmentManagerMain)
		self.w.alignFull.getNSButton().setToolTip_("Full align: aligns the component according to base glyph position and/or anchors.")
		self.w.alignmentTypeText = vanilla.TextBox((inset + 50, linePos + 2, -inset, 14), "Quick change for selected components: alignment type", sizeStyle="small", selectable=True)
		linePos += lineHeight

		# Run Button:
		self.w.enableButton = vanilla.Button((-90 - inset, -20 - inset, -inset, -inset), "✅ Enable", callback=self.AutoAlignmentManagerMain)
		self.w.enableButton.getNSButton().setToolTip_("Enables automatic alignment with the current span and settings.")
		self.w.disableButton = vanilla.Button((-190 - inset, -20 - inset, -100 - inset, -inset), "🚫 Disable", callback=self.AutoAlignmentManagerMain)
		self.w.disableButton.getNSButton().setToolTip_("Disables automatic alignment with the current span and settings.")
		self.w.rotateButton = vanilla.Button((-290 - inset, -20 - inset, -200 - inset, -inset), "🔄 Rotate", callback=self.rotateComponents)
		self.w.rotateButton.getNSButton().setToolTip_("Moves the last component into first place. Useful if you quickly want to fix component order without leaving he script UI.")

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

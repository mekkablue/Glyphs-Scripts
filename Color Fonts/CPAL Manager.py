# MenuTitle: CPAL Manager
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Manage color palette (CPAL) indices in color layers: for specified color indexes, delete, disable, reassign or duplicate color layers.
"""

import vanilla
from mekkablue import mekkaObject


class CPALManager(mekkaObject):
	prefDict = {
		"removeIndex": 0,
		"disableIndex": 0,
		"duplicateFromIndex": 0,
		"duplicateToIndex": 1,
		"changeFromIndex": 0,
		"changeToIndex": 1,
		"currentMasterOnly": True,
		"applyFontWide": False,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 330
		windowHeight = 240
		windowWidthResize = 0  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"CPAL Manager",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight, tab1, tab2 = 12, 15, 22, 130, 205

		# Option 1: Remove color index
		self.w.removeText = vanilla.TextBox((inset, linePos + 2, tab1-5, 14), "Remove color index:", sizeStyle='small', selectable=True, alignment="right")
		self.w.removeIndex = vanilla.EditText((inset + tab1, linePos, 65, 19), "0", callback=self.SavePreferences, sizeStyle='small')
		self.w.removeButton = vanilla.Button((inset + tab2, linePos, -inset, 20), "Remove", callback=self.removeColorIndex, sizeStyle='small')
		self.w.removeIndex.setToolTip("Index of color palette layers to remove completely.")
		self.w.removeButton.setToolTip("Removes all layers with the specified color palette index from selected glyphs.")
		linePos += lineHeight

		# Option 2: Disable color index
		self.w.disableText = vanilla.TextBox((inset, linePos + 2, tab1-5, 14), "Disable color index:", sizeStyle='small', selectable=True, alignment="right")
		self.w.disableIndex = vanilla.EditText((inset + tab1, linePos, 65, 19), "0", callback=self.SavePreferences, sizeStyle='small')
		self.w.disableButton = vanilla.Button((inset + tab2, linePos, -inset, 20), "Disable", callback=self.disableColorIndex, sizeStyle='small')
		self.w.disableIndex.setToolTip("Index of color palette layers to disable (convert to backup layers).")
		self.w.disableButton.setToolTip("Removes the color palette attribute and converts layers to backup layers.")
		linePos += lineHeight

		# Option 3: Duplicate color index
		self.w.duplicateText = vanilla.TextBox((inset, linePos + 2, tab1-5, 14), "Duplicate color index:", sizeStyle='small', selectable=True, alignment="right")
		self.w.duplicateFromIndex = vanilla.EditText((inset + tab1, linePos, 25, 19), "0", callback=self.SavePreferences, sizeStyle='small')
		self.w.duplicateArrow = vanilla.TextBox((inset + tab1 + 25, linePos + 2, 15, 14), "→", sizeStyle='small')
		self.w.duplicateToIndex = vanilla.EditText((inset + tab1 + 25 + 15, linePos, 25, 19), "1", callback=self.SavePreferences, sizeStyle='small')
		self.w.duplicateButton = vanilla.Button((inset + tab2, linePos, -inset, 20), "Duplicate", callback=self.duplicateColorIndex, sizeStyle='small')
		self.w.duplicateFromIndex.setToolTip("Source color palette index to duplicate.")
		self.w.duplicateToIndex.setToolTip("Target color palette index for the duplicate.")
		self.w.duplicateButton.setToolTip("Creates a copy of layers with the source index and assigns them the target index.")
		linePos += lineHeight

		# Option 4: Change color index
		self.w.changeText = vanilla.TextBox((inset, linePos + 2, tab1-5, 14), "Change color index:", sizeStyle='small', selectable=True, alignment="right")
		self.w.changeFromIndex = vanilla.EditText((inset + tab1, linePos, 25, 19), "0", callback=self.SavePreferences, sizeStyle='small')
		self.w.changeArrow = vanilla.TextBox((inset + tab1 + 25, linePos + 2, 15, 14), "→", sizeStyle='small')
		self.w.changeToIndex = vanilla.EditText((inset + tab1 + 25 + 15, linePos, 25, 19), "1", callback=self.SavePreferences, sizeStyle='small')
		self.w.changeButton = vanilla.Button((inset + tab2, linePos, -inset, 20), "Reassign", callback=self.changeColorIndex, sizeStyle='small')
		self.w.changeFromIndex.setToolTip("Source color palette index to change from.")
		self.w.changeToIndex.setToolTip("Target color palette index to change to.")
		self.w.changeButton.setToolTip("Changes the color palette index from source to target.")
		linePos += lineHeight

		# Option 5: Cycle color indexes
		self.w.cycleText = vanilla.TextBox((inset, linePos + 2, tab2-5, 14), "Rotate color indexes  (0→1→2→0):", sizeStyle='small', selectable=True, alignment="right")
		self.w.cycleButton = vanilla.Button((inset + tab2, linePos, -inset, 20), "Cycle", callback=self.cycleColorIndexes, sizeStyle='small')
		self.w.cycleButton.setToolTip("Rotates color palette indexes: 0→1, 1→2, 2→3, etc. Last index becomes 0.")
		linePos += lineHeight

		# Option 6: Reverse color indexes
		self.w.reverseText = vanilla.TextBox((inset, linePos + 2, tab2-5, 14), "Reverse color indexes  (0,1,2↔2,1,0):", sizeStyle='small', selectable=True, alignment="right")
		self.w.reverseButton = vanilla.Button((inset + tab2, linePos, -inset, 20), "Reverse", callback=self.reverseColorIndexes, sizeStyle='small')
		self.w.reverseButton.setToolTip("Reverses color palette indexes: 0↔highest, 1↔second-highest, etc.")
		linePos += lineHeight + 10

		# Separator
		self.w.separator = vanilla.HorizontalLine((inset, linePos, -inset, 1))
		linePos += 10

		# Checkboxes
		self.w.currentMasterOnly = vanilla.CheckBox((inset, linePos, -inset, 20), "Current master only (otherwise all masters)", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.currentMasterOnly.setToolTip("Only process layers in the current master. Unchecked: process all masters.")
		linePos += lineHeight

		self.w.applyFontWide = vanilla.CheckBox((inset, linePos, -inset, 20), "⚠️ Apply to ALL glyphs (otherwise selected only)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.applyFontWide.setToolTip("Process all glyphs in the font. Unchecked: only process selected glyphs.")
		linePos += lineHeight + 5

		# Status line
		self.w.status = vanilla.TextBox((inset, linePos, -inset, 14), "", sizeStyle='small')
		linePos += lineHeight

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def getGlyphsToProcess(self):
		"""Returns the list of glyphs to process based on settings."""
		font = Glyphs.font
		if not font:
			return []

		if self.pref("applyFontWide"):
			return list(font.glyphs)
		else:
			return [layer.parent for layer in font.selectedLayers if layer.parent]

	def getLayersFromGlyph(self, glyph):
		"""Returns layers to process from a glyph based on settings."""
		if self.pref("currentMasterOnly"):
			currentMaster = Glyphs.font.selectedFontMaster
			return list([l for l in glyph.layers if l.associatedMasterId == currentMaster.id])
		else:
			return list(glyph.layers)

	def processLayers(self, operation, fromIndex, toIndex=None):
		"""
		Generic method to process layers based on operation type.
		
		operation: 'remove', 'disable', 'duplicate', or 'change'
		fromIndex: the color palette index to look for
		toIndex: the target index (for duplicate and change operations)
		"""
		font = Glyphs.font
		if not font:
			Message("No font open", "Please open a font first.", OKButton=None)
			return

		glyphs = self.getGlyphsToProcess()
		if not glyphs:
			Message("No glyphs to process", "Please select glyphs or enable ‘Apply font-wide’.", OKButton=None)
			return

		processedCount = 0
		glyphCount = 0
		font.disableUpdateInterface()

		for glyph in glyphs:
			glyphModified = False
			layers = self.getLayersFromGlyph(glyph)
			
			for i in range(len(layers)-1, -1, -1):
				layer = layers[i]
				layerID = layer.layerId

				# Check if layer has color palette attribute
				colorPalette = layer.attributes.get('colorPalette')
				if colorPalette is None:
					continue
				
				if colorPalette == fromIndex:
					if operation == 'remove':
						# Remove the layer
						glyph.removeLayerForId_(layerID)
						processedCount += 1
						glyphModified = True
						
					elif operation == 'disable':
						# Remove color palette attribute
						del layer.attributes['colorPalette']
						layer.name = f"Color {fromIndex} (disabled)"
						layer.elementDidChange_(1) # force updates the palette view
						processedCount += 1
						glyphModified = True
						
					elif operation == 'duplicate':
						# Create a duplicate layer
						newLayer = layer.copy()
						newLayer.attributes['colorPalette'] = toIndex
						glyph.layers.append(newLayer)
						processedCount += 1
						glyphModified = True
						
					elif operation == 'change':
						# Change the color palette index
						layer.attributes['colorPalette'] = toIndex
						processedCount += 1
						glyphModified = True
			
			if glyphModified:
				glyphCount += 1

		font.enableUpdateInterface()
		
		# Report results via status line
		operationNames = {
			'remove': 'removed',
			'disable': 'disabled',
			'duplicate': 'duplicated',
			'change': 'changed'
		}
		operationName = operationNames.get(operation, 'processed')
		self.w.status.set(f"{operationName.capitalize()} {processedCount} layer(s) in {glyphCount} glyph(s).")

	def removeColorIndex(self, sender=None):
		"""Remove all layers with the specified color index."""
		try:
			index = int(self.pref("removeIndex"))
			self.processLayers('remove', index)
		except ValueError:
			Message("Invalid input", "Please enter a valid number for the color index.", OKButton=None)

	def disableColorIndex(self, sender=None):
		"""Disable color layers (convert to backup layers)."""
		try:
			index = int(self.pref("disableIndex"))
			self.processLayers('disable', index)
		except ValueError:
			Message("Invalid input", "Please enter a valid number for the color index.", OKButton=None)

	def duplicateColorIndex(self, sender=None):
		"""Duplicate layers from one color index to another."""
		try:
			fromIndex = int(self.pref("duplicateFromIndex"))
			toIndex = int(self.pref("duplicateToIndex"))
			self.processLayers('duplicate', fromIndex, toIndex)
		except ValueError:
			Message("Invalid input", "Please enter valid numbers for both indices.", OKButton=None)

	def changeColorIndex(self, sender=None):
		"""Change color palette index from one value to another."""
		try:
			fromIndex = int(self.pref("changeFromIndex"))
			toIndex = int(self.pref("changeToIndex"))
			self.processLayers('change', fromIndex, toIndex)
		except ValueError:
			Message("Invalid input", "Please enter valid numbers for both indices.", OKButton=None)

	def cycleColorIndexes(self, sender=None):
		"""Cycle color palette indexes: 0→1, 1→2, 2→3, etc."""
		font = Glyphs.font
		if not font:
			Message("No font open", "Please open a font first.", OKButton=None)
			return

		glyphs = self.getGlyphsToProcess()
		if not glyphs:
			Message("No glyphs to process", "Please select glyphs or enable 'Apply font-wide'.", OKButton=None)
			return

		# Find max color index
		maxIndex = -1
		for glyph in glyphs:
			layers = self.getLayersFromGlyph(glyph)
			for layer in layers:
				colorPalette = layer.attributes.get('colorPalette')
				if colorPalette is not None and colorPalette > maxIndex:
					maxIndex = colorPalette

		if maxIndex < 0:
			self.w.status.set("No color layers found.")
			return

		# Cycle: use negative indices as temporary markers to avoid conflicts
		processedCount = 0
		glyphCount = 0
		font.disableUpdateInterface()

		for glyph in glyphs:
			glyphModified = False
			layers = self.getLayersFromGlyph(glyph)
			
			for layer in layers:
				colorPalette = layer.attributes.get('colorPalette')
				if colorPalette is not None:
					# First pass: mark with negative indices
					newIndex = -((colorPalette + 1) % (maxIndex + 1)) - 1
					layer.attributes['colorPalette'] = newIndex
					processedCount += 1
					glyphModified = True
			
			if glyphModified:
				glyphCount += 1

		# Second pass: convert negative indices back to positive
		for glyph in glyphs:
			layers = self.getLayersFromGlyph(glyph)
			for layer in layers:
				colorPalette = layer.attributes.get('colorPalette')
				if colorPalette is not None and colorPalette < 0:
					layer.attributes['colorPalette'] = -(colorPalette + 1)

		font.enableUpdateInterface()
		self.w.status.set(f"Cycled {processedCount} layer(s) in {glyphCount} glyph(s).")

	def reverseColorIndexes(self, sender=None):
		"""Reverse color palette indexes: 0↔highest, 1↔second-highest, etc."""
		font = Glyphs.font
		if not font:
			Message("No font open", "Please open a font first.", OKButton=None)
			return

		glyphs = self.getGlyphsToProcess()
		if not glyphs:
			Message("No glyphs to process", "Please select glyphs or enable 'Apply font-wide'.", OKButton=None)
			return

		# Find max color index
		maxIndex = -1
		for glyph in glyphs:
			layers = self.getLayersFromGlyph(glyph)
			for layer in layers:
				colorPalette = layer.attributes.get('colorPalette')
				if colorPalette is not None and colorPalette > maxIndex:
					maxIndex = colorPalette

		if maxIndex < 0:
			self.w.status.set("No color layers found.")
			return

		# Reverse
		processedCount = 0
		glyphCount = 0
		font.disableUpdateInterface()

		for glyph in glyphs:
			glyphModified = False
			layers = self.getLayersFromGlyph(glyph)
			
			for layer in layers:
				colorPalette = layer.attributes.get('colorPalette')
				if colorPalette is not None:
					newIndex = maxIndex - colorPalette
					layer.attributes['colorPalette'] = newIndex
					processedCount += 1
					glyphModified = True
			
			if glyphModified:
				glyphCount += 1

		font.enableUpdateInterface()
		self.w.status.set(f"Reversed {processedCount} layer(s) in {glyphCount} glyph(s).")


CPALManager()

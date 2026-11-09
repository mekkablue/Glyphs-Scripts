# MenuTitle: CPAL Manager
__doc__ = """
Manage color palette (CPAL) indices in color layers: for specified color indexes, delete, disable, reassign or duplicate color layers.
"""

import objc
import vanilla
from mekkablue import mekkaObject
from GlyphsApp import Glyphs, Message
from AppKit import (
	NSLayoutConstraintOrientationHorizontal,
	NSLayoutConstraintOrientationVertical,
	NSLayoutPriorityDefaultHigh,
	NSLayoutPriorityRequired,
	NSLayoutPriorityWindowSizeStayPut,
	NSTextAlignmentRight,
)
from Foundation import NSNumberFormatter


class SteppingEditText(vanilla.EditText):
	"""EditText with arrow-key stepping, as in Glyphs’ own numeric fields."""
	nsTextFieldClass = objc.lookUpClass("GSSteppingTextField")


def integerFormatter(minimum=None, maximum=None):
	formatter = NSNumberFormatter.alloc().init()
	formatter.setAllowsFloats_(False)
	if minimum is not None:
		formatter.setMinimum_(minimum)
	if maximum is not None:
		formatter.setMaximum_(maximum)
	return formatter


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
		windowWidth = 340
		windowHeight = 1  # Auto Layout grows the window to the height the content needs
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"CPAL Manager",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position
		)

		# UI elements:
		inset = 15

		# Option 1: Remove color index
		self.w.removeText = vanilla.TextBox("auto", "Remove color index:", sizeStyle='small', selectable=True)
		self.w.removeIndex = SteppingEditText("auto", "0", callback=self.SavePreferences, sizeStyle='small', formatter=integerFormatter(minimum=0))
		self.w.removeButton = vanilla.Button("auto", "Remove", callback=self.removeColorIndex, sizeStyle='small')
		tooltipText = "Index of color palette layers to remove completely."
		self.w.removeText.setToolTip(tooltipText)
		self.w.removeIndex.setToolTip(tooltipText)
		self.w.removeButton.setToolTip("Removes all layers with the specified color palette index from selected glyphs.")

		# Option 2: Disable color index
		self.w.disableText = vanilla.TextBox("auto", "Disable color index:", sizeStyle='small', selectable=True)
		self.w.disableIndex = SteppingEditText("auto", "0", callback=self.SavePreferences, sizeStyle='small', formatter=integerFormatter(minimum=0))
		self.w.disableButton = vanilla.Button("auto", "Disable", callback=self.disableColorIndex, sizeStyle='small')
		tooltipText = "Index of color palette layers to disable (convert to backup layers)."
		self.w.disableText.setToolTip(tooltipText)
		self.w.disableIndex.setToolTip(tooltipText)
		self.w.disableButton.setToolTip("Removes the color palette attribute and converts layers to backup layers.")

		# Option 3: Duplicate color index
		self.w.duplicateText = vanilla.TextBox("auto", "Duplicate color index:", sizeStyle='small', selectable=True)
		self.w.duplicateFromIndex = SteppingEditText("auto", "0", callback=self.SavePreferences, sizeStyle='small', formatter=integerFormatter(minimum=0))
		self.w.duplicateArrow = vanilla.TextBox("auto", "→", sizeStyle='small')
		self.w.duplicateToIndex = SteppingEditText("auto", "1", callback=self.SavePreferences, sizeStyle='small', formatter=integerFormatter(minimum=0))
		self.w.duplicateButton = vanilla.Button("auto", "Duplicate", callback=self.duplicateColorIndex, sizeStyle='small')
		self.w.duplicateText.setToolTip("Duplicate layers from the source index to the target index.")
		self.w.duplicateFromIndex.setToolTip("Source color palette index to duplicate.")
		self.w.duplicateToIndex.setToolTip("Target color palette index for the duplicate.")
		self.w.duplicateButton.setToolTip("Creates a copy of layers with the source index and assigns them the target index.")

		# Option 4: Change color index
		self.w.changeText = vanilla.TextBox("auto", "Change color index:", sizeStyle='small', selectable=True)
		self.w.changeFromIndex = SteppingEditText("auto", "0", callback=self.SavePreferences, sizeStyle='small', formatter=integerFormatter(minimum=0))
		self.w.changeArrow = vanilla.TextBox("auto", "→", sizeStyle='small')
		self.w.changeToIndex = SteppingEditText("auto", "1", callback=self.SavePreferences, sizeStyle='small', formatter=integerFormatter(minimum=0))
		self.w.changeButton = vanilla.Button("auto", "Reassign", callback=self.changeColorIndex, sizeStyle='small')
		self.w.changeText.setToolTip("Change the color palette index from the source to the target index.")
		self.w.changeFromIndex.setToolTip("Source color palette index to change from.")
		self.w.changeToIndex.setToolTip("Target color palette index to change to.")
		self.w.changeButton.setToolTip("Changes the color palette index from source to target.")

		# Option 5: Cycle color indexes
		self.w.cycleText = vanilla.TextBox("auto", "Rotate color indexes  (0→1→2→0):", sizeStyle='small', selectable=True)
		self.w.cycleButton = vanilla.Button("auto", "Cycle", callback=self.cycleColorIndexes, sizeStyle='small')
		tooltipText = "Rotates color palette indexes: 0→1, 1→2, 2→3, etc. Last index becomes 0."
		self.w.cycleText.setToolTip(tooltipText)
		self.w.cycleButton.setToolTip(tooltipText)

		# Option 6: Reverse color indexes
		self.w.reverseText = vanilla.TextBox("auto", "Reverse color indexes  (0,1,2↔2,1,0):", sizeStyle='small', selectable=True)
		self.w.reverseButton = vanilla.Button("auto", "Reverse", callback=self.reverseColorIndexes, sizeStyle='small')
		tooltipText = "Reverses color palette indexes: 0↔highest, 1↔second-highest, etc."
		self.w.reverseText.setToolTip(tooltipText)
		self.w.reverseButton.setToolTip(tooltipText)

		# Separator
		self.w.separator = vanilla.HorizontalLine("auto")

		# Checkboxes
		self.w.currentMasterOnly = vanilla.CheckBox("auto", "Current master only (otherwise all masters)", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.currentMasterOnly.setToolTip("Only process layers in the current master. Unchecked: process all masters.")

		self.w.applyFontWide = vanilla.CheckBox("auto", "⚠️ Apply to ALL glyphs (otherwise selected only)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.applyFontWide.setToolTip("Process all glyphs in the font. Unchecked: only process selected glyphs.")

		# Status line
		self.w.status = vanilla.TextBox("auto", "", sizeStyle='small')

		# labels: right-aligned, same width, hugging their text
		labelNames = ("removeText", "disableText", "duplicateText", "changeText", "cycleText", "reverseText")
		for labelName in labelNames:
			nsLabel = getattr(self.w, labelName).getNSTextField()
			nsLabel.setAlignment_(NSTextAlignmentRight)
			nsLabel.setContentHuggingPriority_forOrientation_(NSLayoutPriorityDefaultHigh, NSLayoutConstraintOrientationHorizontal)
			nsLabel.setContentCompressionResistancePriority_forOrientation_(NSLayoutPriorityRequired, NSLayoutConstraintOrientationHorizontal)

		# checkboxes stretch vertically by default; hug so the window is as tall as its content
		for view in self.w.getNSWindow().contentView().subviews():
			view.setContentHuggingPriority_forOrientation_(NSLayoutPriorityWindowSizeStayPut, NSLayoutConstraintOrientationVertical)

		# the four labels in front of fields share one width, all buttons share one width
		fieldLabelNames = ("removeText", "disableText", "duplicateText", "changeText")
		widestLabel = "duplicateText"
		buttonNames = ("removeButton", "disableButton", "changeButton", "cycleButton", "reverseButton")
		widestButton = "duplicateButton"
		widthRules = [
			{"view1": getattr(self.w, labelName), "attribute1": "width", "view2": getattr(self.w, widestLabel), "attribute2": "width"}
			for labelName in fieldLabelNames if labelName != widestLabel
		]
		widthRules += [
			{"view1": getattr(self.w, buttonName), "attribute1": "width", "view2": getattr(self.w, widestButton), "attribute2": "width"}
			for buttonName in buttonNames
		]

		self.w.addAutoPosSizeRules(
			[
				"H:|-inset-[removeText]-gap-[removeIndex(50)]-(>=gap)-[removeButton(>=70)]-inset-|",
				"H:|-inset-[disableText]-gap-[disableIndex(50)]-(>=gap)-[disableButton(>=70)]-inset-|",
				"H:|-inset-[duplicateText]-gap-[duplicateFromIndex(50)]-arrowGap-[duplicateArrow]-arrowGap-[duplicateToIndex(50)]-(>=gap)-[duplicateButton(>=70)]-inset-|",
				"H:|-inset-[changeText]-gap-[changeFromIndex(50)]-arrowGap-[changeArrow]-arrowGap-[changeToIndex(50)]-(>=gap)-[changeButton(>=70)]-inset-|",
				"H:|-inset-[cycleText]-gap-[cycleButton(>=70)]-inset-|",
				"H:|-inset-[reverseText]-gap-[reverseButton(>=70)]-inset-|",
				"H:|-inset-[separator]-inset-|",
				"H:|-inset-[currentMasterOnly]-(>=inset)-|",
				"H:|-inset-[applyFontWide]-(>=inset)-|",
				"H:|-inset-[status]-inset-|",
				"V:|-gap-[removeIndex]-row-[disableIndex]-row-[duplicateFromIndex]-row-[changeFromIndex]-row-[cycleButton]-row-[reverseButton]-inset-[separator(1)]-inset-[currentMasterOnly]-checkRow-[applyFontWide]-inset-[status]-inset-|",
				{"view1": self.w.removeText, "attribute1": "centerY", "view2": self.w.removeIndex, "attribute2": "centerY"},
				{"view1": self.w.removeButton, "attribute1": "centerY", "view2": self.w.removeIndex, "attribute2": "centerY"},
				{"view1": self.w.disableText, "attribute1": "centerY", "view2": self.w.disableIndex, "attribute2": "centerY"},
				{"view1": self.w.disableButton, "attribute1": "centerY", "view2": self.w.disableIndex, "attribute2": "centerY"},
				{"view1": self.w.duplicateText, "attribute1": "centerY", "view2": self.w.duplicateFromIndex, "attribute2": "centerY"},
				{"view1": self.w.duplicateArrow, "attribute1": "centerY", "view2": self.w.duplicateFromIndex, "attribute2": "centerY"},
				{"view1": self.w.duplicateToIndex, "attribute1": "centerY", "view2": self.w.duplicateFromIndex, "attribute2": "centerY"},
				{"view1": self.w.duplicateButton, "attribute1": "centerY", "view2": self.w.duplicateFromIndex, "attribute2": "centerY"},
				{"view1": self.w.changeText, "attribute1": "centerY", "view2": self.w.changeFromIndex, "attribute2": "centerY"},
				{"view1": self.w.changeArrow, "attribute1": "centerY", "view2": self.w.changeFromIndex, "attribute2": "centerY"},
				{"view1": self.w.changeToIndex, "attribute1": "centerY", "view2": self.w.changeFromIndex, "attribute2": "centerY"},
				{"view1": self.w.changeButton, "attribute1": "centerY", "view2": self.w.changeFromIndex, "attribute2": "centerY"},
				{"view1": self.w.cycleText, "attribute1": "centerY", "view2": self.w.cycleButton, "attribute2": "centerY"},
				{"view1": self.w.reverseText, "attribute1": "centerY", "view2": self.w.reverseButton, "attribute2": "centerY"},
			] + widthRules,
			metrics={"inset": inset, "gap": 8, "row": 6, "checkRow": 5, "arrowGap": 4},
		)

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
		self.processLayers('remove', self.prefInt("removeIndex"))

	def disableColorIndex(self, sender=None):
		"""Disable color layers (convert to backup layers)."""
		self.processLayers('disable', self.prefInt("disableIndex"))

	def duplicateColorIndex(self, sender=None):
		"""Duplicate layers from one color index to another."""
		fromIndex = self.prefInt("duplicateFromIndex")
		toIndex = self.prefInt("duplicateToIndex")
		self.processLayers('duplicate', fromIndex, toIndex)

	def changeColorIndex(self, sender=None):
		"""Change color palette index from one value to another."""
		fromIndex = self.prefInt("changeFromIndex")
		toIndex = self.prefInt("changeToIndex")
		self.processLayers('change', fromIndex, toIndex)

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

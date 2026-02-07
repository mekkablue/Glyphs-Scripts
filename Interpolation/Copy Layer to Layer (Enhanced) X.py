#MenuTitle: Copy Layer to Layer (Enhanced)
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Copies one layer to another layer across selected glyphs with enhanced options:
- Copy within the same glyph
- Create target glyph & layer if not present
- Add to existing layer contents (append mode)
- Support for color palette layers
- Copy to background layer
- Selective copying of paths, components, anchors, metrics
- Apply font-wide
"""

import vanilla
from Foundation import NSPoint
from mekkablue import mekkaObject, UpdateButton

class CopyLayerToLayer(mekkaObject):
	prefDict = {
		"intoBackground": False,
		"createIfNotPresent": True,
		"addToContents": False,
		"applyFontWide": False,
		"includePaths": True,
		"includeComponents": True,
		"includeAnchors": True,
		"includeMetrics": True,
	}
	
	def __init__(self):
		# Window 'self.w':
		windowWidth = 300
		windowHeight = 350
		windowWidthResize = 300
		windowHeightResize = 0
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Copy Layer to Layer (Enhanced)",
			minSize=(windowWidth, windowHeight),
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),
			autosaveName=self.domain("mainwindow")
		)

		# UI elements:
		linePos, inset, lineHeight, tabStop = 12, 15, 22, 80
		
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Copy layer contents from one layer to another:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.sourceFontText = vanilla.TextBox((inset, linePos + 2, tabStop, 14), "Source font:", sizeStyle='small', selectable=True)
		self.w.sourceFontPopup = vanilla.PopUpButton((inset + tabStop, linePos, -inset - 25, 17), self.GetFonts(), sizeStyle='small', callback=self.UpdateSourceLayers)
		self.w.sourceFontUpdateButton = UpdateButton((-inset - 20, linePos - 2, -inset, 18), callback=self.UpdateFontList)
		linePos += lineHeight

		self.w.sourceLayerText = vanilla.TextBox((inset, linePos + 2, tabStop, 14), "Source layer:", sizeStyle='small', selectable=True)
		self.w.sourceLayerPopup = vanilla.PopUpButton((inset + tabStop, linePos, -inset, 17), [], sizeStyle='small')
		linePos += lineHeight

		self.w.targetFontText = vanilla.TextBox((inset, linePos + 2, tabStop, 14), "Target font:", sizeStyle='small', selectable=True)
		self.w.targetFontPopup = vanilla.PopUpButton((inset + tabStop, linePos, -inset, 17), self.GetFonts(), sizeStyle='small', callback=self.UpdateTargetLayers)
		linePos += lineHeight

		self.w.targetLayerText = vanilla.TextBox((inset, linePos + 2, tabStop, 14), "Target layer:", sizeStyle='small', selectable=True)
		self.w.targetLayerPopup = vanilla.PopUpButton((inset + tabStop, linePos, -inset, 17), [], sizeStyle='small')
		linePos += lineHeight

		# Options with tooltips
		linePos += 5
		self.w.intoBackground = vanilla.CheckBox((inset, linePos, -inset, 20), "Copy into background instead", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.intoBackground.getNSButton().setToolTip_("Copies source layer content into the background of the target layer instead of the foreground.")
		linePos += lineHeight

		self.w.createIfNotPresent = vanilla.CheckBox((inset, linePos, -inset, 20), "Create target glyph & layer if not already present", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.createIfNotPresent.getNSButton().setToolTip_("Automatically creates the target layer (and glyph if necessary) if it doesn't exist. Useful for adding new layers to all selected glyphs.")
		linePos += lineHeight

		self.w.addToContents = vanilla.CheckBox((inset, linePos, -inset, 20), "Add to layer contents (don't overwrite)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.addToContents.getNSButton().setToolTip_("Appends source content to target layer instead of replacing it. Useful for combining multiple design elements.")
		linePos += lineHeight

		self.w.applyFontWide = vanilla.CheckBox((inset, linePos, -inset, 20), "Apply font-wide (all glyphs in source font)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.applyFontWide.getNSButton().setToolTip_("Processes all glyphs in the source font instead of only selected glyphs in the target font.")
		linePos += lineHeight

		# Include options
		linePos += 5
		self.w.includeText = vanilla.TextBox((inset, linePos + 2, 90, 14), "Include:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.includePaths = vanilla.CheckBox((inset + 10, linePos, 80, 20), "Paths", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includePaths.getNSButton().setToolTip_("Copy all paths (outlines) from the source layer.")
		
		self.w.includeComponents = vanilla.CheckBox((inset + 90, linePos, 100, 20), "Components", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeComponents.getNSButton().setToolTip_("Copy all components (references to other glyphs) from the source layer.")
		linePos += lineHeight

		self.w.includeAnchors = vanilla.CheckBox((inset + 10, linePos, 80, 20), "Anchors", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeAnchors.getNSButton().setToolTip_("Copy all anchors (attachment points) from the source layer.")
		
		self.w.includeMetrics = vanilla.CheckBox((inset + 90, linePos, 100, 20), "Metrics", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeMetrics.getNSButton().setToolTip_("Copy layer width and sidebearing metrics from the source layer.")
		linePos += lineHeight

		# Color palette option (hidden by default)
		linePos += 5
		self.w.colorPaletteText = vanilla.TextBox((inset, linePos + 2, 90, 14), "Color palette:", sizeStyle='small', selectable=True)
		self.w.colorPalettePopup = vanilla.PopUpButton((inset + 90, linePos, -inset, 17), ["None"], sizeStyle='small')
		self.w.colorPaletteText.show(False)
		self.w.colorPalettePopup.show(False)
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-120 - inset, -20 - inset, -inset, -inset), "Copy Layers", sizeStyle='regular', callback=self.CopyLayerToLayerMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Update the layer popups after fonts are loaded
		self.UpdateSourceLayers(None)
		self.UpdateTargetLayers(None)

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def GetFonts(self):
		"""Returns a list of font names for the popups"""
		myFontList = ["Current Font"]
		for thisFont in Glyphs.fonts:
			fontName = thisFont.filepath.lastPathComponent() if thisFont.filepath else "<unsaved file>"
			myFontList.append('%s (family: %s)' % (fontName, thisFont.familyName))
		return myFontList

	def GetFont(self, fontPopup):
		"""Returns the font object based on popup selection"""
		fontIndex = fontPopup.get()
		if fontIndex == 0:
			return Glyphs.font
		else:
			return Glyphs.fonts[fontIndex - 1]

	def UpdateFontList(self, sender=None):
		"""Updates all font popups with currently opened fonts"""
		fontList = self.GetFonts()
		
		# Store current selections
		sourceSelection = self.w.sourceFontPopup.get()
		targetSelection = self.w.targetFontPopup.get()
		
		# Update popup lists
		self.w.sourceFontPopup.setItems(fontList)
		self.w.targetFontPopup.setItems(fontList)
		
		# Try to restore selections if still valid
		if sourceSelection < len(fontList):
			self.w.sourceFontPopup.set(sourceSelection)
		else:
			self.w.sourceFontPopup.set(0)
			
		if targetSelection < len(fontList):
			self.w.targetFontPopup.set(targetSelection)
		else:
			self.w.targetFontPopup.set(0)
		
		# Update layer lists
		self.UpdateSourceLayers(None)
		self.UpdateTargetLayers(None)

	def UpdateSourceLayers(self, sender):
		"""Updates the source layer popup based on selected font"""
		font = self.GetFont(self.w.sourceFontPopup)
		if font and len(font.glyphs) > 0:
			layerNames = []
			for layer in font.glyphs[0].layers:
				if layer.name:
					layerNames.append(layer.name)
			self.w.sourceLayerPopup.setItems(layerNames if layerNames else ["Regular"])

	def UpdateTargetLayers(self, sender):
		"""Updates the target layer popup and color palette options based on selected font"""
		font = self.GetFont(self.w.targetFontPopup)
		if font and len(font.glyphs) > 0:
			# Update layer list
			layerNames = []
			for layer in font.glyphs[0].layers:
				if layer.name:
					layerNames.append(layer.name)
			self.w.targetLayerPopup.setItems(layerNames if layerNames else ["Regular"])
			
			# Check for color palettes
			if hasattr(font, 'colorPalettes') and font.colorPalettes:
				paletteOptions = ["None (default)"]
				for i, palette in enumerate(font.colorPalettes):
					paletteOptions.append("Color %d (%s)" % (i, palette.name if hasattr(palette, 'name') and palette.name else "Unnamed"))
				self.w.colorPalettePopup.setItems(paletteOptions)
				self.w.colorPaletteText.show(True)
				self.w.colorPalettePopup.show(True)
			else:
				self.w.colorPaletteText.show(False)
				self.w.colorPalettePopup.show(False)

	def CopyLayerToLayerMain(self, sender=None):
		"""Main function to copy layers"""
		try:
			# Get fonts
			sourceFont = self.GetFont(self.w.sourceFontPopup)
			targetFont = self.GetFont(self.w.targetFontPopup)
			
			if not sourceFont or not targetFont:
				Message("Error", "Could not access source or target font.", OKButton=None)
				return

			# Get layer names
			sourceLayerName = self.w.sourceLayerPopup.getItems()[self.w.sourceLayerPopup.get()]
			targetLayerName = self.w.targetLayerPopup.getItems()[self.w.targetLayerPopup.get()]
			
			# Get options using prefDict keys - no repetition!
			prefs = {key: self.pref(key) for key in self.prefDict.keys()}
			
			# Get color palette selection
			colorPaletteIndex = None
			if self.w.colorPalettePopup.isVisible() and self.w.colorPalettePopup.get() > 0:
				colorPaletteIndex = self.w.colorPalettePopup.get() - 1

			# Determine which glyphs to process
			if prefs["applyFontWide"]:
				glyphsToProcess = [g.name for g in sourceFont.glyphs]
			else:
				selectedGlyphs = [layer.parent for layer in targetFont.selectedLayers]
				if not selectedGlyphs:
					Message("No Selection", "Please select at least one glyph.", OKButton=None)
					return
				glyphsToProcess = [g.name for g in selectedGlyphs]

			processedCount = 0
			skippedCount = 0
			createdGlyphCount = 0
			createdLayerCount = 0

			for glyphName in glyphsToProcess:
				# Find corresponding glyph in source font
				sourceGlyph = sourceFont.glyphs[glyphName]
				if not sourceGlyph:
					skippedCount += 1
					continue

				# Find source layer
				sourceLayer = None
				for layer in sourceGlyph.layers:
					if layer.name == sourceLayerName:
						sourceLayer = layer
						break
				
				if not sourceLayer:
					skippedCount += 1
					continue

				# Find or create target glyph
				targetGlyph = targetFont.glyphs[glyphName]
				if not targetGlyph:
					if prefs["createIfNotPresent"]:
						targetGlyph = GSGlyph(glyphName)
						targetFont.glyphs.append(targetGlyph)
						createdGlyphCount += 1
					else:
						skippedCount += 1
						continue

				# Find or create target layer
				targetLayer = None
				for layer in targetGlyph.layers:
					if layer.name == targetLayerName:
						targetLayer = layer
						break

				# Create layer if requested and not present
				if not targetLayer and prefs["createIfNotPresent"]:
					targetLayer = GSLayer()
					targetLayer.name = targetLayerName
					
					# Handle color palette assignment
					if colorPaletteIndex is not None:
						targetLayer.attributes['colorPalette'] = colorPaletteIndex
					
					targetGlyph.layers.append(targetLayer)
					createdLayerCount += 1
				
				if not targetLayer:
					skippedCount += 1
					continue

				# Determine target for copying (foreground or background)
				if prefs["intoBackground"]:
					if not prefs["addToContents"]:
						targetLayer.background.clear()
					copyTarget = targetLayer.background
				else:
					if not prefs["addToContents"]:
						targetLayer.clear()
					copyTarget = targetLayer

				# Copy paths
				if prefs["includePaths"]:
					for path in sourceLayer.paths:
						newPath = path.copy()
						copyTarget.shapes.append(newPath)

				# Copy components
				if prefs["includeComponents"]:
					for component in sourceLayer.components:
						newComponent = component.copy()
						copyTarget.shapes.append(newComponent)

				# Copy anchors
				if prefs["includeAnchors"]:
					if prefs["addToContents"]:
						# Add anchors only if they don't already exist
						for anchor in sourceLayer.anchors:
							existingAnchor = None
							for a in copyTarget.anchors:
								if a.name == anchor.name:
									existingAnchor = a
									break
							if not existingAnchor:
								newAnchor = anchor.copy()
								copyTarget.anchors.append(newAnchor)
					else:
						# Replace all anchors
						for anchor in sourceLayer.anchors:
							newAnchor = anchor.copy()
							copyTarget.anchors.append(newAnchor)

				# Copy metrics if requested and not copying to background
				if prefs["includeMetrics"] and not prefs["intoBackground"]:
					targetLayer.width = sourceLayer.width
					if hasattr(sourceLayer, 'leftMetricsKey') and sourceLayer.leftMetricsKey:
						targetLayer.leftMetricsKey = sourceLayer.leftMetricsKey
					if hasattr(sourceLayer, 'rightMetricsKey') and sourceLayer.rightMetricsKey:
						targetLayer.rightMetricsKey = sourceLayer.rightMetricsKey

				processedCount += 1

			# Show results
			resultMessage = "Processed %d glyph(s)" % processedCount
			if createdGlyphCount > 0:
				resultMessage += "\nCreated %d new glyph(s)" % createdGlyphCount
			if createdLayerCount > 0:
				resultMessage += "\nCreated %d new layer(s)" % createdLayerCount
			if skippedCount > 0:
				resultMessage += "\nSkipped %d glyph(s)" % skippedCount
			
			Message("Copy Complete", resultMessage, OKButton=None)

			# Save preferences
			self.SavePreferences()

			# Close window
			self.w.close()

		except Exception as e:
			# Brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Copy Layer to Layer Error: %s" % e)
			import traceback
			print(traceback.format_exc())

# Run the script
CopyLayerToLayer()

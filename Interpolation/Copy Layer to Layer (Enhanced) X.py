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
- Selective copying of paths, components, anchors, hints, metrics
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
		"includeHints": True,
		"includeMetrics": True,
	}
	
	def __init__(self):
		# Window 'self.w':
		windowWidth = 300
		windowHeight = 370
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

		self.w.includePaths = vanilla.CheckBox((inset + 10, linePos, 65, 20), "Paths", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includePaths.getNSButton().setToolTip_("Copy all paths (outlines) from the source layer.")
		
		self.w.includeComponents = vanilla.CheckBox((inset + 75, linePos, 90, 20), "Components", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeComponents.getNSButton().setToolTip_("Copy all components (references to other glyphs) from the source layer.")
		
		self.w.includeHints = vanilla.CheckBox((inset + 165, linePos, 90, 20), "Hints", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeHints.getNSButton().setToolTip_("Copy all hints (TrueType instructions) from the source layer.")
		linePos += lineHeight

		self.w.includeAnchors = vanilla.CheckBox((inset + 10, linePos, 65, 20), "Anchors", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeAnchors.getNSButton().setToolTip_("Copy all anchors (attachment points) from the source layer.")
		
		self.w.includeMetrics = vanilla.CheckBox((inset + 75, linePos, 90, 20), "Metrics", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeMetrics.getNSButton().setToolTip_("Copy layer width and sidebearing metrics from the source layer.")
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

	def GetColorPalettes(self, font):
		"""Returns the color palettes from font's custom parameters"""
		if font and font.customParameters["Color Palettes"]:
			palettes = font.customParameters["Color Palettes"]
			if palettes and len(palettes) > 0:
				# Return the first palette (index 0) which contains the color definitions
				return palettes[0]
		return None

	def GetLayerList(self, font):
		"""Returns a list of layer names and master+color combinations"""
		if not font or len(font.glyphs) == 0:
			return ["Regular"]
		
		layerNames = []
		masterLayers = []
		
		# Collect regular master layers
		for layer in font.glyphs[0].layers:
			if layer.name:
				masterLayers.append(layer.name)
				layerNames.append(layer.name)
		
		# Add color palette layers if they exist
		colorPalette = self.GetColorPalettes(font)
		if colorPalette:
			numColors = len(colorPalette)
			# For each master, add master+color combinations
			for masterName in masterLayers:
				for colorIndex in range(numColors):
					layerNames.append("%s, Color %d" % (masterName, colorIndex))
		
		return layerNames if layerNames else ["Regular"]

	def ParseLayerSelection(self, layerName):
		"""Parses layer selection to determine if it's a color palette layer
		Returns: (isColorLayer, masterName, colorIndex)"""
		if ", Color " in layerName:
			try:
				parts = layerName.split(", Color ")
				masterName = parts[0]
				colorIndex = int(parts[1])
				return (True, masterName, colorIndex)
			except:
				pass
		return (False, layerName, None)

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
		layerNames = self.GetLayerList(font)
		self.w.sourceLayerPopup.setItems(layerNames)

	def UpdateTargetLayers(self, sender):
		"""Updates the target layer popup based on selected font"""
		font = self.GetFont(self.w.targetFontPopup)
		layerNames = self.GetLayerList(font)
		self.w.targetLayerPopup.setItems(layerNames)

	def GetColorLayers(self, glyph, masterName, colorIndex):
		"""Returns all layers with the specified master and color palette index"""
		colorLayers = []
		for layer in glyph.layers:
			if layer.name == masterName and hasattr(layer, 'attributes') and layer.attributes.get('colorPalette') == colorIndex:
				colorLayers.append(layer)
		return colorLayers

	def CopyLayerToLayerMain(self, sender=None):
		"""Main function to copy layers"""
		try:
			# Get fonts
			sourceFont = self.GetFont(self.w.sourceFontPopup)
			targetFont = self.GetFont(self.w.targetFontPopup)
			
			if not sourceFont or not targetFont:
				Message("Error", "Could not access source or target font.", OKButton=None)
				return

			# Get layer names and parse them
			sourceLayerName = self.w.sourceLayerPopup.getItems()[self.w.sourceLayerPopup.get()]
			targetLayerName = self.w.targetLayerPopup.getItems()[self.w.targetLayerPopup.get()]
			
			sourceIsColor, sourceMasterName, sourceColorIndex = self.ParseLayerSelection(sourceLayerName)
			targetIsColor, targetMasterName, targetColorIndex = self.ParseLayerSelection(targetLayerName)
			
			# Get options using prefDict keys
			prefs = {key: self.pref(key) for key in self.prefDict.keys()}

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

				# Find source layer(s)
				sourceLayers = []
				if sourceIsColor:
					# Get all layers with this master name and color palette index
					sourceLayers = self.GetColorLayers(sourceGlyph, sourceMasterName, sourceColorIndex)
				else:
					# Get the named master layer
					for layer in sourceGlyph.layers:
						if layer.name == sourceMasterName:
							sourceLayers = [layer]
							break
				
				if not sourceLayers:
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

				# Handle color to color copying (potentially multiple layers)
				if sourceIsColor and targetIsColor:
					# Copy each source color layer to corresponding target color layer
					targetColorLayers = self.GetColorLayers(targetGlyph, targetMasterName, targetColorIndex)
					
					for i, sourceLayer in enumerate(sourceLayers):
						# Find or create corresponding target layer
						if i < len(targetColorLayers):
							targetLayer = targetColorLayers[i]
						elif prefs["createIfNotPresent"]:
							# Create new color layer
							targetLayer = GSLayer()
							targetLayer.name = targetMasterName
							targetLayer.attributes['colorPalette'] = targetColorIndex
							# Associate with the master
							targetLayer.associatedMasterId = targetGlyph.layers[0].associatedMasterId
							targetGlyph.layers.append(targetLayer)
							createdLayerCount += 1
						else:
							continue
						
						self.CopyLayerContents(sourceLayer, targetLayer, prefs)
						processedCount += 1
				
				# Handle non-color to color copying
				elif not sourceIsColor and targetIsColor:
					sourceLayer = sourceLayers[0]
					# Find first target layer with matching master and color index
					targetColorLayers = self.GetColorLayers(targetGlyph, targetMasterName, targetColorIndex)
					
					if targetColorLayers:
						targetLayer = targetColorLayers[0]
					elif prefs["createIfNotPresent"]:
						targetLayer = GSLayer()
						targetLayer.name = targetMasterName
						targetLayer.attributes['colorPalette'] = targetColorIndex
						# Associate with the master
						for layer in targetGlyph.layers:
							if layer.name == targetMasterName and not layer.attributes.get('colorPalette'):
								targetLayer.associatedMasterId = layer.associatedMasterId
								break
						targetGlyph.layers.append(targetLayer)
						createdLayerCount += 1
					else:
						skippedCount += 1
						continue
					
					self.CopyLayerContents(sourceLayer, targetLayer, prefs)
					processedCount += 1
				
				# Handle color to non-color copying
				elif sourceIsColor and not targetIsColor:
					# Copy first source color layer to target master layer
					sourceLayer = sourceLayers[0]
					
					# Find target master layer
					targetLayer = None
					for layer in targetGlyph.layers:
						if layer.name == targetMasterName and not layer.attributes.get('colorPalette'):
							targetLayer = layer
							break

					if not targetLayer and prefs["createIfNotPresent"]:
						targetLayer = GSLayer()
						targetLayer.name = targetMasterName
						targetGlyph.layers.append(targetLayer)
						createdLayerCount += 1
					
					if not targetLayer:
						skippedCount += 1
						continue

					self.CopyLayerContents(sourceLayer, targetLayer, prefs)
					processedCount += 1
				
				# Handle regular master to master layer copying
				else:
					sourceLayer = sourceLayers[0]
					
					# Find or create target master layer
					targetLayer = None
					for layer in targetGlyph.layers:
						if layer.name == targetMasterName and not layer.attributes.get('colorPalette'):
							targetLayer = layer
							break

					# Create layer if requested and not present
					if not targetLayer and prefs["createIfNotPresent"]:
						targetLayer = GSLayer()
						targetLayer.name = targetMasterName
						targetGlyph.layers.append(targetLayer)
						createdLayerCount += 1
					
					if not targetLayer:
						skippedCount += 1
						continue

					self.CopyLayerContents(sourceLayer, targetLayer, prefs)
					processedCount += 1

			# Show results
			resultMessage = "Processed %d layer(s)" % processedCount
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

	def CopyLayerContents(self, sourceLayer, targetLayer, prefs):
		"""Copies contents from source layer to target layer based on preferences"""
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

		# Copy hints
		if prefs["includeHints"]:
			for hint in sourceLayer.hints:
				newHint = hint.copy()
				copyTarget.hints.append(newHint)

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

# Run the script
CopyLayerToLayer()

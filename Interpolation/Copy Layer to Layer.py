# MenuTitle: Copy Layer to Layer
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Copies one layer to another layer across selected glyphs:
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
from mekkablue import mekkaObject, newGlyphWithName, UpdateButton


def isColorLayer(layer):
	"""True if the layer carries a colorPalette attribute.
	Must test `is not None`: color index 0 is falsy."""
	attributes = getattr(layer, "attributes", None)
	if not attributes:
		return False
	return attributes.get("colorPalette") is not None


class CopyLayerToLayer(mekkaObject):
	prefDict = {
		"sourceFontPopup": 0,
		"targetFontPopup": 0,
		"sourceLayerPopup": 0,
		"targetLayerPopup": 0,
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
		# Layer specs parallel to the layer popup items: (masterID, masterName, colorIndex).
		# Initialised before any widget so that updateUI() is safe if called early.
		self.sourceLayerSpecs = []
		self.targetLayerSpecs = []

		# Window 'self.w':
		windowWidth = 300
		windowHeight = 330
		windowWidthResize = 300
		windowHeightResize = 0
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),
			"Copy Layer to Layer",
			minSize=(windowWidth, windowHeight),
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),
			autosaveName=self.domain("mainwindow")
		)

		# UI elements:
		linePos, inset, lineHeight, tabStop = 12, 15, 22, 80

		self.w.descriptionText = vanilla.TextBox((inset, linePos, -inset, 14), "Copy layer contents from one layer to another:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.sourceFontText = vanilla.TextBox((inset, linePos + 2, tabStop, 14), "Source font:", sizeStyle='small', selectable=True)
		self.w.sourceFontPopup = vanilla.PopUpButton((inset + tabStop, linePos, -inset - 25, 17), self.GetFonts(), sizeStyle='small', callback=self.UpdateSourceLayers)
		self.w.sourceFontUpdateButton = UpdateButton((-inset - 20, linePos - 2, -inset, 18), callback=self.UpdateFontList)
		linePos += lineHeight

		self.w.sourceLayerText = vanilla.TextBox((inset, linePos + 2, tabStop, 14), "Source layer:", sizeStyle='small', selectable=True)
		self.w.sourceLayerPopup = vanilla.PopUpButton((inset + tabStop, linePos, -inset, 17), [], sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		self.w.targetFontText = vanilla.TextBox((inset, linePos + 2, tabStop, 14), "Target font:", sizeStyle='small', selectable=True)
		self.w.targetFontPopup = vanilla.PopUpButton((inset + tabStop, linePos, -inset, 17), self.GetFonts(), sizeStyle='small', callback=self.UpdateTargetLayers)
		linePos += lineHeight

		self.w.targetLayerText = vanilla.TextBox((inset, linePos + 2, tabStop, 14), "Target layer:", sizeStyle='small', selectable=True)
		self.w.targetLayerPopup = vanilla.PopUpButton((inset + tabStop, linePos, -inset, 17), [], sizeStyle='small', callback=self.SavePreferences)
		linePos += lineHeight

		# Include options
		self.w.includeText = vanilla.TextBox((inset, linePos + 2, 60, 14), "Include:", sizeStyle='small', selectable=True)

		self.w.includePaths = vanilla.CheckBox((inset + 60, linePos, 65, 20), "Paths", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includePaths.setToolTip("Copy all paths (outlines) from the source layer.")

		self.w.includeComponents = vanilla.CheckBox((inset + 135, linePos, 80, 20), "Components", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeComponents.setToolTip("Copy all components (references to other glyphs) from the source layer.")
		linePos += lineHeight

		self.w.includeAnchors = vanilla.CheckBox((inset + 60, linePos, 65, 20), "Anchors", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeAnchors.setToolTip("Copy all anchors (attachment points) from the source layer. Anchors of the same name in the target are replaced.")

		self.w.includeMetrics = vanilla.CheckBox((inset + 135, linePos, 80, 20), "Metrics", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeMetrics.setToolTip("Copy layer width and sidebearing metrics from the source layer.")

		self.w.includeHints = vanilla.CheckBox((inset + 210, linePos, 90, 20), "Hints", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeHints.setToolTip("Copy all hints (TrueType instructions) from the source layer.")
		linePos += lineHeight

		self.w.separator1 = vanilla.HorizontalLine((inset, linePos + 5, -inset, 1))

		# Options with tooltips
		linePos += 12
		self.w.intoBackground = vanilla.CheckBox((inset, linePos, -inset, 20), "Copy into background instead", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.intoBackground.setToolTip("Copies source layer content into the background of the target layer instead of the foreground.")
		linePos += lineHeight

		self.w.createIfNotPresent = vanilla.CheckBox((inset, linePos, -inset, 20), "Create target glyph & layer if not already present", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.createIfNotPresent.setToolTip("Automatically creates the target layer (and glyph if necessary) if it doesn't exist. Useful for adding new layers to all selected glyphs.")
		linePos += lineHeight

		self.w.addToContents = vanilla.CheckBox((inset, linePos, -inset, 20), "Add to layer contents (don't overwrite)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.addToContents.setToolTip("Appends source content to target layer instead of replacing it. Useful for combining multiple design elements.")
		linePos += lineHeight

		self.w.applyFontWide = vanilla.CheckBox((inset, linePos, -inset, 20), "Apply font-wide (all glyphs in source font)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.applyFontWide.setToolTip("Processes all glyphs in the source font instead of only selected glyphs in the target font. If not selected, will process only selected glyphs.")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-120 - inset, -20 - inset, -inset, -inset), "Copy Layers", sizeStyle='regular', callback=self.CopyLayerToLayerMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Restored font indices may exceed the number of currently open fonts:
		self.ClampFontPopups()

		# Update the layer popups after fonts are loaded
		self.UpdateSourceLayers(None)
		self.UpdateTargetLayers(None)

		# Now restore the layer popup indices, clamped to the current item counts:
		self.w.sourceLayerPopup.set(self.ClampedPref("sourceLayerPopup", len(self.sourceLayerSpecs)))
		self.w.targetLayerPopup.set(self.ClampedPref("targetLayerPopup", len(self.targetLayerSpecs)))

		self.updateUI()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		"""Disables the run button only when source and target resolve to the same
		font, master and color index, and we are not copying into the background
		(copying a layer into its own background is a legitimate operation)."""
		try:
			sourceFont = self.GetFont(self.w.sourceFontPopup)
			targetFont = self.GetFont(self.w.targetFontPopup)
			sourceSpec = self.SelectedSpec(self.w.sourceLayerPopup, self.sourceLayerSpecs)
			targetSpec = self.SelectedSpec(self.w.targetLayerPopup, self.targetLayerSpecs)

			identical = (
				sourceFont is not None
				and sourceFont == targetFont  # compare font objects, not popup indices
				and sourceSpec is not None
				and sourceSpec == targetSpec
				and not self.w.intoBackground.get()
			)
			self.w.runButton.enable(not identical)

		except Exception as e:
			print(e)
			# If there's any error, enable the button to be safe
			self.w.runButton.enable(True)

	def GetFonts(self):
		"""Returns a list of font names for the popups"""
		myFontList = ["Current Font"]
		for thisFont in Glyphs.fonts:
			fontName = thisFont.filepath.lastPathComponent() if thisFont.filepath else "<unsaved file>"
			myFontList.append('%s (family: %s)' % (fontName, thisFont.familyName))
		return myFontList

	def GetFont(self, fontPopup):
		"""Returns the font object based on popup selection.
		Bounds-checked: a stale preference or an empty selection must not index
		Glyphs.fonts negatively or out of range."""
		fontIndex = fontPopup.get()
		if fontIndex is None or fontIndex <= 0:
			return Glyphs.font
		if fontIndex - 1 < len(Glyphs.fonts):
			return Glyphs.fonts[fontIndex - 1]
		return Glyphs.font

	def ClampFontPopups(self):
		"""Resets font popups whose restored index is out of range."""
		itemCount = len(self.w.sourceFontPopup.getItems())
		for popup in (self.w.sourceFontPopup, self.w.targetFontPopup):
			index = popup.get()
			if index is None or index < 0 or index >= itemCount:
				popup.set(0)

	def ClampedPref(self, prefName, itemCount):
		"""Returns the stored popup index, or 0 if it is out of range."""
		try:
			index = int(self.pref(prefName))
		except (TypeError, ValueError):
			index = 0
		if index < 0 or index >= itemCount:
			index = 0
		return index

	def SelectedSpec(self, layerPopup, specs):
		"""(masterID, masterName, colorIndex) for the current popup selection, or None."""
		index = layerPopup.get()
		if specs and index is not None and 0 <= index < len(specs):
			return specs[index]
		return None

	def GetColorPalettes(self, font):
		"""Returns the color palettes from font's custom parameters"""
		if font and font.customParameters["Color Palettes"]:
			palettes = font.customParameters["Color Palettes"]
			if palettes and len(palettes) > 0:
				# Return the first palette (index 0) which contains the color definitions
				return palettes[0]
		return None

	def GetLayerList(self, font):
		"""Returns (displayNames, specs).

		specs[i] is (masterID, masterName, colorIndex) for displayNames[i], with
		colorIndex None for plain master layers. Layers are identified by master
		ID rather than by name, because master names are not guaranteed unique."""
		if not font or not font.masters:
			return (["Regular"], [(None, "Regular", None)])

		displayNames = []
		specs = []
		masterEntries = []  # (masterID, masterName, displayName)
		usedNames = set()

		for masterIndex, master in enumerate(font.masters):
			displayName = master.name or "Master %d" % (masterIndex + 1)
			if displayName in usedNames:
				# Duplicate master names are legal; disambiguate for display only.
				displayName = "%s [%d]" % (displayName, masterIndex + 1)
			usedNames.add(displayName)

			masterEntries.append((master.id, master.name, displayName))
			displayNames.append(displayName)
			specs.append((master.id, master.name, None))

		colorPalette = self.GetColorPalettes(font)
		if colorPalette:
			numColors = len(colorPalette)
			for masterID, masterName, displayName in masterEntries:
				for colorIndex in range(numColors):
					displayNames.append("%s, Color %d" % (displayName, colorIndex))
					specs.append((masterID, masterName, colorIndex))

		return (displayNames, specs)

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
		if 0 <= sourceSelection < len(fontList):
			self.w.sourceFontPopup.set(sourceSelection)
		else:
			self.w.sourceFontPopup.set(0)

		if 0 <= targetSelection < len(fontList):
			self.w.targetFontPopup.set(targetSelection)
		else:
			self.w.targetFontPopup.set(0)

		# Update layer lists
		self.UpdateSourceLayers(None)
		self.UpdateTargetLayers(None)

		if sender is self.w.sourceFontUpdateButton:
			self.LoadPreferences()
			# LoadPreferences() writes the stored indices straight into the popups,
			# which may be out of range for the refreshed lists; re-clamp them and
			# rebuild the layer lists for whatever font the prefs just selected.
			self.ClampFontPopups()
			self.UpdateSourceLayers(None)
			self.UpdateTargetLayers(None)
			self.w.sourceLayerPopup.set(self.ClampedPref("sourceLayerPopup", len(self.sourceLayerSpecs)))
			self.w.targetLayerPopup.set(self.ClampedPref("targetLayerPopup", len(self.targetLayerSpecs)))
			self.updateUI()
		else:
			self.SavePreferences()

	def UpdateSourceLayers(self, sender=None):
		"""Updates the source layer popup based on selected font"""
		font = self.GetFont(self.w.sourceFontPopup)
		previousSpec = self.SelectedSpec(self.w.sourceLayerPopup, self.sourceLayerSpecs)
		layerNames, self.sourceLayerSpecs = self.GetLayerList(font)
		self.w.sourceLayerPopup.setItems(layerNames)
		self.w.sourceLayerPopup.set(self.sourceLayerSpecs.index(previousSpec) if previousSpec in self.sourceLayerSpecs else 0)
		self.updateUI()

	def UpdateTargetLayers(self, sender):
		"""Updates the target layer popup based on selected font"""
		font = self.GetFont(self.w.targetFontPopup)
		previousSpec = self.SelectedSpec(self.w.targetLayerPopup, self.targetLayerSpecs)
		layerNames, self.targetLayerSpecs = self.GetLayerList(font)
		self.w.targetLayerPopup.setItems(layerNames)
		self.w.targetLayerPopup.set(self.targetLayerSpecs.index(previousSpec) if previousSpec in self.targetLayerSpecs else 0)
		self.updateUI()

	def GetMasterLayer(self, glyph, masterID):
		"""Returns the layer of `glyph` belonging to master `masterID`, or None."""
		if not masterID:
			return None
		for layer in glyph.layers:
			if layer.layerId == masterID:
				return layer
		return None

	def GetColorLayers(self, glyph, masterID, colorIndex):
		"""Returns all layers with the specified master and color palette index"""
		colorLayers = []
		if not masterID:
			return colorLayers
		for layer in glyph.layers:
			if layer.associatedMasterId == masterID and isColorLayer(layer):
				if layer.attributes.get('colorPalette') == colorIndex:
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

			# Resolve the popup selections to (masterID, masterName, colorIndex)
			sourceSpec = self.SelectedSpec(self.w.sourceLayerPopup, self.sourceLayerSpecs)
			targetSpec = self.SelectedSpec(self.w.targetLayerPopup, self.targetLayerSpecs)

			if sourceSpec is None or targetSpec is None:
				Message("Error", "Could not determine the source or target layer.", OKButton=None)
				return

			sourceMasterID, sourceMasterName, sourceColorIndex = sourceSpec
			targetMasterID, targetMasterName, targetColorIndex = targetSpec
			sourceIsColor = sourceColorIndex is not None
			targetIsColor = targetColorIndex is not None

			# Get preferences
			prefs = {
				"intoBackground": self.w.intoBackground.get(),
				"createIfNotPresent": self.w.createIfNotPresent.get(),
				"addToContents": self.w.addToContents.get(),
				"applyFontWide": self.w.applyFontWide.get(),
				"includePaths": self.w.includePaths.get(),
				"includeComponents": self.w.includeComponents.get(),
				"includeAnchors": self.w.includeAnchors.get(),
				"includeHints": self.w.includeHints.get(),
				"includeMetrics": self.w.includeMetrics.get(),
			}

			# Determine which glyphs to process
			if prefs["applyFontWide"]:
				# Process all glyphs in source font
				glyphsToProcess = [g.name for g in sourceFont.glyphs]
			else:
				# Process only selected glyphs in target font
				if targetFont.selectedLayers:
					glyphsToProcess = list(set([layer.parent.name for layer in targetFont.selectedLayers]))
				else:
					Message("Error", "No glyphs selected.", OKButton=None)
					return

			# Counters for reporting
			processedCount = 0
			skippedCount = 0
			createdGlyphCount = 0
			createdLayerCount = 0

			# Process each glyph
			for glyphName in glyphsToProcess:
				print("🔡 Processing %s..." % glyphName)
				# Get source glyph
				sourceGlyph = sourceFont.glyphs[glyphName]
				if not sourceGlyph:
					skippedCount += 1
					continue

				# Get source layer(s)
				if sourceIsColor:
					# Get all color layers with this master and color index
					sourceLayers = self.GetColorLayers(sourceGlyph, sourceMasterID, sourceColorIndex)
				else:
					sourceLayer = self.GetMasterLayer(sourceGlyph, sourceMasterID)
					sourceLayers = [sourceLayer] if sourceLayer else []

				if not sourceLayers:
					skippedCount += 1
					continue

				# Find or create target glyph
				targetGlyph = targetFont.glyphs[glyphName]
				if not targetGlyph:
					if prefs["createIfNotPresent"]:
						targetGlyph = newGlyphWithName(glyphName)
						targetFont.glyphs.append(targetGlyph)
						createdGlyphCount += 1
					else:
						skippedCount += 1
						continue

				# Handle color to color copying (potentially multiple layers)
				if sourceIsColor and targetIsColor:
					# Copy each source color layer to corresponding target color layer
					targetColorLayers = self.GetColorLayers(targetGlyph, targetMasterID, targetColorIndex)

					for i, sourceLayer in enumerate(sourceLayers):
						# Find or create corresponding target layer
						if i < len(targetColorLayers):
							targetLayer = targetColorLayers[i]
						elif prefs["createIfNotPresent"]:
							# Create new color layer
							targetLayer = GSLayer()
							targetLayer.name = targetMasterName
							targetLayer.attributes['colorPalette'] = targetColorIndex
							# Associate with the selected master, not with layer 0's master
							targetLayer.associatedMasterId = targetMasterID
							targetGlyph.layers.append(targetLayer)
							createdLayerCount += 1
						else:
							continue

						self.CopyLayerContents(sourceLayer, targetLayer, prefs)
						processedCount += 1

				# Handle non-color to color copying
				elif not sourceIsColor and targetIsColor:
					sourceLayer = sourceLayers[0]
					# Find or create target layer with matching master and color index
					targetColorLayers = self.GetColorLayers(targetGlyph, targetMasterID, targetColorIndex)

					if targetColorLayers:
						# Use the first existing color layer with this color index
						targetLayer = targetColorLayers[0]
					elif prefs["createIfNotPresent"]:
						# Create new color layer only if it doesn't exist
						targetLayer = GSLayer()
						targetLayer.name = targetMasterName
						targetLayer.attributes['colorPalette'] = targetColorIndex
						targetLayer.associatedMasterId = targetMasterID
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

					targetLayer = self.GetMasterLayer(targetGlyph, targetMasterID)

					if not targetLayer and prefs["createIfNotPresent"]:
						targetLayer = GSLayer()
						targetLayer.name = targetMasterName
						targetLayer.associatedMasterId = targetMasterID
						targetLayer.layerId = targetMasterID
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

					targetLayer = self.GetMasterLayer(targetGlyph, targetMasterID)

					# Create layer if requested and not present
					if not targetLayer and prefs["createIfNotPresent"]:
						targetLayer = GSLayer()
						targetLayer.name = targetMasterName
						targetLayer.associatedMasterId = targetMasterID
						targetLayer.layerId = targetMasterID
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

		# Copy anchors. Assignment by name adds the anchor if absent and replaces
		# it if present, which matches Glyphs' own paste behaviour in append mode.
		if prefs["includeAnchors"]:
			for anchor in sourceLayer.anchors:
				copyTarget.anchors[anchor.name] = anchor.copy()

		# Copy metrics if requested and not copying to background
		if prefs["includeMetrics"] and not prefs["intoBackground"]:
			targetLayer.width = sourceLayer.width
			if hasattr(sourceLayer, 'leftMetricsKey') and sourceLayer.leftMetricsKey:
				targetLayer.leftMetricsKey = sourceLayer.leftMetricsKey
			if hasattr(sourceLayer, 'rightMetricsKey') and sourceLayer.rightMetricsKey:
				targetLayer.rightMetricsKey = sourceLayer.rightMetricsKey


# Run the script
CopyLayerToLayer()

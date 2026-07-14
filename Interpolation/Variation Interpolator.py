# MenuTitle: Variation Interpolator
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Interpolates each layer x times with its background and creates glyph variations with the results.
"""

import vanilla
from Cocoa import NSHeight
from Foundation import NSPoint
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject


def interpolateDicts(dictA, dictB, interpolationFactor=0.5):
	"""
	Returns a new dict containing only keys that exist in both dictA and dictB.
	Values are interpolated linearly:
	- interpolationFactor = 0 -> dictA values
	- interpolationFactor = 1 -> dictB values
	- interpolationFactor in between -> blended values
	"""

	commonKeys = set(dictA.keys()) & set(dictB.keys())
	if not commonKeys:
		return {}

	factorA = 1.0 - interpolationFactor
	factorB = interpolationFactor
	result = {}

	for key in commonKeys:
		valueA = dictA[key]
		valueB = dictB[key]
		result[key] = float(valueA) * factorA + float(valueB) * factorB

	return result


def compatibilityReport(layerA, layerB, labelA="Foreground", labelB="Background"):
	lines = []

	# Shapes (paths)
	pathCountA = len(layerA.paths)
	pathCountB = len(layerB.paths)
	if pathCountA != pathCountB:
		lines.append(f"    Shapes: {labelA} has {pathCountA} path(s), {labelB} has {pathCountB}")
	elif pathCountA > 0:
		nodeMismatches = []
		for i, (pathA, pathB) in enumerate(zip(layerA.paths, layerB.paths)):
			nA, nB = len(pathA.nodes), len(pathB.nodes)
			if nA != nB:
				nodeMismatches.append(f"path {i + 1}: {nA} vs {nB} nodes")
		if nodeMismatches:
			lines.append(f"    Shapes: node count mismatch – {'; '.join(nodeMismatches)}")

	# Anchors
	anchorsA = {a.name for a in layerA.anchors}
	anchorsB = {a.name for a in layerB.anchors}
	onlyInA = anchorsA - anchorsB
	onlyInB = anchorsB - anchorsA
	if onlyInA:
		lines.append(f"    Anchors only in {labelA}: {', '.join(sorted(onlyInA))}")
	if onlyInB:
		lines.append(f"    Anchors only in {labelB}: {', '.join(sorted(onlyInB))}")

	# Components and smart components
	compCountA = len(layerA.components)
	compCountB = len(layerB.components)
	if compCountA != compCountB:
		lines.append(f"    Components: {labelA} has {compCountA}, {labelB} has {compCountB}")
	else:
		for i, (compA, compB) in enumerate(zip(layerA.components, layerB.components)):
			if compA.componentName != compB.componentName:
				lines.append(f"    Component {i + 1}: '{compA.componentName}' vs '{compB.componentName}'")
			else:
				valA = dict(compA.smartComponentValues or {})
				valB = dict(compB.smartComponentValues or {})
				if valA or valB:
					axesA, axesB = set(valA.keys()), set(valB.keys())
					if axesA != axesB:
						lines.append(f"    Smart component {i + 1} '{compA.componentName}': axes differ")
						if axesA - axesB:
							lines.append(f"      Only in {labelA}: {', '.join(sorted(axesA - axesB))}")
						if axesB - axesA:
							lines.append(f"      Only in {labelB}: {', '.join(sorted(axesB - axesA))}")

	return "\n".join(lines) if lines else "    (compareString mismatch – no further structural difference found)"


def interpolateLayers(newGlyph, layerA, layerB, interpolationFactor, thisFont):

	if Glyphs.versionNumber >= 3.5:
		newLayer = newGlyph._interpolateLayers_interpolation_scale_masters_decompose_font_error_(
			[layerA, layerB],  # layers
			{
				layerA.layerId: 1.0 - interpolationFactor,
				layerB.layerId: interpolationFactor
			},                 # interpolation
			1.0,               #scale
			None,              # masters
			False,             # decompose
			thisFont,          # font
			None,              # error
		)
	else:
		newLayer = newGlyph._interpolateLayers_interpolation_masters_decompose_font_error_(
			[layerA, layerB],  # layers
			{
				layerA.layerId: 1.0 - interpolationFactor,
				layerB.layerId: interpolationFactor
			},                 # interpolation
			None,              # masters
			False,             # decompose
			thisFont,          # font
			None,              # error
		)

	# fix smart components:
	for i, component in enumerate(newLayer.components):
		if component.smartComponentValues is None:
			continue
		component.setPieceSettings_(
			interpolateDicts(
				dict(layerA.components[i].smartComponentValues or {}),
				dict(layerB.components[i].smartComponentValues or {}),
				interpolationFactor,
			)
		)

	return newLayer


class VariationInterpolator(mekkaObject):
	prefDict = {
		"numberOfInterpolations": 10,
		"suffix": "",
		"glyphName": "interpolated",
		"choice": 0,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 240
		windowHeight = 120
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Variation Interpolator",  # window title
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 10, 14, 24

		self.w.text_1 = vanilla.TextBox((inset, linePos + 2, 40, 14), "Create", sizeStyle='small')
		self.w.numberOfInterpolations = vanilla.ComboBox((inset + 42, linePos - 1, -inset - 135, 19), [x * 5 for x in range(1, 7)], sizeStyle='small', callback=self.SavePreferences)
		self.w.text_2 = vanilla.TextBox((-inset - 130, linePos + 2, -inset, 14), "interpolations between", sizeStyle='small')
		linePos += lineHeight

		options = (
			"background to foreground",
			"foreground to background",
			"first two selected glyphs",
			"first two selected glyphs (reversed)",
		)
		self.w.choice = vanilla.PopUpButton((inset, linePos, -inset - 40, 17), options, sizeStyle='small', callback=self.SavePreferences)
		self.w.text_21 = vanilla.TextBox((-inset - 35, linePos + 2, -inset, 14), "with", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.suffixText = vanilla.TextBox((inset, linePos + 2, 35, 14), "suffix", sizeStyle='small')
		self.w.suffix = vanilla.EditText((inset + 35, linePos - 1, -130, 20), "", callback=self.SavePreferences, sizeStyle='small')
		self.w.postSuffixText = vanilla.TextBox((-125, linePos + 2, -15, 14), "for selected glyphs.", sizeStyle='small')
		tooltip = "Select any number of glyphs and the script will create interpolations between foreground and background of each individual glyph. They will be named after their glyph, plus the suffix you provide, plus a continuous number. LEAVE EMPTY FOR MATRA VARIATIONS (because the pres feature generation requires pure figure suffixes)."
		self.w.suffixText.setToolTip(tooltip)
		self.w.suffix.setToolTip(tooltip)
		self.w.postSuffixText.setToolTip(tooltip)

		self.w.glyphNameText = vanilla.TextBox((inset, linePos + 2, 70, 14), "glyph name:", sizeStyle='small', selectable=True)
		self.w.glyphName = vanilla.EditText((inset + 70, linePos - 1, -inset, 19), "interpolation.", callback=self.SavePreferences, sizeStyle='small')
		tooltip = "Select exactly two glyphs to interpolate, and the script creates interpolations with this name and a continuous number suffix."
		self.w.glyphName.setToolTip(tooltip)
		self.w.glyphNameText.setToolTip(tooltip)

		# Run Button:
		self.w.runButton = vanilla.Button((-100 - 15, -20 - 15, -15, -15), "Interpolate", callback=self.VariationInterpolatorMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.updateUI()
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		if self.w.choice.get() > 1:
			self.w.suffixText.show(False)
			self.w.suffix.show(False)
			self.w.postSuffixText.show(False)
			self.w.glyphNameText.show(True)
			self.w.glyphName.show(True)
			self.w.runButton.enable(bool(self.w.glyphName.get().strip()) and Glyphs.font and len(Glyphs.font.selectedLayers) == 2)
		else:
			self.w.suffixText.show(True)
			self.w.suffix.show(True)
			self.w.postSuffixText.show(True)
			self.w.glyphNameText.show(False)
			self.w.glyphName.show(False)
			self.w.runButton.enable(Glyphs.font and Glyphs.font.selectedLayers)

	def createGlyphCopy(self, thisGlyph, newSuffix=None, newName=None):
		thisFont = thisGlyph.parent

		# prepare glyph:
		newGlyph = thisGlyph.copy()
		if newSuffix:
			newGlyphName = f"{newGlyph.name}.{newSuffix}"
		elif newName:
			newGlyphName = newName
		newGlyph.name = newGlyphName
		newGlyph.unicode = None

		# remove previously generated glyph with the same name:
		oldGlyph = thisFont.glyphs[newGlyphName]
		if oldGlyph:
			thisFont.removeGlyph_(oldGlyph)

		return newGlyph

	def interpolatedPosition(self, foregroundPosition, foregroundFactor, backgroundPosition, backgroundFactor):
		interpolatedX = foregroundPosition.x * foregroundFactor + backgroundPosition.x * backgroundFactor
		interpolatedY = foregroundPosition.y * foregroundFactor + backgroundPosition.y * backgroundFactor
		interpolatedPosition = NSPoint(interpolatedX, interpolatedY)
		return interpolatedPosition

	def interpolatePaths(self, thisLayer, backgroundFactor, foregroundFactor):
		# interpolate paths only if there is a compatible background:
		if thisLayer.background:  # and (thisLayer.compareString() == thisLayer.background.compareString()):
			for path_index, path in enumerate(thisLayer.paths):
				for node_index, node in enumerate(path.nodes):
					foregroundPosition = node.position
					bPath = thisLayer.background.paths[path_index]
					if bPath:
						backgroundPosition = bPath.nodes[node_index].position
						node.setPosition_(self.interpolatedPosition(
							foregroundPosition,
							foregroundFactor,
							backgroundPosition,
							backgroundFactor,
						))
		else:
			thisGlyph = thisLayer.parent
			print(f"{thisGlyph.name}: incompatible background layer (‘{thisLayer.name}’):")
			print(f"Foreground: {thisLayer.compareString()}\nBackground:{thisLayer.background.compareString()}")

	def interpolateAnchors(self, thisLayer, backgroundFactor, foregroundFactor):
		# interpolate anchor only if there is an anchor of the same name:
		if thisLayer.anchors:
			for foregroundAnchor in thisLayer.anchors:
				backgroundAnchor = thisLayer.background.anchors[foregroundAnchor.name]
				if backgroundAnchor:
					foregroundPosition = foregroundAnchor.position
					backgroundPosition = backgroundAnchor.position
					foregroundAnchor.setPosition_(self.interpolatedPosition(foregroundPosition, foregroundFactor, backgroundPosition, backgroundFactor))
				else:
					thisGlyph = thisLayer.parent
					print(f"{thisGlyph.name}: Anchor ‘{foregroundAnchor.name}’ not in background.")

	def interpolateComponents(self, thisLayer, backgroundFactor, foregroundFactor):
		for i, thisComponent in enumerate(thisLayer.components):
			backgroundComponent = thisLayer.background.components[i]
			if backgroundComponent:

				# general component settings:
				thisComponent.position = self.interpolatedPosition(
					thisComponent.position,
					foregroundFactor,
					backgroundComponent.position,
					backgroundFactor,
				)
				thisComponent.scale = (
					thisComponent.scale[0] * foregroundFactor + backgroundComponent.scale[0] * backgroundFactor,
					thisComponent.scale[1] * foregroundFactor + backgroundComponent.scale[1] * backgroundFactor,
				)
				thisComponent.rotation = (
					thisComponent.rotation * foregroundFactor + backgroundComponent.rotation * backgroundFactor
				)
				thisComponent.smartComponentValues = interpolateDicts(
					dict(thisComponent.smartComponentValues),
					dict(backgroundComponent.smartComponentValues),
					interpolationFactor=foregroundFactor,
				)

				# # smart components:
				# thisFont = thisLayer.parent.parent
				# if thisFont:
				# 	for axis in thisFont.glyphs[thisComponent.componentName].smartComponentAxes:
				# 		newValue = float(thisComponent.smartComponentValues[axis.name]) * foregroundFactor + \
				# 			float(backgroundComponent.smartComponentValues[axis.name]) * backgroundFactor
				# 		thisComponent.smartComponentValues[axis.name] = (newValue)

	def interpolateLayerWithBackground(self, thisLayer, backgroundFactor):
		foregroundFactor = 1.0 - backgroundFactor
		self.interpolatePaths(thisLayer, backgroundFactor, foregroundFactor)
		self.interpolateAnchors(thisLayer, backgroundFactor, foregroundFactor)
		self.interpolateComponents(thisLayer, backgroundFactor, foregroundFactor)
		thisLayer.background = None

	def interpolateGlyphWithBackgrounds(self, newGlyph, backgroundFactor):
		# go through every layer of newGlyph:
		for thisLayer in newGlyph.layers:
			self.interpolateLayerWithBackground(thisLayer, backgroundFactor)

	def layersAreCompatible(self, layerA, layerB):
		return layerA.compareString() == layerB.compareString()

	def VariationInterpolatorMain(self, sender):
		try:
			thisFont = Glyphs.font  # frontmost font
			if not thisFont:
				Message(
					title="No font",
					message="Please open a font and select a glyph to interpolate.",
					OKButton=None,
				)
				return

			selectedLayers = thisFont.selectedLayers
			if not selectedLayers:
				Message(
					title="Select exactly something",
					message="Please select one or two glyphs to interpolate.",
					OKButton=None,
				)
				return

			thisFont.disableUpdateInterface()  # suppresses UI updates in Font View
			try:
				numberOfInterpolations = self.prefInt("numberOfInterpolations")
				glyphSuffix = self.pref("suffix").strip()
				glyphName = self.pref("glyphName").strip()
				choice = self.pref("choice")
				selectedGlyphs = [layer.parent for layer in thisFont.selectedLayers]  # currently selected glyphs
				incompatible = []
				incompatibleReports = []  # list of (reportString, detailString), no duplicates
				incompatibleSeen = set()
				interpolatedGlyphNames = []
				if choice < 2:
					# interpolate between foreground and background
					for thisGlyph in selectedGlyphs:
						for numberOfThisVariation in range(1, numberOfInterpolations + 1):
							interpolationFactor = float(numberOfThisVariation - 1) / float(numberOfInterpolations)
							if choice == 0:  # reverse
								interpolationFactor = 1.0 - interpolationFactor
							newSuffix = "%s%03i" % (glyphSuffix, numberOfThisVariation)
							newGlyph = self.createGlyphCopy(thisGlyph, newSuffix)
							thisFont.glyphs.append(newGlyph)
							interpolatedGlyphNames.append(newGlyph.name)

							for masterIndex, thisMaster in enumerate(thisFont.masters):
								layerA = thisGlyph.layers[thisMaster.id].copy()
								layerA.layerId = "layerIDA%05i" % masterIndex
								layerB = thisGlyph.layers[thisMaster.id].copy()
								layerB.swapForegroundWithBackground()
								layerB.layerId = "layerIDB%05i" % masterIndex

								# check compatibility
								if not self.layersAreCompatible(layerA, layerB):
									reportString = thisGlyph.name
									if len(thisFont.masters) > 1:
										reportString += f" ({thisMaster.name})"
									if reportString not in incompatibleSeen:
										incompatibleSeen.add(reportString)
										detail = compatibilityReport(layerA, layerB, "Foreground", "Background")
										incompatibleReports.append((reportString, detail))
										incompatible.append(reportString)
									continue

								newGlyph.layers[thisMaster.id] = interpolateLayers(newGlyph, layerA, layerB, interpolationFactor, thisFont)

				else:
					# interpolate between first two glyphs
					if not len(selectedGlyphs) == 2:
						Message(
							title="Select exactly two glyphs",
							message="Please select exactly two glyphs to interpolate.",
							OKButton=None,
						)
						return

					glyphA, glyphB = selectedGlyphs
					for numberOfThisVariation in range(1, numberOfInterpolations + 1):
						interpolationFactor = float(numberOfThisVariation - 1) / float(numberOfInterpolations)
						if choice == 3:
							interpolationFactor = 1.0 - interpolationFactor
						newName = "%s.%04i" % (glyphName, numberOfThisVariation)
						newGlyph = self.createGlyphCopy(glyphA, newName=newName)
						thisFont.glyphs.append(newGlyph)
						interpolatedGlyphNames.append(newName)

						for masterIndex, thisMaster in enumerate(thisFont.masters):
							layerA = glyphA.layers[thisMaster.id].copy()
							layerA.layerId = "layerIDA%05i" % masterIndex
							layerB = glyphB.layers[thisMaster.id].copy()
							layerB.layerId = "layerIDB%05i" % masterIndex

							# check compatibility
							if not self.layersAreCompatible(layerA, layerB):
								reportString = f"{glyphA.name}→{glyphB.name}"
								if len(thisFont.masters) > 1:
									reportString += f" ({thisMaster.name})"
								if reportString not in incompatibleSeen:
									incompatibleSeen.add(reportString)
									detail = compatibilityReport(layerA, layerB, glyphA.name, glyphB.name)
									incompatibleReports.append((reportString, detail))
									incompatible.append(reportString)
								continue

							newGlyph.layers[thisMaster.id] = interpolateLayers(newGlyph, layerA, layerB, interpolationFactor, thisFont)

				if incompatible:
					incompatible = sorted(set(incompatible))
					print("Variation Interpolator – Incompatibility Report:\n")
					for reportString, detail in incompatibleReports:
						print(f"  ❌ {reportString}:")
						print(detail)
						print()
					Glyphs.showMacroWindow()
					if Glyphs.versionNumber < 4.0:
						splitview = Glyphs.delegate().macroPanelController().consoleSplitView()
						frame = splitview.frame()
						height = NSHeight(frame)
						newPos = 0.2
						splitview.setPosition_ofDividerAtIndex_(height * newPos, 0)
					Message(
						title="Incompatible glyphs",
						message=f"Could not interpolate:\n{', '.join(incompatible)}\nDetails in Macro Window.",
						OKButton=None,
					)
				else:
					tab = thisFont.currentTab or thisFont.newTab()
					tab.text = "/" + "/".join([g.name for g in selectedGlyphs]) + "\n/" + "/".join(interpolatedGlyphNames)

			except Exception as e:
				Glyphs.showMacroWindow()
				print("\n⚠️ Script Error:\n")
				import traceback
				print(traceback.format_exc())
				print()
				raise e

			finally:
				thisFont.enableUpdateInterface()  # re-enables UI updates in Font View

			self.SavePreferences()

			self.w.close()  # delete if you want window to stay open
		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print(f"Variation Interpolator Error: {e}")
			import traceback
			print(traceback.format_exc())


VariationInterpolator()

# MenuTitle: Variation Interpolator
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Interpolates each layer x times with its background and creates glyph variations with the results.
"""

import vanilla
from Foundation import NSPoint
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject


class VariationInterpolator(mekkaObject):
	prefDict = {
		"numberOfInterpolations": 10,
		"suffix": "var",
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
			"background and foreground",
			"foreground and background",
			"first two selected glyphs",
			"first two selected glyphs (reversed)",
		)
		self.w.choice = vanilla.PopUpButton((inset, linePos, -inset - 40, 17), options, sizeStyle='small', callback=self.SavePreferences)
		self.w.text_21 = vanilla.TextBox((-inset - 35, linePos + 2, -inset, 14), "with", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.suffixText = vanilla.TextBox((inset, linePos + 2, 35, 14), "suffix", sizeStyle='small')
		self.w.suffix = vanilla.EditText((inset + 35, linePos - 1, -130, 20), "var", callback=self.SavePreferences, sizeStyle='small')
		self.w.postSuffixText = vanilla.TextBox((-125, linePos + 2, -15, 14), "for selected glyphs.", sizeStyle='small')
		tooltip = "Select any number of glyphs and the script will create interpolations between foreground and background of each individual glyph. They will be named after their glyph, plus the suffix you provide, plus a continuous number."
		self.w.suffixText.getNSTextField().setToolTip_(tooltip)
		self.w.suffix.getNSTextField().setToolTip_(tooltip)
		self.w.postSuffixText.getNSTextField().setToolTip_(tooltip)

		self.w.glyphNameText = vanilla.TextBox((inset, linePos + 2, 70, 14), "glyph name:", sizeStyle='small', selectable=True)
		self.w.glyphName = vanilla.EditText((inset + 70, linePos - 1, -inset, 19), "interpolation.", callback=self.SavePreferences, sizeStyle='small')
		tooltip = "Select exactly two glyphs to interpolate, and the script creates interpolations with this name and a continuous number suffix."
		self.w.glyphName.getNSTextField().setToolTip_(tooltip)
		self.w.glyphNameText.getNSTextField().setToolTip_(tooltip)

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
			self.w.runButton.enable(bool(self.w.glyphName.get().strip()))
		else:
			self.w.suffixText.show(True)
			self.w.suffix.show(True)
			self.w.postSuffixText.show(True)
			self.w.glyphNameText.show(False)
			self.w.glyphName.show(False)
			self.w.runButton.enable(bool(self.w.suffix.get().strip()))

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
				thisComponent.rotation = (thisComponent.rotation * foregroundFactor + backgroundComponent.rotation * backgroundFactor)

				# smart components:
				thisFont = thisLayer.parent.parent
				if thisFont:
					for axis in thisFont.glyphs[thisComponent.componentName].smartComponentAxes:
						newValue = float(thisComponent.smartComponentValues[axis.name]) * foregroundFactor + \
							float(backgroundComponent.smartComponentValues[axis.name]) * backgroundFactor
						thisComponent.smartComponentValues[axis.name] = (newValue)

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
			selectedLayers = thisFont.selectedLayers
			if not selectedLayers:
				Message(
					title="Select exactly something",
					message="Please select exactly two glyphs to interpolate.",
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

				if choice < 2:
					# interpolate between foreground and background
					for thisGlyph in selectedGlyphs:
						for numberOfThisVariation in range(1, numberOfInterpolations + 1):
							interpolationFactor = float(numberOfThisVariation - 1) / float(numberOfInterpolations)
							if choice == 1:  # reverse
								interpolationFactor = 1.0 - interpolationFactor
							newSuffix = "%s%03i" % (glyphSuffix, numberOfThisVariation)
							newGlyph = self.createGlyphCopy(thisGlyph, newSuffix)
							thisFont.glyphs.append(newGlyph)

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
									incompatible.append(reportString)
									continue

								newGlyph.layers[thisMaster.id] = newGlyph._interpolateLayers_interpolation_masters_decompose_font_error_(
									[layerA, layerB],  # layers
									{
										layerA.layerId: interpolationFactor,
										layerB.layerId: 1.0 - interpolationFactor
									},  # interpolation
									None,  # masters
									False,  # decompose
									thisFont,  # font
									None,  # error
								)

				else:
					# interpolate between first two glyphs
					if not len(selectedGlyphs) == 2:
						Message(
							title="Select exactly two glyphs",
							message="Please select exactly two glyphs to interpolate.",
							OKButton=None,
						)
					else:
						glyphA, glyphB = selectedGlyphs
						for numberOfThisVariation in range(1, numberOfInterpolations + 1):
							interpolationFactor = float(numberOfThisVariation - 1) / float(numberOfInterpolations)
							if choice == 3:
								interpolationFactor = 1.0 - interpolationFactor
							newName = "%s.%04i" % (glyphName, numberOfThisVariation)
							newGlyph = self.createGlyphCopy(glyphA, newName=newName)
							thisFont.glyphs.append(newGlyph)

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
									incompatible.append(reportString)
									continue

								newGlyph.layers[thisMaster.id] = newGlyph._interpolateLayers_interpolation_masters_decompose_font_error_(
									[layerA, layerB],  # layers
									{
										layerA.layerId: interpolationFactor,
										layerB.layerId: 1.0 - interpolationFactor,
									},  # interpolation
									None,  # masters
									False,  # decompose
									thisFont,  # font
									None,  # error
								)

				if incompatible:
					incompatible = sorted(set(incompatible))
					Message(
						title="Incompatible glyphs",
						message=f"Could not interpolate:\n{', '.join(incompatible)}",
						OKButton=None,
					)
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

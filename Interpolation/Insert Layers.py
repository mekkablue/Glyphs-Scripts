# MenuTitle: Insert Layers
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Batch-insert brace or bracket layers in selected glyphs.
"""

import vanilla
from GlyphsApp import Glyphs, GSLayer, Message
from mekkaCore import mekkaObject


class InsertSpecialLayers(mekkaObject):
	prefDict = {
		"layerName": "Intermediate {100}",
		"prefillWithMasterContent": 0,
		"keepExistingBrace": 1,
		"reinterpolateBrace": 1,
	}

	def __init__(self):
		# Window 'self.w':
		windowWidth = 240
		windowHeight = 180
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Insert Special Layers",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), "Insert layer into selected glyphs:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.layerNameText = vanilla.TextBox((inset, linePos + 2, 70, 14), "Layer name:", sizeStyle='small', selectable=True)
		self.w.layerName = vanilla.EditText((inset + 70, linePos - 1, -inset, 19), "Intermediate {100}", callback=self.SavePreferences, sizeStyle='small')
		linePos += lineHeight

		self.w.prefillWithMasterContent = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Create as duplicate of master layer", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.prefillWithMasterContent.getNSButton().setToolTip_("Will add the new layer with the content of the associated master layer. If checkbox is off, will insert empty layer. In case of brace layers, the Reinterpolate option (further down) takes precedence, though.")
		linePos += lineHeight

		self.w.keepExistingBrace = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Keep existing brace layer", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.keepExistingBrace.getNSButton().setToolTip_("Only applies to brace layers. If checkbox is on and a glyph already contains (on any master) a brace layer at the indicated value, the script will skip the glyph. If the checkbox is off, it will deactivate the existing brace layer by replacing the curly braces with hashtags.")
		linePos += lineHeight

		self.w.reinterpolateBrace = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Reinterpolate brace layers", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.reinterpolateBrace.getNSButton().setToolTip_("Only applies to brace layers. If checkbox is on and a brace layer is inserted, it will reinterpolate the newly generated brace layer. It only does this for newly generated layer, and will not reinterpolate existing brace layers.")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Insert", sizeStyle='regular', callback=self.InsertSpecialLayersMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		if not self.LoadPreferences():
			print("Note: 'Insert Special Layers' could not load preferences. Will resort to defaults")

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def braceValueFromName(self, braceName):
		return braceName[braceName.find("{"):braceName.find("}") + 1]

	def InsertSpecialLayersMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			if not self.SavePreferences():
				print("Note: 'Insert Special Layers' could not write preferences.")

			thisFont = Glyphs.font  # frontmost font
			if thisFont is None:
				Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			else:
				print("Insert Special Layers Report for %s" % thisFont.familyName)
				if thisFont.filepath:
					print(thisFont.filepath)
				else:
					print("⚠️ The font file has not been saved yet.")
				print()

				layerName = self.pref("layerName")
				prefillWithMasterContent = self.pref("prefillWithMasterContent")
				keepExistingBrace = self.pref("keepExistingBrace")
				reinterpolateBrace = self.pref("reinterpolateBrace")

				isBrace = "{" in layerName and "}" in layerName and layerName.find("{") < layerName.find("}") - 1

				currentMaster = thisFont.selectedFontMaster
				insertedLayerCount = 0

				for thisGlyph in [layer.parent for layer in thisFont.selectedLayers]:
					print("🔠 Processing %s" % thisGlyph.name)
					if isBrace and not keepExistingBrace:
						braceParticle = self.braceValueFromName(layerName)
						for potentialBraceLayer in thisGlyph.layers:
							if potentialBraceLayer.isSpecialLayer and braceParticle in potentialBraceLayer.name:
								# deactivate it: {100} -> #100#
								print("  Deactivating layer: %s" % potentialBraceLayer.name)
								potentialBraceLayer.name = potentialBraceLayer.name.replace("{", "#").replace("}", "#")

					if prefillWithMasterContent:
						newLayer = thisGlyph.layers[currentMaster.id].copy()
					else:
						newLayer = GSLayer()
						newLayer.associatedMasterId = currentMaster.id

					if newLayer:
						newLayer.name = layerName
						print("  Adding layer: %s" % newLayer.name)
						thisGlyph.layers.append(newLayer)
						insertedLayerCount += 1

						if isBrace and reinterpolateBrace:
							newLayer.reinterpolate()

			# Final report:
			Glyphs.showNotification(
				"%s: Done" % (thisFont.familyName),
				"Inserted %i layer%s. Details in Macro Window." % (
					insertedLayerCount,
					"" if insertedLayerCount == 1 else "s",
				),
			)
			print("\nDone.")

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Insert Special Layers Error: %s" % e)
			import traceback
			print(traceback.format_exc())


InsertSpecialLayers()

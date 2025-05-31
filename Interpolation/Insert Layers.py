# MenuTitle: Insert Layers
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
if Glyphs.versionNumber < 3:
	__doc__ = "Batch-insert brace or bracket layers in selected glyphs."
else:
	__doc__ = "Batch-insert intermediate layers (‘brace layers’) in selected glyphs."

import vanilla
from GlyphsApp import Glyphs, GSLayer, Message
from mekkablue import mekkaObject
from copy import copy


class InsertSpecialLayersV3(mekkaObject):
	prefDict = {
		"intermediateCoordinates": "wght=400, wdth=100",
		"keepExistingBrace": 1,
	}
	
	def __init__(self):
		windowWidth = 330
		windowHeight = 140
		windowWidthResize = 500  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Insert Intermediate Layers",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)
		
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos+2, -inset, 14), "Add intermediate (‘brace’) layers to selected glyphs:", sizeStyle="small", selectable=True)
		linePos += lineHeight
		
		self.w.intermediateCoordinates = vanilla.EditText((inset, linePos, -inset-21, 19), self.pref("intermediateCoordinates"), callback=self.SavePreferences, sizeStyle="small")
		self.w.updateCoordinates = UpdateButton((-inset-16, linePos-3, -inset, 16), callback=self.resetCoordinates)
		self.w.updateCoordinates.getNSButton().setToolTip_("Will reset the entry to half way between the first two masters, or same as the only master (if there is only one).")
		linePos += lineHeight

		self.w.keepExistingBrace = vanilla.CheckBox((inset, linePos, -inset, 20), "Keep (don’t overwrite) existing brace layers", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.keepExistingBrace.getNSButton().setToolTip_("If checkbox is on and a glyph already contains (on any master) a brace layer at the indicated value, the script will skip the glyph. If the checkbox is off, it will deactivate the existing brace layer, and insert a new one.")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80-inset, -20-inset, -inset, -inset), "Insert", callback=self.InsertSpecialLayersV3Main)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()


	def resetCoordinates(self, sender=None):
		if not Glyphs.font:
			return
		text = self.braceDefaultForFont(Glyphs.font)
		self.setPref("intermediateCoordinates", text)
		self.LoadPreferences()


	def braceDefaultForFont(self, font):
		tags = [axis.axisTag for axis in font.axes]
		ids = [axis.axisId for axis in font.axes]
		coords = list(font.masters[0].axes)
		if len(font.masters) > 1:
			otherMaster = font.masters[1]
			for i, coord in enumerate(coords):
				coords[i] = round((coord + otherMaster.axes[i]) / 2)
		braceText = ", ".join([f"{tag}={val}" for tag, val in zip(tags, coords)])
		return braceText


	def InsertSpecialLayersV3Main(self, sender=None):
		# clear macro window log:
		Glyphs.clearLog()

		# update settings to the latest user input:
		self.SavePreferences()

		thisFont = Glyphs.font  # frontmost font
		if thisFont is None:
			Message(title="No Font Open", message="The script requires a font. Open a font and run the script again.", OKButton=None)
			return

		print("Insert Special Layers Report for %s" % thisFont.familyName)
		if thisFont.filepath:
			print(f"📄 {thisFont.filepath}")
		else:
			print("⚠️ The font file has not been saved yet.")
		print()
		
		coordinates = {}
		for coordDef in [c.strip() for c in self.pref("intermediateCoordinates").split(",") if "=" in c]:
			axisTag, braceValue = coordDef.split("=")
			axisTag = axisTag.strip()
			braceValue = float(braceValue.strip())
			axis = thisFont.axisForTag_(axisTag)
			if not axis:
				Message(
					title=f"Axis Not Found: {axisTag}",
					message=f"No axis with tag ‘{axisTag}’ found in frontmost font ‘{thisFont.familyName}’.",
					OKButton=None,
					)
				return
			axisID = axis.axisId
			coordinates[axisID] = braceValue
		
		numUser = len(coordinates)
		numFont = len(thisFont.axes)
		if numUser != numFont:
			Message(
				title="Axes Mismatch Error",
				message=f"You defined {numUser} ax{'i' if numUser==1 else 'e'}s, but the frontmost font ‘{thisFont.familyName}’ has {numFont} ax{'i' if numFont==1 else 'e'}s.",
				OKButton=None,
				)
			return
		
		selectedGlyphs = set([l.parent for l in thisFont.selectedLayers])
		for selectedGlyph in selectedGlyphs:
			self.addBraceToGlyph(selectedGlyph, coordinates)

	
	def addBraceToGlyph(self, glyph, coordinates):
		if self.prefBool("keepExistingBrace"):
			for existingLayer in glyph.layers:
				if existingLayer.attributes["coordinates"] == coordinates:
					return
		braceLayer = copy(glyph.layers[0])
		braceLayer.attributes["coordinates"] = coordinates
		glyph.layers.append(braceLayer)
		braceLayer.reinterpolate()


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

		self.w.prefillWithMasterContent = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Create as duplicate of master layer", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.prefillWithMasterContent.getNSButton().setToolTip_("Will add the new layer with the content of the associated master layer. If checkbox is off, will insert empty layer. In case of brace layers, the Reinterpolate option (further down) takes precedence, though.")
		linePos += lineHeight

		self.w.keepExistingBrace = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Keep existing brace layer", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.keepExistingBrace.getNSButton().setToolTip_("Only applies to brace layers. If checkbox is on and a glyph already contains (on any master) a brace layer at the indicated value, the script will skip the glyph. If the checkbox is off, it will deactivate the existing brace layer by replacing the curly braces with hashtags.")
		linePos += lineHeight

		self.w.reinterpolateBrace = vanilla.CheckBox((inset + 2, linePos - 1, -inset, 20), "Reinterpolate brace layers", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.reinterpolateBrace.getNSButton().setToolTip_("Only applies to brace layers. If checkbox is on and a brace layer is inserted, it will reinterpolate the newly generated brace layer. It only does this for newly generated layer, and will not reinterpolate existing brace layers.")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-80 - inset, -20 - inset, -inset, -inset), "Insert", callback=self.InsertSpecialLayersMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

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
			self.SavePreferences()

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


if Glyphs.versionNumber < 3:
	InsertSpecialLayers()
else:
	InsertSpecialLayersV3()

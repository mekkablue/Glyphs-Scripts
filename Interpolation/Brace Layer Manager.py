# MenuTitle: Brace and Bracket Manager
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Find and replace brace and bracket layer coordinates.
"""

import vanilla
from AppKit import NSNotificationCenter
from GlyphsApp import Glyphs, Message
from mekkablue import mekkaObject


class BraceLayerManager(mekkaObject):
	prefDict = {
		"layerType": 0,
		"scope": 0,
		"oldCoordinate": 100,
		"newCoordinate": 200,
		"axisIndex": 0,
		"currentMasterOnly": 0,
	}
	layerTypes = (
		"{ } brace (intermediate) layers",
		"[ ] bracket (alternate) layers",
	)

	scopes = (
		"in selected glyphs",
		"⚠️ in ALL glyphs of current font",
		"⚠️ in ALL glyphs of ⚠️ ALL open fonts",
	)

	def __init__(self):
		# Window 'self.w':
		windowWidth = 270
		windowHeight = 225
		windowWidthResize = 100  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Brace and Bracket Manager",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow"),  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 12, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, 20, 14), "In", sizeStyle="small", selectable=True)
		self.w.layerType = vanilla.PopUpButton((inset + 20, linePos, -inset, 17), self.layerTypes, sizeStyle="small", callback=self.SavePreferences)

		linePos += lineHeight
		self.w.replaceText = vanilla.TextBox((inset, linePos + 2, 45, 14), "replace", sizeStyle="small", selectable=True)
		self.w.oldCoordinate = vanilla.ComboBox((inset + 45, linePos - 1, 55, 19), self.allBraceAndBracketLayerCoordinatesInFrontmostFont(), sizeStyle="small", callback=self.SavePreferences)
		self.w.oldCoordinateUpdate = vanilla.SquareButton((inset + 105, linePos, 20, 18), "↺", sizeStyle="small", callback=self.update)
		self.w.withText = vanilla.TextBox((inset + 130, linePos + 2, 30, 14), "with", sizeStyle="small", selectable=True)
		self.w.newCoordinate = vanilla.EditText((inset + 160, linePos - 1, -inset, 19), "100", callback=self.SavePreferences, sizeStyle="small")
		self.w.newCoordinate.getNSTextField().setToolTip_("Leave empty for disabling the brace layer or deleting the bracket layer condition.")
		linePos += lineHeight

		self.w.axisText = vanilla.TextBox((inset, linePos + 2, 95, 14), "for axis at index", sizeStyle="small", selectable=True)
		self.w.axisIndex = vanilla.EditText((inset + 90, linePos - 1, -inset - 80, 19), "0", callback=self.SavePreferences, sizeStyle="small")
		self.w.axisTextAfter = vanilla.TextBox((-inset - 78, linePos + 2, -inset, 14), "(first axis = 0)", sizeStyle="small", selectable=True)
		linePos += lineHeight

		self.w.scope = vanilla.RadioGroup((inset, linePos, -inset, lineHeight * len(self.scopes)), self.scopes, callback=self.SavePreferences, sizeStyle="small")
		self.w.scope.set(0)
		linePos += lineHeight * len(self.scopes)

		self.w.currentMasterOnly = vanilla.CheckBox((inset, linePos - 1, -inset, 20), "Restrict to currently selected master(s) only", value=False, callback=self.SavePreferences, sizeStyle="small")
		linePos += lineHeight

		# Run Button:
		self.w.runButton = vanilla.Button((-90 - inset, -20 - inset, -inset, -inset), "Change", callback=self.BraceLayerManagerMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def update(self, sender=None):
		if sender == self.w.oldCoordinateUpdate:
			allCoordinates = self.allBraceAndBracketLayerCoordinatesInFrontmostFont()
			self.w.oldCoordinate.setItems(allCoordinates)

	def allBraceAndBracketLayerCoordinatesInFrontmostFont(self, sender=None):
		allCoordinates = []
		axisIndex = 0
		currentFont = Glyphs.font
		isBraceLayer = self.pref("layerType") == 0
		try:
			axisIndex = self.prefInt("axisIndex")
		except:
			print("Warning: could not retrieve preference for axis index, will default to 0.")

		if currentFont and len(currentFont.axes) > axisIndex:
			axisID = currentFont.axes[axisIndex].axisId
			for thisGlyph in currentFont.glyphs:
				for thisLayer in thisGlyph.layers:
					if thisLayer.isSpecialLayer and thisLayer.attributes:
						if isBraceLayer and "coordinates" in thisLayer.attributes.keys():
							currentCoord = thisLayer.attributes["coordinates"][str(axisID)]
							allCoordinates.append(currentCoord)
						if not isBraceLayer and "axisRules" in thisLayer.attributes:
							axisRules = thisLayer.attributes["axisRules"]
							if axisRules and axisID in axisRules.keys():
								axisLimits = axisRules[axisID]
								for border in ("min", "max"):
									if border in axisLimits.keys():
										borderLimit = axisLimits[border]
										allCoordinates.append(borderLimit)

			allCoordinates = sorted(set(allCoordinates), key=lambda coordinate: float(coordinate))

		return allCoordinates

	def BraceLayerManagerMain(self, sender=None):
		try:
			# clear macro window log:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			isBraceLayer = self.pref("layerType") == 0
			scope = self.pref("scope")
			if scope < 2:
				fonts = (Glyphs.font, )
			else:
				fonts = Glyphs.fonts

			count = 0

			for thisFont in fonts:
				if thisFont is None:
					Message(
						title="No Font Open",
						message="The script requires a font. Open a font and run the script again.",
						OKButton=None,
					)
					return
				else:
					self.processFont(thisFont, isBraceLayer, scope, count)

					if thisFont.currentTab and Glyphs.versionNumber >= 3:
						NSNotificationCenter.defaultCenter().postNotificationName_object_("GSUpdateInterface", thisFont.currentTab)

				print()

			# Final report:
			reportMsg = "Changed %i %s layer%s" % (
				count,
				"brace" if isBraceLayer else "bracket",
				"" if count == 1 else "s",
			)
			if len(fonts) > 1:
				reportMsg += " in %i fonts"
			Glyphs.showNotification(
				"Brace & Bracket Layer Update Done",
				"%s. Details in Macro Window" % reportMsg,
			)
			print("%s.\nDone." % reportMsg)

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Brace and Bracket Manager Error: %s" % e)
			import traceback

			print(traceback.format_exc())

	def processFont(self, thisFont, isBraceLayer, scope, count):
		print("Brace and Bracket Manager Report for %s" % thisFont.familyName)
		if thisFont.filepath:
			print(thisFont.filepath)
		else:
			print("⚠️ The font file has not been saved yet.")
		print()

		searchFor = self.prefFloat("oldCoordinate")
		replaceWith = self.pref("newCoordinate").strip()
		if replaceWith == "":
			replaceWith = None
		else:
			replaceWith = float(replaceWith)
		currentMasterOnly = self.prefBool("currentMasterOnly")
		currentMasterID = thisFont.selectedFontMaster.id
		axisIndex = self.prefInt("axisIndex")
		axis = thisFont.axes[axisIndex]
		axisID = axis.axisId
		axisName = axis.name

		if replaceWith is None:
			print(f"🚫 Disabling {axisName}: {searchFor}")
		else:
			print(f"🔢 Attempting {axisName}: {searchFor} → {replaceWith}")

		if scope == 0:
			glyphs = [layer.parent for layer in thisFont.selectedLayers]
		else:
			glyphs = thisFont.glyphs

		for glyph in glyphs:
			# print(f"  Processing {glyph.name}...")
			for layer in glyph.layers:
				if currentMasterOnly and layer.associatedMasterId != currentMasterID:
					continue
				if layer.isSpecialLayer and layer.attributes:
					if isBraceLayer:
						result, count = self.processBraceLayer(layer, count, searchFor, replaceWith, axisID)
					else:
						result, count = self.processBracketLayer(layer, count, searchFor, replaceWith, axisID, axisIndex)
					if not result:
						break

	def processBraceLayer(self, layer, count, searchFor, replaceWith, axisID):
		if "coordinates" not in layer.attributes.keys():
			return True, count
		# print(f'layer.attributes["coordinates"]["{axisID}"]')
		currentPos = layer.attributes["coordinates"][axisID]
		if currentPos == searchFor:
			if replaceWith is not None:
				try:
					layer.attributes["coordinates"][axisID] = replaceWith
				except Exception as e:
					print(f"⚠️ Error in {layer.parent.name}, ‘{layer.name}’: {e}")
			else:
				del layer.attributes["coordinates"][axisID]
				if not layer.attributes["coordinates"]:
					del layer.attributes["coordinates"]
			count += 1
			print(f"  🔠 {count}. {layer.parent.name}")
		return True, count

	def processBracketLayer(self, layer, count, searchFor, replaceWith, axisID, axisIndex):
		axisRules = layer.attributes["axisRules"]
		if not axisRules:
			return True, count
		if axisID not in axisRules.keys():
			print(f"⚠️ Could not find bracket layers for axis ‘{layer.font.axisForId_(axisID).name}’ (index {axisIndex}) in {layer.parent.name}. Did you select the correct axis?")
			Glyphs.showMacroWindow()
			return False

		print(axisRules)
		axisLimits = axisRules[axisID]
		if not axisLimits:
			return

		for border in ("min", "max"):
			if border in axisLimits.keys():
				borderLimit = float(axisLimits[border])
				if borderLimit == searchFor:
					if replaceWith is not None:
						axisLimits[border] = replaceWith
					else:
						del layer.attributes["axisRules"][axisID][border]
						if not layer.attributes["axisRules"][border]:
							del layer.attributes["axisRules"][border]
						if not layer.attributes["axisRules"]:
							del layer.attributes["axisRules"]
					count += 1
					print(f"  🔠 {count}. {layer.parent.name} ({border})")
		return True, count


if Glyphs.versionNumber >= 3:
	# GLYPHS 3
	BraceLayerManager()
else:
	# GLYPHS 2
	Message(
		title="Version Error",
		message="This script requires Glyphs 3 or later.",
		OKButton=None,
	)
